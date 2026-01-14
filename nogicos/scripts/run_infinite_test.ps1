# NogicOS Infinite AI Tester - PowerShell Launcher
# 无限 AI 测试循环，直到产品稳定

param(
    [int]$MaxRounds = 100,
    [int]$StabilityThreshold = 3,
    [int]$TestsPerRound = 10,
    [int]$Timeout = 60
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NogicOS Infinite AI Tester" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "[1/3] Checking environment..." -ForegroundColor Yellow

# Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Python not found!" -ForegroundColor Red
    exit 1
}
Write-Host "      Python: $pythonVersion" -ForegroundColor Green

# Check if api_keys.py exists
if (-not (Test-Path "api_keys.py")) {
    Write-Host "[X] api_keys.py not found!" -ForegroundColor Red
    Write-Host "    Copy api_keys.example.py and fill in your API keys" -ForegroundColor Yellow
    exit 1
}
Write-Host "      API keys: Found" -ForegroundColor Green

Write-Host ""
Write-Host "[2/3] Configuration" -ForegroundColor Yellow
Write-Host "      Max rounds: $MaxRounds"
Write-Host "      Stability threshold: $StabilityThreshold consecutive stable rounds"
Write-Host "      Tests per round: $TestsPerRound"
Write-Host "      Timeout per test: ${Timeout}s"

Write-Host ""
Write-Host "[3/3] Starting infinite test loop..." -ForegroundColor Yellow
Write-Host ""

# Run the tester
python -m tests.infinite_ai_tester `
    --max-rounds $MaxRounds `
    --stability-threshold $StabilityThreshold `
    --tests-per-round $TestsPerRound `
    --timeout $Timeout

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Product reached stability! ✓" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "Testing completed (not stable)" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Results saved to: tests/infinite_test_results/" -ForegroundColor Cyan

exit $exitCode

