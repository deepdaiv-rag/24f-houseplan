import os
from datetime import datetime
from ragdata_repo import (
    subscription_parser,
    policy_parser,
    financial_product_parser,
)
from llm.response_generator import OpenAIResponseGenerator
from dotenv import load_dotenv
import json
import pandas as pd

load_dotenv()
API_KEY = os.getenv("API_KEY")
openai_client = OpenAIResponseGenerator(api_key=API_KEY)

class RequestData:
    def __init__(
        self,
        user_name:str,
        user_age: int,
        user_region: str,
        special_supply_conditions: list[str],
        mainbank: str,
        concerns: str,  # Added concerns parameter
        current_date: datetime = None,
        debug: bool = False,
        debugDate: bool = False,
    ):
        self.user_name=user_name,
        self.user_age = user_age
        self.user_region = user_region
        self.special_supply_conditions = special_supply_conditions
        self.mainbank = mainbank
        self.concerns = concerns  # Store concerns
        self.current_date = current_date or datetime.now()
        self.debug = debug
        self.debugDate = debugDate

    def to_json(self):
        return {
            "name": self.user_name,
            "user_age": self.user_age,
            "user_region": self.user_region,
            "special_supply_conditions": self.special_supply_conditions,
            "mainbank": self.mainbank,
            "concerns": self.concerns,  # Include concerns in JSON
            "current_date": self.current_date.strftime("%Y-%m-%d %H:%M:%S"),
            "debug": self.debug,
            "debugDate": self.debugDate,
        }


def get_document(request_data: RequestData):
    # 정책 임베딩(고민에 맞는)
    #embedding_policies_doc = search_policies(request_data.concerns)

    # 정책 파싱
    parser_policies_doc = policy_parser(
        {
            "current_date": request_data.current_date.strftime("%Y-%m-%d"),
            "user_age": request_data.user_age,
            "user_region": request_data.user_region,
            "debug": request_data.debug,
            "debugDate": request_data.debugDate,
        }
    )
    # 금융 파싱(추가예정)
    parser_financial_doc = financial_product_parser(
        {"main_bank": request_data.mainbank}
    )

    # 청약 파싱
    parser_subscription_doc = subscription_parser(
        {
            "user_region": request_data.user_region,
            "special_supply_conditions": request_data.special_supply_conditions,
        }
    )

    # print("정책", parser_policies_doc)
    # print("금융", parser_financial_doc)
    # print("청약", parser_subscription_doc)
