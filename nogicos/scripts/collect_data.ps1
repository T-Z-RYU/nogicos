# NogicOS 自动数据收集脚本
# 用法: .\scripts\collect_data.ps1 [-Count 50] [-Delay 2]

param(
    [int]$Count = 50,
    [float]$Delay = 2.0
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "NogicOS 自动数据收集" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "配置:"
Write-Host "  - 任务数量: $Count"
Write-Host "  - 延迟: ${Delay}s"
Write-Host "  - 预计时间: $([math]::Round($Count * ($Delay + 5) / 60, 1)) 分钟"
Write-Host ""

# 切换到 nogicos 目录
Set-Location $PSScriptRoot\..

# 检查服务器是否运行
$serverRunning = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*hive_server*" }

if (-not $serverRunning) {
    Write-Host "[启动] HiveServer..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "hive_server.py" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

# 运行数据收集
Write-Host "[运行] 开始收集数据..." -ForegroundColor Green
Write-Host ""

python -m engine.evaluation.auto_data_collector --count $Count --delay $Delay

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "完成! 查看 LangSmith Dashboard" -ForegroundColor Green
Write-Host "https://smith.langchain.com" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Green

