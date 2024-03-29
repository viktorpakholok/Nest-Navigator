from bs4 import BeautifulSoup
import requests
import random
import json
import time
import re

session = requests.Session()

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geck\
o) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, lik\
e Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geck\
o) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, lik\
e Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/\
108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, l\
ike Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like\
 Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; \
+http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36'
]

headers_ = {'Accept-Encoding': 'gzip', 'User-Agent': random.choice(user_agents)}
headers_['User-Agent'] = random.choice(user_agents)


def parser_olx(pages_to_read: int, adv_set: set):
    # dct_all = {}
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
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        with open('sth_3.txt', 'w', encoding='UTF-8') as file_:
            file_.write(repr(soup.find('script', id = 'olx-init-config').text))

        el = soup.find('script', id = 'olx-init-config').text.split('window.__PRERENDERED_STATE__= "', maxsplit=1)[1].split(',\\"metaData\\"', maxsplit=1)[0].replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', ' ').replace('\\\\u003Cbr \\\\u002F\\\\u003E\\\\n', '').replace('\\"', '"').replace('\\\\u002F', '/').replace('\\\\u003Cp\\\\u003E', '').replace('\\\\u003C/p\\\\u003E', ' ').replace('    ', '').replace('\\\\"', '"').replace(r'\\r\\n', ' ').replace('\\\\u003Cbr /\\> \\\\u003Cbr /\\> ', ' ')

        with open('sth_4.txt', 'w', encoding='UTF-8') as file_:
            file_.write(el)

        # with open('sth_7.txt', 'w', encoding='UTF-8') as file_:
        #     file_.write(str(re.findall('([^"])( |:)"([^"]*)"( |,|"|.)', el)))

        el = re.sub(r'"([^"]+)"([^:])', r"'\1'\2", el) + '}}}'

        

        t__s = time.time()
        # el = re.sub(r'([А-Яа-я]+)"([А-Яа-я]+)', r"\1'\2'", el)
        print(time.time() - t__s)

        # el = el.replace('"', "'").replace("','", '","').replace('":\'"', '":""').replace("\":' '",'":" "').replace('":\'."', '":" "').replace(' \',"', ' ","').replace("'},", '"},').replace("{'", '{"').replace("':{", '":{').replace("':", '":').replace("\":'", '":"').replace('\',"', '","').replace('":[\'', '":["').replace('\'],"', '"],"').replace('\']},{"', '"]},{"').replace('\'}],"', '"}],"').replace('\']}', '"]}').replace('\'}}', '"}}').replace('": ', "': ")\
# +'}}}'

        with open('sth_5.txt', 'w', encoding='UTF-8') as file_:
            file_.write(el)

        loaded = json.loads(el)['listing']['listing']['ads']

        # with open('res_0.json', 'w', encoding='UTF-8') as file_:
        #     json.dump(json.loads(el), file_, indent=4, ensure_ascii=False)

        for offer in loaded:
            adv_set.add((tuple(offer["photos"]), offer["url"], offer["title"], offer["params"][2]["normalizedValue"], offer["price"]["regularPrice"]["value"], offer["price"]["regularPrice"]["currencyCode"], offer["params"][4]["value"], offer["location"]["districtName"], offer["location"]["cityName"]))

        count += 1
    return adv_set


if __name__ == '__main__':
    t_s = time.time()

    res = parser_olx(100, set())
    with open('Bohdan.txt', 'w', encoding='UTF-8') as file:
        file.write(str(res))

    print(time.time() - t_s)

# .replace(",'",',"')