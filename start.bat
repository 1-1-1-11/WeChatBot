@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   微信值班助手 - 一键启动脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] 检查依赖包...
python -c "import pyweixin" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装依赖包...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败
        pause
        exit /b 1
    )
    echo [完成] 依赖包安装成功
) else (
    echo [跳过] 依赖包已安装
)
echo.

echo [2/5] 检查配置文件...
if not exist ".env" (
    echo [创建] 正在从模板创建 .env 配置文件...
    copy .env.example .env >nul
    echo [警告] 请编辑 .env 文件，填入你的 API 配置！
    echo.
    echo 需要配置的关键项：
    echo   - OPENAI_BASE_URL   （API 地址）
    echo   - OPENAI_API_KEY    （API 密钥）
    echo   - MODEL_NAME        （模型名称）
    echo.
    echo 按任意键打开配置文件编辑...
    pause >nul
    notepad .env
    echo.
    echo 配置完成后，按任意键继续...
    pause >nul
) else (
    echo [跳过] 配置文件已存在
)
echo.

echo [3/5] 检查微信 UI Automation...
python -m wechat_bot.app --env .env --live-check >nul 2>&1
if errorlevel 1 (
    echo [警告] 微信 UI Automation 可能不可用
    echo.
    echo 请执行以下步骤：
    echo   1. 按 Win+Ctrl+Enter 启动"讲述人"
    echo   2. 登录微信（如果未登录）
    echo   3. 等待 5 分钟
    echo   4. 按 Win+Ctrl+Enter 关闭"讲述人"
    echo   5. 重新运行此脚本
    echo.
    echo 详细说明请查看 GETTING_STARTED.md
    echo.
    choice /C YN /M "是否继续启动（不推荐）"
    if errorlevel 2 exit /b 0
) else (
    echo [完成] 微信 UI Automation 可用
)
echo.

echo [4/5] 运行快速测试...
python -m wechat_bot.app --env .env --smoke-test
if errorlevel 1 (
    echo [错误] Smoke test 失败，请检查配置
    pause
    exit /b 1
)
echo.

echo [5/5] 确认运行模式...
echo.
echo 当前配置：
findstr /C:"DRY_RUN" .env
echo.
echo ==========================================
echo   重要提示：
echo ==========================================
echo.
echo   DRY_RUN=true  ：测试模式，不真实发送消息
echo   DRY_RUN=false ：生产模式，会真实发送消息！
echo.
echo ==========================================

findstr /C:"DRY_RUN=false" .env >nul
if not errorlevel 1 (
    echo.
    echo [警告] 你即将启动【生产模式】，将真实发送微信消息！
    echo.
    choice /C YN /M "确认启动生产模式"
    if errorlevel 2 (
        echo [取消] 已取消启动
        echo.
        echo 如需测试，请编辑 .env 文件，设置 DRY_RUN=true
        pause
        exit /b 0
    )
) else (
    echo.
    echo [安全] 当前为测试模式，不会真实发送消息
    echo.
    echo 如需真实发送，请编辑 .env 文件，设置 DRY_RUN=false
    echo.
    pause
)

echo.
echo ========================================
echo   正在启动微信值班助手...
echo ========================================
echo.
echo 控制台说明：
echo   - 状态栏显示：在线状态、模式、空闲时间
echo   - 暂停自动回复：勾选后停止自动回复
echo   - 模式选择：自动检测/强制在线/强制离线
echo   - 标签页：每日总览/待办风险/自动回复
echo.
echo 关闭控制台：点击窗口的 X 按钮或按 Ctrl+C
echo.
echo ========================================
echo.

python -m wechat_bot --env .env

echo.
echo 控制台已关闭。
pause
