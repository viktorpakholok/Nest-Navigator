"""HOuses"""
from flask import Flask, request, render_template, Blueprint, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json
import os
from sqlalchemy import create_engine, ForeignKey, Column, String, \
Integer, CHAR, ARRAY, BLOB, REAL, and_, true
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random
# with open("js.json", "r") as file:
#     data_json = json.load(file)
#     data_json = data_json['mainEntity']['itemListElement'][0]['offers']['offers']
#     print(data_json)

# with open('result.json', 'r') as file:
#     data_json_olx = json.load(file)


#######################################################################################################################

from bs4 import BeautifulSoup
import requests
import random
import json

# headers = {'Accept-Encoding': 'gzip'}

session1 = requests.Session()

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]
# user_agents = ['Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; \
# Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36']

headers_ = {'Accept-Encoding': 'gzip', 'User-Agent': random.choice(user_agents)}
headers_['User-Agent'] = random.choice(user_agents)
# session.headers.update({'User-Agent': headers_['User-Agent']})
# lst_ = []

dct_all = {}

def parser_dom():
    # t_s = time.time()
    list_ = []

    count = 1
    url = 'https://dom.ria.com/uk/arenda-kvartir/?page='
    while count <= 400:

        response = requests.get(url+str(count), headers=headers_)

        # print(time.time() - t_s)
        # t_s = time.time()

        if response.status_code == 200:
            print(f'Success {count}!')
            count += 1
        else:
            print('An error has occurred')

        soup = BeautifulSoup(response.content, 'html.parser')

        # print(time.time() - t_s)
        # t_s = time.time()

        loaded = json.loads('  {'+str(str(soup).split('  {', maxsplit=1)[1].split(']</script></div>', maxsplit=1)[0]))

        list_.extend(loaded['mainEntity']['itemListElement'][0]['offers']['offers'])

        # print(time.time() - t_s)
        # print(json_object)
    # print(time.time() - t_s)
    return list_


def parse_olx():
    count = 1
    url = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/\
dolgosrochnaya-arenda-kvartir/?currency=UAH&page='
    while count <= 1:

        response = requests.get(url+str(count), headers=headers_)

        if response.status_code == 200:
            print(f'Success {count}!')
            # pass
        else:
            print('An error has occurred')

        soup = BeautifulSoup(response.content, 'html.parser')

        links = []
        for link in soup.find_all('a'):
            text = link.get('href')
            if 'obyavlenie' in text:
                dict_off = {}
                links.append(text)
                url_add = 'https://www.olx.ua/d' if '/uk/' in text else 'https://www.olx.ua/d/uk'
                # print(f'url_add: {url_add}')
                url_off = url_add + text[2:]
                # print(url_off)
                response_1 = requests.get(url_off, headers=headers_)
                soup_1 = BeautifulSoup(response_1.content, 'html.parser')

                dict_off['url'] = url_off

                dict_off['name'] = soup_1.find('h4', class_ = 'css-1juynto').get_text()

                dict_off['price'] = soup_1.find('h3', class_ = 'css-12vqlj3').get_text()

                for el in soup_1.find_all('p', class_ = 'css-b5m1rv er34gjf0'):

                    get_t = el.get_text()
                    if 'Поверх: ' in get_t:
                        dict_off['floor'] = get_t.split('Поверх: ')[1]
                    elif 'Загальна площа: ' in get_t:
                        dict_off['square'] = get_t.split('Загальна площа: ')[1]
                    elif 'Кількість кімнат: ' in get_t:
                        dict_off['num_of_rooms'] = get_t.split('Кількість кімнат: ')[1]
                for ind, el in enumerate(soup_1.find_all('a', class_ = 'css-tyi2d1')):
                    get_t = el.get_text()
                    dict_off['district'] = ''
                    # print(ind, get_t)
                    if ind == 5:
                        dict_off['city'] =  get_t.split(' - ')[1]
                    elif ind == 6:
                        dict_off['district'] =  get_t.split(' - ')[1]

                dict_off['images'] = [el['src'] for el in soup_1.find_all('img', class_ = 'css-1bmvjcs')]
                # print(dict_off)
                dct_all[len(dct_all)] = dict_off
                with open('result.json', 'w', encoding='UTF-8') as json_file:
                    json.dump(dct_all, json_file, indent=4, ensure_ascii=False)
                # break
        count += 1
    return dct_all

# with open('result.json', 'w', encoding='UTF-8') as json_file:
#     json.dump(dct_all, json_file, indent=4, ensure_ascii=False)


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
            print(dictinary)
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

@app.route('/', methods = ["POST", "GET"], defaults = {'page': 5})
@app.route('/<int:page>', methods = ["GET", "POST"])
def index(page):
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
        return redirect(url_for('index', page=page))

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

    apartaments = query.paginate(page, pages, error_out = False)
    # session.clear()
    return render_template('index.html', apartaments=apartaments)

if __name__ == "__main__":
    data = DatabaseManipulation('houses_test_db.db')
    # data.read_dictinary_to_objects_olx(parse_olx())
    data.read_dictinary_to_objects_dom(parser_dom())
    app.run(debug=True, use_reloader = False)
