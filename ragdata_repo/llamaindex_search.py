import pandas as pd
from llama_index.core import Document, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex

import os
import pandas as pd

# 현재 디렉토리 가져오기
current_dir = os.getcwd()
print("Current Directory:", current_dir)

# 파일 경로 구성
csv_file_path = os.path.join(current_dir, "data", "policy_saving_sentences.csv")

# 파일 경로 확인
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"파일을 찾을 수 없습니다: {csv_file_path}")

# 데이터 읽기
df = pd.read_csv(csv_file_path)

# Document 객체 생성
documents = []
for _, row in df.iterrows():
    sentence = row["sentence"]
    index = row["index"]
    doc = Document(text=sentence, metadata={"doc_id": index})  # 청크 텍스트  # 원본 문서 전체 포함
    documents.append(doc)

# Hugging Face 임베딩 모델 로드
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-mpnet-base-v2"
)  # "sentence-transformers/all-mpnet-base-v2" #sentence-transformers/all-MiniLM-L6-v2", #"dunzhang/stella_en_1.5B_v5"

# VectorStoreIndex 생성
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)


def search_policies(query: str):
    # 리트리버 생성
    retriever = index.as_retriever(verbose=True, top_k=5)

    # 검색 수행
    results = retriever.retrieve(query)

    search_results = []
    for idx, result in enumerate(results):
        doc_id = result.metadata.get("doc_id")
        matching_docs = [
            doc for doc in documents if doc.metadata.get("doc_id") == doc_id
        ]

        if not matching_docs:
            continue

        original_text = matching_docs[0].text
        search_results.append(
            {
                "policy_number": idx + 1,
                "text": original_text,
                "similarity_score": round(result.score, 3),
            }
        )

    return search_results


# 함수 사용 예시
if __name__ == "__main__":
    query = "전세를 알아보려고 하는데 전세 사기가 걱정돼요"
    results = search_policies(query)

    for result in results:
        print(f"*정책 {result['policy_number']}:")
        print("*검색결과")
        chunk_size = 50
        for i in range(0, len(result["text"]), chunk_size):
            print(result["text"][i : i + chunk_size])
        print(f"*유사도 점수: {result['similarity_score']}")
        print("-" * 50)
