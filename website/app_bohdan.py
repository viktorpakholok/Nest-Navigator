"""HOuses"""
from flask import Flask, request, render_template, Blueprint, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json
import os
from sqlalchemy import create_engine, ForeignKey, Column, String, \
Integer, CHAR, ARRAY, BLOB, REAL, and_, true
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from static.parsers.ria_parser import parser_dom
from static.parsers.test_work_olx import parse_olx

import random

# with open("js.json", "r") as file:
#     data_json = json.load(file)
#     data_json = data_json['mainEntity']['itemListElement'][0]['offers']['offers']
#     print(data_json)

# with open('result.json', 'r') as file:
#     data_json_olx = json.load(file)


#######################################################################################################################



#######################################################################################################################

Base = declarative_base()
class Apartament_write(Base):
    '''
    How the table will be looking to the perspective 
    of every element
    '''
    ### Create a table
    __tablename__ = "Apartaments"
    images = Column("images", String) #
    url = Column("url", String, primary_key = True) #
    name = Column("name", String) #
    area = Column("area", REAL) #
    price = Column("price", REAL)
    currency = Column("currency", String)
    rooms = Column('rooms', Integer)
    district = Column('district', String)
    city = Column('city', String)

    def __init__(self, images, url, name, area, price, currency, rooms, district, city) -> None:
        self.images = images
        self.url = url
        self.name = name
        self.area = area
        self.currency = currency
        self.price = price
        self.rooms = rooms
        self.district = district
        self.city = city

    def __repr__(self) -> str:
        return f"{self.number} {self.name} {self.price} {self.currency}"


class DatabaseManipulation:
    '''Do smth with a database'''
    def __init__(self, database_name:str) -> None:
        self.database_name = database_name
        if os.path.exists(database_name):
            os.remove(database_name)

        engine = create_engine(f"sqlite:///{database_name}", echo = True)
        Base.metadata.create_all(bind = engine)

        Session = sessionmaker(bind = engine)
        self.session = Session()



    def read_dictinary_to_objects_dom(self, dictinary_list:list) -> None:
        '''
        Read selected Viktortype dictinary to the database. 
        Can make a new database or delete the existing one and make another.

        
        '''
        for dictinary in dictinary_list:
            names = dictinary['name'].split(',')[2:]
            if 'р‑н.' in names[2]:
                area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()),\
                names[2][5:].strip(), names[3].strip()
            else:
                area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()),\
                '', names[2].strip()
            self.session.add(Apartament_write((",".join(dictinary["image"])), dictinary['url']\
                                , dictinary['name'],area, float("".join(\
                                    dictinary['price'].split())), dictinary['priceCurrency'], rooms, district, city))
        self.session.commit()

    # def get_filtered_data_dom(self, price_boundaries:tuple | None = None, room_boundaries:tuple\
    #                     | None = None, districts:tuple | None = None, cities:tuple | None = None) -> list:
        # '''Filter the data needed and output the list of Apartament objects'''
        # return self.session.query(Apartament).filter(and_(true(), Apartament.price >= price_boundaries[0] and Apartament.price <= price_boundaries[1])).all()
 
    def read_dictinary_to_objects_olx(self, dictinary_list:dict) -> None:
        '''
        Read selected Viktortype dictinary to the database. 
        Can make a new database or delete the existing one and make another.

        '''
        for value in dictinary_list.values():
            # print(value)
            currency =  'UAH' if value['price'][-4:-1] == 'грн' else 'USD' if value['price'][-1] == '$' else 'EUR'
            self.session.add(Apartament_write(",".join(value['images']), value['url'], value['name'], float(value['square'][:-3]),\
    float("".join(value['price'][:-5].split(' '))) if currency == 'UAH' else float("".join(value['price'][:-2].split(' '))), currency, int(value['num_of_rooms'][:-8]), value['district'],value['city']))
        self.session.commit()
        # result = session.query(Apartament).all()
        # print(result)
# students = session.query(Student).filter(
#     and_(Student.id >= 100, Student.id <= 200,
#          Student.dob > '2000-01-01')).all()
    # read_dictinary_to_objects(data_json, 'houses3_db.db')

# data = DatabaseManipulation('houses_test_db.db')
# data.read_dictinary_to_objects_dom(data_json)


#######################################################################################################################



app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'houses_test_db.db')
app.config['SECRET_KEY'] = 'BohdanBohdanBohdan'

db = SQLAlchemy(app)

class Apartament(db.Model):
    '''
    How the table will be looking to the perspective 
    of every element
    '''
    ### Create a table
    __tablename__ = 'Apartaments'
    images = db.Column(db.String)
    url = db.Column(db.String, primary_key = True)
    name = db.Column(db.String)
    area = db.Column(db.REAL)
    price = db.Column(db.REAL)
    currency = db.Column(db.String)
    rooms = db.Column(db.Integer)
    district = db.Column(db.String)
    city = db.Column(db.String)

    def __init__(self, images, url, name, area, price, currency, rooms, district, city) -> None:
        self.images = images
        self.url = url
        self.name = name
        self.area = area
        self.currency = currency
        self.price = price
        self.rooms = rooms
        self.district = district
        self.city = city

    def __repr__(self) -> str:
        return f"{self.name} {self.price} {self.currency}"

@app.route('/')
def main():

    return render_template('main_page.html')

@app.route("/our_team")
def team():

    return render_template('team_page.html')

@app.route('/search', methods = ["POST", "GET"], defaults = {'page': 5})
@app.route('/search/<int:page>', methods = ["GET", "POST"])
def search(page):

    pages = 5
    if request.method == 'POST':
        # Save filters into session
        session['filters'] = {
            'city': request.form.get('city_tag'),
            'district': request.form.get('district_tag'),
            'min_area': request.form.get('min_area_tag'),
            'max_area': request.form.get('max_area_tag'),
            'min_price': request.form.get('min_price_tag'),
            'max_price': request.form.get('max_price_tag'),
            'min_rooms': request.form.get('min_rooms_tag'),
            'max_rooms': request.form.get('max_rooms_tag'),
        }
        return redirect(url_for('search', page=page))

    # Get filters from session
    filters = session.get('filters', {})

    # Use filters to fetch data
    query = Apartament.query
    if filters.get('city'):
        query = query.filter(Apartament.city.like(filters['city']))
    if filters.get('district'):
        query = query.filter(Apartament.district.like(filters['district']))
    if filters.get('min_area'):
        query = query.filter(Apartament.area >= float(filters['min_area']))
    if filters.get('max_area'):
        query = query.filter(Apartament.area <= float(filters['max_area']))
    if filters.get('min_price'):
        query = query.filter(Apartament.price >= float(filters['min_price']))
    if filters.get('max_price'):
        query = query.filter(Apartament.price <= float(filters['max_price']))
    if filters.get('min_rooms'):
        query = query.filter(Apartament.rooms >= int(filters['min_rooms']))
    if filters.get('max_rooms'):
        query = query.filter(Apartament.rooms <= int(filters['max_rooms']))

    apartaments = query.paginate(per_page=pages, error_out = False)
    # session.clear()
    return render_template('search_page.html', apartaments=apartaments)

if __name__ == "__main__":
    data = DatabaseManipulation('./website/houses_test_db.db')
    # data.read_dictinary_to_objects_olx(parse_olx())
    data.read_dictinary_to_objects_dom(parser_dom())
    app.run(debug=True, use_reloader = False, threaded=True)
