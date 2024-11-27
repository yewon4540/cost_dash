import os
import re
import time
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

today_date = datetime.now().strftime("%Y-%m-%d")

url = 'https://console.opsnow.com/account/signin'

download_dir = os.path.join(os.getcwd(), "download")
os.makedirs(download_dir, exist_ok=True)

options = Options()
options.add_argument("--window-size=1920,1080")  # 브라우저 창 크기 설정
options.add_argument("--headless") # webdriver 화면 띄우지 않기 : Docker container 에서 돌릴 시 필수입니당
options.add_argument('--disable-gpu') # gpu 옵션 해제 : gpu 없어서 해제함
options.add_argument('--disable-dev-shm-usage') # 메모리 캐시 매핑 해제 : 불필요한 공간 차지 방지
options.add_argument('--no-sandbox') # 샌드박스 옵션 해제 : Sandbox option은 브라우저 자체를 하나의 프로세스로 냅두지 않 고, 시스템 상에서(container일 경우 container 시스템으로 속해짐) 돌아가도록 설정함 (보안 수준 낮아짐, 브라우저 crash 방지 O)
options.add_argument("--log-level=3")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

print('드라이버 열기 시도중...')
driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
print('드라이버 열기 완료')

driver.get(url)
time.sleep(5)

mail_path = '/html/body/div[2]/div[1]/form/div/div/div[1]/div/input'
pass_path = '/html/body/div[2]/div[1]/form/div/div/div[2]/div[2]/input'

mail_element = driver.find_element(By.XPATH, mail_path)
mail_element.send_keys('genia@chunjae.co.kr')
time.sleep(0.5)

pass_element = driver.find_element(By.XPATH, pass_path)
pass_element.send_keys('Genia@11')
time.sleep(0.5)

print('로그인 시도중')
pass_element.send_keys('\n')
time.sleep(3)
print('로그인 완료')

report_url = 'https://metering.opsnow.com/cost/cost-analytics'
driver.get(report_url)
time.sleep(2)
print('리포트 페이지로 이동')

print('필터 설정중')
filter_menu_path = '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/div[4]/div/button'
filter_menu_elemenet = driver.find_element(By.XPATH, filter_menu_path)
filter_menu_elemenet.click()
time.sleep(1)

filter_lms_path = '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/div[4]/div/ul/li/ul/li/a'
filter_lms_element = driver.find_element(By.XPATH, filter_lms_path)
filter_lms_element.click()
time.sleep(5)
print('필터 설정 완료')

print('view 수정 중')
view_toggle_xpath = '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div[1]/div[1]/div[1]/button'
view_toggle_element = driver.find_element(By.XPATH, view_toggle_xpath)
view_toggle_element.click()
time.sleep(1)

resource_toggle_xpath = '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div[1]/div[1]/div[1]/ul/li/ul/li[2]/a'
resource_toggle_element = driver.find_element(By.XPATH, resource_toggle_xpath)
resource_toggle_element.click()
time.sleep(5)
print('view 수정 완료')

print('다운로드 시도 중')
down_toggle_xpath = '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div[2]/div[3]/button'
down_toggle_element = driver.find_element(By.XPATH, down_toggle_xpath)
down_toggle_element.click()
time.sleep(1)

down_button_xpath = '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div[2]/div[3]/ul/li/ul/li[1]/a'
down_button_element = driver.find_element(By.XPATH, down_button_xpath)
down_button_element.click()
time.sleep(5)
print('다운로드 완료')

os.rename('./download/DailyCostTrend_Product.csv', f'./download/{today_date}.csv')
print(f'이름 변환 완료 : {today_date}')

new_file = f'./download/{today_date}.csv'
origin_file = './data.csv'

# origin_data 읽기
origin_data = pd.read_csv(origin_file, encoding='utf-8')
origin_data.columns = origin_data.columns.str.strip()  # 공백 제거

# new_data 읽기
new_data = pd.read_csv(new_file, encoding='utf-8')
new_data.columns = new_data.columns.str.strip()  # 공백 제거

# 'Total (￦)' 행 제거
new_data = new_data[new_data['Cloud Service'] != 'Total (￦)']

# 덮어쓸 날짜 범위 설정 (2024-11-20 ~ 2024-11-26)
date_range_to_update = pd.date_range(start="2024-11-20", end="2024-11-26").strftime('%m/%d/%Y').tolist()

# 숫자형 데이터로 변환 (쉼표 제거 후)
for col in origin_data.columns[2:]:
    origin_data[col] = origin_data[col].replace({',': ''}, regex=True).apply(pd.to_numeric, errors='coerce')

for col in new_data.columns[2:]:
    new_data[col] = new_data[col].replace({',': ''}, regex=True).apply(pd.to_numeric, errors='coerce')

# '클라우드 서비스' + '제품' 기준 열 생성 (origin_data)
origin_data['key'] = origin_data['클라우드 서비스'].fillna('') + '|' + origin_data['제품'].fillna('')

# 'Cloud Service' + 'Product' 기준 열 생성 (new_data)
new_data['key'] = new_data['Cloud Service'].fillna('') + '|' + new_data['Product'].fillna('')

# Product 열을 기준으로 merge
updated_data = origin_data.copy()
for key in new_data['key'].unique():
    # 해당 key 필터링
    new_product_data = new_data[new_data['key'] == key]
    origin_product_index = updated_data[updated_data['key'] == key].index

    # key가 origin_data에 없으면 새로운 row 추가
    if origin_product_index.empty:
        print(f"Adding new Product '{key}' to origin_data")
        
        # 빈 row 생성
        cloud_service, product = key.split('|')
        new_row = pd.DataFrame({
            '클라우드 서비스': [cloud_service],  # new_data의 Cloud Service 값 사용
            '제품': [product],
            **{col: 0 for col in origin_data.columns[2:]},  # 나머지 값 0 초기화
            'key': [key]  # key 추가
        })
        updated_data = pd.concat([updated_data, new_row], ignore_index=True)
        
        # 추가된 row의 인덱스 다시 가져오기
        origin_product_index = updated_data[updated_data['key'] == key].index

    # 날짜 범위 값 업데이트
    for date_col in date_range_to_update:
        if date_col not in new_product_data.columns:
            print(f"Warning: Date '{date_col}' not found in new_data for Product '{key}'")
            continue

        updated_data.loc[origin_product_index, date_col] = new_product_data[date_col].values[0]

    # 총계 (￦) 업데이트
    if "총계 (￦)" in new_product_data.columns and not new_product_data["총계 (￦)"].empty:
        updated_data.loc[origin_product_index, "총계 (￦)"] = new_product_data["총계 (￦)"].values[0]
    else:
        print(f"Warning: '총계 (￦)' not found or empty for Product '{key}'")

# 'key' 열 삭제 (병합 후 불필요)
updated_data = updated_data.drop(columns=['key'])

# '총계 (￦)' 행을 마지막으로 이동
total_row = updated_data[updated_data['클라우드 서비스'] == '총계 (￦)']
updated_data = updated_data[updated_data['클라우드 서비스'] != '총계 (￦)']
updated_data = pd.concat([updated_data, total_row], ignore_index=True)

# 갱신된 origin_data.csv 저장
updated_data.to_csv(origin_file, index=False, encoding='utf-8-sig')

print("원본 파일이 성공적으로 갱신되었습니다!")
