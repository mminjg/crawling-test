from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import pymysql
import os

# dotenv
load_dotenv(verbose=True)
WEBDRIVER_PATH = os.getenv('WEBDRIVER_PATH')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PW = os.getenv('MYSQL_PW')
MYSQL_DB = os.getenv('MYSQL_DB')
MYSQL_CHARSET = os.getenv('MYSQL_CHARSET')

# url
yes24_url = 'http://ticket.yes24.com/New/Notice/NoticeMain.aspx'
interpark_purl = 'http://ticket.interpark.com/webzine/paper/'
interpark_url = interpark_purl + 'TPNoticeList.asp'

# webdriver
options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

info_list = []

# yes24 크롤링
driver.get(yes24_url)
soup = BeautifulSoup(driver.page_source, 'html.parser')

for tr in soup.find_all('tr')[1:]:
    type = tr.select('td')[0].text.strip()
    if type != "티켓오픈":
        continue
    title = tr.select('td')[1].text.strip()
    link = yes24_url + tr.select('td')[1].find('a')['href']
    dateStr = tr.select('td')[2].text.strip()
    date = re.sub('\((월|화|수|목|금|토|일)\)', '', dateStr).replace('.','-')
    info_list.append((title, date, link, "YES24"))

# 인터파크 크롤링
driver.get(interpark_url)
driver.switch_to.frame('iFrmNotice')
soup = BeautifulSoup(driver.page_source, 'html.parser')
types = ['뮤지컬', '콘서트', '연극', '클래식/무용']

for tr in soup.select('tbody > tr'):
    if tr.has_attr('class'):
        continue
    type = tr.select_one('.type').text
    if type not in types:
        continue
    title = tr.select_one('.subject > a').text
    link = interpark_purl + tr.select_one('.subject > a')['href']
    dateStr = tr.select_one('.date').text
    date = '20' + re.sub('\((월|화|수|목|금|토|일)\)', '', dateStr).replace('.', '-').replace(u'\xa0', ' ')
    info_list.append((title, date, link, "INTERPARK"))

#db 연결
conn = pymysql.connect(host=MYSQL_HOST,
                       user=MYSQL_USER,
                       password=MYSQL_PW,
                       db=MYSQL_DB,
                       charset=MYSQL_CHARSET)

sql = "INSERT INTO open_info (title, date, link, site) VALUES (%s, %s, %s, %s)"
with conn:
    with conn.cursor() as cur:
        for title, date, link, site in info_list:
            cur.execute(sql, (title, date, link, site))
            conn.commit()