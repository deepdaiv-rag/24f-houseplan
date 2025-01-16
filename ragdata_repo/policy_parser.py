from collections import defaultdict

# 사업 운영 기간 파서
import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import re
from datetime import datetime, date

# 날짜 패턴별 정규표현식
date_patterns = {
    # 1. YYYY.MM.DD. ~ YYYY.MM.DD. 형식
    "full_date_dots": r"(\d{4})\.(\d{1,2})\.(\d{1,2})\.?\s*~\s*(\d{4})\.(\d{1,2})\.(\d{1,2})\.?",
    "A": "(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*~\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일",
    # 2. YYYY. MM. ~ YYYY. MM. 형식
    "year_month_dots": r"(\d{4})\.\s*(\d{1,2})\.\s*~\s*(\d{4})\.\s*(\d{1,2})\.",
    # 3. YYYY-MM-DD~YYYY-MM-DD 형식
    "full_date_hyphens": r"(\d{4})-(\d{2})-(\d{2})\s*~\s*(\d{4})-(\d{2})-(\d{2})",
    # 4. YYYY. M. ~ MM. 형식 (같은 해 다른 달)
    "same_year_months": r"(\d{4})\.\s*(\d{1,2})\.\s*~\s*(\d{1,2})\.",
    # 5. 'YY. ~ 'YY. 형식
    "short_years": r"\'(\d{2})\.\s*~\s*\'(\d{2})\.",
    # 6. 'YY. MM. ~ 'YY. MM. 형식
    "short_year_month": r"\'(\d{2})\.\s*(\d{1,2})\.\s*~\s*\'(\d{2})\.\s*(\d{1,2})\.",
    # 7. YYYY년 MM월 ~ YYYY년 MM월 형식
    "korean_date": r"(\d{4})[년]\s*(\d{1,2})[월]\s*~\s*(\d{4})[년]\s*(\d{1,2})[월]",
    # 8. YYYY.M ~ YYYY.MM 형식
    "year_month_minimal": r"(\d{4})\.(\d{1,2})\s*~\s*(\d{4})\.(\d{1,2})",
    # 9. [NEW] YYYY. ~ YYYY. 형식 (연도만)
    "years_only": r"(\d{4})\.\s*~\s*(\d{4})\.",
    # 5. 'YY.MM. ~ MM.' 형식 (연도 축약)
    "short_year_month_dots": r"'(\d{2})\.(\d{1,2})\.?\s*~\s*(\d{1,2})\.'",
    # 10. [NEW] YYYY. MM. DD.(요일) 형식
    "date_with_day": r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*\([월화수목금토일]\)",
    # 3. YYYY년 MM월 DD일 ~ YYYY년 MM월 DD일(예정) 형식
    "full_date_korean_with_optional_scheduled": r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*~\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일(?:\(예정\))?",
    # 11. [NEW] 특수 케이스 패턴
    "special_cases": r"(연중|예산소진시까지|계속사업|현재|상시|미정|-)",
    "bullet_full_year_month": r"[□○•]\s*(\d{4})\.(\d{1,2})\.\s*~\s*(\d{4})\.(\d{1,2})",  # □2024.3.~2024.12 패턴
    "bullet_short_year_month": r"[□○•][사업|추진]기간:\s*\'(\d{2})\.(\d{1,2})\.\s*~\s*(\d{1,2})\.(?:\s*※.*)?",  # ○사업기간:'24.1.~12. 패턴
    "bullet_period_short": r"[○•]\s*(?:추진|사업)기간:\s*\'(\d{2})\.(\d{1,2})\.\s*~\s*(\d{1,2})\.(?:\s*※.*)?",  # ○추진기간:'24.1.~12.
    "bullet_period_years": r"[•○]\s*사업기간:\s*\'(\d{2})\.(\d{1,2})\.\s*~\s*\'(\d{2})\.(\d{1,2})\.(?:\s*\([^)]+\))?",  # •사업기간:'24.2.~'26.12.
    "year_month_short": r"(\d{4})\.(\d{2})~(\d{2})",  # 2024.02~12
    "year_month_korean": r"(\d{4})\.(\d{1,2})월?\s*~\s*(\d{4})\.(\d{1,2})월?",  # 2024.1월~2024.12월
    "bullet_period_years_with_note": r"[•○]\s*사업기간:\s*\'(\d{2})\.(\d{1,2})\.\s*~\s*\'(\d{2})\.(\d{1,2})\.\s*\(※[^)]+\)",
}


