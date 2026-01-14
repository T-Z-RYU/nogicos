# -*- coding: utf-8 -*-
"""
Desktop Hook - 桌面Window感知

感知当BeforeActiveWindow和WindowList
提供通用的Window发现能力（用于 App Connector）
"""

import asyncio
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .base_hook import BaseHook, HookConfig
from ..store import HookType, DesktopContext

logger = logging.getLogger(__name__)

# Windows API
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False

# Icon extraction support
try:
    from PIL import Image
    import io
    import base64
    ICON_EXTRACTION_AVAILABLE = WINDOWS_AVAILABLE
except ImportError:
    ICON_EXTRACTION_AVAILABLE = False


@dataclass
class WindowInfo:
    """Window information (for window selector)"""
    hwnd: int                          # Window handle
    title: str                         # Window title
    app_name: str                      # Application name (e.g. chrome.exe)
    app_display_name: str = ""         # Display name (e.g. Google Chrome)
    icon_base64: str = ""              # Icon base64 data (data:image/png;base64,...)
    is_browser: bool = False           # Whether it's a browser
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hwnd": self.hwnd,
            "title": self.title,
            "app_name": self.app_name,
            "app_display_name": self.app_display_name or self.app_name,
            "icon_base64": self.icon_base64,
            "is_browser": self.is_browser,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }


# ============================================================================
# Icon Extraction - Extract app icons from window/process
# ============================================================================

# Cache for extracted icons (app_name -> base64)
_icon_cache: Dict[str, str] = {}


def _extract_icon_from_hwnd(hwnd: int, process_path: str = "") -> str:
    """
    Extract app icon from window handle or process path
    
    Args:
        hwnd: Window handle
        process_path: Executable file path (optional)
    
    Returns:
        Base64 encoded PNG icon data (data:image/png;base64,...) or empty string
    """
    if not ICON_EXTRACTION_AVAILABLE:
        return ""
    
    try:
        user32 = ctypes.windll.user32
        shell32 = ctypes.windll.shell32
        
        # Define constants
        ICON_SMALL = 0
        ICON_BIG = 1
        WM_GETICON = 0x007F
        GCLP_HICON = -14
        GCLP_HICONSM = -34
        
        hicon = None
        
        # Method 1: Get icon from window message
        hicon = user32.SendMessageW(hwnd, WM_GETICON, ICON_BIG, 0)
        if not hicon:
            hicon = user32.SendMessageW(hwnd, WM_GETICON, ICON_SMALL, 0)
        
        # Method 2: Get icon from window class
        if not hicon:
            hicon = user32.GetClassLongPtrW(hwnd, GCLP_HICON)
        if not hicon:
            hicon = user32.GetClassLongPtrW(hwnd, GCLP_HICONSM)
        
        # Method 3: Extract from executable file
        if not hicon and process_path:
            # ExtractIconExW returns icon count
            large_icon = (ctypes.c_void_p * 1)()
            small_icon = (ctypes.c_void_p * 1)()
            count = shell32.ExtractIconExW(process_path, 0, large_icon, small_icon, 1)
            if count > 0 and large_icon[0]:
                hicon = large_icon[0]
            elif count > 0 and small_icon[0]:
                hicon = small_icon[0]
        
        if not hicon:
            return ""
        
        # Convert icon to bitmap
        return _hicon_to_base64(hicon)
        
    except Exception as e:
        logger.debug(f"[IconExtract] Failed to extract icon for hwnd {hwnd}: {e}")
        return ""


