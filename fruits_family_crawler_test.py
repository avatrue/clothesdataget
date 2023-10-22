from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import json

def setup_driver():
    # 웹드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return webdriver.Chrome(options=options)



def scroll_down(driver):
    old_product_count = 0  # 이전 제품 개수 초기화
    while True:
        # 스크롤 다운
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 스크롤 후 페이지 소스 가져오기
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 현재 페이지의 제품 개수 체크
        current_products = soup.find_all(class_='ProductPreview')
        current_product_count = len(current_products)

        # 이전 제품 개수와 현재 제품 개수 비교
        if current_product_count == old_product_count:
            break  # 제품 수에 변화가 없으면 스크롤 중지
        else:
            old_product_count = current_product_count  # 제품 수 업데이트 후 스크롤 계속

        time.sleep(2)  # 페이지 로드 대기
def extract_info(driver, product):
    # 팝업이나 새 페이지에서 원하는 정보를 추출하는 함수

    title = description = category = brand = seller = date = None
    is_sold_out = 0  # 기본값은 '판매 중'입니다.
    price = None

    try:
        # 제품의 제목을 가져옵니다.
        title_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".Product-title.font-nhaasgrotesk"))
        )
        title = title_element.text.strip()

        # 제품의 설명(본문)을 가져옵니다.
        description_element = driver.find_element(By.CSS_SELECTOR, ".Product-description")
        description = description_element.text.strip()

        # 제품 분류를 가져옵니다.
        category_elements = driver.find_elements(By.CSS_SELECTOR, "a.Product-tag.btn.btn-outline-dark.btn-sm")
        category = [elem.text.strip() for elem in category_elements if '/discover/product/' in elem.get_attribute('href')]

        # 브랜드 분류를 가져옵니다.
        brand_elements = driver.find_elements(By.CSS_SELECTOR, "a.Product-tag.btn.btn-outline-dark.btn-sm")
        brand = [elem.text.strip() for elem in brand_elements if '/brand/' in elem.get_attribute('href')]

        # 판매자 닉네임을 가져옵니다.
        seller_element = driver.find_element(By.CSS_SELECTOR, ".SellerPreview-nickname.font-nhaasgrotesk")
        seller = seller_element.text.strip()

        # 날짜 정보를 가져옵니다
        date_element = driver.find_element(By.CSS_SELECTOR, ".Product-date.small")
        date = date_element.text.strip()

        # 판매 완료 여부 확인
        try:
            # '품절' 버튼이 있는지 확인합니다.
            driver.find_element(By.CSS_SELECTOR, 'button.Product-buy[disabled]')
            is_sold_out = 1  # '품절' 버튼이 있으면, 상품이 판매 완료된 것입니다.
        except NoSuchElementException:
            # '품절' 버튼이 없으면, 상품이 판매 중인 것으로 간주합니다.
            is_sold_out = 0

        # 가격 정보를 추출합니다.
        price_element = driver.find_element(By.CSS_SELECTOR, 'div.Product-price')
        price_text = price_element.text.strip()
        # ","와 "원"을 제거하고 숫자만을 추출합니다.
        price = int(''.join(filter(str.isdigit, price_text)))

    except Exception as e:
        print(f"정보 추출 중 오류 발생: {e}")

    return {
        'title': title,
        'description': description,
        'category': category,
        'brand': brand,
        'seller': seller,
        'date': date,
        'is_sold_out': is_sold_out,  # 판매 완료 여부
        'price': price  # 상품 가격
    }

"""
    get_dates_from_products함수
    받는 인자: driver
    
    페이지 끝까지 스크롤
    각 제품 클릭해 창 열고
    데이터크롤링
    나오기 반복
"""
def get_info_from_products(driver, url):
    driver.get(url)
    # 페이지 내의 모든 제품 요소를 담을 리스트를 초기화합니다.
    all_item_info = []
    # 먼저, 페이지 끝까지 스크롤합니다.
    scroll_down(driver)

    try:
        # 제품 요소들을 찾습니다.
        products = driver.find_elements(By.CSS_SELECTOR, ".ProductPreview")

        # 각 제품에 대해 반복 처리합니다.
        for product in products:
            try:
                # 요소가 화면 중앙에 오도록 스크롤합니다. 첫 4개의 아이템이 스크롤되지 않는 문제 발생으로 추가
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product)

                time.sleep(1)

                # 제품 클릭
                product.click()

                time.sleep(1) #현재 제품클릭 앞뒤에 sleep웨이팅을 걸지 않으면 작동하지 않는 것을 확인 webdriverwait사용해보려했으나 실패 현재 최적화로는 1초가 최소


                # 날짜 정보를 추출합니다.
                info_text = extract_info(driver, product)


                all_item_info.append(info_text)

                # 상세 정보 창을 닫습니다.
                driver.execute_script("window.history.go(-1)")

            except Exception as e:
                print(f"제품 처리 중 오류 발생: {e}")
                continue

    except TimeoutException:
        print("제품 로딩 시간 초과")
    except NoSuchElementException:
        print("제품 요소를 찾을 수 없습니다.")

    return all_item_info

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    driver = setup_driver()
    target_url = 'https://fruitsfamily.com/search/바퀘라'  # 예시 URL
    product_infos = get_info_from_products(driver, target_url)
    for detail in product_infos:
        print(detail)
    save_to_json(product_infos, 'product_info_vaquera.json')
    driver.quit()
