from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback
import os
from agent import generate_fix

app = FastAPI()

# 일부러 에러를 발생시키는 엔드포인트
@app.get("/calculate")
async def calculate():
    result = 10 / 0  # 이 부분을 AI가 고치게 됩니다.
    return {"result": result}

# 에러 가로채기 (ExceptionHandler)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🚨 시스템 에러 감지! 자가 치유 프로세스 시작...")
    
    error_log = traceback.format_exc()
    current_file_path = os.path.abspath(__file__)
    
    with open(current_file_path, "r", encoding="utf-8") as f:
        source_code = f.read()
        
    print("🧠 AI가 원인을 분석하고 코드를 수정 중입니다...")
    fixed_code = generate_fix(error_log, source_code)
    
    # 수정된 코드 덮어쓰기 (--fix Action!)
    with open(current_file_path, "w", encoding="utf-8") as f:
        f.write(fixed_code)
        
    print("✨ 코드 수정 완료! 서버가 자동으로 재시작됩니다.")
    
    return JSONResponse(
        status_code=500,
        content={"message": "서버에 문제가 발생하여 스스로 코드를 수정했습니다. 잠시 후 다시 시도해주세요."}
    )