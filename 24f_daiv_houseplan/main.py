import os
from datetime import datetime
from ragdata_repo import (
    subscription_parser,
    policy_parser,
    search_policies,
    financial_product_parser,
)
from llm.response_generator import OpenAIResponseGenerator
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv("API_KEY")
openai_client = OpenAIResponseGenerator(api_key=API_KEY)


class RequestData:
    def __init__(
        self,
        # 변수명 : 타입지정 = "기본값"
        query: str = "전세를 알아보려고 하는데 전세 사기가 걱정돼요",
        current_date: datetime = None,
        user_age: int = 31,
        user_region: str = "서울",
        debug: bool = False,
        debugDate: bool = False,
        special_supply_conditions: list[str] = ["청년"],
        mainbank: str = "국민은행",
    ):
        self.query = query
        self.current_date = current_date or datetime.now()
        self.user_age = user_age
        self.user_region = user_region
        self.debug = debug
        self.debugDate = debugDate
        self.special_supply_conditions = special_supply_conditions
        self.mainbank = mainbank

    def to_json(self):  # 데이터조회할때
        return {
            "query": self.query,
            "current_date": self.current_date.strftime("%Y-%m-%d %H:%M:%S"),
            "user_age": self.user_age,
            "user_region": self.user_region,
            "debug": self.debug,
            "debugDate": self.debugDate,
            "special_supply_conditions": self.special_supply_conditions,
        }


def get_document(requset_data: RequestData):
    # 정책 임베딩(고민에 맞는)
    embedding_policies_doc = search_policies(requset_data.query)

    # 정책 파싱
    parser_policies_doc = policy_parser(
        {
            "current_date": requset_data.current_date.strftime("%Y-%m-%d"),
            "user_age": requset_data.user_age,
            "user_region": requset_data.user_region,
            "debug": requset_data.debug,
            "debugDate": requset_data.debugDate,
        }
    )
    # 금융 파싱(추가예정)
    parser_financial_doc = financial_product_parser(
        {"main_bank": requset_data.mainbank}
    )

    # 청약 파싱
    parser_subscription_doc = subscription_parser(
        {
            "user_region": requset_data.user_region,
            "special_supply_conditions": requset_data.special_supply_conditions,
        }
    )

    # print("정책", parser_policies_doc)
    # print("금융", parser_financial_doc)
    # print("청약", parser_subscription_doc)

    respone = openai_client.generate_response(
        prompt="집 사기가 걱정 돼",
        system_prompt=f"""
아래 문서를 기반으로 답변 잘해봐
===============================================
{str(embedding_policies_doc)}
===============================================
{str(parser_policies_doc)}
===============================================
{str(parser_subscription_doc)}
===============================================
{str(parser_financial_doc)}

        """,
    )

    return respone


if __name__ == "__main__":
    data = RequestData(query="고민을 입력하세요.", user_age=30)

    data = get_document(data)
    print(data)
