# -*- coding: utf-8 -*-
"""
Coordinate System - CoordinateSystemConvert

CoordinateSystemOff系Graph:
┌─────────────────────────────────────────┐
│ Screen Coordinates (0,0 = LeftUp角)        │
│  ┌───────────────────────────────┐      │
│  │ Window (GetWindowRect)         │      │
│  │  ┌─────────────────────────┐  │      │
│  │  │ Client Area             │  │      │
│  │  │ (GetClientRect)         │  │      │
│  │  │                         │  │      │
│  │  │ ← PostMessage 需要的Coordinate │  │      │
│  │  └─────────────────────────┘  │      │
│  │  ↑ title栏、Border             │      │
│  └───────────────────────────────┘      │
└─────────────────────────────────────────┘

Key区分:
- GetWindowRect: Package含Border和title栏的完整Window矩形
- GetClientRect: 客户区 (可Draw区域) 矩形
- ClientToScreen: 客户区Coordinate → 屏幕Coordinate
- PostMessage: 需要客户区Coordinate
"""

import ctypes
from ctypes import wintypes
import logging
from dataclasses import dataclass
from typing import Tuple

logger = logging.getLogger("nogicos.tools.coordinate_system")


@dataclass
class WindowCoordinates:
    """WindowCoordinateInfo"""
    # WindowRectangle (ScreenCoordinate，PackagecontainBorder)
    window_rect: Tuple[int, int, int, int]  # (left, top, right, bottom)
    # Client AreaRectangle (RelativeatWindow，notPackagecontainBorder)
    client_rect: Tuple[int, int, int, int]  # (0, 0, width, height)
    # Client AreainScreenUp's Position
    client_origin: Tuple[int, int]  # (x, y)
    # DPI ScalingbecauseChild
    dpi_scale: float
    
    @property
    def client_width(self) -> int:
        return self.client_rect[2] - self.client_rect[0]
    
    @property
    def client_height(self) -> int:
        return self.client_rect[3] - self.client_rect[1]
    
    @property
    def window_width(self) -> int:
        return self.window_rect[2] - self.window_rect[0]
    
    @property
    def window_height(self) -> int:
        return self.window_rect[3] - self.window_rect[1]


