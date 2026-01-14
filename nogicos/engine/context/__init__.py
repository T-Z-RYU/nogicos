# -*- coding: utf-8 -*-
"""
Context Module - Automatic context injection for NogicOS Agent

This module provides automatic context collection and injection, similar to Cursor's
approach of enriching each message with relevant information about the user's environment.

Components:
- ContextInjector: Main class for collecting and injecting context
- WorkspaceInfo: Workspace structure and metadata
- TerminalTracker: Recent terminal command history
- HookManager: Hook system for real-time context awareness
- ContextStore: Persistent context storage
"""

from .injector import ContextInjector, ContextConfig, get_context_injector
from .workspace import WorkspaceInfo, get_workspace_layout
from .terminal import TerminalTracker
from .store import (
    ContextStore,
    get_context_store,
    HookType,
    HookStatus,
    HookState,
    BrowserContext,
    DesktopContext,
    FileContext,
    AppContext,
    AppType,
)
from .hook_manager import HookManager, get_hook_manager, ConnectionTarget

__all__ = [
    # Original exports
    "ContextInjector",
    "ContextConfig",
    "get_context_injector",
    "WorkspaceInfo",
    "get_workspace_layout",
    "TerminalTracker",
    # Hook system exports
    "HookManager",
    "get_hook_manager",
    "ConnectionTarget",
    "ContextStore",
    "get_context_store",
    "HookType",
    "HookStatus",
    "HookState",
    "BrowserContext",
    "DesktopContext",
    "FileContext",
    # New universal App connector
    "AppContext",
    "AppType",
]

