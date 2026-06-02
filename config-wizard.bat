@echo off
REM 设置代码页为 UTF-8
chcp 65001 >nul 2>&1

echo ========================================
echo   WeChatBot - Configuration Wizard
echo ========================================
echo.

REM 检查是否已有配置
if exist ".env" (
    echo Existing .env configuration file detected.
    echo.
    choice /C YN /M "Reconfigure (will overwrite existing config)"
    if errorlevel 2 (
        echo.
        echo Keeping existing config. Opening for edit:
        notepad .env
        pause
        exit /b 0
    )
    echo.
)

echo [1/8] Creating configuration file...
if exist ".env.example" (
    copy .env.example .env >nul 2>&1
) else (
    echo [Error] .env.example not found
    pause
    exit /b 1
)
echo [Done] Configuration file created
echo.

echo ========================================
echo   Configuration Wizard Started
echo ========================================
echo.

REM API Base URL
echo [2/8] OpenAI Compatible API Configuration
echo.
set /p api_url="Enter API base URL (e.g. https://api.openai.com): "
if "%api_url%"=="" set "api_url=https://api.openai.com"

REM API Key
echo.
set /p api_key="Enter API key (e.g. sk-xxx): "
if "%api_key%"=="" (
    echo [Warning] API key is empty, needs manual configuration later
    set "api_key=sk-your-api-key-here"
)

REM Model Name
echo.
echo Common models:
echo   1. gpt-3.5-turbo (Recommended, cheap)
echo   2. gpt-4
echo   3. gpt-4-turbo
echo   4. Custom
echo.
set /p model_choice="Select model (1-4): "

if "%model_choice%"=="1" set "model_name=gpt-3.5-turbo"
if "%model_choice%"=="2" set "model_name=gpt-4"
if "%model_choice%"=="3" set "model_name=gpt-4-turbo"
if "%model_choice%"=="4" (
    set /p model_name="Enter custom model name: "
)
if "%model_name%"=="" set "model_name=gpt-3.5-turbo"

REM Idle Time
echo.
echo [3/8] Online Detection Configuration
echo.
set /p idle_min="Idle minutes to trigger offline (default 10): "
if "%idle_min%"=="" set "idle_min=10"

REM Auto Reply Delay
echo.
echo [4/8] Auto Reply Delay Configuration
echo.
set /p delay_min="Minimum delay seconds (default 20): "
if "%delay_min%"=="" set "delay_min=20"

set /p delay_max="Maximum delay seconds (default 60): "
if "%delay_max%"=="" set "delay_max=60"

REM Cooldown
echo.
echo [5/8] Contact Cooldown Time
echo.
set /p cooldown="Reply interval minutes for same contact (default 10): "
if "%cooldown%"=="" set "cooldown=10"

REM Data Directory
echo.
echo [6/8] Data Storage Directory
echo.
set /p data_dir="Data storage directory (default data): "
if "%data_dir%"=="" set "data_dir=data"

REM Running Mode
echo.
echo [7/8] Running Mode Selection
echo.
echo Important:
echo   - Test mode (DRY_RUN=true): Record only, no real sending
echo   - Production mode (DRY_RUN=false): WILL send real messages
echo.
choice /C 12 /M "1=Test Mode  2=Production Mode, Choose"

if errorlevel 2 (
    set "dry_run=false"
    echo [Warning] Production mode selected!
) else (
    set "dry_run=true"
    echo [Safe] Test mode selected
)

REM Write Configuration
echo.
echo [8/8] Saving configuration...

(
echo # OpenAI Compatible API Configuration
echo OPENAI_BASE_URL=%api_url%
echo OPENAI_API_KEY=%api_key%
echo MODEL_NAME=%model_name%
echo.
echo # User Online Detection Configuration
echo IDLE_MINUTES=%idle_min%
echo.
echo # Auto Reply Delay Configuration
echo AUTO_REPLY_DELAY_MIN_SECONDS=%delay_min%
echo AUTO_REPLY_DELAY_MAX_SECONDS=%delay_max%
echo.
echo # Contact Cooldown Time
echo CONTACT_COOLDOWN_MINUTES=%cooldown%
echo.
echo # Data Storage Directory
echo DATA_DIR=%data_dir%
echo.
echo # Running Mode
echo DRY_RUN=%dry_run%
) > .env

echo [Done] Configuration saved to .env
echo.

echo ========================================
echo   Configuration Summary
echo ========================================
echo.
echo API URL: %api_url%
echo Model: %model_name%
echo Idle Minutes: %idle_min%
echo Reply Delay: %delay_min%-%delay_max% seconds
echo Cooldown: %cooldown% minutes
echo Running Mode: DRY_RUN=%dry_run%
echo.

if "%api_key%"=="sk-your-api-key-here" (
    echo [Warning] You haven't configured API key yet!
    echo.
    choice /C YN /M "Edit configuration file now"
    if not errorlevel 2 notepad .env
)

echo.
echo ========================================
echo   Configuration Complete!
echo ========================================
echo.
echo Next steps:
if "%dry_run%"=="true" (
    echo   1. Double-click "quick-start.bat" to start testing
) else (
    echo   1. Double-click "production-start.bat" to start
)
echo   2. Read GETTING_STARTED.md for detailed instructions
echo.

pause
