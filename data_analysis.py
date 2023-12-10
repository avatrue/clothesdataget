import json

def count_line_delimited_json_entries(file_path):
    """ 줄 분리된 JSON 파일에서 데이터 항목의 수를 세는 함수 """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return sum(1 for line in file if line.strip())  # 비어 있지 않은 줄의 수를 세서 반환
    except Exception as e:
        return f"오류 발생: {e}"

# 사용 예시
file_path = './result_merge/line_merge_231127.json'
print(count_line_delimited_json_entries(file_path))

# 위 코드를 사용할 때는 'your_line_de
