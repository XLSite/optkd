#!/usr/bin/python3
import logging
import concurrent.futures
import requests
import pymysql
#import tldextract
import re
import ssl
import urllib3
from bs4 import BeautifulSoup
#from requests.packages.urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def writesql(price, product_id):
    connection = pymysql.connect(
        host='localhost',
        user='optkds',
        password='1234',
        db='optkds',
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    with connection.cursor() as cursor:
        query = 'UPDATE oc_product SET price = '+str(price)+' WHERE product_id = '+str(product_id)
        cursor.execute(query)
        connection.commit()
    connection.close()
    print(query)

from pymysql.cursors import DictCursor
connection = pymysql.connect(
    host='localhost',
    user='optkds',
    password='1234',
    db='optkds',
    charset='utf8mb4',
    cursorclass=DictCursor
)

urls = dict()
minimum = dict()
typepr = dict()

with connection.cursor() as cursor:
    query = 'SELECT * FROM oc_product WHERE upc LIKE "%tbm.ru%" AND product_id = "3005731" '
    cursor.execute(query)
    for row in cursor:
        urls[row['product_id']] = row['upc']
        typepr[row['product_id']] = row['isbn']

connection.close()
user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
with requests.Session() as session:
    session.post('https://www.tbm.ru/', headers=user_agent)
    cookies = {
        'TBM_TOWN': '1',
    }

def thread_function(product_id):
    logging.info("Апдейт ID = %s: starting", product_id)
    value = urls[product_id]
    ptype = typepr[product_id]
    try:
        r = requests.get(value, headers=user_agent, cookies=cookies, timeout=15, verify=False)
        html = r.content
        soup = BeautifulSoup(html, 'lxml')
        price = soup.select_one('.cat-product__price__new-price__count')
        price = price.string.replace(' ', '')
        price_int = float(price)
        price_new = round(price_int - (price_int * 0.07))

        if ptype == '3':
            price_out = price_new/100
        else:
            price_out = price_new

        print(price_out)

        writesql(price_out, product_id)

    except Exception:
        print('Запрос не выполнен')

    logging.info("Апдейт ID = %s: finishing",product_id)

#запуск потоков
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(thread_function, urls)
