# NogicOS Agent 架构改进建议

> 基于顶级架构师视角的 Plan Review + `/check` 研究结果

---

## 📊 Executive Summary

当前计划是一个**功能导向**的计划，功能覆盖全面，但缺少对**系统本质复杂度**的深入应对。

**核心问题**：
1. 通信契约模糊（三种通道，三种格式）
2. 状态真相源不清晰（SQLite、内存、UI 三处状态）
3. LLM 不确定性处理不足
4. 成功/失败边界未定义

**参考研究**：
- **UFO (Microsoft)**：五层 Agent Interaction Protocol (AIP)、ERROR vs FAIL 状态区分
- **LangGraph**：Checkpointer 持久化模式、interrupt() Human-in-the-loop
- **Anthropic computer-use**：ToolError → ToolFailure(is_error=True)、Callbacks 可观察性

---

## 🏗️ 架构改进方案

### Phase 0: 通信契约层（新增）

**问题**：WebSocket、IPC、REST API 三种通信方式，数据格式不统一，调试困难。

**解决方案**：参考 UFO 的 AIP，定义统一的 `AgentEvent` 消息格式。

```python
# nogicos/engine/agent/protocol.py

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional
import uuid
import time

class EventType(Enum):
    """事件类型 - 统一所有通道"""
    # 状态事件
    STATUS_CHANGED = "status_changed"
    PROGRESS_UPDATE = "progress_update"
    
    # 工具事件
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    TOOL_ERROR = "tool_error"
    
    # 交互事件
    CONFIRM_REQUEST = "confirm_request"
    CONFIRM_RESPONSE = "confirm_response"
    
    # 流式事件
    THINKING_DELTA = "thinking_delta"
    TEXT_DELTA = "text_delta"
    
    # 生命周期
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_INTERRUPTED = "task_interrupted"


@dataclass(frozen=True)
class AgentEvent:
    """
    统一事件格式 - 所有通道都用这个
    
    参考：UFO AIP L1 (Message Schema Layer)
    """
    id: str                          # 唯一 ID
    type: EventType                  # 事件类型
    task_id: str                     # 所属任务
    timestamp: float                 # Unix 时间戳
    payload: dict                    # 事件数据
    
    # 可选元数据
    hwnd: Optional[int] = None       # 目标窗口
    iteration: Optional[int] = None  # 迭代次数
    
    @classmethod
    def create(cls, event_type: EventType, task_id: str, payload: dict, **kwargs):
        return cls(
            id=str(uuid.uuid4()),
            type=event_type,
            task_id=task_id,
            timestamp=time.time(),
            payload=payload,
            **kwargs
        )
    
    def to_dict(self) -> dict:
        """序列化为字典（用于 WebSocket/IPC）"""
        return {
            "id": self.id,
            "type": self.type.value,
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "hwnd": self.hwnd,
            "iteration": self.iteration,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AgentEvent":
        """从字典反序列化"""
        return cls(
            id=data["id"],
            type=EventType(data["type"]),
            task_id=data["task_id"],
            timestamp=data["timestamp"],
            payload=data["payload"],
            hwnd=data.get("hwnd"),
            iteration=data.get("iteration"),
        )


class EventBus:
    """
    事件总线 - 统一分发到各通道
    
    参考：UFO AIP L3 (Protocol Orchestration Layer)
    """
    def __init__(self):
        self._handlers: dict[EventType, list[callable]] = {}
        self._websockets: list = []
        self._ipc_sender: Optional[callable] = None
    
    def subscribe(self, event_type: EventType, handler: callable):
        """订阅特定事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def register_websocket(self, ws):
        """注册 WebSocket 连接"""
        self._websockets.append(ws)
    
    def register_ipc(self, sender: callable):
        """注册 IPC 发送器"""
        self._ipc_sender = sender
    
    async def emit(self, event: AgentEvent):
        """发送事件到所有通道"""
        event_dict = event.to_dict()
        
        # 1. 本地处理器
        for handler in self._handlers.get(event.type, []):
            try:
                await handler(event)
            except Exception as e:
                print(f"Handler error: {e}")
        
        # 2. WebSocket
        for ws in self._websockets:
            try:
                await ws.send_json(event_dict)
            except Exception:
                self._websockets.remove(ws)
        
        # 3. IPC (Electron)
        if self._ipc_sender:
            self._ipc_sender("agent:event", event_dict)
```

