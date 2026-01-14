@echo off
chcp 65001 > nul
echo ========================================
echo   SkillWeaver 泛化测试
echo   测试将在后台运行
echo ========================================
echo.

cd /d "%~dp0"

echo 清理旧日志...
del /f benchmark_log.txt 2>nul
del /f benchmark_error.txt 2>nul

echo 启动测试...
start /B python benchmark_generalization.py > benchmark_log.txt 2>&1

echo.
echo 测试已在后台启动！
echo.
echo 查看进度: python check_progress.py
echo 日志文件: benchmark_log.txt
echo.
echo 按任意键退出...
pause > nul
