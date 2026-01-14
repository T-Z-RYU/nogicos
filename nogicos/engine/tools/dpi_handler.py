# -*- coding: utf-8 -*-
"""
DPI Handler - DPI 缩放Handle器

DPI Set与截Graph尺寸的Off系:
+------------+------------+----------------+-----------+
| DPI Set   | 截Graph尺寸   | 实际Window尺寸   | Coordinate偏差  |
+------------+------------+----------------+-----------+
| 100%       | 1280x800   | 1280x800       | 0%        |
| 125%       | 1280x800   | 1600x1000      | 25%       |
| 150%       | 1280x800   | 1920x1200      | 50%       |
+------------+------------+----------------+-----------+

如果不Handle DPI，点击Coordinate会有 25%-50% 的偏差!
"""

import ctypes
from ctypes import wintypes
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger("nogicos.tools.dpi_handler")


@dataclass
class MonitorDPIInfo:
    """Display器 DPI Info"""
    monitor_handle: int
    dpi_x: int
    dpi_y: int
    scale_factor: float  # dpi / 96
    monitor_rect: Tuple[int, int, int, int]
    work_rect: Tuple[int, int, int, int]
    is_primary: bool


class DPIHandler:
    """DPI 缩放Handle器"""
    
    # Standard DPI (100%)
    STANDARD_DPI = 96
    
    def __init__(self):
        self._dpi_cache: Dict[int, float] = {}  # hwnd -> scale_factor
        self._setup_api()
    
    def _setup_api(self):
        """Set Windows API"""
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        
        # CheckAvailable's  DPI API
        self._api_level = self._detect_api_level()
        logger.debug(f"DPI API level: {self._api_level}")
        
        if self._api_level >= 3:
            # Windows 10 1607+ GetDpiForWindow
            self.user32.GetDpiForWindow.argtypes = [wintypes.HWND]
            self.user32.GetDpiForWindow.restype = wintypes.UINT
        
        # MonitorFromWindow
        self.user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
        self.user32.MonitorFromWindow.restype = wintypes.HMONITOR
        
        # GetMonitorInfoW
        self.user32.GetMonitorInfoW.argtypes = [wintypes.HMONITOR, ctypes.c_void_p]
        self.user32.GetMonitorInfoW.restype = wintypes.BOOL
    
    def _detect_api_level(self) -> int:
        """
        检测Available的 DPI API 级别
        
        Returns:
            3: Windows 10 1607+ (GetDpiForWindow)
            2: Windows 8.1+ (GetDpiForMonitor)
            1: Windows Vista+ (GetDeviceCaps)
        """
        try:
            # try GetDpiForWindow
            self.user32.GetDpiForWindow
            return 3
        except AttributeError:
            pass
        
        try:
            # try GetDpiForMonitor
            shcore = ctypes.WinDLL('shcore')
            shcore.GetDpiForMonitor
            return 2
        except:
            pass
        
        return 1
    
    def get_window_dpi(self, hwnd: int) -> float:
        """
        GetWindow DPI 缩放比例
        
        Args:
            hwnd: Window句柄
            
        Returns:
            DPI 缩放比例 (1.0 = 100%, 1.25 = 125%, etc.)
        """
        if hwnd in self._dpi_cache:
            return self._dpi_cache[hwnd]
        
        dpi_scale = self._query_dpi(hwnd)
        self._dpi_cache[hwnd] = dpi_scale
        
        logger.debug(f"Window {hwnd} DPI scale: {dpi_scale:.2f} ({int(dpi_scale * 100)}%)")
        return dpi_scale
    
    def _query_dpi(self, hwnd: int) -> float:
        """Query DPI"""
        # Method 1: Windows 10 1607+ GetDpiForWindow
        if self._api_level >= 3:
            try:
                dpi = self.user32.GetDpiForWindow(hwnd)
                if dpi > 0:
                    return dpi / self.STANDARD_DPI
            except Exception as e:
                logger.debug(f"GetDpiForWindow failed: {e}")
        
        # Method 2: GetDpiForMonitor
        if self._api_level >= 2:
            try:
                shcore = ctypes.WinDLL('shcore')
                MDT_EFFECTIVE_DPI = 0
                monitor = self.user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
                dpi_x = ctypes.c_uint()
                dpi_y = ctypes.c_uint()
                shcore.GetDpiForMonitor(
                    monitor, MDT_EFFECTIVE_DPI,
                    ctypes.byref(dpi_x), ctypes.byref(dpi_y)
                )
                if dpi_x.value > 0:
                    return dpi_x.value / self.STANDARD_DPI
            except Exception as e:
                logger.debug(f"GetDpiForMonitor failed: {e}")
        
        # Method 3: GetDeviceCaps (last resort)
        hdc = None
        try:
            hdc = self.user32.GetDC(hwnd)
            if hdc:
                gdi32 = ctypes.WinDLL('gdi32')
                LOGPIXELSX = 88
                dpi = gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
                if dpi > 0:
                    return dpi / self.STANDARD_DPI
        except Exception as e:
            logger.debug(f"GetDeviceCaps failed: {e}")
        finally:
            if hdc:
                self.user32.ReleaseDC(hwnd, hdc)
        
        return 1.0  # Default 100%
    
    def invalidate_cache(self, hwnd: Optional[int] = None) -> None:
        """Clear DPI Cache"""
        if hwnd:
            self._dpi_cache.pop(hwnd, None)
        else:
            self._dpi_cache.clear()
    
    def get_monitor_info(self, hwnd: int) -> Optional[MonitorDPIInfo]:
        """GetWindow所在Display器 DPI Info"""
        try:
            monitor = self.user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
            
            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT),
                    ("dwFlags", wintypes.DWORD)
                ]
            
            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(MONITORINFO)
            
            if not self.user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
                return None
            
            # Get DPI
            dpi_x, dpi_y = self.STANDARD_DPI, self.STANDARD_DPI
            if self._api_level >= 2:
                try:
                    shcore = ctypes.WinDLL('shcore')
                    dx, dy = ctypes.c_uint(), ctypes.c_uint()
                    shcore.GetDpiForMonitor(monitor, 0, ctypes.byref(dx), ctypes.byref(dy))
                    dpi_x, dpi_y = dx.value, dy.value
                except:
                    pass
            
            return MonitorDPIInfo(
                monitor_handle=monitor,
                dpi_x=dpi_x,
                dpi_y=dpi_y,
                scale_factor=dpi_x / self.STANDARD_DPI,
                monitor_rect=(
                    info.rcMonitor.left, info.rcMonitor.top,
                    info.rcMonitor.right, info.rcMonitor.bottom
                ),
                work_rect=(
                    info.rcWork.left, info.rcWork.top,
                    info.rcWork.right, info.rcWork.bottom
                ),
                is_primary=bool(info.dwFlags & 1),
            )
            
        except Exception as e:
            logger.error(f"Failed to get monitor info: {e}")
            return None
    
    def scale_for_dpi(self, x: int, y: int, hwnd: int) -> Tuple[int, int]:
        """
        Root据 DPI 缩放Coordinate
        
        用于将逻辑CoordinateConvert为物理像素Coordinate
        """
        scale = self.get_window_dpi(hwnd)
        return int(x * scale), int(y * scale)
    
    def unscale_for_dpi(self, x: int, y: int, hwnd: int) -> Tuple[int, int]:
        """
        反向 DPI 缩放
        
        用于将物理像素CoordinateConvert为逻辑Coordinate
        """
        scale = self.get_window_dpi(hwnd)
        if scale == 0:
            return x, y
        return int(x / scale), int(y / scale)


# GlobalSingleton
_global_dpi_handler: Optional[DPIHandler] = None


def get_dpi_handler() -> DPIHandler:
    """GetGlobal DPI Handle器"""
    global _global_dpi_handler
    if _global_dpi_handler is None:
        _global_dpi_handler = DPIHandler()
    return _global_dpi_handler


# Export
__all__ = [
    'MonitorDPIInfo',
    'DPIHandler',
    'get_dpi_handler',
]
