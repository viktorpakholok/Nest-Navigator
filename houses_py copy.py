"""HOuses"""
from sqlalchemy import create_engine, ForeignKey, Column, String, \
Integer, CHAR, ARRAY, BLOB, REAL, and_, true
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import os

with open("js.json", "r") as file:
    data_json = json.load(file)
    data_json = data_json['mainEntity']['itemListElement'][0]['offers']['offers']

with open('result.json', 'r') as file:
    data_json_olx = json.load(file)

# print(data_json)
Base = declarative_base()
class Apartament(Base):
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
            self.session.add(Apartament((",".join(dictinary["image"])), dictinary['url']\
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
            currency =  'UAH' if value['price'][-3:] == 'грн' else 'USD' if value['price'][-1] == '$' else 'EUR'
            self.session.add(Apartament(",".join(value['images']), value['url'], value['name'], float(value['square'][:-3]),\
    float("".join(value['price'][:-4].split(' '))) if currency == 'UAH' else float("".join(value['price'][:-2].split(' '))), currency, int(value['num_of_rooms'][:-8]), value['district'],value['city']))
        self.session.commit()
        # result = session.query(Apartament).all()
        # print(result)
# students = session.query(Student).filter(
#     and_(Student.id >= 100, Student.id <= 200,
#          Student.dob > '2000-01-01')).all()
    # read_dictinary_to_objects(data_json, 'houses3_db.db')

data = DatabaseManipulation('houses_test_db.db')
data.read_dictinary_to_objects_dom(data_json)
# data.read_dictinary_to_objects_olx(data_json_olx)
# print(data.get_filtered_data_dom((2000, 10000)))