**Electron 端对应**：

```javascript
// client/agent-event-handler.js

const EventType = {
  STATUS_CHANGED: 'status_changed',
  TOOL_START: 'tool_start',
  TOOL_END: 'tool_end',
  CONFIRM_REQUEST: 'confirm_request',
  // ... 其他类型
};

class AgentEventHandler {
  constructor() {
    this.handlers = new Map();
    
    // 监听来自 Python 的事件
    ipcMain.on('agent:event', (_, event) => {
      this.dispatch(event);
    });
  }
  
  on(eventType, handler) {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }
    this.handlers.get(eventType).push(handler);
  }
  
  dispatch(event) {
    const handlers = this.handlers.get(event.type) || [];
    for (const handler of handlers) {
      handler(event);
    }
    
    // 转发到 Overlay
    if (event.hwnd && this.overlayManager) {
      this.overlayManager.sendEvent(event.hwnd, event);
    }
  }
}
```

---

### Phase 0.5: 状态真相源（新增）

**问题**：任务状态分散在 TaskStore、HostAgent.is_processing、Overlay UI、前端 ChatArea 四处，可能不一致。

**解决方案**：明确 TaskStore 为唯一真相源，其他状态都是派生。

```python
# nogicos/engine/agent/task_state.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
import sqlite3
import json
from datetime import datetime


class TaskStatus(Enum):
    """
    任务状态 - 参考 UFO ERROR vs FAIL 区分
    
    PENDING → RUNNING → COMPLETED
                     ↘ NEEDS_HELP (可恢复)
                     ↘ FAILED (可恢复)
                     ↘ ERROR (不可恢复)
                     ↘ INTERRUPTED (外部中断)
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    NEEDS_HELP = "needs_help"   # LLM 主动请求帮助（可恢复）
    FAILED = "failed"           # 操作失败但可重试（可恢复）
    ERROR = "error"             # 严重错误（不可恢复）
    INTERRUPTED = "interrupted" # 外部中断（可恢复）
    
    @property
    def is_terminal(self) -> bool:
        """是否是终态"""
        return self in (TaskStatus.COMPLETED, TaskStatus.ERROR)
    
    @property
    def is_recoverable(self) -> bool:
        """是否可恢复"""
        return self in (TaskStatus.NEEDS_HELP, TaskStatus.FAILED, TaskStatus.INTERRUPTED)


@dataclass
class TaskState:
    """
    任务状态容器 - 唯一真相源
    
    所有其他组件的状态都从这里派生
    """
    id: str
    status: TaskStatus
    task_text: str
    target_hwnds: List[int]
    iteration: int
    max_iterations: int
    created_at: datetime
    updated_at: datetime
    
    # 错误信息（仅当 status 是错误状态时）
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    
    # 最后一次检查点
    last_checkpoint_iteration: Optional[int] = None
    
    @property
    def is_running(self) -> bool:
        """是否正在运行 - 派生状态"""
        return self.status == TaskStatus.RUNNING
    
    @property
    def can_resume(self) -> bool:
        """是否可以恢复 - 派生状态"""
        return self.status.is_recoverable and self.last_checkpoint_iteration is not None
    
    @property
    def progress_percent(self) -> float:
        """进度百分比 - 派生状态"""
        return (self.iteration / self.max_iterations) * 100


class TaskStateManager:
    """
    任务状态管理器 - 唯一写入点
    
    所有状态修改必须通过这个类，保证一致性
    """
    
    def __init__(self, db_path: str, event_bus: EventBus):
        self.db_path = db_path
        self.event_bus = event_bus
        self._cache: dict[str, TaskState] = {}  # 内存缓存
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_states (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    task_text TEXT,
                    target_hwnds TEXT,
                    iteration INTEGER DEFAULT 0,
                    max_iterations INTEGER DEFAULT 20,
                    created_at TEXT,
                    updated_at TEXT,
                    error_type TEXT,
                    error_message TEXT,
                    last_checkpoint_iteration INTEGER
                )
            """)
    
    async def create(self, task_id: str, task_text: str, target_hwnds: List[int], max_iterations: int = 20) -> TaskState:
        """创建任务"""
        now = datetime.now()
        state = TaskState(
            id=task_id,
            status=TaskStatus.PENDING,
            task_text=task_text,
            target_hwnds=target_hwnds,
            iteration=0,
            max_iterations=max_iterations,
            created_at=now,
            updated_at=now,
        )
        
        await self._save(state)
        await self._emit_change(state)
        return state
    
    async def transition(self, task_id: str, new_status: TaskStatus, **kwargs) -> TaskState:
        """
        状态转换 - 唯一的状态修改入口
        
        自动验证转换合法性、更新缓存、持久化、发送事件
        """
        state = await self.get(task_id)
        
        # 验证转换合法性
        if state.status.is_terminal:
            raise ValueError(f"Cannot transition from terminal state {state.status}")
        
        # 更新状态
        old_status = state.status
        state.status = new_status
        state.updated_at = datetime.now()
        
        # 更新额外字段
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        # 持久化
        await self._save(state)
        
        # 发送事件
        await self._emit_change(state, old_status)
        
        return state
    
    async def increment_iteration(self, task_id: str) -> TaskState:
        """增加迭代次数"""
        state = await self.get(task_id)
        state.iteration += 1
        state.updated_at = datetime.now()
        await self._save(state)
        
        # 发送进度事件
        await self.event_bus.emit(AgentEvent.create(
            EventType.PROGRESS_UPDATE,
            task_id,
            {"iteration": state.iteration, "max": state.max_iterations, "percent": state.progress_percent}
        ))
        
        return state
    
    async def get(self, task_id: str) -> TaskState:
        """获取任务状态"""
        if task_id in self._cache:
            return self._cache[task_id]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM task_states WHERE id = ?", (task_id,)).fetchone()
            
            if not row:
                raise ValueError(f"Task {task_id} not found")
            
            state = self._row_to_state(row)
            self._cache[task_id] = state
            return state
    
    async def list_recoverable(self) -> List[TaskState]:
        """列出可恢复的任务"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM task_states WHERE status IN (?, ?, ?)",
                (TaskStatus.NEEDS_HELP.value, TaskStatus.FAILED.value, TaskStatus.INTERRUPTED.value)
            ).fetchall()
            return [self._row_to_state(row) for row in rows]
    
    async def _save(self, state: TaskState):
        """保存到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO task_states 
                (id, status, task_text, target_hwnds, iteration, max_iterations, 
                 created_at, updated_at, error_type, error_message, last_checkpoint_iteration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.id, state.status.value, state.task_text, json.dumps(state.target_hwnds),
                state.iteration, state.max_iterations, state.created_at.isoformat(),
                state.updated_at.isoformat(), state.error_type, state.error_message,
                state.last_checkpoint_iteration
            ))
        
        self._cache[state.id] = state
    
    async def _emit_change(self, state: TaskState, old_status: Optional[TaskStatus] = None):
        """发送状态变更事件"""
        await self.event_bus.emit(AgentEvent.create(
            EventType.STATUS_CHANGED,
            state.id,
            {
                "old_status": old_status.value if old_status else None,
                "new_status": state.status.value,
                "iteration": state.iteration,
                "is_terminal": state.status.is_terminal,
                "can_resume": state.can_resume,
            }
        ))
    
    def _row_to_state(self, row) -> TaskState:
        """数据库行转状态对象"""
        return TaskState(
            id=row["id"],
            status=TaskStatus(row["status"]),
            task_text=row["task_text"],
            target_hwnds=json.loads(row["target_hwnds"]),
            iteration=row["iteration"],
            max_iterations=row["max_iterations"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            error_type=row["error_type"],
            error_message=row["error_message"],
            last_checkpoint_iteration=row["last_checkpoint_iteration"],
        )
```

