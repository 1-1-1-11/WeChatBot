@echo off

echo ========================================
echo   WeChatBot - Full Startup with Checks
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found. Install Python 3.9+
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

echo [2/5] Checking config...
if not exist ".env" (
    echo [Create] Creating .env from template...
    if exist ".env.example" (
        copy .env.example .env >nul 2>&1
    ) else (
        echo [Error] .env.example not found
        pause
        exit /b 1
    )
    echo [Warning] Please edit .env file!
    echo.
    echo Key settings:
    echo   - OPENAI_BASE_URL   (API endpoint)
    echo   - OPENAI_API_KEY    (API key)
    echo   - MODEL_NAME        (Model name)
    echo.
    echo Press any key to open editor...
    pause >nul
    notepad .env
    echo.
    echo After editing, press any key...
    pause >nul
) else (
    echo [Skip] Config exists
)
echo.

echo [3/5] Checking WeChat UI Automation...
python -m wechat_bot.app --env .env --live-check >nul 2>&1
if errorlevel 1 (
    echo [Warning] WeChat UI Automation may be unavailable
    echo.
    echo Steps:
    echo   1. Press Win+Ctrl+Enter to start Narrator
    echo   2. Login WeChat (if not logged in)
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

echo [4/5] Running test...
python -m wechat_bot.app --env .env --smoke-test
if errorlevel 1 (
    echo [Error] Test failed, check config
    echo.
    pause
    exit /b 1
)
echo.

echo [5/5] Confirming mode...
echo.
echo Current config:
findstr /C:"DRY_RUN" .env
echo.
echo ==========================================
echo   Important:
echo ==========================================
echo.
echo   DRY_RUN=true  : Test mode, no sending
echo   DRY_RUN=false : Production, WILL send!
echo.
echo ==========================================

findstr /C:"DRY_RUN=false" .env >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [Warning] Starting in PRODUCTION MODE!
    echo Real messages will be sent!
    echo.
    choice /C YN /M "Confirm production mode"
    if errorlevel 2 (
        echo [Cancelled] Startup cancelled
        echo.
        echo For test, edit .env: DRY_RUN=true
        echo.
        pause
        exit /b 0
    )
) else (
    echo.
    echo [Safe] Test mode, will not send
    echo.
    echo To send, edit .env: DRY_RUN=false
    echo.
    pause
)

echo.
echo ========================================
echo   Starting WeChatBot...
echo ========================================
echo.
echo Console info:
echo   - Status bar: online status, mode, idle time
echo   - Pause auto reply: Check to stop
echo   - Mode: Auto detect / Force online / Force offline
echo   - Tabs: Daily summary / Pending risks / Auto replies
echo.
echo To close: Click X or press Ctrl+C
echo.
echo ========================================
echo.

python -m wechat_bot --env .env

if errorlevel 1 (
    echo.
    echo [Error] Failed to start. Check:
    echo   1. Python environment
    echo   2. Dependencies installed
    echo   3. WeChat logged in
    echo   4. .env valid
    echo.
)

echo.
echo Console closed
pause
