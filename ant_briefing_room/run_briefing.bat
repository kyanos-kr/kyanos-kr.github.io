@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
cd /d "%~dp0"
echo ====================================================== >> briefing_log.txt
echo [%date% %time%] AntNews Briefing Room Auto-Update Start >> briefing_log.txt
echo ====================================================== >> briefing_log.txt
"%~dp0..\antnews_auto\.venv\Scripts\python.exe" collector.py >> briefing_log.txt 2>&1
"%~dp0..\antnews_auto\.venv\Scripts\python.exe" git_publisher.py >> briefing_log.txt 2>&1
echo [%date% %time%] AntNews Briefing Room Update Completed (Code: %ERRORLEVEL%) >> briefing_log.txt
