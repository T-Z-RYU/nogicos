@echo off
echo ========================================
echo AI Browser 技术验证
echo ========================================
echo.

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python
    pause
    exit /b 1
)

echo 选择操作:
echo   1. 快速环境检查
echo   2. 运行完整验证
echo   3. 运行基础测试
echo   4. 启动 Electron 浏览器
echo   5. 退出
echo.
set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 运行环境检查...
    python quick_test.py
) else if "%choice%"=="2" (
    echo.
    echo 运行完整验证...
    python run_verify.py
) else if "%choice%"=="3" (
    echo.
    echo 运行基础测试...
    python tests/basic_test.py
) else if "%choice%"=="4" (
    echo.
    echo 启动 Electron 浏览器...
    cd electron-browser
    npm start
) else if "%choice%"=="5" (
    exit /b 0
) else (
    echo 无效选项
)

echo.
pause
