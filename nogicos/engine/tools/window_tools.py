# -*- coding: utf-8 -*-
"""
Window Tools - Window隔离Tool

整合所有 Windows 兼容性Handle:
- PostMessage 点击 (非侵入式)
- CoordinateConvert (截GraphCoordinate ↔ 客户区Coordinate)
- DPI Handle
- UIPI PermissionCheck
- WindowState检测
- HWND 生命Cycle管理

参考:
- Anthropic Computer Use: Coordinate缩放
- ByteBot: 750ms WaitTime
"""

import asyncio
import base64
import logging
from typing import Optional, Tuple
from io import BytesIO
from dataclasses import dataclass
import json as _json
from pathlib import Path as _Path
import time

# Import compatibility modules
from .windows_compat import WindowInputController, InputResult, InputMethod
from .hwnd_manager import HwndManager, WindowLostError, get_hwnd_manager
from .coordinate_system import CoordinateTransformer, scale_coordinates, get_transformer
from .dpi_handler import DPIHandler, get_dpi_handler
from .uipi_checker import UIPIChecker, get_uipi_checker
from .window_state import WindowStateChecker, get_state_checker
from .win11_compat import get_win11_compat

logger = logging.getLogger("nogicos.tools.window_tools")

# #region agent log helper (debug mode)
_DEBUG_LOG_PATH = _Path(r"c:\Users\WIN\Desktop\Cursor Project\.cursor\debug.log")

