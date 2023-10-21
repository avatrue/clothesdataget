import json
import pandas as pd
import matplotlib.pyplot as plt

def load_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def analyze_and_visualize(json_file):
    # 데이터 로드
    data = load_data(json_file)

    # 데이터를 pandas DataFrame으로 변환
    df = pd.DataFrame(data)

    # 가격 데이터 변환 (','와 '원' 제거 후 숫자형으로 변환)
    df['price'] = df['price'].str.replace('원', '').str.replace(',', '').str.strip().astype(float)

    # 팔린 제품과 판매 중인 제품으로 나누기
    sold_products = df[df['is_sold'] == 0]
    available_products = df[df['is_sold'] == 1]

    # 가격 분포 그래프를 위한 데이터 준비
    fig, axs = plt.subplots(2, 1, figsize=(12, 8))

    # 여기에서 bins의 숫자를 늘려 세분화할 수 있습니다.
    num_bins = 1000  # 더 세분화된 히스토그램을 위한 bin 수

    # 팔린 제품의 가격 분포 시각화
    n, bins, patches = axs[0].hist(sold_products['price'], bins=num_bins, color='red', alpha=0.7)
    axs[0].set_title('sold')
    axs[0].set_xlabel('Price (in KRW)')
    axs[0].set_ylabel('Number of Products')

    # y축의 스케일을 조정하여 더 세밀한 뷰를 제공합니다.
    axs[0].set_yscale('log')  # 로그 스케일 사용
    axs[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

    # 판매 중인 제품의 가격 분포 시각화
    n, bins, patches = axs[1].hist(available_products['price'], bins=num_bins, color='blue', alpha=0.7)
    axs[1].set_title('available')
    axs[1].set_xlabel('Price (in KRW)')
    axs[1].set_ylabel('Number of Products')

    # 이 축에 대해서도 로그 스케일을 적용합니다.
    axs[1].set_yscale('log')
    axs[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

    # 그래프 레이아웃 조정
    plt.tight_layout()
    plt.show()

# main.py에서 이 스크립트를 호출할 경우에 대비해 분석 기능을 자체 실행 가능하도록 구성
if __name__ == "__main__":
    data_file = 'fruits_family_products.json'  # JSON 파일 경로
    analyze_and_visualize(data_file)
