@echo off
rem Run YouTube Shorts daily generator
set PYTHON="%USERPROFILE%\.local\bin\python3.11.exe"
%PYTHON% "%~dp0..\scripts\youtube_shorts_generator.py"
