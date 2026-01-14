# NogicOS Hook 系统技术规范

> 版本: 1.0  
> 更新日期: 2026-01-05  
> 状态: **已实现**

---

## 一、概述

Hook 系统是 NogicOS 的核心差异化功能，实现"The AI that works where you work"的核心价值主张。

### 1.1 设计目标

- **用户主动选择**：Hook 不是自动开启，用户选择"连接"哪个应用
- **双向状态反馈**：NogicOS 内 + 被 hook 应用都有视觉指示
- **Hook 与执行解耦**：Hook 常驻运行，与任务执行无关
- **通用感知架构**：不依赖插件，对任何应用都能工作

### 1.2 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| Browser Hook | ✅ | 窗口检测 + 标题解析 + OCR URL 提取 |
| Desktop Hook | ✅ | 活跃窗口 + 窗口列表 |
| File Hook | ✅ | 目录监听 + 剪贴板 + 最近文件 |
| Context Store | ✅ | 内存状态 + SQLite 历史 |
| Hook Manager | ✅ | 生命周期管理 + 状态同步 |
| Agent 集成 | ✅ | 自动上下文注入 |
| 前端 UI | ✅ | ConnectorPanel 组件 |
| Overlay | ✅ | Electron 透明窗口（需 ffi-napi） |

---

## 二、架构

```
┌─────────────────────────────────────────────────────────────┐
│                      NogicOS 前端                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ConnectorPanel                           │  │
│  │  [Browser: Connected]  [Desktop: -]  [Files: -]      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP API
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Hook Manager                              │
│  ┌──────────────┬──────────────┬────────────────────────┐  │
│  │ BrowserHook  │ DesktopHook  │ FileHook               │  │
│  │ - 窗口检测   │ - 活跃窗口   │ - 目录监听            │  │
│  │ - 标题解析   │ - 窗口列表   │ - 剪贴板              │  │
│  │ - OCR URL    │              │ - 最近文件            │  │
│  └──────────────┴──────────────┴────────────────────────┘  │
│                             │                                │
│                             ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Context Store                            │  │
│  │  - 当前状态（内存）                                   │  │
│  │  - 历史记录（SQLite）                                 │  │
│  │  - format_context_prompt() → Agent                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     ReAct Agent                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ System Prompt + Hook Context + User Message          │  │
│  │                                                      │  │
│  │ "[Current Context - NogicOS is aware of:]            │  │
│  │  ## Browser (Chrome)                                 │  │
│  │  - Active URL: https://ycombinator.com               │  │
│  │  - Page Title: Y Combinator                          │  │
│  │  ..."                                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、API 接口

### 3.1 获取 Hook 状态

```
GET /api/hooks/status
```

返回：
```json
{
  "hooks": {
    "browser": {
      "type": "browser",
      "status": "connected",
      "target": "chrome",
      "context": {
        "app": "Chrome",
        "url": "https://ycombinator.com",
        "title": "Y Combinator",
        "tab_count": 5
      },
      "connected_at": "2026-01-05T10:00:00"
    }
  },
  "available_types": ["browser", "desktop", "file"]
}
```

### 3.2 连接 Hook

```
POST /api/hooks/connect
Content-Type: application/json

{
  "type": "browser",
  "target": ""  // 可选，如 "chrome"、目录路径等
}
```

### 3.3 断开 Hook

```
POST /api/hooks/disconnect/{hook_id}
```

### 3.4 获取上下文

```
GET /api/hooks/context
```

返回：
```json
{
  "context": {
    "connected_hooks": ["browser"],
    "browser": {
      "app": "Chrome",
      "url": "https://...",
      "title": "...",
      "tabs": [...]
    }
  },
  "prompt": "[Current Context - NogicOS is aware of...]"
}
```

---

## 四、文件结构

```
nogicos/
├── engine/
│   └── context/
│       ├── __init__.py          # 模块导出
│       ├── store.py             # Context Store
│       ├── hook_manager.py      # Hook Manager
│       └── hooks/
│           ├── __init__.py
│           ├── base_hook.py     # Hook 基类
│           ├── browser_hook.py  # 浏览器 Hook
│           ├── desktop_hook.py  # 桌面 Hook
│           ├── file_hook.py     # 文件 Hook
│           ├── ocr_utils.py     # OCR 工具
│           └── screenshot_utils.py  # 截图工具
├── client/
│   ├── main.js                  # Electron 主进程（已集成 Overlay）
│   └── overlay.js               # Overlay 管理器
├── nogicos-ui/
│   └── src/
│       └── components/
│           └── nogicos/
│               └── ConnectorPanel.tsx  # 前端连接器面板
└── hive_server.py              # API 端点（已集成 Hook API）
```

---

## 五、使用示例

### 5.1 Python 后端

```python
from engine.context import get_hook_manager, get_context_store

# 获取 Hook Manager
manager = await get_hook_manager()

# 连接浏览器
await manager.connect_browser()

# 获取上下文
context = await manager.get_browser_context()
print(f"当前 URL: {context.url}")

# 获取 Agent 可用的上下文
store = get_context_store()
prompt = store.format_context_prompt()
# 注入到 Agent 的 system prompt
```

### 5.2 前端

```tsx
import { ConnectorPanel } from '@/components/nogicos';

function App() {
  return (
    <Sidebar>
      <ConnectorPanel defaultExpanded={true} />
    </Sidebar>
  );
}
```

---

## 六、测试验证

运行测试：
```bash
cd nogicos
python test_hook_system.py
```

期望输出：
```
============================================================
Test Summary
============================================================
  [PASS] Browser Hook
  [PASS] Desktop Hook
  [PASS] File Hook
  [PASS] Context Store
  [PASS] Hook Manager
  [PASS] Screenshot OCR
------------------------------------------------------------
  Total: 6 passed, 0 failed
============================================================
```

---

## 七、后续优化

### 7.1 短期
- [ ] 安装 pytesseract 启用 OCR URL 提取
- [ ] 安装 ffi-napi 启用 Overlay 功能
- [ ] 在 Sidebar 中集成 ConnectorPanel

### 7.2 中期
- [ ] Vision API 集成（Claude Vision 分析截图）
- [ ] 多浏览器支持优化
- [ ] 多显示器支持

### 7.3 长期
- [ ] 应用级 Hook（VS Code、Office 等）
- [ ] 智能上下文过滤
- [ ] 历史上下文搜索

---

## 八、依赖

### 必需
- Python 3.9+
- Windows 10/11（部分功能仅 Windows）

### 可选（增强功能）
- `mss`：截图功能
- `pillow`：图像处理
- `pytesseract` + Tesseract-OCR：OCR 功能
- `watchdog`：文件监听
- `ffi-napi`（Node.js）：Overlay 窗口跟踪

安装可选依赖：
```bash
pip install mss pillow pytesseract watchdog
```