def _hicon_to_base64(hicon: int) -> str:
    """Convert HICON to base64 PNG"""
    if not ICON_EXTRACTION_AVAILABLE:
        return ""
    
    try:
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        
        # Get icon info
        class ICONINFO(ctypes.Structure):
            _fields_ = [
                ("fIcon", wintypes.BOOL),
                ("xHotspot", wintypes.DWORD),
                ("yHotspot", wintypes.DWORD),
                ("hbmMask", wintypes.HBITMAP),
                ("hbmColor", wintypes.HBITMAP),
            ]
        
        icon_info = ICONINFO()
        if not user32.GetIconInfo(hicon, ctypes.byref(icon_info)):
            return ""
        
        # Get bitmap info
        class BITMAP(ctypes.Structure):
            _fields_ = [
                ("bmType", wintypes.LONG),
                ("bmWidth", wintypes.LONG),
                ("bmHeight", wintypes.LONG),
                ("bmWidthBytes", wintypes.LONG),
                ("bmPlanes", wintypes.WORD),
                ("bmBitsPixel", wintypes.WORD),
                ("bmBits", ctypes.c_void_p),
            ]
        
        bmp = BITMAP()
        hbm = icon_info.hbmColor or icon_info.hbmMask
        if not hbm:
            return ""
        
        gdi32.GetObjectW(hbm, ctypes.sizeof(BITMAP), ctypes.byref(bmp))
        
        width = bmp.bmWidth
        height = bmp.bmHeight
        
        if width <= 0 or height <= 0:
            return ""
        
        # Create DC and compatible bitmap
        hdc_screen = user32.GetDC(0)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        
        # BITMAPINFOHEADER
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]
        
        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = width
        bmi.biHeight = -height  # Top-down DIB
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0  # BI_RGB
        
        # Create DIB section
        bits = ctypes.c_void_p()
        hbm_dib = gdi32.CreateDIBSection(
            hdc_mem, ctypes.byref(bmi), 0, ctypes.byref(bits), None, 0
        )
        
        if not hbm_dib:
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(0, hdc_screen)
            return ""
        
        old_bm = gdi32.SelectObject(hdc_mem, hbm_dib)
        
        # Draw icon
        user32.DrawIconEx(hdc_mem, 0, 0, hicon, width, height, 0, 0, 3)  # DI_NORMAL
        
        # Read pixel data
        buffer_size = width * height * 4
        pixel_data = (ctypes.c_ubyte * buffer_size)()
        ctypes.memmove(pixel_data, bits, buffer_size)
        
        # Convert to PIL Image (BGRA -> RGBA)
        img = Image.frombuffer('RGBA', (width, height), bytes(pixel_data), 'raw', 'BGRA', 0, 1)
        
        # Clean up resources
        gdi32.SelectObject(hdc_mem, old_bm)
        gdi32.DeleteObject(hbm_dib)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc_screen)
        
        # Clean up icon resources
        if icon_info.hbmColor:
            gdi32.DeleteObject(icon_info.hbmColor)
        if icon_info.hbmMask:
            gdi32.DeleteObject(icon_info.hbmMask)
        
        # Resize to 64x64 (uniform size)
        img = img.resize((64, 64), Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{b64}"
        
    except Exception as e:
        logger.debug(f"[IconExtract] Failed to convert HICON to base64: {e}")
        return ""


def _get_process_path(hwnd: int) -> str:
    """GetWindow对应的可ExecuteFilePath"""
    if not WINDOWS_AVAILABLE:
        return ""
    
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        
        # Get process ID
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        if not pid.value:
            return ""
        
        # Open process
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        hprocess = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        
        if not hprocess:
            return ""
        
        try:
            # Get executable file path
            path_buffer = ctypes.create_unicode_buffer(512)
            size = wintypes.DWORD(512)
            
            # Use QueryFullProcessImageNameW
            kernel32.QueryFullProcessImageNameW(hprocess, 0, path_buffer, ctypes.byref(size))
            
            return path_buffer.value
        finally:
            kernel32.CloseHandle(hprocess)
            
    except Exception as e:
        logger.debug(f"[IconExtract] Failed to get process path for hwnd {hwnd}: {e}")
        return ""


# Browser process name mapping
BROWSER_PROCESSES = {
    "chrome.exe": "Google Chrome",
    "firefox.exe": "Mozilla Firefox",
    "msedge.exe": "Microsoft Edge",
    "brave.exe": "Brave",
    "opera.exe": "Opera",
    "arc.exe": "Arc",
}

# Common app process name mapping
APP_DISPLAY_NAMES = {
    **BROWSER_PROCESSES,
    "code.exe": "VS Code",
    "cursor.exe": "Cursor",
    "figma.exe": "Figma",
    "slack.exe": "Slack",
    "discord.exe": "Discord",
    "notion.exe": "Notion",
    "obsidian.exe": "Obsidian",
    "spotify.exe": "Spotify",
    "explorer.exe": "File Explorer",
    "wps.exe": "WPS Office",
    "excel.exe": "Excel",
    "word.exe": "Word",
    "powerpnt.exe": "PowerPoint",
}


class DesktopHook(BaseHook):
    """
    桌面 Hook
    
    支持两种模式：
    1. 无Target：感知当BeforeActiveWindow（焦点Window）
    2. 有Target HWND：Lock定Monitor特定Window
    """
    
    def __init__(
        self,
        hook_id: str = "desktop",
        config: Optional[HookConfig] = None,
    ):
        super().__init__(hook_id, HookType.DESKTOP, config)
        
        self._last_context: Optional[DesktopContext] = None
        self._target_hwnd: Optional[int] = None  # Target window HWND (locked if specified)
    
    async def _connect(self, target: Optional[str] = None) -> bool:
        """
        Connect到TargetWindow
        
        Args:
            target: TargetWindow的 HWND（Character串形式），None 则Monitor当Before活动Window
        """
        if target:
            try:
                self._target_hwnd = int(target)
                logger.info(f"[DesktopHook] Locked to window HWND: {self._target_hwnd}")
            except ValueError:
                logger.error(f"[DesktopHook] Invalid HWND: {target}")
                return False
        else:
            self._target_hwnd = None
            logger.info("[DesktopHook] Monitoring active (foreground) window")
        return True
    
    async def _disconnect(self) -> bool:
        """DisconnectConnect"""
        self._last_context = None
        self._target_hwnd = None
        return True
    
    async def capture(self) -> Optional[DesktopContext]:
        """
        捕获桌面UpDown文
        
        Returns:
            DesktopContext 或 None
        """
        try:
            if sys.platform == "win32" and WINDOWS_AVAILABLE:
                return await self._capture_windows()
            else:
                logger.warning(f"[DesktopHook] Platform {sys.platform} not fully supported")
                return None
                
        except Exception as e:
            logger.error(f"[DesktopHook] Capture failed: {e}")
            return self._last_context
    
    async def _capture_windows(self) -> Optional[DesktopContext]:
        """Windows Platform捕获"""
        try:
            user32 = ctypes.windll.user32
            
            # Decide which window to monitor
            if self._target_hwnd:
                # Lock mode: use specified HWND
                hwnd = self._target_hwnd
                # Verify window still exists
                if not user32.IsWindow(hwnd):
                    logger.warning(f"[DesktopHook] Target window {hwnd} no longer exists")
                    hwnd = 0
            else:
                # Active window mode: get foreground window
                hwnd = user32.GetForegroundWindow()

            # Early return if no valid hwnd
            if hwnd == 0:
                return self._last_context

            active_app = ""
            active_window = ""

            if hwnd:
                # Get window title
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    active_window = buffer.value
                
                # Get process name
                active_app = self._get_process_name_windows(hwnd)
            
            # Get window list (only in non-lock mode, not needed in lock mode)
            window_list = [] if self._target_hwnd else await self._get_window_list_windows()
            
            context = DesktopContext(
                hwnd=hwnd,  # Add hwnd to context
                active_app=active_app,
                active_window=active_window,
                window_list=window_list,
                last_updated=datetime.now().isoformat(),
            )
            
            self._last_context = context
            return context
            
        except Exception as e:
            logger.error(f"[DesktopHook] Windows capture failed: {e}")
            return self._last_context
    
    def _get_process_name_windows(self, hwnd: int) -> str:
        """GetWindow的Process名"""
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            psapi = ctypes.windll.psapi
            
            # Get process ID
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # Open process
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010
            
            process = kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                False,
                pid.value
            )
            
            if process:
                try:
                    # Get process name
                    buffer = ctypes.create_unicode_buffer(260)
                    psapi.GetModuleBaseNameW(process, None, buffer, 260)
                    return buffer.value
                finally:
                    kernel32.CloseHandle(process)
            
            return ""
            
        except Exception as e:
            logger.debug(f"[DesktopHook] Get process name failed: {e}")
            return ""
    
    async def _get_window_list_windows(self) -> List[Dict[str, str]]:
        """GetVisibleWindowList"""
        try:
            user32 = ctypes.windll.user32
            windows = []
            
            def enum_callback(hwnd, _):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buffer, length + 1)
                        title = buffer.value
                        
                        # Filter system windows
                        if title and not self._is_system_window(title):
                            app = self._get_process_name_windows(hwnd)
                            windows.append({
                                "app": app,
                                "title": title,
                            })
                return True
            
            # [Fix #18 + Segfault fix]
            # Key: Must keep callback instance reference, otherwise GC causes Segfault
            if not hasattr(DesktopHook, '_WNDENUMPROC'):
                DesktopHook._WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
            callback_instance = DesktopHook._WNDENUMPROC(enum_callback)
            user32.EnumWindows(callback_instance, 0)

            return windows[:20]  # Return max 20 windows
            
        except Exception as e:
            logger.error(f"[DesktopHook] Get window list failed: {e}")
            return []
    
    def _is_system_window(self, title: str) -> bool:
        """JudgeYesNoYesSystemWindow（应该Ignore）"""
        system_titles = [
            "Program Manager",
            "Windows Input Experience",
            "Microsoft Text Input Application",
            "Settings",
            "Calculator",
        ]
        
        # Exact match
        if title in system_titles:
            return True
        
        # Empty or very short title
        if len(title) < 2:
            return True
        
        return False


