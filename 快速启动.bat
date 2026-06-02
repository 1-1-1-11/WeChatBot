@echo off
chcp 65001 >nul

echo ========================================
echo   微信值班助手 - 快速启动
echo ========================================
echo.

REM 检查配置文件
if not exist ".env" (
    echo [首次运行] 正在创建配置文件...
    copy .env.example .env >nul
    echo.
    echo 请编辑 .env 文件，配置你的 API 信息：
    echo.
    notepad .env
    echo.
    echo 配置说明：
    echo   - OPENAI_BASE_URL: 你的 API 地址
    echo   - OPENAI_API_KEY: 你的 API 密钥
    echo   - MODEL_NAME: 模型名称
    echo   - DRY_RUN: true=测试模式，false=生产模式
    echo.
    pause
)

REM 检查是否为生产模式
findstr /C:"DRY_RUN=false" .env >nul
if not errorlevel 1 (
    echo [生产模式] 将真实发送微信消息！
    echo.
) else (
    echo [测试模式] 不会真实发送消息
    echo.
    echo 如需真实发送，编辑 .env 设置: DRY_RUN=false
    echo.
)

echo 正在启动...
echo.

python -m wechat_bot --env .env

pause