#   

    response = openai_client.generate_response(
        prompt=f'''
        당신은 2030 청년 대상의 주거 문제를 해결하는 고객 맞춤형 금융 전문가입니다.
        다음 내용을 포함한 종합 금융 플랜을 작성해주세요:
        사용자의 나이, 지역, 고민을 분석하고,  그에 맞는 정책,금융 상품,청약을 정보를 제공합니다.

        각 정책과 금융 상품, 청약 전략은 사용자 상황에 적합한 이유를 설명하며,요청된 항목들을 체계적으로 작성해주세요.

        사용자 정보:
        - 이름: {request_data.user_name}
        - 나이: {request_data.user_age}세
        - 지역: {request_data.user_region}
        - 특별 공급 조건: {request_data.special_supply_conditions}
        - 주거래 은행: {request_data.mainbank}
        - 고민 사항: "{request_data.concerns}"


        요구 사항:
        1. **사용자 상황 분석**: 사용자자가 입력한 정보와 주요 고민 사항 등을 명시. (연령대, 나이, 특별조건, 주거래은행, 고민사항)
        2. **추천 정책 및 지원 사업**:
            - 정책 이름 그대로 제목에 사용**
            - 2-1. 본 정책을 추천한 이유를 사용자 상황 및 고민 사항을 근거로 설명
            - 2-2. 각 정책별 신청 자격, 혜택, 신청 방법
        3. **추천 금융 상품 포트폴리오**:
            - **상품명 그대로 제목에 사용**
            - 3-1. 본 금융 상품을 추천한 이유를 사용자 상황에 적합하게 설명
            - 3-2. 각 상품별 추천 이유, 예상 수익률, 가입 방법
            - 3-3. 대출이 필요한 경우 대출 금액, 예상 이자
            - 3-4. 예/적금은 금리가 높은 순으로 추천
        4. **추천 청약 상품 제시**:
            - **청약 상품명 그대로 제목에 사용**
            - 4-1. 본 청약을 추천한 이유를 사용자 상황에 적합하게 설명
            - 4-2. 추천 청약 상품은 사용자의 지역, 특별공급조건 등을 반영
        5. **월간 저축 계획**:
            - 목표액, 필수 저축액, 권장 저축액, 세부 계획 포함 (월세/대출 상환 포함)
        6. **단계별 실행 계획**:
            - **(1 Step) 상품 추천 후에 (2 Step) 이를 반영하여 계획 및 마일스톤을 제시**
            - 즉시, 1-3개월, 3-6개월, 6개월-1년, 1년 이상으로 구분하여 구체적으로 실천 가능한 계획 작성
            - 정책 신청, 금융 상품 가입, 저축 실행, 청약 준비 등의 액션 항목 포함

        주의 사항:
        - 각 정책, 금융 상품, 청약 상품의 상품명은 추천된 정책 그대로 사용
        - 사용자의 주요 고민사항을 해결할 실질적인 방안을 중심으로 작성
        - 추천 이유는 반드시 구체적으로 설명하며 추천 상품 그대로 제목에 사용
        - 각 정책, 상품, 청약의 **신청 마감일** 및 **주요 주의사항**을 반드시 확인해주세요.

 **출력 형식은 반드시 JSON이어야 하며, 아래 JSON 스키마를 따르세요.**
 ** 출력형식은 아래와 같이 나오면 됩니다.**
    """
    {{
        "user_analysis": {{
            "name":"<사용자의 이름>",
            "age": "<사용자의 나이>",
            "region": "<사용자의 지역>",
            "special_conditions": "<특별 공급 조건>",
            "main_bank": "<주거래 은행>",
            "concerns": "<사용자의 주요 고민>"
        }},
        "recommended_policies": [
            {{
                "policy_name": "<정책 이름>",
                "recommendation_reason": "<정책 추천 이유>",
                "eligibility": {{
                    "age_range": "<적용 가능한 나이 범위>",
                    "income_criteria": "<소득 기준>",
                    "other_conditions": "<기타 조건>"
                }},
                "benefits": {{
                    "description": "<정책 혜택 설명>"
                }},
                "application_method": "<신청 방법>"
            }}
        ],
        "recommended_financial_products": [
            {{
                "product_name": "<금융 상품 이름>",
                "recommendation_reason": "<추천 이유>",
                "expected_interest_rate": "<예상 금리>",
                "application_method": "<가입 방법>",
                "loan_example": {{
                    "loan_amount": "<대출 금액>",
                    "monthly_payment": "<월 상환액>"
                }}
            }}
        ],
        "recommended_housing_products": [
            {{
                "product_name": "<청약 상품 이름>",
                "recommendation_reason": "<추천 이유>",
                "application_method": "<신청 방법>",
                "application_deadline": "<신청 마감일>"
            }}
        ],
        "monthly_savings_plan": {{
            "goal_amount": "<목표 금액>",
            "mandatory_savings": "<필수 저축액>",
            "recommended_savings": "<권장 저축액>",
            "detailed_plan": {{
                "monthly_rent": "<월세>",
                "loan_repayment": "<대출 상환>",
                "savings": "<저축>",
                "other_living_expenses": "<기타 생활비>"
            }}
        }},
        "step_by_step_plan": [
            {{
                "step": "<단계 이름>",
                "actions": [
                    "<실행 계획1>",
                    "<실행 계획2>"
                ],
                "timeline": {{
                    "immediate": "<즉시 실행 항목>",
                    "1_3_months": "<1-3개월 실행 항목>",
                    "3_6_months": "<3-6개월 실행 항목>",
                    "6_12_months": "<6-12개월 실행 항목>",
                    "12_months_plus": "<12개월 이상 실행 항목>"
                }}
            }}
        ]
    }}
    """
            

        ''',
        system_prompt=f"""
아래 문서를 기반으로 답변 해주세요.
===============================================
policies_doc : 
{str(parser_policies_doc)}
===============================================
financial_doc : 
{str(parser_financial_doc)}
===============================================
subscription_doc : 
{str(parser_subscription_doc)}
===============================================

        """,
    )
    
    return response


if __name__ == "__main__":
    request_data = RequestData(
        user_name="안효주",
        concerns = "전세 사기도 많다던데, 급하게 옮기다 피해를 볼까 봐 무서워요.",
            user_age =  27,
            user_region = "인천",
            special_supply_conditions = "청년",
            mainbank="우리은행" )   
 
    data = get_document(request_data)
    print(data)
