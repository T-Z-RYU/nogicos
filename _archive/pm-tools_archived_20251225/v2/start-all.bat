@echo off
title PM Tool v2 - Launcher
echo ============================================
echo   PM Tool v2 - 启动器
echo ============================================
echo.

:: 检查端口是否已被占用，如果是则跳过
netstat -ano | findstr ":8001.*LISTENING" >nul
if %errorlevel%==0 (
    echo [后端] 已在运行中，跳过启动
) else (
    echo [后端] 启动中...
    start "PM Tool Backend" /min cmd /c "cd /d \"C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\backend\" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
)

:: 等待后端启动
timeout /t 2 /nobreak >nul

netstat -ano | findstr ":3001.*LISTENING" >nul
if %errorlevel%==0 (
    echo [前端] 已在运行中，跳过启动
) else (
    echo [前端] 启动中...
    start "PM Tool Frontend" /min cmd /c "cd /d \"C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\frontend\" && npm run dev"
)

echo.
echo ============================================
echo   服务已启动！
echo   前端: http://localhost:3001
echo   后端: http://localhost:8001
echo ============================================
echo.
echo 提示：两个最小化的命令窗口正在运行服务
echo       关闭那些窗口会停止服务
echo       关闭这个窗口不会影响服务
echo.
pause
