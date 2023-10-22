# main.py
import fruits_family_crawler as crawler
import data_analysis as analysis  # 데이터 분석 스크립트 import
import fruits_family_crawler_test as scraper

def main():
    # # 사용자에게 검색어를 입력 받습니다.
    # search_query = input("검색어를 입력하세요: ")
    #
    # # 크롤러 함수를 호출하여 데이터를 수집합니다.
    # product_data = crawler.crawl_fruits_family(search_query)
    #
    # # JSON 파일로 데이터를 저장합니다.
    json_file_name = 'fruits_family_products.json'
    # crawler.save_to_json(product_data, json_file_name)
    #
    # print(f"크롤링이 완료되었으며, '{search_query}'에 대한 데이터가 {json_file_name}에 저장되었습니다.")

    # 분석 및 시각화 함수를 호출합니다. (analysis.py 내의 함수)



    driver = scraper.setup_driver()
    product_data = scraper.get_info_from_products(driver, 'https://fruitsfamily.com/search/바퀘라')
    scraper.save_to_json(product_data, 'output.json')
    driver.quit()

    # print("데이터 분석 및 시각화를 시작합니다...")
    # analysis.analyze_and_visualize(json_file_name)  # 분석 스크립트에 JSON 파일 이름을 전달합니다.


if __name__ == "__main__":
    main()
