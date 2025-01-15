import os
import pandas as pd


# 저장된 메타데이터 로드
def load_metadata_from_file(metadata_save_path):
    if os.path.exists(metadata_save_path):
        return pd.read_csv(metadata_save_path)
    else:
        print("Metadata file not found. Please extract metadata first.")
        return pd.DataFrame()


# 데이터 필터링 함수
def filter_data(data, user_input):
    filtered_data = data.copy()
    if "region_name" in user_input:
        filtered_data = filtered_data[
            filtered_data["region_name"].str.contains(
                user_input["user_region"], na=False
            )
        ]
    if "special_supply_conditions" in user_input:
        filtered_data = filtered_data[
            filtered_data["special_supply_conditions"].str.contains(
                "|".join(user_input["special_supply_conditions"]), na=False
            )
        ]
    return filtered_data


# 메인 실행 함수
def main(metadata_save_path, user_input):
    # 저장된 메타데이터 로드
    print("Loading metadata...")
    combined_data = load_metadata_from_file(metadata_save_path)

    # 추천 결과 필터링
    recommended_supplies = filter_data(combined_data, user_input)

    if not recommended_supplies.empty:
        return recommended_supplies
    else:
        return "조건에 맞는 청약 정보를 찾을 수 없습니다."


"""
user_input: dict
    - region_name: str
    - special_supply_conditions: list[str]
"""


def subscription_parser(user_input: dict):
    current_dir = "/Users/hyottz/Desktop/24f-houseplan/24f_daiv_houseplan"
    metadata_save_path = os.path.join(current_dir, "combined_data.csv")
    result = main(metadata_save_path, user_input)
    result_json = result.to_json(orient="records", force_ascii=False)
    return result_json


if __name__ == "__main__":
    # 사용자 입력 예시
    user_input = {"user_region": "인천", "special_supply_conditions": ["청년"]}
    # 메인 실행 및 결과 출력
    print(subscription_parser(user_input))
