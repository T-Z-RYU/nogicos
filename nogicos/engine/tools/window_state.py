# -*- coding: utf-8 -*-
"""
Window State - WindowState全面检测

检测项目:
- exists: WindowYesNo存在
- visible: YesNoVisible
- minimized: YesNoMin化
- maximized: YesNoMax化
- foreground: YesNoBefore台Window
- enabled: YesNoEnable
- hung: YesNo无Response
- cloaked: YesNo被Hide (UWP/Virtual Desktop)
- on_current_desktop: YesNo在当Before虚拟桌面
"""

import ctypes
from ctypes import wintypes
import logging
from dataclasses import dataclass
from typing import Tuple, Optional

logger = logging.getLogger("nogicos.tools.window_state")


@dataclass
class WindowState:
    """完整的WindowState"""
    exists: bool           # WindowYesNostorein
    visible: bool          # YesNoVisible
    minimized: bool        # YesNoMinize
    maximized: bool        # YesNoMaxize
    foreground: bool       # YesNoBeforeplatformWindow
    enabled: bool          # YesNoEnable
    hung: bool             # YesNoNoneResponse
    cloaked: bool          # YesNobeHide (UWP/Virtual Desktop)
    on_current_desktop: bool  # YesNoinwhenBeforeVirtualdesktop
    
    def is_operable(self) -> Tuple[bool, str]:
        """
        CheckWindowYesNo可操作
        
        Returns:
            (可操作, 原因) 元组
        """
        if not self.exists:
            return False, "Window已Close"
        if self.minimized:
            return False, "Window已Min化"
        if self.hung:
            return False, "应用程序无Response"
        if self.cloaked:
            return False, "Window在其他虚拟桌面或被Hide"
        if not self.on_current_desktop:
            return False, "Window不在当Before虚拟桌面"
        if not self.enabled:
            return False, "Window已Disable"
        
        return True, "可以操作"


