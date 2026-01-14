"""
NogicOS Tool调用Verify器
======================

Verify LLM Return的Tool调用，防止Invalid调用。

功能:
- VerifyToolYesNo存在
- VerifyArgumentClass型和Range
- VerifyCoordinateYesNo在WindowInner
- SecurityCheck（敏感操作）

参考:
- Anthropic ToolError Handle
- UFO ArgumentVerify
"""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Set
import re

from .types import ToolCall, ToolResult, ToolDefinition

# DelayedImportavoidLoopDependency
try:
    from ..config import SecurityConfig, get_config
except ImportError:
    SecurityConfig = None  # type: ignore
    get_config = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """VerifyError"""
    field: str
    message: str
    value: Any = None
    
    def __str__(self) -> str:
        if self.value is not None:
            return f"{self.field}: {self.message} (got: {self.value})"
        return f"{self.field}: {self.message}"


@dataclass
class ValidationResult:
    """VerifyResult"""
    valid: bool
    errors: List[ValidationError]
    warnings: List[str]
    is_sensitive: bool = False  # YesNoforsensitiveAction
    requires_confirmation: bool = False  # YesNoNeedUserConfirm
    filled_arguments: Optional[Dict[str, Any]] = None  # CompletionDefaultValueAfter's Argument
    
    @classmethod
    def success(cls, filled_arguments: Optional[Dict[str, Any]] = None) -> "ValidationResult":
        """CreateSuccessResult"""
        return cls(valid=True, errors=[], warnings=[], is_sensitive=False, 
                   requires_confirmation=False, filled_arguments=filled_arguments)
    
    @classmethod
    def failure(cls, errors: List[ValidationError]) -> "ValidationResult":
        """CreateFailedResult"""
        return cls(valid=False, errors=errors, warnings=[], is_sensitive=False)
    
    @classmethod
    def needs_confirmation(cls, tool_name: str, filled_arguments: Optional[Dict[str, Any]] = None) -> "ValidationResult":
        """Create需要UserConfirm的Result"""
        return cls(
            valid=True,  # VerifythroughbutneedConfirm
            errors=[],
            warnings=[f"Tool '{tool_name}' requires user confirmation"],
            is_sensitive=True,
            requires_confirmation=True,
            filled_arguments=filled_arguments,
        )
    
    def to_tool_result(self) -> ToolResult:
        """Convert为 ToolResult（用于ReturnError给 LLM）"""
        if self.requires_confirmation:
            return ToolResult.failure("Operation requires user confirmation before execution")
        if self.valid:
            return ToolResult.success("Validation passed")
        
        error_msg = "; ".join(str(e) for e in self.errors)
        return ToolResult.failure(f"Validation failed: {error_msg}")
    
    def to_confirmation_payload(self, tool_call: Any) -> Dict[str, Any]:
        """
        生成ConfirmEvent的 payload
        
        用于发布 USER_CONFIRM_REQUIRED Event
        """
        return {
            "tool_name": tool_call.name,
            "tool_id": tool_call.id,
            "arguments": self.filled_arguments or tool_call.arguments,
            "hwnd": tool_call.hwnd,
            "warnings": self.warnings,
            "reason": "sensitive_operation",
        }
    
    def get_filled_tool_call(self, tool_call: Any) -> Any:
        """
        Get补全Default值After的 ToolCall
        
        确保Down游Usage补全After的ArgumentExecuteTool。
        
        Usage:
            result = validator.validate(tool_call, bounds)
            if result.valid:
                filled_call = result.get_filled_tool_call(tool_call)
                # Usage filled_call ExecuteTool
        """
        if self.filled_arguments is None:
            return tool_call
        
        # DelayedImportavoidLoopDependency
        from .types import ToolCall as TC
        return TC(
            id=tool_call.id,
            name=tool_call.name,
            arguments=self.filled_arguments,
            hwnd=tool_call.hwnd,
        )


