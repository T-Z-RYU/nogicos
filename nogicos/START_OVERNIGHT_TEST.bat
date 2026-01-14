@echo off
chcp 65001 > nul
title NogicOS Overnight Self-Healing Test

echo.
echo ========================================
echo   NogicOS Overnight Self-Healing Test
echo ========================================
echo.
echo This will run tests all night and auto-fix issues.
echo Results will be in: tests\self_healing_results\
echo.
echo Press any key to start, or close this window to cancel...
pause > nul

cd /d "%~dp0"

echo.
echo [1/2] Starting backend server...
start "NogicOS Backend" /min cmd /c "python hive_server.py"
timeout /t 10 /nobreak > nul

echo [2/2] Starting self-healing test...
echo.

python -m tests.self_healing_test --overnight

echo.
echo ========================================
echo   TEST COMPLETED
echo   Check: tests\self_healing_results\final_report.txt
echo ========================================
echo.
pause

