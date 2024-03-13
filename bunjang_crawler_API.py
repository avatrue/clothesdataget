import requests
import json

def get_total_pages(brand, category_id):
    base_url = "https://api.bunjang.co.kr/api/1/find_v2.json"
    params = {
        "q": brand[0],
        "order": "date",
        "page": 0,
        "f_category_id": category_id,
        "stat_category_required": 1
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    total_count = data["categories"][0]["count"]
    total_pages = (total_count - 1) // 100 + 1

    return total_pages

def get_product_data(brand, category_id, page):
    base_url = "https://api.bunjang.co.kr/api/1/find_v2.json"
    params = {
        "q": brand[0],
        "order": "date",
        "page": page,
        "f_category_id": category_id,
        "stat_category_required": 1
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    product_list = []
    for product in data["list"]:
        if brand[0] not in product["name"] and brand[1] not in product["name"]:
            continue

        price = product["price"]
        if not price.isdigit() or price[-1] != "0":
            continue

        product_info = {
            "pid": product["pid"],
            "Brand": brand[0],
            "name": product["name"],
            "price": price,
            "product_image": product["product_image"],
            "status": product["status"],
            "category_id": product["category_id"],
            "update_time": product["update_time"]
        }
        product_list.append(product_info)

    return product_list

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def main():
    brand_name = ["마틴로즈", "martinerose"]
    category_id = 320

    total_pages = get_total_pages(brand_name, category_id)
    print(f"총 페이지 수: {total_pages}")

    all_products = []
    for page in range(total_pages):
        print(f"{page + 1} 페이지 데이터 수집 중...")
        products = get_product_data(brand_name, category_id, page)
        all_products.extend(products)

    save_to_json(all_products, "bunjang_products.json")
    print("데이터 수집 완료!")

if __name__ == "__main__":
    main()