#!/usr/bin/env pwsh
# =============================================================================
# China Travel Pro - 一键启动脚本 (PowerShell)
# =============================================================================
# 使用说明:
#   ./start.ps1          - 启动所有服务
#   ./start.ps1 backend  - 仅启动后端
#   ./start.ps1 frontend - 仅启动前端
#
# 前置条件:
#   1. Python 3.11+ 已安装
#   2. Node.js 18+ 已安装
#   3. LM Studio 已安装并运行本地模型 (可选)
#   4. 已配置 .env 文件 (复制 .env.example)
# =============================================================================

param(
    [ValidateSet("all", "backend", "frontend")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"

# 端口配置
$BackendPort = 10001
$FrontendPort = 5173

# 颜色函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# 获取脚本目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-ColorOutput "`n============================================================" "Cyan"
Write-ColorOutput "     China Travel Pro - AI 旅游规划系统" "Cyan"
Write-ColorOutput "============================================================`n" "Cyan"

# 检查 .env 文件
if (-not (Test-Path ".env")) {
    Write-ColorOutput "[错误] .env 文件不存在" "Red"
    Write-ColorOutput "`n请执行以下步骤:" "Yellow"
    Write-ColorOutput "  1. Copy-Item .env.example .env" "White"
    Write-ColorOutput "  2. 编辑 .env 填写 API Keys" "White"
    Read-Host "按回车键退出"
    exit 1
}

# 检查 Python 虚拟环境
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-ColorOutput "[警告] Python 虚拟环境不存在，正在创建..." "Yellow"
    python -m venv .venv
    & .venv\Scripts\Activate.ps1
    pip install -e .
} else {
    & .venv\Scripts\Activate.ps1
}

# 检查前端依赖
if (-not (Test-Path "src\frontend\node_modules")) {
    Write-ColorOutput "[警告] 前端依赖未安装，正在安装..." "Yellow"
    Set-Location src\frontend
    npm install
    Set-Location $ScriptDir
}

# 检查 LM Studio (可选)
Write-ColorOutput "[检查] LM Studio 本地模型服务..." "Cyan"
try {
    $lmStudioCheck = Invoke-WebRequest -Uri "http://127.0.0.1:1234/v1/models" -TimeoutSec 2 -UseBasicParsing
    Write-ColorOutput "[正常] LM Studio 已运行" "Green"
} catch {
    Write-ColorOutput "[提示] LM Studio 未运行，意图识别将使用备用方案" "Yellow"
    Write-ColorOutput "       如需本地模型支持，请启动 LM Studio 并加载模型" "White"
}
Write-Host ""

Write-ColorOutput "启动模式: $Mode`n" "Green"

# 启动函数
function Start-Backend {
    Write-ColorOutput "[启动] 后端服务 (端口: $BackendPort)" "Cyan"
    Start-Process powershell -ArgumentList @"
-NoExit", "-Command", "cd '$ScriptDir'; & .\.venv\Scripts\Activate.ps1; python -m uvicorn src.orchestrator.api.app:app --host 0.0.0.0 --port $BackendPort --reload"
"@
    Write-ColorOutput "[完成] 后端服务已启动" "Green"
    Write-ColorOutput "       API 文档: http://localhost:$BackendPort/docs" "White"
}

function Start-Frontend {
    Write-ColorOutput "[启动] 前端服务 (端口: $FrontendPort)" "Cyan"
    Start-Process powershell -ArgumentList @"
-NoExit", "-Command", "cd '$ScriptDir\src\frontend'; npm run dev"
"@
    Write-ColorOutput "[完成] 前端服务已启动" "Green"
    Write-ColorOutput "       访问地址: http://localhost:$FrontendPort" "White"
}

# 根据模式启动
switch ($Mode) {
    "backend" {
        Start-Backend
    }
    "frontend" {
        Start-Frontend
    }
    "all" {
        Start-Backend
        Start-Sleep -Seconds 3
        Start-Frontend

        Write-ColorOutput "`n============================================================" "Green"
        Write-ColorOutput "  所有服务已启动!" "Green"
        Write-ColorOutput "============================================================`n" "Green"

        Write-ColorOutput "  前端地址:  " "Cyan" -NoNewline; Write-Host "http://localhost:$FrontendPort"
        Write-ColorOutput "  后端 API:  " "Cyan" -NoNewline; Write-Host "http://localhost:$BackendPort"
        Write-ColorOutput "  API 文档:  " "Cyan" -NoNewline; Write-Host "http://localhost:$BackendPort/docs"

        Write-ColorOutput "`n  提示:" "Yellow"
        Write-ColorOutput "  - 关闭此窗口不会停止服务" "White"
        Write-ColorOutput "  - 请关闭对应的 PowerShell 窗口来停止服务" "White"
        Write-ColorOutput "  - 或运行 ./stop.ps1 停止所有服务`n" "White"
    }
}

Write-Host ""
Read-Host "按回车键退出"