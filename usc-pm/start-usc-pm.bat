@echo off
setlocal
cd /d "%~dp0"

REM Start backend in a hidden window if not already running
powershell -NoProfile -Command "if (-not (Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue)) { Start-Process -WindowStyle Hidden -FilePath '%~dp0backend\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8080' -WorkingDirectory '%~dp0' }"

REM Wait for backend to be ready
powershell -NoProfile -Command "for ($i=0; $i -lt 30; $i++) { try { (Invoke-WebRequest -UseBasicParsing -Uri http://127.0.0.1:8080/health -TimeoutSec 1) | Out-Null; break } catch { Start-Sleep -Milliseconds 500 } }"

REM Start Vite if not already running
powershell -NoProfile -Command "if (-not (Get-NetTCPConnection -LocalPort 1420 -State Listen -ErrorAction SilentlyContinue)) { Start-Process -WindowStyle Hidden -FilePath 'cmd.exe' -ArgumentList '/c','npm.cmd','run','dev' -WorkingDirectory '%~dp0desktop' }"

REM Wait for Vite
powershell -NoProfile -Command "for ($i=0; $i -lt 30; $i++) { try { (Invoke-WebRequest -UseBasicParsing -Uri http://localhost:1420 -TimeoutSec 1) | Out-Null; break } catch { Start-Sleep -Milliseconds 500 } }"

REM Launch Electron window (foreground; closing it leaves backend running)
cd /d "%~dp0desktop"
start "" "%~dp0desktop\node_modules\.bin\electron.cmd" .

endlocal
