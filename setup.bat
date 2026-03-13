@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo    Reddit-to-Shorts Automation - Easy Installer
echo ======================================================
echo.

:: 1. Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 goto :NO_PYTHON

:: 2. Check for Git
where git >nul 2>&1
if %errorlevel% neq 0 goto :NO_GIT

:: 3. Check for FFmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 goto :FFMPEG_WARNING
goto :CHECK_FILES

:NO_PYTHON
echo [ERROR] Python is NOT installed or not in your PATH.
echo.
echo To fix this:
echo 1. Download Python from: https://www.python.org/downloads/
echo 2. Run the installer.
echo 3. IMPORTANT: Check the box "Add Python to PATH" before clicking Install.
echo 4. Restart your computer and run this script again.
echo.
pause
exit /b

:NO_GIT
echo [ERROR] Git is NOT installed.
echo.
echo To fix this:
echo 1. Download Git from: https://git-scm.com/downloads
echo 2. Run the installer (you can keep the default settings).
echo 3. Restart your computer and run this script again.
echo.
pause
exit /b

:FFMPEG_WARNING
echo [WARNING] FFmpeg was NOT found. This is required for video editing.
echo.
echo How to install FFmpeg:
echo 1. Visit: https://www.gyan.dev/ffmpeg/builds/
echo 2. Download "ffmpeg-git-full.7z" (or similar zip).
echo 3. Extract it to a folder ^(e.g., C:\ffmpeg^).
echo 4. You will need to put this path in the .env file later.
echo.
set /p CONTINUE="Do you want to continue with setup? (Y/N): "
if /i "!CONTINUE!" neq "Y" exit /b
goto :CHECK_FILES

:CHECK_FILES
:: 4. Clone Repository (Optional - if not already in a repo)
if exist "requirements.txt" goto :VENV_START
echo [STEP 1] Downloading repository...
set REPO_URL=https://github.com/ItsArsalanMD/youtube-reddit-automation.git
git clone -b v2 %REPO_URL% youtube-automation
cd youtube-automation

:VENV_START
:: 5. Create Virtual Environment
echo [STEP 2] Preparing Python Environment...
python -m venv venv
if %errorlevel% neq 0 goto :VENV_ERROR

:: 6. Install Dependencies
echo [STEP 3] Installing tools (may take a few minutes)...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 goto :pip_ERROR
goto :FOLDERS

:VENV_ERROR
echo [ERROR] Failed to create environment.
pause
exit /b

:pip_ERROR
echo [ERROR] Tool installation failed.
pause
exit /b

:FOLDERS
:: 7. Create Folders
echo [STEP 4] Creating project folders...
if not exist assets mkdir assets
if not exist data\audio mkdir data\audio
if not exist data\captions mkdir data\captions
if not exist data\videos mkdir data\videos
if not exist data\scripts mkdir data\scripts
if not exist data\overlays mkdir data\overlays

:: 8. Setup .env
echo [STEP 5] Configuring your settings...
if exist .env goto :FINISH

echo.
echo ------------------------------------------------------
echo    GEMINI API KEY SETUP
echo ------------------------------------------------------
echo 1. Go to: https://aistudio.google.com/app/apikey
echo 2. Click "Create API key in new project".
echo 3. Copy the key and paste it below.
echo.
set /p API_KEY="Paste your Gemini API Key: "

echo # Created by setup.bat > .env
echo GEMINI_API_KEY=!API_KEY! >> .env
echo REDDIT_USERNAME= >> .env
echo YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json >> .env

where ffmpeg >nul 2>&1
if %errorlevel% eq 0 (
    echo FFMPEG_PATH=ffmpeg >> .env
) else (
    echo.
    echo Please enter the full path to ffmpeg.exe ^(e.g., C:\ffmpeg\bin\ffmpeg.exe^)
    echo Leave empty if you will add it manually later.
    set /p FF_PATH="FFmpeg Path: "
    echo FFMPEG_PATH=!FF_PATH! >> .env
)
echo.
echo [SUCCESS] .env file created.

:FINISH
echo.
echo ======================================================
echo    INSTALLATION FINISHED!
echo ======================================================
echo.
echo To start the app, run the "run_app.bat" script.
echo.
pause
