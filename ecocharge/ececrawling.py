from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time as t
from bs4 import BeautifulSoup

# pip install mysql-connector-python
import mysql.connector

# DB 접속을 위한 정보 세팅
mydb = mysql.connector.connect(
    host='ecocharge-db.clmka4a6awo7.ap-northeast-2.rds.amazonaws.com',
    user='root',
    passwd='ecocharge',
    database='ecocharge_db'
)

# sql 실행을 위한 커서 생성
mycursor = mydb.cursor()

# 셀레늄 사용 중 브라우저 꺼짐 현상 방지 옵션
option = webdriver.ChromeOptions()
# option.add_experimental_option('detach', False)
option.add_argument('--headless')

# 크롬 드라이버를 별도로 설치하지 않고 버전에 맞는 드라이버를 사용하게 해 주는 코드
service = webdriver.ChromeService(ChromeDriverManager().install())

# 크롬 드라이버를 활용하여 웹 브라우저를 제어할 수 있는 객체를 리턴
driver = webdriver.Chrome(options=option, service=service)

driver.get('https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=%EC%A0%84%EA%B8%B0%EC%B0%A8')


driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[6]/div[2]/div[1]/div/div[2]/div/div/ul/li[2]/a/span').click()
t.sleep(0.2)
soup = BeautifulSoup(driver.page_source, 'html.parser')

div_list = soup.select('div._car_panel_wrapper > div.list_info')

query = 'TRUNCATE TABLE tbl_crawling'
mycursor.execute(query)

img_list = div_list[0].select('div.thumb_area > a > img')
name_list = div_list[0].select('div.info_area > strong.title > a._text')

index = len(img_list)
for n in range(0, 6):
    query = 'INSERT INTO tbl_crawling (img_url, info_url) VALUES(%s, %s)'
    values = (img_list[n].attrs['src'], 'https://search.naver.com/search.naver' +  name_list[n].attrs['href'])
    mycursor.execute(query, values)

mydb.commit()
mycursor.close()
mydb.close()

del soup
driver.close()