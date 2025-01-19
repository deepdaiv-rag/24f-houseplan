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
    #embedding_policies_doc = search_policies(requset_data.query)

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
        prompt="""
        고민 : 전세를 알아보려고 하는데 전세 사기가 걱정돼요,
        현재기간 : 2024년 1월 16일
        나이 : 31,
        거주지역 : "서울",
        특별조건 : 청년,
        주거래은행 : 국민은행

        ===============================================
        {str(parser_policies_doc)}
        ===============================================
        {str(parser_subscription_doc)}
        ===============================================
        {str(parser_financial_doc)}""",
        system_prompt=f"""

"프롬프트 예시:

"당신은 청년에게 내 집 마련 금융 정책을 추천해주는 금융 전문가입니다. 다음 내용을 포함한 종합 금융 플랜을 작성해주세요. 사용자의 상황을 분석하고, 추천 정책, 금융 상품, 청약 전략, 저축 계획 등을 구체적으로 제시해주세요.
각 정책과 금융 상품, 청약 전략은 사용자 상황에 적합한 이유를 설명하며, 요청된 항목들을 체계적으로 작성해주세요.
최신성을 반영한 현재 시행중인 정책/금융/청약 정보를 추천합니다. 

*요구 사항:
1. 사용자 상황 분석: 사용자의 재정 상태, 주요 고민 사항, 목표 등을 평가
2. 추천 정책 및 지원 사업:
	2-1.각 정책별 신청 자격, 혜택, 신청 방법 포함.
	2-2. 정책 이름 그대로 제목에 사용
3. 추천 금융 상품 포트폴리오:
	3-1. 각 상품별 추천 이유, 예상 수익률, 가입 방법 설명.
	3-2. 대출이 필요한 경우 대출 금액, 예상 이자 포함
	3-3. 예/적금은 금리가 높은순으로 추천
	3-4. 대출은 이자율 낮고, 한도 높은 순으로 추천
	3-5. 금융 상품의 경우 권장 월 저축 금액, 대출 금액, 상환 기간도 함께 알려줘. 
4. 추천 청약 상품 제시: 
	4-1. 각 청약별 추천 이유를 명확하게 설명.
	4-2. 추천한 청약 상품은 사용자의 지역, 특별공급조건 등을 반영하여 추천.
5. 월간 저축 계획:
 5-1. 추천된 금융상푸필수 저축액, 권장 저축액, 세부 계획 포함
 5-2. 계획에 월세 및 대출 상환이 있을 경우 이를 포함하여 추천해줘
 
6. 단계별 실행 계획:
즉시, 1-3개월, 3-6개월, 6개월-1년, 1년 이상으로 구분하여 구체적으로 실천 가능한 계획 작성.
시기 별 마일스톤

6-2. 단계별 마일스톤
   - 자산 형성 목표: 시기별 목표 자산 규모
   - 저축 달성률: 시기별 목표 저축액 대비 실제 저축액
   - 대출상환 현황: 시기별 대출잔액 감소 목표

6-3. 시각화 요소
   - 시기별 자산 증가 그래프
   - 월별 저축 계획 대비 실적 차트
   - 대출상환 계획 진행률 게이지
   - 청약 자격 획득 진행도
   - 마일스톤 달성 체크리스트

7. 주의사항 및 체크리스트: 사용자가 실수하지 않도록 반드시 주의할 점을 포함
  - 각 정책, 금융 상품, 청약 상품의 상품명은 추천된 정책 그대로 사용
	- 사용자의 주요 고민사항을 해결할 실질적인 방안을 중심으로 작성
	- 추천 이유는 반드시 구체적으로 설명하고, 작성된 플랜은 실용적이고 실행 가능한 형태로 작성

플랜을 체계적으로 작성하여 사용자가 즉시 활용할 수 있도록 도와주세요."



""")

    return respone


if __name__ == "__main__":
    data = RequestData(query="고민을 입력하세요.", user_age=30)

    data = get_document(data)
    print(data)
