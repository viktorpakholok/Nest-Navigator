from bs4 import BeautifulSoup
import requests
import random
import json


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
                adv_set.add((tuple(dict_off['images']), url_off, dict_off['name'], \
dict_off['square'], dict_off['price'], dict_off['num_of_rooms'], \
dict_off['district'], dict_off['city'], ))

                # with open('result.json', 'w', encoding='UTF-8') as json_file:
                #     json.dump(dct_all, json_file, indent=4, ensure_ascii=False)

                # break
        count += 1
    return adv_set


# if __name__ == '__main__':
#     parse_olx()
