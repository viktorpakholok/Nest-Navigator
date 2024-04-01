"""HOuses"""
import os
import datetime
import pytz
import random
import json
import time
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, Column, String, Integer, REAL, func, update, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
import requests


# headers = {'Accept-Encoding': 'gzip'}

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

def parser_dom(pages_to_parse: int, adv_set: set, url_set:set):
    print('started: parser_dom')
    count = 1
    url = 'https://dom.ria.com/uk/arenda-kvartir/?page='
    while count <= pages_to_parse:

        response = requests.get(url+str(count), headers=headers_)
        if response.status_code == 200:
            print(f'Success {count}!')

        else:
            print('An error has occurred')
            # count += 1
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        loaded = json.loads('  {'+str(str(soup).split('  {', maxsplit=1)[1].split\
(']</script></div>', maxsplit=1)[0]))
        for offer in loaded['mainEntity']['itemListElement'][0]['offers']['offers']:
            if not offer['url'] in url_set:
                adv_set.add((tuple(offer['image']), offer['url'], offer['name'], \
offer['price'], offer['priceCurrency']))
                url_set.add(offer['url'])

        count += 1
    return adv_set

def parser_olx_new(num_of_pages:int, adv_set:set, url_set:set):
    print('started: parser_olx_new')
    url = "https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH&page=2&search%5Border%5D=created_at%3Adesc"
    count = 1
    while count <= num_of_pages:
        url = url.replace('page=2', f"page={count}")
        response = requests.get(url, headers=headers_)
        if response.status_code == 200:
            print(f'Success {count}!')
        else:
            print('An error has occurred')
            count += 1
            continue
        soup = BeautifulSoup(response.content, 'html.parser')
        el = soup.find('script', id = 'olx-init-config').text.split('window.__PRERENDERED_STATE__= "', maxsplit=1)[1].split(',\\"metaData\\"', maxsplit=1)[0].replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', ' ').replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', '').replace('\\"', '"').replace('\\\\u002F', '/').replace('\\\\u003Cp\\\\u003E', '').replace('\\\\u003C/p\\\\u003E', ' ').replace('    ', '').replace('\\\\"', '"').replace(r'\\r\\n', ' ')\

        el = el.replace('"', "'").replace('":\'"', '":""').replace("\":' '",'":" "').replace('":\'."', '":" "').replace(' \',"', ' ","').replace("'},", '"},').replace("{'", '{"').replace("':{", '":{').replace("':", '":').replace(",'",',"').replace("\":'", '":"').replace('\',"', '","').replace('":[\'', '":["').replace('\'],"', '"],"').replace('\']},{"', '"]},{"').replace('\'}],"', '"}],"').replace('\']}', '"]}').replace('\'}}', '"}}').replace('": ', "': ")+'}}}'

        try:
            loaded = json.loads(el)['listing']['listing']['ads']
        except Exception:
            count += 1
            continue
        for offer in loaded:
            area, rooms = 0, ''
            for val in offer['params']:
                if val['key'] == 'number_of_rooms_string':
                    rooms = val["value"]
                elif val['key'] == 'total_area':
                    area = val["normalizedValue"]
            if not offer['url'] in url_set:
                adv_set.add((tuple(offer["photos"]), offer["url"], offer["title"], area, offer["price"]["regularPrice"]["value"], offer["price"]["regularPrice"]["currencyCode"], rooms, offer["location"]["districtName"], offer["location"]["cityName"]))
                url_set.add(offer['url'])
        count += 1
    return adv_set