# ============================================================================
# Standalone function: Get all windows (for direct API calls)
# ============================================================================

def get_all_windows() -> List[WindowInfo]:
    """
    Get所有VisibleWindow的详细Info

    供 /api/windows 端点调用，用于WindowSelect器 UI

    Returns:
        List[WindowInfo]: WindowInfoList，按最近ActiveSort
    """
    if not WINDOWS_AVAILABLE:
        logger.warning("[DesktopHook] Windows API not available")
        return []
    
    try:
        user32 = ctypes.windll.user32
        windows: List[WindowInfo] = []
        
        def enum_callback(hwnd, _):
            # Only process visible windows
            if not user32.IsWindowVisible(hwnd):
                return True
            
            # Get window title
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True
            
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value
            
            # Get process name (get first, for filtering)
            app_name = _get_process_name_static(hwnd)
            if not app_name:
                return True
            
            # Filter system windows and our own app
            if _is_system_window_static(title, app_name):
                return True
            
            # Get window position
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            # Filter too small windows (might be hidden windows)
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            if width < 100 or height < 100:
                return True
            
            # Check if it's a browser
            app_lower = app_name.lower()
            is_browser = app_lower in BROWSER_PROCESSES
            
            # Get display name
            app_display_name = APP_DISPLAY_NAMES.get(app_lower, app_name.replace(".exe", "").title())
            
            # Extract icon (use cache to avoid repeated extraction)
            icon_base64 = ""
            if ICON_EXTRACTION_AVAILABLE:
                cache_key = app_lower
                if cache_key in _icon_cache:
                    icon_base64 = _icon_cache[cache_key]
                else:
                    process_path = _get_process_path(hwnd)
                    try:
                        icon_base64 = _extract_icon_from_hwnd(hwnd, process_path)
                    except Exception as e:
                        logger.debug(f"[IconExtract] Failed for {app_name}: {e}")
                    if icon_base64:
                        _icon_cache[cache_key] = icon_base64
            
            windows.append(WindowInfo(
                hwnd=hwnd,
                title=title,
                app_name=app_name,
                app_display_name=app_display_name,
                icon_base64=icon_base64,
                is_browser=is_browser,
                x=rect.left,
                y=rect.top,
                width=width,
                height=height,
            ))
            
            return True
        
        # [Fix #18 + Segfault fix]
        # Key: Must keep callback instance reference, otherwise GC causes Segfault
        global _WNDENUMPROC_CACHED
        if '_WNDENUMPROC_CACHED' not in globals():
            _WNDENUMPROC_CACHED = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
        callback_instance = _WNDENUMPROC_CACHED(enum_callback)
        user32.EnumWindows(callback_instance, 0)
        
        # Get current foreground window, put at front of list
        foreground_hwnd = user32.GetForegroundWindow()
        windows.sort(key=lambda w: (w.hwnd != foreground_hwnd, w.app_display_name))
        
        logger.debug(f"[DesktopHook] Found {len(windows)} windows")

        return windows[:30]  # Return max 30 windows

    except Exception as e:
        logger.error(f"[DesktopHook] get_all_windows failed: {e}")
        return []