class ToolCallValidator:
    """
    Tool调用Verify器
    
    UsageExample:
    ```python
    validator = ToolCallValidator(tool_registry)
    
    # VerifysingleToolCall
    result = validator.validate(tool_call, window_bounds)
    if not result.valid:
        return result.to_tool_result()
    
    # ExecuteTool...
    ```
    """
    
    # CoordinaterelatedOffArgument
    COORDINATE_PARAMS = {"x", "y", "start_x", "start_y", "end_x", "end_y"}
    
    # Mustforcorrectnumber's Argument
    POSITIVE_PARAMS = {"width", "height", "delay", "timeout"}
    
    def __init__(
        self, 
        registered_tools: Dict[str, ToolDefinition],
        security_config: Optional[Any] = None,
    ):
        """
        InitializeVerify器
        
        Args:
            registered_tools: 已Register的Tool定义
            security_config: SecurityConfig（Auto从GlobalGet）
        """
        self.registered_tools = registered_tools
        
        # from SecurityConfig GetConfig
        if security_config is None and get_config is not None:
            try:
                config = get_config()
                security_config = config.security
            except Exception:
                security_config = None
        
        if security_config is not None:
            self.sensitive_tools = set(security_config.sensitive_tools)
            self.max_string_length = security_config.max_tool_param_length
            self.require_confirm_for_sensitive = security_config.require_confirm_for_sensitive
        else:
            # FallbackDefaultValue
            self.sensitive_tools = {
                "delete_file", "send_message", "window_type", 
                "execute_command", "modify_system_settings"
            }
            self.max_string_length = 10000
            self.require_confirm_for_sensitive = True  # DefaultforceConfirm
        
        # from ToolDefinition.is_sensitive supplementsensitiveToolList
        for name, tool_def in registered_tools.items():
            if tool_def.is_sensitive:
                self.sensitive_tools.add(name)
    
    def validate(
        self, 
        tool_call: ToolCall,
        window_bounds: Optional[Dict[str, int]] = None,
    ) -> ValidationResult:
        """
        VerifyTool调用
        
        Args:
            tool_call: Tool调用
            window_bounds: WindowBoundary {"x": 0, "y": 0, "width": 1920, "height": 1080}
            
        Returns:
            VerifyResult
        """
        errors: List[ValidationError] = []
        warnings: List[str] = []
        
        # 1. VerifyToolYesNostorein
        if tool_call.name not in self.registered_tools:
            errors.append(ValidationError(
                field="name",
                message=f"Tool '{tool_call.name}' does not exist",
                value=tool_call.name
            ))
            return ValidationResult.failure(errors)
        
        tool_def = self.registered_tools[tool_call.name]
        
        # 2. Verify hwnd with supports_hwnd onecauseproperty
        hwnd_errors = self._validate_hwnd_consistency(tool_call, tool_def)
        errors.extend(hwnd_errors)
        
        # 3. CompletionDefaultValue
        param_map = {p.name: p for p in tool_def.parameters}
        filled_arguments = self._fill_defaults(tool_call.arguments, param_map)
        
        # 4. VerifyRequiredArgument（inCompletionDefaultValueAfterCheck）
        required_params = {p.name for p in tool_def.parameters if p.required}
        provided_params = set(filled_arguments.keys())
        missing_params = required_params - provided_params
        
        if missing_params:
            errors.append(ValidationError(
                field="arguments",
                message=f"Missing required parameters: {missing_params}",
                value=list(provided_params)
            ))
        
        # 5. VerifyArgumentClasstypeandconstraint
        for param_name, value in filled_arguments.items():
            if param_name in param_map:
                param_def = param_map[param_name]
                # Classtypevalidate
                type_error = self._validate_type(param_name, value, param_def.type)
                if type_error:
                    errors.append(type_error)
                # Enumconstraint
                enum_error = self._validate_enum(param_name, value, param_def)
                if enum_error:
                    errors.append(enum_error)
        
        # 6. VerifyCoordinateRange（onlywhenToolSupportWindowIsolationtime）
        has_coordinate_params = any(
            p in filled_arguments for p in self.COORDINATE_PARAMS
        )
        if tool_def.supports_hwnd and has_coordinate_params:
            if window_bounds:
                coord_errors = self._validate_coordinates(filled_arguments, window_bounds)
                errors.extend(coord_errors)
            else:
                # window_bounds missingbuthaveCoordinateArgument -> DowngradeforWarning
                warnings.append(
                    f"Window bounds not provided, coordinate validation skipped. "
                    f"Please obtain window bounds before executing coordinate-based operations."
                )
        
        # 7. VerifyCharacterstringLength
        for param_name, value in filled_arguments.items():
            if isinstance(value, str) and len(value) > self.max_string_length:
                errors.append(ValidationError(
                    field=param_name,
                    message=f"String too long (max {self.max_string_length})",
                    value=f"length={len(value)}"
                ))
        
        # 8. sensitiveActionHandle
        is_sensitive = tool_call.name in self.sensitive_tools or tool_def.is_sensitive
        
        if errors:
            return ValidationResult.failure(errors)
        
        # sensitiveAction + ConfigforceConfirm -> ReturnNeedConfirm's Result
        if is_sensitive and self.require_confirm_for_sensitive:
            result = ValidationResult.needs_confirmation(tool_call.name, filled_arguments)
            result.warnings = warnings
            return result
        
        # normalthrough
        result = ValidationResult.success(filled_arguments=filled_arguments)
        result.warnings = warnings
        result.is_sensitive = is_sensitive  # passsensitiveMark（even ifnotforceConfirm）
        return result
    
    def _fill_defaults(
        self,
        arguments: Dict[str, Any],
        param_map: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        补全OptionalArgument的Default值
        
        Args:
            arguments: OriginalArgument
            param_map: Argument定义映射
            
        Returns:
            补全After的ArgumentDict
        """
        filled = dict(arguments)  # CopyoriginalArgument
        
        for param_name, param_def in param_map.items():
            # Argumentnot yetmentionprovideandhaveDefaultValue
            if param_name not in filled and param_def.default is not None:
                filled[param_name] = param_def.default
        
        return filled
    
    def _validate_hwnd_consistency(
        self, 
        tool_call: ToolCall, 
        tool_def: ToolDefinition,
    ) -> List[ValidationError]:
        """Verify hwnd 与 supports_hwnd 一致性"""
        errors = []
        
        if tool_def.supports_hwnd:
            # ToolSupportWindowIsolation，shouldmentionprovide hwnd
            if tool_call.hwnd is None:
                errors.append(ValidationError(
                    field="hwnd",
                    message=f"Tool '{tool_call.name}' requires hwnd (supports_hwnd=True)",
                    value=None
                ))
        else:
            # ToolNot SupportWindowIsolation，notshouldmentionprovide hwnd
            if tool_call.hwnd is not None:
                errors.append(ValidationError(
                    field="hwnd",
                    message=f"Tool '{tool_call.name}' does not support hwnd (supports_hwnd=False)",
                    value=tool_call.hwnd
                ))
        
        return errors
    
    def _validate_enum(
        self, 
        param_name: str, 
        value: Any, 
        param_def: Any,
    ) -> Optional[ValidationError]:
        """Verify枚举约束"""
        if param_def.enum is None:
            return None
        
        if value not in param_def.enum:
            return ValidationError(
                field=param_name,
                message=f"Value must be one of {param_def.enum}",
                value=value
            )
        return None
    
    def _validate_type(
        self, 
        param_name: str, 
        value: Any, 
        expected_type: str,
    ) -> Optional[ValidationError]:
        """VerifyArgumentClass型"""
        type_checks = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, list),
            "object": lambda v: isinstance(v, dict),
        }
        
        checker = type_checks.get(expected_type)
        if checker and not checker(value):
            return ValidationError(
                field=param_name,
                message=f"Expected type '{expected_type}'",
                value=f"{type(value).__name__}: {value}"
            )
        
        # quotaOuterCheck：correctnumberArgument
        if param_name in self.POSITIVE_PARAMS:
            if isinstance(value, (int, float)) and value <= 0:
                return ValidationError(
                    field=param_name,
                    message="Must be positive",
                    value=value
                )
        
        return None
    
    def _validate_coordinates(
        self, 
        arguments: Dict[str, Any],
        bounds: Dict[str, int],
    ) -> List[ValidationError]:
        """
        VerifyCoordinateRange
        
        Coordinate必须在WindowBoundaryInner。
        
        注意：Windows 多Display器场景Down，Left/Up屏幕Coordinate可能为负数，
        因此不对Coordinate本身做非负约束，只CheckYesNo在 bounds IntervalInner。
        """
        errors = []
        
        # MustmentionprovideComplete's WindowBoundary
        required_keys = {"x", "y", "width", "height"}
        if not required_keys.issubset(bounds.keys()):
            missing = required_keys - set(bounds.keys())
            errors.append(ValidationError(
                field="window_bounds",
                message=f"Incomplete window bounds, missing: {missing}",
                value=bounds
            ))
            return errors
        
        # WindowBoundary（SupportnegativeCoordinate，multipleDisplayerscene）
        min_x = bounds["x"]
        min_y = bounds["y"]
        max_x = min_x + bounds["width"]
        max_y = min_y + bounds["height"]
        
        # VerifySizereasonableproperty（SizeMustforcorrect）
        if bounds["width"] <= 0 or bounds["height"] <= 0:
            errors.append(ValidationError(
                field="window_bounds",
                message="Window dimensions must be positive",
                value=bounds
            ))
            return errors
        
        for param_name in self.COORDINATE_PARAMS:
            if param_name not in arguments:
                continue
            
            value = arguments[param_name]
            if not isinstance(value, (int, float)):
                continue
            
            # Check X Coordinate（AllownegativeValue，multipleDisplayerSupport）
            if "x" in param_name.lower():
                if value < min_x or value > max_x:
                    errors.append(ValidationError(
                        field=param_name,
                        message=f"X coordinate out of window bounds [{min_x}, {max_x}]",
                        value=value
                    ))
            
            # Check Y Coordinate（AllownegativeValue，multipleDisplayerSupport）
            if "y" in param_name.lower():
                if value < min_y or value > max_y:
                    errors.append(ValidationError(
                        field=param_name,
                        message=f"Y coordinate out of window bounds [{min_y}, {max_y}]",
                        value=value
                    ))
        
        return errors
    
    def is_sensitive(self, tool_name: str) -> bool:
        """CheckYesNo为敏感Tool"""
        return tool_name in self.sensitive_tools
    
    def get_available_tools(self) -> List[str]:
        """Get所有AvailableTool名"""
        return list(self.registered_tools.keys())
    
    async def handle_confirmation(
        self,
        tool_call: ToolCall,
        result: ValidationResult,
        task_id: str,
        event_bus: Any,
        state_manager: Any = None,
    ) -> None:
        """
        Handle需要Confirm的Tool调用
        
        1. Switch任务State到 NEEDS_HELP
        2. 发布 USER_CONFIRM_REQUIRED Event
        3. WaitUp层HandleConfirm逻辑
        
        Args:
            tool_call: Tool调用
            result: VerifyResult（应为 requires_confirmation=True）
            task_id: 任务 ID
            event_bus: Event总线
            state_manager: State管理器（Optional，用于SwitchState）
            
        Usage:
            result = validator.validate(tool_call, bounds)
            if result.requires_confirmation:
                await validator.handle_confirmation(tool_call, result, task_id, event_bus)
                # thistimeshouldPauseToolExecute，WaitUserConfirm
        """
        if not result.requires_confirmation:
            return
        
        # DelayedImportavoidLoopDependency
        from .events import AgentEvent, EventType
        
        # 1. SwitchState（Ifmentionprovide state_manager）
        if state_manager is not None:
            try:
                from .types import TaskStatus
                await state_manager.transition(task_id, TaskStatus.NEEDS_HELP, 
                                               reason=f"Sensitive tool: {tool_call.name}")
            except Exception as e:
                logger.warning(f"Failed to transition to NEEDS_HELP: {e}")
        
        # 2. PublishConfirmEvent
        await event_bus.publish(AgentEvent.create(
            event_type=EventType.USER_CONFIRM_REQUIRED,
            task_id=task_id,
            payload=result.to_confirmation_payload(tool_call)
        ))
        
        logger.info(f"Confirmation required for tool '{tool_call.name}' in task {task_id}")


# ========== SecurityVerifyer ==========

class SecurityValidator:
    """
    SecurityVerify器
    
    检测潜在的Security问题
    """
    
    # Prompt injectPattern
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous\s+)?instructions",
        r"disregard\s+(all\s+)?(previous\s+)?instructions",
        r"forget\s+(all\s+)?(previous\s+)?instructions",
        r"new\s+instructions?:",
        r"system\s*:\s*",
        r"<\s*/?system\s*>",
        r"\[\s*INST\s*\]",
    ]
    
    # sensitiveDataPattern
    SENSITIVE_PATTERNS = [
        r"\b\d{16}\b",                    # trustusecard number
        r"\b\d{3}-\d{2}-\d{4}\b",         # SSN
        r"password\s*[:=]\s*\S+",         # Password
        r"api[_-]?key\s*[:=]\s*\S+",      # API Key
        r"secret\s*[:=]\s*\S+",           # Secret
        r"token\s*[:=]\s*[a-zA-Z0-9_-]+", # Token
    ]
    
    def __init__(self):
        self._injection_regex = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self._sensitive_regex = [re.compile(p, re.IGNORECASE) for p in self.SENSITIVE_PATTERNS]
    
    def check_prompt_injection(self, text: str) -> List[str]:
        """
        检测 Prompt 注入
        
        Returns:
            检测到的注入模式List
        """
        detected = []
        for pattern, regex in zip(self.INJECTION_PATTERNS, self._injection_regex):
            if regex.search(text):
                detected.append(pattern)
        return detected
    
    def check_sensitive_data(self, text: str) -> List[str]:
        """
        检测敏感数据
        
        Returns:
            检测到的敏感数据Class型List
        """
        detected = []
        type_names = ["credit_card", "ssn", "password", "api_key", "secret", "token"]
        for type_name, regex in zip(type_names, self._sensitive_regex):
            if regex.search(text):
                detected.append(type_name)
        return detected
    
    def sanitize(self, text: str) -> str:
        """
        Cleanup敏感数据
        
        用 [REDACTED] Replace检测到的敏感数据
        """
        result = text
        for regex in self._sensitive_regex:
            result = regex.sub("[REDACTED]", result)
        return result
