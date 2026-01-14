@echo off
echo ================================================
echo PM Tool v2 - 设置开机自启动
echo ================================================
echo.

set SCRIPT_DIR=%~dp0
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo 正在创建启动快捷方式...

:: 使用 PowerShell 创建快捷方式
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP_FOLDER%\PM Tool v2.lnk'); $s.TargetPath = '%SCRIPT_DIR%start-background.vbs'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = 'PM Tool v2 自动启动'; $s.Save()"

if exist "%STARTUP_FOLDER%\PM Tool v2.lnk" (
    echo.
    echo ✅ 开机自启动已设置！
    echo    快捷方式位置: %STARTUP_FOLDER%\PM Tool v2.lnk
    echo.
    echo    下次开机时，PM Tool v2 将自动在后台启动
) else (
    echo.
    echo ❌ 设置失败，请手动操作：
    echo    1. 按 Win+R，输入 shell:startup
    echo    2. 把 start-background.vbs 的快捷方式放进去
)

echo.
pause


