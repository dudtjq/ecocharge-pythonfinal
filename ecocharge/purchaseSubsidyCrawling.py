from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time as t
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select

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
option.add_experimental_option('detach', False)
# option.add_argument('--headless')

# 크롬 드라이버를 별도로 설치하지 않고 버전에 맞는 드라이버를 사용하게 해 주는 코드
service = webdriver.ChromeService(ChromeDriverManager().install())

# 크롬 드라이버를 활용하여 웹 브라우저를 제어할 수 있는 객체를 리턴
driver = webdriver.Chrome(options=option, service=service)

driver.get('https://ev.or.kr/nportal/buySupprt/initSubsidyTargetVehicleAction.do')

query = 'TRUNCATE TABLE tbl_crawling_subsidycar'
mycursor.execute(query)

query = 'INSERT INTO tbl_crawling_subsidycar (car_name, img_url, riding_capacity, top_speed, full_charge_range, battery, subsidy, call_number, company, country) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

count = 1
while count <= 2:
    driver.implicitly_wait(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    tr_list = soup.select('div#contents > div.subPage > div.pageBox > div.subWrap > form#searchForm > div.searchWrap > table.table02 > tbody > tr')

    options = tr_list[3].select('select#schCompany > option')
    index = len(options)
    for idx in range(1, index+1):
        t.sleep(0.5)
        new_soup = BeautifulSoup(driver.page_source, 'html.parser')
        page = 0

        a_list = new_soup.select('div#pageingPosition > a')

        page = len(a_list)
        next_button = page - 1
        p = 2
        page -= 3
        while p <= page:
            t.sleep(0.5)
            n_soup = BeautifulSoup(driver.page_source, 'html.parser')
            sub_wrap = n_soup.select_one('div#contents > div.subPage > div.pageBox > div.subWrap')
            h4_list = n_soup.select('div#contents > div.subPage > div.pageBox > div.subWrap > div.itemCont > div.infoBox > a > h4')
            dl_list = n_soup.select('div#contents > div.subPage > div.pageBox > div.subWrap > div.itemCont > div.infoBox > a > dl')
            
            for n in range(0, len(h4_list)):
                car_name = h4_list[n].select_one('p').text
                # print(p_text)
                dl = dl_list[n]
                img = dl.select_one('dt > img').get_attribute_list('src')[0]
                dd_list = dl.select('dd')
                riding_capacity = dd_list[0].text.split(':', 1)[1]
                top_speed = dd_list[1].text.split(':', 1)[1]
                full_charge_range = dd_list[2].text.split(':', 1)[1]
                battery = dd_list[3].text.split(':', 1)[1]
                subsidy = dd_list[4].text.split(':', 1)[1]
                call_number = dd_list[5].text.split(':', 1)[1]
                company = dd_list[6].text.split(':', 1)[1]
                country = dd_list[7].text.split(':', 1)[1]

                values = (car_name, img, riding_capacity, top_speed, full_charge_range, battery, subsidy, call_number, company, country)
                mycursor.execute(query, values)

            driver.find_element(By.XPATH, f'//*[@id="pageingPosition"]/a[{next_button}]').click()
            
            p += 1

        schCompanys = Select(driver.find_element(By.XPATH, '//*[@id="schCompany"]'))
        if idx < index:
            schCompanys.select_by_index(idx)
            driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/div/div/form/div/table/tbody/tr[4]/td/button').click()
    count += 1
    driver.find_element(By.XPATH, '//*[@id="searchForm"]/div/table/tbody/tr[2]/td/label[2]').click()

mydb.commit()
mycursor.close()
mydb.close()

del soup
driver.close()