def convert_to_date(year, month=1, day=1):
    """Convert year, month, day components to datetime object"""
    try:
        return datetime(int(year), int(month) if month else 1, int(day) if day else 1)
    except (ValueError, TypeError):
        return None


def is_policy_active(period, current_date):
    """Check if policy is currently active based on period information"""
    if not period or period.get("type") == "special_case":
        return True

    # Start date check
    if period.get("start"):
        start_info = period["start"]
        start_date = convert_to_date(
            start_info.get("year"), start_info.get("month"), start_info.get("day")
        )
        if start_date and current_date < start_date:
            return False

    # End date check
    if period.get("end"):
        end_info = period["end"]
        end_date = convert_to_date(
            end_info.get("year"), end_info.get("month"), end_info.get("day")
        )
        if end_date and current_date > end_date:
            return False

    return True


def parse_date_string(date_str):
    """
    주어진 날짜 문자열에서 시작일과 종료일을 추출

    Args:
        date_str (str): 날짜 문자열

    Returns:
        dict: 파싱된 날짜 정보 또는 특수 케이스 문자열
    """
    # 특수 케이스 먼저 체크
    special_match = re.search(date_patterns["special_cases"], date_str)
    if special_match:
        return {"type": "special_case", "value": special_match.group(1)}

    for pattern_name, pattern in date_patterns.items():
        if pattern_name == "special_cases":
            continue

        match = re.search(pattern, date_str)
        if match:
            groups = match.groups()

            # 패턴별 결과 처리
            if pattern_name == "full_date_dots":
                return {
                    "type": "full_date",
                    "start": {"year": groups[0], "month": groups[1], "day": groups[2]},
                    "end": {"year": groups[3], "month": groups[4], "day": groups[5]},
                }
            elif pattern_name in [
                "year_month_dots",
                "korean_date",
                "year_month_minimal",
            ]:
                return {
                    "type": "year_month",
                    "start": {"year": groups[0], "month": groups[1]},
                    "end": {"year": groups[2], "month": groups[3]},
                }
            elif pattern_name == "full_date_hyphens":
                return {
                    "type": "full_date",
                    "start": {"year": groups[0], "month": groups[1], "day": groups[2]},
                    "end": {"year": groups[3], "month": groups[4], "day": groups[5]},
                }
            elif pattern_name == "same_year_months":
                return {
                    "type": "same_year_months",
                    "start": {"year": groups[0], "month": groups[1]},
                    "end": {"year": groups[0], "month": groups[2]},
                }
            elif pattern_name == "short_years":
                start_year = "20" + groups[0]
                end_year = "20" + groups[1]
                return {
                    "type": "years_only",
                    "start": {"year": start_year},
                    "end": {"year": end_year},
                }
            elif pattern_name == "short_year_month":
                start_year = "20" + groups[0]
                end_year = "20" + groups[2]
                return {
                    "type": "year_month",
                    "start": {"year": start_year, "month": groups[1]},
                    "end": {"year": end_year, "month": groups[3]},
                }
            elif pattern_name == "years_only":
                return {
                    "type": "years_only",
                    "start": {"year": groups[0]},
                    "end": {"year": groups[1]},
                }
            elif pattern_name == "date_with_day":
                return {
                    "type": "single_date_with_day",
                    "date": {"year": groups[0], "month": groups[1], "day": groups[2]},
                }
            elif pattern_name == "full_date_korean_with_optional_scheduled":
                return {
                    "type": "full_date_korean_with_optional_scheduled",
                    "start": {"year": groups[0], "month": groups[1], "day": groups[2]},
                    "end": {"year": groups[3], "month": groups[4], "day": groups[5]},
                }
            elif pattern_name == "A":
                return {
                    "type": "A",
                    "start": {"year": groups[0], "month": groups[1], "day": groups[2]},
                    "end": {"year": groups[3], "month": groups[4], "day": groups[5]},
                }
            elif pattern_name == "short_year_month_dots":
                return {
                    "type": "short_year_month_dots",
                    "start": {"year": groups[0], "month": groups[1]},
                    "end": {"year": groups[0], "month": groups[2]},
                }
            elif pattern_name == "bullet_full_year_month":
                return {
                    "type": "year_month",
                    "start": {"year": groups[0], "month": groups[1]},
                    "end": {"year": groups[2], "month": groups[3]},
                }

            elif pattern_name == "bullet_short_year_month":
                start_year = "20" + groups[0]
                return {
                    "type": "same_year_months",
                    "start": {"year": start_year, "month": groups[1]},
                    "end": {"year": start_year, "month": groups[2]},
                }
            # parse_date_string 함수 내 if-elif 문에 추가
            elif pattern_name == "bullet_period_short":
                start_year = "20" + groups[0]
                return {
                    "type": "same_year_months",
                    "start": {"year": start_year, "month": groups[1]},
                    "end": {"year": start_year, "month": groups[2]},
                }

            elif pattern_name == "bullet_period_years":
                start_year = "20" + groups[0]
                end_year = "20" + groups[2]
                return {
                    "type": "year_month",
                    "start": {"year": start_year, "month": groups[1]},
                    "end": {"year": end_year, "month": groups[3]},
                }

            elif pattern_name == "year_month_short":
                return {
                    "type": "same_year_months",
                    "start": {"year": groups[0], "month": groups[1]},
                    "end": {"year": groups[0], "month": groups[2]},
                }

            elif pattern_name == "year_month_korean":
                return {
                    "type": "year_month",
                    "start": {"year": groups[0], "month": groups[1]},
                    "end": {"year": groups[2], "month": groups[3]},
                }
            # parse_date_string 함수 내 if-elif 문에 추가
            elif pattern_name == "bullet_period_years_with_note":
                start_year = "20" + groups[0]
                end_year = "20" + groups[2]
                return {
                    "type": "year_month",
                    "start": {"year": start_year, "month": groups[1]},
                    "end": {"year": end_year, "month": groups[3]},
                }

    return None


