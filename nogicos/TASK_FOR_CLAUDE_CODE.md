# NogicOS 代码质量提升任务

## 目标
让 NogicOS 达到**顶级最佳质量**，可以自信地展示给投资人和用户。

---

## 项目背景
- **产品定位**："The AI that works where you work" - 第一个能同时看到浏览器、文件和桌面的 AI
- **技术栈**：Python (FastAPI) + Electron + React + TypeScript
- **截止时间**：2025/1/10

---

## 已完成的工作

### Round 1: 安全审查 ✅
- [x] XSS 防护（overlay.js HTML 转义）
- [x] CORS 限制（hive_server.py）
- [x] API 认证（/v2/quick-search）
- [x] 命令注入防护（local.py 45+ 危险模式）
- [x] 路径遍历修复（realpath + 符号链接检查）

### Round 2: 潜在 Bug 修复 ✅
- [x] Electron nodeIntegration: false
- [x] WebSocket DoS 防护
- [x] 资源泄露清理（browser/session.py）
- [x] 并发安全（contextvars）

### Round 3: 代码质量 ✅
- [x] 日志规范化（print → logger）
- [x] 异常处理细化（bare except → specific）
- [x] 类型注解完善
- [x] 重复代码抽取（shared-overlay-utils.js）

---

## 待审查目录

按优先级排序：

```
nogicos/
├── engine/           # 核心引擎 ⭐ P0
│   ├── agent/        # ReAct Agent
│   ├── tools/        # 工具系统
│   ├── browser/      # 浏览器自动化
│   └── context/      # 上下文管理
├── client/           # Electron 客户端 ⭐ P1
├── nogicos-ui/       # React 前端 P2
└── tests/            # 测试 P3
```

---

## 审查标准

### 安全性 (P0)
- [ ] 无 API 密钥泄露
- [ ] 无命令注入风险
- [ ] 无路径遍历漏洞
- [ ] 无 XSS/SSRF 漏洞
- [ ] Electron 安全配置正确

### 可靠性 (P1)
- [ ] 无竞态条件
- [ ] 资源正确释放
- [ ] 异常正确处理
- [ ] 边界条件检查

### 可维护性 (P2)
- [ ] 代码无重复
- [ ] 命名清晰
- [ ] 类型注解完整
- [ ] 日志/注释充分

---

## 如何使用此任务

在 Claude Code 中运行：

```bash
# 方式 1：直接审查
claude "请阅读 TASK_FOR_CLAUDE_CODE.md 并执行代码审查任务"

# 方式 2：用 ralph-wiggum 循环
/ralph-loop
# 然后粘贴此任务内容

# 方式 3：分目录审查
claude "审查 engine/agent/ 目录，按照 TASK_FOR_CLAUDE_CODE.md 的标准"
```

---

## 预期输出

每轮审查后输出：
1. **发现的问题**（文件:行号:描述）
2. **修复代码**（diff 格式）
3. **验证方式**（如何确认修复有效）
4. **剩余问题数量**（直到为 0）
