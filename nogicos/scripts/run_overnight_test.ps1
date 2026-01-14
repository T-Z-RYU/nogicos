# NogicOS Overnight Self-Healing Test
# 过夜自动测试 + 修复脚本
# 运行后可以去睡觉，明天来看结果

param(
    [switch]$NoFix,
    [switch]$NoBrowser,
    [int]$MaxRounds = 500
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NogicOS Overnight Self-Healing Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will run continuously until:" -ForegroundColor Yellow
Write-Host "  1. Product reaches stability (5 consecutive stable rounds)" -ForegroundColor Yellow
Write-Host "  2. Maximum rounds reached ($MaxRounds)" -ForegroundColor Yellow
Write-Host "  3. You press Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Navigate to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "[1/4] Checking prerequisites..." -ForegroundColor Green

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Python: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "  [ERROR] Python not found!" -ForegroundColor Red
    exit 1
}

# Check API keys
if (-not (Test-Path "api_keys.py")) {
    Write-Host "  [ERROR] api_keys.py not found!" -ForegroundColor Red
    exit 1
}
Write-Host "  API Keys: OK" -ForegroundColor Gray

# Check if server is running
Write-Host ""
Write-Host "[2/4] Checking services..." -ForegroundColor Green

$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $backendRunning = $true
        Write-Host "  Backend (8080): Running" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Backend (8080): Not running" -ForegroundColor Yellow
}

$frontendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $frontendRunning = $true
        Write-Host "  Frontend (5173): Running" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Frontend (5173): Not running" -ForegroundColor Yellow
}

if (-not $backendRunning) {
    Write-Host ""
    Write-Host "  [!] Backend is not running. Starting it now..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "hive_server.py" -WindowStyle Minimized
    Write-Host "  Waiting 10 seconds for backend to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
}

Write-Host ""
Write-Host "[3/4] Configuration" -ForegroundColor Green
Write-Host "  Max rounds: $MaxRounds" -ForegroundColor Gray
Write-Host "  Auto-fix: $(if ($NoFix) { 'Disabled' } else { 'Enabled' })" -ForegroundColor Gray
Write-Host "  Browser tests: $(if ($NoBrowser) { 'Disabled' } else { 'Enabled' })" -ForegroundColor Gray
Write-Host "  Stability threshold: 5 consecutive stable rounds" -ForegroundColor Gray

# Build command
$cmd = "python -m tests.self_healing_test --overnight --max-rounds $MaxRounds"
if ($NoFix) { $cmd += " --no-fix" }
if ($NoBrowser) { $cmd += " --no-browser" }

Write-Host ""
Write-Host "[4/4] Starting overnight test..." -ForegroundColor Green
Write-Host ""
Write-Host "Command: $cmd" -ForegroundColor DarkGray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEST STARTED - You can go to sleep!" -ForegroundColor Cyan
Write-Host "  Results will be in:" -ForegroundColor Cyan
Write-Host "  tests/self_healing_results/" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the test
Invoke-Expression $cmd

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  PRODUCT IS STABLE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "  Testing completed (check results)" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Full report: tests/self_healing_results/final_report.txt" -ForegroundColor Cyan
Write-Host ""

exit $exitCode

