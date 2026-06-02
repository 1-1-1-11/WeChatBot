@echo off
REM 设置代码页为 UTF-8
chcp 65001 >nul 2>&1

echo ========================================
echo   WeChatBot - Complete Startup
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found. Please install Python 3.9+
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking dependencies...
python -c "import pyweixin" >nul 2>&1
if errorlevel 1 (
    echo [Install] Installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [Error] Failed to install dependencies
        echo.
        pause
        exit /b 1
    )
    echo [Done] Dependencies installed
) else (
    echo [Skip] Dependencies already installed
)
echo.

echo [2/5] Checking configuration file...
if not exist ".env" (
    echo [Create] Creating .env from template...
    if exist ".env.example" (
        copy .env.example .env >nul 2>&1
    ) else (
        echo [Error] .env.example not found
        pause
        exit /b 1
    )
    echo [Warning] Please edit .env file to configure your API settings!
    echo.
    echo Key configuration items:
    echo   - OPENAI_BASE_URL   (API endpoint)
    echo   - OPENAI_API_KEY    (API key)
    echo   - MODEL_NAME        (Model name)
    echo.
    echo Press any key to open config file for editing...
    pause >nul
    notepad .env
    echo.
    echo After configuration, press any key to continue...
    pause >nul
) else (
    echo [Skip] Configuration file exists
)
echo.

echo [3/5] Checking WeChat UI Automation...
python -m wechat_bot.app --env .env --live-check >nul 2>&1
if errorlevel 1 (
    echo [Warning] WeChat UI Automation may not be available
    echo.
    echo Please follow these steps:
    echo   1. Press Win+Ctrl+Enter to start Narrator
    echo   2. Login to WeChat (if not logged in)
    echo   3. Wait 5 minutes
    echo   4. Press Win+Ctrl+Enter to close Narrator
    echo   5. Run this script again
    echo.
    echo See GETTING_STARTED.md for details
    echo.
    choice /C YN /M "Continue anyway (not recommended)"
    if errorlevel 2 exit /b 0
) else (
    echo [Done] WeChat UI Automation available
)
echo.

echo [4/5] Running quick test...
python -m wechat_bot.app --env .env --smoke-test
if errorlevel 1 (
    echo [Error] Smoke test failed, please check configuration
    echo.
    pause
    exit /b 1
)
echo.

echo [5/5] Confirming running mode...
echo.
echo Current configuration:
findstr /C:"DRY_RUN" .env
echo.
echo ==========================================
echo   Important Notice:
echo ==========================================
echo.
echo   DRY_RUN=true  : Test mode, no real sending
echo   DRY_RUN=false : Production mode, WILL send real messages!
echo.
echo ==========================================

findstr /C:"DRY_RUN=false" .env >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [Warning] You are about to start in PRODUCTION MODE!
    echo Real WeChat messages will be sent!
    echo.
    choice /C YN /M "Confirm starting production mode"
    if errorlevel 2 (
        echo [Cancelled] Startup cancelled
        echo.
        echo For testing, edit .env and set DRY_RUN=true
        echo.
        pause
        exit /b 0
    )
) else (
    echo.
    echo [Safe] Current test mode, will not send real messages
    echo.
    echo To enable real sending, edit .env and set DRY_RUN=false
    echo.
    pause
)

echo.
echo ========================================
echo   Starting WeChatBot...
echo ========================================
echo.
echo Console instructions:
echo   - Status bar shows: online status, mode, idle time
echo   - Pause auto reply: Check to stop auto-reply
echo   - Mode selection: Auto detect / Force online / Force offline
echo   - Tabs: Daily summary / Pending risks / Auto replies
echo.
echo To close: Click X button or press Ctrl+C
echo.
echo ========================================
echo.

python -m wechat_bot --env .env

if errorlevel 1 (
    echo.
    echo [Error] Failed to start. Please check:
    echo   1. Python environment is correct
    echo   2. Dependencies are installed
    echo   3. WeChat is logged in
    echo   4. .env configuration is valid
    echo.
)

echo.
echo Console closed.
pause
