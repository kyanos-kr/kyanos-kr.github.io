@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
"%~dp0.venv\Scripts\python.exe" src\main.py >> output\..\run_log.txt 2>&1
"%~dp0.venv\Scripts\python.exe" src\git_publisher.py >> run_log.txt 2>&1
