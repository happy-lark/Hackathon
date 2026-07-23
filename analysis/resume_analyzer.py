"""
analysis/resume_analyzer.py

사용자가 입력한 이력서 내용 또는 지원 직무 정보를 바탕으로,
그 맥락에 맞는 사진/배경/의상 스타일 추천을 생성합니다.
선택적 기능이므로, 실패하거나 입력이 없으면 조용히 생략됩니다.

.env에서 API 키를 읽어옵니다 (text_analyzer.py와 동일한 방식).
"""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SCHOOL_API_KEY")
BASE_URL = os.getenv("SCHOOL_BASE_URL")

client = Anthropic(api_key=API_KEY, base_url=BASE_URL)
MODEL = "claude-sonnet-4-6"

RESUME_SYSTEM_PROMPT = """당신은 채용 이미지 컨설턴트입니다.
사람의 능력이나 자격을 판단하지 마세요. 오직 "이 직무/업계에서 일반적으로
선호되는 시각적 스타일"에 대한 참고 의견만 제공하세요.

아래 JSON 형식으로만 답하세요. 다른 설명 없이 순수 JSON만 출력하세요.
각 필드는 반드시 한 문장, 50자 이내로 짧게 작성하세요.

{
  "industry_tone": "짧은 한 문장",
  "background_advice": "짧은 한 문장",
  "clothing_advice": "짧은 한 문장",
  "keyword_tip": "짧은 한 문장"
}
"""


def analyze_resume_context(resume_or_job_text: str) -> dict:
    """
    resume_or_job_text: 사용자가 입력한 이력서 내용 또는 지원 직무 설명

    반환값 (성공 시):
    {
        "success": True,
        "industry_tone": "...",
        "background_advice": "...",
        "clothing_advice": "...",
        "keyword_tip": "...",
    }
    실패 시: {"success": False, "message": "..."}
    """
    if not resume_or_job_text or not resume_or_job_text.strip():
        return {"success": False, "message": "입력된 이력서/직무 정보가 없습니다."}

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=RESUME_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"다음 이력서/지원 직무 정보를 참고해서 JSON으로 답해주세요:\n\n{resume_or_job_text}",
                }
            ],
        )

        raw_text = response.content[0].text.strip()
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned)
        parsed["success"] = True
        return parsed

    except Exception as error:
        # 실패해도 메인 파이프라인은 안 끊기도록 조용히 실패 처리
        return {
            "success": False,
            "message": "이력서 맞춤 분석에 실패했습니다. 기본 결과만 표시됩니다.",
            "error": str(error),
        }