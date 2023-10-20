from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import json


def crawl_fruits_family(search_query):


    # 스크롤 횟수 또는 'all' 입력 받기
    scroll_input = input("스크롤 횟수를 입력하세요 (모든 페이지를 스크롤하려면 'all' 입력): ")

    # WebDriver 경로 설정 및 사이트 접속
    driver = webdriver.Chrome()
    url = f"https://fruitsfamily.com/search/{search_query}"
    driver.get(url)

    # WebDriverWait 설정
    wait = WebDriverWait(driver, 10)  # 최대 10초 동안 대기합니다.

    # 스크롤 다운 함수
    def scroll_down():
        # 스크롤 다운 스크립트
        scroll_script = """
        window.scrollTo(0, document.body.scrollHeight);
        """
        driver.execute_script(scroll_script)

    # 'all'이 입력되면, 스크롤이 더 이상 안 되는 지점까지 반복합니다.
    if scroll_input.lower() == 'all':
        old_product_count = 0  # 이전 제품 개수 초기화
        while True:
            # 스크롤 다운
            scroll_down()

            # 스크롤 후 페이지 소스 가져오기
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 현재 페이지의 제품 개수 체크
            current_products = soup.find_all(class_='ProductsListItem')  # 수정: 실제 사이트의 제품 리스트 클래스 이름을 사용하세요.
            current_product_count = len(current_products)

            # 이전 제품 개수와 현재 제품 개수 비교
            if current_product_count == old_product_count:
                break  # 제품 수에 변화가 없으면 스크롤 중지
            else:
                old_product_count = current_product_count  # 제품 수 업데이트 후 스크롤 계속

            time.sleep(2)  # 페이지 로드 대기
    else:
        # 사용자가 지정한 횟수만큼 스크롤 합니다.
        try:
            scroll_count = int(scroll_input)
        except ValueError:
            print("유효하지 않은 숫자입니다. 프로그램을 종료합니다.")
            driver.quit()
            return

        for _ in range(scroll_count):
            scroll_down()
            time.sleep(2)  # 페이지 로드를 위해 잠시 대기합니다.

    # 페이지의 모든 내용을 BeautifulSoup 객체로 변환
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # [데이터 추출 로직 - 예: 제품 정보, 가격 등의 추출]
    # ...




    #데이터 추출과정
    products = []
    product_elements = soup.find_all(class_='ProductsListItem')

    size_pattern = re.compile(r'\b(?:L|M|S|XL|l|m|s|xl|48|50|52|38)\b')  # 사이즈 패턴

    for product_elem in product_elements:
        try:
            brand = product_elem.find(class_='ProductsListItem-brand').get_text(strip=True)
            title = product_elem.find(class_='ProductsListItem-title').get_text(strip=True)
            price = product_elem.find(class_='ProductsListItem-price').get_text(strip=True)
            product_link = product_elem.find('a')['href']

            # 판매 여부를 확인합니다. 'SoldRibbon' 클래스가 있으면 판매된 것으로 간주합니다.
            is_sold = 1 if product_elem.find(class_='SoldRibbon') is None else 0  # 판매 안됨: 1, 판매됨: 0

            size_match = size_pattern.findall(title)
            size = size_match[0] if size_match else 'N/A'

            product_info = {
                'brand': brand,
                'title': title,
                'price': price,
                'size': size,
                'link': product_link,
                'is_sold': is_sold  # 판매 여부
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
# 이 스크립트가 독립적으로 실행되는 경우에만 crawl_fruits_family 함수를 호출합니다.

if __name__ == "__main__":
    crawl_fruits_family()
