#!/usr/bin/python3
import logging
import concurrent.futures
import requests
import pymysql
#import tldextract
import re
import ssl
import openpyxl
from openpyxl.reader.excel import load_workbook
import urllib3
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def writesql(price,quantity,stock,product_id):
    connection = pymysql.connect(
        host='localhost',
        user='optkds',
        password='1234',
        db='optkds',
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    with connection.cursor() as cursor:
        query = 'UPDATE oc_product SET quantity = '+str(quantity)+', stock_status_id = '+str(stock)+', date_modified = current_date() WHERE product_id = '+str(product_id)
        cursor.execute(query)
        connection.commit()
    connection.close()
    print(query)

def writexls(name,url,qty,oldprice,newprice):
    datastr = [name,url,qty,oldprice,newprice]
    fn = 'price.xlsx'
    wb = load_workbook(fn)
    ws = wb['data']
    ws.append(datastr)
    wb.save(fn)
    wb.close()

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
marg = dict()
pname = dict()
oldprice = dict()

with connection.cursor() as cursor:
    query = 'UPDATE oc_product SET stock_status_id = 5, quantity = 0 WHERE upc LIKE "%tbm.ru%"'
    cursor.execute(query)
    query = 'SELECT * FROM oc_product p, oc_product_description pd WHERE p.product_id = pd.product_id AND p.upc LIKE "%tbm.ru%"'
    cursor.execute(query)
    for row in cursor:
        urls[row['product_id']] = row['upc']
        minimum[row['product_id']] = row['minimum']
        pname[row['product_id']] = row['name']
        oldprice[row['product_id']] = row['price']
connection.close()



payload={'j_username': "somkd@yandex.ru",'j_password': "Bnn2208@3"}
response = requests.post('https://www.tbm.ru/tbm-online/j_spring_security_check', data=payload)
jsession = response.cookies['JSESSIONID_OLP']

def thread_function(product_id):
    logging.info("Thread %s: starting", product_id)
    value = urls[product_id]
    #ext = tldextract.extract(value)
    #domain = ext.domain
    print(value)
    try:
        cookies = {'JSESSIONID_OLP': jsession}
        r = requests.get(value, headers=headers, cookies=cookies, timeout=15, verify=False)
        html = r.content
        soup = BeautifulSoup(html, 'lxml')
        availability = soup.select_one('.cat-product__for-order')
        availability_s = availability.span.string
        availability_re = re.findall(r'\d+', availability_s)
        if availability_re[0]:
            availability_int = availability_re[0]
            stock_status_id = 1
        else:
            availability_int = 0
            stock_status_id = 5

        print(availability_int)

        price = soup.select_one('.cat-product__price__new-price__count')
        price = price.string.replace(' ', '')

        price_int = float(price)
        print('Price - ' + str(price_int))
        if availability_int:
            if price_int:
                # price_new = round((price_int+(price_int*(marg[product_id]/100)))*minimum[product_id])
               # price_new = round(price_int+(price_int*(marg[product_id]/100)))
                price_new = round(price_int+(price_int*(30/100)))
                print(price_new)
                print(availability_int)
                writesql(price_int,availability_int,stock_status_id,product_id)
               # writexls(pname[product_id], urls[product_id],availability_int, oldprice[product_id], price_int)
            else:
                special = false

    except Exception:
        print('Запрос не выполнен')
    logging.info("Thread %s: finishing",product_id)

#запуск потоков
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(thread_function, urls)
