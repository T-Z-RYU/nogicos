# NogicOS 参考索引表

> 最后更新: 2025/01/07

---

## 快速检索

当你需要实现某个功能时，先查这个表，找到对应的参考项目和文件。

### 按功能检索

| 功能 | 主要参考 | 参考文档 | 关键代码 | 优先级 |
|------|---------|----------|----------|--------|
| **Agent 循环** | ByteBot | `BYTEBOT_REFERENCE.md` | `runIteration()` | P0 |
| **工具定义** | ByteBot | `BYTEBOT_REFERENCE.md` | `agentTools` | P0 |
| **System Prompt** | ByteBot | `BYTEBOT_REFERENCE.md` | `AGENT_SYSTEM_PROMPT` | P0 |
| **双层 Agent** | UFO | `UFO_REFERENCE.md` | `HostAgent`, `AppAgent` | P0 |
| **状态机** | UFO | `UFO_REFERENCE.md` | `AgentStatus` enum | P1 |
| **工厂模式** | UFO | `UFO_REFERENCE.md` | `AgentFactory` | P1 |
| **MCP 工具注册** | UFO | `UFO_REFERENCE.md` | `_load_mcp_context()` | P1 |
| **采样循环** | Anthropic | `ANTHROPIC_REFERENCE.md` | `sampling_loop()` | P0 |
| **工具结果** | Anthropic | `ANTHROPIC_REFERENCE.md` | `ToolResult` | P0 |
| **坐标缩放** | Anthropic | `ANTHROPIC_REFERENCE.md` | `scale_coordinates()` | P1 |
| **截图机制** | Anthropic | `ANTHROPIC_REFERENCE.md` | `screenshot()` | P1 |
| **工具执行** | ByteBot | `BYTEBOT_REFERENCE.md` | `handleComputerToolUse()` | P0 |
| **任务状态** | ByteBot | `BYTEBOT_REFERENCE.md` | `set_task_status` | P1 |
| **上下文压缩** | ByteBot | `BYTEBOT_REFERENCE.md` | `shouldSummarize` | P2 |
| **黑板通信** | UFO | `UFO_REFERENCE.md` | `Blackboard` | P2 |
| **敏感操作确认** | UFO | `UFO_REFERENCE.md` | `process_confirmation()` | P1 |

---

### 按项目检索

#### ByteBot (最佳 Agent 循环参考)

```
BYTEBOT_REFERENCE.md
├── Agent 主循环     → runIteration()
├── 工具定义        → agentTools (17 个工具)
├── System Prompt   → AGENT_SYSTEM_PROMPT
├── 工具执行        → handleComputerToolUse()
├── 任务状态        → set_task_status tool
└── 上下文压缩      → shouldSummarize
```

**适用场景**: 
- 设计 Agent 主循环
- 定义工具 Schema
- 编写 System Prompt
- 实现工具执行逻辑

---

#### UFO (最佳架构参考)

```
UFO_REFERENCE.md
├── 双层架构        → HostAgent + AppAgent
├── 状态机          → HostAgentStatus, AppAgentStatus
├── 工厂模式        → AgentFactory
├── MCP 集成        → _load_mcp_context()
├── 黑板通信        → Blackboard
└── 敏感操作确认    → process_confirmation()
```

**适用场景**:
- 设计多 Agent 架构
- 实现状态管理
- 集成 MCP 工具
- Agent 间通信

---

#### Anthropic (最佳循环终止参考)

```
ANTHROPIC_REFERENCE.md
├── 采样循环        → sampling_loop()
├── 循环终止        → if not tool_result_content: return
├── 工具结果        → ToolResult dataclass
├── 坐标缩放        → scale_coordinates()
└── 截图机制        → screenshot()
```

**适用场景**:
- 设计循环终止条件
- 定义工具结果格式
- 处理 DPI 缩放
- 实现截图功能

---

#### NogicOS (内部架构参考)

```
NOGICOS_REFERENCE.md
├── 架构总览        → 系统架构图, 数据流向
├── ReAct Agent     → ReActAgent 类, run(), _execute_with_retry()
├── Tool System     → ToolRegistry, @registry.action, execute()
├── Hook System     → HookManager, DesktopHook, get_all_windows()
├── Context Store   → ContextStore, format_context_prompt()
├── Electron Client → main.js, preload.js, multi-overlay-manager.js
└── 适配指南        → 添加工具/Hook, 扩展 Agent
```

**适用场景**:
- 理解 NogicOS 现有架构
- 在现有代码基础上扩展
- 避免与现有实现冲突
- 新功能开发参考

---

## 实现对照表

### NogicOS vs 参考项目

| NogicOS 需求 | ByteBot | UFO | Anthropic | NogicOS 现状 |
|-------------|---------|-----|-----------|-------------|
| Agent 主循环 | runIteration() | process() | sampling_loop() | `ReActAgent.run()` |
| 工具定义 | agentTools | MCP tools | ComputerTool | `@registry.action` |
| 窗口控制 | N/A (全局) | UIA (全局) | xdotool (全局) | `DesktopHook` |
| 窗口隔离 | N/A | N/A | N/A | `multi-overlay-manager.js` |
| 多窗口支持 | N/A | 多 AppAgent | N/A | `Map<hwnd, OverlayInstance>` |
| 截图 | screenshot() | screenshot() | screenshot() | `vision.py` |
| DPI 缩放 | N/A | 部分 | scale_coordinates() | `screen.screenToDipRect` |
| 状态机 | TaskStatus | AgentStatus | N/A | `HookStatus` enum |
| 用户确认 | N/A | process_confirmation() | N/A | 待实现 |

---

## 使用指南

### 开发前必读

在开发以下功能前，**必须**先读对应的参考文档：

1. **开发 Agent 循环** → 先读 `BYTEBOT_REFERENCE.md` 的 `runIteration()`
2. **定义工具** → 先读 `BYTEBOT_REFERENCE.md` 的 `agentTools`
3. **设计架构** → 先读 `UFO_REFERENCE.md` 的双层架构
4. **处理截图** → 先读 `ANTHROPIC_REFERENCE.md` 的 `screenshot()`

### 代码对照

写完代码后，用以下命令对照检查：

```
对照 ByteBot 的 [具体模块] 检查一下这个实现是否合理
```

### 参考驱动开发流程

```
1. 查索引 → 找到功能对应的参考项目
2. 读参考文档 → 理解参考实现
3. 写代码 → 基于参考实现
4. 对照检查 → 确保没有遗漏
```

---

## 常见问题

### Q: 如何实现窗口隔离？

三个参考项目都没有窗口隔离能力。NogicOS 需要**自行实现**：
- 使用 `PostMessage` 代替 `SendInput`
- 使用窗口截图代替全屏截图
- 在工具参数中添加 `hwnd`

### Q: 如何处理 DPI 缩放？

参考 `ANTHROPIC_REFERENCE.md` 的 `scale_coordinates()`，但需要改为窗口级别：
- 获取窗口实际大小
- 计算与目标大小的比例
- 转换坐标

### Q: 如何设计多 Agent 协作？

参考 `UFO_REFERENCE.md` 的 HostAgent + AppAgent 架构：
- HostAgent 负责任务分发
- AppAgent 负责具体执行
- 使用 Blackboard 通信

---

## 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2025/01/07 | 创建初始版本，包含 ByteBot、UFO、Anthropic 三个项目的参考 |
| 2025/01/07 | 添加 NogicOS 内部架构参考 (NOGICOS_REFERENCE.md) |