class CoordinateTransformer:
    """CoordinateConvert器 - Handle所有CoordinateSystemConvert"""
    
    # captureGraphTargetSize (Anthropic Reference)
    TARGET_WIDTH = 1280
    TARGET_HEIGHT = 800
    
    def __init__(self, target_size: Tuple[int, int] = None):
        self.target_size = target_size or (self.TARGET_WIDTH, self.TARGET_HEIGHT)
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self._setup_functions()
    
    def _setup_functions(self):
        """Set Windows API FunctionSignature"""
        # GetWindowRect
        self.user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.user32.GetWindowRect.restype = wintypes.BOOL
        
        # GetClientRect
        self.user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.user32.GetClientRect.restype = wintypes.BOOL
        
        # ClientToScreen
        self.user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
        self.user32.ClientToScreen.restype = wintypes.BOOL
        
        # GetDpiForWindow (Windows 10 1607+)
        try:
            self.user32.GetDpiForWindow.argtypes = [wintypes.HWND]
            self.user32.GetDpiForWindow.restype = wintypes.UINT
            self._has_per_window_dpi = True
        except AttributeError:
            self._has_per_window_dpi = False
    
    def get_window_coordinates(self, hwnd: int) -> WindowCoordinates:
        """GetWindow的完整CoordinateInfo"""
        # 1. GetWindowRectangle (ScreenCoordinate)
        window_rect = wintypes.RECT()
        self.user32.GetWindowRect(hwnd, ctypes.byref(window_rect))
        
        # 2. GetClient AreaRectangle (RelativeCoordinate)
        client_rect = wintypes.RECT()
        self.user32.GetClientRect(hwnd, ctypes.byref(client_rect))
        
        # 3. GetClient AreaoriginalPointinScreenUp's Position
        point = wintypes.POINT(0, 0)
        self.user32.ClientToScreen(hwnd, ctypes.byref(point))
        
        # 4. Get DPI Scaling
        dpi_scale = self._get_dpi_scale(hwnd)
        
        return WindowCoordinates(
            window_rect=(window_rect.left, window_rect.top, window_rect.right, window_rect.bottom),
            client_rect=(client_rect.left, client_rect.top, client_rect.right, client_rect.bottom),
            client_origin=(point.x, point.y),
            dpi_scale=dpi_scale
        )
    
    def screenshot_to_client(self, x: int, y: int, hwnd: int) -> Tuple[int, int]:
        """
        将截GraphCoordinateConvert为客户区Coordinate
        
        截GraphYes 1280x800，需要Convert到实际客户区尺寸
        
        Args:
            x, y: 截GraphUp的Coordinate (相对于 1280x800)
            hwnd: TargetWindow句柄
            
        Returns:
            客户区Coordinate (x, y)
        """
        coords = self.get_window_coordinates(hwnd)
        
        # calculateScalingbecauseChild
        scale_x = coords.client_width / self.target_size[0]
        scale_y = coords.client_height / self.target_size[1]
        
        # ApplyScaling (no need to multiply again DPI，becausecaptureGraphalreadyYesActualPixel)
        client_x = int(x * scale_x)
        client_y = int(y * scale_y)
        
        logger.debug(
            f"screenshot_to_client: ({x}, {y}) -> ({client_x}, {client_y}) "
            f"[scale: {scale_x:.2f}x{scale_y:.2f}, client: {coords.client_width}x{coords.client_height}]"
        )
        
        return client_x, client_y
    
    def client_to_screenshot(self, x: int, y: int, hwnd: int) -> Tuple[int, int]:
        """
        将客户区CoordinateConvert为截GraphCoordinate
        
        Args:
            x, y: 客户区Coordinate
            hwnd: TargetWindow句柄
            
        Returns:
            截GraphCoordinate (x, y) (相对于 1280x800)
        """
        coords = self.get_window_coordinates(hwnd)
        
        # calculateScalingbecauseChild
        scale_x = self.target_size[0] / coords.client_width
        scale_y = self.target_size[1] / coords.client_height
        
        screenshot_x = int(x * scale_x)
        screenshot_y = int(y * scale_y)
        
        return screenshot_x, screenshot_y
    
    def client_to_screen(self, x: int, y: int, hwnd: int) -> Tuple[int, int]:
        """将客户区CoordinateConvert为屏幕Coordinate"""
        point = wintypes.POINT(x, y)
        self.user32.ClientToScreen(hwnd, ctypes.byref(point))
        return point.x, point.y
    
    def get_postmessage_lparam(self, hwnd: int, client_x: int, client_y: int) -> int:
        """
        Get PostMessage 需要的 lParam
        
        VerifyCoordinate在客户区Inner，并打Package为 lParam
        """
        coords = self.get_window_coordinates(hwnd)
        
        # VerifyCoordinateinClient AreaInner
        if not (0 <= client_x < coords.client_width and 0 <= client_y < coords.client_height):
            logger.warning(
                f"Coordinates ({client_x}, {client_y}) outside client area "
                f"(0,0)-({coords.client_width},{coords.client_height})"
            )
        
        # hitPackagefor lParam: x in low word, y in high word
        lparam = (client_y << 16) | (client_x & 0xFFFF)
        return lparam
    
    def _get_dpi_scale(self, hwnd: int) -> float:
        """GetWindow DPI 缩放比例"""
        if self._has_per_window_dpi:
            try:
                dpi = self.user32.GetDpiForWindow(hwnd)
                if dpi > 0:
                    return dpi / 96.0
            except Exception:
                pass
        
        # Fallback: GetDisplayer DPI
        try:
            shcore = ctypes.WinDLL('shcore', use_last_error=True)
            MDT_EFFECTIVE_DPI = 0
            monitor = self.user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
            dpi_x = ctypes.c_uint()
            dpi_y = ctypes.c_uint()
            shcore.GetDpiForMonitor(
                monitor, MDT_EFFECTIVE_DPI, 
                ctypes.byref(dpi_x), ctypes.byref(dpi_y)
            )
            if dpi_x.value > 0:
                return dpi_x.value / 96.0
        except Exception:
            pass
        
        return 1.0  # Default 100%


def scale_coordinates(source: str, x: int, y: int, hwnd: int) -> Tuple[int, int]:
    """
    Coordinate缩放 - 便捷Function
    
    Args:
        source: "api" (从截GraphCoordinate转Window) 或 "window" (从WindowCoordinate转截Graph)
        x, y: InputCoordinate
        hwnd: TargetWindow句柄
    
    Returns:
        ConvertAfter的Coordinate
    """
    transformer = CoordinateTransformer()
    
    if source == "api":
        # fromcaptureGraphCoordinate (1280x800) ConvertforClient AreaCoordinate
        return transformer.screenshot_to_client(x, y, hwnd)
    else:
        # fromClient AreaCoordinateConvertforcaptureGraphCoordinate
        return transformer.client_to_screenshot(x, y, hwnd)


# GlobalSingleton
_global_transformer: CoordinateTransformer = None


def get_transformer() -> CoordinateTransformer:
    """GetGlobalCoordinateConvert器"""
    global _global_transformer
    if _global_transformer is None:
        _global_transformer = CoordinateTransformer()
    return _global_transformer


# Export
__all__ = [
    'WindowCoordinates',
    'CoordinateTransformer',
    'scale_coordinates',
    'get_transformer',
]