def _win_dbg_log(hypothesis_id: str, location: str, message: str, data: dict):
    import os
    try:
        payload = {
            "sessionId": "debug-session",
            "runId": "pre-fix-1",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        _DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(_DEBUG_LOG_PATH), os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        try:
            line = _json.dumps(payload, ensure_ascii=False) + "\n"
            os.write(fd, line.encode("utf-8"))
            os.fsync(fd)  # Force flush to disk immediately (prevent segfault data loss)
        finally:
            os.close(fd)
    except Exception:
        pass
# #endregion


@dataclass
class WindowToolResult:
    """Window tool execution result"""
    success: bool
    output: str
    base64_image: Optional[str] = None
    error: Optional[str] = None
    input_method: Optional[InputMethod] = None
    fallback_count: int = 0


class WindowTools:
    """
    Window tools - integrates all compatibility handling
    
    Provides high-level API for window automation operations
    """
    
    # Post-action wait time (reference: ByteBot)
    POST_ACTION_DELAY_MS = 750
    
    def __init__(self):
        self.input_controller = WindowInputController()
        self.hwnd_manager = get_hwnd_manager()
        self.coord_transformer = get_transformer()
        self.dpi_handler = get_dpi_handler()
        self.uipi_checker = get_uipi_checker()
        self.state_checker = get_state_checker()
        self.win11_compat = get_win11_compat()
    
    async def window_click(
        self, 
        x: int, 
        y: int, 
        hwnd: int,
        button: str = "left",
        capture_screenshot: bool = True
    ) -> WindowToolResult:
        """
        Click window - full version
        
        Includes: coordinate conversion, DPI handling, fallback policy, state check
        
        Args:
            x: Screenshot coordinate X (relative to 1280x800)
            y: Screenshot coordinate Y (relative to 1280x800)
            hwnd: Target window handle
            button: "left", "right", "middle"
            capture_screenshot: Whether to capture screenshot after operation
            
        Returns:
            WindowToolResult
        """
        # #region agent log H7
        _win_dbg_log("H7", "window_click:start", "window_click called", {"hwnd": hwnd, "x": x, "y": y, "button": button})
        # #endregion
        
        # 1. Check window operability
        operable, reason = self.state_checker.is_operable(hwnd)
        if not operable:
            return WindowToolResult(
                success=False,
                output="",
                error=f"Window not operable: {reason}"
            )
        
        # #region agent log H7
        _win_dbg_log("H7", "window_click:operable", "Window operable check passed", {"operable": operable})
        # #endregion
        
        # 2. Check UIPI Permission
        accessibility = self.uipi_checker.check_window_accessibility(hwnd)
        if not accessibility.accessible:
            return WindowToolResult(
                success=False,
                output="",
                error=f"Insufficient permission: {accessibility.reason}\nSuggestion: {accessibility.suggestion}"
            )
        
        # 3. Use coordinates directly (screenshot is original size, Agent passes correct coordinates)
        # Note: Previous scale_coordinates would incorrectly scale coordinates, assuming screenshot was 1280x800
        # But we actually return original size screenshot, so Agent's coordinates are already client coordinates
        client_x, client_y = x, y
        
        # #region agent log H7
        _win_dbg_log("H7", "window_click:coords", "Using direct coordinates (no scaling)", {"client_x": client_x, "client_y": client_y, "original_x": x, "original_y": y})
        # #endregion
        
        # 4. Windows 11 rounded corners compensation
        if self.win11_compat.is_windows_11():
            client_x, client_y = self.win11_compat.adjust_coordinates_for_rounded_corners(
                client_x, client_y, hwnd
            )
        
        # #region agent log H7
        _win_dbg_log("H7", "window_click:pre_click", "About to execute click", {"client_x": client_x, "client_y": client_y})
        # #endregion
        
        # 5. Execute click (auto fallback)
        result = await self.input_controller.click(hwnd, client_x, client_y, button)
        
        # #region agent log H7
        _win_dbg_log("H7", "window_click:post_click", "Click executed", {"success": result.success, "method": result.method_used.value if result.method_used else None})
        # #endregion
        
        # 6. Wait UI Response
        await asyncio.sleep(self.POST_ACTION_DELAY_MS / 1000)
        
        # 7. Screenshot verification
        screenshot_b64 = None
        if capture_screenshot:
            # #region agent log H7
            _win_dbg_log("H7", "window_click:pre_screenshot", "About to capture screenshot", {})
            # #endregion
            screenshot_b64 = await self._capture_window(hwnd)
            # #region agent log H7
            _win_dbg_log("H7", "window_click:post_screenshot", "Screenshot captured", {"has_image": screenshot_b64 is not None})
            # #endregion
        
        # 8. Build return result
        output = f"Click ({x}, {y}) -> client area ({client_x}, {client_y})"
        if result.fallback_count > 0:
            output += f" [Usage Fallback: {result.method_used.value}]"
        
        # #region agent log H7
        _win_dbg_log("H7", "window_click:end", "window_click completed", {"success": result.success})
        # #endregion
        
        # Enhanced error diagnostics for debugging
        error_msg = None
        if not result.success:
            error_msg = f"{result.error or 'Unknown error'} | Debug: orig=({x},{y}) client=({client_x},{client_y}) hwnd={hwnd} method={result.method_used.value if result.method_used else 'none'} fallbacks={result.fallback_count}"

        return WindowToolResult(
            success=result.success,
            output=output,
            base64_image=screenshot_b64,
            error=error_msg,
            input_method=result.method_used,
            fallback_count=result.fallback_count
        )
    
    async def window_double_click(
        self, 
        x: int, 
        y: int, 
        hwnd: int,
        capture_screenshot: bool = True
    ) -> WindowToolResult:
        """Double click on window"""
        # Check
        operable, reason = self.state_checker.is_operable(hwnd)
        if not operable:
            return WindowToolResult(success=False, output="", error=f"Window not operable: {reason}")
        
        # Coordinate conversion
        client_x, client_y = scale_coordinates("api", x, y, hwnd)
        
        # Execute double click
        result = await self.input_controller.double_click(hwnd, client_x, client_y)
        
        # Wait
        await asyncio.sleep(self.POST_ACTION_DELAY_MS / 1000)
        
        # Capture screenshot
        screenshot_b64 = None
        if capture_screenshot:
            screenshot_b64 = await self._capture_window(hwnd)
        
        return WindowToolResult(
            success=result.success,
            output=f"Double click ({x}, {y}) -> client area ({client_x}, {client_y})",
            base64_image=screenshot_b64,
            error=result.error,
            input_method=result.method_used,
            fallback_count=result.fallback_count
        )
    
    async def window_type(
        self, 
        text: str, 
        hwnd: int,
        capture_screenshot: bool = True
    ) -> WindowToolResult:
        """Type text in window"""
        # #region agent log F1
        _win_dbg_log("F1", "window_type:start", "window_type called", {"hwnd": hwnd, "text": text[:100] if text else "", "text_len": len(text) if text else 0})
        # #endregion
        
        # Check
        operable, reason = self.state_checker.is_operable(hwnd)
        if not operable:
            # #region agent log F1
            _win_dbg_log("F1", "window_type:not_operable", "Window not operable", {"reason": reason})
            # #endregion
            return WindowToolResult(success=False, output="", error=f"Window not operable: {reason}")
        
        # Execute input
        result = await self.input_controller.type_text(hwnd, text)
        
        # #region agent log F1
        _win_dbg_log("F1", "window_type:result", "Input result", {"success": result.success, "method": result.method_used.value if result.method_used else None, "error": result.error})
        
        # Wait
        await asyncio.sleep(self.POST_ACTION_DELAY_MS / 1000)
        
        # Capture screenshot
        screenshot_b64 = None
        if capture_screenshot:
            screenshot_b64 = await self._capture_window(hwnd)
        
        return WindowToolResult(
            success=result.success,
            output=f"Input: {text[:50]}{'...' if len(text) > 50 else ''}",
            base64_image=screenshot_b64,
            error=result.error,
            input_method=result.method_used
        )
    
    async def window_drag(
        self, 
        from_x: int, from_y: int,
        to_x: int, to_y: int,
        hwnd: int,
        capture_screenshot: bool = True
    ) -> WindowToolResult:
        """Drag in window"""
        # Check
        operable, reason = self.state_checker.is_operable(hwnd)
        if not operable:
            return WindowToolResult(success=False, output="", error=f"Window not operable: {reason}")
        
        # Coordinate conversion
        from_client_x, from_client_y = scale_coordinates("api", from_x, from_y, hwnd)
        to_client_x, to_client_y = scale_coordinates("api", to_x, to_y, hwnd)
        
        # Execute drag
        result = await self.input_controller.drag(
            hwnd, from_client_x, from_client_y, to_client_x, to_client_y
        )
        
        # Wait
        await asyncio.sleep(self.POST_ACTION_DELAY_MS / 1000)
        
        # Capture screenshot
        screenshot_b64 = None
        if capture_screenshot:
            screenshot_b64 = await self._capture_window(hwnd)
        
        return WindowToolResult(
            success=result.success,
            output=f"Drag ({from_x},{from_y}) -> ({to_x},{to_y})",
            base64_image=screenshot_b64,
            error=result.error,
            input_method=result.method_used
        )
    
    async def window_screenshot(self, hwnd: int) -> WindowToolResult:
        """Capture window screenshot"""
        # Check if window exists
        state = self.state_checker.get_window_state(hwnd)
        if not state.exists:
            return WindowToolResult(
                success=False,
                output="",
                error="Window does not exist"
            )
        
        # Capture screenshot
        screenshot_b64 = await self._capture_window(hwnd)
        
        if screenshot_b64:
            return WindowToolResult(
                success=True,
                output="Screenshot captured successfully",
                base64_image=screenshot_b64
            )
        else:
            return WindowToolResult(
                success=False,
                output="",
                error="Screenshot capture failed"
            )
    
    async def window_scroll(
        self,
        hwnd: int,
        direction: str,
        amount: int = 3,
        capture_screenshot: bool = True
    ) -> WindowToolResult:
        """
        Scroll window
        
        Args:
            hwnd: Window handle
            direction: "up", "down", "left", "right"
            amount: Number of lines to scroll
            capture_screenshot: Whether to capture screenshot
        """
        # Check
        operable, reason = self.state_checker.is_operable(hwnd)
        if not operable:
            return WindowToolResult(success=False, output="", error=f"Window not operable: {reason}")
        
        # Execute scroll
        result = await self.input_controller.scroll(hwnd, direction, amount)
        
        # Wait
        await asyncio.sleep(self.POST_ACTION_DELAY_MS / 1000)
        
        # Capture screenshot
        screenshot_b64 = None
        if capture_screenshot:
            screenshot_b64 = await self._capture_window(hwnd)
        
        return WindowToolResult(
            success=result.success,
            output=f"Scroll {direction} {amount} lines",
            base64_image=screenshot_b64,
            error=result.error,
            input_method=result.method_used
        )
    
    async def window_hotkey(
        self,
        hwnd: int,
        keys: str,
        capture_screenshot: bool = True
    ) -> WindowToolResult:
        """
        Send hotkey
        
        Args:
            hwnd: Window handle
            keys: Hotkey string, e.g. "ctrl+c", "alt+tab"
            capture_screenshot: Whether to capture screenshot
        """
        # Check
        operable, reason = self.state_checker.is_operable(hwnd)
        if not operable:
            return WindowToolResult(success=False, output="", error=f"Window not operable: {reason}")
        
        # Execute hotkey
        result = await self.input_controller.hotkey(hwnd, keys)
        
        # Wait
        await asyncio.sleep(self.POST_ACTION_DELAY_MS / 1000)
        
        # Capture screenshot
        screenshot_b64 = None
        if capture_screenshot:
            screenshot_b64 = await self._capture_window(hwnd)
        
        return WindowToolResult(
            success=result.success,
            output=f"Hotkey {keys}",
            base64_image=screenshot_b64,
            error=result.error,
            input_method=result.method_used
        )
    
    async def window_key_press(
        self,
        hwnd: int,
        key: str,
        capture_screenshot: bool = False
    ) -> WindowToolResult:
        """
        Press a single key
        
        Args:
            hwnd: Window handle
            key: Key name, e.g. "enter", "tab", "escape"
            capture_screenshot: Whether to capture screenshot
        """
        # Check
        operable, reason = self.state_checker.is_operable(hwnd)
        if not operable:
            return WindowToolResult(success=False, output="", error=f"Window not operable: {reason}")
        
        # Execute key press
        result = await self.input_controller.key_press_by_name(hwnd, key)
        
        # Brief wait
        await asyncio.sleep(0.1)
        
        # Capture screenshot
        screenshot_b64 = None
        if capture_screenshot:
            screenshot_b64 = await self._capture_window(hwnd)
        
        return WindowToolResult(
            success=result.success,
            output=f"Key press {key}",
            base64_image=screenshot_b64,
            error=result.error,
            input_method=result.method_used
        )
    
    async def _capture_window(self, hwnd: int) -> Optional[str]:
        """
        Capture window and return base64 encoded image
        
        Uses PrintWindow API to capture specific window (works even when occluded)
        Scales to 1280x800
        """
        try:
            from PIL import Image
            import ctypes
            from ctypes import wintypes
            
            # First try PrintWindow (not affected by occlusion)
            screenshot = await self._capture_with_printwindow(hwnd)
            
            if screenshot is None:
                # Fallback: Use ImageGrab (simple but affected by occlusion)
                screenshot = await self._capture_with_imagegrab(hwnd)
            
            if screenshot is None:
                return None
            
            # Scale to target size
            target_size = (self.coord_transformer.TARGET_WIDTH,
                          self.coord_transformer.TARGET_HEIGHT)
            screenshot = screenshot.resize(target_size, Image.Resampling.LANCZOS)

            # Convert to base64 (use JPEG compression to reduce token consumption)
            # PNG lossless compression is too large for big images, may exceed token limit
            buffer = BytesIO()
            # Convert to RGB (JPEG doesn't support alpha channel)
            if screenshot.mode in ('RGBA', 'LA', 'P'):
                screenshot = screenshot.convert('RGB')
            screenshot.save(buffer, format='JPEG', quality=60, optimize=True)
            b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return b64
            
        except ImportError:
            logger.error("PIL not available for screenshot")
            return None
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    async def _capture_with_printwindow(self, hwnd: int) -> Optional["Image.Image"]:
        """
        Use PrintWindow API to capture window
        
        Pros: Can capture window even when occluded
        Cons: Some apps may not support it (e.g. some DirectX apps)
        """
        try:
            from PIL import Image
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)
            
            # Get window client area size
            rect = wintypes.RECT()
            user32.GetClientRect(hwnd, ctypes.byref(rect))
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            
            if width <= 0 or height <= 0:
                logger.warning(f"Invalid window size: {width}x{height}")
                return None
            
            # Create compatible DC and bitmap
            hwnd_dc = user32.GetDC(hwnd)
            if not hwnd_dc:
                return None
            
            try:
                mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
                if not mem_dc:
                    return None
                
                try:
                    bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, width, height)
                    if not bitmap:
                        return None
                    
                    try:
                        old_bitmap = gdi32.SelectObject(mem_dc, bitmap)
                        
                        # PrintWindow - PW_RENDERFULLCONTENT = 2 (Windows 8.1+)
                        # This flag can capture DirectComposition content
                        PW_RENDERFULLCONTENT = 2
                        result = user32.PrintWindow(hwnd, mem_dc, PW_RENDERFULLCONTENT)
                        
                        if not result:
                            # Fallback: Try without flag
                            result = user32.PrintWindow(hwnd, mem_dc, 0)
                        
                        if not result:
                            logger.debug("PrintWindow failed")
                            return None
                        
                        # Prepare BITMAPINFO
                        class BITMAPINFOHEADER(ctypes.Structure):
                            _fields_ = [
                                ('biSize', wintypes.DWORD),
                                ('biWidth', wintypes.LONG),
                                ('biHeight', wintypes.LONG),
                                ('biPlanes', wintypes.WORD),
                                ('biBitCount', wintypes.WORD),
                                ('biCompression', wintypes.DWORD),
                                ('biSizeImage', wintypes.DWORD),
                                ('biXPelsPerMeter', wintypes.LONG),
                                ('biYPelsPerMeter', wintypes.LONG),
                                ('biClrUsed', wintypes.DWORD),
                                ('biClrImportant', wintypes.DWORD),
                            ]
                        
                        bi = BITMAPINFOHEADER()
                        bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
                        bi.biWidth = width
                        bi.biHeight = -height  # Negative = top-down
                        bi.biPlanes = 1
                        bi.biBitCount = 32
                        bi.biCompression = 0  # BI_RGB
                        
                        # Get bitmap data
                        buffer_size = width * height * 4
                        buffer = ctypes.create_string_buffer(buffer_size)
                        
                        gdi32.GetDIBits(
                            mem_dc, bitmap, 0, height,
                            buffer, ctypes.byref(bi), 0  # DIB_RGB_COLORS
                        )
                        
                        # Convert to PIL Image (BGRA -> RGBA)
                        img = Image.frombuffer('RGBA', (width, height), buffer, 'raw', 'BGRA', 0, 1)
                        
                        # Convert to RGB (remove alpha)
                        img = img.convert('RGB')
                        
                        return img
                        
                    finally:
                        gdi32.SelectObject(mem_dc, old_bitmap)
                        gdi32.DeleteObject(bitmap)
                finally:
                    gdi32.DeleteDC(mem_dc)
            finally:
                user32.ReleaseDC(hwnd, hwnd_dc)
                
        except Exception as e:
            logger.debug(f"PrintWindow capture failed: {e}")
            return None
    
    async def _capture_with_imagegrab(self, hwnd: int) -> Optional["Image.Image"]:
        """
        Use ImageGrab to capture window (fallback)
        
        Note: If window is occluded, will capture occluding window's content
        """
        try:
            from PIL import ImageGrab
            
            # Get window actual visible area (Windows 11 compatible)
            rect = self.win11_compat.get_actual_window_rect(hwnd)
            
            # Use PIL to capture screenshot
            screenshot = ImageGrab.grab(bbox=rect)
            return screenshot
            
        except Exception as e:
            logger.debug(f"ImageGrab capture failed: {e}")
            return None
    
    def get_window_info(self, hwnd: int) -> dict:
        """Get window info"""
        state = self.state_checker.get_window_state(hwnd)
        coords = self.coord_transformer.get_window_coordinates(hwnd)
        dpi_scale = self.dpi_handler.get_window_dpi(hwnd)
        
        return {
            "hwnd": hwnd,
            "title": self.hwnd_manager.get_window_title(hwnd),
            "state": {
                "exists": state.exists,
                "visible": state.visible,
                "minimized": state.minimized,
                "maximized": state.maximized,
                "foreground": state.foreground,
                "enabled": state.enabled,
                "hung": state.hung,
            },
            "coordinates": {
                "window_rect": coords.window_rect,
                "client_rect": coords.client_rect,
                "client_size": (coords.client_width, coords.client_height),
            },
            "dpi_scale": dpi_scale,
            "is_windows_11": self.win11_compat.is_windows_11(),
        }


