# Windows VNC + noVNC 一键启动测试脚本
# 运行方式: 右键 -> 使用 PowerShell 运行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NogicOS VNC 测试环境启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 配置
$VNC_PORT = 5900
$NOVNC_PORT = 6080
$NOVNC_PATH = "C:\Users\WIN\Desktop\Cursor Project\nogicos\novnc-client"

# Step 1: 检查 TightVNC Server
Write-Host "[1/4] 检查 TightVNC Server..." -ForegroundColor Yellow
$vncProcess = Get-Process -Name "tvnserver" -ErrorAction SilentlyContinue
if ($vncProcess) {
    Write-Host "  ✓ TightVNC Server 正在运行" -ForegroundColor Green
} else {
    Write-Host "  ✗ TightVNC Server 未运行！" -ForegroundColor Red
    Write-Host "  请先安装并启动 TightVNC Server" -ForegroundColor Red
    Write-Host "  下载地址: https://www.tightvnc.com/download.php" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit
}

# Step 2: 检查 websockify
Write-Host "[2/4] 检查 websockify..." -ForegroundColor Yellow
$websockify = pip show websockify 2>$null
if ($websockify) {
    Write-Host "  ✓ websockify 已安装" -ForegroundColor Green
} else {
    Write-Host "  正在安装 websockify..." -ForegroundColor Yellow
    pip install websockify
}

# Step 3: 检查/下载 noVNC
Write-Host "[3/4] 检查 noVNC 客户端..." -ForegroundColor Yellow
if (Test-Path $NOVNC_PATH) {
    Write-Host "  ✓ noVNC 已存在" -ForegroundColor Green
} else {
    Write-Host "  正在下载 noVNC..." -ForegroundColor Yellow
    cd "C:\Users\WIN\Desktop\Cursor Project\nogicos"
    git clone https://github.com/novnc/noVNC.git novnc-client
}

# Step 4: 启动 websockify + noVNC
Write-Host "[4/4] 启动 noVNC 服务..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  启动成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  浏览器访问: http://localhost:$NOVNC_PORT/vnc.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  测试步骤:" -ForegroundColor Yellow
Write-Host "  1. 打开 Chrome" -ForegroundColor White
Write-Host "  2. 访问 http://localhost:6080/vnc.html" -ForegroundColor White
Write-Host "  3. 输入 VNC 密码连接" -ForegroundColor White
Write-Host "  4. 打开 Claude.ai，让 Claude in Chrome 操作这个桌面" -ForegroundColor White
Write-Host ""
Write-Host "  按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

# 启动 websockify
cd $NOVNC_PATH
websockify --web . $NOVNC_PORT localhost:$VNC_PORT








