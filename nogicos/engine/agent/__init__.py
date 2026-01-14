# -*- coding: utf-8 -*-
"""
NogicOS Agent - Pure ReAct Agent with Plan-Execute capabilities

Components:
- ReActAgent: Core Think-Act-Observe loop
- TaskPlanner: Complex task decomposition and replanning
- TaskClassifier: Intelligent task routing (browser/local/mixed)
- AgentMode: Cursor-style interaction modes (Agent/Ask/Plan)
- Event System: Unified communication via EventBus (Phase 0)
"""

from .react_agent import ReActAgent, AgentResult
from .planner import TaskPlanner, Plan, PlanExecuteState, is_simple_task
from .classifier import TaskClassifier, TaskType, TaskComplexity, ClassificationResult
from .modes import AgentMode, ModeRouter, get_mode_router, ModeConfig
from .imports import get_available_features

# Phase 0: communicationcontractaboutlayer
from .events import (
    EventType, EventPriority, AgentEvent,
    task_started_event, task_completed_event, task_failed_event,
    tool_start_event, tool_end_event, tool_error_event,
    confirm_required_event, llm_chunk_event,
)
from .event_bus import (
    EventBus, get_event_bus, set_event_bus, on_event, on_all_events,
    BackpressureEventBus, get_backpressure_bus, init_backpressure_bus,
    EventBusOverflowError,
)
from .ws_adapter import (
    WebSocketEventAdapter, get_ws_adapter, set_ws_adapter,
    SecurityError, ValidationError,
)

# Phase 0.25: Performancebasesetapply
from .async_db import AsyncTaskStore, get_task_store, set_task_store
from .screenshot_manager import ScreenshotManager, get_screenshot_manager, set_screenshot_manager
from .incremental_checkpoint import IncrementalCheckpointer, create_checkpointer

# Phase 0.5: StateTruerelatedSource
from .state_manager import (
    TaskStateManager, get_state_manager, set_state_manager,
    TaskState, InvalidTransitionError, TaskNotFoundError,
)

# Phase 1: CoreDatastructure（TaskStatus/AgentStatus systemoneinthisdefine）
from .types import (
    TaskStatus, AgentStatus,  # StateEnum（systemonedefinePosition）
    ToolResult, ToolCall, ToolDefinition, ToolParameter,
    Message, MessageRole, MessageHistory,
    WindowContext, AgentContext,
    LLMResponse, StopReason,
    HWND,
)
from .validators import (
    ToolCallValidator, SecurityValidator,
    ValidationResult, ValidationError,
)

# Phase 2: doublelayer Agent Architecture
from .errors import (
    AgentError, ErrorSeverity, ErrorCategory,
    LLMError, ClaudeAPIError, RateLimitError, TokenLimitError, LLMResponseError,
    ToolError, ToolExecutionError, ToolNotFoundError, ToolValidationError, ToolTimeoutError,
    WindowError, WindowLostError, WindowNotFocusableError, WindowLockedError,
    StateError, InvalidStateTransitionError, CheckpointError,
    ConcurrencyError, TooManyTasksError, ResourceLockError,
    CriticalError, FatalError,
    RecoveryStrategy, get_recovery_strategy,
)
# alreadyDelete: blackboard, host_agent, app_agent, factory
# theseModulealreadybe UnifiedAgentManager + ReActAgent replace

# Phase 3: Agent Loop + ErrorResume + Concurrentcontrol + TerminationChecker
from .concurrency import (
    ConcurrencyManager, ConcurrencyConfig,
    TaskSlotInfo, WindowLockInfo,
    get_concurrency_manager, set_concurrency_manager,
)
from .termination import (
    TerminationChecker, TerminationConfig, TerminationResult,
    TerminationReason, TerminationType,
    SuccessVerifier, TaskStatusCall,
    detect_set_task_status,
)

# Phase 5: LLM Integration
from .llm_client import (
    LLMClient, LLMConfig, CacheStats,
    get_llm_client, generate,
)
from .prompts import (
    AgentMode as PromptAgentMode,
    PromptBuilder, build_system_prompt, get_prompt_builder,
    SYSTEM_PROMPT_TEMPLATE, THINKING_TEMPLATES,
)
from .tool_descriptions import (
    ToolDescription, ToolRegistry,
    get_tool_registry, get_tool_schemas,
    TOOL_DESCRIPTIONS,
)
from .context_manager import (
    ContextManager, TokenBudget, TokenCounter,
    ContextCompressor, CompressionResult,
    get_context_manager,
)

