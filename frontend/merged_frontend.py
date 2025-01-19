import streamlit as st
import pandas as pd
from datetime import datetime
import os
from ragdata_repo import (
    subscription_parser,
    policy_parser,
    search_policies,
    financial_product_parser,
)
from llm.response_generator import OpenAIResponseGenerator
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
openai_client = OpenAIResponseGenerator(api_key=API_KEY)

class RequestData:
    def __init__(
        self,
        query: str,
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

def get_document(request_data: RequestData):
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
    
    # 금융 파싱
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

    response = openai_client.generate_response(
        prompt=f"""
        고민 : {request_data.query},
        현재기간 : {request_data.current_date.strftime("%Y년 %m월 %d일")}
        나이 : {request_data.user_age},
        거주지역 : {request_data.user_region},
        특별조건 : {', '.join(request_data.special_supply_conditions)},
        주거래은행 : {request_data.mainbank}

        ===============================================
        {str(parser_policies_doc)}
        ===============================================
        {str(parser_subscription_doc)}
        ===============================================
        {str(parser_financial_doc)}""",
        system_prompt="""[이전 system_prompt 내용 그대로 유지]""")

    return response

# Streamlit UI 코드
def local_css():
    st.markdown("""
    <style>
        .section-box {
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .response-section {
            background-color: #E8F4FA;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .info-card {
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("맞춤형 주거/금융 상담 서비스")
    local_css()
    
    # 사용자 정보 입력 폼
    with st.form("user_info"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("나이", min_value=19, max_value=65, value=29)
            location = st.selectbox(
                "지역",
                ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "세종", 
                 "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
            )
        with col2:
            special_conditions = st.multiselect(
                "특별조건",
                ["다자녀", "신혼부부", "생애최초첫청약", "노부모부양", "신생아", "청년"]
            )
            bank = st.selectbox(
                "주거래은행",
                ["국민은행", "신한은행", "우리은행", "하나은행", "농협은행", "기타"]
            )
        
        concerns = st.text_area("고민사항")
        submitted = st.form_submit_button("상담 받기")
    
    if submitted:
        with st.spinner('상담 내용을 분석중입니다...'):
            # RequestData 객체 생성
            request_data = RequestData(
                query=concerns,
                user_age=age,
                user_region=location,
                special_supply_conditions=special_conditions,
                mainbank=bank
            )
            
            # 백엔드 처리
            #### 중요!
            response = get_document(request_data)
            
            # 응답 표시
            st.markdown("""
            <div class="response-section">
                <h2>상담 결과</h2>
                <div class="info-card">
            """, unsafe_allow_html=True)
            
            #### 수정
            st.markdown(response)
            ####


            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()