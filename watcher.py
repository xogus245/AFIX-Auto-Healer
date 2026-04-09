import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from agent import generate_fix

# 🛡️ 절대 건드리면 안 되는 시스템 코어 파일들 (블랙리스트)
EXCLUDE_FILES = ["watcher.py", "agent.py", "main.py"]

class AutoFixHandler(FileSystemEventHandler):
    def __init__(self):
        # 파일별로 마지막 저장 시간을 따로 관리합니다 (여러 파일 동시 작업 대비)
        self.last_modified = {}

    def on_modified(self, event):
        file_path = event.src_path
        file_name = os.path.basename(file_path)

        # 1. 파이썬(.py) 파일이 아니거나, 블랙리스트에 있는 파일이면 감시하지 않음
        if not file_path.endswith(".py") or file_name in EXCLUDE_FILES:
            return
            
        # 2. 파일별 중복 감지 방지 (1초 이내의 연속 저장은 무시)
        current_time = time.time()
        if current_time - self.last_modified.get(file_path, 0) < 1.0:
            return
        self.last_modified[file_path] = current_time
        
        print(f"\n[👀 Watchdog] 💾 '{file_name}' 저장 감지! 코드를 테스트합니다...")

        # 3. 방금 저장된 그 파일을 가상으로 실행해 봅니다.
        result = subprocess.run(
            ["python", file_path], 
            capture_output=True, 
            text=True,
            encoding="utf-8",
            errors="ignore" 
        )

        # 4. 에러가 났을 때만 제미나이 호출
        if result.returncode != 0:
            error_log = result.stderr
            print(f"[🚨 Watchdog] '{file_name}'에서 에러 발생!\n{error_log.strip()}")
            print("[🧠 Watchdog] AI 요원에게 수리를 요청합니다...")
            
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            # AI에게 해당 파일의 코드와 에러 로그를 보냄
            fixed_code = generate_fix(error_log, source_code)

            # 수정된 코드로 원본 파일 덮어쓰기
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            
            print(f"[✨ Watchdog] 조치 완료! '{file_name}' 파일이 자동으로 수정되었습니다.")
        else:
            print(f"[✅ Watchdog] '{file_name}' 에러 없음. 코드가 완벽하게 실행됩니다!")

if __name__ == "__main__":
    path = "." # 현재 폴더 전체를 감시
    event_handler = AutoFixHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    print(f"==================================================")
    print(f" 🛡️ AFIX Omni-Watchdog 실행 중... ")
    print(f" 📂 현재 폴더의 [모든 파이썬 파일]을 감시합니다.")
    print(f" ⚠️ 단, 시스템 코어({', '.join(EXCLUDE_FILES)})는 제외됩니다.")
    print(f"==================================================")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()