# NogicOS 代码审查报告 - Round 1

**审查日期**: 2026-01-07
**审查模型**: Claude Opus 4.5
**审查范围**: engine/, hive_server.py, client/, nogicos-ui/src/, tests/

---

## 当前评分

| 指标 | Round 1 初始 | Round 1 修复后 | 目标值 |
|------|-------------|---------------|--------|
| **安全评分** | 4/10 | 6/10 | >= 9/10 |
| **代码质量评分** | 6/10 | 6.5/10 | >= 9/10 |
| **P0 问题** | 14 | 9 (-5) | 0 |
| **P1 问题** | 21 | 21 | 0 |
| **P2 问题** | 18 | 18 | <= 3 |

---

## Round 1 已修复的 P0 问题 (5 个)

### 1. 命令链白名单过于宽松 (engine/tools/local.py:455-464)
- **问题**: 白名单包含 npm/pip/git，可执行任意代码
- **修复**: 移除危险命令，仅保留 echo/cd/pwd/ls/dir/type/cat

### 2. SSRF 缺少 DNS 预解析验证 (engine/browser/session.py:381-392)
- **问题**: DNS rebinding 攻击可绕过 SSRF 检测
- **修复**: 添加 DNS 预解析，验证解析后的 IP 不是私有地址

### 3. Markdown XSS 漏洞 (nogicos-ui/src/components/chat/MinimalChatArea.tsx:1411-1428)
- **问题**: 链接未验证协议，可执行 javascript: URL
- **修复**: 添加 URL 协议白名单验证

### 4. Electron 缺少 CSP (client/main.js:318-334)
- **问题**: 无内容安全策略，易受 XSS 攻击
- **修复**: 添加 session.webRequest CSP 头

### 5. IPC 消息来源未验证 (client/main.js:312-384)
- **问题**: 任意渲染进程可调用特权 IPC
- **修复**: 添加 isValidSender 验证和参数校验

---

## 剩余 P0 问题（9 个，需 Round 2 修复）

| # | 模块 | 问题 | 优先级 |
|---|------|------|--------|
| 1 | hive_server.py | API 密钥硬编码 (api_keys.py) | 最高 |
| 2 | hive_server.py | /read_file 绝对路径绕过 | 高 |
| 3 | hive_server.py | 缺少 CSRF 保护 | 高 |
| 4 | client/ | 调试日志硬编码路径 | 高 |
| 5 | nogicos-ui/ | Base64 图片验证不完整 | 中 |
| 6 | nogicos-ui/ | 全局类型污染风险 | 中 |
| 7 | tests/ | 无限循环资源耗尽 | 中 |
| 8 | tests/ | 自动代码修复安全风险 | 中 |
| 9 | engine/ | WebSocket 工具白名单包含 shell_execute | 高 |

---

## P1 问题汇总（21 个）

### 后端 (8 个)
1. WebSocket JSON 炸弹
2. 缺少速率限制
3. 认证不完整
4. 并发竞态
5. CORS 宽松
6. 日志泄露
7. 请求大小
8. HWND TOCTOU

### 前端 (4 个)
1. WebSocket 内存泄漏
2. 闭包陷阱
3. 定时器清理
4. 拖拽事件清理

### Electron (5 个)
1. HWND 未验证
2. Native 模块风险
3. HTML 注入
4. 缺少 Sandbox
5. IPC 速率限制

### 测试 (4 个)
1. 外部依赖 Mock
2. 硬编码 URL
3. 异步超时
4. Sleep 性能

---

## 下一步（Round 2）

1. 移除 api_keys.py 导入
2. 修复 /read_file 绝对路径
3. 移除 WebSocket shell_execute
4. 添加 CSRF 保护
5. 清理调试日志

---

**报告时间**: 2026-01-07
