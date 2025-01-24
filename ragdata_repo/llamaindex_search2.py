import pandas as pd
import openai
from llama_index.core import Document, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
import os

# OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv("API_KEY")

# CSV 파일 경로
csv_file_path = "/Users/hyottz/Desktop/24f-houseplan/daiv_houseplan/policy_saving_sentences.csv"

# 데이터 로드 및 Document 객체 생성
def load_and_prepare_documents(csv_file_path: str) -> list:
    """
    CSV 파일 로드 및 Document 객체 리스트 생성
    Args:
        csv_file_path (str): CSV 파일 경로
    Returns:
        list: Document 객체 리스트
    """
    df = pd.read_csv(csv_file_path)
    documents = [
        Document(text=row["sentence"], metadata={"doc_id": row["index"]})
        for _, row in df.iterrows()
    ]
    return documents


# Hugging Face 임베딩 모델 로드
def load_embedding_model() -> OpenAIEmbedding:
    """
    OpenAI 임베딩 모델 로드
    Returns:
        OpenAIEmbedding: 로드된 OpenAI 임베딩 모델
    """
    return OpenAIEmbedding(model="text-embedding-ada-002")


# VectorStoreIndex 생성
def create_index(documents: list) -> VectorStoreIndex:
    """
    VectorStoreIndex 생성
    Args:
        documents (list): Document 객체 리스트
    Returns:
        VectorStoreIndex: 생성된 인덱스
    """
    embed_model = load_embedding_model()
    return VectorStoreIndex.from_documents(documents, embed_model=embed_model)


# 정책 검색 함수
def search_policies(query: str) -> list:
    """
    검색 수행
    Args:
        query (str): 검색어
    Returns:
        list: 검색 결과 리스트
    """
    retriever = index.as_retriever(top_k=10)
    results = retriever.retrieve(query)

    search_results = []
    for idx, result in enumerate(results):
        doc_id = result.metadata.get("doc_id")
        matching_docs = [doc for doc in documents if doc.metadata["doc_id"] == doc_id]

        if matching_docs:
            original_text = matching_docs[0].text
            search_results.append(
                {
                    "policy_number": idx + 1,
                    "text": original_text,
                    "similarity_score": round(result.score, 3),
                }
            )
    return search_results


# 검색 결과 출력 함수
def display_results(results: list):
    """
    검색 결과 출력
    Args:
        results (list): 검색 결과 리스트
    """
    for result in results:
        print(f"*정책 {result['policy_number']}:")
        print("*검색결과")
        chunk_size = 50
        for i in range(0, len(result["text"]), chunk_size):
            print(result["text"][i : i + chunk_size])
        print(f"*유사도 점수: {result['similarity_score']}")
        print("-" * 50)


# 전역 변수 설정
documents = load_and_prepare_documents(csv_file_path)
index = create_index(documents)


# 메인 함수
if __name__ == "__main__":
    query = "전세사기관련한 정책 알려줘"
    results = search_policies(query)
    display_results(results)
