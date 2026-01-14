基于全面审查，现在让我输出完整的审查报告：

# NogicOS Engine 代码审查报告

## ✅ 已修复确认

经过对比审查，以下问题已确认修复：

### 1. SQL 注入防护 ✅
**文件**: `engine/context/injector.py:41-47`
```python
cursor.execute("""
    SELECT id, title, content
    FROM memories
    WHERE namespace IN (?, ?)
    ORDER BY updated_at DESC
    LIMIT ?
""", (namespace, "default", limit))
```
**状态**: 已使用参数化查询，SQL 注入风险已解决。

### 2. 路径遍历防护 ✅
**文件**: `hive_server.py:567-573`
```python
full_path = os.path.realpath(os.path.join(workspace, path))
if not full_path.startswith(workspace + os.sep):
    raise HTTPException(status_code=403, detail="Access denied")
```
**状态**: 使用 `realpath` 和严格前缀检查，路径遍历已修复。

### 3. 敏感文件过滤 ✅
**文件**: `hive_server.py:576-579`
```python
sensitive_patterns = ['.env', '.ssh', 'credentials', 'secrets', '.git/config']
for pattern in sensitive_patterns:
    if pattern in full_path.lower():
        raise HTTPException(status_code=403, detail="Access denied to sensitive file")
```
**状态**: 已添加敏感文件模式过滤。

### 4. 本地文件工具路径安全 ✅
**文件**: `engine/tools/local.py:26-56`
- 添加了 `ALLOWED_ROOTS` 白名单
- 添加了 `SENSITIVE_PATTERNS` 敏感路径黑名单
- 实现了 `_is_path_allowed()` 和 `_is_sensitive_path()` 检查
**状态**: 文件系统访问控制已实现。

### 5. 危险命令过滤 ✅
**文件**: `engine/tools/local.py:304-326`
```python
dangerous_patterns = [
    r'\brm\s+-rf\s+/',
    r'\bsudo\b',
    r'\bformat\b',
    r';\s*sh\b',  # 命令注入
    r'\beval\s',   # eval 命令
    r'\.\./',      # 路径遍历
    # ... 更多模式
]
```
**状态**: 危险命令模式检测已增强。

### 6. WebSocket 连接超时关闭 ✅
**文件**: `engine/server/websocket.py:178-189`
```python
await asyncio.wait_for(
    asyncio.gather(
        *[client.close() for client in self._clients],
        return_exceptions=True
    ),
    timeout=5.0
)
```
**状态**: 添加了 5 秒超时关闭机制。

### 7. 删除文件危险路径保护 ✅
**文件**: `engine/tools/local.py:760-783`
- 添加了 `danger_paths` 列表（Unix）
- 添加了 `windows_danger_paths` 列表（Windows）
- 大小写不敏感比较（Windows）
**状态**: 系统关键路径已受保护。

### 8. 代码文件保护 ✅
**文件**: `engine/tools/local.py:69-148`
- 添加了 `PROTECTED_PATTERNS`
- 添加了 `CODE_EXTENSIONS`
- 实现了 `_check_file_safety()` 检查
**状态**: 代码项目和 Git 仓库已受保护。

### 9. CORS 来源限制 ✅
**文件**: `hive_server.py:367-376`
```python
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",") if ... else [
    "http://localhost:5173",
    # ... 明确列出的来源
]
```
**状态**: CORS 已限制为白名单来源，支持环境变量配置。

### 10. 工具执行超时和重试 ✅
**文件**: `engine/tools/base.py:293-387`
- D1.1: 自动重试（最多 max_retries 次）
- D1.2: 超时处理（timeout_seconds）
- D1.3: 优雅降级
- D1.4: 用户友好错误消息
**状态**: 已实现完整的可靠性机制。

### 11. 异步安全的浏览器会话管理 ✅
**文件**: `engine/browser/session.py:628-661`
```python
import contextvars
_active_session_var: contextvars.ContextVar[Optional[BrowserSession]] = ...
```
**状态**: 使用 `contextvars` 实现异步安全的会话管理。