**关键设计**：
- `TaskStateManager.transition()` 是唯一的状态修改入口
- 每次修改自动：验证 → 更新缓存 → 持久化 → 发送事件
- 其他组件（HostAgent、Overlay、前端）只能读取，不能直接修改

---

### Phase 1 改进: LLM 输出验证层（新增）

**问题**：计划假设 LLM 会按预期返回工具调用，但 LLM 可能返回不存在的工具、超出范围的坐标、格式错误的参数。

**解决方案**：参考 Anthropic computer-use 的 ToolError，在 LLM 和执行层之间加验证层。

```python
# nogicos/engine/agent/tool_validator.py

from dataclasses import dataclass
from typing import Optional, List, Any
from enum import Enum


class ValidationError(Exception):
    """验证错误基类"""
    pass


class ToolNotFoundError(ValidationError):
    """工具不存在"""
    pass


class CoordinateOutOfBoundsError(ValidationError):
    """坐标超出窗口范围"""
    pass


class InvalidArgumentError(ValidationError):
    """参数格式错误"""
    pass


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    error: Optional[ValidationError] = None
    corrected_args: Optional[dict] = None  # 自动修正后的参数（如坐标裁剪）
    warnings: List[str] = None


class ToolCallValidator:
    """
    工具调用验证器
    
    参考：Anthropic computer-use 的参数验证
    """
    
    def __init__(self, tool_registry, config):
        self.registry = tool_registry
        self.config = config
    
    async def validate(
        self, 
        tool_name: str, 
        tool_args: dict, 
        window_bounds: Optional[dict] = None
    ) -> ValidationResult:
        """
        验证工具调用
        
        Returns:
            ValidationResult: 包含验证结果、错误信息、修正后的参数
        """
        warnings = []
        corrected_args = tool_args.copy()
        
        # 1. 检查工具是否存在
        if not self.registry.has_tool(tool_name):
            return ValidationResult(
                is_valid=False,
                error=ToolNotFoundError(f"Tool '{tool_name}' not found. Available: {self.registry.list_tools()}")
            )
        
        tool_def = self.registry.get_tool(tool_name)
        
        # 2. 检查必需参数
        for param_name, param_def in tool_def.parameters.items():
            if param_def.required and param_name not in tool_args:
                return ValidationResult(
                    is_valid=False,
                    error=InvalidArgumentError(f"Missing required parameter: {param_name}")
                )
        
        # 3. 检查参数类型
        for param_name, value in tool_args.items():
            if param_name not in tool_def.parameters:
                warnings.append(f"Unknown parameter '{param_name}' will be ignored")
                continue
            
            expected_type = tool_def.parameters[param_name].type
            if not self._check_type(value, expected_type):
                return ValidationResult(
                    is_valid=False,
                    error=InvalidArgumentError(f"Parameter '{param_name}' expected {expected_type}, got {type(value).__name__}")
                )
        
        # 4. 坐标范围检查（如果是点击工具且有窗口边界）
        if tool_name in ("window_click", "desktop_click") and window_bounds:
            x, y = tool_args.get("x", 0), tool_args.get("y", 0)
            max_x, max_y = window_bounds.get("width", 1280), window_bounds.get("height", 800)
            
            # 检查是否超出范围
            if x < 0 or y < 0 or x > max_x or y > max_y:
                # 自动裁剪到边界（而不是直接拒绝）
                corrected_x = max(0, min(x, max_x))
                corrected_y = max(0, min(y, max_y))
                
                corrected_args["x"] = corrected_x
                corrected_args["y"] = corrected_y
                
                warnings.append(
                    f"Coordinates ({x}, {y}) out of bounds, corrected to ({corrected_x}, {corrected_y})"
                )
        
        # 5. hwnd 检查
        if tool_def.supports_hwnd and "hwnd" not in tool_args:
            return ValidationResult(
                is_valid=False,
                error=InvalidArgumentError(f"Tool '{tool_name}' requires 'hwnd' parameter for window isolation")
            )
        
        return ValidationResult(
            is_valid=True,
            corrected_args=corrected_args if corrected_args != tool_args else None,
            warnings=warnings if warnings else None
        )
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """类型检查"""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        expected = type_map.get(expected_type, object)
        return isinstance(value, expected)


class ToolResultHandler:
    """
    工具结果处理器
    
    参考：Anthropic computer-use 的 ToolFailure 处理
    """
    
    @staticmethod
    def to_llm_result(result: "ToolResult", validation: ValidationResult = None) -> dict:
        """
        将工具结果转换为 LLM 可理解的格式
        
        如果有错误，设置 is_error=True，让 LLM 知道并调整策略
        """
        content = []
        
        # 添加文本输出
        if result.output:
            content.append({"type": "text", "text": result.output})
        
        # 添加错误信息
        if result.error:
            content.append({
                "type": "text", 
                "text": f"ERROR: {result.error}\n\nPlease analyze what went wrong and try an alternative approach."
            })
        
        # 添加验证警告
        if validation and validation.warnings:
            content.append({
                "type": "text",
                "text": f"WARNINGS: {'; '.join(validation.warnings)}"
            })
        
        # 添加截图
        if result.base64_image:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": result.base64_image
                }
            })
        
        return {
            "type": "tool_result",
            "tool_use_id": result.tool_use_id,
            "content": content,
            "is_error": result.error is not None  # 关键：告诉 LLM 这是错误
        }
```

