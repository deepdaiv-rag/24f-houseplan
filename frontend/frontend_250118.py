import streamlit as st
import pandas as pd
from datetime import datetime

def calculate_age_group(age):
    if age < 20:
        return "10대"
    elif age < 30:
        return "20대"
    elif age < 40:
        return "30대"
    else:
        return "40대 이상"

def get_recommendations(age, location, special_conditions, bank, concerns):
    recommendations = {
        "사용자 상황 분석": {
            "연령대": f"{age}세",
            "거주지역": location,
            "특별조건": special_conditions,
            "주거래은행": bank,
            "주요 고민사항": concerns
        },
        "추천 정책 및 지원 사업": [],
        "추천 금융 상품": [],
        "추천 청약 상품": [],
        "월간 저축 계획": {},
        "단계별 실행 계획": []
    }
    
    # 연령대별 정책 추천
    age_group = calculate_age_group(age)
    if age_group in ["20대", "30대"]:
        recommendations["추천 정책 및 지원 사업"].append({
            "정책명": "청년 주택 임차보증금 이자 지원",
            "자격": "만 19세 ~ 39세, 중위소득 150% 이하",
            "혜택": "최대 4.5% 이자 지원, 대출한도 1억 5천만원 이내"
        })
    
    # 특별조건별 추천
    if "신혼부부" in special_conditions:
        recommendations["추천 청약 상품"].append({
            "상품명": "신혼부부 특별공급",
            "자격": "혼인기간 7년 이내",
            "혜택": "청약 가점 우대"
        })
    
    # 은행별 금융상품 추천
    if bank == "국민은행":
        recommendations["추천 금융 상품"].extend([
            {
                "상품명": "KB Star 정기예금",
                "수익률": "연 2.5%",
                "특징": "원금 보장, 안정적 수익"
            },
            {
                "상품명": "KB국민프리미엄적금",
                "수익률": "연 3.0%",
                "특징": "월 적립식 고금리 상품"
            }
        ])
    
    # 월간 저축 계획 수립
    monthly_income = 3500000 // 12  # 예시 연봉 기준
    recommendations["월간 저축 계획"] = {
        "목표액": "1,000만원 (1년 내)",
        "필수 저축액": "월 50만원",
        "권장 저축액": "월 80만원"
    }
    
    # 단계별 실행 계획
    recommendations["단계별 실행 계획"] = [
        "즉시: 정책 신청",
        "1-3개월: 금융 상품 가입",
        "3-6개월: 청약 준비",
        "6개월-1년: 저축 실행",
        "1년 이상: 주택 구매 계획 수립"
    ]
    
    return recommendations


# CSS 스타일 정의
def local_css():
    st.markdown("""
    <style>
        .section-box {
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .analysis-section {
            background-color: #E8F4FA;
        }
        .policy-section {
            background-color: #E8F0E8;
        }
        .financial-section {
            background-color: #FAF0E6;
        }
        .housing-section {
            background-color: #F5E6E8;
        }
        .savings-section {
            background-color: #E6E6FA;
        }
        .plan-section {
            background-color: #F0FFF0;
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


def display_section(title, content, section_class):
    st.markdown(f"""
        <div class="section-box {section_class}">
            <h2>{title}</h2>
            {content}
        </div>
    """, unsafe_allow_html=True)

def format_analysis(analysis):
    content = "<div class='info-card'>"
    for key, value in analysis.items():
        content += f"<p><strong>{key}</strong>: {value}</p>"
    content += "</div>"
    return content

def format_policies(policies):
    content = ""
    for policy in policies:
        content += f"""
        <div class='info-card'>
            <h3>{policy['정책명']}</h3>
            <p><strong>신청 자격</strong>: {policy['자격']}</p>
            <p><strong>혜택</strong>: {policy['혜택']}</p>
        </div>
        """
    return content

def format_products(products):
    content = ""
    for product in products:
        content += f"""
        <div class='info-card'>
            <h3>{product['상품명']}</h3>
            <p><strong>예상 수익률</strong>: {product['수익률']}</p>
            <p><strong>특징</strong>: {product['특징']}</p>
        </div>
        """
    return content

def format_savings_plan(plan):
    content = "<div class='info-card'>"
    for key, value in plan.items():
        content += f"<p><strong>{key}</strong>: {value}</p>"
    content += "</div>"
    return content

def format_action_plan(steps):
    content = "<div class='info-card'><ol>"
    for step in steps:
        content += f"<li>{step}</li>"
    content += "</ol></div>"
    return content

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
        recommendations = get_recommendations(age, location, special_conditions, bank, concerns)
        
        # 결과 표시 - 섹션별로 다른 색상의 박스 사용
        display_section(
            "1. 사용자 상황 분석",
            format_analysis(recommendations["사용자 상황 분석"]),
            "analysis-section"
        )
        
        display_section(
            "2. 추천 정책 및 지원 사업",
            format_policies(recommendations["추천 정책 및 지원 사업"]),
            "policy-section"
        )
        
        display_section(
            "3. 추천 금융 상품",
            format_products(recommendations["추천 금융 상품"]),
            "financial-section"
        )
        
        display_section(
            "4. 추천 청약 상품",
            format_policies(recommendations["추천 청약 상품"]),
            "housing-section"
        )
        
        display_section(
            "5. 월간 저축 계획",
            format_savings_plan(recommendations["월간 저축 계획"]),
            "savings-section"
        )
        
        display_section(
            "6. 단계별 실행 계획",
            format_action_plan(recommendations["단계별 실행 계획"]),
            "plan-section"
        )

if __name__ == "__main__":
    main()