### 12. 线程安全的全局注册表 ✅
**文件**: `engine/tools/base.py:421-435`
```python
_registry_lock = threading.Lock()
def get_registry() -> ToolRegistry:
    global _global_registry
    if _global_registry is None:
        with _registry_lock:
            if _global_registry is None:
                _global_registry = ToolRegistry()
    return _global_registry
```
**状态**: 使用双重检查锁定模式。

---

## ⚠️ 未完全修复

### 1. 命令注入防护仍可绕过 ⚠️
**文件**: `engine/tools/local.py:300-363`
**严重程度**: 高

**当前实现**:
```python
dangerous_patterns = [
    r'\brm\s+-rf\s+/',
    # ...
]
```

**仍可绕过**:
- `rm${IFS}-rf${IFS}/` - 使用 IFS 变量绕过空格检测
- `/bin/rm -rf /` - 使用绝对路径
- `python -c "import os; os.system('rm -rf /')"` - 通过 Python 执行
- `sh -c "危险命令"` - 通过 sh 执行

**建议**: 改用命令白名单或禁用 `shell=True`。

### 2. BrowserSession 异常时资源泄漏 ⚠️
**文件**: `engine/browser/session.py:100-150`
**严重程度**: 中

**问题**: 如果在 `new_page()` 时失败，前面创建的 browser 和 context 可能未正确关闭。`stop()` 方法虽然会被调用，但实例变量可能未赋值。

**当前代码**:
```python
async def start(self) -> bool:
    try:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(...)
        self._context = await self._browser.new_context(...)
        self._page = await self._context.new_page()  # 如果这里失败
        # ...
    except Exception as e:
        await self.stop()  # stop() 依赖实例变量
        return False
```

### 3. 符号链接攻击风险 ⚠️
**文件**: `engine/tools/local.py:76-86`
**严重程度**: 中

**问题**: `realpath()` 在检查之前解析符号链接，但攻击者可以：
1. 在允许目录创建符号链接指向敏感文件
2. 符号链接被解析后通过路径检查

**建议**:
```python
def _is_path_allowed(path: str) -> bool:
    # 先检查是否为符号链接
    if os.path.islink(path):
        return False
    # ...
```

---

## 🆕 新发现问题

### 1. 裸 except 块 - 异常吞噬 🆕
**文件**: `engine/browser/session.py:351, 362, 372, 422, 433`
**严重程度**: 中

```python
except Exception:
    continue  # 吞噬所有异常
```

**问题**: 这些裸 except 可能隐藏重要错误（如内存不足、系统错误）。

### 2. 无界字典增长 - 内存泄漏风险 🆕
**文件**: `engine/server/websocket.py:134-137`
**严重程度**: 中

```python
self._cdp_response_handlers: Dict[str, Any] = {}
self._tool_response_handlers: Dict[str, Any] = {}
```

**问题**: 如果请求超时或异常，handler 可能永久残留，导致内存泄漏。

### 3. 潜在的 None 访问 🆕
**文件**: `engine/browser/session.py:183`
**严重程度**: 低

```python
def _on_navigated(self, frame) -> None:
    if frame == self._page.main_frame:  # _page 可能为 None
```

### 4. 未使用的导入 🆕
**文件**: `engine/context/terminal.py:12`
**严重程度**: 低

```python
from typing import Optional, List, Dict, Any  # Dict, Any 未使用
```

### 5. API Key 可能被日志记录 🆕
**文件**: `engine/evaluation/dataset_manager.py:85-89`
**严重程度**: 中

```python
self.api_key = api_key or LANGSMITH_API_KEY
# 如果开启 DEBUG 日志，API Key 可能被记录
```

**建议**: 添加 `__repr__` 方法屏蔽敏感信息。

### 6. 硬编码配置 🆕
**文件**: 多处
**严重程度**: 低

- `engine/browser/session.py:77` - 硬编码视口大小 `{"width": 1280, "height": 720}`
- `engine/tools/base.py:298` - 硬编码超时 `timeout_seconds: float = 30.0`

---

## 总结

| 类别 | 数量 |
|------|------|
| ✅ 已修复 | 12 |
| ⚠️ 未完全修复 | 3 |
| 🆕 新发现 | 6 |

**整体评估**: 之前的 20 个主要问题大部分已修复，代码安全性明显提升。但仍有 3 个需要进一步完善的问题和 6 个新发现的低中风险问题需要关注。
