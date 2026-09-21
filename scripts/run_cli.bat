@echo off
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat
python cli\meeting_cli.py %*