---

### Phase 3 改进: 成功/失败边界定义（新增）

**问题**：计划没有定义什么情况算成功/失败。

**解决方案**：定义明确的终止条件。

```python
# nogicos/engine/agent/termination.py

from dataclasses import dataclass
from typing import Optional, Callable, List
from enum import Enum


class TerminationReason(Enum):
    """终止原因"""
    # 成功
    TASK_COMPLETED = "task_completed"           # LLM 调用 set_task_status("completed")
    VERIFIED_SUCCESS = "verified_success"       # 通过验证截图确认完成
    
    # 失败（可恢复）
    NEEDS_HELP = "needs_help"                   # LLM 请求帮助
    MAX_ITERATIONS = "max_iterations"           # 达到最大迭代次数
    CONSECUTIVE_FAILURES = "consecutive_failures"  # 连续工具失败
    
    # 错误（不可恢复）
    WINDOW_LOST = "window_lost"                 # 目标窗口关闭
    CRITICAL_ERROR = "critical_error"           # 严重异常
    USER_CANCELLED = "user_cancelled"           # 用户主动取消


@dataclass
class TerminationCondition:
    """终止条件"""
    reason: TerminationReason
    triggered: bool
    details: Optional[str] = None


class TerminationChecker:
    """
    终止条件检查器
    
    每次迭代后检查是否应该终止
    """
    
    def __init__(self, config: "AgentConfig"):
        self.config = config
        self._consecutive_failures = 0
    
    async def check(
        self, 
        state: "TaskState",
        last_response: Optional[dict] = None,
        last_tool_results: Optional[List["ToolResult"]] = None,
        window_state: Optional[dict] = None,
    ) -> Optional[TerminationCondition]:
        """
        检查是否应该终止
        
        Returns:
            TerminationCondition if should terminate, None otherwise
        """
        
        # 1. LLM 主动完成
        if last_response and self._check_task_status_called(last_response, "completed"):
            return TerminationCondition(
                reason=TerminationReason.TASK_COMPLETED,
                triggered=True,
                details="LLM called set_task_status('completed')"
            )
        
        # 2. LLM 请求帮助
        if last_response and self._check_task_status_called(last_response, "needs_help"):
            return TerminationCondition(
                reason=TerminationReason.NEEDS_HELP,
                triggered=True,
                details=self._extract_help_reason(last_response)
            )
        
        # 3. 最大迭代次数
        if state.iteration >= state.max_iterations:
            return TerminationCondition(
                reason=TerminationReason.MAX_ITERATIONS,
                triggered=True,
                details=f"Reached max iterations: {state.max_iterations}"
            )
        
        # 4. 连续工具失败
        if last_tool_results:
            if all(r.error for r in last_tool_results):
                self._consecutive_failures += 1
            else:
                self._consecutive_failures = 0
            
            if self._consecutive_failures >= self.config.max_consecutive_failures:
                return TerminationCondition(
                    reason=TerminationReason.CONSECUTIVE_FAILURES,
                    triggered=True,
                    details=f"Failed {self._consecutive_failures} times consecutively"
                )
        
        # 5. 窗口丢失
        if window_state and not window_state.get("is_valid", True):
            return TerminationCondition(
                reason=TerminationReason.WINDOW_LOST,
                triggered=True,
                details="Target window is no longer available"
            )
        
        return None
    
    def _check_task_status_called(self, response: dict, status: str) -> bool:
        """检查是否调用了 set_task_status"""
        for tool_call in response.get("tool_calls", []):
            if tool_call.get("name") == "set_task_status":
                return tool_call.get("input", {}).get("status") == status
        return False
    
    def _extract_help_reason(self, response: dict) -> str:
        """提取请求帮助的原因"""
        for tool_call in response.get("tool_calls", []):
            if tool_call.get("name") == "set_task_status":
                return tool_call.get("input", {}).get("description", "No reason provided")
        return "Unknown"


class SuccessVerifier:
    """
    成功验证器
    
    LLM 说完成了，但真的完成了吗？
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def verify(
        self, 
        task_text: str, 
        final_screenshot: str,
        completion_description: str
    ) -> bool:
        """
        验证任务是否真的完成
        
        使用另一次 LLM 调用来验证
        """
        response = await self.llm.messages.create(
            model="claude-3-haiku-20240307",  # 用便宜的模型验证
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Based on the screenshot, verify if this task was completed successfully.

Task: {task_text}
Agent's completion claim: {completion_description}

Answer only "YES" or "NO" followed by a brief reason."""
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": final_screenshot
                        }
                    }
                ]
            }]
        )
        
        answer = response.content[0].text.strip().upper()
        return answer.startswith("YES")
```

