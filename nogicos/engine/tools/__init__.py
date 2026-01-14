# -*- coding: utf-8 -*-
"""
NogicOS Tools - V2 Unified Tool System

This module provides:
- ToolRegistry: Central registry for all tools
- Browser Tools: Web automation capabilities (via Electron IPC)
- Local Tools: File system and shell operations
- Window Tools: PostMessage-based window automation (Phase 4)
- System Tools: Task control and system utilities (Phase 4)
"""

from .base import (
    ToolRegistry,
    ToolCategory,
    ToolDefinition,
    ToolResult,
    get_registry,
    reset_registry,
)
from .browser import register_browser_tools
from .local import register_local_tools
from .cursor_tools import register_cursor_tools

# Desktop tools (Phase C) - optional, requires pyautogui
try:
    from .desktop import register_desktop_tools
    DESKTOP_TOOLS_AVAILABLE = True
except ImportError:
    DESKTOP_TOOLS_AVAILABLE = False
    register_desktop_tools = None

# Messaging tools (WhatsApp, etc.) - optional, requires pyautogui + pyperclip
try:
    from .messaging import register_messaging_tools
    MESSAGING_TOOLS_AVAILABLE = True
except ImportError:
    MESSAGING_TOOLS_AVAILABLE = False
    register_messaging_tools = None

# Vision tools (Phase C4) - optional, requires anthropic
try:
    from .vision import register_vision_tools
    VISION_TOOLS_AVAILABLE = True
except ImportError:
    VISION_TOOLS_AVAILABLE = False
    register_vision_tools = None

# Window tools (Phase 4) - Windows only, PostMessage-based
try:
    from .window_tools import register_window_tools, WindowTools, WindowLostError
    WINDOW_TOOLS_AVAILABLE = True
except ImportError:
    WINDOW_TOOLS_AVAILABLE = False
    register_window_tools = None
    WindowTools = None
    WindowLostError = None

# System tools (Phase 4) - Task control and system utilities
try:
    from .system_tools import register_system_tools, SystemTools, TaskStatus
    SYSTEM_TOOLS_AVAILABLE = True
except ImportError:
    SYSTEM_TOOLS_AVAILABLE = False
    register_system_tools = None
    SystemTools = None
    TaskStatus = None

# UFO tools (Microsoft UFO) - AI-powered desktop automation
try:
    from .ufo_executor import register_ufo_tools, UFOExecutor, execute_desktop_task
    UFO_TOOLS_AVAILABLE = True
except ImportError:
    UFO_TOOLS_AVAILABLE = False
    register_ufo_tools = None
    UFOExecutor = None
    execute_desktop_task = None

# Browser Executor (Browser Use) - AI vision-powered browser automation
try:
    from .browser_executor import (
        register_browser_executor_tools, 
        NogicBrowserExecutor, 
        get_browser_executor
    )
    BROWSER_EXECUTOR_AVAILABLE = True
except ImportError:
    BROWSER_EXECUTOR_AVAILABLE = False
    register_browser_executor_tools = None
    NogicBrowserExecutor = None
    get_browser_executor = None

# Playwright Executor - Playwright-based browser automation (like Cursor MCP)
try:
    from .playwright_executor import (
        register_playwright_tools,
        NogicPlaywrightExecutor,
        get_playwright_executor
    )
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    register_playwright_tools = None
    NogicPlaywrightExecutor = None
    get_playwright_executor = None

# Form Workflow - Complete form filling workflow (like Cursor + Playwright MCP)
try:
    from .form_workflow import (
        register_form_workflow_tools,
        FormWorkflow,
        FormWorkflowContext,
    )
    FORM_WORKFLOW_AVAILABLE = True
except ImportError:
    FORM_WORKFLOW_AVAILABLE = False
    register_form_workflow_tools = None
    FormWorkflow = None
    FormWorkflowContext = None

# YC Workflow - Preset workflow for filling YC application
try:
    from .yc_workflow import (
        register_yc_workflow_tools,
        execute_yc_workflow,
        is_yc_workflow_trigger,
        YCWorkflowContext,
    )
    YC_WORKFLOW_AVAILABLE = True
except (ImportError, SyntaxError) as e:
    import logging
    logging.getLogger(__name__).warning(f"YC Workflow not available: {e}")
    YC_WORKFLOW_AVAILABLE = False
    register_yc_workflow_tools = None
    execute_yc_workflow = None
    is_yc_workflow_trigger = None
    YCWorkflowContext = None

# Windows compatibility modules (Phase 4.5)
try:
    from .windows_compat import WindowInputController, InputResult, InputMethod
    from .hwnd_manager import HwndManager, get_hwnd_manager
    from .coordinate_system import CoordinateTransformer, scale_coordinates
    from .dpi_handler import DPIHandler, get_dpi_handler
    from .uipi_checker import UIPIChecker, can_control_window
    from .window_state import WindowStateChecker, is_window_operable
    from .multi_monitor import MultiMonitorManager, get_monitor_manager
    from .win11_compat import Windows11Compatibility, is_windows_11
    WINDOWS_COMPAT_AVAILABLE = True
except ImportError:
    WINDOWS_COMPAT_AVAILABLE = False


