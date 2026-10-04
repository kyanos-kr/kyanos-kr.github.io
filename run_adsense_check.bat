@echo off
chcp 65001 >nul
title [AntNews] 구글 애드센스 실시간 건전성 진단기 (파이튼 & 앤트)

echo ======================================================================
echo  [AntNews] 애드센스 인프라 실시간 진단을 시작합니다...
echo  통치자: 파이튼 님 ^| 보좌: 앤트
echo ======================================================================
echo.

set PYTHON_PATH=%USERPROFILE%\.local\bin\python3.11.exe

if not exist "%PYTHON_PATH%" (
    echo [경고] 파이썬 3.11 실행기를 찾을 수 없어 시스템 기본 python을 시도합니다.
    set PYTHON_PATH=python
)

"%PYTHON_PATH%" "%~dp0scripts\check_adsense_health.py"

echo.
echo ----------------------------------------------------------------------
echo [1] Microsoft Edge 브라우저로 antnews.org 열기 (광고 송출 확인)
echo [2] 진단 종료
echo ----------------------------------------------------------------------
set /p user_choice="선택하세요 (1 또는 2, 기본값 2): "

if "%user_choice%"=="1" (
    echo Microsoft Edge로 antnews.org를 실행합니다...
    start msedge "https://www.antnews.org"
)

echo.
echo 진단이 완료되었습니다. 창을 닫으려면 아무 키나 누르세요.
pause >nul
