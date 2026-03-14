@echo off
echo ======================================================
echo    Reddit-to-Shorts Automation - Starting App...
echo ======================================================
echo.

:: Check if venv exists
if not exist venv (
    echo [ERROR] Virtual environment not found. Please run "setup.bat" first.
    pause
    exit /b
)

:: Activate venv and run streamlit
echo [INFO] Activating environment and launching UI...
call venv\Scripts\activate
python -m streamlit run app.py

pause
