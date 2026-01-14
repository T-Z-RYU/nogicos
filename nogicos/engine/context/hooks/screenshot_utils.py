# -*- coding: utf-8 -*-
"""
Screenshot Utilities - 截GraphTool

提供Window截Graph和屏幕截Graph功能
"""

# [Fix] Ensure user-installed packages can be found
import sys
import os
_user_site = os.path.expanduser("~\\AppData\\Roaming\\Python\\Python314\\site-packages")
if _user_site not in sys.path:
    sys.path.insert(0, _user_site)

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class WindowRect:
    """Window矩形"""
    left: int
    top: int
    right: int
    bottom: int
    
    @property
    def width(self) -> int:
        return self.right - self.left
    
    @property
    def height(self) -> int:
        return self.bottom - self.top
    
    @property
    def x(self) -> int:
        return self.left
    
    @property
    def y(self) -> int:
        return self.top


async def capture_screen(region: Optional[Tuple[int, int, int, int]] = None) -> Optional[bytes]:
    """
    截取屏幕
    
    Args:
        region: Optional的区域 (x, y, width, height)，None Table示全屏
    
    Returns:
        PNG 格式的截Graph数据
    """
    try:
        import mss
        from PIL import Image
        from io import BytesIO
        
        with mss.mss() as sct:
            if region:
                monitor = {
                    "left": region[0],
                    "top": region[1],
                    "width": region[2],
                    "height": region[3],
                }
            else:
                monitor = sct.monitors[1]  # Primary monitor
            
            screenshot = sct.grab(monitor)
            
            # Convert to PNG
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()
            
    except ImportError:
        logger.error("[Screenshot] mss not installed. Run: pip install mss")
        return None
    except Exception as e:
        logger.error(f"[Screenshot] Capture failed: {e}")
        return None


async def capture_window(hwnd: int) -> Optional[bytes]:
    """
    截取SpecifyWindow
    
    Args:
        hwnd: Window句柄
    
    Returns:
        PNG 格式的截Graph数据
    """
    if sys.platform != "win32":
        logger.warning("[Screenshot] Window capture only supported on Windows")
        return None
    
    try:
        import ctypes
        from ctypes import wintypes
        
        user32 = ctypes.windll.user32
        
        # Get window position
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        # Capture region
        return await capture_screen((
            rect.left,
            rect.top,
            rect.right - rect.left,
            rect.bottom - rect.top,
        ))
        
    except Exception as e:
        logger.error(f"[Screenshot] Window capture failed: {e}")
        return None


async def get_window_rect(hwnd: int) -> Optional[WindowRect]:
    """
    GetWindowPosition和Size
    
    Args:
        hwnd: Window句柄
    
    Returns:
        WindowRect 或 None
    """
    if sys.platform != "win32":
        return None
    
    try:
        import ctypes
        from ctypes import wintypes
        
        user32 = ctypes.windll.user32
        
        rect = wintypes.RECT()
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return WindowRect(
                left=rect.left,
                top=rect.top,
                right=rect.right,
                bottom=rect.bottom,
            )
        return None
        
    except Exception as e:
        logger.error(f"[Screenshot] Get window rect failed: {e}")
        return None


async def capture_browser_address_bar(hwnd: int) -> Optional[bytes]:
    """
    截取浏览器Address栏区域
    
    浏览器Address栏通常在WindowTop 50-100 像素
    
    Args:
        hwnd: 浏览器Window句柄
    
    Returns:
        Address栏区域的截Graph
    """
    rect = await get_window_rect(hwnd)
    if not rect:
        return None
    
    # Address bar region estimate: top 30-90 pixels
    address_bar_region = (
        rect.left + 80,  # Skip browser buttons
        rect.top + 30,   # Skip title bar
        rect.width - 200,  # Minus right-side buttons
        60,              # Address bar height
    )
    
    return await capture_screen(address_bar_region)


class ScreenshotManager:
    """
    截Graph管理器
    
    提供High级截Graph功能
    """
    
    def __init__(self):
        self._cache: dict = {}
    
    async def capture_with_cache(
        self,
        key: str,
        capture_fn,
        cache_seconds: float = 1.0,
    ) -> Optional[bytes]:
        """
        带Cache的截Graph
        
        避免频繁截Graph
        """
        import time
        
        now = time.time()
        
        # Check cache
        if key in self._cache:
            cached_time, cached_data = self._cache[key]
            if now - cached_time < cache_seconds:
                return cached_data
        
        # Execute screenshot
        data = await capture_fn()
        
        if data:
            self._cache[key] = (now, data)
        
        return data
    
    def clear_cache(self):
        """ClearCache"""
        self._cache.clear()


# Global singleton
_screenshot_manager: Optional[ScreenshotManager] = None


def get_screenshot_manager() -> ScreenshotManager:
    """Get ScreenshotManager Singleton"""
    global _screenshot_manager
    if _screenshot_manager is None:
        _screenshot_manager = ScreenshotManager()
    return _screenshot_manager