def create_full_registry() -> ToolRegistry:
    """
    Create a fully populated tool registry with all tools.
    
    Returns:
        ToolRegistry with browser, local, desktop, window, system, and vision tools registered.
    
    Tool simplification strategy (2026-01-09):
    - Remove low-level desktop tools (desktop_tools, window_tools), let UFO handle all desktop automation
    - UFO is AI-driven desktop automation that automatically understands UI and executes complete tasks (e.g. sending messages)
    - This reduces tool count, preventing Agent from choosing low-level tools that lead to incomplete tasks
    """
    registry = ToolRegistry()
    
    # Core tools (always available)
    register_browser_tools(registry)    # CDP Browser
    register_local_tools(registry)      # File system
    register_cursor_tools(registry)     # Cursor IDE
    
    # Desktop tools (Phase C) - pyautogui based (re-enabled for form filling)
    # For form filling and other scenarios requiring precise input
    if DESKTOP_TOOLS_AVAILABLE and register_desktop_tools:
        register_desktop_tools(registry)
    
    # Messaging tools (WhatsApp, etc.)
    # For sending messages to WhatsApp and other desktop messaging apps
    if MESSAGING_TOOLS_AVAILABLE and register_messaging_tools:
        register_messaging_tools(registry)
    
    # Vision tools (Phase C4) - Claude Vision (re-enabled for screen reading)
    # For reading screen content, desktop_analyze_screen doesn't need UFO
    if VISION_TOOLS_AVAILABLE and register_vision_tools:
        register_vision_tools(registry)
    
    # [Removed] Window tools (Phase 4) - PostMessage based, window isolation
    # Reason: UFO can handle window operations, low-level tools easily cause input-without-send issues
    # if WINDOW_TOOLS_AVAILABLE and register_window_tools:
    #     register_window_tools(registry)
    
    # System tools (Phase 4) - Task control (keep list_windows and other system info tools)
    if SYSTEM_TOOLS_AVAILABLE and register_system_tools:
        register_system_tools(registry)
    
    # UFO tools - Microsoft UFO AI-powered desktop automation
    if UFO_TOOLS_AVAILABLE and register_ufo_tools:
        register_ufo_tools(registry)
    
    # [DISABLED] Browser Executor - Browser Use AI vision-powered browser automation
    # Disabled Browser-Use, using Playwright instead (same as Cursor MCP)
    # if BROWSER_EXECUTOR_AVAILABLE and register_browser_executor_tools:
    #     register_browser_executor_tools(registry)
    
    # Playwright Executor - Playwright-based browser automation (like Cursor MCP)
    # This is our browser automation solution
    if PLAYWRIGHT_AVAILABLE and register_playwright_tools:
        register_playwright_tools(registry)
    
    # [DISABLED] Form Workflow - disabled, using atomic tools instead (like Cursor MCP)
    # Agent should compose playwright_snapshot + read_file + playwright_type itself
    # This enables progressive interaction, confirming with user at each step
    # if FORM_WORKFLOW_AVAILABLE and register_form_workflow_tools:
    #     register_form_workflow_tools(registry)
    
    # [DISABLED] YC Workflow - disabled, same as above
    # if YC_WORKFLOW_AVAILABLE and register_yc_workflow_tools:
    #     register_yc_workflow_tools(registry)
    
    return registry


__all__ = [
    # Core
    'ToolRegistry',
    'ToolCategory',
    'ToolDefinition',
    'ToolResult',
    'get_registry',
    'reset_registry',
    
    # Tool registration
    'register_browser_tools',
    'register_local_tools',
    'register_cursor_tools',
    'register_window_tools',
    'register_system_tools',
    'create_full_registry',
    
    # Phase 4 tools
    'WindowTools',
    'WindowLostError',
    'SystemTools',
    'TaskStatus',
    
    # Windows compatibility (Phase 4.5)
    'WindowInputController',
    'HwndManager',
    'CoordinateTransformer',
    'DPIHandler',
    'UIPIChecker',
    'WindowStateChecker',
    'MultiMonitorManager',
    'Windows11Compatibility',
    
    # Convenience functions
    'scale_coordinates',
    'can_control_window',
    'is_window_operable',
    'is_windows_11',
    'get_hwnd_manager',
    'get_dpi_handler',
    'get_monitor_manager',
    
    # UFO tools
    'register_ufo_tools',
    'UFOExecutor',
    'execute_desktop_task',
    
    # Browser Executor (Browser Use)
    'register_browser_executor_tools',
    'NogicBrowserExecutor',
    'get_browser_executor',
    
    # Availability flags
    'DESKTOP_TOOLS_AVAILABLE',
    'VISION_TOOLS_AVAILABLE',
    'WINDOW_TOOLS_AVAILABLE',
    'SYSTEM_TOOLS_AVAILABLE',
    'WINDOWS_COMPAT_AVAILABLE',
    'UFO_TOOLS_AVAILABLE',
    'BROWSER_EXECUTOR_AVAILABLE',
    'YC_WORKFLOW_AVAILABLE',
    'MESSAGING_TOOLS_AVAILABLE',
    
    # Messaging tools
    'register_messaging_tools',
    
    # YC Workflow
    'register_yc_workflow_tools',
    'execute_yc_workflow',
    'is_yc_workflow_trigger',
    'YCWorkflowContext',
]


