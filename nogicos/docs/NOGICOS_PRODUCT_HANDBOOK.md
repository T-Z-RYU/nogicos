# NogicOS 产品手册

> **版本**: 1.0.0  
> **更新日期**: 2026-01-09  
> **维护者**: NogicOS Team

---

## 目录

1. [产品定位](#1-产品定位)
2. [核心差异化](#2-核心差异化)
3. [系统架构](#3-系统架构)
4. [Hook 系统](#4-hook-系统)
5. [Agent 系统](#5-agent-系统)
6. [工具能力](#6-工具能力)
7. [前端架构](#7-前端架构)
8. [Living Canvas](#8-living-canvas)
9. [API 接口](#9-api-接口)
10. [部署与运行](#10-部署与运行)
11. [典型场景](#11-典型场景)
12. [路线图](#12-路线图)

---

## 1. 产品定位

### 1.1 一句话定位

> **"NogicOS: The AI that works where you work"**  
> 在你工作的地方工作的 AI

### 1.2 核心问题

知识工作者（PM、分析师、研究员）的工作分散在浏览器、本地文件、各种应用里。现有 AI 只能看到一个窗口，用户需要不断复制粘贴上下文。

**这不是 AI 能力的问题，是上下文获取的问题。**

### 1.3 解决方案

NogicOS 是**第一个能同时看到浏览器、文件和桌面的 AI**。它不只是聊天，它能直接在你的工作环境里行动。

### 1.4 目标用户

| 用户类型 | 典型任务 |
|----------|----------|
| **产品经理** | 竞品分析、用户研究、文档整理 |
| **分析师** | 数据提取、报告生成、信息汇总 |
| **研究员** | 文献管理、笔记整理、资料收集 |
| **创业者** | 市场调研、申请材料准备 |

### 1.5 不是什么

- ❌ 不是 ChatGPT 替代品（专注任务执行，不是闲聊）
- ❌ 不是 Cursor 复制品（面向所有人，不只是程序员）
- ❌ 不是浏览器自动化工具（浏览器只是能力之一）

---

## 2. 核心差异化

### 2.1 三大卖点

| 卖点 | 说明 | 实现方式 |
|------|------|----------|
| **Complete Context** | 完整上下文 | 浏览器 + 本地文件 + 桌面应用 |
| **Direct Action** | 直接行动 | 不只建议，而是直接执行 |
| **Local-First** | 本地优先 | 数据不上传云端，隐私保护 |

### 2.2 竞品对比

| AI 产品 | 能看到什么 | 不能看到什么 |
|---------|-----------|-------------|
| ChatGPT | 你贴进去的文字 | 你的文件、你的浏览器 |
| Claude | 你上传的文件 | 你的工作流、你的屏幕 |
| Cursor | 你的代码仓库 | 你的浏览器、你的设计文件 |
| **NogicOS** | **浏览器 + 文件 + 桌面** | **（完整上下文）** |

### 2.3 市场验证

**YC 2024-2026 数据分析（1,265 家公司）：**
- AI Agent 公司占比已超过 51%
- 同时具备「浏览器+本地+学习」能力的只有 19 家（1.5%）
- 「本地优先/隐私」定位只有 17 家 → **稀缺赛道**

---

## 3. 系统架构

### 3.1 总体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户                                         │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ 自然语言任务
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Electron Client (前端)                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │    Chat UI      │  │   Hook System   │  │  Overlay Layer  │      │
│  │ (Living Canvas) │  │   (Connector)   │  │   (Indicators)  │      │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │
│           └────────────────────┼────────────────────┘                │
│                    ┌───────────▼───────────┐                         │
│                    │   IPC + WebSocket     │                         │
│                    └───────────┬───────────┘                         │
└────────────────────────────────┼────────────────────────────────────┘
                                 │ WS: 8765 / HTTP: 8080
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Python Backend (后端)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                        HiveServer                              │  │
│  │  HTTP API (FastAPI) + WebSocket + Hook Manager + Health       │  │
│  └──────────────────────────────┬────────────────────────────────┘  │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐  │
│  │                      ReAct Agent                              │  │
│  │            Think → Act → Observe → (repeat)                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │  │
│  │  │ Classifier  │  │  Planner    │  │Error Handler│           │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘           │  │
│  └──────────────────────────────┬────────────────────────────────┘  │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐  │
│  │                      Tool Registry                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │  │
│  │  │ Browser     │  │ Local       │  │ Desktop     │           │  │
│  │  │ Tools       │  │ Tools       │  │ Tools       │           │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐  │
│  │                    Knowledge Store                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │  │
│  │  │ Semantic    │  │ Session     │  │ Trajectory  │           │  │
│  │  │ Memory      │  │ History     │  │ Cache       │           │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        系统资源层                                    │
│  Playwright (Browser) │ pathlib (Files) │ Win32 API (Desktop)      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 模块职责

| 模块 | 文件位置 | 职责 |
|------|----------|------|
| Electron Shell | `client/main.js` | 窗口管理、IPC 通信 |
| React UI | `nogicos-ui/src/` | 用户界面 |
| HiveServer | `hive_server.py` | 入口路由、API 网关 |
| ReAct Agent | `engine/agent/react_agent.py` | AI 核心循环 |
| Tool Registry | `engine/tools/` | 工具管理与执行 |
| Knowledge Store | `engine/knowledge/` | 持久化存储 |

### 3.3 文件结构

```
nogicos/
├── client/                    # Electron 客户端
│   ├── main.js               # 主进程入口
│   ├── preload.js            # 预加载脚本
│   └── multi-overlay-manager.js  # Overlay 管理
├── nogicos-ui/               # React 前端
│   └── src/
│       ├── components/
│       │   ├── nogicos/      # NogicOS 核心组件
│       │   │   ├── LivingCanvasChat.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   └── ConnectorPanel.tsx
│       │   └── chat/         # 聊天组件
│       └── hooks/            # 自定义 Hooks
├── engine/                   # Python 后端核心
│   ├── agent/               # AI Agent
│   │   ├── react_agent.py   # ReAct 循环
│   │   ├── classifier.py    # 任务分类
│   │   └── planner.py       # 任务分解
│   ├── tools/               # 工具集
│   │   ├── base.py          # 工具基类
│   │   ├── browser.py       # 浏览器工具
│   │   ├── local.py         # 本地文件工具
│   │   └── desktop.py       # 桌面工具
│   ├── browser/             # 浏览器管理
│   │   └── session.py       # Playwright 会话
│   └── knowledge/           # 知识存储
│       ├── store.py         # 存储接口
│       └── models.py        # 数据模型
├── tests/                   # 测试
├── hive_server.py           # 服务器入口
└── docs/                    # 文档
```

---

## 4. Hook 系统

### 4.1 概述

Hook 系统是 NogicOS 的核心差异化能力，允许 AI "连接"到用户的其他应用程序，获取完整的工作上下文。

### 4.2 连接流程

```
┌──────────────────────────────────────────────────────────────┐
│                     Hook 连接流程                             │
│                                                              │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐              │
│  │ NogicOS │─────▶│  Hook   │─────▶│ 目标App │              │
│  │   UI    │      │ Manager │      │ (Chrome) │              │
│  └─────────┘      └─────────┘      └─────────┘              │
│       │                │                 │                   │
│       │ 1. 用户拖拽    │                 │                   │
│       │────────────▶   │                 │                   │
│       │                │ 2. 获取 HWND    │                   │
│       │                │────────────────▶│                   │
│       │                │                 │                   │
│       │                │ 3. 创建 Overlay │                   │
│       │                │◀────────────────│                   │
│       │                │                 │                   │
│       │ 4. 连接成功    │                 │                   │
│       │◀───────────────│                 │                   │
│       │                │                 │                   │
│       │ 5. 实时数据流  │                 │                   │
│       │◀═══════════════│◀════════════════│                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 数据模型

```typescript
interface ConnectedApp {
  hwnd: number;              // Windows 窗口句柄
  title: string;             // 窗口标题
  app_name: string;          // 进程名（如 "chrome.exe"）
  app_display_name: string;  // 显示名（如 "Google Chrome"）
  is_browser: boolean;       // 是否是浏览器
  connected_at: string;      // 连接时间 ISO 字符串
}
```

### 4.4 Overlay 系统

连接成功后，目标应用窗口会显示一个 Overlay 指示器：

```
┌────────────────────────────────────────────────┐
│  目标应用窗口（如 Chrome）                       │
│                                                │
│                                                │
│                              ╭───────────────╮ │
│                              │ ● NogicOS     │ │
│                              │   Connected   │ │
│                              ╰───────────────╯ │
│                                                │
└────────────────────────────────────────────────┘
```

**Overlay 特性**：
- 翠绿色主题（`#10b981`）
- 扫描线动画
- 实时状态更新（Reading / Writing / Idle）
- 不阻挡用户操作（`pointer-events: none`）

---

## 5. Agent 系统

### 5.1 ReAct 循环

NogicOS 使用 ReAct（Reasoning + Acting）架构：

```
┌─────────────────────────────────────────────────────────────┐
│                     ReAct Agent 循环                         │
│                                                             │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐             │
│  │ Observe │─────▶│  Think  │─────▶│   Act   │             │
│  │  观察   │      │  思考   │      │  行动   │             │
│  └────▲────┘      └─────────┘      └────┬────┘             │
│       │                                  │                  │
│       │          Result/Error            │                  │
│       └──────────────────────────────────┘                  │
│                                                             │
│  重复直到：                                                  │
│  - 任务完成 (success)                                       │
│  - 达到最大迭代 (max_iterations)                            │
│  - 遇到不可恢复错误 (fatal_error)                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 任务分类

Agent 首先对用户任务进行分类：

| 分类 | 说明 | 示例 |
|------|------|------|
| `browser` | 需要浏览器操作 | "打开 Google" |
| `local` | 只需本地文件 | "列出桌面文件" |
| `mixed` | 混合操作 | "把网页数据存到 Excel" |
| `chat` | 纯对话 | "你好" |

### 5.3 System Prompt 结构

```python
SYSTEM_PROMPT = """
你是 NogicOS，一个能看到用户完整工作环境的 AI 助手。

## 你的能力
1. 浏览器操作：打开网页、点击、输入、截图、提取内容
2. 本地文件：读写文件、搜索、创建文件夹
3. 桌面感知：截屏、理解屏幕状态

## 当前连接的应用
{connected_apps}

## 上下文感知（重要！）
当你操作多个应用时，明确说明你在做什么：
- "我正在从 Chrome 读取数据..."
- "我现在切换到 Excel 写入..."
- "我看到 Chrome 显示的是..."

## 输出格式
使用 ReAct 格式：
Thought: [你的思考]
Action: [工具名称]
Action Input: [工具参数 JSON]
"""
```

### 5.4 Trajectory 学习

Agent 会保存成功执行的轨迹，用于加速类似任务：

```python
@dataclass
class Trajectory:
    id: str
    task: str                    # 任务描述
    tools_used: List[str]        # 使用的工具
    success: bool                # 是否成功
    duration_ms: float           # 执行时长
    iterations: int              # 迭代次数
    error_message: Optional[str] # 错误信息
    created_at: datetime         # 创建时间
```

---

## 6. 工具能力

### 6.1 Browser Tools

| 工具 | 功能 | 参数 |
|------|------|------|
| `browser_navigate` | 打开 URL | `url: str` |
| `browser_click` | 点击元素 | `selector: str` |
| `browser_type` | 输入文字 | `selector: str, text: str` |
| `browser_screenshot` | 截图 | `full_page: bool` |
| `browser_extract` | 提取内容 | `selector: str` |
| `browser_snapshot` | A11y 快照 | - |

### 6.2 Local Tools

| 工具 | 功能 | 参数 |
|------|------|------|
| `read_file` | 读取文件 | `path: str` |
| `write_file` | 写入文件 | `path: str, content: str` |
| `list_directory` | 列出目录 | `path: str` |
| `search_files` | 搜索文件 | `pattern: str, path: str` |
| `create_directory` | 创建目录 | `path: str` |
| `execute_command` | 执行命令 | `command: str` |

### 6.3 Desktop Tools

| 工具 | 功能 | 参数 |
|------|------|------|
| `desktop_screenshot` | 桌面截图 | - |
| `get_active_window` | 获取当前窗口 | - |
| `list_windows` | 列出所有窗口 | - |
| `focus_window` | 聚焦窗口 | `hwnd: int` |

---

## 7. 前端架构

### 7.1 技术栈

| 技术 | 用途 |
|------|------|
| **Electron** | 桌面应用容器 |
| **React 18** | UI 框架 |
| **TypeScript** | 类型安全 |
| **Tailwind CSS** | 样式系统 |
| **Motion for React** | 动画库 |
| **Vercel AI SDK** | AI 聊天 |

### 7.2 组件结构

```
App.tsx
├── Header                     # 顶栏（标题、控制按钮）
├── Sidebar                    # 侧边栏
│   ├── SessionList           # 会话列表
│   ├── HookMapButton         # Hook Map 入口
│   └── ConnectorPanel        # 应用连接器
└── LivingCanvasChat          # 主对话区（Living Canvas）
    ├── NeuralBackground      # 神经网络背景
    ├── MessageArea           # 消息区域
    └── InputArea             # 输入区域
```

### 7.3 状态管理

```typescript
// App.tsx 核心状态
const [sessions, setSessions] = useState<Session[]>([]);
const [activeSessionId, setActiveSessionId] = useState<string>();
const [connectedApps, setConnectedApps] = useState<ConnectedApp[]>([]);
const [chatSessions, setChatSessions] = useState<Record<string, Message[]>>({});
```

---

## 8. Living Canvas

### 8.1 概述

Living Canvas 是 NogicOS 的核心交互界面，将 **Hook Map（神经网络可视化）** 与 **对话界面** 融为一体。

### 8.2 三层结构

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           神经网络层 (Neural Background)             │   │
│  │                    固定高度 240px                    │   │
│  │     [App] ─────────── [AI] ─────────── [App]        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              对话层 (Content Layer)                  │   │
│  │                    flex-1 滚动                       │   │
│  │     ╭────────────────────────────────────────╮      │   │
│  │     │ User: 帮我填写这个表单                  │      │   │
│  │     ╰────────────────────────────────────────╯      │   │
│  │     ╭────────────────────────────────────────╮      │   │
│  │     │ AI: 好的，我来帮你...                   │      │   │
│  │     ╰────────────────────────────────────────╯      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              控制层 (Control Layer)                  │   │
│  │         状态条 + 输入框 + 发送按钮                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 AI 状态

| 状态 | 颜色 | 图标 | 触发条件 |
|------|------|------|----------|
| `idle` | 翠绿 #10b981 | ⚡ Zap | 默认状态 |
| `reading` | 天蓝 #0ea5e9 | 👁 Eye | 读取数据 |
| `thinking` | 紫色 #8b5cf6 | 🧠 Brain | 生成回复 |
| `acting` | 琥珀 #f59e0b | ✏️ Pencil | 执行工具 |
| `success` | 翠绿 #10b981 | ✨ Sparkles | 任务完成 |

### 8.4 视觉规范

**颜色系统**：
```css
--emerald-primary: #10b981;
--emerald-light: #34d399;
--emerald-glow: rgba(16, 185, 129, 0.3);
--background: #0a0a0a;
--card: #111111;
--border: rgba(255, 255, 255, 0.06);
```

**动画配置**：
```typescript
const SPRING = {
  gentle: { type: 'spring', stiffness: 120, damping: 14 },
  snappy: { type: 'spring', stiffness: 400, damping: 25 },
};
```

---

## 9. API 接口

### 9.1 HTTP 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/execute` | POST | 执行 AI 任务 |
| `/api/chat` | POST | Vercel AI SDK 聊天流 |
| `/v2/sessions` | GET | 获取所有会话 |
| `/v2/sessions/:id` | GET/POST/DELETE | 会话 CRUD |
| `/api/hooks` | GET | 获取已连接应用 |
| `/api/hooks` | POST | 连接新应用 |
| `/api/hooks/:hwnd` | DELETE | 断开连接 |

### 9.2 WebSocket 消息

```typescript
// 客户端 → 服务端
{ type: 'execute', task: string, sessionId: string }
{ type: 'stop', sessionId: string }

// 服务端 → 客户端
{ type: 'agent_thought', content: string }
{ type: 'agent_action', tool: string, input: object }
{ type: 'tool_output', result: string }
{ type: 'agent_complete', result: string }
{ type: 'agent_error', error: string }
```

### 9.3 示例请求

```bash
# 执行任务
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "列出桌面文件", "session_id": "abc123"}'

# 获取已连接应用
curl http://localhost:8080/api/hooks
```

---

## 10. 部署与运行

### 10.1 环境要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 后端运行时 |
| Node.js | 18+ | 前端构建 |
| Chrome | 最新 | CDP 浏览器 |
| Windows | 10/11 | 桌面 API |

### 10.2 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/yourname/nogicos.git
cd nogicos/nogicos

# 2. 安装后端依赖
pip install -r requirements.txt
playwright install chromium

# 3. 安装前端依赖
cd nogicos-ui && npm install
cd ../client && npm install

# 4. 配置 API Keys
cp api_keys.example.py api_keys.py
# 编辑 api_keys.py 填入你的 Anthropic API Key
```

### 10.3 启动服务

```powershell
# 终端 1: 启动后端
cd nogicos
python hive_server.py

# 终端 2: 启动前端开发服务器
cd nogicos/nogicos-ui
npm run dev

# 终端 3: 启动 Electron（可选）
cd nogicos/client
npm start
```

### 10.4 端口配置

| 服务 | 端口 | 说明 |
|------|------|------|
| HTTP API | 8080 | FastAPI 服务 |
| WebSocket | 8765 | 实时通信 |
| 前端开发 | 5173 | Vite 开发服务器 |
| Chrome CDP | 9222 | 浏览器调试协议 |

---

## 11. 典型场景

### 场景 1: 竞品分析

> 用户: "帮我分析 Notion AI 的功能"

```
Agent 执行流程:
1. browser_navigate → notion.so/product/ai
2. browser_screenshot → 保存功能截图
3. browser_extract → 提取功能列表
4. read_file → 读取本地产品文档
5. LLM → 生成对比分析报告
6. write_file → 保存报告
```

### 场景 2: YC 申请表填写

> 用户: "帮我填写 YC 申请表"

```
Agent 执行流程:
1. read_file → 读取 PITCH_CONTEXT.md
2. browser_navigate → apply.ycombinator.com
3. browser_snapshot → 获取表单结构
4. LLM → 根据文档生成答案
5. browser_type → 填写表单字段
6. browser_screenshot → 截图确认
```

### 场景 3: 数据整合

> 用户: "把这个网页的表格数据整理到 Excel"

```
Agent 执行流程:
1. browser_snapshot → 获取页面结构
2. browser_extract → 提取表格数据
3. LLM → 整理为结构化格式
4. write_file → 生成 CSV/Excel 文件
```

---

## 12. 路线图

### 当前版本: L2.5 (Alpha+)

- ✅ 核心架构完成
- ✅ Local Tools 工作
- ✅ Browser Tools 工作
- ✅ Living Canvas UI
- ✅ Hook 系统
- ⚠️ 稳定性待验证

### L3 目标 (Beta)

- [ ] 所有核心场景 100% 通过
- [ ] 无内存泄漏
- [ ] 错误友好提示
- [ ] 首次响应 < 2s

### L4 目标 (Launch)

- [ ] 零配置安装
- [ ] 新手引导
- [ ] PDF/Word/Excel 支持
- [ ] 项目索引功能

### L5 目标 (Growth)

- [ ] 插件系统
- [ ] 多 Agent 协作
- [ ] 工作流模板
- [ ] 社区生态

---

## 附录

### A. 快捷命令

```bash
# 启动全部服务
cd nogicos && python hive_server.py &
cd nogicos/nogicos-ui && npm run dev

# 运行测试
pytest tests/test_agent_core.py -v

# 构建生产版本
cd nogicos-ui && npm run build
cd client && npm run package
```

### B. 常见问题

**Q: Chrome CDP 连接失败？**
A: 确保以 `--remote-debugging-port=9222` 启动 Chrome

**Q: 后端启动报错 port in use？**
A: 运行 `netstat -ano | findstr :8080` 找到占用进程并结束

**Q: 前端组件不更新？**
A: 尝试 `npm run dev -- --force` 清除缓存

### C. 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 产品上下文 | `PITCH_CONTEXT.md` | 核心叙事 |
| 产品规范 | `PRODUCT_SPEC.md` | 开发规范 |
| 架构说明 | `ARCHITECTURE.md` | 技术架构 |
| Living Canvas | `nogicos-ui/docs/LIVING_CANVAS_SPEC.md` | UI 规范 |

---

*NogicOS - The AI that works where you work*

**文档版本**: 1.0.0  
**最后更新**: 2026-01-09  
**维护者**: NogicOS Team
