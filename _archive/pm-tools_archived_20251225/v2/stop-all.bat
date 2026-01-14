@echo off
title PM Tool v2 - 停止服务
echo ============================================
echo   PM Tool v2 - 停止所有服务
echo ============================================
echo.

:: 查找并终止后端进程
echo [后端] 正在停止...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo [后端] 已停止 (PID: %%a)
)

:: 查找并终止前端进程
echo [前端] 正在停止...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3001.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo [前端] 已停止 (PID: %%a)
)

echo.
echo ============================================
echo   所有服务已停止
echo ============================================
pause