def register_window_tools(registry):
    """RegisterWindowTool到 Registry"""
    from .base import ToolCategory
    from typing import Dict, Any
    
    # CreateSingleton
    window_tools = WindowTools()
    
    @registry.action(
        description="""点击WindowMedium的SpecifyPosition。

Argument:
- x: 截GraphUp的 X Coordinate (0-1280)
- y: 截GraphUp的 Y Coordinate (0-800)
- hwnd: TargetWindow句柄 (从 Hook UpDown文Get，见提示OnHead的 CONNECTED TARGET)
- button: 鼠标按键 ("left", "right", "middle")

功能:
- Auto将截GraphCoordinateConvert为Window客户区Coordinate
- Usage PostMessage 非侵入式点击 (不抢焦点)
- AutoHandle DPI 缩放和 Windows 11 圆角
- 点击AfterAuto截GraphVerify

Important: 如果User已ConnectWindow，请Usage提示OnHeadDisplay的 HWND，不要调用 list_windows。

Return: Package含截Graph的结构化数据，用于Verify点击Effect""",
        category=ToolCategory.LOCAL,
    )
    async def window_click(
        x: Optional[int] = None,
        y: Optional[int] = None,
        hwnd: Optional[int] = None,
        button: str = "left",
        # Common aliases AI might use
        title: Optional[str] = None,
        window_title: Optional[str] = None,
        window_name: Optional[str] = None,
        handle: Optional[int] = None,
        window_handle: Optional[int] = None,
        coord_x: Optional[int] = None,
        coord_y: Optional[int] = None,
        pos_x: Optional[int] = None,
        pos_y: Optional[int] = None,
    ) -> Dict[str, Any]:
        """点击Window - Return结构化数据含截Graph"""
        # Support multiple parameter names for hwnd
        actual_hwnd = hwnd or handle or window_handle
        actual_x = x if x is not None else coord_x if coord_x is not None else pos_x
        actual_y = y if y is not None else coord_y if coord_y is not None else pos_y

        # If title provided instead of hwnd, try to find the window
        actual_title = title or window_title or window_name
        if actual_title and not actual_hwnd:
            try:
                import ctypes
                user32 = ctypes.windll.user32
                # Find window by title
                found_hwnd = user32.FindWindowW(None, actual_title)
                if not found_hwnd:
                    # Try partial match
                    from pywinauto import Desktop
                    desktop = Desktop(backend="uia")
                    for win in desktop.windows():
                        if actual_title.lower() in win.window_text().lower():
                            found_hwnd = win.handle
                            break
                if found_hwnd:
                    actual_hwnd = found_hwnd
                else:
                    return {
                        "type": "window_action",
                        "action": "click",
                        "success": False,
                        "output": "",
                        "error": f"Window with title '{actual_title}' not found",
                        "image_base64": None,
                        "input_method": None,
                        "fallback_count": 0,
                    }
            except Exception as e:
                return {
                    "type": "window_action",
                    "action": "click",
                    "success": False,
                    "output": "",
                    "error": f"Error finding window by title: {e}",
                    "image_base64": None,
                    "input_method": None,
                    "fallback_count": 0,
                }

        if actual_hwnd is None:
            return {
                "type": "window_action",
                "action": "click",
                "success": False,
                "output": "",
                "error": "Must provide hwnd (or handle/window_handle) or title (window_title/window_name)",
                "image_base64": None,
                "input_method": None,
                "fallback_count": 0,
            }

        if actual_x is None or actual_y is None:
            return {
                "type": "window_action",
                "action": "click",
                "success": False,
                "output": "",
                "error": "Must provide x and y coordinates",
                "image_base64": None,
                "input_method": None,
                "fallback_count": 0,
            }

        result = await window_tools.window_click(actual_x, actual_y, actual_hwnd, button)
        return {
            "type": "window_action",
            "action": "click",
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "image_base64": result.base64_image,
            "input_method": result.input_method.value if result.input_method else None,
            "fallback_count": result.fallback_count,
        }
    
    @registry.action(
        description="""双击WindowMedium的SpecifyPosition。

Argument:
- x: 截GraphUp的 X Coordinate (0-1280)
- y: 截GraphUp的 Y Coordinate (0-800)
- hwnd: TargetWindow句柄

Return: Package含截Graph的结构化数据""",
        category=ToolCategory.LOCAL,
    )
    async def window_double_click(
        x: int, 
        y: int, 
        hwnd: int
    ) -> Dict[str, Any]:
        """双击Window - Return结构化数据含截Graph"""
        result = await window_tools.window_double_click(x, y, hwnd)
        return {
            "type": "window_action",
            "action": "double_click",
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "image_base64": result.base64_image,
            "input_method": result.input_method.value if result.input_method else None,
            "fallback_count": result.fallback_count,
        }
    
    @registry.action(
        description="""在WindowMediumInput文字。

Argument:
- text: 要Input的文字
- hwnd: TargetWindow句柄

功能:
- ASCII CharacterUsage PostMessage WM_CHAR
- Medium文等非 ASCII CharacterUsage剪贴板粘贴

Return: Package含截Graph的结构化数据""",
        category=ToolCategory.LOCAL,
    )
    async def window_type(
        text: str, 
        hwnd: int
    ) -> Dict[str, Any]:
        """Input文字 - Return结构化数据含截Graph"""
        result = await window_tools.window_type(text, hwnd)
        return {
            "type": "window_action",
            "action": "type",
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "image_base64": result.base64_image,
            "input_method": result.input_method.value if result.input_method else None,
        }
    
    @registry.action(
        description="""在WindowMedium拖拽。

Argument:
- from_x, from_y: 起始Position (截GraphCoordinate)
- to_x, to_y: TerminatePosition (截GraphCoordinate)
- hwnd: TargetWindow句柄

Return: Package含截Graph的结构化数据""",
        category=ToolCategory.LOCAL,
    )
    async def window_drag(
        from_x: int, from_y: int,
        to_x: int, to_y: int,
        hwnd: int
    ) -> Dict[str, Any]:
        """拖拽 - Return结构化数据含截Graph"""
        result = await window_tools.window_drag(from_x, from_y, to_x, to_y, hwnd)
        return {
            "type": "window_action",
            "action": "drag",
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "image_base64": result.base64_image,
            "input_method": result.input_method.value if result.input_method else None,
        }
    
    @registry.action(
        description="""截取Window截Graph。

Argument:
- hwnd: TargetWindow句柄 (从 Hook UpDown文Get，见提示OnHead的 CONNECTED TARGET)

Return: 1280x800 的Window截Graph (base64 编码)

Important: 如果User已ConnectWindow，请Usage提示OnHeadDisplay的 HWND，不要调用 list_windows 或 find_window。""",
        category=ToolCategory.LOCAL,
    )
    async def window_screenshot(hwnd: int) -> Dict[str, Any]:
        """截取Window截Graph - Return结构化数据含截Graph"""
        result = await window_tools.window_screenshot(hwnd)
        window_info = window_tools.get_window_info(hwnd)
        try:
            _win_dbg_log(
                hypothesis_id="H5",
                location="window_tools:window_screenshot",
                message="Captured window screenshot",
                data={
                    "hwnd": hwnd,
                    "success": result.success,
                    "title": window_info.get("title", ""),
                    "size": window_info.get("coordinates", {}).get("client_size", [0, 0]),
                },
            )
        except Exception:
            pass
        return {
            "type": "window_screenshot",
            "success": result.success,
            "image_base64": result.base64_image,
            "error": result.error,
            "window_title": window_info.get("title", ""),
            "window_size": window_info.get("coordinates", {}).get("client_size", [0, 0]),
        }
    
    @registry.action(
        description="""GetWindowInfo。

Argument:
- hwnd: TargetWindow句柄

Return: Windowtitle、State、尺寸、DPI 等Info""",
        category=ToolCategory.LOCAL,
    )
    async def get_window_info(hwnd: int) -> Dict[str, Any]:
        """GetWindowInfo"""
        info = window_tools.get_window_info(hwnd)
        return {
            "type": "window_info",
            **info
        }
    
    logger.info("[WindowTools] All window tools registered")


# Export
__all__ = [
    'WindowToolResult',
    'WindowTools',
    'register_window_tools',
    'WindowLostError',
]