---

### 并发模型改进

**问题**：当前 `window_locks` 粒度过粗（一个窗口一个锁）。

**解决方案**：更细粒度的锁 + 操作类型区分。

```python
# nogicos/engine/agent/concurrency.py

import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from enum import Enum


class LockType(Enum):
    """锁类型"""
    INPUT = "input"           # 输入操作（点击、输入）- 互斥
    SCREENSHOT = "screenshot" # 截图 - 可与其他截图并行
    FOCUS = "focus"           # 焦点切换 - 全局互斥


class WindowLockManager:
    """
    细粒度窗口锁管理器
    
    - 点击和输入需要互斥（不能同时点两个地方）
    - 截图可以并行（多个窗口同时截图）
    - 焦点切换全局互斥（任何时候只能有一个焦点操作）
    """
    
    def __init__(self):
        self._input_locks: dict[int, asyncio.Lock] = {}
        self._screenshot_semaphores: dict[int, asyncio.Semaphore] = {}
        self._focus_lock = asyncio.Lock()
        self._global_input_lock = asyncio.Lock()  # 防止跨窗口的输入混乱
    
    @asynccontextmanager
    async def input_lock(self, hwnd: int):
        """
        获取输入锁
        
        同一窗口的输入互斥，且全局输入也互斥（防止同时操作多窗口）
        """
        if hwnd not in self._input_locks:
            self._input_locks[hwnd] = asyncio.Lock()
        
        async with self._global_input_lock:
            async with self._input_locks[hwnd]:
                yield
    
    @asynccontextmanager
    async def screenshot_lock(self, hwnd: int, max_concurrent: int = 3):
        """
        获取截图锁
        
        同一窗口最多 3 个并发截图（防止资源耗尽），不同窗口可并行
        """
        if hwnd not in self._screenshot_semaphores:
            self._screenshot_semaphores[hwnd] = asyncio.Semaphore(max_concurrent)
        
        async with self._screenshot_semaphores[hwnd]:
            yield
    
    @asynccontextmanager
    async def focus_lock(self):
        """
        获取焦点锁
        
        全局互斥，任何时候只能有一个焦点切换
        """
        async with self._focus_lock:
            yield


class TaskSlotManager:
    """任务槽位管理"""
    
    def __init__(self, max_concurrent_tasks: int = 3):
        self.max_tasks = max_concurrent_tasks
        self._active_tasks: set[str] = set()
        self._task_windows: dict[str, set[int]] = {}  # task_id -> hwnd set
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
    
    async def acquire(self, task_id: str, target_hwnds: list[int]) -> bool:
        """
        获取任务槽位
        
        检查：
        1. 总任务数不超过上限
        2. 目标窗口没有被其他任务占用
        """
        # 检查窗口冲突
        for hwnd in target_hwnds:
            for other_task, other_hwnds in self._task_windows.items():
                if hwnd in other_hwnds:
                    return False  # 窗口被占用
        
        # 获取槽位
        if len(self._active_tasks) >= self.max_tasks:
            return False
        
        self._active_tasks.add(task_id)
        self._task_windows[task_id] = set(target_hwnds)
        return True
    
    def release(self, task_id: str):
        """释放任务槽位"""
        self._active_tasks.discard(task_id)
        self._task_windows.pop(task_id, None)
```

