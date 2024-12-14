# Собираем все урлы товаров для парсинга из файла с урлами категорий и пишем
# в файл xls
import requests
import openpyxl
from openpyxl.reader.excel import load_workbook
import logging
from time import sleep
from bs4 import BeautifulSoup
import concurrent.futures
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PAGES = 20 #  Макс Кол-во сканируемых страниц
cat_file = 'cats_url.txt'

user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
with requests.Session() as session:
    session.post('https://www.tbmmarket.ru/', headers=user_agent)
    tbms = session.cookies['PHPSESSID_IM']
    cookies = {
        'cityID': '5984',
        'PHPSESSID_IM': tbms,
    }
def cats_links():
    file = open(cat_file, "r")
    lines = file.readlines()
    for line in lines:
        cat_link = line.strip()
        parser(cat_link)
    file.close


def write_to_xlsx(f_url):
    fn = 'prod_links.xlsx'
    wb = load_workbook(fn)
    ws = wb['data']
    ws.append(f_url)
    wb.save(fn)
    wb.close()


def parser(url):
    logging.info("Thread %s: starting", url)
    try:
        i =1
        while i < PAGES:
            cur_url = url + f"?page={i}"
            r = requests.get(cur_url, headers=user_agent, cookies=cookies, verify=False)
            if r.status_code == 200:
                html = r.content
                soup = BeautifulSoup(html, 'lxml')
                item_link = soup.find_all('a', class_="name_item")
                for link in item_link:
                    full_url = ['https://www.tbmmarket.ru' + str(link['href'])]
                    write_to_xlsx(full_url)
                    #print(full_url)
                i += 1
    except Exception:
        print('Запрос не выполнен')
    logging.info("Thread %s: finishing",url)

cats_links()