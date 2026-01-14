# AI Browser 项目

## 目标
验证 SkillWeaver 技术路线能否实现 AI Agent 执行速度 **10x 提升**，并做成生产级产品。

## 核心假设
- **知识库驱动** vs **每步 LLM 推理**，前者更快
- 已验证：知识库模式比 Computer Use 快 **48%**（在 HN 搜索任务上）

---

## 技术栈
| 组件 | 技术 | 版本 |
|------|------|------|
| 后端 | Python | 3.11+ |
| AI 框架 | SkillWeaver (OSU-NLP-Group) | fork |
| 浏览器自动化 | Playwright | latest |
| 桌面客户端 | Electron | 28 |
| LLM | GPT-5.2 / Claude Opus 4.5 | 2025.12 |

---

## 当前阶段
**Phase 1: 稳定化** - 让 SkillWeaver 在 3 个网站达到 95%+ 成功率

### Phase 1 目标
- [ ] HN 搜索任务：100% 成功率
- [ ] HN 评论任务：100% 成功率  
- [ ] GitHub 搜索：95%+ 成功率
- [ ] 有/无知识库对比数据

---

## 核心 Bug（必须修复）

### 1. TimeoutError: Locator.click/fill Timeout exceeded
**原因**: 默认超时 5s 太短
**解决**: 
```python
await element.click(timeout=15000)
page.set_default_timeout(15000)
```

### 2. strict mode violation: resolved to N elements
**原因**: get_by_role 匹配多个元素
**解决**: 
```python
await page.get_by_role("link", name="Submit").first.click()
```

### 3. SyntaxError: Non-UTF-8 code
**原因**: LLM 生成了非 ASCII 字符
**解决**: 
```python
code = code.encode('ascii', 'ignore').decode('ascii')
```

### 4. AI 不知道何时停止
**原因**: codegen.md 模板中 terminate 指令不够明确
**解决**: 强化模板中的终止条件说明

---

## 对 SkillWeaver 的修改记录

| 文件 | 修改 | 原因 |
|------|------|------|
| lm.py | 添加 Claude/Gemini 支持 | 多模型适配 |
| lm.py | 用同步客户端 + ThreadPool | 修复 nest_asyncio 冲突 |
| explore.py | 文件操作加 encoding="utf-8" | 修复 Windows GBK 问题 |
| attempt_task_with_ws.py | 添加 WebSocket 广播 | 支持 NogicOS 状态同步 |

---

## 关键文件说明

```
ai-browser-verify/
├── SkillWeaver/
│   └── skillweaver/
│       ├── lm.py              # LLM 适配器（多模型支持）
│       ├── agent.py           # 代码执行逻辑
│       ├── explore.py         # 探索模式
│       ├── attempt_task.py    # 任务执行
│       └── templates/
│           └── codegen.md     # ⚠️ 代码生成提示词（关键）
├── electron-browser/          # NogicOS 浏览器客户端
├── config.py                  # 配置文件
├── quick_test.py              # 快速环境检查
└── run_verify.py              # 完整验证脚本
```

---

## 常用命令

```bash
# 进入项目
cd "C:\Users\WIN\Desktop\Cursor Project\ai-browser-verify"

# 快速环境检查
python quick_test.py

# 完整验证
python run_verify.py

# 启动 NogicOS 浏览器
cd electron-browser; npm start
```

---

## 测试场景

| 网站 | 任务 | 知识库技能 |
|------|------|-----------|
| Hacker News | 搜索 | hn_search_from_footer |
| Hacker News | 查看评论 | hn_open_comments |
| GitHub | 搜索仓库 | - |
| Reddit | 浏览帖子 | - |

---

## 验证指标

| 指标 | 目标 | 必须达到 |
|------|------|---------|
| 成功率 | > 95% | > 80% |
| 有知识库加速比 | > 5x | > 2x |
| 单任务耗时（有 KB） | < 10s | < 30s |

