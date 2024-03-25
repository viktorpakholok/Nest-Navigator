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
from static.parsers.test_work_olx import parser_olx

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


    def read_set_to_objects_dom(self, adv_set:set):
        '''
        Read selected Viktortype dictinary to the database. 
        Can make a new database or delete the existing one and make another.

        
        '''
        for dictinary in adv_set:
            if isinstance(dictinary[3], str):
                names = dictinary[2].split(',')[2:]
                if 'р‑н.' in names[2]:
                    area, rooms, district, city = float(names[0][:-5].strip()), \
        int(names[1][:-5].strip()[0]), names[2][5:].strip(), names[3].strip()
                else:
                    area, rooms, district, city = float(names[0][:-5].strip()), \
        int(names[1][:-5].strip()[0]), '', names[2].strip()
                price = float("".join(dictinary[3].split()))
                test = round(price/area, 1) if dictinary[4] == 'UAH' else round(price * \
        self.usd_to_uah / area, 1) if dictinary[4]== 'USD' else \
        round(price * self.eur_to_uah / area ,1)
                if test < 29:
                    continue
                self.session.add(Apartments((",".join(dictinary[0])), dictinary[1], dictinary[2], area, price, dictinary[4],rooms, district, city, test))
        self.session.commit()


    def read_set_to_objects_olx(self, adv_set:set) -> None:
        '''
        Read selected Viktortype dictinary to the database. 
        Can make a new database or delete the existing one and make another.

        '''
        for value in adv_set:
            # print(value)
            currency =  'UAH' if value[4][-4:-1] == 'грн' else 'USD' if \
                value[4][-1] == '$' else 'EUR'
            price = float("".join(value[4][:-5].split(' '))) if currency \
                    == 'UAH' else float("".join(value[4][:-2].split(' ')))
            area = float(value[3][:-3])
            self.session.add(Apartments(",".join(value[0]), value[1], \
value[2], area, price, currency, \
int(value[5][:-8]), value[6],value[7], round(price/area, 1) if currency == \
'UAH' else round(price * self.usd_to_uah / area, 1) if currency== 'USD' else \
round(price * self.eur_to_uah / area, 1)))
        self.session.commit()


    def get_all_districts_and_cities(self) -> dict:
        """
        Return all districts in a form of a dictinary

        {city : set of all districts}
        
        """
        query = self.session.query(Apartments).filter(Apartments.district!='')
        output_dictinary = {}
        for row in query:
            output_dictinary.setdefault(row.city, set()).add(row.district)
        return output_dictinary
            # output_dictinary.setdefault()

if __name__ == "__main__":
    my_check_set = set()
    dict1 = parser_dom(5, my_check_set)
    # print(dict1)
    # set2 = parser_olx(1, my_check_set)
    # print(set2)
    data = DatabaseManipulation(38.81, 42.28)
    # data.read_set_to_objects_olx(set2)
    # start = time.time()
    data.read_set_to_objects_dom(dict1)
    dick = data.get_all_districts_and_cities()
    print(dick)
    # print(time.time() - start)
    # print(dict1)
