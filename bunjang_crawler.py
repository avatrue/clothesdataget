from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import json
import datetime
import re

# 시간 변환 함수
def convert_time(time_str):
    current_time = datetime.datetime.now()
    numbers = re.findall(r'\d+', time_str)
    number = int(numbers[0]) if numbers else 0

    if '분 전' in time_str or '시간 전' in time_str:
        return current_time.strftime('%Y-%m-%d')
    elif '일 전' in time_str:
        return (current_time - datetime.timedelta(days=number)).strftime('%Y-%m-%d')
    elif '주 전' in time_str:
        return (current_time - datetime.timedelta(weeks=number)).strftime('%Y-%m-%d')
    elif '달 전' in time_str:

        return (current_time - datetime.timedelta(days=number * 30)).strftime('%Y-%m-%d')
    elif '년 전' in time_str:
        return current_time.replace(year=current_time.year - number).strftime('%Y-%m-%d')
    return current_time.strftime('%Y-%m-%d')

# 검색 입력
itemname = input("검색어 입력 : ")
pages = input("몇 페이지까지 조회할까요? (모든 페이지를 조회하려면 'all'을 입력) : ")

# Selenium 구동
browser = webdriver.Chrome()
browser.implicitly_wait(10)
browser.get('https://m.bunjang.co.kr/')

# 수집한 데이터를 저장할 리스트
data_list = []

# 페이지 순환을 위한 설정
page = 1
is_last_page = False

while not is_last_page:
    url = f"https://m.bunjang.co.kr/search/products?order=score&page={page}&q={itemname}"
    browser.get(url)

    WebDriverWait(browser, 10).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "app")))

    html = browser.page_source
    html_parser = BeautifulSoup(html, features="html.parser")
    product_list = html_parser.find_all(attrs={'alt': '상품 이미지'})

    if not product_list or (pages.isdigit() and page >= int(pages)):
        break  # 제품 목록이 없거나, 사용자가 지정한 페이지에 도달한 경우 반복 종료

    # 제품정보 추출
    for item in product_list:
        aTag = item.parent.parent
        product_id = aTag.get('data-pid')

        for i, c in enumerate(aTag.children, 0):
            if i == 1:
                infor = c.get_text(separator=';;;').split(sep=';;;')

        title = infor[0]
        if itemname.lower() not in title.lower():
            continue  # 검색어가 제목에 없으면 이 제품은 건너뛰기
        # 판매 상태 확인
        status_tag = aTag.find('img', alt=lambda x: x and ('예약중' in x or '판매 완료' in x))
        status = 0 if status_tag else 1

        # 시간 값 변환
        raw_time = infor[2] if len(infor) >2 else "미 확인"
        converted_time = convert_time(raw_time) if raw_time != "미 확인" else raw_time
        # 가격 값 변환
        raw_price = infor[1] if len(infor) > 1 else "0"
        converted_price = int(raw_price.replace(',', ''))

        try:
            product_data = {
                "product_id": product_id,
                "title": infor[0],
                "price": converted_price,
                "time": converted_time,
                "link": f"https://m.bunjang.co.kr/products/{product_id}",
                "status": status
            }
            data_list.append(product_data)
        except Exception as e:
            print("Error:", e)

    page += 1

    # 마지막 페이지라면 종료
    if pages.isdigit() and page > int(pages):
        break

browser.quit()

json_data = json.dumps(data_list, ensure_ascii=False, indent=4)

print(json_data)

with open('products.json', 'w', encoding='utf-8') as file:
    file.write(json_data)
