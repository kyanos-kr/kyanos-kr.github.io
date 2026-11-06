@echo off
cd /d "%~dp0"
title KYANOS Market Pulse (Console)
echo ===================================================
echo   [KYANOS] Starting Console Monitor...
echo ===================================================
"%USERPROFILE%\.local\bin\python3.11.exe" monitor_console.py
pause