class WindowStateChecker:
    """全面的WindowState检测"""
    
    def __init__(self):
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self._setup_functions()
        self._virtual_desktop_manager = None
    
    def _setup_functions(self):
        """Set Windows API FunctionSignature"""
        # IsWindow
        self.user32.IsWindow.argtypes = [wintypes.HWND]
        self.user32.IsWindow.restype = wintypes.BOOL
        
        # IsWindowVisible
        self.user32.IsWindowVisible.argtypes = [wintypes.HWND]
        self.user32.IsWindowVisible.restype = wintypes.BOOL
        
        # IsIconic (minimized)
        self.user32.IsIconic.argtypes = [wintypes.HWND]
        self.user32.IsIconic.restype = wintypes.BOOL
        
        # IsZoomed (maximized)
        self.user32.IsZoomed.argtypes = [wintypes.HWND]
        self.user32.IsZoomed.restype = wintypes.BOOL
        
        # GetForegroundWindow
        self.user32.GetForegroundWindow.argtypes = []
        self.user32.GetForegroundWindow.restype = wintypes.HWND
        
        # IsWindowEnabled
        self.user32.IsWindowEnabled.argtypes = [wintypes.HWND]
        self.user32.IsWindowEnabled.restype = wintypes.BOOL
        
        # IsHungAppWindow
        self.user32.IsHungAppWindow.argtypes = [wintypes.HWND]
        self.user32.IsHungAppWindow.restype = wintypes.BOOL
    
    def get_window_state(self, hwnd: int) -> WindowState:
        """Get完整WindowState"""
        return WindowState(
            exists=self._is_window(hwnd),
            visible=self._is_visible(hwnd),
            minimized=self._is_minimized(hwnd),
            maximized=self._is_maximized(hwnd),
            foreground=self._is_foreground(hwnd),
            enabled=self._is_enabled(hwnd),
            hung=self._is_hung(hwnd),
            cloaked=self._is_cloaked(hwnd),
            on_current_desktop=self._is_on_current_desktop(hwnd),
        )
    
    def is_operable(self, hwnd: int) -> Tuple[bool, str]:
        """CheckWindowYesNo可操作"""
        state = self.get_window_state(hwnd)
        return state.is_operable()
    
    def _is_window(self, hwnd: int) -> bool:
        """CheckWindowYesNo存在"""
        return bool(self.user32.IsWindow(hwnd))
    
    def _is_visible(self, hwnd: int) -> bool:
        """CheckWindowYesNoVisible"""
        return bool(self.user32.IsWindowVisible(hwnd))
    
    def _is_minimized(self, hwnd: int) -> bool:
        """CheckWindowYesNoMin化"""
        return bool(self.user32.IsIconic(hwnd))
    
    def _is_maximized(self, hwnd: int) -> bool:
        """CheckWindowYesNoMax化"""
        return bool(self.user32.IsZoomed(hwnd))
    
    def _is_foreground(self, hwnd: int) -> bool:
        """CheckWindowYesNo为Before台Window"""
        return self.user32.GetForegroundWindow() == hwnd
    
    def _is_enabled(self, hwnd: int) -> bool:
        """CheckWindowYesNoEnable"""
        return bool(self.user32.IsWindowEnabled(hwnd))
    
    def _is_hung(self, hwnd: int) -> bool:
        """Check应用YesNo无Response"""
        return bool(self.user32.IsHungAppWindow(hwnd))
    
    def _is_cloaked(self, hwnd: int) -> bool:
        """
        CheckWindowYesNo被Hide (Windows 8+ 特性)
        
        Cloaked State用于:
        - UWP 应用Pause时
        - Window在其他虚拟桌面
        - DWM 组合Effect
        """
        try:
            dwmapi = ctypes.WinDLL('dwmapi')
            DWMWA_CLOAKED = 14
            cloaked = ctypes.c_int()
            result = dwmapi.DwmGetWindowAttribute(
                hwnd, DWMWA_CLOAKED, 
                ctypes.byref(cloaked), ctypes.sizeof(cloaked)
            )
            return result == 0 and cloaked.value != 0
        except Exception:
            return False
    
    def _is_on_current_desktop(self, hwnd: int) -> bool:
        """
        CheckWindowYesNo在当Before虚拟桌面 (Windows 10+)
        
        Usage IVirtualDesktopManager COM Interface
        """
        try:
            # DelayedInitialize Virtual Desktop Manager
            if self._virtual_desktop_manager is None:
                self._init_virtual_desktop_manager()
            
            if self._virtual_desktop_manager:
                is_on_current = ctypes.c_bool()
                hr = self._virtual_desktop_manager.IsWindowOnCurrentVirtualDesktop(
                    hwnd, ctypes.byref(is_on_current)
                )
                if hr == 0:  # S_OK
                    return is_on_current.value
        except Exception as e:
            logger.debug(f"Virtual desktop check failed: {e}")
        
        # NonemethodDetectionthenFalsesetinwhenBeforedesktop
        return True
    
    def _init_virtual_desktop_manager(self):
        """Initialize Virtual Desktop Manager COM Interface"""
        try:
            import comtypes.client
            CLSID_VirtualDesktopManager = "{AA509086-5CA9-4C25-8F95-589D3C07B48A}"
            self._virtual_desktop_manager = comtypes.client.CreateObject(
                CLSID_VirtualDesktopManager
            )
        except Exception as e:
            logger.debug(f"Cannot initialize VirtualDesktopManager: {e}")
            self._virtual_desktop_manager = None
    
    def restore_window(self, hwnd: int) -> bool:
        """
        ResumeWindow (如果Min化)
        
        Returns:
            YesNoSuccessResume
        """
        if not self._is_window(hwnd):
            return False
        
        if self._is_minimized(hwnd):
            SW_RESTORE = 9
            self.user32.ShowWindow(hwnd, SW_RESTORE)
            return True
        
        return False
    
    def bring_to_foreground(self, hwnd: int) -> bool:
        """
        将Window置于Before台
        
        Returns:
            YesNoSuccess
        """
        if not self._is_window(hwnd):
            return False
        
        # firstResume
        self.restore_window(hwnd)
        
        # SetBeforeplatform
        return bool(self.user32.SetForegroundWindow(hwnd))


# GlobalSingleton
_global_state_checker: Optional[WindowStateChecker] = None


def get_state_checker() -> WindowStateChecker:
    """GetGlobalWindowStateCheck器"""
    global _global_state_checker
    if _global_state_checker is None:
        _global_state_checker = WindowStateChecker()
    return _global_state_checker


# convenientFunction
def is_window_operable(hwnd: int) -> Tuple[bool, str]:
    """FastCheckWindowYesNo可操作"""
    return get_state_checker().is_operable(hwnd)


# Export
__all__ = [
    'WindowState',
    'WindowStateChecker',
    'get_state_checker',
    'is_window_operable',
]
