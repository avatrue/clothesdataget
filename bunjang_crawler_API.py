import requests
from urllib.parse import quote
import json

def load_brand_names(filename):
    with open(filename, "r", encoding="utf-8") as file:
        brand_names = json.load(file)
    return brand_names

def get_total_count(brands, category_id):
    base_url = "https://api.bunjang.co.kr/api/1/find_v2.json"
    params = {
        "q": brands[0],
        "order": "score",
        "page": 0,
        "f_category_id": category_id,
        "n": 100,
        "stat_category_required": 1
    }

    response = requests.get(base_url, params=params)
    print(f"전체 제품 수 조회 API: {response.url}")  # API URL 출력
    data = response.json()

    total_count = data["categories"][0]["count"]
    return total_count

def get_category_counts(brands, category_id):
    base_url = "https://api.bunjang.co.kr/api/1/find_v2.json"
    params = {
        "q": brands[0],
        "order": "score",
        "page": 0,
        "f_category_id": category_id,
        "n": 100,
        "stat_category_required": 1
    }

    response = requests.get(base_url, params=params)
    print(f"카테고리별 제품 수 조회 API: {response.url}")  # API URL 출력
    data = response.json()

    category_counts = {}
    for category in data["categories"][0]["categories"]:
        category_counts[category["id"]] = category["count"]

    return category_counts

def get_product_data(brands, category_id, page):
    base_url = "https://api.bunjang.co.kr/api/1/find_v2.json"
    params = {
        "q": brands[0],
        "order": "score",
        "page": page,
        "f_category_id": category_id,
        "n": 100,
        "stat_category_required": 1
    }

    response = requests.get(base_url, params=params)
    print(f"제품 데이터 조회 API (페이지 {page + 1}): {response.url}")  # API URL 출력
    data = response.json()

    product_list = []
    for product in data["list"]:
        price = product["price"]
        product_info = {
            "pid": product["pid"],
            "brands": [brand for brand in brands if brand in product["name"]],
            "name": product["name"],
            "price_updates": [{product["update_time"]: price}],
            "product_image": product["product_image"],
            "status": product["status"],
            "category_id": product["category_id"]
        }
        product_list.append(product_info)

    return data["no_result"], data["categories"][0]["count"], data["list"], product_list

def update_products(all_products, new_products):
    for new_product in new_products:
        for product in all_products:
            if product["pid"] == new_product["pid"]:
                for brand in new_product["brands"]:
                    if brand not in product["brands"]:
                        product["brands"].append(brand)
                for update in new_product["price_updates"]:
                    update_time = list(update.keys())[0]
                    if update_time not in [list(p.keys())[0] for p in product["price_updates"]]:
                        product["price_updates"].insert(0, update)
                if new_product["status"] != product["status"]:
                    product["status"] = new_product["status"]
                break
        else:
            all_products.append(new_product)

    return all_products

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def collect_data(brand_names, output_filename):
    try:
        with open(output_filename, "r", encoding="utf-8") as file:
            all_products = json.load(file)
    except FileNotFoundError:
        all_products = []

    for brands in brand_names.items():
        category_id = 320  # 카테고리 ID를 320으로 초기화
        total_count = get_total_count(brands, category_id)
        print(f"브랜드 {brands[0]} - 전체 제품 수: {total_count}")

        filtered_products = []
        actual_count = 0

        if total_count >= 30000:
            category_counts = get_category_counts(brands, category_id)
            print(f"브랜드 {brands[0]} - 카테고리별 제품 수:")
            for category_id, count in category_counts.items():
                print(f"카테고리 ID: {category_id}, 제품 수: {count}")

            for category_id in category_counts.keys():
                page = 0
                while True:
                    print(f"{page + 1} 페이지 데이터 수집 중...")
                    no_result, total_count, products, filtered = get_product_data(brands, category_id, page)
                    filtered_products.extend(filtered)
                    actual_count += len(products)

                    if no_result:
                        break

                    page += 1
                    if page == 499:
                        break
        else:
            page = 0
            while True:
                print(f"{page + 1} 페이지 데이터 수집 중...")
                no_result, total_count, products, filtered = get_product_data(brands, category_id, page)
                filtered_products.extend(filtered)
                actual_count += len(products)

                if no_result:
                    break

                page += 1
                if page == 499:
                    break

        print(f"브랜드 {brands[0]} - 필터링 후 남은 제품 수: {len(filtered_products)}")
        print(f"브랜드 {brands[0]} - 실제로 조회한 제품 수: {actual_count}")
        print()

        all_products = update_products(all_products, filtered_products)
        save_to_json(all_products, output_filename)  # 브랜드별로 JSON 파일 업데이트
        print(f"브랜드 {brands[0]} 데이터 수집 완료 및 JSON 파일 업데이트")
        print()

    print("모든 브랜드 데이터 수집 완료!")


def filter_data(input_filename, output_filename):
    with open(input_filename, "r", encoding="utf-8") as file:
        products = json.load(file)

    filtered_products = []
    for product in products:
        price_updates = product["price_updates"]
        latest_price = list(price_updates[0].values())[0]
        if not any(brand in product["name"] for brand in product["brands"]) or not latest_price.isdigit() or latest_price[-1] != "0" or int(latest_price) < 10000:
            continue
        filtered_products.append(product)

    save_to_json(filtered_products, output_filename)
    print("데이터 필터링 완료!")


def merge_data(filtered_filename, existing_filename, output_filename):
    with open(filtered_filename, "r", encoding="utf-8") as file:
        filtered_products = json.load(file)

    try:
        with open(existing_filename, "r", encoding="utf-8") as file:
            existing_products = json.load(file)
    except FileNotFoundError:
        existing_products = []

    merged_products = update_products(existing_products, filtered_products)
    save_to_json(merged_products, output_filename)
    print("데이터 병합 완료!")

if __name__ == "__main__":
    brand_names_file = "brands_test.json"
    collected_file = "collected_products.json"
    filtered_file = "filtered_products.json"
    merged_file = "merged_products.json"

    brand_names = load_brand_names(brand_names_file)
    collect_data(brand_names, collected_file)
    filter_data(collected_file, filtered_file)
    merge_data(filtered_file, merged_file, merged_file)