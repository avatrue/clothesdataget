import json
import pandas as pd
import matplotlib.pyplot as plt

def load_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def analyze_and_visualize(data):
    # 데이터를 pandas DataFrame으로 변환
    df = pd.DataFrame(data)

    # 가격데이터 변환 (, 원 제거)
    df['price'] = df['price'].str.replace('원', '').str.replace(',', '').str.strip().astype(float)

    # 팔린 제품과 판매 중인 제품으로 나누기
    sold_products = df[df['is_sold'] == 0]
    available_products = df[df['is_sold'] == 1]

    # 가격 분포 그래프를 위한 데이터 준비
    fig, axs = plt.subplots(2, 1, figsize=(12, 8))

    # 팔린 제품의 가격 분포 시각화
    axs[0].hist(sold_products['price'], bins=20, color='red', alpha=0.7)
    axs[0].set_title('판매된 가격 분포')
    axs[0].set_xlabel('Price')
    axs[0].set_ylabel('Number of Products')

    # 판매 중인 제품의 가격 분포 시각화
    axs[1].hist(available_products['price'], bins=20, color='blue', alpha=0.7)
    axs[1].set_title('판매중인 가격분포')
    axs[1].set_xlabel('Price')
    axs[1].set_ylabel('Number of Products')

    # 그래프 레이아웃 조정
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 데이터 로드
    data_file = 'fruits_family_products.json'  # JSON 파일 경로
    products_data = load_data(data_file)

    # 데이터 분석 및 시각화
    analyze_and_visualize(products_data)
