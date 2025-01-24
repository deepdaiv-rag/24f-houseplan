from typing import Optional, List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


class OpenAIResponseGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    # API호출 실패시 최대3번 시도
    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )

    # 응답 생성 메서드
    def generate_response(
        self,
        prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,  # 응답의 창의성 수준 (0.1은 매우 일관된 응답)
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        messages = []
        if system_prompt:  # 시스템 프롬프트가 있을 시 먼저 추가
            messages.append({"role": "system", "content": system_prompt})
        # 사용자 프롬프트 추가
        messages.append({"role": "user", "content": prompt})

        # 응답생성
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content  # 여러응답중 보통 첫번째껄 사용한다고함
