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
from sqlalchemy import func, update
from bs4 import BeautifulSoup
import requests
import random
import json
import time
from urllib3 import PoolManager
import datetime
http = PoolManager()

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

def parser_dom(pages_to_parse: int, adv_set: set):

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
            adv_set.add((tuple(offer['image']), offer['url'], offer['name'], \
offer['price'], offer['priceCurrency']))

        count += 1
    return adv_set
def parser_olx_new(adv_set:set, num_of_pages:int):
    url = "https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH&page=2&search%5Border%5D=created_at%3Adesc"
    count = 1
    while count <= num_of_pages:
        url = url.replace('page=2', f"page={count}")
        response = requests.get(url, headers=headers_)
        if response.status_code == 200:
            print(f'Success {count}!')
        else:
            print('An error has occurred')
        soup = BeautifulSoup(response.content, 'html.parser')
        el = soup.find('script', id = 'olx-init-config').text.split('window.__PRERENDERED_STATE__= "', maxsplit=1)[1].split(',\\"metaData\\"', maxsplit=1)[0].replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', ' ').replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', '').replace('\\"', '"').replace('\\\\u002F', '/').replace('\\\\u003Cp\\\\u003E', '').replace('\\\\u003C/p\\\\u003E', ' ').replace('    ', '').replace('\\\\"', '"').replace(r'\\r\\n', ' ')\

        el = el.replace('"', "'").replace('":\'"', '":""').replace("\":' '",'":" "').replace('":\'."', '":" "').replace(' \',"', ' ","').replace("'},", '"},').replace("{'", '{"').replace("':{", '":{').replace("':", '":').replace(",'",',"').replace("\":'", '":"').replace('\',"', '","').replace('":[\'', '":["').replace('\'],"', '"],"').replace('\']},{"', '"]},{"').replace('\'}],"', '"}],"').replace('\']}', '"]}').replace('\'}}', '"}}').replace('": ', "': ")+'}}}'

        with open('1111122222333333.txt', 'w', encoding='utf-8') as file:
            file.write(el)
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
            adv_set.add((tuple(offer["photos"]), offer["url"], offer["title"], area, offer["price"]["regularPrice"]["value"], offer["price"]["regularPrice"]["currencyCode"], rooms, offer["location"]["districtName"], offer["location"]["cityName"]))
            count += 1
    return adv_set
