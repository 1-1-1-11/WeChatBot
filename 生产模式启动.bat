@echo off
REM 设置代码页为 UTF-8
chcp 65001 >nul 2>&1

echo ========================================
echo   WeChatBot - Production Mode
echo ========================================
echo.

REM 检查配置文件
if not exist ".env" (
    echo [Error] Configuration file .env not found
    echo.
    echo Please run start.bat or quick-start.bat first
    echo to complete initial setup.
    echo.
    pause
    exit /b 1
)

REM 自动设置为生产模式
echo [Config] Setting to production mode...
echo.

REM 创建临时 PowerShell 脚本
echo (Get-Content .env) -replace 'DRY_RUN=true', 'DRY_RUN=false' ^| Set-Content .env.tmp > update.ps1
echo Move-Item -Force .env.tmp .env >> update.ps1

REM 执行更新
powershell -ExecutionPolicy Bypass -File update.ps1 2>nul
del update.ps1 2>nul

echo [Done] Production mode enabled
echo.

echo ==========================================
echo   WARNING: Production Mode Active!
echo ==========================================
echo.
echo   Real WeChat messages WILL be sent!
echo   Make sure you have:
echo     - Tested thoroughly with test contacts
echo     - Understood the auto-reply conditions
echo     - Know how to pause auto-reply
echo.
echo ==========================================
echo.

choice /C YN /M "Confirm starting in production mode"
if errorlevel 2 (
    echo.
    echo [Cancelled] Startup cancelled
    echo.
    echo For test mode, run quick-start.bat instead
    echo.
    pause
    exit /b 0
)

echo.
echo Starting WeChatBot (Production Mode)...
echo.

python -m wechat_bot --env .env

if errorlevel 1 (
    echo.
    echo [Error] Failed to start. Please check:
    echo   1. Python is installed
    echo   2. Dependencies are installed
    echo   3. WeChat is logged in
    echo.
)

echo.
echo Console closed.
pause