# Phase 5c: visualEnhancement
from .vision import (
    VisionEnhancer, EnhancedScreenshot, UIElement,
    get_vision_enhancer,
    OCRExtractor, OCRResult, TextRegion,
    get_ocr_extractor,
)

__all__ = [
    # Core Agent
    'ReActAgent',
    'AgentResult',
    # Planning
    'TaskPlanner',
    'Plan',
    'PlanExecuteState',
    'is_simple_task',
    # Classification
    'TaskClassifier',
    'TaskType',
    'TaskComplexity',
    'ClassificationResult',
    # Modes
    'AgentMode',
    'ModeRouter',
    'ModeConfig',
    'get_mode_router',
    # Utils
    'get_available_features',
    # Event System (Phase 0)
    'EventType',
    'EventPriority',
    'AgentEvent',
    'EventBus',
    'get_event_bus',
    'set_event_bus',
    'on_event',
    'on_all_events',
    'BackpressureEventBus',
    'get_backpressure_bus',
    'init_backpressure_bus',
    'EventBusOverflowError',
    'WebSocketEventAdapter',
    'get_ws_adapter',
    'set_ws_adapter',
    'SecurityError',
    'ValidationError',
    # Event Factory Functions
    'task_started_event',
    'task_completed_event',
    'task_failed_event',
    'tool_start_event',
    'tool_end_event',
    'tool_error_event',
    'confirm_required_event',
    'llm_chunk_event',
    # Performance Infrastructure (Phase 0.25)
    'AsyncTaskStore',
    'get_task_store',
    'set_task_store',
    'ScreenshotManager',
    'get_screenshot_manager',
    'set_screenshot_manager',
    'IncrementalCheckpointer',
    'create_checkpointer',
    # State Management (Phase 0.5)
    'TaskStateManager',
    'get_state_manager',
    'set_state_manager',
    'TaskStatus',
    'AgentStatus',
    'TaskState',
    'InvalidTransitionError',
    'TaskNotFoundError',
    # Core Types (Phase 1)
    'ToolResult',
    'ToolCall',
    'ToolDefinition',
    'ToolParameter',
    'Message',
    'MessageRole',
    'MessageHistory',
    'WindowContext',
    'AgentContext',
    'LLMResponse',
    'StopReason',
    'HWND',
    'ToolCallValidator',
    'SecurityValidator',
    'ValidationResult',
    # Error System (Phase 2)
    'AgentError',
    'ErrorSeverity',
    'ErrorCategory',
    'LLMError',
    'ClaudeAPIError',
    'RateLimitError',
    'TokenLimitError',
    'LLMResponseError',
    'ToolError',
    'ToolExecutionError',
    'ToolNotFoundError',
    'ToolValidationError',
    'ToolTimeoutError',
    'WindowError',
    'WindowLostError',
    'WindowNotFocusableError',
    'WindowLockedError',
    'StateError',
    'ConcurrencyError',
    'TooManyTasksError',
    'ResourceLockError',
    'CriticalError',
    'FatalError',
    'RecoveryStrategy',
    'get_recovery_strategy',
    # alreadyDelete: Blackboard, HostAgent, AppAgent, Factory (be UnifiedAgentManager replace)
    # Concurrency (Phase 3)
    'ConcurrencyManager',
    'ConcurrencyConfig',
    'TaskSlotInfo',
    'WindowLockInfo',
    'get_concurrency_manager',
    'set_concurrency_manager',
    # Termination (Phase 3)
    'TerminationChecker',
    'TerminationConfig',
    'TerminationResult',
    'TerminationReason',
    'TerminationType',
    'SuccessVerifier',
    'TaskStatusCall',
    'detect_set_task_status',
    # LLM Client (Phase 5)
    'LLMClient',
    'LLMConfig',
    'CacheStats',
    'get_llm_client',
    'generate',
    # Prompts (Phase 5a)
    'PromptAgentMode',
    'PromptBuilder',
    'build_system_prompt',
    'get_prompt_builder',
    'SYSTEM_PROMPT_TEMPLATE',
    'THINKING_TEMPLATES',
    # Tool Descriptions (Phase 5a)
    'ToolDescription',
    'ToolRegistry',
    'get_tool_registry',
    'get_tool_schemas',
    'TOOL_DESCRIPTIONS',
    # Context Manager (Phase 5b)
    'ContextManager',
    'TokenBudget',
    'TokenCounter',
    'ContextCompressor',
    'CompressionResult',
    'get_context_manager',
    # Vision (Phase 5c)
    'VisionEnhancer',
    'EnhancedScreenshot',
    'UIElement',
    'get_vision_enhancer',
    'OCRExtractor',
    'OCRResult',
    'TextRegion',
    'get_ocr_extractor',
]
