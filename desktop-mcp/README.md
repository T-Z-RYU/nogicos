# Desktop MCP Server

让 Cursor 能操作 Windows 桌面应用的 MCP Server。

## 安装

```bash
cd desktop-mcp
pip install -r requirements.txt
```

## 配置 Cursor

编辑 `%APPDATA%\Cursor\User\globalStorage\cursor.mcp\mcp.json`：

```json
{
  "mcpServers": {
    "desktop": {
      "command": "python",
      "args": ["C:\\Users\\TE\\532-CorporateHell-Git\\nogicos\\desktop-mcp\\server.py"]
    }
  }
}
```

## 可用工具

| 工具 | 描述 |
|------|------|
| `desktop_screenshot` | 截取屏幕截图 |
| `desktop_click` | 在指定坐标点击 |
| `desktop_type` | 输入文字 |
| `desktop_hotkey` | 按下组合键 |
| `desktop_open_app` | 通过开始菜单打开应用 |
| `desktop_list_windows` | 列出所有窗口 |
| `desktop_focus_window` | 聚焦指定窗口 |
| `desktop_window_click` | 点击窗口中的控件 |
| `desktop_window_type` | 在窗口输入框中输入 |

## 使用示例

在 Cursor 中：

```
"打开 WhatsApp 并发送消息给 John"
```

Cursor 会依次调用：
1. `desktop_open_app("WhatsApp")`
2. `desktop_screenshot()` - 查看当前屏幕
3. `desktop_click(x, y)` - 点击搜索框
4. `desktop_type("John")` - 输入名字
5. ...

## 注意事项

1. **安全模式**：鼠标移到屏幕左上角可中断操作
2. **中文输入**：自动使用剪贴板粘贴
3. **权限**：需要管理员权限操作某些应用
