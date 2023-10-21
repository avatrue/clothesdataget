from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time


# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)

# 웹 페이지 접속
url = 'https://fruitsfamily.com/search/바퀘라'
driver.get(url)




def scroll_down(driver):
    old_product_count = 0  # 이전 제품 개수 초기화
    while True:
        # 스크롤 다운
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 스크롤 후 페이지 소스 가져오기
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 현재 페이지의 제품 개수 체크
        current_products = soup.find_all(class_='ProductPreview')  # 수정: 실제 사이트의 제품 리스트 클래스 이름을 사용하세요.
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

    except Exception as e:
        print(f"정보 추출 중 오류 발생: {e}")

    return {
        'title': title,
        'description': description,
        'category': category,
        'brand': brand,
        'seller': seller,
        'date': date
    }

def get_dates_from_products(driver):
    # 페이지 내의 모든 제품 요소를 담을 리스트를 초기화합니다.
    all_dates = []

    # 먼저, 페이지 끝까지 스크롤합니다.
    scroll_down(driver)

    try:
        # 제품 요소들을 찾습니다.
        products = driver.find_elements(By.CSS_SELECTOR, ".ProductPreview")  # 변경된 부분

        # 각 제품에 대해 반복 처리합니다.
        for product in products:
            try:
                # 제품을 클릭합니다.
                product.click()
                time.sleep(2)  # 팝업 창이 나타날 때까지 대기합니다.

                # 날짜 정보 요소를 찾습니다.
                date_element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".Product-date.small"))
                )

                # 날짜 정보를 추출합니다.
                date_text = extract_info(driver, product)


                all_dates.append(date_text)

                # 상세 정보 창을 닫습니다.
                driver.execute_script("window.history.go(-1)")

            except Exception as e:
                print(f"제품 처리 중 오류 발생: {e}")
                continue

    except TimeoutException:
        print("제품 로딩 시간 초과")
    except NoSuchElementException:
        print("제품 요소를 찾을 수 없습니다.")

    return all_dates


# 함수를 호출하여 날짜 데이터를 가져옵니다.
product_dates = get_dates_from_products(driver)
for detail in product_dates:
    print(detail)

# 웹 드라이버 종료
driver.quit()

