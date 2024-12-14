#!/usr/bin/python3
import logging
import concurrent.futures
import requests
import pymysql
import tldextract
import re
import ssl
import urllib3
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
from pymysql.cursors import DictCursor
connection = pymysql.connect(
    host='localhost',
    user='userKash_optkd',
    password='gKL3102gKL3102',
    db='userKash_optkd',
    charset='utf8mb4',
    cursorclass=DictCursor
)
print("Hello from losst!")
connection.close()