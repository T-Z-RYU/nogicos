@echo off
echo ================================================
echo PM Tool v2 - 停止服务
echo ================================================
echo.

echo 正在停止后端 (Python/Uvicorn)...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul

echo 正在停止前端 (Node.js)...
taskkill /f /im node.exe 2>nul

echo.
echo ✅ 服务已停止
pause