def parse_operating_periods(text):
    # Regular expression to match date ranges
    status_pattern = r"상시|미정"

    results = []

    for line in text.splitlines():
        # Check for date ranges
        date_match = re.search(date_patterns, line)
        if date_match:
            (
                start_year,
                start_month,
                start_day,
                end_year,
                end_month,
                end_day,
            ) = date_match.groups()
            results.append(
                {
                    "start_date": f"{start_year}-{int(start_month):02d}-{int(start_day):02d}",
                    "end_date": f"{end_year}-{int(end_month):02d}-{int(end_day):02d}",
                }
            )
        else:
            # Check for '상시' or '미정'
            status_match = re.search(status_pattern, line)
            if status_match:
                results.append({"start_date": "0000-0-0", "end_date": "9999-99-99"})

    return results


def extract_age_range(text):
    # 정규 표현식 정의
    age_pattern = r"(?:(?:만\s*)?(\d+)\s*세\s*~\s*(\d+)\s*세|(?:만\s*)?(\d+)\s*세\s*~\s*제한 없음|(?:만\s*)?제한 없음)"
    match = re.search(age_pattern, text)

    if match:
        if match.group(1) and match.group(2):  # "만 19세 ~ 34세" 형태
            min_age = int(match.group(1))
            max_age = int(match.group(2))
        elif match.group(3):  # "만 19세 ~ 제한 없음" 형태
            min_age = int(match.group(3))
            max_age = 9999
        else:  # "제한 없음" 형태
            min_age = 0
            max_age = 9999
    else:
        # 매치되지 않을 경우 기본 값
        min_age = 0
        max_age = 9999

    return min_age, max_age


