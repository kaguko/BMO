@echo off
title BMO - Adventure Time Companion
echo =======================================================
echo          STARTING BMO (ADVENTURE TIME OFFLINE)         
echo =======================================================
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Co loi xay ra khi chay BMO. Vui long kiem tra Python va cac thu vien pygame, pyttsx3.
    pause
)
