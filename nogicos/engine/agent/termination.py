"""
NogicOS TerminateCheck器 + SuccessVerify器
==============================

定义清晰的任务TerminateCondition，区分 ERROR vs FAIL：

- TerminationChecker: Judge Agent LoopYesNo应该Terminate
- SuccessVerifier: Verify任务YesNoTrue正Complete（Agent 说Complete不一定TrueComplete）

参考:
- ByteBot set_task_status + termination 逻辑
- UFO ERROR vs FAIL State区分
- UFO AppAgent 可Resume FAIL vs HostAgent 终态 ERROR
"""

import logging
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Protocol, TYPE_CHECKING
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from .types import ToolResult

logger = logging.getLogger(__name__)


class TerminationReason(Enum):
    """
    Terminate原因
    
    区分正常Terminate和ExceptionTerminate
    """
    # ===== normalTerminate =====
    COMPLETED = "completed"           # TasknormalComplete
    NEEDS_HELP = "needs_help"         # Agent RequestUserHelp
    
    # ===== resourceSourceLimit =====
    MAX_ITERATIONS = "max_iterations" # reachtoMaxIteratecount
    TIMEOUT = "timeout"               # TaskTimeout
    TOKEN_LIMIT = "token_limit"       # Token Limit
    
    # ===== FailedTerminate =====
    CONSECUTIVE_FAILURES = "consecutive_failures"  # continuousFailedovermultiple
    WINDOW_LOST = "window_lost"       # TargetWindowlost
    CRITICAL_ERROR = "critical_error" # severeError
    
    # ===== Usercontrol =====
    USER_CANCELLED = "user_cancelled" # UserCancel
    USER_PAUSED = "user_paused"       # UserPause


class TerminationType(Enum):
    """TerminateClass型 - 区分 ERROR vs FAIL"""
    SUCCESS = "success"     # SuccessComplete
    FAIL = "fail"           # logicFailed（maybecanRetry）
    ERROR = "error"         # SystemError（notcanResume）
    CANCELLED = "cancelled" # UserCancel


