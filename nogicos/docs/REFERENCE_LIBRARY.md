# NogicOS 开源项目参考库

> 📚 这是我们通过深度学习顶级开源项目积累的知识库
> 
> **用途**：开发时参考最佳实践，避免重复造轮子
> 
> **更新时间**：2025-12-27

---

## 📊 项目索引

| 项目 | Stars | 类型 | 学习状态 |
|------|-------|------|----------|
| [browser-use](https://github.com/browser-use/browser-use) | 56K+ | Python AI Agent | 🔄 进行中 |
| [Stagehand](https://github.com/browserbase/stagehand) | 10K+ | TypeScript Agent | ⏳ 待学习 |
| [Zen Browser](https://github.com/AuroraHQ/zen-browser) | 20K+ | Firefox Fork | ⏳ 待学习 |
| [LaVague](https://github.com/lavague-ai/LaVague) | 8K+ | Python Web Agent | ⏳ 待学习 |

---

# 🤖 browser-use (56K+ Stars)

> 最成功的开源 AI 浏览器 Agent 项目

## 1. 项目架构

```
browser_use/
├── agent/           # AI Agent 核心
│   ├── service.py   # Agent 主循环
│   ├── views.py     # 数据结构
│   ├── prompts.py   # 提示词工具
│   └── system_prompts/
│       └── system_prompt.md  # 核心系统提示词
├── browser/         # 浏览器会话管理
│   ├── session.py   # 浏览器会话
│   ├── profile.py   # 用户配置管理
│   └── events.py    # 事件系统
├── dom/             # DOM 处理
│   ├── service.py   # DOM 服务
│   ├── views.py     # DOM 视图
│   └── serializer/  # 序列化器
├── tools/           # 动作/工具系统
│   ├── service.py   # 工具服务
│   └── registry/    # 工具注册
└── llm/             # LLM 集成
    ├── base.py      # 基础抽象
    └── schema.py    # 数据模型
```

## 2. Agent 系统核心

### 2.1 Agent 主循环 (service.py)

```python
# 核心运行流程
async def run(self, starting_url=None):
    # 1. 初始化浏览器会话
    # 2. 循环执行步骤
    while not done:
        # a) 获取浏览器状态 (DOM + 截图)
        state = await self._get_browser_state()
        
        # b) 发送给 LLM 获取下一步动作
        action = await self._get_next_action(state)
        
        # c) 执行动作
        result = await self._execute_action(action)
        
        # d) 更新历史
        self._update_history(result)
```

### 2.2 消息管理系统

**关键设计**：Token 优化
```python
# 当 Token 超限时，压缩历史
if tokens > max_tokens:
    # 1. 先尝试移除图片
    # 2. 再删除中间历史，只保留首尾
    # 3. 标注压缩（告知 AI 内容被压缩）
```

### 2.3 步骤产物 (AgentStepInfo)

```python
@dataclass
class AgentStepInfo:
    step_number: int
    max_steps: int
    task: str
    add_infos: str
    memory: str           # AI 的记忆
    task_progress: str    # 任务进度
```

## 3. 系统提示词设计

### 3.1 输入结构
```markdown
<agent_history>历史记录</agent_history>
<agent_state>当前状态</agent_state>
<browser_state>浏览器状态</browser_state>
<browser_vision>[截图]</browser_vision>
```

### 3.2 输出格式（强制推理）
```json
{
  "thinking": "当前情况分析...",
  "evaluation_previous_goal": "上一步评估 (success/failed/unknown)",
  "memory": "需要记住的信息",
  "next_goal": "下一步目标",
  "action": [{"type": "click", "index": 5}]
}
```

### 3.3 关键规则
1. **只与带 [index] 的元素交互** - 防止幻觉
2. **研究用新标签，保留原标签** - 方便回退
3. **允许多动作组合** - 提高效率 (如 input + click)
4. **持久化文件** - `todo.md` + `results.md` 管理长任务
5. **任务完成才调用 done** - 防止过早结束

## 4. Tools 系统设计

### 4.1 动作注册装饰器
```python
@self.registry.action('Navigate to URL', param_model=NavigateAction)
async def navigate(params: NavigateAction, browser: Browser):
    page = await browser.get_current_page()
    await page.goto(params.url)
```

### 4.2 核心动作清单
| 动作 | 参数 | 说明 |
|------|------|------|
| `navigate` | url | 导航到 URL |
| `click` | index | 点击元素 |
| `input_text` | index, text | 输入文本 |
| `scroll` | direction, amount | 滚动页面 |
| `wait` | seconds | 等待 |
| `go_back` | - | 后退 |
| `open_new_tab` | url | 新标签 |
| `switch_tab` | index | 切换标签 |
| `extract_content` | selector | 提取内容 |
| `done` | result | 完成任务 |

### 4.3 工具上下文
```python
class ToolContext:
    browser: Browser
    page: Page
    agent: Agent
    # 提供所有工具需要的依赖
```

## 5. DOM 处理系统

### 5.1 核心思路
1. **简化 DOM** - 只保留可交互元素
2. **添加索引** - 每个元素加 `[index]`
3. **提取文本** - 保留关键信息
4. **生成描述** - 供 LLM 理解

### 5.2 DOM 视图格式
```
[0] <button>Login</button>
[1] <input type="text" placeholder="Email">
[2] <a href="/signup">Sign up</a>
```

## 6. Browser 会话管理

### 6.1 会话生命周期
```python
class BrowserSession:
    async def start(self):
        # 启动 Playwright 浏览器
        self.browser = await playwright.chromium.launch()
        self.context = await self.browser.new_context()
        
    async def get_state(self):
        # 获取当前状态 (DOM + 截图)
        dom = await self.dom_service.get_dom()
        screenshot = await self.page.screenshot()
        return BrowserState(dom, screenshot)
```

### 6.2 Profile 管理
- 持久化 cookies/localStorage
- 支持多账户切换
- 自动登录状态保持

## 7. 💡 关键设计模式（可借鉴）

### 7.1 Token 优化策略
```python
# 问题：长会话 Token 爆炸
# 解决：智能压缩历史
- 优先移除图片 (节省最多)
- 保留首尾历史 (保持上下文)
- 标注压缩 (告知 AI)
```

### 7.2 强制推理输出
```python
# 问题：AI 直接行动不思考
# 解决：结构化输出格式
{
  "thinking": "...",      # 强制思考
  "evaluation": "...",    # 强制评估
  "next_goal": "...",     # 强制规划
  "action": [...]         # 才执行
}
```

### 7.3 文件持久化
```python
# 问题：长任务信息丢失
# 解决：持久化到文件
- todo.md: 任务清单
- results.md: 中间结果
- 会话重启后可恢复
```

### 7.4 索引元素交互
```python
# 问题：AI 产生幻觉选择器
# 解决：只允许用索引
- DOM 预处理添加 [index]
- AI 只能用 index 引用
- 杜绝选择器错误
```

---

# 📝 待学习项目

## Stagehand (TypeScript Agent)
> 待深入学习...

## Zen Browser (Firefox Fork)
> 待深入学习...

## LaVague (Python Web Agent)
> 待深入学习...

---

# 🎯 NogicOS 最佳实践总结

> 综合所有学习后提炼（持续更新）

## 1. Agent 设计
- [ ] 采用 browser-use 的强制推理输出格式
- [ ] 实现 Token 优化策略
- [ ] 支持文件持久化长任务

## 2. DOM 处理
- [ ] 借鉴 browser-use 的索引元素系统
- [ ] 简化 DOM 只保留可交互元素

## 3. 浏览器控制
- [ ] 学习 Stagehand 的 TypeScript 方案
- [ ] 参考 Zen Browser 的性能优化

## 4. UI/UX
- [ ] 保持当前 Glassmorphism 设计
- [ ] 加入 AI 操作可视化反馈

---

*最后更新: 2025-12-27*
*学习进度: browser-use Agent 系统 ✅*

