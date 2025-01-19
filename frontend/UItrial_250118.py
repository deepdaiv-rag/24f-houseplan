import streamlit as st
from datetime import datetime

def display_financial_plan(response_text):
    # CSS 스타일 정의
    st.markdown("""
        <style>
            .plan-section {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 5px solid #4361ee;
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
                padding: 10px;
                border-radius: 5px;
                flex: 1;
                min-width: 200px;
            }
            .highlight {
                color: #4361ee;
                font-weight: bold;
            }
            .step-container {
                border-left: 2px solid #4361ee;
                padding-left: 20px;
                margin: 10px 0;
            }
        </style>
    """, unsafe_allow_html=True)


    """
    - 아래와 같이 어떻게 value 값 추출할지

    """

    # 1. 사용자 상황 분석
    with st.container():
        st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
        st.subheader("1️⃣ 사용자 상황 분석")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="연령", value="29세")
            st.metric(label="월 소득", value="290만원")
        with col2:
            st.metric(label="현재 저축액", value="300만원")
            st.metric(label="월세", value="50만원")
        with col3:
            st.metric(label="대출 여부", value="없음")
        
        st.markdown("**🎯 주요 고민 사항**")
        st.markdown("""
        - 주거비 부담 경감
        - 안정적인 주거 환경 확보
        - 향후 주택 구매를 위한 자산 축적
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. 추천 정책 및 지원 사업
    with st.container():
        st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
        st.subheader("2️⃣ 추천 정책 및 지원 사업")
        
        tab1, tab2 = st.tabs(["주택 연세·월세 대출이자 지원", "청년 주택 임차보증금 이자 지원"])
        
        with tab1:
            st.markdown("<div class='subsection'>", unsafe_allow_html=True)
            st.markdown("**💡 추천 이유**")
            st.write("무주택자로서 주거비 부담이 크고, 자녀 출산 계획이 없는 사회초년생에게 적합한 정책")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📋 신청 자격**")
                st.write("- 만 19세 ~ 39세\n- 무주택자\n- 제주도민")
            with col2:
                st.markdown("**🎁 혜택**")
                st.write("- 주택자금 대출 이율 3.5% 지원\n- 최대 21만원\n- 연 600만원 대출 가능")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='subsection'>", unsafe_allow_html=True)
            st.markdown("**💡 추천 이유**")
            st.write("청년의 주택 임차보증금 이자를 지원하여 주거비 부담 경감")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📋 신청 자격**")
                st.write("- 만 19세 ~ 39세\n- 중위소득 150% 이하")
            with col2:
                st.markdown("**🎁 혜택**")
                st.write("- 최대 4.5% 이자 지원\n- 대출한도 1억 5천만원 이내")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. 추천 금융 상품 포트폴리오
    with st.container():
        st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
        st.subheader("3️⃣ 추천 금융 상품 포트폴리오")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='subsection'>", unsafe_allow_html=True)
            st.markdown("**📍 KB Star 정기예금**")
            st.markdown("- 수익률: **2.5%**\n- 특징: 원금 보장, 안정적 수익\n- 가입: 지점 방문 또는 온라인 뱅킹")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='subsection'>", unsafe_allow_html=True)
            st.markdown("**📍 KB국민프리미엄적금**")
            st.markdown("- 수익률: **3.0%**\n- 특징: 월 적립식 고금리 상품\n- 가입: 지점 방문 또는 온라인 뱅킹")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. 월간 저축 계획
    with st.container():
        st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
        st.subheader("4️⃣ 월간 저축 계획")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="목표액 (1년)", value="1,000만원")
        with col2:
            st.metric(label="필수 저축액 (월)", value="50만원")
        with col3:
            st.metric(label="권장 저축액 (월)", value="80만원")
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. 단계별 실행 계획
    with st.container():
        st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
        st.subheader("5️⃣ 단계별 실행 계획")
        
        st.markdown("<div class='step-container'>", unsafe_allow_html=True)
        steps = {
            "즉시": "정책 신청 (주택 연세·월세 대출이자 지원)",
            "1-3개월": "금융 상품 가입 (KB Star 정기예금, KB국민프리미엄적금)",
            "3-6개월": "청약 준비 (청년행복주택 신청)",
            "6개월-1년": "저축 실행 및 대출 이자 지원 신청",
            "1년 이상": "주택 구매 계획 수립 및 자산 축적"
        }
        
        for period, action in steps.items():
            st.markdown(f"**{period}**: {action}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# 메인 앱에서 사용할 때는 아래와 같이 호출
def main():
    st.title("맞춤형 금융 플랜")
    display_financial_plan(None)  # response_text 파라미터 대신 실제 응답 텍스트를 넣으세요

if __name__ == "__main__":
    main()