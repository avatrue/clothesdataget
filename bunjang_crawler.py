from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import json
import datetime
import re

# 웹 드라이버 초기화
def initialize_browser():
    browser = webdriver.Chrome()
    browser.implicitly_wait(10)
    return browser

# 페이지 HTML 가져오기
def get_page_html(browser, url):
    browser.get(url)
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "app")))
    return browser.page_source
# 제품정보 추출 함수 정의
# 제품 상세페이지로부터 카테고리 번호 추출 함수
def extract_product_details(product_id,browser):
    try:
        # 상세페이지로 이동
        details_url = f"https://m.bunjang.co.kr/products/{product_id}"
        browser.get(details_url)

        # 상세페이지의 내용을 기다린 후, 파싱
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/categories/']"))
        )
        details_html = browser.page_source
        details_parser = BeautifulSoup(details_html, 'html.parser')

        # 카테고리 링크 추출
        category_link_tag = details_parser.find('a', href=re.compile(r'/categories/\d+'))
        if category_link_tag and 'href' in category_link_tag.attrs:
            category_href = category_link_tag['href']
            category_number = re.search(r'/categories/(\d+)', category_href).group(1)
            print(f"Extracted category number: {category_number}")  # 디버깅을 위한 출력
            browser.back()
            return category_number
        else:
            print("Category number not found.")  # 디버깅을 위한 출력
            browser.back()
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        browser.back()
        return None

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
# 카테고리 ID 처리
def process_category_id(cat_id):
    # 카테고리 ID를 3개의 부분으로 분리
    parts = re.findall('...', cat_id)
    # 분리된 부분이 없는 경우 0으로 채움
    parts += ['0'] * (3 - len(parts))
    return tuple(parts[:3])  # 최대 3개의 카테고리 ID 반환
# 메인 함수
def main():
    # 사용자 입력 처리
    item_name = input("검색어 입력 : ")
    pages = input("몇 페이지까지 조회할까요? (모든 페이지를 조회하려면 'all'을 입력) : ")
    category_id = input("카테고리 ID 입력 (3, 6, 또는 9자리): ")

    # Selenium 구동
    browser = initialize_browser()
    browser.get('https://m.bunjang.co.kr/')

    # 데이터 수집 로직
    # 큰 카테고리, 중간 카테고리, 작은 카테고리 추출
    big_category, mid_category, small_category = process_category_id(category_id)

    # 수집한 데이터를 저장할 리스트
    data_list = []

    # 이전 페이지의 제품 ID를 저장할 변수
    previous_product_ids = None

    # 페이지 순환을 위한 설정
    page = 1
    is_last_page = False

    while not is_last_page:
        url = f"https://m.bunjang.co.kr/search/products?category_id={category_id}&order=date&page={page}&q={item_name}"
        browser.get(url)
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "app")))
        html = browser.page_source
        html_parser = BeautifulSoup(html, features="html.parser")
        product_list = html_parser.find_all(attrs={'alt': '상품 이미지'})

        if not product_list or (pages.isdigit() and page > int(pages)):
            print(f"No products found on page {page}. Ending the search.")
            break

        # 현재 페이지의 제품 ID를 저장할 리스트
        current_product_ids = []

        # 제품정보 추출
        for item in product_list:
            aTag = item.parent.parent
            product_id = aTag.get('data-pid')
            for i, c in enumerate(aTag.children, 0):
                if i == 1:
                    infor = c.get_text(separator=';;;').split(sep=';;;')

            title = infor[0]
            if item_name.lower() not in title.lower():
                continue  # 검색어가 제목에 없으면 이 제품은 건너뛰기
            # 제품넘버 추출
            if product_id:
                current_product_ids.append(product_id)
            if product_id == None:
                continue

            # 이미지 링크 추출
            image_tag = aTag.find('img', {'alt': '상품 이미지'})
            image_link = image_tag.get('src') if image_tag else None


            # 판매 상태 확인
            status_tag = aTag.find('img', alt=lambda x: x and ('예약중' in x or '판매 완료' in x))
            status = 0 if status_tag else 1
            if status == 1:
                # 카테고리 넘버 뽑기
                category_number = extract_product_details(product_id,browser)
                big_category, mid_category, small_category = process_category_id(category_number)

            # 시간 값 변환
            raw_time = infor[2] if len(infor) > 2 else "미 확인"
            converted_time = convert_time(raw_time) if raw_time != "미 확인" else raw_time

            # 가격 값 변환
            raw_price = infor[1] if len(infor) > 1 else "0"
            if "연락요망" in raw_price:
                continue  # "연락요망"이 포함되어 있으면 이 제품은 건너뛰기

            converted_price = int(raw_price.replace(',', ''))

            try:
                product_data = {
                    "brand": item_name,
                    "product_id": product_id,
                    "title": infor[0],
                    "price": converted_price,
                    "time": converted_time,
                    "link": f"https://m.bunjang.co.kr/products/{product_id}",
                    "status": status,
                    "image_link": image_link,
                    "category": {
                        "big_category": big_category,
                        "mid_category": mid_category,
                        "small_category": small_category}
                }
                data_list.append(product_data)
            except Exception as e:
                print("Error:", e)
        # 현재 페이지와 이전 페이지의 제품 ID 목록 비교
        if previous_product_ids is not None and previous_product_ids == current_product_ids:
            print(f"Reached the last page with new products at page {page}.")
            break

        # 이전 페이지의 제품 ID 목록 업데이트
        previous_product_ids = current_product_ids
        page += 1

        # 마지막 페이지라면 종료
        if pages.isdigit() and page > int(pages):
            break



    # 종료
    browser.quit()

    # JSON 데이터 저장
    json_data = json.dumps(data_list, ensure_ascii=False, indent=4)
    print(json_data)
    with open('products.json', 'w', encoding='utf-8') as file:
        file.write(json_data)

# 프로그램 실행
if __name__ == '__main__':
    main()







