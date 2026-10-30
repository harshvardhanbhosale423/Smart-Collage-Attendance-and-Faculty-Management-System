@echo off
title Build Attendance System .exe
cd /d "%~dp0"
echo ================================================================
echo   Building the desktop .exe (needs internet ONE TIME, on this PC)
echo ================================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install from python.org and tick "Add Python to PATH".
    pause
    exit /b 1
)

if not exist venv python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
pip install pywebview pyinstaller

pyinstaller --noconfirm --clean --windowed --name AttendanceSystem ^
  --add-data "templates;templates" --add-data "static;static" ^
  --collect-all reportlab --hidden-import pymysql --hidden-import psycopg2 ^
  desktop_app.py

if not exist dist\AttendanceSystem\AttendanceSystem.exe (
    echo.
    echo BUILD FAILED - scroll up and read the first red error.
    pause
    exit /b 1
)

if not exist dist\AttendanceSystem\.env copy .env.example dist\AttendanceSystem\.env >nul
if not exist dist\AttendanceSystem\backups mkdir dist\AttendanceSystem\backups
if not exist dist\AttendanceSystem\database mkdir dist\AttendanceSystem\database

echo.
echo ================================================================
echo   DONE!  Your app is in:  dist\AttendanceSystem\
echo   Double-click  AttendanceSystem.exe  to run (works offline).
echo   Copy the whole "AttendanceSystem" folder to any Windows PC.
echo ================================================================
pause
