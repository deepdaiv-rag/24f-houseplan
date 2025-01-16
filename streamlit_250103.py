import streamlit as st
import json
from typing import List, Dict, Any
from dataclasses import dataclass
import pandas as pd
import re

st.set_page_config(
    page_title="주거 지원 정책 매칭 시스템",
    page_icon="🏠",
    layout="wide"
)

@dataclass
class UserProfile:
    # 기존 필드
    age: int
    income: float
    residence_city: str
    residence_district: str
    is_married: bool
    has_own_house: bool
    education: str
    major: str
    employment_status: str
    
    # 추가 필드
    housing_subscription_account: bool = False  # 청약통장 가입 여부
    # 가구 구성 정보
    independent_household: bool = False  # 부모와 별도 거주 여부
    household_members: int = 1  # 가구원 수
    children_count: int = 0  # 자녀 수
    # 재산 정보
    personal_assets: float = 0  # 본인 재산 (만원)
    parent_assets: float = 0  # 부모 재산 (만원)
    # 주거 정보
    housing_type: str = "월세"  # 월세/전세/기타
    deposit_amount: float = 0  # 임차보증금 (만원)
    monthly_rent: float = 0  # 월세 금액 (만원)
    # 거주 기간 정보
    residence_period: int = 0  # 현재 지역 거주 기간 (개월)
    is_moved_from_other_region: bool = False  # 타 지역 전입 여부

class PolicyMatcher:
    def __init__(self, policies_data: List[Dict[str, Any]]):
        self.policies = policies_data

    def match_policies(self, user: UserProfile) -> List[Dict[str, Any]]:
        matched_policies = []
        
        for policy in self.policies:
            if self._is_policy_match(policy, user):
                matched_policies.append(policy)
        
        return matched_policies
        
    def _parse_amount(self, text: str) -> float:
        """금액 문자열을 숫자로 변환"""
        try:
            # "5천만원", "1억 5천만원" 등의 형식 처리
            text = text.replace("억", "0000").replace("천", "000").replace("만원", "")
            return float(text.strip())
        except:
            return float('inf')
    
    def _check_household_requirements(self, requirements: str, user: UserProfile) -> bool:
        """가구 구성 요건 체크"""
        if "부모" in requirements and "별도" in requirements:
            if not user.independent_household:
                return False
                
        if "가구원수" in requirements:
            try:
                required_members = int(re.search(r'가구원수 (\d+)인', requirements).group(1))
                if user.household_members < required_members:
                    return False
            except:
                pass
                
        return True
    
    def _check_asset_requirements(self, requirements: str, user: UserProfile) -> bool:
        """재산 요건 체크"""
        if "재산" in requirements:
            try:
                # 예: "재산 122백만원 이하"
                asset_limit = float(re.search(r'재산 (\d+)백만원', requirements).group(1)) * 100
                if user.personal_assets > asset_limit:
                    return False
                    
                if "원가구" in requirements:
                    parent_asset_limit = float(re.search(r'원가구.*재산 (\d+)백만원', requirements).group(1)) * 100
                    if user.parent_assets > parent_asset_limit:
                        return False
            except:
                pass
                
        return True
    
    def _check_housing_requirements(self, requirements: str, user: UserProfile) -> bool:
        """주거 조건 체크"""
        if "임차보증금" in requirements:
            try:
                deposit_limit = self._parse_amount(re.search(r'임차보증금 ([\d천억만원]+)', requirements).group(1))
                if user.deposit_amount > deposit_limit:
                    return False
            except:
                pass
                
        if "월세" in requirements:
            try:
                rent_limit = float(re.search(r'월세 (\d+)만원', requirements).group(1))
                if user.monthly_rent > rent_limit:
                    return False
            except:
                pass
                
        return True
    
    def _check_residence_period(self, requirements: str, user: UserProfile) -> bool:
        """거주 기간 요건 체크"""
        if "이상 거주" in requirements:
            try:
                required_months = int(re.search(r'(\d+)년', requirements).group(1)) * 12
                if user.residence_period < required_months:
                    return False
            except:
                pass
                
        if "전입" in requirements and user.is_moved_from_other_region:
            if "타 지역 전입 제외" in requirements:
                return False
                
        return True
    
    def _check_subscription_account(self, requirements: str, user: UserProfile) -> bool:
        """청약통장 요건 체크"""
        if "청약통장" in requirements and "필수" in requirements:
            return user.housing_subscription_account
        return True
    
    def _is_policy_match(self, policy: Dict[str, Any], user: UserProfile) -> bool:
        details = {detail["Title"]: detail["Content"] for detail in policy["Details"]}
        
        # Get residence and income requirements
        residence_income = details.get("거주지 및 소득", "-")
        
        # Check all requirements
        if not all([
            self._check_household_requirements(residence_income, user),
            self._check_asset_requirements(residence_income, user),
            self._check_housing_requirements(residence_income, user),
            self._check_residence_period(residence_income, user),
            self._check_subscription_account(residence_income, user)
        ]):
            return False
            
        return True
