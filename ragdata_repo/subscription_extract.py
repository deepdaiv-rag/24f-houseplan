import os
import pdfplumber
import pandas as pd
import re

# 현재 작업 디렉토리 확인
# current_dir = "/Users/hyottz/Desktop/24f-houseplan/24f_daiv_houseplan"
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 상대 경로 설정
api_data_path = os.path.join(current_dir, "data/api_data")
crawl_data_path = os.path.join(current_dir, "data/crawl_data")


# PDF 파일 읽기 함수
def read_pdf_files(directory_path):
    pdf_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files


# 텍스트 추출 함수
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None


# API 메타데이터 추출 함수
def extract_metadata_api(text, max_supply_price):
    metadata = {
        "supply_name": None,
        "region_name": None,
        "application_schedule": None,
        "special_supply_conditions": [],
        "enter_day": None,
        "max_supply_price": max_supply_price,
    }

    # 공급명 추출
    supply_name_match = re.search(r"입주자모집공고주요정보\s*(.+)", text)
    if supply_name_match:
        metadata["supply_name"] = supply_name_match.group(1).strip()

    # 지역명 추출
    region_name_match = re.search(r"공급위치\s*(.+)", text)
    if region_name_match:
        metadata["region_name"] = region_name_match.group(1).strip()

    # 청약일정 추출
    schedule_match = re.search(r"당첨자 발표일\s*(\d{4}-\d{2}-\d{2})", text)
    if schedule_match:
        metadata["application_schedule"] = schedule_match.group(1).strip()

    # 특별공급조건 추출
    special_conditions_keywords = ["다자녀", "신혼부", "생애최", "노부모", "신생아", "청년"]
    for keyword in special_conditions_keywords:
        if keyword in text:
            metadata["special_supply_conditions"].append(keyword)

    # 입주예정월 추출
    enter_day_match = re.search(r"입주예정월 :\s*(\d{4}\.\d{2})", text)
    if enter_day_match:
        metadata["enter_day"] = enter_day_match.group(1).strip()

    return metadata


# Crawl 메타데이터 추출 함수
def extract_metadata_crawl(text):
    metadata = {
        "supply_name": None,
        "region_name": None,
        "supply_type": None,
        "area": None,
        "application_schedule": None,
        "special_supply_conditions": [],
    }

    # 공급명 추출
    supply_name_match = re.search(r"(.+?)\.pdf 바로보기", text)
    if supply_name_match:
        metadata["supply_name"] = supply_name_match.group(1).strip()

    # 지역명 추출
    region_name_match = re.search(
        r"모집지역\s*:\s*(.+?)$|소재지\s*:\s*(.+?)$", text, re.MULTILINE
    )
    if region_name_match:
        region_name = region_name_match.group(1) or region_name_match.group(2)
        if "확인" not in region_name:
            metadata["region_name"] = region_name.strip()

    # 공급유형 추출
    supply_type_match = re.search(r"유형\s*:\s*(.+?)\s", text)
    if supply_type_match:
        metadata["supply_type"] = supply_type_match.group(1).strip()

    # 면적 추출
    area_match = re.search(r"전용면적\(㎡\)\s*:\s*(\d+\.\d+)", text)
    if area_match:
        metadata["area"] = area_match.group(1).strip()

    # 청약일정 추출
    schedule_match = re.search(
        r"접수기간\s*:\s*(\d{4}\.\d{2}\.\d{2})\s*~\s*(\d{4}\.\d{2}\.\d{2})", text
    )
    if schedule_match:
        metadata["application_schedule"] = schedule_match.group(2).strip()

    # 특별공급조건 추출
    special_conditions_keywords = ["다자녀", "신혼", "생애", "노부모", "신생아", "청년"]
    for keyword in special_conditions_keywords:
        if keyword in text:
            metadata["special_supply_conditions"].append(keyword)

    return metadata


# PDF 파일 가져오기
api_pdfs = read_pdf_files(api_data_path)
crawl_pdfs = read_pdf_files(crawl_data_path)

# API PDF 메타데이터 추출
api_metadata = []
if api_pdfs:
    for pdf_path in api_pdfs:
        print(f"Reading API PDF: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)

        max_supply_price = None
        if text:
            metadata = extract_metadata_api(text, max_supply_price)
            api_metadata.append(metadata)

# Crawl PDF 메타데이터 추출
crawl_metadata = []
if crawl_pdfs:
    for pdf_path in crawl_pdfs:
        print(f"Reading Crawl PDF: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)
        if text:
            metadata = extract_metadata_crawl(text)
            crawl_metadata.append(metadata)

# DataFrame으로 변환 및 결합
api_data = pd.DataFrame(api_metadata)
crawl_data = pd.DataFrame(crawl_metadata)
combined_data = pd.concat([api_data, crawl_data], ignore_index=True)

# CSV 저장
output_path = os.path.join(current_dir, "data/combined_data.csv")
combined_data.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"Combined data saved to {output_path}")
