import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import get_document, RequestData

def calculate_age_group(age):
    if age < 20:
        return "10대"
    elif age < 30:
        return "20대"
    elif age < 40:
        return "30대"
    else:
        return "40대 이상"

def display_financial_plan(response_data, user_name):
    # Add refresh button at the top
    if st.button("🔄 새로고침"):
        st.rerun()
        
    # Updated CSS with new styles
    st.markdown("""
        <style>
            .hero-section {
                background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin-bottom: 2rem;
                text-align: center;
            }
            .plan-section {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 5px solid #4361ee;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .subsection {
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .metric-container {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 10px 0;
            }
            .metric-card {
                background-color: #e9ecef;
                padding: 15px;
                border-radius: 8px;
                flex: 1;
                min-width: 200px;
                transition: transform 0.2s;
            }
            .metric-card:hover {
                transform: translateY(-2px);
            }
            .highlight {
                color: #4361ee;
                font-weight: bold;
            }
            .step-container {
                border-left: 3px solid #4361ee;
                padding-left: 20px;
                margin: 10px 0;
            }
            .user-name {
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # New hero section with user name
    st.markdown(f"""
        <div class='hero-section'>
            <div class='user-name'>{user_name}님을 위한 주택 마련 계획</div>
            <p>맞춤형 금융 플랜을 통해 주택 마련의 꿈을 실현하세요</p>
        </div>
    """, unsafe_allow_html=True)

    # 1. 사용자 상황 분석
    with st.container():
        st.subheader("1️⃣ 사용자 상황 분석")
        
        user_analysis = response_data["user_analysis"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="**🎯이름**", value=user_analysis['name'])
            st.metric(label="**🎯연령**", value=f"{user_analysis['age']}")
        with col2:
            st.metric(label="**🏠지역**", value=user_analysis['region'])
            st.metric(label="**🏦주거래은행**", value=user_analysis['main_bank'])
        with col3:
            st.markdown("**✨ 특별조건**" if user_analysis['special_conditions'] else "")
            if user_analysis['special_conditions']:
                st.write(", ".join(user_analysis['special_conditions']))
            st.markdown("**💭 주요 고민 사항**")
            st.write(user_analysis['concerns'])

    # Rest of the sections remain similar but with updated styling
    # 2. 추천 정책 및 지원 사업
    # 2. 추천 정책 및 지원 사업
    with st.container():
        st.subheader("2️⃣ 추천 정책 및 지원 사업")

        # 추천 정책 반복 출력
        for policy in response_data["recommended_policies"]:
            with st.expander(f"🏠 {policy['policy_name']}"):
                # 추천 이유
                st.markdown("**💡 추천 이유**")
                st.write(policy["recommendation_reason"])

                # 두 열로 신청 자격과 혜택 나누기
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📋 신청 자격**")
                    # 신청 자격 항목 출력
                    for key, value in policy.get("eligibility", {}).items():
                        st.write(f"- {value}")
                with col2:
                    st.markdown("**🎁 혜택**")
                    # 혜택 설명 출력
                    st.write(policy.get("benefits", {}).get("description", "정보 없음"))


    # 3. 추천 금융 상품 포트폴리오
    with st.container():
        st.subheader("3️⃣ 추천 금융 상품 포트폴리오")

        # 금융 상품을 순차적으로 표시
        for product in response_data["recommended_financial_products"]:
            st.markdown(f"""
                <div class='metric-card'>
                    <h3>📍 {product['product_name']}</h3>
                    <p><strong>수익률:</strong> {product['expected_interest_rate']}</p>
                    <p><strong>추천 이유:</strong> {product['recommendation_reason']}</p>
                    <p><strong>가입 방법:</strong> {product['application_method']}</p>
                </div>
            """, unsafe_allow_html=True)

    

    # 4. 추천 주택 상품 포트폴리오
    with st.container():
        st.subheader("3️⃣ 추천 주택 상품 포트폴리오")

        # 주택 상품 개수만큼 열 생성
        cols = st.columns(len(response_data["recommended_housing_products"]))

        # 주택 상품 데이터를 순회하며 표시
        for idx, (col, product) in enumerate(zip(cols, response_data["recommended_housing_products"])):
            with col:
                st.markdown(f"""
                    <div class='metric-card'>
                        <h3>🏠 {product['product_name']}</h3>
                        <p><strong>추천 이유:</strong> {product['recommendation_reason']}</p>
                        <p><strong>신청 방법:</strong> {product['application_method']}</p>
                        <p><strong>신청 마감일:</strong> {product['application_deadline']}</p>
                    </div>
                """, unsafe_allow_html=True)

    # 5. 월간 저축 계획
    with st.container():
        st.subheader("4️⃣ 월간 저축 계획")
        
        savings_plan = response_data["monthly_savings_plan"]
        cols = st.columns(3)
        metrics = [
            ("🎯 목표액", savings_plan["goal_amount"]),
            ("💰 필수 저축액 (월)", savings_plan["mandatory_savings"]),
            ("✨ 권장 저축액 (월)", savings_plan["recommended_savings"])
        ]
        for col, (label, value) in zip(cols, metrics):
            with col:
                st.metric(label=label, value=value)

    # 6. 단계별 실행 계획
    with st.container():
        st.subheader("5️⃣ 단계별 실행 계획")
        
        timeline_labels = {
            "immediate": "즉시",
            "1_3_months": "1-3개월",
            "3_6_months": "3-6개월",
            "6_12_months": "6개월-1년",
            "12_months_plus": "1년 이상"
        }
        
        for step in response_data["step_by_step_plan"]:
            timeline = step["timeline"]
            for key, label in timeline_labels.items():
                if timeline[key]:
                    st.markdown(f"""
                        <div class='step-container'>
                            <h4>{label}</h4>
                            <p>{timeline[key]}</p>
                        </div>
                    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="맞춤형 주거/금융 상담 서비스",
        page_icon="🏠",
        layout="wide"
    )
    
    st.title("🏠 맞춤형 주거/금융 상담 서비스")
    
    # Add refresh button at the top of the page
    if st.button("🔄 새로고침", key="main_refresh"):
        st.rerun()
    
    # 사용자 정보 입력 폼
    with st.form("user_info"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름", placeholder="홍길동")
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
                ["국민은행", "기업은행", "농협은행", "신한은행", "우리은행", "카카오뱅크", "하나은행", "토스뱅크", "KDB산업은행", "SC제일은행"] 
            )
            
        concerns = st.text_area(
            "주요 고민사항",
            placeholder="Ex 1) 전세로 옮길려고 하는데 대출이 많이 나올까 궁금해요\
Ex 2) 학자금 대출이 남아있는데 월세까지 낼 생각하니 막막해요",
            height=100
        )
        
        submitted = st.form_submit_button("상담 받기")
    
    if submitted:
        if not name:
            st.error("이름을 입력해주세요!")
            return
            
        with st.spinner('맞춤형 금융 플랜을 생성하고 있습니다...'):
            # Create request data with name and concerns
            request_data = RequestData(
                user_name=name,
                user_age=age,
                user_region=location,
                special_supply_conditions=special_conditions,
                mainbank=bank,
                concerns=concerns
            )
            try:
                response_data = get_document(request_data)

                 # 응답이 문자열인지 확인
                if isinstance(response_data, str):
                        response_data = response_data.strip()

                        # 백틱(```) 제거
                        if response_data.startswith("```") and response_data.endswith("```"):
                            response_data = response_data[3:-3].strip()
                            
                        # 'json' 접두사가 있는 경우 제거
                        if response_data.startswith("json"):
                            response_data = response_data[response_data.find("{"):].strip()  # '{'부터 시작하도록 자르기

                        try:
                            # JSON 문자열을 Python 딕셔너리로 변환
                            response_data = json.loads(response_data)
                        except json.JSONDecodeError as e:
                            print(f"JSON 변환 실패: {str(e)}")
                            print(f"문제 발생 데이터: {response_data}")  # 디버깅용 출력
                            raise ValueError("JSON 문자열을 변환하는 데 실패했습니다.")
                elif not isinstance(response_data, dict):
                        raise ValueError("get_document 함수에서 반환된 데이터가 문자열 또는 딕셔너리가 아닙니다.")

                # Add name to user_analysis in response_data
                response_data["user_analysis"]["name"] = name
                # Display the financial plan
                display_financial_plan(response_data, name)
            except Exception as e:
                st.error(f"금융 플랜 생성 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()