from bs4 import BeautifulSoup
import requests
import random
import json
import time

# headers = {'Accept-Encoding': 'gzip'}

session = requests.Session()

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]

headers_ = {'Accept-Encoding': 'gzip', 'User-Agent': random.choice(user_agents)}
headers_['User-Agent'] = random.choice(user_agents)

def parser_dom():
    # t_s = time.time()
    list_ = []

    count = 1
    url = 'https://dom.ria.com/uk/arenda-kvartir/?page='
    while count <= 5:

        response = requests.get(url+str(count), headers=headers_)

        # print(time.time() - t_s)
        # t_s = time.time()

        if response.status_code == 200:
            print(f'Success {count}!')
            count += 1
        else:
            print('An error has occurred')

        soup = BeautifulSoup(response.content, 'html.parser')

        # print(time.time() - t_s)
        # t_s = time.time()

        loaded = json.loads('  {'+str(str(soup).split('  {', maxsplit=1)[1].split(']</script></div>', maxsplit=1)[0]))

        list_.extend(loaded['mainEntity']['itemListElement'][0]['offers']['offers'])

        # print(time.time() - t_s)
        # print(json_object)
    # print(time.time() - t_s)
    return list_

# if __name__ == '__main__':
#     print(parser_dom())
