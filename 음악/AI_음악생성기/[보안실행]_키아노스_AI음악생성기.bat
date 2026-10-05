@echo off
chcp 65001 > nul
title [K-SEF 보안실행] 키아노스 국립음악창작원 AI 음원 생성기
color 0b

echo ====================================================================
echo  [키아노스 국립음악창작원] AI 음악 생성 시스템
echo  관할: 키아노스 국제질서유지 보안사령부 (K-SEF) 퀀텀 아이기스 방위단
echo  보안 등급: 최고 등급 격리 실행 (VRAM 안전 캡 60%% 강제 적용)
echo ====================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [오류] 전용 가상환경을 찾을 수 없습니다: %VENV_PYTHON%
    pause
    exit /b 1
)

echo [시스템 확인] 보안 가상환경 격리 확인 완료.
echo [시스템 가동] 키아노스 음악 엔진(kyanos_music_engine.py)을 구동합니다...
echo.

"%VENV_PYTHON%" "%SCRIPT_DIR%kyanos_music_engine.py"

echo.
echo ====================================================================
echo  작업이 완료되었습니다. 창을 닫으려면 아무 키나 누르십시오.
echo ====================================================================
pause > nul
