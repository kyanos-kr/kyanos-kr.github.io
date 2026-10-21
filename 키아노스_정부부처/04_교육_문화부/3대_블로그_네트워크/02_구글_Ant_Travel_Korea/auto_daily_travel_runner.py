import os
import sys
import glob
import json
import re
import datetime
import subprocess
import shutil

# 경로 설정
BASE_DIR = r"d:\안티그래비티파이튼"
TRAVEL_DIR = os.path.join(BASE_DIR, r"키아노스_정부부처\04_교육_문화부\3대_블로그_네트워크\02_구글_Ant_Travel_Korea")
TOOLS_DIR = os.path.join(BASE_DIR, r"키아노스_정부부처\04_교육_문화부\3대_블로그_네트워크\tools")
UPLOAD_SCRIPT = os.path.join(TOOLS_DIR, "blogger_upload.ps1")
STATE_FILE = os.path.join(TRAVEL_DIR, "travel_upload_state.yaml")
SRC_ROOT = r"E:\편집 기사\오늘편집\국내"
WEB_IMG_ROOT = os.path.join(BASE_DIR, r"assets\images\travel")
PIPELINE_MD = os.path.join(TRAVEL_DIR, "DAILY_TRAVEL_AUTO_PIPELINE.md")

today_str = datetime.date.today().isoformat()

def log(msg):
    t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{t} {msg}"
    print(line)
    with open(os.path.join(TRAVEL_DIR, "auto_upload.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")

def check_already_uploaded_today():
    if not os.path.exists(STATE_FILE):
        return False
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    if f"last_uploaded_date: {today_str}" in content:
        return True
    return False

def record_upload(spot_name, post_id=""):
    log_entry = f"""
  - date: {today_str}
    spot: {spot_name}
    post_id: "{post_id}"
"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.startswith("last_uploaded_date:"):
                new_lines.append(f"last_uploaded_date: {today_str}\n")
            elif line.startswith("last_uploaded_spot:"):
                new_lines.append(f"last_uploaded_spot: {spot_name}\n")
            else:
                new_lines.append(line)
        new_lines.append(log_entry)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    else:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(f"last_uploaded_date: {today_str}\nlast_uploaded_spot: {spot_name}\ndaily_quota: 1\nhistory:{log_entry}")

def run_daily_upload():
    log("=== Ant-Travel Korea 일일 자동 1편 업로드 점검 시작 ===")
    
    # 1. 일일 1편 쿼터 확인 (하루 2편 방지)
    if check_already_uploaded_today():
        log(f"오늘({today_str}) 이미 여행기 1편이 발행되었습니다. 규칙에 따라 추가 업로드를 중단하고 내일로 대기합니다.")
        return

    # 2. 오늘 날짜로 이미 작성된 HTML 파일이 있는지 확인
    today_files = glob.glob(os.path.join(TRAVEL_DIR, f"{today_str}_Travel_*.html"))
    if today_files:
        target_html = today_files[0]
        spot_name = os.path.basename(target_html)
        log(f"오늘자 기작성 원고 발견: {spot_name} -> Blogger 업로드 실행")
        cmd = f'powershell -ExecutionPolicy Bypass -File "{UPLOAD_SCRIPT}" -File "{target_html}" -Blog travel -Publish'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        log(f"Blogger 업로드 결과:\n{res.stdout}")
        
        post_id_match = re.search(r"글 ID\s*:\s*(\d+)", res.stdout)
        post_id = post_id_match.group(1) if post_id_match else ""
        record_upload(spot_name, post_id)
        return

    log("오늘자 신규 원고 작성이 필요한 상태입니다. 큐에서 미발행 여행지를 선별합니다.")
    # 향후 미작성 시 파이프라인에서 다음 순번 여행지를 자동 빌드하여 업로드하는 로직 연결
    log("=== 점검 완료 ===")

if __name__ == "__main__":
    run_daily_upload()
