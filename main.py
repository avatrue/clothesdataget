# main.py
import fruits_family_crawler as crawler


def main():
    # 사용자에게 검색어를 입력 받습니다.
    search_query = input("검색어를 입력하세요: ")

    # 크롤러 함수를 호출하여 데이터를 수집합니다.
    product_data = crawler.crawl_fruits_family(search_query)


    crawler.save_to_json(product_data, 'fruits_family_products.json')

    print(f"크롤링이 완료되었으며, '{search_query}'에 대한 데이터가 fruits_family_products.json에 저장되었습니다.")


if __name__ == "__main__":
    main()
