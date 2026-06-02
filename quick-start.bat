@echo off

echo ========================================
echo   WeChatBot - Quick Start (Test Mode)
echo ========================================
echo.

REM Check config
if not exist ".env" (
    echo [First Run] Creating config from template...
    if exist ".env.example" (
        copy .env.example .env >nul 2>&1
    ) else (
        echo [Error] .env.example not found
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Please edit .env file:
    echo   - OPENAI_BASE_URL: Your API endpoint
    echo   - OPENAI_API_KEY: Your API key
    echo   - MODEL_NAME: Model name (e.g. gpt-3.5-turbo)
    echo   - DRY_RUN: true=test, false=production
    echo.
    notepad .env
    echo.
    pause
)

REM Check mode
findstr /C:"DRY_RUN=false" .env >nul 2>&1
if not errorlevel 1 (
    echo [Production Mode] WILL send real messages!
    echo.
) else (
    echo [Test Mode] Will NOT send real messages
    echo.
    echo To enable sending, edit .env: DRY_RUN=false
    echo.
)

echo Starting WeChatBot...
echo.

python -m wechat_bot --env .env

if errorlevel 1 (
    echo.
    echo [Error] Failed to start. Check:
    echo   1. Python installed
    echo   2. Dependencies: pip install -r requirements.txt
    echo   3. .env configured correctly
    echo.
)

pause
