@echo off

echo ========================================
echo   微信值班助手 - 生产模式启动
echo ========================================
echo.

REM 检查配置文件
if not exist ".env" (
    echo [错误] 未找到配置文件 .env
    echo.
    echo 请先运行"配置向导.bat"或"快速启动.bat"完成初始配置
    echo.
    pause
    exit /b 1
)

REM 自动设置为生产模式
echo [配置] 正在设置为生产模式...
echo.

REM 创建临时 PowerShell 脚本
echo (Get-Content .env) -replace 'DRY_RUN=true', 'DRY_RUN=false' ^| Set-Content .env.tmp > update.ps1
echo Move-Item -Force .env.tmp .env >> update.ps1

REM 执行更新
powershell -ExecutionPolicy Bypass -File update.ps1 2>nul
del update.ps1 2>nul

echo [完成] 已设置为生产模式
echo.

echo ==========================================
echo   警告：生产模式已启用！
echo ==========================================
echo.
echo   将会真实发送微信消息！
echo   确保你已经：
echo     - 用测试联系人充分验证过功能
echo     - 理解自动回复的触发条件
echo     - 知道如何暂停自动回复
echo.
echo ==========================================
echo.

choice /C YN /M "确认启动生产模式"
if errorlevel 2 (
    echo.
    echo [取消] 已取消启动
    echo.
    echo 如需测试模式，请运行"快速启动.bat"
    echo.
    pause
    exit /b 0
)

echo.
echo 正在启动微信值班助手（生产模式）...
echo.

python -m wechat_bot --env .env

if errorlevel 1 (
    echo.
    echo [错误] 启动失败，请检查：
    echo   1. Python 是否已安装
    echo   2. 依赖是否已安装
    echo   3. 微信是否已登录
    echo.
)

echo.
echo 控制台已关闭
pause