---

## 📋 修改后的 Phase 列表

| Phase | 内容 | 时间 | 状态 |
|-------|------|------|------|
| **0** | **通信契约层（AgentEvent、EventBus）** | **1天** | **新增** |
| **0.5** | **状态真相源（TaskStateManager）** | **0.5天** | **新增** |
| 1 | 核心数据结构 + 配置管理 + **验证器** | 2天 | 扩展 |
| 2 | 双层 Agent 架构 + 状态持久化 | 2.5天 | 不变 |
| 3 | Agent 循环 + 错误恢复 + 并发控制 + **终止条件** | 3.5天 | 扩展 |
| 4 | 工具系统 | 2天 | 不变 |
| 5 | LLM 集成 | 2天 | 不变 |
| 5a | Prompt Engineering | 1天 | 不变 |
| 5b | 上下文压缩 | 0.5天 | 不变 |
| 5c | 视觉增强 | 1天 | 不变 |
| 6 | 后端 API + **EventBus 集成** | 1.5天 | 扩展 |
| 7 | 前端集成 + **EventBus 订阅** | 3天 | 扩展 |
| 8 | 评估系统 | 1天 | 不变 |
| 9 | 迁移策略 | 1天 | 不变 |
| 10 | 调试与审计 | 1天 | 不变 |

