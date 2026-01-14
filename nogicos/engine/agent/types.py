"""
NogicOS Core数据Class型
====================

定义 Agent System的Core数据结构。

Class型:
- TaskStatus: 任务State（参考 ByteBot）
- AgentStatus: Agent State（参考 UFO）
- ToolResult: ToolExecuteResult（参考 Anthropic）
- ToolCall: Tool调用Request
- Message: Message格式

参考:
- Anthropic Computer Use ToolResult
- ByteBot TaskStatus
- LangGraph Message
- UFO Agent Status
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import json


# ========== StateEnum（systemonedefinePosition）==========

class TaskStatus(Enum):
    """
    任务State - 参考 ByteBot
    
    State流转:
    PENDING -> RUNNING -> COMPLETED/FAILED/NEEDS_HELP
    RUNNING -> PAUSED -> RUNNING
    RUNNING -> INTERRUPTED -> RUNNING/CANCELLED
    """
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    NEEDS_HELP = "needs_help"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"


class AgentStatus(Enum):
    """
    Agent State - 参考 UFO
    
    IDLE: Empty闲，Wait任务
    ACTIVE: 正在Execute
    PAUSED: PauseMedium
    CONFIRM: WaitUserConfirm
    """
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    CONFIRM = "confirm"


# ========== ToolrelatedOffClasstype ==========

@dataclass(frozen=True)
class ToolResult:
    """
    ToolExecuteResult - 参考 Anthropic
    
    不可变数据Class，确保Result不会被意OuterModify
    
    Property:
        output: Success时的Output文本
        error: Error时的ErrorInfo
        base64_image: 截Graph数据 (base64 编码)
        hwnd: 来SourceWindow句柄 (NogicOS 独有)
        duration_ms: ExecuteTime (毫Second)
    """
    output: Optional[str] = None
    error: Optional[str] = None
    base64_image: Optional[str] = None
    hwnd: Optional[int] = None  # NogicOS alonehave
    duration_ms: float = 0.0
    
    @property
    def is_error(self) -> bool:
        """YesNo为ErrorResult"""
        return self.error is not None
    
    @property
    def is_success(self) -> bool:
        """YesNoSuccess"""
        return self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert为Dict"""
        result = {}
        if self.output is not None:
            result["output"] = self.output
        if self.error is not None:
            result["error"] = self.error
        if self.base64_image is not None:
            result["base64_image"] = self.base64_image
        if self.hwnd is not None:
            result["hwnd"] = self.hwnd
        if self.duration_ms > 0:
            result["duration_ms"] = self.duration_ms
        return result
    
    @classmethod
    def success(
        cls, 
        output: str, 
        base64_image: Optional[str] = None,
        hwnd: Optional[int] = None,
        duration_ms: float = 0.0,
    ) -> "ToolResult":
        """CreateSuccessResult"""
        return cls(
            output=output,
            base64_image=base64_image,
            hwnd=hwnd,
            duration_ms=duration_ms,
        )
    
    @classmethod
    def failure(
        cls, 
        error: str,
        hwnd: Optional[int] = None,
        duration_ms: float = 0.0,
    ) -> "ToolResult":
        """CreateFailedResult"""
        return cls(
            error=error,
            hwnd=hwnd,
            duration_ms=duration_ms,
        )


