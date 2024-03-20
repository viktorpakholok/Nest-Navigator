from bs4 import BeautifulSoup
import requests
import random
import json
import time
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

def parser_dom(pages_to_parse):
    all_time = time.time()
    dict_gen = {}

    count = 1
    url = 'https://dom.ria.com/uk/arenda-kvartir/?page='
    while count <= pages_to_parse:

        t_s = time.time()
        response = requests.get(url+str(count), headers=headers_)
        # print(time.time() - t_s)
        if response.status_code == 200:
            print(f'Success {count}!')

        else:
            print('An error has occurred')
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # with open('sth.txt', 'a', encoding='UTF-8') as file:
        #     file.write(str(soup))

        # with open('sth_1.txt', 'a', encoding='UTF-8') as file:
        #     file.write(f'{response.content}\n')

        # with open('sth_0.txt', 'a', encoding='UTF-8') as file:
        #     file.write(f'{soup}\n')


        loaded = json.loads('  {'+str(str(soup).split('  {', maxsplit=1)[1].split\
(']</script></div>', maxsplit=1)[0]))
        
        # with open('res.json', 'a', encoding='UTF-8') as file:
        #     json.dump(loaded, file, indent=4, ensure_ascii=False)
        #     file.write('\n')

        # dict_gen.extend(loaded['mainEntity']['itemListElement'][0]['offers']['offers'])
        for offer in loaded['mainEntity']['itemListElement'][0]['offers']['offers']:
            dict_gen[offer['url']] = offer

        count += 1
        # print(time.time()-t_s)
    print(f'all_time: {(time.time()-all_time)}, on_one: {(time.time()-all_time)/pages_to_parse}')
    return dict_gen

# parser_dom()