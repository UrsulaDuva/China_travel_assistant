#!/usr/bin/env pwsh
# =============================================================================
# China Travel Pro - 停止所有服务 (PowerShell)
# =============================================================================

Write-Host "`n正在停止所有服务...`n" -ForegroundColor Yellow

# 停止端口 10001 上的进程 (后端)
$backendPort = Get-NetTCPConnection -LocalPort 10001 -ErrorAction SilentlyContinue
if ($backendPort) {
    $backendPid = $backendPort.OwningProcess
    Stop-Process -Id $backendPid -Force -ErrorAction SilentlyContinue
    Write-Host "[已停止] 后端服务 (端口 10001)" -ForegroundColor Green
} else {
    Write-Host "[跳过] 后端服务未运行" -ForegroundColor Gray
}

# 停止端口 5173 上的进程 (前端)
$frontendPort = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($frontendPort) {
    $frontendPid = $frontendPort.OwningProcess
    Stop-Process -Id $frontendPid -Force -ErrorAction SilentlyContinue
    Write-Host "[已停止] 前端服务 (端口 5173)" -ForegroundColor Green
} else {
    Write-Host "[跳过] 前端服务未运行" -ForegroundColor Gray
}

# 清理残留进程
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*vite*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "`n[完成] 所有服务已停止`n" -ForegroundColor Green
Read-Host "按回车键退出"