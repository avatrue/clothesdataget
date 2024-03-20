import json
from playwright.sync_api import sync_playwright
import re
import datetime

def load_brands(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        brands = json.load(file)
    return brands

def check_brand_in_title(title, primary_brand_name, alternative_brand_name):
    title = re.sub(r"\s+", "", title).lower()
    primary_brand_name = re.sub(r"\s+", "", primary_brand_name).lower()
    if alternative_brand_name:
        alternative_brand_name = re.sub(r"\s+", "", alternative_brand_name).lower()

    return primary_brand_name in title or alternative_brand_name in title if alternative_brand_name else False

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

def process_category_id(cat_id):
    parts = re.findall('...', cat_id)
    parts += ['0'] * (3 - len(parts))
    return tuple(parts[:3])

def bunjang_crawler(brand_name, alternative_brand_name, category_id):
    data_list = []
    previous_product_ids = None
    page_num = 1

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        while True:
            url = f"https://m.bunjang.co.kr/search/products?category_id={category_id}&order=date&page={page_num}&q={brand_name}"
            print(url)  # 추가된 코드
            page.goto(url)
            product_list = page.query_selector_all('img[alt="상품 이미지"]')
            print(len(product_list))
            if not product_list:
                print(f"No more products found. Ending the search.")
                break

            current_product_ids = []

            for item in product_list:
                aTag = item.query_selector('xpath=ancestor::a')
                if aTag:
                    product_id = aTag.get_attribute('data-pid')
                    infor = aTag.query_selector('div').inner_text().split(';;;')

                    if not check_brand_in_title(infor[0], brand_name, alternative_brand_name):
                        continue

                    if product_id:
                        current_product_ids.append(product_id)
                    if product_id is None:
                        continue

                    image_link = item.get_attribute('src')

                    status_tag = aTag.query_selector('img[alt*="예약중"], img[alt*="판매 완료"]')
                    status = 0 if status_tag else 1

                    raw_time = infor[2] if len(infor) > 2 else "미 확인"
                    converted_time = convert_time(raw_time) if raw_time != "미 확인" else raw_time

                    raw_price = infor[1] if len(infor) > 1 else "0"
                    cleaned_price = ''.join(filter(str.isdigit, raw_price.replace(',', '')))

                    if cleaned_price:
                        converted_price = int(cleaned_price)
                    else:
                        print(f"Could not convert price for product_id {product_id}: {raw_price}")
                        converted_price = 0

                    big_category, mid_category, small_category = process_category_id(category_id)

                    product_data = {
                        "product_id": int(product_id),
                        "brand": [brand_name],
                        "title": infor[0],
                        "price_history": [converted_price],
                        "link": f"https://m.bunjang.co.kr/products/{product_id}",
                        "status": status,
                        "image_link": image_link,
                        "time": converted_time,
                        "category": {
                            "big": int(big_category) if big_category.isdigit() else big_category,
                            "mid": int(mid_category) if mid_category.isdigit() else mid_category,
                            "small": int(small_category) if small_category.isdigit() else small_category
                        }
                    }
                    data_list.append(product_data)
                else:
                    print(f"Could not find ancestor <a> tag for product.")
                    continue

            if previous_product_ids is not None and previous_product_ids == current_product_ids:
                print(f"Reached the last page with new products at page {page_num}.")
                break

            previous_product_ids = current_product_ids
            page_num += 1

        browser.close()

    return data_list
def main(brand_file_path, category_id):
    brands = load_brands(brand_file_path)
    print(brands)
    for brand_name, alternative_brand_name in brands.items():
        data_list = bunjang_crawler(brand_name, alternative_brand_name, category_id)

        json_data = json.dumps(data_list, ensure_ascii=False, indent=4)
        filename = f"{brand_name}_data.json"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(json_data)
        print(f"Data for {brand_name} saved to {filename}")

if __name__ == '__main__':
    brand_file_path = 'brands_test.json'
    category_id = '320300600'
    main(brand_file_path, category_id)