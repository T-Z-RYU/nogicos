# Cursor 最佳实践（基于 Boris Cherny 理念）

> 来源：Claude Code 之父 Boris Cherny 的 9 条实战技巧
> 适配：Cursor IDE 环境
> 日期：2026-01-05

---

## 核心理念

> **"没有唯一正确的方式，适合自己的节奏最重要。"** — Boris Cherny

Boris 的配置出乎意料地"原装"，因为 Claude Code 开箱即用效果就很好。
Cursor 也是一样——先把基础用好，再折腾花活。

---

## 1. 复利工程：规则持续迭代 ⭐

**Boris 做法**：每周更新 CLAUDE.md，每次看到 AI 犯错就加一条规则。

**Cursor 实现**：
```
.cursor/rules/lessons-learned.md  ← 错误记录
.cursor/rules/*.md               ← 项目规则
.cursorrules                     ← 根目录规则
```

**执行方式**：
```
每次 AI 犯错 → 问自己"这个错误以后能避免吗？" → 能就加规则
```

**检查清单**：
- [ ] 每周 review 一次规则文件
- [ ] 新踩的坑立即记录
- [ ] PR/代码审查时发现问题也记录

---

## 2. 先规划再动手 ⭐

**Boris 做法**：大多数会话从 Plan 模式开始，`Shift+Tab` 切换。

**Cursor 实现**（手动触发）：

方法一：对话开头说
```
我要做 XXX 功能。
先给我一个执行计划，列出步骤，不要直接写代码。
等我确认后再开始。
```

方法二：加到 `.cursorrules`
```markdown
## 复杂任务必须先规划
对于超过 3 个步骤的任务：
1. 先输出执行计划
2. 等用户确认
3. 然后再动手

格式：
## 执行计划
1. [ ] 步骤一：...
2. [ ] 步骤二：...
3. [ ] 步骤三：...

等你确认后我再开始。
```

**核心逻辑**：花几分钟对齐计划，能省几小时的返工。

---

## 3. 用最强模型 ⭐

**Boris 做法**：所有任务都用 Opus 4.5 + thinking 模式。

> "虽然单次响应慢一点，但你需要纠正它的次数少得多，最终算下来反而更快。"

**Cursor 设置**：
1. 设置 → Models → 选择 Claude Opus 4.5
2. 复杂任务时确保用的是最强模型

**什么时候用 Sonnet**：
- 简单的单文件修改
- 重复性的批量操作
- 不需要深度推理的任务

---

## 4. 写代码前必查文档 ⭐

**Boris 做法**：通过 MCP 连接外部服务获取最新信息。

**Cursor 实现**：`/check` 命令

```
触发条件：
- 写新代码/功能
- 技术选型
- 解决复杂 Bug
- 接入新 API/库

执行内容（并行）：
├── Context7  → 官方文档
├── DeepWiki  → GitHub 参考
└── WebSearch → 最新信息 2025
```

**规则**：不问，直接查。三个同时调用，查完再写代码。

---

## 5. 验证机制是最重要的 ⭐⭐⭐

**Boris 原话**：
> "如果 Claude 能验证自己的工作，最终产出质量能提升 2-3 倍。"

**Cursor 实现**：浏览器工具 + 终端测试

```
写代码
   │
   ▼
浏览器测试（browser_navigate → browser_snapshot）
   │
   ▼
看截图/快照
   │
   ▼
发现问题 ──► 修复 ──► 再测试
   │
   ▼
功能正常 ──► 完成
```

**具体工具**：
- `browser_navigate` - 打开页面
- `browser_snapshot` - 获取页面结构
- `browser_take_screenshot` - 截图检查
- `browser_click/type` - 交互测试
- `run_terminal_cmd` - 跑测试命令

**核心逻辑**：让 AI 有反馈闭环，不是"写完就算"。

---

## 6. 多任务并行（Cursor 版）

**Boris 做法**：终端开 5 个实例 + 网页版 5-10 个任务。

**Cursor 限制**：不能像 CLI 那样开多实例。

**变通方案**：
1. **多窗口**：开多个项目窗口，每个独立 Agent
2. **Background Agent**：让任务后台跑
3. **任务拆分**：把大任务拆成独立的小任务

**适合并行的任务**：
- 独立的功能模块
- 不同项目的开发
- 调研和实现分离

---

## 7. 自动化重复操作

**Boris 做法**：斜杠命令 + 子 Agent + Hooks。

**Cursor 实现**：

| Boris 的 | Cursor 的 | 位置 |
|----------|-----------|------|
| 斜杠命令 | Skills | `openskills read <skill>` |
| 子 Agent | 无直接对应 | 用规则模拟 |
| Hooks | 无 | 手动或脚本 |

**Skills 用法**：
```bash
openskills read frontend-design  # 前端设计技能
openskills read webapp-testing   # 测试技能
```

**自定义命令**（放在 `.cursor/commands/`）：
```markdown
# check.md
并行执行以下查询：
1. Context7 查询 [技术名] 最新文档
2. DeepWiki 查询相关 GitHub 项目
3. WebSearch 搜索 "[技术名] 2025 最佳实践"
```

---

## 8. 安全与权限

**Boris 做法**：不用 `--dangerously-skip-permissions`，而是预先批准安全命令。

**Cursor 实现**：
- 审批模式默认开启，保持开启
- 复杂操作让 AI 先说明要做什么
- 敏感操作手动确认

---

## 9. 长任务处理

**Boris 做法**：让 Claude 自己验证，用 Stop Hook 触发后续检查。

**Cursor 实现**：

方法一：在任务描述里加验证要求
```
完成后：
1. 在浏览器中测试功能
2. 截图确认 UI 正确
3. 跑一遍相关测试
4. 汇报结果
```

方法二：分阶段检查点
```
每完成一个阶段，停下来让我确认：
- 阶段 1 完成 → 确认
- 阶段 2 完成 → 确认
- ...
```

---

## 快速检查清单

每次开始任务前：

- [ ] 复杂任务？→ 先要计划
- [ ] 写新代码？→ `/check` 查文档
- [ ] 有 UI？→ 完成后浏览器测试
- [ ] 犯过的错？→ 检查 `lessons-learned.md`
- [ ] 用的是最强模型？→ 确认是 Opus

---

## 一句话总结

> **"无招胜有招"** — 不需要复杂配置，把基础用好：
> 1. 学会规划
> 2. 学会查文档
> 3. 学会积累规则
> 4. 学会给 AI 验证手段

等你真正遇到瓶颈了，再去折腾那些花活不迟。

---

## 参考链接

- 原文：[Boris Cherny 的 9 条实战技巧](https://www.53ai.com/news/tishicijiqiao/2026010376241.html)
- Claude Code 官方文档：https://code.claude.com/docs/
- 子 Agent 文档：https://code.claude.com/docs/en/sub-agents
- Hooks 文档：https://code.claude.com/docs/en/hooks


