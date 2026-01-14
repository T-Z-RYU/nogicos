# -*- coding: utf-8 -*-
"""
Browser Hook - 浏览器感知

通用方式感知User浏览器State：
1. Accessibility API - GetWindowtitle
2. Screenshot + Vision - 提取 URL、页面Inner容
3. OCR - 本地 OCR 提取Address栏文字
"""

import asyncio
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .base_hook import BaseHook, HookConfig
from ..store import HookType, BrowserContext

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


@dataclass 
class WindowInfo:
    """WindowInfo"""
    hwnd: int = 0
    title: str = ""
    class_name: str = ""
    process_name: str = ""
    rect: Tuple[int, int, int, int] = (0, 0, 0, 0)  # left, top, right, bottom
    
    @property
    def width(self) -> int:
        return self.rect[2] - self.rect[0]
    
    @property
    def height(self) -> int:
        return self.rect[3] - self.rect[1]
    
    @property
    def x(self) -> int:
        return self.rect[0]
    
    @property
    def y(self) -> int:
        return self.rect[1]


class BrowserHook(BaseHook):
    """
    浏览器 Hook
    
    感知User浏览器State，不需要任何Plugin
    """
    
    # Support's Browser
    SUPPORTED_BROWSERS = {
        "chrome": ["Chrome", "Google Chrome"],
        "firefox": ["Firefox", "Mozilla Firefox"],
        "edge": ["Edge", "Microsoft Edge"],
        "brave": ["Brave"],
        "arc": ["Arc"],
    }
    
    # BrowserWindowClassname（Windows）
    BROWSER_CLASS_NAMES = {
        "Chrome_WidgetWin_1": "chrome",
        "MozillaWindowClass": "firefox",
        "Chrome_WidgetWin_0": "edge",  # Edge alsouse Chromium
    }
    
    def __init__(
        self,
        hook_id: str = "browser",
        config: Optional[HookConfig] = None,
    ):
        super().__init__(hook_id, HookType.BROWSER, config)
        
        self._target_browser: Optional[str] = None  # chrome, firefox, edge, etc.
        self._target_hwnd: Optional[int] = None
        self._last_context: Optional[BrowserContext] = None
    
    async def _connect(self, target: Optional[str] = None) -> bool:
        """
        Connect到浏览器
        
        Args:
            target: 浏览器Class型（chrome, firefox, edge）、HWND（NumberCharacter串）或 None（Auto检测）
        """
        # [Repair]If target YesNumberCharacterstring（HWND），directlyUsagethisWindow
        if target and target.isdigit():
            if not WINDOWS_AVAILABLE:
                logger.warning("[BrowserHook] HWND connection not supported on this platform")
                return False
            try:
                hwnd = int(target)
                window = self._get_window_info_windows(hwnd)
                if window and self._is_browser_window(window):
                    self._target_hwnd = hwnd
                    self._target_browser = self._detect_browser_type(window)
                    logger.info(f"[BrowserHook] Connected to HWND {hwnd}: {window.title}")
                    return True
                else:
                    logger.warning(f"[BrowserHook] HWND {hwnd} is not a valid browser window")
                    return False
            except Exception as e:
                logger.error(f"[BrowserHook] Failed to connect to HWND {target}: {e}")
                return False
        
        # Nothen，byBrowserClasstypeFind
        self._target_browser = target
        
        # DetectionBrowserWindow
        window = await self._find_browser_window(target)
        
        if window:
            self._target_hwnd = window.hwnd
            self._target_browser = self._detect_browser_type(window)
            logger.info(f"[BrowserHook] Found {self._target_browser}: {window.title}")
            return True
        else:
            logger.warning("[BrowserHook] No browser window found")
            return False
    
    async def _disconnect(self) -> bool:
        """DisconnectConnect"""
        self._target_hwnd = None
        self._target_browser = None
        self._last_context = None
        return True
    
    async def capture(self) -> Optional[BrowserContext]:
        """
        捕获浏览器UpDown文
        
        Returns:
            BrowserContext 或 None
        """
        try:
            # [Repair]IfalreadyhaveTarget HWND，directlyUsageit
            if self._target_hwnd:
                window = self._get_window_info_windows(self._target_hwnd)
                if not window:
                    logger.warning(f"[BrowserHook] Target HWND {self._target_hwnd} no longer valid")
                    return self._last_context
            else:
                # Nothen，FindBrowserWindow
                window = await self._find_browser_window(self._target_browser)
                if not window:
                    return self._last_context
                self._target_hwnd = window.hwnd
            
            # fromWindowtitleExtractionInfo
            title, url = self._parse_browser_title(window.title)
            
            # CreateUpDowntext
            context = BrowserContext(
                app=self._target_browser or self._detect_browser_type(window),
                url=url,
                title=title,
                window_title=window.title,  # CompleteWindowtitle（for Overlay preciseMatch）
                hwnd=window.hwnd,  # Windowhandle，for Overlay
                tab_count=1,  # fromtitleNonemethodlearn tab Count
                last_updated=datetime.now().isoformat(),
            )
            
            # IfEnable OCR，tryExtractionMoreInfo
            if self.config.enable_ocr:
                try:
                    url_from_ocr = await self._ocr_address_bar(window)
                    if url_from_ocr:
                        context.url = url_from_ocr
                except Exception as e:
                    logger.debug(f"[BrowserHook] OCR failed: {e}")
            
            self._last_context = context
            return context
            
        except Exception as e:
            logger.error(f"[BrowserHook] Capture failed: {e}")
            return self._last_context
    
    def _detect_browser_type(self, window: WindowInfo) -> str:
        """从WindowInfo检测浏览器Class型"""
        # Priorityuse class_name
        if window.class_name in self.BROWSER_CLASS_NAMES:
            return self.BROWSER_CLASS_NAMES[window.class_name]
        
        # fromtitleDetection
        title_lower = window.title.lower()
        for browser_id, names in self.SUPPORTED_BROWSERS.items():
            for name in names:
                if name.lower() in title_lower:
                    return browser_id
        
        return "unknown"
    
    def _parse_browser_title(self, title: str) -> Tuple[str, str]:
        """
        从浏览器titleParse页面title和可能的 URL
        
        典型格式: "Google - Chrome"
                  "example.com - Page Title - Edge"
        
        Returns:
            (page_title, url_hint)
        """
        if not title:
            return "", ""
        
        # RemoveBrowsernameAftersuffix
        for names in self.SUPPORTED_BROWSERS.values():
            for name in names:
                if title.endswith(f" - {name}"):
                    title = title[:-len(f" - {name}")]
                    break
                if title.endswith(f" — {name}"):  # em dash
                    title = title[:-len(f" — {name}")]
                    break
        
        # tryExtractiondomainname
        url_hint = ""
        # Match domain.com Format
        domain_match = re.search(r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', title)
        if domain_match:
            url_hint = f"https://{domain_match.group(1)}"
        
        return title.strip(), url_hint
    
    async def _find_browser_window(self, target_browser: Optional[str] = None) -> Optional[WindowInfo]:
        """
        Find浏览器Window
        
        Args:
            target_browser: Specify浏览器，None 则Find任意浏览器
            
        Returns:
            WindowInfo 或 None
        """
        if sys.platform == "win32" and WINDOWS_AVAILABLE:
            return await self._find_browser_window_windows(target_browser)
        else:
            # macOS / Linux not yetImplement
            logger.warning(f"[BrowserHook] Platform {sys.platform} not fully supported")
            return None
    
    async def _find_browser_window_windows(self, target_browser: Optional[str] = None) -> Optional[WindowInfo]:
        """Windows PlatformFind浏览器Window"""
        try:
            user32 = ctypes.windll.user32
            
            # GetBeforeplatformWindow
            hwnd = user32.GetForegroundWindow()
            if hwnd:
                window = self._get_window_info_windows(hwnd)
                if window and self._is_browser_window(window, target_browser):
                    return window
            
            # EnumallWindowFindBrowser
            windows = []
            
            def enum_callback(hwnd, _):
                if user32.IsWindowVisible(hwnd):
                    window = self._get_window_info_windows(hwnd)
                    if window and self._is_browser_window(window, target_browser):
                        windows.append(window)
                return True
            
            # [Repair #18 + Segfault Repair]
            # MustkeepCallbackInstance's Reference，Nothenwillbe GC causeCrash
            if not hasattr(self, '_WNDENUMPROC'):
                self._WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
            callback_instance = self._WNDENUMPROC(enum_callback)
            user32.EnumWindows(callback_instance, 0)
            
            if windows:
                return windows[0]
            
            return None
            
        except Exception as e:
            logger.error(f"[BrowserHook] Window enumeration failed: {e}")
            return None
    
    def _get_window_info_windows(self, hwnd: int) -> Optional[WindowInfo]:
        """Get Windows WindowInfo"""
        try:
            user32 = ctypes.windll.user32
            
            # GetWindowtitle
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return None
            
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value
            
            # GetClassname
            class_buffer = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buffer, 256)
            class_name = class_buffer.value
            
            # GetWindowPosition
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            return WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_name,
                rect=(rect.left, rect.top, rect.right, rect.bottom),
            )
            
        except Exception as e:
            logger.debug(f"[BrowserHook] Get window info failed: {e}")
            return None
    
    # needexclude's  Electron Apply（itpluralalsouse Chrome_WidgetWin_1 Classname）
    EXCLUDED_ELECTRON_APPS = [
        "nogicos", "nogicos-ui", "cursor", "vscode", "visual studio code",
        "electron", "slack", "discord", "notion", "figma",
    ]
    
    def _is_browser_window(self, window: WindowInfo, target_browser: Optional[str] = None) -> bool:
        """
        JudgeYesNoYes浏览器Window
        
        [通用方案]PriorityChecktitleMediumYesNoPackage含浏览器名称，
        因为 Chrome_WidgetWin_1 Class名被很多 Electron 应用Usage。
        """
        title_lower = window.title.lower()
        
        # [Priority]ChecktitleYesNoPackagecontainBrowsername
        # Truecorrect's BrowsertitleFormat: "pagetitle - Google Chrome"
        for browser_id, names in self.SUPPORTED_BROWSERS.items():
            if target_browser and browser_id != target_browser:
                continue
            for name in names:
                if name.lower() in title_lower:
                    return True
        
        # [backup]IftitlenoBrowsername，CheckClassname
        # butthismaybemisjudge Electron Apply，soonlyasforbackup
        # if window.class_name in self.BROWSER_CLASS_NAMES:
        #     detected = self.BROWSER_CLASS_NAMES[window.class_name]
        #     if target_browser is None or detected == target_browser:
        #         return True
        
        return False
    
    async def _ocr_address_bar(self, window: WindowInfo) -> Optional[str]:
        """
        OCR 提取Address栏 URL
        
        Usage Windows Inner置 OCR 或 Tesseract
        """
        try:
            from .screenshot_utils import capture_screen
            from .ocr_utils import get_screenshot_ocr
            
            # AddressbarLocaleestimate：WindowTop
            # Chrome/Edge: Title Barabout 30px，tab barabout 35px，Addressbarin 70-130px
            address_bar_region = (
                window.x + 100,       # SkipBrowserNavigationButton
                window.y + 50,        # SkipTitle Bar
                window.width - 300,   # subtractRightsideButton
                60,                   # AddressbarHeight
            )
            
            # capturetakeAddressbar
            screenshot_data = await capture_screen(address_bar_region)
            if not screenshot_data:
                return None
            
            # OCR Extraction URL
            ocr = get_screenshot_ocr()
            if not ocr.available:
                logger.debug("[BrowserHook] OCR not available")
                return None
            
            url = await ocr.extract_url(screenshot_data)
            if url:
                logger.debug(f"[BrowserHook] OCR extracted URL: {url}")
            return url
            
        except Exception as e:
            logger.debug(f"[BrowserHook] OCR failed: {e}")
            return None
    
    def get_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get当Before浏览器WindowPosition
        
        供 Overlay Usage
        
        Returns:
            (x, y, width, height) 或 None
        """
        if not self._target_hwnd:
            return None
        
        try:
            if sys.platform == "win32" and WINDOWS_AVAILABLE:
                window = self._get_window_info_windows(self._target_hwnd)
                if window:
                    return (window.x, window.y, window.width, window.height)
        except Exception as e:
            logger.error(f"[BrowserHook] Get window rect failed: {e}")
        
        return None

