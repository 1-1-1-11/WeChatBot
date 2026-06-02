@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   WeChatBot Setup Wizard
echo ========================================
echo.

REM Check existing config
if exist ".env" (
    echo Existing .env config detected
    echo.
    choice /C YN /M "Reconfigure (overwrite existing)"
    if errorlevel 2 (
        echo.
        echo Opening editor...
        notepad .env
        pause
        exit /b 0
    )
    echo.
)

echo [1/8] Creating config file...
if exist ".env.example" (
    copy .env.example .env >nul 2>&1
) else (
    echo [Error] .env.example template not found
    pause
    exit /b 1
)
echo [Done] Config file created
echo.

echo ========================================
echo   Setup Wizard Started
echo ========================================
echo.

REM API Base URL
echo [2/8] OpenAI Compatible API Config
echo.
set /p "api_url=API URL (e.g. https://api.openai.com): "
if "!api_url!"=="" set "api_url=https://api.openai.com"

REM API Key
echo.
set /p "api_key=API Key (e.g. sk-xxx): "
if "!api_key!"=="" (
    echo [Warning] API key empty, need manual config
    set "api_key=sk-your-api-key-here"
)

REM Model
echo.
echo Models:
echo   1. gpt-3.5-turbo (Recommended, cheap)
echo   2. gpt-4
echo   3. gpt-4-turbo
echo   4. Custom
echo.
set /p "model_choice=Select model (1-4): "

if "!model_choice!"=="1" set "model_name=gpt-3.5-turbo"
if "!model_choice!"=="2" set "model_name=gpt-4"
if "!model_choice!"=="3" set "model_name=gpt-4-turbo"
if "!model_choice!"=="4" (
    set /p "model_name=Custom model name: "
)
if "!model_name!"=="" set "model_name=gpt-3.5-turbo"

REM Idle time
echo.
echo [3/8] Online Detection Config
echo.
set /p "idle_min=Idle minutes for offline (default 10): "
if "!idle_min!"=="" set "idle_min=10"

REM Delay
echo.
echo [4/8] Auto Reply Delay Config
echo.
set /p "delay_min=Min delay seconds (default 20): "
if "!delay_min!"=="" set "delay_min=20"

set /p "delay_max=Max delay seconds (default 60): "
if "!delay_max!"=="" set "delay_max=60"

REM Cooldown
echo.
echo [5/8] Contact Cooldown
echo.
set /p "cooldown=Reply interval minutes (default 10): "
if "!cooldown!"=="" set "cooldown=10"

REM Data dir
echo.
echo [6/8] Data Directory
echo.
set /p "data_dir=Data directory (default data): "
if "!data_dir!"=="" set "data_dir=data"

REM Mode
echo.
echo [7/8] Running Mode
echo.
echo Important:
echo   - Test mode (DRY_RUN=true): Log only, no sending
echo   - Production (DRY_RUN=false): WILL send real messages
echo.
choice /C 12 /M "1=Test  2=Production"

if errorlevel 2 (
    set "dry_run=false"
    echo [Warning] Production mode selected!
) else (
    set "dry_run=true"
    echo [Safe] Test mode selected
)

REM Write config
echo.
echo [8/8] Saving config...

(
echo # OpenAI Compatible API Config
echo OPENAI_BASE_URL=!api_url!
echo OPENAI_API_KEY=!api_key!
echo MODEL_NAME=!model_name!
echo.
echo # Online Detection Config
echo IDLE_MINUTES=!idle_min!
echo.
echo # Auto Reply Delay Config
echo AUTO_REPLY_DELAY_MIN_SECONDS=!delay_min!
echo AUTO_REPLY_DELAY_MAX_SECONDS=!delay_max!
echo.
echo # Contact Cooldown
echo CONTACT_COOLDOWN_MINUTES=!cooldown!
echo.
echo # Data Directory
echo DATA_DIR=!data_dir!
echo.
echo # Running Mode
echo DRY_RUN=!dry_run!
) > .env

echo [Done] Config saved to .env
echo.

echo ========================================
echo   Config Summary
echo ========================================
echo.
echo API URL: !api_url!
echo Model: !model_name!
echo Idle: !idle_min! minutes
echo Delay: !delay_min!-!delay_max! seconds
echo Cooldown: !cooldown! minutes
echo Mode: DRY_RUN=!dry_run!
echo.

if "!api_key!"=="sk-your-api-key-here" (
    echo [Warning] API key not configured yet!
    echo.
    choice /C YN /M "Edit config now"
    if not errorlevel 2 notepad .env
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next:
if "!dry_run!"=="true" (
    echo   1. Run quick-start.bat to test
) else (
    echo   1. Run production-start.bat
)
echo   2. Read GETTING_STARTED.md for details
echo.

pause
