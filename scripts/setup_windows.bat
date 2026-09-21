@echo off
REM AI Meeting ASR Agent - Windows setup
setlocal
cd /d "%~dp0\.."

echo [1/3] Creating virtual environment...
python -m venv .venv
if errorlevel 1 goto :error

echo [2/3] Activating and installing dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [3/3] Done.
echo.
echo NOTE: FunASR models download on first transcription run (cached under %%USERPROFILE%%\.cache\modelscope).
echo For mp3/m4a transcription, install ffmpeg:  winget install Gyan.FFmpeg
exit /b 0

:error
echo Setup failed. See messages above.
exit /b 1
