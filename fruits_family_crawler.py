# fruits_family_crawler.py
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import json

def crawl_fruits_family(search_query):
    # WebDriver 경로 설정 및 사이트 접속
    driver = webdriver.Chrome()
    url = f"https://fruitsfamily.com/search/{search_query}"
    driver.get(url)

    # 스크롤 다운 스크립트
    scroll_script = """
    window.scrollTo(0, document.body.scrollHeight);
    """

    # 여러 번 스크롤 다운을 수행하여 모든 콘텐츠 로딩
    scroll_count = 3

    for i in range(scroll_count):
        driver.execute_script(scroll_script)  # 스크롤 다운 스크립트 실행
        time.sleep(2)  # 로딩 대기

    # 페이지의 모든 내용을 BeautifulSoup 객체로 변환
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 데이터 추출
    products = []
    product_elements = soup.find_all(class_='ProductsListItem')

    size_pattern = re.compile(r'\b(?:L|M|S|XL|l|m|s|xl|48|50|52|38)\b')  # 사이즈 패턴

    for product_elem in product_elements:
        try:
            brand = product_elem.find(class_='ProductsListItem-brand').get_text(strip=True)
            title = product_elem.find(class_='ProductsListItem-title').get_text(strip=True)
            price = product_elem.find(class_='ProductsListItem-price').get_text(strip=True)
            product_link = product_elem.find('a')['href']

            size_match = size_pattern.findall(title)
            size = size_match[0] if size_match else 'N/A'

            product_info = {
                'brand': brand,
                'title': title,
                'price': price,
                'size': size,
                'link': product_link
            }
            products.append(product_info)

        except AttributeError as e:
            print("누락된 정보가 있습니다.", e)

    # 드라이버 종료
    driver.close()

    return products

def save_to_json(products, file_name='products.json'):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

