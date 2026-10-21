@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
cd /d "%~dp0"

echo ====================================================== >> auto_upload.log
echo [%date% %time%] Ant-Travel Korea 자동 1편 실행 시작 >> auto_upload.log
echo ====================================================== >> auto_upload.log

"C:\Users\태봉\.local\bin\python3.11.exe" auto_daily_travel_runner.py >> auto_upload.log 2>&1

echo [%date% %time%] Ant-Travel Korea 자동 실행 종료 (코드: %ERRORLEVEL%) >> auto_upload.log
