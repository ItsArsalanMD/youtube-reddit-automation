@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo    Reddit-to-Shorts Automation - Easy Installer
echo ======================================================
echo.

:: 1. Check for Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed. Please install Git and try again.
    pause
    exit /b
)

:: 2. Clone Repository
set REPO_URL=https://github.com/ItsArsalanMD/youtube-reddit-automation.git
echo [STEP 1] Cloning repository...
git clone -b v2 %REPO_URL% youtube-automation
cd youtube-automation

:: 3. Create Virtual Environment
echo [STEP 2] Creating Python Virtual Environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment. Ensure Python is installed.
    pause
    exit /b
)

:: 4. Install Dependencies
echo [STEP 3] Installing dependencies (this may take a few minutes)...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b
)

:: 5. Create Folders
echo [STEP 4] Creating necessary folders...
if not exist assets mkdir assets
if not exist data\audio mkdir data\audio
if not exist data\captions mkdir data\captions
if not exist data\videos mkdir data\videos
if not exist data\scripts mkdir data\scripts
if not exist data\overlays mkdir data\overlays

:: 6. Setup .env
echo [STEP 5] Configuring environment variables...
if exist .env (
    echo .env already exists. Skipping...
) else (
    set /p API_KEY="Enter your GEMINI_API_KEY: "
    set /p SUB_USER="Enter your REDDIT_USERNAME (Optional): "
    
    echo # Created by setup.bat > .env
    echo GEMINI_API_KEY=!API_KEY! >> .env
    echo REDDIT_USERNAME=!SUB_USER! >> .env
    echo YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json >> .env
    echo FFMPEG_PATH= >> .env
    echo.
    echo [IMPORTANT] If FFmpeg is not in your PATH, please add its folder to FFMPEG_PATH in .env manually.
)

echo.
echo ======================================================
echo    INSTALLATION COMPLETE!
echo ======================================================
echo.
echo To start the app, run the "run_app.bat" script.
echo.
pause
