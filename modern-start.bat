@echo off
echo ========================================
echo   Modern WeChat Bot Dashboard
echo ========================================
echo.
echo Starting modern UI...
echo (Use --classic-ui flag for old interface)
echo.

python -m wechat_bot --env .env

if errorlevel 1 (
    echo.
    echo [Error] Failed to start
    pause
)
