@echo off

echo ========================================
echo   WeChatBot - Production Mode
echo ========================================
echo.

REM Check config
if not exist ".env" (
    echo [Error] .env not found
    echo.
    echo Please run setup-wizard.bat or quick-start.bat first
    echo.
    pause
    exit /b 1
)

REM Set production mode
echo [Config] Setting production mode...
echo.

REM Create temp PowerShell script
echo (Get-Content .env) -replace 'DRY_RUN=true', 'DRY_RUN=false' ^| Set-Content .env.tmp > update.ps1
echo Move-Item -Force .env.tmp .env >> update.ps1

REM Execute
powershell -ExecutionPolicy Bypass -File update.ps1 2>nul
del update.ps1 2>nul

echo [Done] Production mode enabled
echo.

echo ==========================================
echo   WARNING: Production Mode Active!
echo ==========================================
echo.
echo   WILL send real WeChat messages!
echo   Make sure:
echo     - Tested with test contacts
echo     - Understand auto-reply conditions
echo     - Know how to pause auto-reply
echo.
echo ==========================================
echo.

choice /C YN /M "Confirm starting production mode"
if errorlevel 2 (
    echo.
    echo [Cancelled] Startup cancelled
    echo.
    echo For test mode, run quick-start.bat
    echo.
    pause
    exit /b 0
)

echo.
echo Starting WeChatBot (Production)...
echo.

python -m wechat_bot --env .env

if errorlevel 1 (
    echo.
    echo [Error] Failed to start. Check:
    echo   1. Python installed
    echo   2. Dependencies installed
    echo   3. WeChat logged in
    echo.
)

echo.
echo Console closed
pause
