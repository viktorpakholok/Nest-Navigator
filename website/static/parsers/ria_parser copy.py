from bs4 import BeautifulSoup
import requests
import random
import json
import time
import codecs
from urllib3 import PoolManager

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

url = 'https://dom.ria.com/uk/arenda-kvartir/?page='

response = requests.get('https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH', headers=headers_)

# if response.status_code == 200:
#     print(f'Success {count}!')

# else:
#     print('An error has occurred')
#     continue

soup = BeautifulSoup(response.content, 'html.parser')


# with open('sth_3.txt', 'w', encoding='UTF-8') as file:
#     file.write(repr(el.split(',"metaData":')[0]))

# with open('sth.txt', 'w', encoding='UTF-8') as file:
#     file.write(el)

# print(json.loads(el))

# with open('res.json', 'w', encoding='UTF-8') as file:
#     json.dump(json.loads(el), file, indent=4, ensure_ascii=False)

el = soup.find('script', id = 'olx-init-config')

loaded = json.loads(el.text.split('window.__PRERENDERED_STATE__= "', maxsplit=1)[1].split(',\\"metaData\\"', maxsplit=1)[0].replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', ' ').replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', '').replace('\\"', '"').replace('\\\\u002F', '/').replace('\\\\u003Cp\\\\u003E', '').replace('\\\\u003C/p\\\\u003E', ' ').replace('    ', '').replace('\\\\"', '"').replace(r'\\r\\n', ' ')\
.replace('"', "'").replace('":\'"', '":""').replace("\":' '",'":" "').replace('":\'."', '":" "').replace(' \',"', ' ","').replace("'},", '"},').replace("{'", '{"').replace("':{", '":{').replace("':", '":').replace(",'",',"').replace("\":'", '":"').replace('\',"', '","').replace('":[\'', '":["').replace('\'],"', '"],"').replace('\']},{"', '"]},{"').replace('\'}],"', '"}],"').replace('\']}', '"]}').replace('\'}}', '"}}')+'}}}')['listing']['listing']['ads']

# with open('res.json', 'a', encoding='UTF-8') as file:
#     json.dump(loaded, file, indent=4, ensure_ascii=False)
#     file.write('\n')

# dict_gen.extend(loaded['mainEntity']['itemListElement'][0]['offers']['offers'])
#     for offer in loaded['mainEntity']['itemListElement'][0]['offers']['offers']:
#         adv_set.add((tuple(offer['image']), offer['url'], offer['name'], \
# offer['price'], offer['priceCurrency']))
    # dict_gen[offer['url']] = offer

# print(time.time()-t_s)
# print(f'all_time: {(time.time()-all_time)}, on_one: {(time.time()-all_time)/pages_to_parse}')


# parser_dom()