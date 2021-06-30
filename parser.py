import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sys

headers = {'user-agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
           '(KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
           'accept':
           '*/*'}


def get_content(url, param):
    html = requests.get(url, headers=headers)
    return html


def get_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='dtList-inner')
    if items:
        goods = []
        tag = u'\xa0'
        for item in items:
            if item.find('span', class_='c-stars-line-lg'):
                rate = int(
                    re.findall(
                        r'\d',
                        str(item.find('span', class_='c-stars-line-lg')))[0])
            else:
                rate = 'Нет оценок'
            if item.find('span', class_='lower-price'):
                price = int(
                    item.find(
                        'span', class_='lower-price').get_text().replace(
                        tag, '')[1:-1])
            else:
                price = int(
                    item.find(
                        'ins', class_='lower-price').get_text().replace(
                        tag, '')[1:-1])
            goods.append({
                'title': item.find('span', class_='goods-name').get_text(),
                'brand': item.find(
                    'strong', class_='brand-name').get_text()[:-3],
                'price': price,
                'rate': rate,
            })
        return goods
    else:
        return False


def parse(url):
    res = []
    page = 1
    while True:
        html = get_content(url, param={'page': page})
        if html.status_code == 200:
            info = get_info(html.content)
            if not info:
                break
            res.append(info)
        else:
            print('problem')
        page += 1
    return res


def save(data, file):
    res_dict = {'title': [], 'brand': [], 'price': [], 'rate': []}
    for items in data:
        for item in items:
            res_dict['title'].append(item['title'])
            res_dict['brand'].append(item['brand'])
            res_dict['price'].append(item['price'])
            res_dict['rate'].append(item['rate'])

    df = pd.DataFrame(res_dict)
    with pd.ExcelWriter(file) as writer:
        df.to_excel(writer)


def main(url, file):
    result = parse(url)
    save(result, file)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
