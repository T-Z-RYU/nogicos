# Peloton 竞品截图下载

## 目标页面
https://screensdesign.com/apps/peloton-fitness-workouts/?ts=0&vt=1&id=87

## 使用步骤

### 1. 以调试模式启动 Chrome

在 PowerShell 中运行：
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

### 2. 登录 screensdesign.com 会员账号

在打开的 Chrome 窗口中登录你的会员账号，确保可以访问完整截图。

### 3. 运行下载脚本

```bash
cd Peloton_Analysis
python download_screens.py
```

## 输出说明

- 截图将保存到 `Peloton_Screens_Downloaded` 文件夹
- 图片格式：PNG
- 图片宽度：统一调整为 402px（保持宽高比）
- 命名规则：`Screen_001.png`, `Screen_002.png`, ...

## 依赖

```
selenium
requests
Pillow
```

安装依赖：
```bash
pip install selenium requests Pillow
```

