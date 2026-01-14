# -*- coding: utf-8 -*-
"""
HWND Lifecycle Manager - Window句柄生命Cycle管理

Handle场景:
- WindowClose: HWND 失效 → WindowLostError
- 应用Restart: New HWND → Auto重NewFind
- Window重建 (Switch标签页): New HWND → AutoRefresh
- WindowMax化/Restore: 可能变化 → 重NewVerify
"""

import ctypes
from ctypes import wintypes
import logging
from typing import Dict, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger("nogicos.tools.hwnd_manager")


class WindowLostError(Exception):
    """Window丢失Error"""
    pass


@dataclass
class WindowInfo:
    """WindowInfoCache"""
    hwnd: int
    title: str
    class_name: str
    process_id: int


class HwndManager:
    """HWND 生命Cycle管理器"""
    
    def __init__(self):
        self._hwnd_cache: Dict[str, int] = {}  # window_identifier -> hwnd
        self._window_info: Dict[int, WindowInfo] = {}  # hwnd -> WindowInfo
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self._setup_functions()
    
    def _setup_functions(self):
        """Set Windows API FunctionSignature"""
        # IsWindow
        self.user32.IsWindow.argtypes = [wintypes.HWND]
        self.user32.IsWindow.restype = wintypes.BOOL
        
        # FindWindowW
        self.user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        self.user32.FindWindowW.restype = wintypes.HWND
        
        # GetWindowTextW
        self.user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.user32.GetWindowTextW.restype = ctypes.c_int
        
        # GetWindowTextLengthW
        self.user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        self.user32.GetWindowTextLengthW.restype = ctypes.c_int
        
        # GetClassNameW
        self.user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.user32.GetClassNameW.restype = ctypes.c_int
        
        # GetWindowThreadProcessId
        self.user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        
        # EnumWindows
        self.WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        self.user32.EnumWindows.argtypes = [self.WNDENUMPROC, wintypes.LPARAM]
        self.user32.EnumWindows.restype = wintypes.BOOL
    
    async def get_valid_hwnd(self, window_identifier: str) -> int:
        """
        GetValid的 HWND，失效时AutoRefresh
        
        Args:
            window_identifier: Window标识符 (title或部分title)
            
        Returns:
            Valid的Window句柄
            
        Raises:
            WindowLostError: Window不存在或无法找到
        """
        hwnd = self._hwnd_cache.get(window_identifier)
        
        # Verify HWND YesNostillthenValid
        if hwnd and not self._is_window_valid(hwnd):
            logger.info(f"HWND {hwnd} invalidated, searching for window '{window_identifier}'")
            # HWND invalid，try to find again
            hwnd = await self._find_window_by_identifier(window_identifier)
            if hwnd:
                self._hwnd_cache[window_identifier] = hwnd
                self._cache_window_info(hwnd)
            else:
                # CleanupCache
                self._hwnd_cache.pop(window_identifier, None)
                raise WindowLostError(f"Window '{window_identifier}' no longer exists")
        
        if not hwnd:
            hwnd = await self._find_window_by_identifier(window_identifier)
            if hwnd:
                self._hwnd_cache[window_identifier] = hwnd
                self._cache_window_info(hwnd)
            else:
                raise WindowLostError(f"Window '{window_identifier}' not found")
        
        return hwnd
    
    def get_hwnd_sync(self, window_identifier: str) -> Optional[int]:
        """SyncGet HWND (不抛Exception)"""
        hwnd = self._hwnd_cache.get(window_identifier)
        if hwnd and self._is_window_valid(hwnd):
            return hwnd
        return None
    
    def register_hwnd(self, identifier: str, hwnd: int) -> None:
        """ManualRegister HWND"""
        if self._is_window_valid(hwnd):
            self._hwnd_cache[identifier] = hwnd
            self._cache_window_info(hwnd)
            logger.debug(f"Registered HWND {hwnd} for '{identifier}'")
        else:
            logger.warning(f"Cannot register invalid HWND {hwnd}")
    
    def _is_window_valid(self, hwnd: int) -> bool:
        """CheckWindowYesNoValid"""
        return bool(self.user32.IsWindow(hwnd))
    
    def _cache_window_info(self, hwnd: int) -> None:
        """CacheWindowInfo用于重NewFind"""
        try:
            # GetWindowtitle
            length = self.user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            self.user32.GetWindowTextW(hwnd, buffer, length)
            title = buffer.value
            
            # GetWindowClassname
            class_buffer = ctypes.create_unicode_buffer(256)
            self.user32.GetClassNameW(hwnd, class_buffer, 256)
            class_name = class_buffer.value
            
            # GetProcess ID
            process_id = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            
            self._window_info[hwnd] = WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_name,
                process_id=process_id.value
            )
            
            logger.debug(f"Cached window info: hwnd={hwnd}, title='{title}', class='{class_name}'")
            
        except Exception as e:
            logger.warning(f"Failed to cache window info for hwnd {hwnd}: {e}")
    
    async def _find_window_by_identifier(self, identifier: str) -> Optional[int]:
        """Root据标识符FindWindow"""
        # Method 1: precisetitleMatch
        hwnd = self.user32.FindWindowW(None, identifier)
        if hwnd:
            logger.debug(f"Found window by exact title: '{identifier}' -> {hwnd}")
            return hwnd
        
        # Method 2: modeblurtitleMatch
        found_hwnd = None
        identifier_lower = identifier.lower()
        
        def enum_callback(hwnd, lparam):
            nonlocal found_hwnd
            if found_hwnd:  # alreadyfindto，StopEnum
                return False
            
            try:
                length = self.user32.GetWindowTextLengthW(hwnd) + 1
                buffer = ctypes.create_unicode_buffer(length)
                self.user32.GetWindowTextW(hwnd, buffer, length)
                
                if identifier_lower in buffer.value.lower():
                    found_hwnd = hwnd
                    return False  # StopEnum
            except:
                pass
            return True
        
        try:
            # [Segfault Repair]MustkeepCallbackInstance's Reference，Nothenwillbe GC causeCrash
            callback_instance = self.WNDENUMPROC(enum_callback)
            self.user32.EnumWindows(callback_instance, 0)
        except Exception as e:
            logger.debug(f"EnumWindows exception (expected): {e}")
        
        if found_hwnd:
            logger.debug(f"Found window by partial title: '{identifier}' -> {found_hwnd}")
        
        return found_hwnd
    
    def invalidate(self, hwnd: int) -> None:
        """标记 HWND 为失效"""
        # fromCacheMediumRemove
        to_remove = [k for k, v in self._hwnd_cache.items() if v == hwnd]
        for key in to_remove:
            del self._hwnd_cache[key]
            logger.debug(f"Invalidated HWND {hwnd} for key '{key}'")
        self._window_info.pop(hwnd, None)
    
    def invalidate_all(self) -> None:
        """Clear所有Cache"""
        self._hwnd_cache.clear()
        self._window_info.clear()
        logger.info("Invalidated all HWND cache")
    
    def get_window_title(self, hwnd: int) -> str:
        """GetWindowtitle"""
        if hwnd in self._window_info:
            return self._window_info[hwnd].title
        
        try:
            length = self.user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            self.user32.GetWindowTextW(hwnd, buffer, length)
            return buffer.value
        except:
            return ""
    
    def get_cached_info(self, hwnd: int) -> Optional[WindowInfo]:
        """GetCache的WindowInfo"""
        return self._window_info.get(hwnd)
    
    def list_cached_windows(self) -> Dict[str, int]:
        """Column出所有Cache的Window"""
        return dict(self._hwnd_cache)


# GlobalSingleton
_global_hwnd_manager: Optional[HwndManager] = None


def get_hwnd_manager() -> HwndManager:
    """GetGlobal HWND 管理器"""
    global _global_hwnd_manager
    if _global_hwnd_manager is None:
        _global_hwnd_manager = HwndManager()
    return _global_hwnd_manager


# Export
__all__ = [
    'WindowLostError',
    'WindowInfo',
    'HwndManager',
    'get_hwnd_manager',
]
