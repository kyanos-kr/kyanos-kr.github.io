@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
cd /d "%~dp0"
echo ====================================================== >> run_log.txt
echo [%date% %time%] AntNews 자동 실행 시작 >> run_log.txt
echo ====================================================== >> run_log.txt
"%~dp0.venv\Scripts\python.exe" src\main.py >> run_log.txt 2>&1
echo [%date% %time%] AntNews 자동 실행 종료 (코드: %ERRORLEVEL%) >> run_log.txt
