"""
NogicOS Agent Error分Class
======================

定义 Agent System的Error层级，区分可Resume和不可ResumeError。

参考:
- UFO ERROR vs FAIL State区分
- ByteBot ErrorHandlePolicy
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any


class ErrorSeverity(Enum):
    """Error严重级别"""
    WARNING = "warning"      # Warning，notaffectExecute
    ERROR = "error"          # Error，canRetry/Downgrade
    CRITICAL = "critical"    # severeError，NeedStop
    FATAL = "fatal"          # causelifeError，urgentStop


class ErrorCategory(Enum):
    """Error分Class"""
    LLM = "llm"              # LLM relatedOffError
    TOOL = "tool"            # ToolExecuteError
    WINDOW = "window"        # WindowrelatedOffError
    NETWORK = "network"      # NetworkError
    STATE = "state"          # StatemanageError
    CONCURRENCY = "concurrency"  # ConcurrentcontrolError
    SECURITY = "security"    # SecurityError
    VALIDATION = "validation"  # VerifyError
    UNKNOWN = "unknown"      # UnknownError


class AgentError(Exception):
    """
    Agent Error基Class
    
    所有 Agent 相OffError都应Inherit此Class，提供：
    - YesNo可Resume标识
    - Error分Class
    - Retry建议
    """
    
    recoverable: bool = True
    category: ErrorCategory = ErrorCategory.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.ERROR
    
    def __init__(
        self, 
        message: str,
        details: Optional[dict] = None,
        cause: Optional[Exception] = None,
    ):
        """
        InitializeError
        
        Args:
            message: ErrorMessage
            details: Attach详情
            cause: OriginalException
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
    
    def to_dict(self) -> dict:
        """Serialize为Dict"""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "recoverable": self.recoverable,
            "details": self.details,
        }
    
    @property
    def should_retry(self) -> bool:
        """YesNo应该Retry"""
        return self.recoverable and self.severity != ErrorSeverity.FATAL
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, recoverable={self.recoverable})"


# ========== LLM relatedOffError ==========

class LLMError(AgentError):
    """LLM Error基Class"""
    category = ErrorCategory.LLM


class ClaudeAPIError(LLMError):
    """
    Claude API Error（可Retry）
    
    Package括：
    - 速率Limit
    - Service器Error
    - Timeout
    """
    recoverable = True
    severity = ErrorSeverity.ERROR
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.retry_after = retry_after
        self.details["status_code"] = status_code
        self.details["retry_after"] = retry_after


class RateLimitError(ClaudeAPIError):
    """速率LimitError"""
    
    def __init__(self, message: str = "API rate limit exceeded", **kwargs):
        super().__init__(message, **kwargs)


