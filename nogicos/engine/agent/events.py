"""
NogicOS Agent EventSystem
========================

定义统一的EventClass型和Message格式，解决Module间耦合问题。

参考:
- UFO Agent Interaction Protocol (AIP) 五层Protocol
- LangGraph Checkpointer Event模型
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Any, Dict
import time
import uuid


class EventType(Enum):
    """
    EventClass型枚举 - 不Allow随意Character串
    
    所有Event必须Usage预定义的Class型，确保Class型Security和可追踪性
    """
    
    # ========== TasklifeCycle ==========
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_INTERRUPTED = "task.interrupted"
    TASK_PAUSED = "task.paused"
    TASK_RESUMED = "task.resumed"
    TASK_CANCELLED = "task.cancelled"
    
    # ========== Agent State ==========
    AGENT_THINKING = "agent.thinking"
    AGENT_PLANNING = "agent.planning"
    AGENT_EXECUTING = "agent.executing"
    AGENT_WAITING = "agent.waiting"
    AGENT_IDLE = "agent.idle"
    AGENT_NEEDS_HELP = "agent.needs_help"  # Needmanualbetweenenter（withsensitiveConfirmsemanticDetach）
    
    # ========== ToolCall ==========
    TOOL_START = "tool.start"
    TOOL_END = "tool.end"
    TOOL_ERROR = "tool.error"
    TOOL_RETRY = "tool.retry"
    
    # ========== Userinteract ==========
    USER_CONFIRM_REQUIRED = "user.confirm_required"
    USER_CONFIRM_RESPONSE = "user.confirm_response"
    USER_TAKEOVER = "user.takeover"
    USER_INPUT = "user.input"
    
    # ========== SystemEvent ==========
    SCREENSHOT_CAPTURED = "system.screenshot"
    CONTEXT_COMPRESSED = "system.context_compressed"
    CHECKPOINT_SAVED = "system.checkpoint_saved"
    CHECKPOINT_RESTORED = "system.checkpoint_restored"
    
    # ========== LLM Event ==========
    LLM_REQUEST_START = "llm.request_start"
    LLM_RESPONSE_CHUNK = "llm.response_chunk"
    LLM_RESPONSE_END = "llm.response_end"
    LLM_ERROR = "llm.error"
    
    # ========== Overlay Event ==========
    OVERLAY_CONNECTED = "overlay.connected"
    OVERLAY_DISCONNECTED = "overlay.disconnected"
    OVERLAY_STATUS_UPDATE = "overlay.status_update"


class EventPriority(Enum):
    """EventPriority级 - 用于背压控制"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class AgentEvent:
    """
    统一Event格式
    
    所有Module间的通信都应该Usage AgentEvent，确保：
    1. 可追踪性（每个Event有唯一 ID）
    2. 可Serialize（支持 JSON 传输）
    3. Class型Security（Usage枚举Class型）
    4. Off联性（通过 task_id Off联任务）
    """
    
    id: str                          # Unique ID
    type: EventType                  # EventClasstype（Enum，notYesCharacterstring）
    task_id: str                     # OffconnectTask
    timestamp: float                 # Unix Timestamp
    payload: Dict[str, Any]          # EventData
    source: str = "host_agent"       # EventfromSource
    target: Optional[str] = None     # Target（Optional）
    priority: EventPriority = EventPriority.NORMAL  # Prioritylevel
    correlation_id: Optional[str] = None  # Offconnect ID（fortrackbecauseresult chain）
    
    @classmethod
    def create(
        cls, 
        event_type: EventType, 
        task_id: str, 
        payload: Dict[str, Any],
        source: str = "host_agent",
        target: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None,
    ) -> "AgentEvent":
        """工厂Method：CreateNewEvent"""
        return cls(
            id=str(uuid.uuid4()),
            type=event_type,
            task_id=task_id,
            timestamp=time.time(),
            payload=payload,
            source=source,
            target=target,
            priority=priority,
            correlation_id=correlation_id,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize为Dict
        
        用于 WebSocket/IPC 传输，枚举转为Character串值
        """
        return {
            "id": self.id,
            "type": self.type.value,  # EnumturnCharacterstring
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "source": self.source,
            "target": self.target,
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentEvent":
        """
        从Dict反Serialize
        
        用于ReceiveOuter部Message时重建EventObject
        """
        return cls(
            id=data["id"],
            type=EventType(data["type"]),  # CharacterstringturnEnum
            task_id=data["task_id"],
            timestamp=data["timestamp"],
            payload=data["payload"],
            source=data.get("source", "unknown"),
            target=data.get("target"),
            priority=EventPriority(data.get("priority", 1)),
            correlation_id=data.get("correlation_id"),
        )
    
    def with_correlation(self, correlation_id: str) -> "AgentEvent":
        """Create带Off联 ID 的NewEvent（用于追踪因果链）"""
        return AgentEvent(
            id=self.id,
            type=self.type,
            task_id=self.task_id,
            timestamp=self.timestamp,
            payload=self.payload,
            source=self.source,
            target=self.target,
            priority=self.priority,
            correlation_id=correlation_id,
        )
    
    def __repr__(self) -> str:
        return f"AgentEvent(type={self.type.value}, task_id={self.task_id[:8]}..., source={self.source})"


# ========== convenientFactoryFunction ==========

def task_started_event(task_id: str, task_description: str) -> AgentEvent:
    """Create任务BeginEvent"""
    return AgentEvent.create(
        EventType.TASK_STARTED,
        task_id,
        {"description": task_description},
    )


def task_completed_event(task_id: str, result: str) -> AgentEvent:
    """Create任务CompleteEvent"""
    return AgentEvent.create(
        EventType.TASK_COMPLETED,
        task_id,
        {"result": result},
    )


def task_failed_event(task_id: str, error: str, recoverable: bool = False) -> AgentEvent:
    """Create任务FailedEvent"""
    return AgentEvent.create(
        EventType.TASK_FAILED,
        task_id,
        {"error": error, "recoverable": recoverable},
        priority=EventPriority.HIGH,
    )


def tool_start_event(task_id: str, tool_name: str, args: Dict[str, Any]) -> AgentEvent:
    """CreateToolBeginExecuteEvent"""
    return AgentEvent.create(
        EventType.TOOL_START,
        task_id,
        {"tool_name": tool_name, "args": args},
    )


def tool_end_event(task_id: str, tool_name: str, result: Any, duration_ms: float) -> AgentEvent:
    """CreateToolExecuteCompleteEvent"""
    return AgentEvent.create(
        EventType.TOOL_END,
        task_id,
        {"tool_name": tool_name, "result": result, "duration_ms": duration_ms},
    )


def tool_error_event(task_id: str, tool_name: str, error: str) -> AgentEvent:
    """CreateToolExecuteErrorEvent"""
    return AgentEvent.create(
        EventType.TOOL_ERROR,
        task_id,
        {"tool_name": tool_name, "error": error},
        priority=EventPriority.HIGH,
    )


def confirm_required_event(
    task_id: str, 
    action_id: str, 
    action_description: str,
    risk_level: str = "medium",
) -> AgentEvent:
    """Create需要UserConfirmEvent"""
    return AgentEvent.create(
        EventType.USER_CONFIRM_REQUIRED,
        task_id,
        {
            "action_id": action_id,
            "description": action_description,
            "risk_level": risk_level,
        },
        priority=EventPriority.CRITICAL,
    )


def llm_chunk_event(task_id: str, chunk: str, token_count: int = 0) -> AgentEvent:
    """Create LLM Response块Event（用于流式Output）"""
    return AgentEvent.create(
        EventType.LLM_RESPONSE_CHUNK,
        task_id,
        {"chunk": chunk, "token_count": token_count},
    )
