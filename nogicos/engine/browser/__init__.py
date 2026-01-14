# -*- coding: utf-8 -*-
"""
NogicOS Browser Module

Provides browser automation capabilities:
- BrowserSession: Playwright-based browser control
- CDP integration (future): Electron WebContentsView control
"""

from .session import (
    BrowserSession,
    BrowserState,
    get_browser_session,
    close_browser_session,
    PLAYWRIGHT_AVAILABLE,
)

__all__ = [
    'BrowserSession',
    'BrowserState',
    'get_browser_session',
    'close_browser_session',
    'PLAYWRIGHT_AVAILABLE',
]

