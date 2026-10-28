@echo off
chcp 65001 >nul
cd /d "%~dp0"
"%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.16-windows-x86_64-none\python.exe" auto_daily_travel_runner.py
