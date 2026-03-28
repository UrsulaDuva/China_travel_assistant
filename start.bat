@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: =============================================================================
:: China Travel Pro - 一键启动脚本 (Windows)
:: =============================================================================
:: 使用说明:
::   start.bat          - 启动所有服务
::   start.bat backend  - 仅启动后端
::   start.bat frontend - 仅启动前端
::
:: 前置条件:
::   1. Python 3.11+ 已安装
::   2. Node.js 18+ 已安装
::   3. LM Studio 已安装并运行本地模型 (可选，用于意图识别)
::   4. 已配置 .env 文件 (复制 .env.example)
:: =============================================================================

title China Travel Pro

:: 颜色定义
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%     China Travel Pro - AI 旅游规划系统%RESET%
echo %CYAN%============================================================%RESET%
echo.

:: 检查 .env 文件
if not exist ".env" (
    echo %RED%[错误] .env 文件不存在%RESET%
    echo.
    echo %YELLOW%请执行以下步骤:%RESET%
    echo   1. 复制 .env.example 为 .env
    echo   2. 编辑 .env 填写 API Keys
    echo.
    pause
    exit /b 1
)

:: 检查 Python 虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo %YELLOW%[警告] Python 虚拟环境不存在，正在创建...%RESET%
    python -m venv .venv
    if errorlevel 1 (
        echo %RED%[错误] 创建虚拟环境失败%RESET%
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    pip install -e .
) else (
    call .venv\Scripts\activate.bat
)

:: 检查前端依赖
if not exist "src\frontend\node_modules" (
    echo %YELLOW%[警告] 前端依赖未安装，正在安装...%RESET%
    cd src\frontend
    call npm install
    cd ..\..
)

:: 检查 LM Studio (可选)
echo %CYAN%[检查] LM Studio 本地模型服务...%RESET%
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:1234/v1/models' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[提示] LM Studio 未运行，意图识别将使用备用方案%RESET%
    echo        如需本地模型支持，请启动 LM Studio 并加载模型
) else (
    echo %GREEN%[正常] LM Studio 已运行%RESET%
)
echo.

:: 解析命令行参数
set "MODE=all"
if not "%1"=="" set "MODE=%1"

echo %GREEN%启动模式: %MODE%%RESET%
echo.

:: 根据模式启动服务
if "%MODE%"=="backend" goto :start_backend
if "%MODE%"=="frontend" goto :start_frontend
if "%MODE%"=="all" goto :start_all
echo %RED%[错误] 未知模式: %MODE%%RESET%
echo 用法: %~nx0 [backend^|frontend^|all]
pause
exit /b 1

:start_backend
echo %CYAN%[启动] 后端服务 (端口: 10001)%RESET%
start "China Travel - Backend" cmd /k "cd /d "%SCRIPT_DIR%" && call .venv\Scripts\activate.bat && python -m uvicorn src.orchestrator.api.app:app --host 0.0.0.0 --port 10001 --reload"
echo %GREEN%[完成] 后端服务已启动%RESET%
echo        API 文档: http://localhost:10001/docs
goto :end

:start_frontend
echo %CYAN%[启动] 前端服务 (端口: 5173)%RESET%
start "China Travel - Frontend" cmd /k "cd /d "%SCRIPT_DIR%\src\frontend" && npm run dev"
echo %GREEN%[完成] 前端服务已启动%RESET%
echo        访问地址: http://localhost:5173
goto :end

:start_all
echo %CYAN%[启动] 后端服务 (端口: 10001)%RESET%
start "China Travel - Backend" cmd /k "cd /d "%SCRIPT_DIR%" && call .venv\Scripts\activate.bat && python -m uvicorn src.orchestrator.api.app:app --host 0.0.0.0 --port 10001 --reload"
timeout /t 3 /nobreak >nul

echo %CYAN%[启动] 前端服务 (端口: 5173)%RESET%
start "China Travel - Frontend" cmd /k "cd /d "%SCRIPT_DIR%\src\frontend" && npm run dev"

echo.
echo %GREEN%============================================================%RESET%
echo %GREEN%  所有服务已启动!%RESET%
echo %GREEN%============================================================%RESET%
echo.
echo   %CYAN%前端地址:%RESET%  http://localhost:5173
echo   %CYAN%后端 API:%RESET%   http://localhost:10001
echo   %CYAN%API 文档:%RESET%   http://localhost:10001/docs
echo.
echo   %YELLOW%提示:%RESET%
echo   - 关闭此窗口不会停止服务
echo   - 请关闭对应的命令行窗口来停止服务
echo   - 或运行 stop.bat 停止所有服务
echo.
goto :end

:end
pause