@echo off
REM 设置代码页为 UTF-8
chcp 65001 >nul 2>&1

echo ========================================
echo   WeChatBot - Quick Start
echo ========================================
echo.

REM 检查配置文件
if not exist ".env" (
    echo [First Run] Creating configuration file...
    if exist ".env.example" (
        copy .env.example .env >nul 2>&1
    ) else (
        echo [Error] .env.example not found
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Please edit .env file to configure your API settings:
    echo.
    notepad .env
    echo.
    echo Configuration guide:
    echo   - OPENAI_BASE_URL: Your API endpoint
    echo   - OPENAI_API_KEY: Your API key
    echo   - MODEL_NAME: Model name
    echo   - DRY_RUN: true=test mode, false=production mode
    echo.
    pause
)

REM 检查运行模式
findstr /C:"DRY_RUN=false" .env >nul 2>&1
if not errorlevel 1 (
    echo [Production Mode] Will send real WeChat messages!
    echo.
) else (
    echo [Test Mode] Will NOT send real messages
    echo.
    echo To enable real sending, edit .env and set: DRY_RUN=false
    echo.
)

echo Starting WeChatBot...
echo.

python -m wechat_bot --env .env

if errorlevel 1 (
    echo.
    echo [Error] Failed to start. Please check:
    echo   1. Python is installed
    echo   2. Dependencies are installed: pip install -r requirements.txt
    echo   3. .env file is configured correctly
    echo.
)

pause
