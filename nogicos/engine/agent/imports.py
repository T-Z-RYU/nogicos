# -*- coding: utf-8 -*-
"""
Agent Import Utilities

Centralized optional imports with availability flags.
Reduces boilerplate try/except blocks in main agent code.
"""

import os
from typing import Any, Dict, Optional, Callable, TypeVar

# =============================================================================
# Core Dependencies (Always Available)
# =============================================================================

# Anthropic Client
ANTHROPIC_AVAILABLE = False
anthropic = None
Anthropic = None
AsyncAnthropic = None

try:
    import anthropic as _anthropic
    from anthropic import Anthropic as _Anthropic, AsyncAnthropic as _AsyncAnthropic
    anthropic = _anthropic
    Anthropic = _Anthropic
    AsyncAnthropic = _AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Knowledge Store (B2)
# =============================================================================

KNOWLEDGE_AVAILABLE = False
KnowledgeStore = None
UserProfile = None
Trajectory = None
get_store: Optional[Callable] = None

try:
    from ..knowledge import (
        KnowledgeStore as _KnowledgeStore,
        UserProfile as _UserProfile,
        Trajectory as _Trajectory,
    )
    from ..knowledge.store import get_store as _get_store
    
    KnowledgeStore = _KnowledgeStore
    UserProfile = _UserProfile
    Trajectory = _Trajectory
    get_store = _get_store
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Long-term Memory System
# =============================================================================

MEMORY_AVAILABLE = False
get_memory_store: Optional[Callable] = None
SemanticMemorySearch = None
BackgroundMemoryProcessor = None
format_memories_for_prompt: Optional[Callable] = None

try:
    from ..knowledge import (
        get_memory_store as _get_memory_store,
        SemanticMemorySearch as _SemanticMemorySearch,
        BackgroundMemoryProcessor as _BackgroundMemoryProcessor,
        format_memories_for_prompt as _format_memories_for_prompt,
    )
    
    get_memory_store = _get_memory_store
    SemanticMemorySearch = _SemanticMemorySearch
    BackgroundMemoryProcessor = _BackgroundMemoryProcessor
    format_memories_for_prompt = _format_memories_for_prompt
    MEMORY_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Visualization Module
# =============================================================================

VISUALIZATION_AVAILABLE = False
visualize_tool_start: Optional[Callable] = None
visualize_tool_end: Optional[Callable] = None
visualize_task_start: Optional[Callable] = None
visualize_task_complete: Optional[Callable] = None
visualize_task_error: Optional[Callable] = None

try:
    from ..visualization import (
        visualize_tool_start as _visualize_tool_start,
        visualize_tool_end as _visualize_tool_end,
        visualize_task_start as _visualize_task_start,
        visualize_task_complete as _visualize_task_complete,
        visualize_task_error as _visualize_task_error,
    )
    
    visualize_tool_start = _visualize_tool_start
    visualize_tool_end = _visualize_tool_end
    visualize_task_start = _visualize_task_start
    visualize_task_complete = _visualize_task_complete
    visualize_task_error = _visualize_task_error
    VISUALIZATION_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Task Planner
# =============================================================================

PLANNER_AVAILABLE = False
TaskPlanner = None
Plan = None
PlanStep = None
PlanExecuteState = None

try:
    from .planner import (
        TaskPlanner as _TaskPlanner,
        Plan as _Plan,
        PlanStep as _PlanStep,
        PlanExecuteState as _PlanExecuteState,
    )
    
    TaskPlanner = _TaskPlanner
    Plan = _Plan
    PlanStep = _PlanStep
    PlanExecuteState = _PlanExecuteState
    PLANNER_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Task Classifier
# =============================================================================

CLASSIFIER_AVAILABLE = False
TaskClassifier = None
TaskType = None
ClassifierComplexity = None
ClassificationResult = None