def parser_olx(adv_set:set, lower_price_bound:int, upper_price_bound:int, url_set:set):
    print('started: parser_olx')
    for i in range(lower_price_bound, upper_price_bound - 5, 5):
        count = 1
        url = f"https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH&page=2&search%5Bfilter_float_total_area%3Afrom%5D={i}&search%5Bfilter_float_total_area%3Ato%5D={i + 5}"
        response = requests.get(url, headers=headers_)
        soup = BeautifulSoup(response.content, 'html.parser')
        if soup.find_all('p', class_='css-1oc165u'):
            continue
        pages_to_read = soup.find_all('a', class_='css-1mi714g')
        pages_to_read = 1 if not pages_to_read else int(pages_to_read[-1].get_text())

        while count <= pages_to_read:
            url = url.replace('page=2', f"page={count}")
            response = requests.get(url, headers=headers_)

            if response.status_code == 200:
                print(f'Success {count}!')
            else:
                print('An error has occurred')
                count += 1
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            el = soup.find('script', id = 'olx-init-config').text.split('window.__PRERENDERED_STATE__= "', maxsplit=1)[1].split(',\\"metaData\\"', maxsplit=1)[0].replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', ' ').replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', '').replace('\\"', '"').replace('\\\\u002F', '/').replace('\\\\u003Cp\\\\u003E', '').replace('\\\\u003C/p\\\\u003E', ' ').replace('    ', '').replace('\\\\"', '"').replace(r'\\r\\n', ' ')\

            el = el.replace('"', "'").replace('":\'"', '":""').replace("\":' '",'":" "').replace('":\'."', '":" "').replace(' \',"', ' ","').replace("'},", '"},').replace("{'", '{"').replace("':{", '":{').replace("':", '":').replace(",'",',"').replace("\":'", '":"').replace('\',"', '","').replace('":[\'', '":["').replace('\'],"', '"],"').replace('\']},{"', '"]},{"').replace('\'}],"', '"}],"').replace('\']}', '"]}').replace('\'}}', '"}}').replace('": ', "': ")+'}}}'

            try:
                loaded = json.loads(el)['listing']['listing']['ads']
            except Exception:
                count += 1
                continue
            for offer in loaded:
                area, rooms = 0, ''
                for val in offer['params']:
                    if val['key'] == 'number_of_rooms_string':
                        rooms = val["value"]
                    elif val['key'] == 'total_area':
                        area = val["normalizedValue"]
                if not offer['url'] in url_set:
                    adv_set.add((tuple(offer["photos"]), offer["url"], offer["title"], area, offer["price"]["regularPrice"]["value"], offer["price"]["regularPrice"]["currencyCode"], rooms, offer["location"]["districtName"], offer["location"]["cityName"]))
                    url_set.add(offer['url'])
                # with open('olx_test.txt', 'a', encoding='utf-8') as file:
                #     file.write(str(a) + '\n\n')
            count += 1
    return adv_set

Base = declarative_base()

class Districts(Base):
    __tablename__ = "Districts"
    __table_args__ = {'schema': 'public'}
    city = Column(String(300), primary_key = True)
    districts = Column(String(1500))

    def __init__(self, city:str, districts:str) -> None:
        self.city = city
        self.districts = districts

    def __repr__(self) -> str:
        return f"{self.sity} {self.districts}"

class Url(Base):
    __tablename__ = "Url"
    __table_args__ = {'schema': 'public'}
    url = Column(String(500), primary_key = True)

    def __init__(self, url) -> None:
        self.url = url
    
    def __repr__(self) -> str:
        return str(self.url)

class Apartments(Base):
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

    def __init__(self, images, url, name, area, price, currency, rooms, district, city, price_per_meter):
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

    def __repr__(self):
        return f"{self.name} {self.price} {self.currency}"

