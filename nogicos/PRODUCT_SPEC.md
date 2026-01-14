# NogicOS 产品规范

> 本文档定义 NogicOS 的产品定位、架构规范、能力标准。
> 所有开发工作必须符合本规范，不做特供版。

---

## 一、产品定义

### 1.1 一句话

**Workspace AI connects your tabs, files, and apps**

> NogicOS 是一个 Workspace AI，让 AI 能连接你的浏览器标签页、本地文件和应用程序，帮你完成任务。

### 1.2 核心价值

| 维度 | 定义 |
|------|------|
| **品类** | Workspace AI（工作环境 AI）|
| **核心价值** | 连接分散的工作上下文，减少复制粘贴 |
| **差异化** | 浏览器 + 本地文件 + 桌面应用的统一连接 |

### 1.3 市场定位

| 竞品 | 他们做什么 | 我们的差异 |
|------|-----------|-----------|
| **ChatGPT/Claude** | 纯聊天，看不到你的工作环境 | 我们能连接 tabs, files, apps |
| **Cursor** | 代码仓库 AI | 我们面向所有知识工作者 |
| **ramAIn** | 通讯自动化（WhatsApp/Email）| 我们做研究/分析/文档整合 |
| **Zapier/Make** | Workflow automation | 我们是 AI agent，不是 if-then 规则 |

### 1.4 三大核心能力

| 能力 | 说明 | 关键词 |
|------|------|--------|
| **Connecting** | 连接 tabs, files, apps 的统一上下文 | tabs, files, apps |
| **Understanding** | AI 理解你的工作环境，不需要复制粘贴 | context-aware |
| **Acting** | 不只是建议，而是直接执行任务 | direct action |

### 1.5 目标用户

- 产品经理、设计师、分析师、研究员
- 工作信息分散在浏览器、文件、多个应用里
- 希望 AI 自己理解工作上下文，不想反复解释
- 典型任务：竞品分析、市场调研、文档整理、数据整合

### 1.6 不是什么

- ❌ 不是 ChatGPT 的替代品（我们专注于任务执行，不是闲聊）
- ❌ 不是 Cursor 的复制品（我们面向所有人，不只是程序员）
- ❌ 不是 ramAIn 的复制品（他们做通讯，我们做研究/分析）
- ❌ 不是 Zapier（我们是 AI agent，不是 workflow automation）

---

## 二、架构规范

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户                                         │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ 自然语言任务
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Electron Client (前端)                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │    Chat UI      │  │   Status Bar    │  │  Result Panel   │      │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │
│           └────────────────────┼────────────────────┘                │
│                    ┌───────────▼───────────┐                         │
│                    │   WebSocket Client    │                         │
│                    └───────────┬───────────┘                         │
└────────────────────────────────┼────────────────────────────────────┘
                                 │ WS: 8765 / HTTP: 8080
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Python Backend (后端)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                        HiveServer                              │  │
│  │  HTTP API (FastAPI) + WebSocket (broadcast) + Health Monitor  │  │
│  └──────────────────────────────┬────────────────────────────────┘  │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐  │
│  │                      ReAct Agent                              │  │
│  │            Think → Act → Observe → (repeat)                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │  │
│  │  │ ModeRouter  │  │  Planner    │  │Event Handler│           │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘           │  │
│  └──────────────────────────────┬────────────────────────────────┘  │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐  │
│  │                      Tool Registry                            │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │  │
│  │  │ Browser  │ │ Local    │ │ Desktop  │ │ Messaging│         │  │
│  │  │ Tools    │ │ Tools    │ │ Tools    │ │ Tools    │         │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                      │  │
│  │  │ System   │ │ Vision   │ │ Window   │                      │  │
│  │  │ Tools    │ │ Tools    │ │ Tools    │                      │  │
│  │  └──────────┘ └──────────┘ └──────────┘                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐  │
│  │                    Knowledge & Memory                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │  │
│  │  │ Knowledge   │  │ Semantic    │  │ Session     │           │  │
│  │  │ Store       │  │ Memory      │  │ Store       │           │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                 │                                    │
│  ┌──────────────────────────────▼───────────────────────────────┐  │
│  │                    Observability                              │  │
│  │  LangSmith Tracing │ DSPy Optimization │ Prometheus Metrics  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        系统资源层                                    │
│  Playwright (Browser) │ pathlib (Files) │ pyautogui (Desktop)       │
│  pywinauto (Windows)  │ UFO (Desktop AI) │ subprocess (Shell)       │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 文件 | 职责 | 可修改范围 |
|------|------|------|-----------|
| Electron Shell | `client/main.js` | 窗口管理 | UI 配置 |
| React UI | `nogicos-ui/src/` | 用户界面 | 自由修改 |
| HiveServer | `hive_server.py` | 入口路由 | 谨慎修改 |
| ReAct Agent | `engine/agent/react_agent.py` | 核心循环 | 谨慎修改 |
| Mode Router | `engine/agent/modes.py` | 模式路由 | 可扩展 |
| Tool Registry | `engine/tools/base.py` | 工具管理 | 只增不删 |
| Browser Tools | `engine/tools/browser.py` | 浏览器操作 | 可扩展 |
| Playwright Executor | `engine/tools/playwright_executor.py` | CDP 浏览器控制 | 可扩展 |
| Local Tools | `engine/tools/local.py` | 文件操作 | 可扩展 |
| Desktop Tools | `engine/tools/desktop.py` | 桌面自动化 | 可扩展 |
| UFO Executor | `engine/tools/ufo_executor.py` | 桌面 AI 任务 | 可扩展 |
| Messaging Tools | `engine/tools/messaging.py` | 消息发送 | 可扩展 |
| System Tools | `engine/tools/system_tools.py` | 系统级操作 | 可扩展 |
| Knowledge Store | `engine/knowledge/store.py` | 知识存储 | 谨慎修改 |
| Semantic Memory | `engine/knowledge/memory.py` | 语义记忆 | 可扩展 |
| LangSmith Tracer | `engine/observability/` | 可观测性 | 可扩展 |