regions = {
    ("서울"): [
        "종로",
        "중구",
        "용산",
        "성동",
        "광진",
        "동대문",
        "중랑",
        "성북",
        "강북",
        "도봉",
        "노원",
        "은평",
        "서대문",
        "마포",
        "양천",
        "강서",
        "구로",
        "금천",
        "영등포",
        "동작",
        "관악",
        "서초",
        "강남",
        "송파",
        "강동",
    ],
    ("부산"): [
        "중구",
        "서구",
        "동구",
        "영도",
        "부산진",
        "동래",
        "남구",
        "북구",
        "해운대",
        "사하",
        "금정",
        "강서",
        "연제",
        "수영",
        "사상",
        "기장",
    ],
    ("대구"): ["중구", "동구", "서구", "남구", "북구", "수성", "달서", "달성"],
    ("인천"): ["중구", "동구", "미추홀", "연수", "남동", "부평", "계양", "서구", "강화", "옹진"],
    ("광주"): ["동구", "서구", "남구", "북구", "광산"],
    ("대전"): ["동구", "중구", "서구", "유성", "대덕"],
    ("울산"): ["중구", "남구", "동구", "북구", "울주"],
    ("세종"): ["세종"],
    ("경기"): [
        "수원",
        "성남",
        "안양",
        "안산",
        "용인",
        "부천",
        "광명",
        "평택",
        "과천",
        "오산",
        "시흥",
        "군포",
        "의왕",
        "하남",
        "이천",
        "안성",
        "김포",
        "화성",
        "광주",
        "양주",
        "포천",
        "여주",
        "연천",
        "가평",
        "양평",
    ],
    ("강원"): [
        "춘천",
        "원주",
        "강릉",
        "동해",
        "태백",
        "속초",
        "삼척",
        "홍천",
        "횡성",
        "영월",
        "평창",
        "정선",
        "철원",
        "화천",
        "양구",
        "인제",
        "고성",
        "양양",
    ],
    ("충북", "충청북도"): ["청주", "충주", "제천", "보은", "옥천", "영동", "증평", "진천", "괴산", "음성", "단양"],
    ("충남", "충청남도"): [
        "천안",
        "공주",
        "보령",
        "아산",
        "서산",
        "논산",
        "계룡",
        "당진",
        "금산",
        "부여",
        "서천",
        "청양",
        "홍성",
        "예산",
        "태안",
    ],
    ("전북", "전라북도"): [
        "전주",
        "군산",
        "익산",
        "정읍",
        "남원",
        "김제",
        "완주",
        "진안",
        "무주",
        "장수",
        "임실",
        "순창",
        "고창",
        "부안",
    ],
    ("전남", "전라남도"): [
        "목포",
        "여수",
        "순천",
        "나주",
        "광양",
        "담양",
        "곡성",
        "구례",
        "고흥",
        "보성",
        "화순",
        "장흥",
        "강진",
        "해남",
        "영암",
        "무안",
        "함평",
        "영광",
        "장성",
        "완도",
        "진도",
        "신안",
    ],
    ("경북", "경상북도"): [
        "포항",
        "경주",
        "김천",
        "안동",
        "구미",
        "영주",
        "영천",
        "상주",
        "문경",
        "경산",
        "군위",
        "의성",
        "청송",
        "영양",
        "영덕",
        "청도",
        "고령",
        "성주",
        "칠곡",
        "예천",
        "봉화",
        "울진",
        "울릉",
    ],
    ("경남", "경상남도"): [
        "창원",
        "진주",
        "통영",
        "사천",
        "김해",
        "밀양",
        "거제",
        "양산",
        "의령",
        "함안",
        "창녕",
        "고성",
        "남해",
        "하동",
        "산청",
        "함양",
        "거창",
        "합천",
    ],
    ("제주"): ["제주", "서귀포"],
}


def classify_regions(entries, regions):
    result = defaultdict(list)

    for entry in entries:
        matched = False
        for regionss in regions.keys():
            if type(regionss) == tuple:
                for region in regionss:
                    if region in entry:
                        result[regionss[0]].append(entry)
                        matched = True
                        break
                if matched:
                    break
            else:
                if regionss in entry:
                    result[regionss].append(entry)
                    matched = True
                    break
        if not matched:
            for region, subregions in regions.items():
                if any(subregion in entry for subregion in subregions):
                    result[region].append(entry)
                    matched = True
                    break
        if not matched:
            result["전국"].append(entry)

    return result