class DatabaseManipulation:
    def __init__(self, usd_to_uah:float, eur_to_uah:float, Viktor_special = True):
        self.usd_to_uah = usd_to_uah
        self.eur_to_uah = eur_to_uah

        connection_string = URL.create('postgresql',
          username='Housesdb_owner',
          password='MOGU0lh5ByIg',
          host='ep-aged-pine-a29r8a5c.eu-central-1.aws.neon.tech',
          database='Housesdb',
        )

        engine = create_engine(connection_string, echo = True, pool_pre_ping = True, pool_recycle = 300)
        self.engine = engine
        self.insp = inspect(engine)
        if Viktor_special:
            Base.metadata.drop_all(engine)

        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()


    def read_set_to_objects_dom(self, adv_set:set):
        print('started: read_set_to_objects_dom')
        for dictinary in adv_set:
            names = dictinary[2].split(',')[2:]
            if isinstance(dictinary[3], str) and names[1][1].isnumeric():
                if 'р‑н.' in names[2]:
                    area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()[0]), names[2][5:].strip(), names[3].strip()
                else:
                    area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()[0]), '', names[2].strip()
                price = float("".join(dictinary[3].split()))
                test = round(price/area, 1) if dictinary[4] == 'UAH' else round(price * self.usd_to_uah / area, 1) if dictinary[4]== 'USD' else round(price * self.eur_to_uah / area ,1)
                if test < 29:
                    continue
                name = dictinary[2].split(',', maxsplit = 1)[1]
                self.session.add(Apartments((",".join(dictinary[0])), dictinary[1], name, area, price, dictinary[4],rooms, district, city, test))
        self.session.commit()


    def read_set_to_objects_olx(self, adv_set:set) -> None:
        '''
        Read selected Viktortype dictinary to the database. 
        Can make a new database or delete the existing one and make another.

        '''
        print('started: read_set_to_objects_olx')
        for value in adv_set:
            # currency =  'UAH' if value[4][-4:-1] == 'грн' else 'USD' if \
            #     value[4][-1] == '$' else 'EUR'
            price = value[4]
            area = float(value[3])
            self.session.add(Apartments(",".join(value[0]), value[1], value[2], area, price, value[5], \
int(value[6][:-8]), value[7],value[8], round(price/area, 1) if value[5] == \
'UAH' else round(price * self.usd_to_uah / area, 1) if value[5]== 'USD' else round(price * self.eur_to_uah / area, 1)))
        self.session.commit()

    def get_all_districts_and_cities(self) -> None:
        """
        Return all districts in a form of a dictionary

        {city : set of all districts}
        
        """
        if self.insp.has_table('Districts'):
            Districts.__table__.drop(self.engine)
            Base.metadata.create_all(bind=self.engine)

        query = self.session.query(Apartments).filter(Apartments.district!='')
        output_dictinary = {}
        for row in query:
            output_dictinary.setdefault(row.city, set()).add(row.district)
        for key, value in output_dictinary.items():
            self.session.add(Districts(key, ",".join(value)))
        self.session.commit()

    # def add_url_to_the_set(self, url_set:set, Viktor_special = False):
    #     if Viktor_special:
    #         Url.__table__.drop(self.engine)
    #         Base.metadata.create_all(bind=self.engine)
    #     for i in url_set:
    #         self.session.add(Url(i))
    #     self.session.commit()

    def read_url_to_set(self):
        query = self.session.query(Apartments)
        output_set = set()
        for i in query:
            output_set.add(i.url)
        return output_set

def start_parse(*args):
    database_url = DatabaseManipulation(38.81, 42, False)
    my_check_set = database_url.read_url_to_set()
    print(f'my_check_set: {my_check_set}')

    current_datetime = datetime.datetime.now()

    # Specify the desired time zone (e.g., Europe/Kiev)
    kiev_timezone = pytz.timezone('Europe/Kiev')

    # Convert the datetime to the specified time zone
    kiev_datetime = current_datetime.astimezone(kiev_timezone)

    current_time = int(kiev_datetime.strftime("%H"))

    print(f'current_time: {current_time}')

    if current_time == 3:
        #  Dom Ria
        my_check_set_ria = parser_dom(500, set(), my_check_set)

        #   OLX
        my_check_set_olx = parser_olx(set(), 10, 500, my_check_set)

        database = DatabaseManipulation(38.81, 42)
        database.read_set_to_objects_dom(my_check_set_ria)
        database.read_set_to_objects_olx(my_check_set_olx)

        print('One timer done!')
    elif 10 <= current_time <= 20:
        database = DatabaseManipulation(38.81, 42, False)
        new_dom_ria = parser_dom(15, set(), my_check_set)
        new_olx = parser_olx_new(15, set(), my_check_set)
        database.read_set_to_objects_dom(new_dom_ria)
        database.read_set_to_objects_olx(new_olx)
        
        print('Added during 10 - 20!')

    else:
        database = DatabaseManipulation(38.81, 42, False)
        
        new_dom_ria = parser_dom(5, set(), my_check_set)
        new_olx = parser_olx_new(5, set(), my_check_set)
        database.read_set_to_objects_dom(new_dom_ria)
        database.read_set_to_objects_olx(new_olx)
        print(f'my_check_set: {my_check_set}')
        print('Added during else!')
    database.get_all_districts_and_cities()

    return 'OK'