### 2.3 依赖关系（修改前必读）

```
修改影响范围:
agent/react_agent.py    →  所有任务执行 (高风险)
agent/modes.py          →  模式路由逻辑 (中风险)
tools/playwright_executor.py  →  所有浏览器操作 (高风险)
tools/local.py          →  Agent 文件能力 (中风险)
tools/desktop.py        →  桌面自动化 (中风险)
knowledge/store.py      →  记忆系统 (中风险)
nogicos-ui/             →  用户界面 (低风险)
```

---

## 三、能力标准

### 3.1 必须具备（核心能力）

| 能力 | 实现方式 | 状态 |
|------|----------|------|
| **文件读取** | `read_file` | ✅ 已实现 |
| **文件写入** | `write_file` | ✅ 已实现 |
| **Shell 执行** | `shell_execute` | ✅ 已实现 |
| **文件搜索** | `glob_search` + `grep_search` | ✅ 已实现 |
| **浏览器导航** | `playwright_snapshot` + CDP | ✅ 已实现 |
| **浏览器交互** | `playwright_click/type` | ✅ 已实现 |
| **桌面截图** | `desktop_screenshot` | ✅ 已实现 |
| **桌面自动化** | `pyautogui` + `pywinauto` | ✅ 已实现 |
| **窗口管理** | `list_windows` + `find_window` | ✅ 已实现 |
| **消息发送** | `send_whatsapp` | ✅ 已实现 |
| **流式输出** | WebSocket | ✅ 已实现 |
| **知识存储** | KnowledgeStore | ✅ 已实现 |
| **语义记忆** | SemanticMemorySearch | ✅ 已实现 |
| **LangSmith 追踪** | Observability | ✅ 已实现 |

### 3.2 工具清单

#### Browser Tools（浏览器工具）
| 工具 | 功能 |
|------|------|
| `playwright_snapshot` | 获取页面快照（A11y Tree） |
| `playwright_click` | 点击元素 |
| `playwright_type` | 输入文字 |
| `playwright_evaluate` | 执行 JavaScript |
| `playwright_find_empty_fields` | 查找空表单字段 |
| `playwright_fill_by_label` | 按标签填充字段 |

#### Local Tools（本地工具）
| 工具 | 功能 |
|------|------|
| `read_file` | 读取文件 |
| `write_file` | 写入文件 |
| `append_file` | 追加内容 |
| `list_directory` | 列出目录 |
| `create_directory` | 创建目录 |
| `move_file` | 移动文件 |
| `copy_file` | 复制文件 |
| `delete_file` | 删除文件 |
| `shell_execute` | 执行命令 |
| `glob_search` | 模式搜索 |
| `grep_search` | 内容搜索 |
| `search_replace` | 搜索替换 |
| `path_exists` | 路径检查 |

#### Desktop Tools（桌面工具）
| 工具 | 功能 |
|------|------|
| `desktop_screenshot` | 桌面截图 |
| `desktop_click` | 鼠标点击 |
| `desktop_type` | 键盘输入 |
| `desktop_hotkey` | 快捷键 |
| `list_windows` | 列出窗口 |
| `find_window` | 查找窗口 |
| `focus_window` | 聚焦窗口 |
| `ufo_desktop_task` | UFO 桌面 AI 任务 |

