# NogicOS Engine 代码审查报告

> **审查工具**: Claude Code (Opus 4.5)
> **模型版本**: claude-opus-4-5-20251101
> **生成时间**: 2026-01-05
> **审查范围**: `nogicos/engine/` 目录

---

## 一、安全漏洞

### 1.1 命令注入风险 [高危]

**文件**: `engine/tools/local.py`

虽然代码中有命令黑名单检查（如 `rm -rf /`, `sudo` 等），但检查并不充分：
- 黑名单可被字符串拼接绕过（如 `"r" + "m -rf /"`）
- 可使用 `;` 链接危险命令
- `shell=True` 的使用存在风险

**修复建议**:
- 使用白名单而不是黑名单
- 使用 `shlex.split()` 解析命令，避免 `shell=True`
- 实现更严格的命令沙箱

### 1.2 路径遍历漏洞 [高危]

**文件**: `engine/tools/local.py`

`read_file`, `write_file` 等函数未充分验证路径，`_resolve_path` 未阻止 `../../` 遍历。

**修复建议**:

```python
def _safe_resolve_path(path: str, workspace: str) -> str:
    resolved = os.path.realpath(os.path.expanduser(path))
    workspace_resolved = os.path.realpath(workspace)
    if not resolved.startswith(workspace_resolved):
        raise ValueError("Path traversal detected")
    return resolved
```

### 1.3 敏感信息泄露 [中危]

**文件**: `engine/observability/langsmith_tracer.py:30-35`

API Key 直接设置到环境变量，可能在日志中泄露。

### 1.4 MD5 用于哈希 [低危]

**文件**: `engine/rag/indexer.py:140, 191`

用于缓存/索引时 MD5 可接受，但应注释说明不用于安全目的。

---

## 二、潜在 Bug

### 2.1 类属性作为可变默认值 [高危]

**文件**: `engine/observability/__init__.py:90`

```python
class ModuleTracer:
    _spans: list = []  # 所有实例共享同一个列表！
```

**修复建议**: 移到 `__init__` 中初始化。

### 2.2 全局可变状态 [中危]

**多个文件**:
- `engine/context/injector.py:382-390`
- `engine/context/terminal.py:152-160`
- `engine/server/websocket.py:1109-1118`
- `engine/rag/indexer.py:367-375`

全局单例模式在多线程环境下可能出现竞态条件。

### 2.3 bare except 语句 [中危]

**文件**:
- `engine/browser/session.py:249, 304`
- `engine/visualization/tool_mapper.py:168-170`

```python
except:
    return False
```

**修复建议**: 改为 `except Exception as e:`

### 2.4 asyncio 事件循环获取方式 [中危]

**文件**: `engine/server/websocket.py:314, 373`

```python
loop = asyncio.get_event_loop()  # Python 3.10+ 中已弃用
```

**修复建议**: 使用 `asyncio.get_running_loop()`

---

## 三、代码质量问题

### 3.1 函数过长 [中危]

**文件**: `engine/agent/react_agent.py`

`run()` 方法超过 200 行，建议拆分为更小的私有方法。

### 3.2 重复代码 [中危]

**文件**: `engine/observability/langsmith_tracer.py:95-129, 154-210`

`trace_agent_run` 和 `trace_tool_call` 装饰器有大量重复逻辑。

### 3.3 魔法数字 [低危]

**文件**: `engine/visualization/tool_mapper.py:103-113`

硬编码的屏幕尺寸和区域配置应移到配置文件中。

---

## 四、最佳实践问题

### 4.1 异常处理不当 [高危]

**文件**: `engine/server/chatkit_server.py:423-426`

```python
await event_queue.put(("response", f"\n⚠️ 出错了: {str(e)}"))
```

将原始异常消息暴露给用户可能泄露敏感信息。

### 4.2 硬编码配置 [中危]

**文件**:
- `engine/browser/session.py:77-78` - viewport 默认值
- `engine/server/websocket.py:125` - host/port 默认值

建议使用配置文件或环境变量管理。

### 4.3 缺少类型注解 [中危]

**文件**: `engine/server/websocket.py`

多个方法的参数缺少类型注解，如 `_handle_client(self, websocket)`。

### 4.4 内部 import [低危]

**文件**: `engine/context/injector.py:52-54`

函数内部 `import logging` 应移到文件顶部。

### 4.5 TODO 注释未清理 [低危]

**文件**: `engine/server/chatkit_server.py:331`

```python
# TODO: 实现停止逻辑
```

---

## 五、总结

| 严重程度 | 数量 | 主要问题 |
|---------|------|---------|
| **高危** | 4 | 命令注入、路径遍历、类属性可变默认值、异常处理不当 |
| **中危** | 12 | 敏感信息泄露、全局状态、bare except、asyncio弃用、函数过长、重复代码 |
| **低危** | 6 | MD5哈希、魔法数字、日志级别、内部import、TODO |

### 优先修复建议

1. **立即修复** (安全相关):
   - `engine/tools/local.py` - 路径遍历和命令注入
   - `engine/observability/__init__.py` - 类属性可变默认值

2. **近期修复** (稳定性相关):
   - bare except 改为具体异常类型
   - asyncio 事件循环获取方式更新
   - 全局状态的线程安全问题

3. **后续优化** (代码质量):
   - 拆分过长的函数
   - 消除重复代码
   - 补充类型注解


