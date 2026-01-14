@echo off
echo ================================================
echo PM Tool v2 - 移除开机自启动
echo ================================================
echo.

set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

if exist "%STARTUP_FOLDER%\PM Tool v2.lnk" (
    del "%STARTUP_FOLDER%\PM Tool v2.lnk"
    echo ✅ 开机自启动已移除
) else (
    echo ⚠️  开机自启动未设置，无需移除
)

echo.
pause