try:
    from .classifier import (
        TaskClassifier as _TaskClassifier,
        TaskType as _TaskType,
        TaskComplexity as _ClassifierComplexity,
        ClassificationResult as _ClassificationResult,
    )
    
    TaskClassifier = _TaskClassifier
    TaskType = _TaskType
    ClassifierComplexity = _ClassifierComplexity
    ClassificationResult = _ClassificationResult
    CLASSIFIER_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Browser Session
# =============================================================================

BROWSER_SESSION_AVAILABLE = False
get_browser_session: Optional[Callable] = None
close_browser_session: Optional[Callable] = None

try:
    from ..browser import (
        get_browser_session as _get_browser_session,
        close_browser_session as _close_browser_session,
        PLAYWRIGHT_AVAILABLE,
    )
    
    get_browser_session = _get_browser_session
    close_browser_session = _close_browser_session
    BROWSER_SESSION_AVAILABLE = PLAYWRIGHT_AVAILABLE
except ImportError:
    pass


# =============================================================================
# Helper for Creating Anthropic Clients
# =============================================================================

def _get_api_key() -> Optional[str]:
    """Get API key from api_keys.py or environment"""
    # First try api_keys.py (local config takes priority)
    try:
        from api_keys import ANTHROPIC_API_KEY
        if ANTHROPIC_API_KEY:
            return ANTHROPIC_API_KEY
    except ImportError:
        pass
    except AttributeError:
        pass

    # Then try environment variable
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key

    return None


def create_anthropic_client(api_key: Optional[str] = None):
    """
    Create Anthropic sync client.
    
    Args:
        api_key: Optional API key. Uses ANTHROPIC_API_KEY env var or api_keys.py if not provided.
        
    Returns:
        Anthropic client or None if not available
    """
    if not ANTHROPIC_AVAILABLE or Anthropic is None:
        return None
    
    key = api_key or _get_api_key()
    if not key:
        return None
    
    return Anthropic(api_key=key)


def create_async_anthropic_client(api_key: Optional[str] = None):
    """
    Create Anthropic async client.
    
    Args:
        api_key: Optional API key. Uses ANTHROPIC_API_KEY env var or api_keys.py if not provided.
        
    Returns:
        AsyncAnthropic client or None if not available
    """
    if not ANTHROPIC_AVAILABLE or AsyncAnthropic is None:
        return None
    
    key = api_key or _get_api_key()
    if not key:
        return None
    
    return AsyncAnthropic(api_key=key)


# =============================================================================
# Verification Module
# =============================================================================

VERIFICATION_AVAILABLE = False
AnswerVerifier = None
verify_answer: Optional[Callable] = None

try:
    from .verification import (
        AnswerVerifier as _AnswerVerifier,
        verify_answer as _verify_answer,
    )

    AnswerVerifier = _AnswerVerifier
    verify_answer = _verify_answer
    VERIFICATION_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Context Injection Module (Cursor-style)
# =============================================================================

CONTEXT_INJECTION_AVAILABLE = False
ContextInjector = None
ContextConfig = None
get_context_injector: Optional[Callable] = None

try:
    from ..context import (
        ContextInjector as _ContextInjector,
        ContextConfig as _ContextConfig,
        get_context_injector as _get_context_injector,
    )

    ContextInjector = _ContextInjector
    ContextConfig = _ContextConfig
    get_context_injector = _get_context_injector
    CONTEXT_INJECTION_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# Summary of Available Features
# =============================================================================

def get_available_features() -> Dict[str, bool]:
    """Return dict of feature availability for debugging"""
    return {
        "anthropic": ANTHROPIC_AVAILABLE,
        "knowledge": KNOWLEDGE_AVAILABLE,
        "memory": MEMORY_AVAILABLE,
        "visualization": VISUALIZATION_AVAILABLE,
        "planner": PLANNER_AVAILABLE,
        "classifier": CLASSIFIER_AVAILABLE,
        "browser_session": BROWSER_SESSION_AVAILABLE,
        "verification": VERIFICATION_AVAILABLE,
        "context_injection": CONTEXT_INJECTION_AVAILABLE,
    }