@dataclass
class TerminationResult:
    """
    TerminateCheckResult
    
    Package含YesNo应该Terminate、原因、Class型等Info
    """
    should_terminate: bool
    reason: Optional[TerminationReason] = None
    termination_type: Optional[TerminationType] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def continue_running(cls) -> "TerminationResult":
        """继continuedRunning"""
        return cls(should_terminate=False, message="Continue")
    
    @classmethod
    def completed(cls, message: str = "Task completed") -> "TerminationResult":
        """任务Complete"""
        return cls(
            should_terminate=True,
            reason=TerminationReason.COMPLETED,
            termination_type=TerminationType.SUCCESS,
            message=message,
        )
    
    @classmethod
    def failed(
        cls, 
        reason: TerminationReason, 
        message: str,
        details: Optional[Dict] = None,
    ) -> "TerminationResult":
        """任务Failed"""
        return cls(
            should_terminate=True,
            reason=reason,
            termination_type=TerminationType.FAIL,
            message=message,
            details=details or {},
        )
    
    @classmethod
    def error(
        cls, 
        reason: TerminationReason, 
        message: str,
        details: Optional[Dict] = None,
    ) -> "TerminationResult":
        """SystemError"""
        return cls(
            should_terminate=True,
            reason=reason,
            termination_type=TerminationType.ERROR,
            message=message,
            details=details or {},
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize为Dict"""
        return {
            "should_terminate": self.should_terminate,
            "reason": self.reason.value if self.reason else None,
            "type": self.termination_type.value if self.termination_type else None,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class TerminationConfig:
    """
    TerminateCheckConfig
    
    定义各种TerminateCondition的Threshold
    """
    # IterateLimit
    max_iterations: int = 50
    
    # Timeout（Second）
    task_timeout_s: float = 1800.0  # 30 Minute
    iteration_timeout_s: float = 120.0  # singletimeIterate 2 Minute
    
    # Failedcontenttoleratedegree
    max_consecutive_failures: int = 3
    max_total_failures: int = 10
    
    # Token Limit
    max_context_tokens: int = 180000
    
    # NoneprogressDetection
    max_no_progress_iterations: int = 5


class TerminationChecker:
    """
    TerminateCheck器
    
    Judge Agent LoopYesNo应该Terminate
    
    CheckOrder（Priority级）：
    1. set_task_status 被调用（最High）
    2. UserCancel
    3. Window丢失
    4. 严重Error
    5. 连continuedFailed
    6. MaxIterate次数
    7. Timeout
    8. Token Limit
    
    UsageExample:
    ```python
    checker = TerminationChecker(config)
    
    result = checker.check(
        iteration=10,
        tool_results=results,
        set_task_status_called=False,
        window_exists=True,
        elapsed_time_s=60.0,
    )
    
    if result.should_terminate:
        print(f"Terminating: {result.reason.value}")
    ```
    """
    
    def __init__(self, config: Optional[TerminationConfig] = None):
        """
        InitializeTerminateCheck器
        
        Args:
            config: TerminateConfig
        """
        self.config = config or TerminationConfig()
        
        # Failedtrack
        self._consecutive_failures = 0
        self._total_failures = 0
        self._last_success_iteration = 0
        
        # progresstrack
        self._last_progress_iteration = 0
        self._last_state_hash: Optional[str] = None
        
        # Usercontrol
        self._user_cancelled = False
        self._user_paused = False
    
    def check(
        self, 
        iteration: int,
        tool_results: Optional[List["ToolResult"]] = None,
        set_task_status_called: bool = False,
        set_task_status_value: Optional[str] = None,
        window_exists: bool = True,
        elapsed_time_s: float = 0,
        current_tokens: int = 0,
        critical_error: Optional[str] = None,
    ) -> TerminationResult:
        """
        CheckYesNo应该Terminate
        
        Args:
            iteration: 当BeforeIterate次数
            tool_results: ToolExecuteResultList
            set_task_status_called: set_task_status ToolYesNo被调用
            set_task_status_value: set_task_status 的值 (completed/needs_help)
            window_exists: TargetWindowYesNo存在
            elapsed_time_s: 已耗时（Second）
            current_tokens: 当BeforeUpDown文 token 数
            critical_error: 严重ErrorInfo
            
        Returns:
            TerminateCheckResult
        """
        tool_results = tool_results or []
        
        # 1. set_task_status beCall（mostHighPrioritylevel）
        if set_task_status_called:
            if set_task_status_value == "completed":
                return TerminationResult.completed("Task completed by agent")
            elif set_task_status_value == "needs_help":
                return TerminationResult(
                    should_terminate=True,
                    reason=TerminationReason.NEEDS_HELP,
                    termination_type=TerminationType.FAIL,  # NeedHelpcalculateasFailed
                    message="Agent needs user help",
                )
        
        # 2. UserCancel
        if self._user_cancelled:
            return TerminationResult(
                should_terminate=True,
                reason=TerminationReason.USER_CANCELLED,
                termination_type=TerminationType.CANCELLED,
                message="Cancelled by user",
            )
        
        # 3. UserPause
        if self._user_paused:
            return TerminationResult(
                should_terminate=True,
                reason=TerminationReason.USER_PAUSED,
                termination_type=TerminationType.CANCELLED,
                message="Paused by user",
            )
        
        # 4. severeError
        if critical_error:
            return TerminationResult.error(
                reason=TerminationReason.CRITICAL_ERROR,
                message=f"Critical error: {critical_error}",
                details={"error": critical_error},
            )
        
        # 5. TargetWindowlost
        if not window_exists:
            return TerminationResult.error(
                reason=TerminationReason.WINDOW_LOST,
                message="Target window no longer exists",
            )
        
        # 6. UpdateFailedtrack
        self._update_failure_tracking(tool_results, iteration)
        
        # 7. continuousFailedCheck
        if self._consecutive_failures >= self.config.max_consecutive_failures:
            return TerminationResult.failed(
                reason=TerminationReason.CONSECUTIVE_FAILURES,
                message=f"{self._consecutive_failures} consecutive tool failures",
                details={
                    "consecutive_failures": self._consecutive_failures,
                    "max_allowed": self.config.max_consecutive_failures,
                },
            )
        
        # 8. totalFailedcountCheck
        if self._total_failures >= self.config.max_total_failures:
            return TerminationResult.failed(
                reason=TerminationReason.CONSECUTIVE_FAILURES,
                message=f"Total failures ({self._total_failures}) exceeded limit",
                details={
                    "total_failures": self._total_failures,
                    "max_allowed": self.config.max_total_failures,
                },
            )
        
        # 9. MaxIteratecount
        if iteration >= self.config.max_iterations:
            return TerminationResult.failed(
                reason=TerminationReason.MAX_ITERATIONS,
                message=f"Reached max iterations ({self.config.max_iterations})",
                details={
                    "iteration": iteration,
                    "max_iterations": self.config.max_iterations,
                },
            )
        
        # 10. TimeoutCheck
        if elapsed_time_s > self.config.task_timeout_s:
            return TerminationResult.failed(
                reason=TerminationReason.TIMEOUT,
                message=f"Task timed out after {elapsed_time_s:.1f}s",
                details={
                    "elapsed_s": elapsed_time_s,
                    "timeout_s": self.config.task_timeout_s,
                },
            )
        
        # 11. Token Limit
        if current_tokens > 0 and current_tokens > self.config.max_context_tokens:
            return TerminationResult.failed(
                reason=TerminationReason.TOKEN_LIMIT,
                message=f"Context exceeds token limit ({current_tokens}/{self.config.max_context_tokens})",
                details={
                    "current_tokens": current_tokens,
                    "max_tokens": self.config.max_context_tokens,
                },
            )
        
        # continueRunning
        return TerminationResult.continue_running()
    
    def _update_failure_tracking(
        self, 
        tool_results: List["ToolResult"],
        iteration: int,
    ):
        """
        UpdateFailed追踪
        
        Args:
            tool_results: ToolResultList
            iteration: 当BeforeIterate
        """
        has_failure = any(
            getattr(r, 'is_error', False) or getattr(r, 'error', None) 
            for r in tool_results
        )
        
        if has_failure:
            self._consecutive_failures += 1
            self._total_failures += 1
        else:
            # ResetcontinuousFailedCount
            self._consecutive_failures = 0
            self._last_success_iteration = iteration
    
    def cancel(self):
        """UserCancel"""
        self._user_cancelled = True
    
    def pause(self):
        """UserPause"""
        self._user_paused = True
    
    def resume(self):
        """ResumeRunning"""
        self._user_paused = False
    
    def reset(self):
        """ResetState（New任务）"""
        self._consecutive_failures = 0
        self._total_failures = 0
        self._last_success_iteration = 0
        self._last_progress_iteration = 0
        self._last_state_hash = None
        self._user_cancelled = False
        self._user_paused = False
    
    def get_stats(self) -> Dict[str, Any]:
        """GetStatisticsInfo"""
        return {
            "consecutive_failures": self._consecutive_failures,
            "total_failures": self._total_failures,
            "last_success_iteration": self._last_success_iteration,
            "user_cancelled": self._user_cancelled,
            "user_paused": self._user_paused,
        }


class LLMClientProtocol(Protocol):
    """LLM ClientProtocol（用于Class型提示）"""
    async def create_message(
        self, 
        model: str,
        max_tokens: int,
        messages: List[Dict[str, Any]],
    ) -> Any: ...


class SuccessVerifier:
    """
    SuccessVerify器
    
    Agent 说 "completed" 不一定True的Complete了。
    Usage LLM Verify任务YesNoTrue正Complete。
    
    VerifyPolicy：
    1. 比对任务Target和Final截Graph
    2. CheckTool调用历史YesNo合理
    3. Usage Haiku 模型降Low成本
    
    UsageExample:
    ```python
    verifier = SuccessVerifier()
    
    verified = await verifier.verify(
        task="在浏览器MediumSearch Python 教程",
        final_screenshot=screenshot_base64,
        tool_history=tools_called,
        llm_client=client,
    )
    
    if not verified:
        print("Task not actually completed!")
    ```
    """
    
    VERIFICATION_PROMPT = """You are a task verification assistant. 

Task was: {task}

Agent claims the task is completed.

Tool calls made:
{tool_summary}

Please verify by looking at the final screenshot:
1. Does the screenshot show the expected result?
2. Were all necessary actions performed?
3. Is there any indication that the task failed or is incomplete?

Respond with JSON only:
{{"verified": true/false, "confidence": 0.0-1.0, "reason": "brief explanation"}}
"""
    
    def __init__(
        self,
        verification_model: str = "claude-3-haiku-20240307",
        min_confidence: float = 0.7,
    ):
        """
        InitializeSuccessVerify器
        
        Args:
            verification_model: 用于Verify的模型（Default Haiku 降Low成本）
            min_confidence: 最Low置信度Threshold
        """
        self.verification_model = verification_model
        self.min_confidence = min_confidence
    
    async def verify(
        self, 
        task: str, 
        final_screenshot: Optional[str],
        tool_history: List[Dict[str, Any]],
        llm_client: Optional[Any] = None,
    ) -> bool:
        """
        Verify任务YesNoTrue正Complete
        
        Args:
            task: Original任务描述
            final_screenshot: Final截Graph（base64）
            tool_history: Tool调用历史
            llm_client: LLM Client（Optional，无则SkipVerify）
            
        Returns:
            YesNoTrue正Complete
        """
        # None LLM Client，Defaultthrough
        if llm_client is None:
            logger.warning("No LLM client provided, skipping verification")
            return True
        
        # NonecaptureGraph，NonemethodVerify
        if not final_screenshot:
            logger.warning("No screenshot provided, skipping verification")
            return True
        
        try:
            # BuildVerify prompt
            tool_summary = self._summarize_tools(tool_history)
            prompt = self.VERIFICATION_PROMPT.format(
                task=task,
                tool_summary=tool_summary,
            )
            
            # BuildMessage
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": final_screenshot,
                        }
                    }
                ]
            }]
            
            # Call LLM
            response = await llm_client.messages.create(
                model=self.verification_model,
                max_tokens=200,
                messages=messages,
            )
            
            # ParseResponse
            result = self._parse_response(response)
            
            if result is None:
                logger.warning("Failed to parse verification response")
                return True  # ParseFailedDefaultthrough
            
            verified = result.get("verified", True)
            confidence = result.get("confidence", 1.0)
            reason = result.get("reason", "")
            
            logger.info(
                f"Verification result: verified={verified}, "
                f"confidence={confidence:.2f}, reason={reason}"
            )
            
            # confidencenotenoughtimealsorecognizefornot yetVerify
            if confidence < self.min_confidence:
                logger.warning(
                    f"Confidence too low: {confidence:.2f} < {self.min_confidence}"
                )
                return False
            
            return verified
            
        except Exception as e:
            logger.error(f"Verification failed with error: {e}")
            return True  # VerifyexitwrongDefaultthrough
    
    def _summarize_tools(self, tool_history: List[Dict[str, Any]]) -> str:
        """
        汇总Tool调用历史
        
        Args:
            tool_history: Tool调用List
            
        Returns:
            汇总文本
        """
        if not tool_history:
            return "No tools were called"
        
        lines = []
        for i, tool in enumerate(tool_history[-10:], 1):  # mostDisplaymostnear 10 a
            name = tool.get("name", "unknown")
            args = tool.get("arguments", {})
            success = not tool.get("error")
            status = "✓" if success else "✗"
            
            # simpleizeArgumentDisplay
            args_str = ", ".join(
                f"{k}={str(v)[:30]}" 
                for k, v in list(args.items())[:3]
            )
            
            lines.append(f"{i}. {status} {name}({args_str})")
        
        if len(tool_history) > 10:
            lines.append(f"... and {len(tool_history) - 10} more tools")
        
        return "\n".join(lines)
    
    def _parse_response(self, response: Any) -> Optional[Dict[str, Any]]:
        """
        Parse LLM Response
        
        Args:
            response: LLM Response
            
        Returns:
            ParseAfter的Dict，或 None
        """
        try:
            # GetResponsetext
            if hasattr(response, 'content') and response.content:
                text = response.content[0].text
            else:
                return None
            
            # tryParse JSON
            # Handlemaybe's  markdown codeblock
            text = text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            
            return json.loads(text)
            
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            logger.debug(f"Failed to parse response: {e}")
            return None


@dataclass
class TaskStatusCall:
    """set_task_status 调用记录"""
    status: str  # "completed" or "needs_help"
    description: str
    timestamp: datetime = field(default_factory=datetime.now)


def detect_set_task_status(tool_calls: List[Dict[str, Any]]) -> Optional[TaskStatusCall]:
    """
    检测 tool_calls MediumYesNo有 set_task_status 调用
    
    Args:
        tool_calls: Tool调用List
        
    Returns:
        TaskStatusCall 或 None
    """
    for call in tool_calls:
        if call.get("name") == "set_task_status":
            args = call.get("arguments", {})
            return TaskStatusCall(
                status=args.get("status", ""),
                description=args.get("description", ""),
            )
    return None


# ========== Export ==========

__all__ = [
    "TerminationReason",
    "TerminationType",
    "TerminationResult",
    "TerminationConfig",
    "TerminationChecker",
    "SuccessVerifier",
    "TaskStatusCall",
    "detect_set_task_status",
]
