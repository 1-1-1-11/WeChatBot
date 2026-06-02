@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   微信值班助手 - 配置向导
echo ========================================
echo.

REM 检查是否已有配置
if exist ".env" (
    echo 检测到已存在的 .env 配置文件
    echo.
    choice /C YN /M "是否重新配置（会覆盖现有配置）"
    if errorlevel 2 (
        echo.
        echo 保持现有配置，正在打开编辑器...
        notepad .env
        pause
        exit /b 0
    )
    echo.
)

echo [1/8] 正在创建配置文件...
if exist ".env.example" (
    copy .env.example .env >nul 2>&1
) else (
    echo [错误] 未找到 .env.example 模板文件
    pause
    exit /b 1
)
echo [完成] 配置文件已创建
echo.

echo ========================================
echo   开始配置向导
echo ========================================
echo.

REM API 基础 URL
echo [2/8] OpenAI 兼容 API 配置
echo.
set /p "api_url=请输入 API 地址（例如 https://api.openai.com）: "
if "!api_url!"=="" set "api_url=https://api.openai.com"

REM API Key
echo.
set /p "api_key=请输入 API 密钥（例如 sk-xxx）: "
if "!api_key!"=="" (
    echo [警告] API 密钥为空，需要后续手动配置
    set "api_key=sk-your-api-key-here"
)

REM 模型名称
echo.
echo 常用模型：
echo   1. gpt-3.5-turbo （推荐，便宜）
echo   2. gpt-4
echo   3. gpt-4-turbo
echo   4. 自定义
echo.
set /p "model_choice=请选择模型（1-4）: "

if "!model_choice!"=="1" set "model_name=gpt-3.5-turbo"
if "!model_choice!"=="2" set "model_name=gpt-4"
if "!model_choice!"=="3" set "model_name=gpt-4-turbo"
if "!model_choice!"=="4" (
    set /p "model_name=请输入自定义模型名称: "
)
if "!model_name!"=="" set "model_name=gpt-3.5-turbo"

REM 空闲时间
echo.
echo [3/8] 在线检测配置
echo.
set /p "idle_min=空闲多少分钟判断为离线（默认 10）: "
if "!idle_min!"=="" set "idle_min=10"

REM 自动回复延迟
echo.
echo [4/8] 自动回复延迟配置
echo.
set /p "delay_min=最小延迟秒数（默认 20）: "
if "!delay_min!"=="" set "delay_min=20"

set /p "delay_max=最大延迟秒数（默认 60）: "
if "!delay_max!"=="" set "delay_max=60"

REM 冷却时间
echo.
echo [5/8] 联系人冷却时间
echo.
set /p "cooldown=同一联系人回复间隔分钟数（默认 10）: "
if "!cooldown!"=="" set "cooldown=10"

REM 数据目录
echo.
echo [6/8] 数据存储目录
echo.
set /p "data_dir=数据存储目录（默认 data）: "
if "!data_dir!"=="" set "data_dir=data"

REM 运行模式
echo.
echo [7/8] 运行模式选择
echo.
echo 重要提示：
echo   - 测试模式（DRY_RUN=true）：只记录，不真实发送
echo   - 生产模式（DRY_RUN=false）：会真实发送微信消息
echo.
choice /C 12 /M "1=测试模式  2=生产模式，请选择"

if errorlevel 2 (
    set "dry_run=false"
    echo [警告] 已选择生产模式！
) else (
    set "dry_run=true"
    echo [安全] 已选择测试模式
)

REM 写入配置
echo.
echo [8/8] 正在保存配置...

(
echo # OpenAI 兼容 API 配置
echo OPENAI_BASE_URL=!api_url!
echo OPENAI_API_KEY=!api_key!
echo MODEL_NAME=!model_name!
echo.
echo # 用户在线检测配置
echo IDLE_MINUTES=!idle_min!
echo.
echo # 自动回复延迟配置
echo AUTO_REPLY_DELAY_MIN_SECONDS=!delay_min!
echo AUTO_REPLY_DELAY_MAX_SECONDS=!delay_max!
echo.
echo # 联系人冷却时间
echo CONTACT_COOLDOWN_MINUTES=!cooldown!
echo.
echo # 数据存储目录
echo DATA_DIR=!data_dir!
echo.
echo # 运行模式
echo DRY_RUN=!dry_run!
) > .env

echo [完成] 配置已保存到 .env
echo.

echo ========================================
echo   配置摘要
echo ========================================
echo.
echo API 地址：!api_url!
echo 模型名称：!model_name!
echo 空闲时间：!idle_min! 分钟
echo 回复延迟：!delay_min!-!delay_max! 秒
echo 冷却时间：!cooldown! 分钟
echo 运行模式：DRY_RUN=!dry_run!
echo.

if "!api_key!"=="sk-your-api-key-here" (
    echo [警告] 你还没有配置 API 密钥！
    echo.
    choice /C YN /M "是否现在编辑配置文件"
    if not errorlevel 2 notepad .env
)

echo.
echo ========================================
echo   配置完成！
echo ========================================
echo.
echo 下一步：
if "!dry_run!"=="true" (
    echo   1. 双击运行"快速启动.bat"开始测试
) else (
    echo   1. 双击运行"生产启动.bat"开始使用
)
echo   2. 查看 GETTING_STARTED.md 了解详细使用方法
echo.

pause
