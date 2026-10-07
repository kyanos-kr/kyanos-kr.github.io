@echo off
cd /d "%~dp0..\.."
chcp 65001 >nul
call "%~dp0..\..\run_adsense_check.bat"