#### Messaging Tools（消息工具）
| 工具 | 功能 |
|------|------|
| `send_whatsapp` | 发送 WhatsApp 消息 |
| `open_whatsapp` | 打开 WhatsApp |

#### System Tools（系统工具）
| 工具 | 功能 |
|------|------|
| `get_system_info` | 获取系统信息 |
| `set_task_status` | 设置任务状态 |
| `request_confirmation` | 请求用户确认 |

### 3.3 工具实现原则

```python
# ✅ 正确：直接调用系统 API
async def read_file(path: str) -> str:
    return Path(path).read_text()

# ❌ 错误：模拟 GUI 操作（除非必要）
async def read_file(path: str) -> str:
    screenshot = take_screenshot()
    return ocr(screenshot)
```

**原则：能用 API 就不用 GUI，能直接调用就不要模拟人类操作。**

---

## 四、质量标准

### 4.1 代码质量

| 指标 | 标准 |
|------|------|
| 单文件行数 | < 500 行（超过需拆分）|
| 函数行数 | < 50 行 |
| 类型注解 | 所有公开函数必须有 |
| 文档字符串 | 所有公开函数必须有 |
| 测试覆盖 | 核心模块 > 80% |

### 4.2 运行时质量

| 指标 | 标准 |
|------|------|
| 首次响应 (TTFT) | < 2s |
| 简单任务完成 | < 30s |
| 复杂任务完成 | < 2min |
| 错误率 | < 10% |
| 内存泄漏 | 无 |

### 4.3 用户体验

| 指标 | 标准 |
|------|------|
| 任务描述 | 用户不需要技术知识 |
| 错误提示 | 人话，不是技术错误 |
| 进度反馈 | 每步都有可见反馈 |
| 可中断 | 用户可随时取消任务 |

---

## 五、配置

### 5.1 核心配置（config.py）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DEFAULT_MODEL` | `claude-opus-4-5-20251101` | 默认 LLM 模型 |
| `LANGSMITH_TRACING` | `true` | LangSmith 追踪 |
| `LANGSMITH_PROJECT` | `nogicos` | LangSmith 项目名 |
| `DSPY_ENABLED` | `true` | DSPy 优化 |
| `HTTP_PORT` | `8080` | HTTP API 端口 |
| `WS_PORT` | `8765` | WebSocket 端口 |
| `BROWSER_HEADLESS` | `false` | 浏览器无头模式 |
| `BROWSER_WIDTH` | `1280` | 浏览器宽度 |
| `BROWSER_HEIGHT` | `720` | 浏览器高度 |

### 5.2 API Keys（api_keys.py）

```python
ANTHROPIC_API_KEY = "sk-ant-..."
LANGSMITH_API_KEY = "lsv2_..."
```

---

## 六、开发流程

### 6.1 Checkpoint 机制（必须遵守）

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Checkpoint 流程                                  │
│                                                                      │
│  [修改前]                                                            │
│  □ 1. 回到 PRODUCT_SPEC.md，确认修改符合规范                         │
│  □ 2. 理解模块依赖关系，评估影响范围                                  │
│  □ 3. 写出预期结果（修改完成后应该是什么样子）                        │
│                                                                      │
│  [修改中]                                                            │
│  □ 4. 小步修改，不要大改                                             │
│  □ 5. 遇到问题停下来思考，不要草率跳过                                │
│                                                                      │
│  [修改后]                                                            │
│  □ 6. 回到 PRODUCT_SPEC.md，检查是否符合规范                         │
│  □ 7. 运行测试验证                                                   │
│  □ 8. 手动测试核心场景                                               │
│  □ 9. 如果不符合规范，立即修正                                        │
│                                                                      │
│  [记录]                                                              │
│  □ 10. 更新 CHANGELOG.md                                            │
│  □ 11. 提交 Git（commit message 说明做了什么）                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 核心场景测试清单

| 场景 | 涉及能力 | 验收标准 |
|------|----------|----------|
| "列出桌面文件" | Local Tools | 返回文件列表 |
| "读取 README.md" | Local Tools | 返回文件内容 |
| "创建 test.txt 写入 hello" | Local Tools | 文件被创建 |
| "打开 google.com" | Browser Tools | 页面被打开 |
| "获取当前页面快照" | Playwright | 返回 A11y Tree |
| "发送 WhatsApp 消息" | Messaging | 消息发送成功 |
| "列出所有窗口" | System Tools | 返回窗口列表 |
| "整理桌面文件" | Local + 分类逻辑 | 文件被移动到分类文件夹 |