class TokenLimitError(LLMError):
    """Token LimitError"""
    recoverable = True  # canthroughCompressUpDowntextResume
    
    def __init__(
        self, 
        message: str = "Context exceeds token limit",
        current_tokens: int = 0,
        max_tokens: int = 0,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.current_tokens = current_tokens
        self.max_tokens = max_tokens
        self.details["current_tokens"] = current_tokens
        self.details["max_tokens"] = max_tokens


class LLMResponseError(LLMError):
    """LLM ResponseParseError"""
    recoverable = True
    
    def __init__(self, message: str, raw_response: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.raw_response = raw_response
        self.details["raw_response"] = raw_response[:500] if raw_response else None


# ========== ToolExecuteError ==========

class ToolError(AgentError):
    """ToolError基Class"""
    category = ErrorCategory.TOOL


class ToolExecutionError(ToolError):
    """
    ToolExecuteError（可Downgrade）
    
    ToolExecuteFailed，但可以让 LLM 知道并调整Policy
    """
    recoverable = True
    severity = ErrorSeverity.ERROR
    
    def __init__(
        self, 
        message: str, 
        tool_name: str,
        tool_args: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.details["tool_name"] = tool_name
        self.details["tool_args"] = tool_args


class ToolNotFoundError(ToolError):
    """Tool不存在Error"""
    recoverable = True  # Cannotify LLM heavyNewSelect
    
    def __init__(self, tool_name: str, **kwargs):
        super().__init__(f"Tool '{tool_name}' not found", **kwargs)
        self.tool_name = tool_name
        self.details["tool_name"] = tool_name


class ToolValidationError(ToolError):
    """ToolArgumentVerifyError"""
    recoverable = True
    category = ErrorCategory.VALIDATION
    
    def __init__(
        self, 
        message: str,
        tool_name: str,
        validation_errors: Optional[list] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name
        self.validation_errors = validation_errors or []
        self.details["tool_name"] = tool_name
        self.details["validation_errors"] = validation_errors


class ToolTimeoutError(ToolError):
    """ToolExecuteTimeout"""
    recoverable = True
    
    def __init__(
        self, 
        tool_name: str, 
        timeout_ms: int,
        **kwargs,
    ):
        super().__init__(
            f"Tool '{tool_name}' timed out after {timeout_ms}ms",
            **kwargs,
        )
        self.tool_name = tool_name
        self.timeout_ms = timeout_ms
        self.details["tool_name"] = tool_name
        self.details["timeout_ms"] = timeout_ms


# ========== WindowrelatedOffError ==========

class WindowError(AgentError):
    """WindowError基Class"""
    category = ErrorCategory.WINDOW


class WindowLostError(WindowError):
    """
    TargetWindow丢失（不可Resume）
    
    Window已Close或不可visit，任务无法继continued
    """
    recoverable = False
    severity = ErrorSeverity.CRITICAL
    
    def __init__(self, hwnd: int, window_title: Optional[str] = None, **kwargs):
        message = f"Window lost: hwnd={hwnd}"
        if window_title:
            message += f" ('{window_title}')"
        super().__init__(message, **kwargs)
        self.hwnd = hwnd
        self.window_title = window_title
        self.details["hwnd"] = hwnd
        self.details["window_title"] = window_title


class WindowNotFocusableError(WindowError):
    """Window无法Get焦点"""
    recoverable = True
    
    def __init__(self, hwnd: int, reason: str = "", **kwargs):
        super().__init__(f"Window {hwnd} cannot be focused: {reason}", **kwargs)
        self.hwnd = hwnd
        self.details["hwnd"] = hwnd
        self.details["reason"] = reason


class WindowLockedError(WindowError):
    """Window被其他任务Lock定"""
    recoverable = True  # CanWait
    
    def __init__(self, hwnd: int, locked_by: str, **kwargs):
        super().__init__(
            f"Window {hwnd} is locked by task '{locked_by}'",
            **kwargs,
        )
        self.hwnd = hwnd
        self.locked_by = locked_by
        self.details["hwnd"] = hwnd
        self.details["locked_by"] = locked_by


# ========== StatemanageError ==========

class StateError(AgentError):
    """State管理Error基Class"""
    category = ErrorCategory.STATE


class InvalidStateTransitionError(StateError):
    """非法StateConvert"""
    recoverable = False
    
    def __init__(
        self, 
        current_state: str, 
        target_state: str,
        valid_targets: Optional[list] = None,
        **kwargs,
    ):
        super().__init__(
            f"Invalid transition: {current_state} -> {target_state}",
            **kwargs,
        )
        self.current_state = current_state
        self.target_state = target_state
        self.valid_targets = valid_targets or []
        self.details["current_state"] = current_state
        self.details["target_state"] = target_state
        self.details["valid_targets"] = valid_targets


class TaskNotFoundError(StateError):
    """任务不存在"""
    recoverable = False
    
    def __init__(self, task_id: str, **kwargs):
        super().__init__(f"Task '{task_id}' not found", **kwargs)
        self.task_id = task_id
        self.details["task_id"] = task_id


class CheckpointError(StateError):
    """Check点Error"""
    recoverable = True


# ========== ConcurrentcontrolError ==========

class ConcurrencyError(AgentError):
    """Concurrent控制Error基Class"""
    category = ErrorCategory.CONCURRENCY


class TooManyTasksError(ConcurrencyError):
    """
    任务过多（Wait）
    
    已达到MaxConcurrent任务数，需要Wait
    """
    recoverable = True
    severity = ErrorSeverity.WARNING
    
    def __init__(
        self, 
        current_count: int, 
        max_count: int,
        **kwargs,
    ):
        super().__init__(
            f"Too many tasks: {current_count}/{max_count}",
            **kwargs,
        )
        self.current_count = current_count
        self.max_count = max_count
        self.details["current_count"] = current_count
        self.details["max_count"] = max_count


class ResourceLockError(ConcurrencyError):
    """资SourceLock定Error"""
    recoverable = True
    
    def __init__(self, resource: str, **kwargs):
        super().__init__(f"Resource '{resource}' is locked", **kwargs)
        self.resource = resource
        self.details["resource"] = resource


# ========== SecurityError ==========

class SecurityError(AgentError):
    """SecurityError基Class"""
    category = ErrorCategory.SECURITY
    recoverable = False
    severity = ErrorSeverity.CRITICAL


class UnauthorizedActionError(SecurityError):
    """未Authorization操作"""
    
    def __init__(self, action: str, reason: str = "", **kwargs):
        super().__init__(f"Unauthorized action '{action}': {reason}", **kwargs)
        self.action = action
        self.details["action"] = action
        self.details["reason"] = reason


class SensitiveOperationDeniedError(SecurityError):
    """敏感操作被Reject"""
    
    def __init__(self, operation: str, **kwargs):
        super().__init__(
            f"Sensitive operation '{operation}' requires user confirmation",
            **kwargs,
        )
        self.operation = operation
        self.details["operation"] = operation


class PromptInjectionError(SecurityError):
    """Prompt 注入检测"""
    severity = ErrorSeverity.FATAL
    
    def __init__(self, detected_pattern: str = "", **kwargs):
        super().__init__("Potential prompt injection detected", **kwargs)
        self.detected_pattern = detected_pattern
        self.details["detected_pattern"] = detected_pattern[:100]  # LimitLength


# ========== severeError ==========

class CriticalError(AgentError):
    """
    严重Error（紧急Stop）
    
    需要ImmediateStop任务，SaveState
    """
    recoverable = False
    severity = ErrorSeverity.CRITICAL
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


class FatalError(AgentError):
    """
    致命Error
    
    System级Error，需要人工介入
    """
    recoverable = False
    severity = ErrorSeverity.FATAL


# ========== ErrorResumePolicy ==========

@dataclass
class RecoveryStrategy:
    """ErrorResumePolicy"""
    retry: bool = False           # YesNoRetry
    max_retries: int = 3          # MaxRetrycount
    backoff_base: float = 2.0     # backoffbasenumber（Second）
    fallback: Optional[str] = None  # DowngradePolicy
    notify_user: bool = False     # YesNoNotifyUser


def get_recovery_strategy(error: AgentError) -> RecoveryStrategy:
    """
    Root据ErrorClass型GetResumePolicy
    
    Args:
        error: Agent Error
        
    Returns:
        ResumePolicy
    """
    if isinstance(error, RateLimitError):
        return RecoveryStrategy(
            retry=True,
            max_retries=5,
            backoff_base=error.retry_after or 5.0,
        )
    
    elif isinstance(error, ClaudeAPIError):
        return RecoveryStrategy(
            retry=True,
            max_retries=3,
            backoff_base=2.0,
        )
    
    elif isinstance(error, TokenLimitError):
        return RecoveryStrategy(
            retry=True,
            max_retries=1,
            fallback="compress_context",
        )
    
    elif isinstance(error, ToolExecutionError):
        return RecoveryStrategy(
            retry=True,
            max_retries=2,
            fallback="inform_llm",
        )
    
    elif isinstance(error, WindowLostError):
        return RecoveryStrategy(
            retry=False,
            notify_user=True,
        )
    
    elif isinstance(error, TooManyTasksError):
        return RecoveryStrategy(
            retry=True,
            max_retries=10,
            backoff_base=1.0,
        )
    
    elif isinstance(error, SecurityError):
        return RecoveryStrategy(
            retry=False,
            notify_user=True,
        )
    
    elif error.recoverable:
        return RecoveryStrategy(retry=True, max_retries=2)
    
    else:
        return RecoveryStrategy(retry=False, notify_user=True)
