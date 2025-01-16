import os
import pandas as pd
import openai  # LLM 호출용 라이브러리 (OpenAI API 예시)


# 저장된 금융상품 데이터 로드
def load_financial_products_from_file(data_save_path):
    if os.path.exists(data_save_path):
        return pd.read_csv(data_save_path)
    else:
        print("Financial products file not found. Please provide the data first.")
        return pd.DataFrame()


# 금융상품 필터링 함수 (첫 번째 콤마 앞에서 은행명 확인)
def filter_financial_products(data, user_input):
    filtered_data = data.copy()

    if "main_bank" in user_input:
        # sentence 열에서 첫 번째 콤마 앞의 문자열 추출 및 필터링
        filtered_data = filtered_data[
            filtered_data["sentence"]
            .apply(lambda x: x.split(",")[0] if isinstance(x, str) else "")
            .str.contains(user_input["main_bank"], na=False)
        ]

    return filtered_data


# # LLM 호출 함수
# def generate_recommendation_with_llm(filtered_data, user_prompt):
#     # 필터링된 데이터를 요약해 LLM 입력으로 변환
#     product_summary = filtered_data.to_dict(orient="records")
#     llm_prompt = f"{user_prompt}\n\n아래 금융상품 중에서 가장 적합한 상품을 추천해주세요:\n{product_summary}"

#     # OpenAI API 호출 (GPT 예시)
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a financial advisor."},
#                 {"role": "user", "content": llm_prompt},
#             ],
#         )
#         return response["choices"][0]["message"]["content"]
#     except Exception as e:
#         return f"LLM 호출 중 오류가 발생했습니다: {e}"


# 메인 실행 함수
def main(data_save_path, user_input):
    # 저장된 금융상품 데이터 로드
    print("Loading financial product data...")
    combined_data = load_financial_products_from_file(data_save_path)

    # 금융상품 필터링
    filtered_products = filter_financial_products(combined_data, user_input)
    if filtered_products.empty:
        return "조건에 맞는 금융상품 정보를 찾을 수 없습니다."
    return filtered_products

    # # LLM을 사용하여 추천 생성
    # recommendation = generate_recommendation_with_llm(filtered_products, user_prompt)
    # return recommendation


"""
user_input: dict
    - main_bank: str
user_prompt: str
    - 사용자 정의 프롬프트
"""


def financial_product_parser(user_input: dict):
    current_dir = "/Users/hyottz/Desktop/24f-houseplan/24f_daiv_houseplan"
    data_save_path = os.path.join(current_dir, "data/financial_data.csv")
    result = main(data_save_path, user_input)
    return result


if __name__ == "__main__":
    # 사용자 입력 예시
    user_input = {"main_bank": "국민은행"}
    # 메인 실행 및 결과 출력
    print(financial_product_parser(user_input))
