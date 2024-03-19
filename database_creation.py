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

def parser_dom(num_of_pages:int):
    """
    Parse info from DIM.RIA
    """
    dict_gen = {}

    count = 1
    url = 'https://dom.ria.com/uk/arenda-kvartir/?page='
    while count <= num_of_pages:

        response = requests.get(url+str(count), headers=headers_)

        if response.status_code == 200:
            print(f'Success {count}!')

        else:
            print('An error has occurred')

        soup = BeautifulSoup(response.content, 'html.parser')


        loaded = json.loads('  {'+str(str(soup).split('  {', maxsplit=1)[1].split\
(']</script></div>', maxsplit=1)[0]))

        for offer in loaded['mainEntity']['itemListElement'][0]['offers']['offers']:
            dict_gen[offer['url']] = offer

        count += 1

    return dict_gen


def parse_olx(num_of_pages:int):
    """
    Parse info from OLX
    """
    dct_all = {}
    count = 1
    url = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/\
dolgosrochnaya-arenda-kvartir/?currency=UAH&page='
    while count <= num_of_pages:

        response = requests.get(url+str(count), headers=headers_)

        if response.status_code == 200:
            print(f'Success {count}!')
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


Base = declarative_base()

class Apartments(Base):
    __tablename__ = "Apartments"
    __table_args__ = {'schema': 'public'}
    images = Column(String(1000))
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
        return f"{self.number} {self.name} {self.price} {self.currency}"

class DatabaseManipulation:
    def __init__(self, database_uri:str, usd_to_uah:float, eur_to_uah:float):
        self.database_uri = database_uri
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

        Session = sessionmaker(bind=engine)
        self.session = Session()


    def read_dictinary_to_objects_dom(self, dictinary_list:dict):
        for key, dictinary in dictinary_list.items():
            names = dictinary['name'].split(',')[2:]
            if 'р‑н.' in names[2]:
                area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()), names[2][5:].strip(), names[3].strip()
            else:
                area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()), '', names[2].strip()
            price = float("".join(dictinary['price'].split()))
            test = round(price/area, 1) if dictinary['priceCurrency'] == 'UAH' else round(price * self.usd_to_uah / area, 1) if dictinary['priceCurrency']== 'USD' else round(price * self.eur_to_uah / area ,1)
            if test < 30:
                print(dictinary)
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
    postgresql = {'pguser' : 'HousesPost_gettingwe',
                  'pgpassword':'12021964',
                  'pghost':'25t.h.filess.io',
                  'pgport':'5433',
                  'pgdb':'HousesPost_gettingwe'}
    data = DatabaseManipulation(postgresql, 38.81, 42.28)
    data.read_dictinary_to_objects_dom(parser_dom(5))
