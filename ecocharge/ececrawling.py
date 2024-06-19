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
option.add_experimental_option('detach', True)
# option.add_argument('--headless')

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

img_list = []
for n in range(1, 9):
    if n != 2:
        if n != 6:
            t.sleep(0.3)
            driver.find_element(By.XPATH, '//*[@id="main_pack"]/div[6]/div[2]/div[1]/div/div[3]/div[1]/div[' + str(n) + ']/div[1]/a').click()
            t.sleep(0.3)  
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            img = soup.select_one("#main_pack > div.sc_new.cs_common_module.case_normal.color_5._cs_car_single > div.cm_content_wrap._content > div:nth-child(1) > div > div.rel_aroundview._image_viewer_wrap > div.view_box.type_normal > div.img_area > a > img").attrs['src']
            img_list.append(img)
            t.sleep(0.3)
            driver.back()
    
print(img_list)
t.sleep(1)
for n in range(0, 6):
    query = 'INSERT INTO tbl_crawling (img_url, info_url) VALUES(%s, %s)'
    values = (img_list[n], 'https://search.naver.com/search.naver' +  div_list[0].select('div.info_area > strong.title > a._text')[n].attrs['href'])
    mycursor.execute(query, values)

mydb.commit()
mycursor.close()
mydb.close()

del soup
driver.close()