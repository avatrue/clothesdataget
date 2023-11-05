from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import json

# 검색 입력
itemname = input("검색어 입력 : ")
# Selenium 구동
browser = webdriver.Chrome()
browser.implicitly_wait(10)
browser.get('https://m.bunjang.co.kr/')



# 수집한 데이터를 저장할 리스트
data_list = []


page = 21


url = f"https://m.bunjang.co.kr/search/products?order=score&page={page}&q={itemname}"
browser.get(url)


WebDriverWait(browser, 10).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "app")))


html = browser.page_source
html_parser = BeautifulSoup(html, features="html.parser")
product_list = html_parser.find_all(attrs={'alt': '상품 이미지'})

# 제품정보 추출
for item in product_list:
    aTag = item.parent.parent
    product_id = aTag.get('data-pid')

    for i, c in enumerate(aTag.children, 0):
        if i == 1:
            infor = c.get_text(separator=';;;').split(sep=';;;')

    # 판매 상태 확인
    status_tag = aTag.find('img', alt=lambda x: x and '예약중' in x or '판매 완료' in x)
    status = 0 if status_tag else 1

    try:
        product_data = {
            "product_id": product_id,
            "title": infor[0],
            "price": infor[1],
            "time": infor[2] if infor[2] else "미 확인",
            "link": f"https://m.bunjang.co.kr/products/{product_id}",
            "status": status  # 상태 업데이트
        }
        data_list.append(product_data)
    except Exception as e:
        print("Error:", e)



browser.quit()

json_data = json.dumps(data_list, ensure_ascii=False, indent=4)

print(json_data)

with open('products.json', 'w', encoding='utf-8') as file:
    file.write(json_data)
