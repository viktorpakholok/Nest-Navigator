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

from bs4 import BeautifulSoup
import requests
import random
import json
import time
from urllib3 import PoolManager

http = PoolManager()

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

def parser_dom(pages_to_parse:int, adv_set:set):

    count = 1
    url = 'https://dom.ria.com/uk/arenda-kvartir/?page='
    while count <= pages_to_parse:

        response = requests.get(url+str(count), headers=headers_)
        if response.status_code == 200:
            print(f'Success {count}!')

        else:
            print('An error has occurred')
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        loaded = json.loads('  {'+str(str(soup).split('  {', maxsplit=1)[1].split\
(']</script></div>', maxsplit=1)[0]))
        
        for offer in loaded['mainEntity']['itemListElement'][0]['offers']['offers']:
            adv_set.add((tuple(offer['image']), offer['url'], offer['name'], offer['price'], offer['priceCurrency']))
            # dict_gen[offer['url']] = offer

        count += 1
    return adv_set

def parser_olx(pages_to_read:int, adv_set:set):
    count = 1
    url = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/\
dolgosrochnaya-arenda-kvartir/?currency=UAH&page='
    while count <= pages_to_read:

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
                print(url_off)
                response_1 = requests.get(url_off, headers=headers_)
                soup_1 = BeautifulSoup(response_1.content, 'html.parser')

                fir_name = soup_1.find('h4', class_ = 'css-1juynto')
                if fir_name:
                    dict_off['name'] = fir_name.get_text()
                else:
                    fir_name = soup_1.find('h4', class_ = 'css-1juynto')
                    if fir_name:
                        dict_off['name'] = fir_name.get_text()
                    else:
                        continue


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

                dict_off['images'] = [el['src'] for el in soup_1.find_all\
('img', class_ = 'css-1bmvjcs')]
                # print(dict_off)
                # dct_all[url_off] = dict_off
                adv_set.add((tuple(dict_off['images']), url_off, dict_off['name'], dict_off['square'], dict_off['price'], dict_off['num_of_rooms'], dict_off['district'], dict_off['city'], ))
        count += 1
    return adv_set


# if __name__ == '__main__':
#     parse_olx()

Base = declarative_base()

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
    def __init__(self, usd_to_uah:float, eur_to_uah:float):
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


    def read_set_to_objects_dom(self, adv_set:set):
        for dictinary in adv_set:
            if isinstance(dictinary[3], str):
                names = dictinary[2].split(',')[2:]
                if 'р‑н.' in names[2]:
                    area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()[0]), names[2][5:].strip(), names[3].strip()
                else:
                    area, rooms, district, city = float(names[0][:-5].strip()), int(names[1][:-5].strip()[0]), '', names[2].strip()
                price = float("".join(dictinary[3].split()))
                test = round(price/area, 1) if dictinary[4] == 'UAH' else round(price * self.usd_to_uah / area, 1) if dictinary[4]== 'USD' else round(price * self.eur_to_uah / area ,1)
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
            print(value)
            currency =  'UAH' if value[4][-4:-1] == 'грн' else 'USD' if \
                value[4][-1] == '$' else 'EUR'
            price = float("".join(value[4][:-5].split(' '))) if currency \
                    == 'UAH' else float("".join(value[4][:-2].split(' ')))
            area = float(value[3][:-3])
            self.session.add(Apartments(",".join(value[0]), value[1], \
value[2], area, price, currency, \
int(value[5][:-8]), value[6],value[7], round(price/area, 1) if currency == \
'UAH' else round(price * self.usd_to_uah / area, 1) if currency== 'USD' else round(price * self.eur_to_uah / area, 1)))
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
    dict1 = parser_dom(1, my_check_set)
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
