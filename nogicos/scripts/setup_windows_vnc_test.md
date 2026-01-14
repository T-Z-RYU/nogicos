# Windows VNC + Claude in Chrome 测试指南

## 🎯 测试目标
在浏览器里看到 Windows 桌面，然后用 Claude in Chrome 操作它

---

## Step 1: 安装 TightVNC Server（3分钟）

### 下载
1. 打开：https://www.tightvnc.com/download.php
2. 下载 **TightVNC for Windows** (64-bit 版本)
3. 运行安装程序

### 安装时注意
- 选择 **Custom** 安装
- **只勾选 TightVNC Server**（不需要 Viewer）
- 设置密码：`demo123`（或你喜欢的密码）

### 确认运行
- 安装完成后，系统托盘会出现 TightVNC 图标
- 右键图标 → 确认 "TightVNC Server is running"

---

## Step 2: 安装 websockify（2分钟）

打开 PowerShell，运行：

```powershell
pip install websockify
```

如果没有 Python，先去 https://www.python.org/downloads/ 下载安装

---

## Step 3: 下载 noVNC（2分钟）

打开 PowerShell，运行：

```powershell
cd C:\Users\WIN\Desktop\Cursor Project\nogicos
git clone https://github.com/novnc/noVNC.git novnc-client
```

---

## Step 4: 启动 websockify（1分钟）

打开 PowerShell，运行：

```powershell
cd C:\Users\WIN\Desktop\Cursor Project\nogicos\novnc-client
websockify --web . 6080 localhost:5900
```

保持这个窗口打开！

---

## Step 5: 测试浏览器访问（1分钟）

1. 打开 Chrome 浏览器
2. 访问：http://localhost:6080/vnc.html
3. 点击 "Connect"
4. 输入密码：`demo123`

**成功标志**：你在浏览器里看到了 Windows 桌面！

---

## Step 6: 用 Claude in Chrome 测试（5分钟）

1. 确保 Chrome 已安装 **Claude in Chrome** 扩展
2. 打开 Claude.ai：https://claude.ai
3. 新建对话，输入：

```
请看一下这个浏览器的另一个标签页（localhost:6080 那个），
那是一个 noVNC 远程桌面。
请帮我在那个 Windows 桌面上：
1. 打开计算器
2. 计算 123 + 456
```

4. 观察 Claude in Chrome 是否能操作 noVNC 里的 Windows 桌面

---

## ✅ 测试成功标志

- [ ] 浏览器能看到 Windows 桌面
- [ ] Claude in Chrome 能识别 noVNC 画面
- [ ] Claude in Chrome 能在 noVNC 里点击、操作

---

## ❌ 如果失败

### 问题1: websockify 报错
```
解决：确保 TightVNC Server 正在运行（端口 5900）
```

### 问题2: noVNC 连接失败
```
解决：检查防火墙，允许 5900 和 6080 端口
```

### 问题3: Claude in Chrome 不操作
```
解决：确保切换到 noVNC 标签页，让 Claude 能"看到"那个页面
```

---

## 📞 测试完告诉我结果！








