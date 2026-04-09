import os
from google import genai
from dotenv import load_dotenv

# .env 파일에서 API 키 불러오기
load_dotenv()

# 새 버전의 클라이언트 초기화 방식
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_fix(error_log: str, source_code: str) -> str:
    """에러 로그와 소스 코드를 Gemini에 보내 수정된 코드를 받아옵니다."""
    
    prompt = f"""
    당신은 최고 수준의 파이썬 버그 해결사입니다.
    아래 소스 코드에서 다음 에러가 발생했습니다.
    
    [에러 로그]
    {error_log}
    
    [현재 소스 코드]
    {source_code}
    
    에러가 발생하지 않도록 코드를 수정해 주세요.
    반드시 마크다운이나 다른 설명 없이 '순수한 파이썬 코드'만 출력해야 합니다.
    """

    # 새 라이브러리의 텍스트 생성 방식 (가장 빠르고 최신인 모델 사용)
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
    )
    
    fixed_code = response.text
    fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()
    
    return fixed_code