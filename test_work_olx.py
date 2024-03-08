from bs4 import BeautifulSoup
import requests
import random
import json

# headers = {'Accept-Encoding': 'gzip'}

session = requests.Session()

# user_agents = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
#     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
# ]
user_agents = ['Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36']

headers_ = {'Accept-Encoding': 'gzip', 'User-Agent': random.choice(user_agents)}
headers_['User-Agent'] = random.choice(user_agents)
# session.headers.update({'User-Agent': headers_['User-Agent']})
# lst_ = []

dct_all = {}

with open('test.txt', 'w', encoding='UTF-8') as file:
    count = 1
    url = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/?currency=UAH&page='
    while count <= 1:
        # headers_['User-Agent'] = random.choice(user_agents)
        # response = session.get(url+str(count))
        response = requests.get(url+str(count), headers=headers_)
        # response = requests.get(url+str(count))
        file.write(f'\n\n{url+str(count)}\n')
        # print(response.content)

        if response.status_code == 200:
            print(f'Success {count}!')
        else:
            print('An error has occurred')

        soup = BeautifulSoup(response.content, 'html.parser')

        # Отримання заголовка сторінки
        title = soup.title.text
        # Отримання списку всіх посилань на сторінці
        links = []
        for link in soup.find_all('a'):
            text = link.get('href')
            if 'obyavlenie' in text:
                dict_off = {}
                print(text)
                links.append(text)
                url_add = 'https://www.olx.ua/d' if '/uk/' in text else 'https://www.olx.ua/d/uk'
                print(f'url_add: {url_add}')
                url_off = url_add + text[2:]
                print(url_off)
                response_1 = requests.get(url_off)
                soup_1 = BeautifulSoup(response_1.content, 'html.parser')
                with open('sth.txt', 'w', encoding='UTF-8') as file_:
                    file_.write(str(soup_1))

                    dict_off['name'] = soup_1.find('h4', class_ = 'css-1juynto').get_text()

                    price_text = soup_1.find('h3', class_ = 'css-12vqlj3').get_text()
                    if 'грн' in price_text:
                        dict_off['price'] = price_text[:-1]
                    else:
                        dict_off['price'] = price_text


                    # print()
                    # for el in soup_1.find_all('img', class_ = 'css-1bmvjcs'):
                    #     print(el['src'])

                    for el in soup_1.find_all('p', class_ = 'css-b5m1rv er34gjf0'):
                        # print(el.get_text())
                        get_t = el.get_text()
                        if 'Поверх: ' in get_t:
                            dict_off['floor'] = get_t.split('Поверх: ')[1]
                        elif 'Загальна площа: ' in get_t:
                            dict_off['square'] = get_t.split('Загальна площа: ')[1]
                        elif 'Кількість кімнат: ' in get_t:
                            dict_off['num_of_rooms'] = get_t.split('Кількість кімнат: ')[1]
                    for ind, el in enumerate(soup_1.find_all('a', class_ = 'css-tyi2d1')):
                        get_t = el.get_text()
                        # print(ind, get_t)
                        if ind == 5:
                            dict_off['city'] =  get_t.split(' - ')[1]
                        elif ind == 6:
                            dict_off['district'] =  get_t.split(' - ')[1]

                    dict_off['images'] = [el['src'] for el in soup_1.find_all('img', class_ = 'css-1bmvjcs')]
                # print(dict_off)
                dct_all[url_off] = dict_off
                # break
            # print(f'link: {link}')

        # lst_ads = []
        # for link in links:
        #     if links.count(link) > 4 and link not in lst_ads and 'realty' in link:
        #         lst_ads.append(link)

        # for i in lst_ads:
        #     print(i)
        # print('https://dom.ria.com'+lst_ads[0])
        # response_1 = session.get('https://dom.ria.com'+lst_ads[0])
        # response_1 = requests.get('https://dom.ria.com'+lst_ads[0], headers=headers_)
        # response_1 = requests.get('https://dom.ria.com'+lst_ads[0])
        # print(response_1.content)
        # soup_1 = BeautifulSoup(response_1.content, 'html.parser')
        # for data in soup_1.select:
        #     data.decompose()
        # with open('sth.txt', 'w', encoding='UTF-8') as file_:
        #     file_.write(str(soup_1))
        #     file_.write('\n\n')
            # file_.write(str(soup_1.find_all('h1')))
        # print(soup_1)
        # print(soup_1.find_all('h1'))
        # print(soup_1.select_one('h1'))
        # for tag in soup_1.find('h1', {"class":"m0 mb-20 size30"}):



        # for i in links:
        #     file.write(f'{i}\n')
        count += 1


with open('result.json', 'w', encoding='UTF-8') as json_file:
    json.dump(dct_all, json_file, indent=4, ensure_ascii=False)