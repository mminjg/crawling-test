from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import pymysql
import os

# dotenv
load_dotenv(verbose=True)
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PW = os.getenv('MYSQL_PW')
MYSQL_DB = os.getenv('MYSQL_DB')
MYSQL_CHARSET = os.getenv('MYSQL_CHARSET')

# yes24 크롤링
driver = webdriver.Chrome(executable_path="/Users/user/Downloads/chromedriver")
url = 'http://ticket.yes24.com/New/Notice/NoticeMain.aspx'
driver.get(url)
soup = BeautifulSoup(driver.page_source, 'html.parser')
info_list = []

for tr in soup.find_all('tr')[1:]:
    type = tr.select('td')[0].text.strip()
    if type != "티켓오픈":
        continue
    title = tr.select('td')[1].text.strip()
    dateStr = tr.select('td')[2].text.strip()
    date = re.sub('\((월|화|수|목|금)\)', '', dateStr).replace('.','-')
    info_list.append((title, date, "YES24"))

# db 연결
conn = pymysql.connect(host=MYSQL_HOST,
                       user=MYSQL_USER,
                       password=MYSQL_PW,
                       db=MYSQL_DB,
                       charset=MYSQL_CHARSET)

sql = "INSERT INTO open_info (title, date, site) VALUES (%s, %s, %s)"
with conn:
    with conn.cursor() as cur:
        for title, date, site in info_list:
            cur.execute(sql, (title, date, site))
            conn.commit()