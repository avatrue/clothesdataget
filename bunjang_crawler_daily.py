from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import json
import datetime
import re



def load_brands():
    with open('brands.json', 'r', encoding='utf-8') as file:
        brands = json.load(file)
    return brands

def load_category_numbers():
    with open('category_numbers.json', 'r', encoding='utf-8') as file:
        category_numbers = json.load(file)
    return category_numbers

def check_brand_in_title(title, primary_brand_name, alternative_brand_name):
    # 띄어쓰기를 제거하고 소문자로 변환하여 비교
    title = re.sub(r"\s+", "", title).lower()
    primary_brand_name = re.sub(r"\s+", "", primary_brand_name).lower()

    # 대체 브랜드명이 제공되었는지 확인하고, 띄어쓰기를 제거
    if alternative_brand_name:
        alternative_brand_name = re.sub(r"\s+", "", alternative_brand_name).lower()

    return primary_brand_name in title or alternative_brand_name in title if alternative_brand_name else False


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
    # brand_name = input("검색어 입력 : ")
    # alternative_brand_name = input("검색할 브랜드의 다른 이름 입력 (없으면 엔터) : ")
    brands = load_brands()  # brands.json 파일 로드
    crawl_end_page = input("몇 페이지까지 조회할까요? (모든 페이지를 조회하려면 'all'을 입력) : ")
    category_id = input("카테고리 ID 입력 (3, 6, 또는 9자리): ")

    # Selenium 구동
    browser = initialize_browser()
    browser.get('https://m.bunjang.co.kr/')
    all_category_list=load_category_numbers()
    # 수집한 데이터를 저장할 리스트
    #테스트코드:크롤링 총 갯수 반환
    total_crawl_count=0
    for brand_name, alternative_brand_name in brands.items():
        brand_crawl_count=0
        data_list=[]
        for category_id in all_category_list:
            crawl_data,category_crawl_count = bunjang_crawler(brand_name, alternative_brand_name, browser, category_id, crawl_end_page)
            print(f"{category_id}크롤링 갯수:{category_crawl_count}")
            total_crawl_count+=category_crawl_count
            brand_crawl_count+=category_crawl_count
            data_list.extend(crawl_data)  # 리스트에 크롤링 데이터 추가

        # JSON 데이터 저장
        json_data = json.dumps(data_list, ensure_ascii=False, indent=4)
        # 파일 이름을 브랜드명_data.json 형식으로 지정합니다.
        filename = f"crawl_data_for_brand/{brand_name}_data.json"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(json_data)
        print(f"Data for {brand_name} saved to {filename}")
        print(f"{brand_name}의 총 크롤링 갯수:{brand_crawl_count}")
    # 종료
    browser.quit()
    #테스트코드: 토탈 크롤링 갯수 반환
    print(total_crawl_count)

def bunjang_crawler(brand_name, alternative_brand_name, browser, category_id, crawl_end_page):
    # 데이터 수집 로직
    # 초기 카테고리 설정
    initial_big_category, initial_mid_category, initial_small_category = process_category_id(category_id)
    # 수집한 데이터를 저장할 리스트
    data_list = []
    # 이전 페이지의 제품 ID를 저장할 변수
    previous_product_ids = None
    # 페이지 순환을 위한 설정
    page = 1
    is_last_page = False
    category_crawl_count=0
    #테스트코드
    print(f"Starting crawl for category: {category_id}")
    while not is_last_page:
        url = f"https://m.bunjang.co.kr/search/products?category_id={category_id}&order=date&page={page}&q={brand_name}"
        browser.get(url)
        #테스트코드
        print(f"Generated URL: {url}")
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "app")))
        html = browser.page_source
        html_parser = BeautifulSoup(html, features="html.parser")
        product_list = html_parser.find_all(attrs={'alt': '상품 이미지'})

        if not product_list or (crawl_end_page.isdigit() and page > int(crawl_end_page)):
            print(f"No products found on page {page}. Ending the search.")
            break

        # 현재 페이지의 제품 ID를 저장할 리스트
        current_product_ids = []

        # 제품정보 추출
        for item in product_list:

            #테스트코드: 총 크롤링 갯수 반환
            category_crawl_count+=1
            aTag = item.parent.parent
            product_id = aTag.get('data-pid')
            for i, c in enumerate(aTag.children, 0):
                if i == 1:
                    infor = c.get_text(separator=';;;').split(sep=';;;')
            # 매 제품을 확인할 때마다 초기 카테고리로 리셋
            big_category, mid_category, small_category = initial_big_category, initial_mid_category, initial_small_category

            # 제목에 브랜드명 또는 대체 브랜드명이 포함되어 있는지 확인
            if not check_brand_in_title(infor[0], brand_name, alternative_brand_name):
                continue  # 두 이름 중 하나도 제목에 없으면 이 제품은 건너뛰기

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
            # if status == 1:
            #     # 카테고리 넘버 뽑기
            #     category_number = extract_product_details(product_id,browser)
            #     big_category, mid_category, small_category = process_category_id(category_number)

            # 시간 값 변환
            raw_time = infor[2] if len(infor) > 2 else "미 확인"
            converted_time = convert_time(raw_time) if raw_time != "미 확인" else raw_time

            # 가격 값 변환
            raw_price = infor[1] if len(infor) > 1 else "0"
            # 숫자가 아닌 문자를 제거하고 숫자만 남기기
            cleaned_price = ''.join(filter(str.isdigit, raw_price.replace(',', '')))

            if cleaned_price:
                # 추출된 숫자 문자열을 정수로 변환
                converted_price = int(cleaned_price)
            else:
                # 가격 정보를 추출할 수 없는 경우 로그를 남기고 0으로 설정
                print(f"Could not convert price for product_id {product_id}: {raw_price}")
                converted_price = 0


            title=infor[0]


            try:
                product_data = {
                    "product_id": int(product_id),  # MongoDB의 _id 필드로 사용할 수 있게 숫자로 변환
                    "brand": [brand_name],  # 브랜드 이름을 배열로 저장
                    "title": infor[0],
                    "price_history": [converted_price],  # 가격 변경 이력을 배열로 저장
                    "link": f"https://m.bunjang.co.kr/products/{product_id}",
                    "status": status,
                    "image_link": image_link,
                    "category": {
                        "big": int(big_category) if big_category.isdigit() else big_category,
                        "mid": int(mid_category) if mid_category.isdigit() else mid_category,
                        "small": int(small_category) if small_category.isdigit() else small_category
                    }
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
        if crawl_end_page.isdigit() and page > int(crawl_end_page):
            break
    return data_list, category_crawl_count


# 프로그램 실행
if __name__ == '__main__':
    main()






