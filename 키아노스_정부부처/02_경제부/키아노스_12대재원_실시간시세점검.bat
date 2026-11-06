@echo off
chcp 65001 >nul
title 키아노스 경제부 12대 전략 재원 실시간 시세 점검
cd /d "%~dp0키아노스_정부부처\02_경제부"
node check_stocks.js
echo.
pause