def _is_system_window_static(title: str, app_name: str = "") -> bool:
    """JudgeYesNoYesSystemWindow或自己的应用"""
    system_titles = [
        "Program Manager",
        "Windows Input Experience",
        "Microsoft Text Input Application",
        "Settings",
        "Calculator",
        "NVIDIA GeForce Overlay",
        "AMD Software",
    ]

    # Filter our own process (NogicOS Electron process)
    self_processes = [
        "nogicos.exe",
    ]
    
    # Exact match NogicOS window title (don't use fuzzy match, otherwise it filters out Cursor with nogicos project)
    nogicos_exact_titles = [
        "NogicOS",
    ]

    if title in system_titles:
        return True
    
    # Exact match NogicOS window (only filter main window, not other apps containing nogicos keyword)
    if title in nogicos_exact_titles:
        return True

    # Check if it's our own process
    if app_name and app_name.lower() in self_processes:
        return True

    if len(title) < 2:
        return True

    return False


def _get_process_name_static(hwnd: int) -> str:
    """GetWindow的Process名"""
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        
        process = kernel32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
            False,
            pid.value
        )
        
        if process:
            try:
                buffer = ctypes.create_unicode_buffer(260)
                psapi.GetModuleBaseNameW(process, None, buffer, 260)
                return buffer.value
            finally:
                kernel32.CloseHandle(process)
        
        return ""
        
    except Exception:
        return ""

