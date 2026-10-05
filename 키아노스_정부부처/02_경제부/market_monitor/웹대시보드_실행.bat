@echo off
cd /d "%~dp0"
title KYANOS Market Pulse (Web Dashboard)
echo ===================================================
echo   [KYANOS] Starting Web Dashboard...
echo   Browser will open automatically at:
echo   http://localhost:8899
echo ===================================================
"%USERPROFILE%\.local\bin\python3.11.exe" monitor_web.py
pause