def parser_olx(adv_set:set, lower_price_bound:int, upper_price_bound:int):
    for i in range(lower_price_bound, upper_price_bound - 5, 5):
        count = 1
        url = f"https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH&page=2&search%5Bfilter_float_total_area%3Afrom%5D={i}&search%5Bfilter_float_total_area%3Ato%5D={i + 5}"
        response = requests.get(url, headers=headers_)
        soup = BeautifulSoup(response.content, 'html.parser')
        if soup.find_all('p', class_='css-1oc165u'):
            continue
        pages_to_read = soup.find_all('a', class_='css-1mi714g')
        pages_to_read = 1 if not pages_to_read else int(pages_to_read[-1].get_text())
        # pages_to_read = int(soup.find_all('a', class_='css-1mi714g')[-1].get_text())

        while count <= pages_to_read:
            url = url.replace('page=2', f"page={count}")
            response = requests.get(url, headers=headers_)

            if response.status_code == 200:
                print(f'Success {count}!')
            else:
                print('An error has occurred')

            soup = BeautifulSoup(response.content, 'html.parser')
            el = soup.find('script', id = 'olx-init-config').text.split('window.__PRERENDERED_STATE__= "', maxsplit=1)[1].split(',\\"metaData\\"', maxsplit=1)[0].replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', ' ').replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', '').replace('\\"', '"').replace('\\\\u002F', '/').replace('\\\\u003Cp\\\\u003E', '').replace('\\\\u003C/p\\\\u003E', ' ').replace('    ', '').replace('\\\\"', '"').replace(r'\\r\\n', ' ')\

            el = el.replace('"', "'").replace('":\'"', '":""').replace("\":' '",'":" "').replace('":\'."', '":" "').replace(' \',"', ' ","').replace("'},", '"},').replace("{'", '{"').replace("':{", '":{').replace("':", '":').replace(",'",',"').replace("\":'", '":"').replace('\',"', '","').replace('":[\'', '":["').replace('\'],"', '"],"').replace('\']},{"', '"]},{"').replace('\'}],"', '"}],"').replace('\']}', '"]}').replace('\'}}', '"}}').replace('": ', "': ")+'}}}'

            with open('1111122222333333.txt', 'w', encoding='utf-8') as file:
                file.write(el)
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
                adv_set.add((tuple(offer["photos"]), offer["url"], offer["title"], area, offer["price"]["regularPrice"]["value"], offer["price"]["regularPrice"]["currencyCode"], rooms, offer["location"]["districtName"], offer["location"]["cityName"]))

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

        engine = create_engine(connection_string, echo = True)
        if Viktor_special:
            Base.metadata.drop_all(engine)

        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()


    def read_set_to_objects_dom(self, adv_set:set):
        for dictinary in adv_set:
            print(dictinary)
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
        for value in adv_set:
            print(value)
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
        Return all districts in a form of a dictinary

        {city : set of all districts}
        
        """
        query = self.session.query(Apartments).filter(Apartments.district!='')
        output_dictinary = {}
        for row in query:
            output_dictinary.setdefault(row.city, set()).add(row.district)
        for key, value in output_dictinary.items():
            self.session.add(Districts(key, ",".join(value)))
        self.session.commit()


def one_timer():

    #  Dom Ria

    dom_set = parser_dom(500, set())
    database = DatabaseManipulation(38.81, 42)
    database.read_set_to_objects_dom(dom_set)

    #   OLX

    database.read_set_to_objects_olx(parser_olx(set(), 10, 150))

    print('One timer done!')

def during_the_day():
    for i in range(150, 500, 50):
        database = DatabaseManipulation(38.81, 42, False)
        database.read_set_to_objects_olx(parser_olx(set(), i, i + 49))
    print('During the day done!')


def add_during_the_day():
    """
    Update the database
    """
    current_time = int(time.strftime("%H:%M:%S").split(':')[0])
    the_set=set()
    if 10 < current_time < 23:
        parser_olx_new(the_set, 15)
        parser_dom(the_set, 15)
    else:
        parser_olx_new(the_set, 5)
        parser_dom(the_set, 5)


if __name__ == "__main__":
    my_check_set = set()
    start = time.time()
    my_check_set = parser_olx(set(), 10, 500)
    # print(my_check_set)
    # dict1 = parser_dom(500, my_check_set)
    # print(dict1)
    # print(dict1)
    # set2 = parser_olx1(1, my_check_set)
    # start = time.time()
    # set2 = parser_olx(10, my_check_set)
    # t = time.time() - start
    # # print(set2)
    # # print(t)
    # # print(set2)
    data = DatabaseManipulation(38.81, 42.28)
    data.read_set_to_objects_olx(my_check_set)
    # # print(set2)
    # print(t)
    # data.read_set_to_objects_dom(dict1)
    data.get_all_districts_and_cities()
    # print(t)
    # data.get_all_districts_and_cities()
    # data.fix_the_database()
    # start = time.time()
    # set2 = parser_olx1(1, my_check_set)

    # fehbfr = data.get_1()
    # dick = data.get_all_districts_and_cities()
    # print(dick)
    # print(set2)
    # print(t)
    # print(dict1)
    # https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH&search%5Bfilter_float_total_area%3Afrom%5D=20&search%5Bfilter_float_total_area%3Ato%5D=21
    # https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH&page=3&search%5Bfilter_float_total_area%3Afrom%5D=20&search%5Bfilter_float_total_area%3Ato%5D=21
    # https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH&page=2&search%5Bfilter_float_total_area%3Afrom%5D=20&search%5Bfilter_float_total_area%3Ato%5D=21
