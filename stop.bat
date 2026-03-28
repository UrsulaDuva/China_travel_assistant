@echo off
chcp 65001 >nul

:: =============================================================================
:: China Travel Pro - 停止所有服务 (Windows)
:: =============================================================================

title China Travel Pro - Stop

echo.
echo 正在停止所有服务...
echo.

:: 停止后端服务 (端口 10001)
echo [检查] 后端服务...
taskkill /FI "WINDOWTITLE eq China Travel - Backend*" /F >nul 2>&1
if errorlevel 1 (
    echo [跳过] 后端服务未运行
) else (
    echo [已停止] 后端服务
)

:: 停止前端服务
echo [检查] 前端服务...
taskkill /FI "WINDOWTITLE eq China Travel - Frontend*" /F >nul 2>&1
if errorlevel 1 (
    echo [跳过] 前端服务未运行
) else (
    echo [已停止] 前端服务
)

:: 清理残留端口进程
echo [清理] 端口占用进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":10001" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo [完成] 所有服务已停止
echo.
pause