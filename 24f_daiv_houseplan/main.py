import os
from datetime import datetime
from ragdata_repo import subscription_parser, policy_parser, search_policies
from llm.response_generator import OpenAIResponseGenerator
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
openai_client = OpenAIResponseGenerator(api_key=API_KEY)


class RequestData:
    def __init__(
        self,
        query: str = "전세를 알아보려고 하는데 전세 사기가 걱정돼요",
        current_date: datetime = None,
        user_age: int = 31,
        user_region: str = "서울",
        debug: bool = False,
        debugDate: bool = False,
        special_supply_conditions: list[str] = ["청년"],
    ):
        self.query = query
        self.current_date = current_date or datetime.now()
        self.user_age = user_age
        self.user_region = user_region
        self.debug = debug
        self.debugDate = debugDate
        self.special_supply_conditions = special_supply_conditions

    def to_json(self):
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
    embedding_policies_doc = search_policies(requset_data.query)
    parser_policies_doc = policy_parser(
        {
            "current_date": requset_data.current_date.strftime("%Y-%m-%d"),
            "user_age": requset_data.user_age,
            "user_region": requset_data.user_region,
            "debug": requset_data.debug,
            "debugDate": requset_data.debugDate,
        }
    )
    parser_subscription_doc = subscription_parser(
        {
            "user_region": requset_data.user_region,
            "special_supply_conditions": requset_data.special_supply_conditions,
        }
    )

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
        """,
    )

    return respone


if __name__ == "__main__":
    data = RequestData(
        # query = "바보"
        user_age=30
    )
    # 데이터 조회용
    # json_data = json.dumps(data.to_json(), ensure_ascii=False, indent=4)
    # print(json_data)

    data = get_document(data)
    print(data)


# llm