---

## 七、版本演进

### 7.1 成熟度模型

| 级别 | 名称 | 标准 |
|------|------|------|
| L1 | Prototype | 核心功能可演示 |
| L2 | Alpha | 端到端流程完整 |
| L3 | Beta | 稳定可日常使用 |
| L4 | Launch | 可交付给用户 |
| L5 | Growth | 用户喜欢并分享 |

### 7.2 当前状态

**L3 Beta**

- ✅ 架构完成
- ✅ Local Tools 全部工作
- ✅ Browser Tools 工作（Playwright Executor）
- ✅ Desktop Tools 工作（pyautogui + pywinauto）
- ✅ Messaging Tools 工作（WhatsApp）
- ✅ Knowledge Store 工作
- ✅ LangSmith 追踪集成
- ✅ DSPy 优化集成
- ⚠️ 多监视器 DPI 兼容性待优化

### 7.3 达到 L4 需要

1. [ ] 用户可零配置安装
2. [ ] 有新手引导
3. [ ] 支持 PDF/Word/Excel
4. [ ] 错误恢复机制
5. [ ] 用户反馈系统

---

## 八、禁止事项

### 8.1 架构禁止

- ❌ 不要把浏览器嵌入 Electron（用 headless Playwright）
- ❌ 不要在前端做业务逻辑（前端只负责展示）
- ❌ 不要硬编码配置（用配置文件）

### 8.2 代码禁止

- ❌ 不要单文件超过 500 行
- ❌ 不要无类型注解的公开函数
- ❌ 不要无测试的核心模块
- ❌ 不要 catch Exception 不处理

### 8.3 产品禁止

- ❌ 不要为特定场景做特供版
- ❌ 不要技术性错误提示
- ❌ 不要无反馈的长等待
- ❌ 不要假设用户懂技术

---

## 九、附录

### 9.1 文件结构

```
nogicos/
├── client/                      # Electron 客户端
│   ├── main.js                 # 主进程
│   └── preload.js              # 预加载脚本
├── nogicos-ui/                  # React 前端
│   └── src/
│       ├── components/         # UI 组件
│       └── hooks/              # 自定义 Hooks
├── engine/                      # Python 后端核心
│   ├── agent/                  # AI Agent
│   │   ├── react_agent.py      # ReAct 循环（核心）
│   │   ├── modes.py            # 模式路由
│   │   ├── planner.py          # 任务分解
│   │   ├── event_bus.py        # 事件总线
│   │   ├── concurrency.py      # 并发处理
│   │   ├── screenshot_manager.py # 截图管理
│   │   └── vision/             # 视觉能力
│   ├── tools/                  # 工具集
│   │   ├── base.py             # 工具注册
│   │   ├── browser.py          # 浏览器工具
│   │   ├── playwright_executor.py # Playwright 执行器
│   │   ├── local.py            # 本地工具
│   │   ├── desktop.py          # 桌面工具
│   │   ├── ufo_executor.py     # UFO 执行器
│   │   ├── messaging.py        # 消息工具
│   │   ├── system_tools.py     # 系统工具
│   │   ├── vision.py           # 视觉工具
│   │   └── window_tools.py     # 窗口工具
│   ├── browser/                # 浏览器管理
│   │   └── session.py          # Session 生命周期
│   ├── knowledge/              # 知识系统
│   │   ├── store.py            # 知识存储
│   │   ├── memory.py           # 语义记忆
│   │   └── search.py           # 语义搜索
│   ├── observability/          # 可观测性
│   │   └── langsmith_tracer.py # LangSmith 集成
│   ├── server/                 # 服务器
│   │   └── websocket.py        # WebSocket
│   └── config.py               # 配置文件
├── tests/                       # 测试
├── hive_server.py               # 入口
├── config.py                    # 全局配置
├── PRODUCT_SPEC.md              # 本文档
├── ARCHITECTURE.md              # 架构详解
├── PITCH_CONTEXT.md             # Pitch 上下文
└── README.md                    # 项目介绍
```

### 9.2 快速命令

```bash
# 启动后端
python hive_server.py

# 启动前端（开发）
cd nogicos-ui && npm run dev

# 启动 Electron
cd client && npm start

# 运行测试
pytest tests/test_agent_core.py -v
```

### 9.3 相关文档

- `README.md` - 项目介绍
- `ARCHITECTURE.md` - 架构详解
- `PITCH_CONTEXT.md` - Pitch 协作上下文
- `docs/yc/NogicOS_YC_Application.md` - YC 申请材料

---

*文档版本: 3.0*
*最后更新: 2026-01-13*
*维护者: Zino + AI*
