# -*- coding: utf-8 -*-
"""
NogicOS Hook System - Hooks Package

各种Class型的 Hook Implement：
- BrowserHook: 浏览器感知
- DesktopHook: 桌面Window感知
- FileHook: FileSystem感知
"""

from .base_hook import BaseHook, HookConfig
from .browser_hook import BrowserHook
from .desktop_hook import DesktopHook
from .file_hook import FileHook

__all__ = [
    "BaseHook",
    "HookConfig",
    "BrowserHook",
    "DesktopHook", 
    "FileHook",
]