def parse_policy_details(policy_data, debug=False, debugDate=False):
    """Parse and extract relevant details from each policy"""
    parsed_policies = []

    for policy in policy_data:
        details = {detail["Title"]: detail["Content"] for detail in policy["Details"]}

        parsed_policy = {
            "title": policy["Policy Title"],
            "description": policy["Description"],
        }

        # Parse support period
        support_period = "".join(details.get("사업 신청 기간", "__").split())
        if support_period:
            parsed_policy["support_period"] = parse_date_string(support_period)

        # Parse operating period
        operating_period = "".join(details.get("사업 운영 기간", "__").split())
        if operating_period:
            parsed_policy["operating_period"] = parse_date_string(operating_period)
        if debugDate:
            if parsed_policy["operating_period"] == None:
                print(operating_period)
            if parsed_policy["support_period"] == None:
                print(support_period)

        # Parse age requirements
        age_str = details.get("연령", "제한없음")
        min_age, max_age = extract_age_range(age_str)
        parsed_policy["age_range"] = {
            "min_age": min_age,
            "max_age": max_age if max_age != 9999 else None,
        }

        # Parse managing organization and region
        managing_org = details.get("주관 기관", "")
        residence_info = details.get("거주지 및 소득", "")

        org_regions = classify_regions([managing_org], regions)
        residence_regions = classify_regions([residence_info], regions)

        parsed_policy["managing_regions"] = set()
        for region, entries in org_regions.items():
            if entries:
                parsed_policy["managing_regions"].add(region)

        parsed_policy["residence_regions"] = set()
        for region, entries in residence_regions.items():
            if entries:
                parsed_policy["residence_regions"].add(region)

        parsed_policy["original_link"] = policy.get("Original Link", "")
        parsed_policy["details"] = details

        parsed_policies.append(parsed_policy)

        if debug:
            print(
                f'{age_str}: {parsed_policy["age_range"]}, {support_period}: {parsed_policy["support_period"]}, {operating_period}: {parsed_policy["operating_period"]}, {managing_org}:{parsed_policy["managing_regions"]}, {residence_info}:{parsed_policy["residence_regions"]}'
            )

    return parsed_policies


def filter_available_policies(parsed_policies, user_age, user_region, current_date):
    """Filter policies based on user criteria"""
    available_policies = []

    for policy in parsed_policies:
        # Check age eligibility
        age_eligible = (policy["age_range"]["min_age"] <= user_age) and (
            policy["age_range"]["max_age"] is None
            or user_age <= policy["age_range"]["max_age"]
        )

        # Check region eligibility
        region_eligible = (
            "전국" in policy["managing_regions"]
            or user_region in policy["managing_regions"]
        ) and (
            "전국" in policy["residence_regions"]
            or user_region in policy["residence_regions"]
        )

        # Check if policy is currently active based on support period
        support_period_active = is_policy_active(
            policy.get("support_period"), current_date
        )

        # Check if policy is currently active based on operating period
        operating_period_active = is_policy_active(
            policy.get("operating_period"), current_date
        )

        if (
            age_eligible
            and region_eligible
            and support_period_active
            and operating_period_active
        ):
            available_policies.append(
                {
                    "title": policy["title"],
                    "description": policy["description"],
                    "link": policy["original_link"],
                    "details": policy["details"],
                }
            )

    return available_policies


def get_policy_recommendations(policy_data, user_age, user_region, current_date_str):
    """Main function to get policy recommendations"""
    current_date = datetime.strptime(current_date_str, "%Y-%m-%d")

    # debug와 debugDate 값을 전달
    parsed_policies = parse_policy_details(
        policy_data, debug=False, debugDate=False  # 기본값 설정  # 기본값 설정
    )

    # Filter available policies
    available_policies = filter_available_policies(
        parsed_policies, user_age, user_region, current_date
    )

    return available_policies


def policy_parser(user_input: dict):
    with open(
        "/Users/hyottz/Desktop/24f-houseplan/24f_daiv_houseplan/data/filtered_policies.json",
        "r",
        encoding="utf-8",
    ) as f:
        json_data = f.read()
    data = json.loads(json_data)
    recommendations = get_policy_recommendations(
        data,
        user_input["user_age"],
        user_input["user_region"],
        user_input["current_date"],
    )
    return recommendations


if __name__ == "__main__":
    user_input = {
        "current_date": "2025-01-10",
        "user_age": 31,
        "user_region": "서울",
        "debug": False,
        "debugDate": False,
    }

    recommendations = policy_parser(user_input)

    for idx, policy in enumerate(recommendations, 1):
        print(f"\n=== 추천 정책 {idx} ===")
        print(f"제목: {policy['title']}")
        print(f"설명: {policy['description']}")
        print(f"연령: {policy['details'].get('연령')}")
        print(f"신청: {policy['details'].get('사업 신청 기간')}")
        print(f"기관: {policy['details'].get('주관 기관')}")
        print(f"지역: {policy['details'].get('거주지 및 소득')}")
        print(f"상세 정보: {policy['link']}")