def create_policy_df(policies: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert policy data to a DataFrame for display"""
    policy_data = []
    
    for policy in policies:
        details = {detail["Title"]: detail["Content"] for detail in policy["Details"]}
        
        # 신청 자격 정보 추출
        eligibility_info = []
        if "연령" in details:
            eligibility_info.append(f"연령: {details['연령']}")
        if "거주지 및 소득" in details:
            eligibility_info.append(f"거주지/소득: {details['거주지 및 소득']}")
        if "학력" in details:
            eligibility_info.append(f"학력: {details['학력']}")
        if "취업 상태" in details:
            eligibility_info.append(f"취업상태: {details['취업 상태']}")
        if "참여 제한 대상" in details:
            eligibility_info.append(f"제한대상: {details['참여 제한 대상']}")
            
        policy_data.append({
            "정책명": policy["Policy Title"],
            "설명": policy["Description"],
            "신청자격": "\n".join(eligibility_info),
            "지원 내용": details.get("지원 내용", "상세내용 없음"),
            "신청 기간": details.get("사업 신청 기간", "상시"),
            "신청 방법": details.get("신청 절차", "-"),
            "상세 링크": policy["Original Link"]
        })
    
    return pd.DataFrame(policy_data)

def get_districts_by_city() -> Dict[str, List[str]]:
    """도시별 구/군 정보를 반환"""
    return {
    "서울특별시": [
        "종로구", "중구", "용산구", "성동구", "광진구", "동대문구", "중랑구", "성북구", 
        "강북구", "도봉구", "노원구", "은평구", "서대문구", "마포구", "양천구", "강서구", 
        "구로구", "금천구", "영등포구", "동작구", "관악구", "서초구", "강남구", "송파구", "강동구"
    ],
    "부산광역시": [
        "중구", "서구", "동구", "영도구", "부산진구", "동래구", "남구", "북구", "해운대구", 
        "사하구", "금정구", "강서구", "연제구", "수영구", "사상구", "기장군"
    ],
    "대구광역시": [
        "중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군"
    ],
    "인천광역시": [
        "중구", "동구", "미추홀구", "연수구", "남동구", "부평구", "계양구", "서구", "강화군", "옹진군"
    ],
    "광주광역시": [
        "동구", "서구", "남구", "북구", "광산구"
    ],
    "대전광역시": [
        "동구", "중구", "서구", "유성구", "대덕구"
    ],
    "울산광역시": [
        "중구", "남구", "동구", "북구", "울주군"
    ],
    "세종특별자치시": [
        "세종시"
    ],
    "경기도": [
        "수원시", "성남시", "안양시", "안산시", "용인시", "부천시", "광명시", "평택시", 
        "과천시", "오산시", "시흥시", "군포시", "의왕시", "하남시", "이천시", "안성시", 
        "김포시", "화성시", "광주시", "양주시", "포천시", "여주시", 
        "연천군", "가평군", "양평군"
    ],
    "강원도": [
        "춘천시", "원주시", "강릉시", "동해시", "태백시", "속초시", "삼척시", 
        "홍천군", "횡성군", "영월군", "평창군", "정선군", "철원군", "화천군", "양구군", "인제군", "고성군", "양양군"
    ],
    "충청북도": [
        "청주시", "충주시", "제천시", 
        "보은군", "옥천군", "영동군", "증평군", "진천군", "괴산군", "음성군", "단양군"
    ],
    "충청남도": [
        "천안시", "공주시", "보령시", "아산시", "서산시", "논산시", "계룡시", "당진시", 
        "금산군", "부여군", "서천군", "청양군", "홍성군", "예산군", "태안군"
    ],
    "전라북도": [
        "전주시", "군산시", "익산시", "정읍시", "남원시", "김제시", 
        "완주군", "진안군", "무주군", "장수군", "임실군", "순창군", "고창군", "부안군"
    ],
    "전라남도": [
        "목포시", "여수시", "순천시", "나주시", "광양시", 
        "담양군", "곡성군", "구례군", "고흥군", "보성군", "화순군", "장흥군", "강진군", "해남군", 
        "영암군", "무안군", "함평군", "영광군", "장성군", "완도군", "진도군", "신안군"
    ],
    "경상북도": [
        "포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시", "상주시", 
        "문경시", "경산시", 
        "군위군", "의성군", "청송군", "영양군", "영덕군", "청도군", "고령군", "성주군", "칠곡군", 
        "예천군", "봉화군", "울진군", "울릉군"
    ],
    "경상남도": [
        "창원시", "진주시", "통영시", "사천시", "김해시", "밀양시", "거제시", "양산시", 
        "의령군", "함안군", "창녕군", "고성군", "남해군", "하동군", "산청군", "함양군", "거창군", "합천군"
    ],
    "제주특별자치도": [
        "제주시", "서귀포시"
    ],
        "기타": ["기타"]
    }

def main():
    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            height: 3em;
            margin-top: 2em;
        }
        .big-font {
            font-size:20px !important;
            font-weight: bold;
        }
        .policy-card {
            border: 1px solid #ddd;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }
        .eligibility-info {
            background-color: #f8f9fa;
            padding: 0.5rem;
            margin: 0.5rem 0;
            border-radius: 4px;
        }
        .input-section {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border: 1px solid #e1e4e8;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🏠 주거 지원 정책 매칭 시스템")
    
    try:
        with open('filtered_policies.json', 'r', encoding='utf-8') as f:
            policies_data = json.load(f)
    except FileNotFoundError:
        st.error("정책 데이터 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError:
        st.error("정책 데이터 파일이 올바른 형식이 아닙니다.")
        return
    # 탭 생성
    tabs = st.tabs(["기본 정보", "가구 정보", "주거 정보", "자산 정보"])
    
    with tabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👤 개인 정보")
            with st.container():
                age = st.number_input("나이", min_value=19, max_value=100, value=25)
                income = st.number_input("연간 소득 (만원)", min_value=0, value=3000)
                education = st.selectbox(
                    "최종학력",
                    options=["고졸 이하", "고졸", "전문대졸", "대졸", "대학원졸"]
                )
                major = st.selectbox(
                    "전공분야",
                    options=["인문", "사회", "공학", "자연", "예체능", "의학", "기타"]
                )
                employment_status = st.selectbox(
                    "취업상태",
                    options=["미취업", "취업준비중", "재직중", "창업준비중", "창업", "기타"]
                )
                
        with col2:
            st.markdown("### 📍 거주지 정보")
            with st.container():
                # 거주지 선택 개선
                districts_by_city = get_districts_by_city()
                cities = list(districts_by_city.keys())
                
                residence_city = st.selectbox("거주 지역 (시/도)", options=cities)
                residence_district = st.selectbox(
                    "상세 지역 (시/군/구)", 
                    options=districts_by_city[residence_city]
                )
                
                # 거주 기간
                col_period1, col_period2 = st.columns(2)
                with col_period1:
                    years = st.number_input("거주 기간 (년)", min_value=0, max_value=100, value=0)
                with col_period2:
                    months = st.number_input("거주 기간 (개월)", min_value=0, max_value=11, value=0)
                
                is_moved = st.radio(
                    "타지역 전입 여부",
                    options=["예", "아니오"],
                    horizontal=True
                ) == "예"

    with tabs[1]:
        st.markdown("### 👨‍👩‍👧‍👦 가구 구성 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            is_married = st.radio("결혼 여부", options=["미혼", "기혼"], horizontal=True) == "기혼"
            independent_household = st.radio(
                "부모와 별도 거주 여부",
                options=["예", "아니오"],
                horizontal=True
            ) == "예"
            
            household_members = st.number_input("가구원 수", min_value=1, value=1)
            if is_married:
                children_count = st.number_input("자녀 수", min_value=0, value=0)
            else:
                children_count = 0
                
        with col2:
            st.markdown("##### 가구원 정보")
            st.info("가구원 수에 따라 소득 및 자산 기준이 달라질 수 있습니다.")
            
            if household_members > 1:
                st.text_input("가구원1 관계", value="본인", disabled=True)
                for i in range(2, household_members + 1):
                    st.text_input(f"가구원{i} 관계")

    with tabs[2]:
        st.markdown("### 🏠 주거 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            has_house = st.radio(
                "주택 소유 여부",
                options=["무주택", "주택 소유"],
                horizontal=True
            ) == "주택 소유"
            
            housing_type = st.selectbox(
                "거주 형태",
                options=["월세", "전세", "보증부월세", "기타"]
            )
            
            if housing_type in ["월세", "보증부월세"]:
                monthly_rent = st.number_input("월세 금액 (만원)", min_value=0, value=0)
            else:
                monthly_rent = 0
                
            if housing_type in ["전세", "보증부월세"]:
                deposit_amount = st.number_input("보증금 (만원)", min_value=0, value=0)
            else:
                deposit_amount = 0
                
        with col2:
            housing_subscription = st.radio(
                "청약통장 가입 여부",
                options=["예", "아니오"],
                horizontal=True
            ) == "예"
            
            if housing_subscription:
                subscription_period = st.number_input("청약통장 가입기간 (개월)", min_value=0, value=0)
            
            st.markdown("##### 📋 주거 지원 이력")
            previous_support = st.multiselect(
                "과거 주거 지원 수혜 이력",
                options=[
                    "주거급여",
                    "전월세 보증금 대출",
                    "청년 월세 지원",
                    "기타 주거 지원"
                ]
            )

    with tabs[3]:
        st.markdown("### 💰 자산 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 본인 자산")
            personal_assets = st.number_input("본인 재산 총액 (만원)", min_value=0, value=0)
            
            st.markdown("##### 부채 정보")
            has_loan = st.checkbox("대출 있음")
            if has_loan:
                loan_amount = st.number_input("대출 총액 (만원)", min_value=0, value=0)
            
        with col2:
            if not independent_household:
                st.markdown("##### 원가구(부모) 자산")
                parent_assets = st.number_input("부모 재산 총액 (만원)", min_value=0, value=0)
            else:
                parent_assets = 0

    # 검색 버튼
    if st.button("정책 검색하기", type="primary"):
        # Create user profile
        user = UserProfile(
            # 기본 정보
            age=age,
            income=income,
            residence_city=residence_city,
            residence_district=residence_district,
            is_married=is_married,
            has_own_house=has_house,
            education=education,
            major=major,
            employment_status=employment_status,
            # 추가 정보
            housing_subscription_account=housing_subscription,
            independent_household=independent_household,
            household_members=household_members,
            children_count=children_count,
            personal_assets=personal_assets,
            parent_assets=parent_assets,
            housing_type=housing_type,
            deposit_amount=deposit_amount,
            monthly_rent=monthly_rent,
            residence_period=years * 12 + months,
            is_moved_from_other_region=is_moved
        )

        # 검색 결과 표시 로직...
        with st.spinner('정책을 검색중입니다...'):
            # Find matching policies
            matcher = PolicyMatcher(policies_data)
            matched_policies = matcher.match_policies(user)

            # Display results
            st.markdown("---")
            st.subheader(f"📋 매칭된 정책 ({len(matched_policies)}건)")

            if not matched_policies:
                st.warning("매칭되는 정책이 없습니다.")
            else:
                # Convert to DataFrame for display
                df = create_policy_df(matched_policies)

                # Display each policy in an expander
                for idx, row in df.iterrows():
                    with st.expander(f"📌 {row['정책명']}", expanded=True):
                        # Two columns for main content
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("**정책 설명**")
                            st.write(row['설명'])
                            
                            st.markdown("**신청 자격**")
                            st.markdown('<div class="eligibility-info">' + 
                                      row['신청자격'].replace('\n', '<br>') + 
                                      '</div>', unsafe_allow_html=True)
                            
                            st.markdown("**지원 내용**")
                            st.write(row['지원 내용'])
                            
                        with col2:
                            st.markdown("**신청 기간**")
                            st.write(row['신청 기간'])
                            
                            st.markdown("**신청 방법**")
                            st.write(row['신청 방법'])
                            
                            st.markdown("**상세 정보**")
                            st.markdown(f"[🔗 자세히 보기]({row['상세 링크']})")

if __name__ == "__main__":
    main()