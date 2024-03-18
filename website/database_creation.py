"""HOuses"""
import os
import random
import json
from sqlalchemy import create_engine, Column, String, Integer, REAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
import requests

from static.parsers.ria_parser import parser_dom
from static.parsers.test_work_olx import parse_olx

session = requests.Session()

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like \
Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,\
 like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like \
Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,\
 like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chr\
ome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTM\
L, like Gecko) Version/16.1 Safari/605.1.15'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, \
like Gecko) Version/16.1 Safari/605.1.15'
]

headers_ = {'Accept-Encoding': 'gzip', 'User-Agent': random.choice(user_agents)}
headers_['User-Agent'] = random.choice(user_agents)



Base = declarative_base()
class Apartaments(Base):
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
    price_per_meter = Column('price_per_meter', REAL)

    def __init__(self, images, url, name, area, price, currency, rooms, district, city, price_per_meter) -> None:
        self.images = images
        self.url = url
        self.name = name
        self.area = area
        self.currency = currency
        self.price = price
        self.rooms = rooms
        self.district = district
        self.city = city
        self.price_per_meter = price_per_meter

    def __repr__(self) -> str:
        return f"{self.number} {self.name} {self.price} {self.currency}"


class DatabaseManipulation:
    '''Do smth with a database'''
    def __init__(self, database_name:str, usd_to_uah:float, eur_to_uah:float) -> None:
        self.database_name = database_name
        self.usd_to_uah = usd_to_uah
        self.eur_to_uah = eur_to_uah
        if os.path.exists(database_name):
            os.remove(database_name)

        engine = create_engine(f"sqlite:///{database_name}", echo = True)
        Base.metadata.create_all(bind = engine)

        Session = sessionmaker(bind = engine)
        self.session = Session()


    def rename_and_delete(self):
        """
        Rename the database to havi an app working anytime
        """
        if os.path.exists(self.database_name):
            os.remove(self.database_name)
        if os.path.exists(f"new_{self.database_name}"):
            os.rename(f"new_{self.database_name}", self.database_name)


    def read_dictinary_to_objects_dom(self, dictinary_list:dict) -> None:
        '''
        Read selected Viktortype dictinary to the database. 
        Can make a new database or delete the existing one and make another.

        
        '''

        for key, dictinary in dictinary_list.items():
            # print(dictinary)
            names = dictinary['name'].split(',')[2:]
            if 'р‑н.' in names[2]:
                area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()),\
                names[2][5:].strip(), names[3].strip()
            else:
                area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()),\
                '', names[2].strip()
            price = float("".join(dictinary['price'].split()))
            test = round(price/area, 1) if dictinary['priceCurrency'] == 'UAH' else round(price * self.usd_to_uah /
area, 1) if dictinary['priceCurrency']== 'USD' else round(price * self.eur_to_uah / area ,1)
            if test < 100:
                print(dictinary)
                with open('test.json', 'a', encoding='UTF-8') as file__:
                    json.dump(dictinary, file__, indent=4, ensure_ascii=False)
            self.session.add(Apartaments((",".join(dictinary["image"])), key\
                                , dictinary['name'], area, price, dictinary['priceCurrency'],rooms,\
district, city, round(price/area, 1) if dictinary['priceCurrency'] == 'UAH' else round(price * self.usd_to_uah /
area, 1) if dictinary['priceCurrency']== 'USD' else round(price * self.eur_to_uah / area ,1)))
        self.session.commit()

    def read_dictinary_to_objects_olx(self, dictinary_list:dict) -> None:
        '''
        Read selected Viktortype dictinary to the database. 
        Can make a new database or delete the existing one and make another.

        '''
        for value in dictinary_list.values():
            print(value)
            currency =  'UAH' if value['price'][-4:-1] == 'грн' else 'USD' if \
                value['price'][-1] == '$' else 'EUR'
            price = float("".join(value['price'][:-5].split(' '))) if currency \
                    == 'UAH' else float("".join(value['price'][:-2].split(' ')))
            area = float(value['square'][:-3])
            self.session.add(Apartaments(",".join(value['images']), value['url'], \
value['name'], area, price, currency, \
int(value['num_of_rooms'][:-8]), value['district'],value['city'], round(price/area, 1) if currency == \
'UAH' else round(price * self.usd_to_uah / area, 1) if currency== 'USD' else round(price * self.eur_to_uah / area, 1)))
        self.session.commit()


if __name__ == "__main__":
    data = DatabaseManipulation('./website/houses_test_test_db.db', 38.81, 42.28)
    # data.rename_and_delete()
    data.read_dictinary_to_objects_dom(parser_dom(10))
    # data.read_dictinary_to_objects_olx(parse_olx(1))
    # data.read_dictinary_to_objects_dom()
    # data.rename_and_delete()