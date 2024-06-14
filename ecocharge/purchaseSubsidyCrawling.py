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
# option.add_experimental_option('detach', True)
option.add_argument('--headless')

# 크롬 드라이버를 별도로 설치하지 않고 버전에 맞는 드라이버를 사용하게 해 주는 코드
service = webdriver.ChromeService(ChromeDriverManager().install())

# 크롬 드라이버를 활용하여 웹 브라우저를 제어할 수 있는 객체를 리턴
driver = webdriver.Chrome(options=option, service=service)

driver.get('https://ev.or.kr/nportal/buySupprt/initSubsidyTargetVehicleAction.do')

soup = BeautifulSoup(driver.page_source, 'html.parser')