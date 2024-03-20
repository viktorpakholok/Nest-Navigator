"""HOuses"""
import random
import json
import time
from sqlalchemy.engine import URL
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
class Apartments(Base):
    '''
    How the table will be looking to the perspective 
    of every element
    '''
    __tablename__ = "Apartments"
    __table_args__ = {'schema': 'public'}
    images = Column(String(10000))
    url = Column(String(1000), primary_key=True)
    name = Column(String(1000))
    area = Column(REAL)
    price = Column(REAL)
    currency = Column(String(1000))
    rooms = Column(Integer)
    district = Column(String(1000))
    city = Column(String(1000))
    price_per_meter = Column(REAL)

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
    def __init__(self, usd_to_uah:float, eur_to_uah:float) -> None:
        self.usd_to_uah = usd_to_uah
        self.eur_to_uah = eur_to_uah
        connection_string = URL.create('postgresql',
          username='Housesdb_owner',
          password='MOGU0lh5ByIg',
          host='ep-aged-pine-a29r8a5c.eu-central-1.aws.neon.tech',
          database='Housesdb',
        )

        engine = create_engine(connection_string, echo = True)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind = engine)
        self.session = Session()


    def read_dictinary_to_objects_dom(self, dictinary_list:dict) -> None:
        '''
        Read selected Viktortype dictinary to the database. 
        Can make a new database or delete the existing one and make another.

        
        '''
        for key, dictinary in dictinary_list.items():
            names = dictinary['name'].split(',')[2:]
            if 'р‑н.' in names[2]:
                area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()[0]), names[2][5:].strip(), names[3].strip()
            else:
                area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()[0]), '', names[2].strip()
            price = float("".join(dictinary['price'].split()))
            test = round(price/area, 1) if dictinary['priceCurrency'] == 'UAH' else round(price * self.usd_to_uah / area, 1) if dictinary['priceCurrency']== 'USD' else round(price * self.eur_to_uah / area ,1)
            if test < 29:
                continue
            # print(dictinary['image'])
            self.session.add(Apartments((",".join(dictinary["image"])), key, dictinary['name'], area, price, dictinary['priceCurrency'],rooms, district, city, test))
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
            self.session.add(Apartments(",".join(value['images']), value['url'], \
value['name'], area, price, currency, \
int(value['num_of_rooms'][:-8]), value['district'],value['city'], round(price/area, 1) if currency == \
'UAH' else round(price * self.usd_to_uah / area, 1) if currency== 'USD' else round(price * self.eur_to_uah / area, 1)))
        self.session.commit()


if __name__ == "__main__":
    # dict_to_read = parser_dom(10)
    dict_to_read = parse_olx(50)
    data = DatabaseManipulation(38.81, 42.28)
    data.read_dictinary_to_objects_olx(dict_to_read)
    # data.read_dictinary_to_objects_dom(dict_to_read)
