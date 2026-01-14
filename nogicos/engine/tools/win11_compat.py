# -*- coding: utf-8 -*-
"""
Windows 11 Compatibility - Windows 11 特有问题Handle

Windows 11 特性影响:
- 圆角Window: GetWindowRect Return的矩形Package含圆角Outer的Transparent区域
- Snap Layouts: WindowPosition可能被SystemAuto调整
- Mica/Acrylic: 截Graph可能Package含模糊Effect
- New的任务栏Row为

Usage DwmGetWindowAttribute Get实际Visible区域
"""

import ctypes
from ctypes import wintypes
import logging
from typing import Tuple, Optional

logger = logging.getLogger("nogicos.tools.win11_compat")


class Windows11Compatibility:
    """Windows 11 特有问题Handle"""
    
    # Windows 11 build number start value
    WIN11_BUILD_START = 22000
    
    # DWM PropertyConstant
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    DWMWA_WINDOW_CORNER_PREFERENCE = 33
    DWMWA_BORDER_COLOR = 34
    DWMWA_CAPTION_COLOR = 35
    DWMWA_TEXT_COLOR = 36
    DWMWA_VISIBLE_FRAME_BORDER_THICKNESS = 37
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    
    # RoundedPreferences
    DWMWCP_DEFAULT = 0       # SystemDefault
    DWMWCP_DONOTROUND = 1    # notUsageRounded
    DWMWCP_ROUND = 2         # Rounded
    DWMWCP_ROUNDSMALL = 3    # SmallRounded
    
    # BackgroundClasstype (Mica, Acrylic)
    DWMSBT_AUTO = 0
    DWMSBT_NONE = 1
    DWMSBT_MAINWINDOW = 2    # Mica
    DWMSBT_TRANSIENTWINDOW = 3  # Acrylic
    DWMSBT_TABBEDWINDOW = 4  # Mica Alt
    
    def __init__(self):
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self.dwmapi = ctypes.WinDLL('dwmapi', use_last_error=True)
        self.ntdll = ctypes.WinDLL('ntdll', use_last_error=True)
        self._is_win11: Optional[bool] = None
        self._build_number: Optional[int] = None
    
    def is_windows_11(self) -> bool:
        """检测YesNoYes Windows 11"""
        if self._is_win11 is not None:
            return self._is_win11
        
        self._is_win11 = self._get_build_number() >= self.WIN11_BUILD_START
        return self._is_win11
    
    def _get_build_number(self) -> int:
        """Get Windows build 号"""
        if self._build_number is not None:
            return self._build_number
        
        try:
            # Usage RtlGetVersion GetTruerealVersion
            class OSVERSIONINFOW(ctypes.Structure):
                _fields_ = [
                    ("dwOSVersionInfoSize", wintypes.DWORD),
                    ("dwMajorVersion", wintypes.DWORD),
                    ("dwMinorVersion", wintypes.DWORD),
                    ("dwBuildNumber", wintypes.DWORD),
                    ("dwPlatformId", wintypes.DWORD),
                    ("szCSDVersion", wintypes.WCHAR * 128)
                ]
            
            version_info = OSVERSIONINFOW()
            version_info.dwOSVersionInfoSize = ctypes.sizeof(OSVERSIONINFOW)
            
            self.ntdll.RtlGetVersion(ctypes.byref(version_info))
            self._build_number = version_info.dwBuildNumber
            
            logger.debug(
                f"Windows version: {version_info.dwMajorVersion}."
                f"{version_info.dwMinorVersion} Build {version_info.dwBuildNumber}"
            )
            
            return self._build_number
            
        except Exception as e:
            logger.warning(f"Failed to get Windows version: {e}")
            self._build_number = 0
            return 0
    
    def get_actual_window_rect(self, hwnd: int) -> Tuple[int, int, int, int]:
        """
        Get实际Window矩形 (排除圆角Transparent区域)
        
        Windows 11 的圆角Window导致 GetWindowRect Return的矩形
        比实际Visible区域大
        
        Args:
            hwnd: Window句柄
            
        Returns:
            (left, top, right, bottom) 实际Visible区域
        """
        # Usage DwmGetWindowAttribute GetExtendframeBoundary
        try:
            rect = wintypes.RECT()
            result = self.dwmapi.DwmGetWindowAttribute(
                hwnd, self.DWMWA_EXTENDED_FRAME_BOUNDS,
                ctypes.byref(rect), ctypes.sizeof(rect)
            )
            if result == 0:  # S_OK
                return (rect.left, rect.top, rect.right, rect.bottom)
        except Exception as e:
            logger.debug(f"DwmGetWindowAttribute failed: {e}")
        
        # Fallback: UsageStandard GetWindowRect
        rect = wintypes.RECT()
        self.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        return (rect.left, rect.top, rect.right, rect.bottom)
    
    def set_window_corner_preference(self, hwnd: int, preference: str = "round") -> bool:
        """
        SetWindow圆角偏好
        
        Args:
            hwnd: Window句柄
            preference: "default", "round", "round_small", "square"
            
        Returns:
            YesNoSetSuccess
        """
        preferences = {
            "default": self.DWMWCP_DEFAULT,
            "square": self.DWMWCP_DONOTROUND,
            "round": self.DWMWCP_ROUND,
            "round_small": self.DWMWCP_ROUNDSMALL,
        }
        
        value = ctypes.c_int(preferences.get(preference, self.DWMWCP_ROUND))
        
        try:
            result = self.dwmapi.DwmSetWindowAttribute(
                hwnd, self.DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(value), ctypes.sizeof(value)
            )
            return result == 0
        except Exception as e:
            logger.debug(f"Failed to set corner preference: {e}")
            return False
    
    def set_window_backdrop(self, hwnd: int, backdrop: str = "mica") -> bool:
        """
        SetWindowBackgroundEffect (Windows 11 only)
        
        Args:
            hwnd: Window句柄
            backdrop: "none", "mica", "acrylic", "tabbed"
            
        Returns:
            YesNoSetSuccess
        """
        if not self.is_windows_11():
            return False
        
        backdrops = {
            "auto": self.DWMSBT_AUTO,
            "none": self.DWMSBT_NONE,
            "mica": self.DWMSBT_MAINWINDOW,
            "acrylic": self.DWMSBT_TRANSIENTWINDOW,
            "tabbed": self.DWMSBT_TABBEDWINDOW,
        }
        
        value = ctypes.c_int(backdrops.get(backdrop, self.DWMSBT_AUTO))
        
        try:
            result = self.dwmapi.DwmSetWindowAttribute(
                hwnd, self.DWMWA_SYSTEMBACKDROP_TYPE,
                ctypes.byref(value), ctypes.sizeof(value)
            )
            return result == 0
        except Exception as e:
            logger.debug(f"Failed to set backdrop: {e}")
            return False
    
    def get_visible_frame_thickness(self, hwnd: int) -> int:
        """
        GetVisible帧Border厚度
        
        Returns:
            Border厚度 (像素)
        """
        try:
            thickness = ctypes.c_uint()
            result = self.dwmapi.DwmGetWindowAttribute(
                hwnd, self.DWMWA_VISIBLE_FRAME_BORDER_THICKNESS,
                ctypes.byref(thickness), ctypes.sizeof(thickness)
            )
            if result == 0:
                return thickness.value
        except Exception:
            pass
        
        return 0
    
    def adjust_coordinates_for_rounded_corners(
        self, x: int, y: int, hwnd: int
    ) -> Tuple[int, int]:
        """
        调整Coordinate以补偿圆角Border
        
        如果点击Position接近Window角落，可能需要调整
        """
        if not self.is_windows_11():
            return x, y
        
        # GetStandardWindowRectangleandActualVisibleLocale
        standard_rect = wintypes.RECT()
        self.user32.GetWindowRect(hwnd, ctypes.byref(standard_rect))
        
        actual_rect = self.get_actual_window_rect(hwnd)
        
        # calculateOffset
        offset_left = actual_rect[0] - standard_rect.left
        offset_top = actual_rect[1] - standard_rect.top
        
        # ApplyOffset
        adjusted_x = x + offset_left
        adjusted_y = y + offset_top
        
        return adjusted_x, adjusted_y
    
    def is_snap_layout_active(self, hwnd: int) -> bool:
        """
        检测WindowYesNo处于 Snap Layout State
        
        (简化Implement - CheckWindowYesNo占据屏幕特定比例)
        """
        if not self.is_windows_11():
            return False
        
        # GetWindowandScreenSize
        rect = self.get_actual_window_rect(hwnd)
        win_width = rect[2] - rect[0]
        win_height = rect[3] - rect[1]
        
        # GetmainDisplayerSize
        screen_width = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        
        # check common snap ratios (50%, 33%, 25%)
        snap_ratios = [0.5, 0.33, 0.25, 0.67, 0.75]
        
        for ratio in snap_ratios:
            if abs(win_width / screen_width - ratio) < 0.05:
                return True
            if abs(win_height / screen_height - ratio) < 0.05:
                return True
        
        return False


# GlobalSingleton
_global_win11_compat: Optional[Windows11Compatibility] = None


def get_win11_compat() -> Windows11Compatibility:
    """GetGlobal Windows 11 兼容性Handle器"""
    global _global_win11_compat
    if _global_win11_compat is None:
        _global_win11_compat = Windows11Compatibility()
    return _global_win11_compat


# convenientFunction
def is_windows_11() -> bool:
    """检测YesNoYes Windows 11"""
    return get_win11_compat().is_windows_11()


def get_actual_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """Get实际Window矩形"""
    return get_win11_compat().get_actual_window_rect(hwnd)


# Export
__all__ = [
    'Windows11Compatibility',
    'get_win11_compat',
    'is_windows_11',
    'get_actual_window_rect',
]
