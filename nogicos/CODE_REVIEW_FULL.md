基于对 NogicOS 项目代码的全面审查，以下是代码审查报告：

---

## 🔴 P0 紧急（安全漏洞）

**engine/tools/local.py:285-290** - **命令注入风险**
- 问题：`shell_execute` 函数使用 `asyncio.create_subprocess_shell(command)` 直接执行用户输入的命令，虽然有 `dangerous_patterns` 过滤，但过滤不完整
- 过滤缺失：`| rm`, `; rm`, `` `rm` ``（反引号命令替换）, `$(rm)`, `curl | bash`, `wget | sh` 等绕过方式
- 修复建议：使用白名单而非黑名单，或改用 `subprocess_exec` 并拆分参数；添加更多命令注入模式

**hive_server.py:549-571** - **路径遍历漏洞**
- 问题：`/read_file` 端点的路径验证可被绕过，`os.path.normpath` 无法防止 `..%2f..%2f` URL 编码攻击
- 修复建议：使用 `os.path.realpath` 替代 `normpath`，并在标准化后再次验证路径

**engine/tools/local.py:26-28** - **ALLOWED_ROOTS 过于宽松**
- 问题：`ALLOWED_ROOTS` 包含用户主目录和当前工作目录，可能允许访问敏感文件（如 `.ssh/`, `.env` 等）
- 修复建议：实现更细粒度的路径访问控制，排除敏感目录

---

## 🟠 P1 高优先（潜在 Bug）

**engine/tools/local.py:419-421** - **静默异常吞噬**
- 问题：`except:` 裸异常捕获会隐藏所有错误，包括 `KeyboardInterrupt`、内存错误等
- 修复建议：改为 `except (IOError, OSError, UnicodeDecodeError):`

**engine/browser/session.py:351** - **except 裸异常**
- 问题：`except:` 裸异常吞噬了所有错误，可能导致难以调试的问题
- 修复建议：捕获具体异常如 `except TimeoutError:`

**hive_server.py:893** - **全局 Agent 实例未加锁**
- 问题：`engine.agent` 在 `generate_ai_sdk_stream` 中被多个请求共享使用，可能导致并发问题
- 修复建议：为每个请求创建新的 Agent 实例，或使用锁保护共享状态

**engine/server/websocket.py:183-186** - **客户端断开时资源泄漏**
- 问题：`asyncio.gather` 关闭客户端时如果某个连接卡住，会阻塞所有其他清理
- 修复建议：添加 timeout 参数：`await asyncio.wait_for(client.close(), timeout=5.0)`

**engine/tools/local.py:711-728** - **危险路径判断不完整（Windows）**
- 问题：`danger_paths` 硬编码了路径，但未考虑大小写不敏感的 Windows 文件系统
- 修复建议：在 Windows 上使用 `abs_path.lower()` 比较

---

## 🟡 P2 中优先（代码质量）

**hive_server.py:171-177** - **单任务执行限制**
- 问题：`_executing` 标志使服务器一次只能处理一个任务，可能导致请求被拒绝（HTTP 429）
- 修复建议：考虑使用任务队列或允许有限的并发执行

**engine/tools/base.py:421-435** - **全局单例无线程安全**
- 问题：`_global_registry` 全局变量在多线程/协程环境下可能出现竞态条件
- 修复建议：使用 `threading.Lock` 或 `asyncio.Lock` 保护

**engine/context/injector.py:40-46** - **SQL 查询潜在问题**
- 问题：虽然使用了参数化查询，但 `'default'` 硬编码在 SQL 中可能导致歧义
- 修复建议：使用 `IN (?, ?)` 并传入两个参数

**hive_server.py:1476** - **裸 except 语句**
- 问题：`except:` 捕获所有异常但只设置 `memory_mb = 0`，可能隐藏重要错误
- 修复建议：改为 `except ImportError:` 或 `except Exception as e:` 并记录日志

**engine/agent/react_agent.py:113-126** - **过多 try/except 导入**
- 问题：多个可选模块导入使用独立的 try/except，代码冗余
- 修复建议：已在 `imports.py` 中集中处理，考虑完全移除这些重复导入

---

## 🟢 P3 低优先（最佳实践）

**hive_server.py:352-360** - **CORS 配置过于宽松**
- 问题：默认 `ALLOWED_ORIGINS` 包含 `file://`，可能允许任意本地文件访问
- 修复建议：生产环境应使用环境变量严格配置允许的 origins

**engine/tools/local.py:797** - **类型注解不一致**
- 问题：`paths: List[str]` 但实际可能接收单个字符串
- 修复建议：添加类型验证或改为 `Union[str, List[str]]`

**engine/server/websocket.py:89** - **可变默认参数**
- 问题：`domains: list = None` 后在 `__post_init__` 中初始化为 `[]`，应直接使用 `field(default_factory=list)`
- 修复建议：使用 `domains: List[str] = field(default_factory=list)`

**hive_server.py:854** - **Pydantic Config 已废弃**
- 问题：`class Config: extra = "allow"` 是 Pydantic v1 语法，v2 中应使用 `model_config`
- 修复建议：改为 `model_config = ConfigDict(extra="allow")`

**engine/browser/session.py:628** - **全局可变状态**
- 问题：`_active_session` 全局变量在并发环境下可能导致问题
- 修复建议：考虑使用 contextvars 或每个上下文独立管理 session

**engine/tools/base.py:317** - **import 放在函数内部**
- 问题：`import time` 在 `execute` 方法内部，每次调用都会执行（虽然 Python 会缓存）
- 修复建议：将 import 移至文件顶部

**hive_server.py:437** - **import 放在函数内部**
- 问题：`import aiohttp` 在 `quick_search` 函数内部，应该在文件顶部导入
- 修复建议：移至文件顶部的 imports 区域

---

### 总结

| 级别 | 数量 | 主要问题域 |
|-----|------|-----------|
| P0 | 3 | 命令注入、路径遍历、权限过宽 |
| P1 | 5 | 异常处理、并发安全、资源泄漏 |
| P2 | 5 | 单例模式、SQL查询、类型系统 |
| P3 | 7 | CORS配置、代码风格、废弃API |

最紧急需要修复的是 **P0 级安全漏洞**，特别是 `shell_execute` 的命令注入风险和 `/read_file` 的路径遍历漏洞。