**总计**: 20.5天 → **23天**（增加 2.5天）

---

## 🎯 架构改进总结

### 已解决的问题

| 问题 | 解决方案 |
|------|----------|
| 三种通信方式格式不统一 | `AgentEvent` + `EventBus` 统一格式 |
| 状态分散不一致 | `TaskStateManager` 单一真相源 |
| LLM 输出未验证 | `ToolCallValidator` 验证层 |
| 成功/失败无定义 | `TerminationChecker` + `SuccessVerifier` |
| 锁粒度过粗 | `WindowLockManager` 按操作类型分锁 |
| ERROR vs FAIL 未区分 | `TaskStatus` 枚举明确定义 |

### 保留的优势

- Hook 系统 ✅
- Multi-Overlay ✅
- PostMessage 窗口隔离 ✅
- @registry.action 装饰器 ✅
- Checkpointer 持久化 ✅

### 参考来源

| 改进点 | 参考来源 |
|-------|----------|
| AgentEvent 格式 | UFO AIP L1 Message Schema |
| EventBus | UFO AIP L3 Protocol Orchestration |
| ERROR vs FAIL | UFO 状态机设计 |
| ToolError → is_error | Anthropic computer-use |
| Checkpointer 模式 | LangGraph SqliteSaver |
| interrupt() 人机交互 | LangGraph Human-in-the-loop |

---

## 🚀 实施建议

### 优先级排序

1. **Phase 0 (通信契约)** - 先做，因为后续所有 Phase 都会用到
2. **Phase 0.5 (状态真相源)** - 紧随其后，确保状态一致性
3. **Phase 1-3** - 核心功能
4. **其他 Phase** - 按依赖关系

### Demo 优先策略

如果时间紧迫，可以先实现 Phase 0 的**简化版**：

```python
# 简化版 - 只统一格式，不做完整的 EventBus
@dataclass
class AgentEvent:
    type: str
    payload: dict
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self):
        return {"type": self.type, "payload": self.payload, "ts": self.timestamp}
```

这样可以在 3 小时内完成，后续再扩展。