@dataclass
class ToolCall:
    """
    Tool调用Request
    
    从 LLM ResponseMediumParse出的Tool调用
    """
    id: str                          # Call ID
    name: str                        # Toolname
    arguments: Dict[str, Any]        # ArgumentDict
    hwnd: Optional[int] = None       # TargetWindow (Optional)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert为Dict"""
        return {
            "id": self.id,
            "name": self.name,
            "arguments": self.arguments,
            "hwnd": self.hwnd,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCall":
        """从DictCreate"""
        return cls(
            id=data["id"],
            name=data["name"],
            arguments=data.get("arguments", {}),
            hwnd=data.get("hwnd"),
        )


# ========== MessageClasstype ==========

class MessageRole(Enum):
    """MessageRole"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    """
    Message格式 - 对齐 LangGraph
    
    支持文本、Graph片、Tool调用、ToolResult等Inner容Class型
    """
    role: MessageRole
    content: Union[str, List[Dict[str, Any]]]
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None  # ToolResultOffconnect's Call ID
    name: Optional[str] = None          # Toolname（role=tool time）
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert为 Claude API 格式"""
        result = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.tool_calls:
            result["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.name:
            result["name"] = self.name
        return result
    
    @classmethod
    def user(cls, content: str) -> "Message":
        """CreateUserMessage"""
        return cls(role=MessageRole.USER, content=content)
    
    @classmethod
    def assistant(
        cls, 
        content: str, 
        tool_calls: Optional[List[ToolCall]] = None,
    ) -> "Message":
        """Create助手Message"""
        return cls(role=MessageRole.ASSISTANT, content=content, tool_calls=tool_calls)
    
    @classmethod
    def tool(cls, tool_call_id: str, name: str, content: str) -> "Message":
        """CreateToolResultMessage"""
        return cls(
            role=MessageRole.TOOL,
            content=content,
            tool_call_id=tool_call_id,
            name=name,
        )
    
    @classmethod
    def system(cls, content: str) -> "Message":
        """CreateSystemMessage"""
        return cls(role=MessageRole.SYSTEM, content=content)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """
        从Dict反Serialize - 用于Check点Resume
        
        Args:
            data: Serialize的MessageDict
            
        Returns:
            Message Instance
        """
        # ParseRole
        role_str = data.get("role", "user")
        try:
            role = MessageRole(role_str)
        except ValueError:
            role = MessageRole.USER
        
        # ParseInnercontent
        content = data.get("content", "")
        
        # ParseToolCall
        tool_calls = None
        if "tool_calls" in data and data["tool_calls"]:
            tool_calls = [
                ToolCall.from_dict(tc) if isinstance(tc, dict) else tc
                for tc in data["tool_calls"]
            ]
        
        return cls(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=data.get("tool_call_id"),
            name=data.get("name"),
        )


# ========== UpDowntextClasstype ==========

@dataclass
class WindowContext:
    """
    WindowUpDown文 - NogicOS 独有
    
    描述TargetWindow的当BeforeState
    """
    hwnd: int
    title: str
    app_type: str  # "browser", "desktop", "ide"
    bounds: Dict[str, int]  # x, y, width, height
    is_foreground: bool
    screenshot_id: Optional[str] = None
    ocr_text: Optional[str] = None
    ui_elements: Optional[List[Dict[str, Any]]] = None


@dataclass
class AgentContext:
    """
    Agent UpDown文
    
    Package含Execute任务所需的所有UpDown文Info
    """
    task_id: str
    task_text: str
    windows: List[WindowContext]
    messages: List[Message]
    iteration: int = 0
    current_hwnd: Optional[int] = None
    
    def get_current_window(self) -> Optional[WindowContext]:
        """Get当BeforeWindowUpDown文"""
        if self.current_hwnd is None:
            return None
        for w in self.windows:
            if w.hwnd == self.current_hwnd:
                return w
        return None


# ========== TooldefineClasstype ==========

@dataclass
class ToolParameter:
    """ToolArgument定义"""
    name: str
    type: str  # "string", "integer", "number", "boolean", "array", "object"
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    default: Optional[Any] = None


@dataclass
class ToolDefinition:
    """
    Tool定义 - 用于生成 Claude API 格式
    
    参考 Anthropic tool schema
    """
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    supports_hwnd: bool = False      # YesNoSupportWindowIsolation
    is_sensitive: bool = False       # YesNoforsensitiveAction
    category: str = "general"        # ToolminuteClass
    
    def to_claude_schema(self) -> Dict[str, Any]:
        """Convert为 Claude API Tool定义格式"""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            properties[param.name] = prop
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }


# ========== ResponseClasstype ==========

class StopReason(Enum):
    """Stop原因"""
    END_TURN = "end_turn"       # normalEnd
    TOOL_USE = "tool_use"       # NeedExecuteTool
    MAX_TOKENS = "max_tokens"   # reachto token Limit
    STOP_SEQUENCE = "stop_sequence"  # encountertoStoporderColumn


@dataclass
class LLMResponse:
    """
    LLM Response
    
    封装 Claude API Response
    """
    content: str
    stop_reason: StopReason
    tool_calls: List[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    is_fallback: bool = False  # YesNoforstreamingFailedAfter's FallbackResponse
    
    @property
    def needs_tool_execution(self) -> bool:
        """YesNo需要ExecuteTool"""
        return self.stop_reason == StopReason.TOOL_USE and len(self.tool_calls) > 0
    
    @property
    def is_final(self) -> bool:
        """YesNo为FinalResponse"""
        return self.stop_reason == StopReason.END_TURN


# ========== Classtypeothername ==========

# MessageHistory
MessageHistory = List[Message]

# ToolResultMap
ToolResultMap = Dict[str, ToolResult]

# Windowhandle
HWND = int
