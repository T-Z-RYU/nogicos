# PM Tool v2 - Background Service Script
# This script starts services in background, they continue running after closing window

param(
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Install
)

$BackendPort = 8001
$FrontendPort = 3001
$ProjectPath = "C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2"

function Test-Port($port) {
    $result = netstat -ano | Select-String ":$port.*LISTENING"
    return $result -ne $null
}

function Get-ProcessByPort($port) {
    $result = netstat -ano | Select-String ":$port.*LISTENING"
    if ($result) {
        $procId = ($result -split '\s+')[-1]
        return [int]$procId
    }
    return $null
}

function Start-Services {
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  PM Tool v2 - Starting Services" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""

    # Start Backend
    if (Test-Port $BackendPort) {
        Write-Host "[Backend] Already running (Port $BackendPort)" -ForegroundColor Yellow
    } else {
        Write-Host "[Backend] Starting..." -ForegroundColor Green
        $backend = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port $BackendPort" -WorkingDirectory "$ProjectPath\backend" -WindowStyle Hidden -PassThru
        Write-Host "[Backend] Started (PID: $($backend.Id))" -ForegroundColor Green
    }

    Start-Sleep -Seconds 2

    # Start Frontend
    if (Test-Port $FrontendPort) {
        Write-Host "[Frontend] Already running (Port $FrontendPort)" -ForegroundColor Yellow
    } else {
        Write-Host "[Frontend] Starting..." -ForegroundColor Green
        $frontend = Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "$ProjectPath\frontend" -WindowStyle Hidden -PassThru
        Write-Host "[Frontend] Started (PID: $($frontend.Id))" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  Services running in background!" -ForegroundColor Green
    Write-Host "  Frontend: http://localhost:$FrontendPort" -ForegroundColor White
    Write-Host "  Backend:  http://localhost:$BackendPort" -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Cyan
}

function Stop-Services {
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  PM Tool v2 - Stopping Services" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""

    # Stop Backend
    $backendPid = Get-ProcessByPort $BackendPort
    if ($backendPid) {
        Stop-Process -Id $backendPid -Force -ErrorAction SilentlyContinue
        Write-Host "[Backend] Stopped (PID: $backendPid)" -ForegroundColor Green
    } else {
        Write-Host "[Backend] Not running" -ForegroundColor Yellow
    }

    # Stop Frontend
    $frontendPid = Get-ProcessByPort $FrontendPort
    if ($frontendPid) {
        Stop-Process -Id $frontendPid -Force -ErrorAction SilentlyContinue
        Write-Host "[Frontend] Stopped (PID: $frontendPid)" -ForegroundColor Green
    } else {
        Write-Host "[Frontend] Not running" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "All services stopped" -ForegroundColor Green
}

function Show-Status {
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  PM Tool v2 - Service Status" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""

    if (Test-Port $BackendPort) {
        $bpid = Get-ProcessByPort $BackendPort
        Write-Host "[Backend]  RUNNING (PID: $bpid, Port: $BackendPort)" -ForegroundColor Green
    } else {
        Write-Host "[Backend]  STOPPED" -ForegroundColor Red
    }

    if (Test-Port $FrontendPort) {
        $fpid = Get-ProcessByPort $FrontendPort
        Write-Host "[Frontend] RUNNING (PID: $fpid, Port: $FrontendPort)" -ForegroundColor Green
    } else {
        Write-Host "[Frontend] STOPPED" -ForegroundColor Red
    }
}

function Install-Startup {
    $startupFolder = [Environment]::GetFolderPath('Startup')
    $shortcutPath = Join-Path $startupFolder "PMTool-Service.lnk"
    $scriptPath = "$ProjectPath\PMTool-Service.ps1"

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`" -Start"
    $shortcut.WorkingDirectory = $ProjectPath
    $shortcut.WindowStyle = 7
    $shortcut.Save()

    Write-Host "Auto-start enabled!" -ForegroundColor Green
    Write-Host "Shortcut: $shortcutPath" -ForegroundColor White
}

# Main
if ($Start) {
    Start-Services
} elseif ($Stop) {
    Stop-Services
} elseif ($Status) {
    Show-Status
} elseif ($Install) {
    Install-Startup
} else {
    Start-Services
}
