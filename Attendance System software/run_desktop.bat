@echo off
cd /d "%~dp0"
if not exist venv ( echo Run install.bat first. & pause & exit /b 1 )
call venv\Scripts\activate.bat
pip install pywebview >nul 2>nul
python desktop_app.py
