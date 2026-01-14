# -*- coding: utf-8 -*-
"""
Desktop Automation Tools - Phase C

Cross-platform desktop automation using pyautogui and pywinauto.

Tools:
- C1: Basic tools (click, type, hotkey, screenshot)
- C2: Window operations (list, focus, get_active)
- C3: Visual positioning (locate_image, wait_for_image)

Reference: desktop-automation skill
"""

import os
import sys
import time
import base64
import logging
import ctypes
from typing import Optional, List, Dict, Any, Tuple
from io import BytesIO

logger = logging.getLogger("nogicos.tools.desktop")

# #region agent log helper (debug mode)
import json as _json
from pathlib import Path as _Path
_DEBUG_LOG_PATH = _Path(r"c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log")

def _desktop_dbg_log(hypothesis_id: str, location: str, message: str, data: dict):
    """Write a single NDJSON debug line to debug.log (append-only)."""
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
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(_json.dumps(payload, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        pass
# #endregion

# ============================================================================
# C1.6: DPI Awareness (must be set before importing pyautogui)
# ============================================================================

if sys.platform == "win32":
    try:
        # Set DPI awareness for accurate coordinates
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        logger.info("[Desktop] DPI awareness set to per-monitor")
    except Exception as e:
        try:
            # Fallback for older Windows
            ctypes.windll.user32.SetProcessDPIAware()
            logger.info("[Desktop] DPI awareness set (legacy)")
        except:
            logger.warning("[Desktop] Could not set DPI awareness")

# ============================================================================
# Import pyautogui (C1.1)
# ============================================================================

try:
    import pyautogui
    # Safety settings
    pyautogui.FAILSAFE = True  # Move to corner to abort
    pyautogui.PAUSE = 0.1  # Small pause between actions
    PYAUTOGUI_AVAILABLE = True
    logger.info("[Desktop] pyautogui loaded successfully")
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None
    logger.warning("[Desktop] pyautogui not installed. Run: pip install pyautogui")

# ============================================================================
# Import pywinauto (C2.1) - Windows only
# ============================================================================

PYWINAUTO_AVAILABLE = False
if sys.platform == "win32":
    try:
        from pywinauto import Application, Desktop
        from pywinauto.findwindows import find_elements
        PYWINAUTO_AVAILABLE = True
        logger.info("[Desktop] pywinauto loaded successfully")
    except ImportError:
        logger.warning("[Desktop] pywinauto not installed. Run: pip install pywinauto")

# ============================================================================
# Import PIL for image handling
# ============================================================================

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageGrab = None
    logger.warning("[Desktop] PIL not installed. Run: pip install pillow")

# ============================================================================
# Import pyperclip for clipboard (Chinese input support)
# ============================================================================

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    pyperclip = None


def register_desktop_tools(registry):
    """
    Register all desktop automation tools to the registry.
    
    Args:
        registry: ToolRegistry instance
    """
    from .base import ToolCategory
    
    # ========================================================================
    # C1: Basic Desktop Tools
    # ========================================================================
    
    @registry.action(
        description="""Click at SCREEN coordinates (全屏Coordinate).

⚠️ Select正确的Tool:
- window_click: 针对特定Window操作，Usage PostMessage 不抢焦点 (推荐)
- desktop_click: 全屏操作，Usage pyautogui 会抢焦点

仅在以Down情况Usage desktop_click:
- 需要点击System托盘、任务栏等System UI
- 需要点击不在任何WindowInner的Position
- window_click 无法工作时的 fallback""",
        category=ToolCategory.LOCAL,
    )
    async def desktop_click(
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        clicks: int = 1,
    ) -> str:
        """
        C1.2: Click at coordinates.
        
        Args:
            x: X coordinate (optional, uses current position if not set)
            y: Y coordinate (optional, uses current position if not set)
            button: "left", "right", or "middle"
            clicks: Number of clicks (1 for single, 2 for double)
            
        Returns:
            Success message with click location
        """
        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"
        
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, button=button)
                return f"Clicked at ({x}, {y}) with {button} button, {clicks} time(s)"
            else:
                pos = pyautogui.position()
                pyautogui.click(clicks=clicks, button=button)
                return f"Clicked at current position ({pos.x}, {pos.y})"
        except Exception as e:
            return f"Error clicking: {str(e)}"
    
    @registry.action(
        description="""Type text at current cursor position (GlobalInput).

⚠️ Select正确的Tool:
- window_type: 针对特定Window，Usage PostMessage 不抢焦点 (推荐)
- desktop_type: GlobalInput，需要Window有焦点

仅在以Down情况Usage desktop_type:
- TargetWindow已经有焦点
- window_type 无法工作时的 fallback""",
        category=ToolCategory.LOCAL,
    )
    async def desktop_type(
        text: str,
        interval: float = 0.0,
        use_clipboard: bool = False,
    ) -> str:
        """
        C1.3: Type text.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes (seconds)
            use_clipboard: Use clipboard for non-ASCII (Chinese, etc.)
            
        Returns:
            Success message
        """
        # #region agent log
        _desktop_dbg_log("C", "desktop.py:desktop_type:entry", "desktop_type called", {"text": text[:50], "interval": interval, "use_clipboard": use_clipboard})
        # #endregion
        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"
        
        try:
            # Check if text contains non-ASCII characters
            is_ascii = all(ord(c) < 128 for c in text)
            
            if not is_ascii or use_clipboard:
                # Use clipboard for non-ASCII text
                if PYPERCLIP_AVAILABLE:
                    pyperclip.copy(text)
                    pyautogui.hotkey('ctrl', 'v')
                    return f"Typed (via clipboard): {text[:50]}..."
                else:
                    return "Error: pyperclip not installed, cannot type non-ASCII"
            else:
                pyautogui.write(text, interval=interval)
                return f"Typed: {text[:50]}..."
        except Exception as e:
            return f"Error typing: {str(e)}"
    
    @registry.action(
        description="Press keyboard hotkey combination",
        category=ToolCategory.LOCAL,
    )
    async def desktop_hotkey(keys: str) -> str:
        """
        C1.4: Press hotkey combination.
        
        Args:
            keys: Keys to press, either single key or '+' separated combination
                  Examples: "enter", "ctrl+c", "ctrl+shift+s", "alt+f4"
            
        Returns:
            Success message
            
        Examples:
            desktop_hotkey("enter")        # Press Enter
            desktop_hotkey("ctrl+c")       # Copy
            desktop_hotkey("ctrl+v")       # Paste
            desktop_hotkey("alt+f4")       # Close window
            desktop_hotkey("ctrl+shift+s") # Save as
        """
        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"
        
        # #region agent log G1
        _desktop_dbg_log("G1", "desktop_hotkey:start", "desktop_hotkey called", {"keys": keys})
        # #endregion
        
        try:
            # Parse keys: support "ctrl+c" format or single key "enter"
            key_list = [k.strip().lower() for k in keys.split('+')]
            
            # #region agent log G1
            _desktop_dbg_log("G1", "desktop_hotkey:parsed", "Keys parsed", {"key_list": key_list})
            # #endregion
            
            pyautogui.hotkey(*key_list)
            
            # #region agent log G1
            _desktop_dbg_log("G1", "desktop_hotkey:success", "Hotkey pressed", {"key_list": key_list})
            # #endregion
            
            return f"Pressed hotkey: {'+'.join(key_list)}"
        except Exception as e:
            # #region agent log G1
            _desktop_dbg_log("G1", "desktop_hotkey:error", "Hotkey error", {"error": str(e)})
            # #endregion
            return f"Error pressing hotkey: {str(e)}"
    
    @registry.action(
        description="""Take screenshot of the desktop.

⚠️ IMPORTANT: Visual recognition is NOT reliable for file names!
- May hallucinate/misidentify files
- Use list_directory for accurate file listing

WHEN TO USE:
- User asks about visual appearance/layout
- User wants to see wallpaper/icons arrangement  
- User explicitly says "截Graph" or "看一眼长什么样"

DO NOT USE FOR:
- Listing files (use list_directory instead)
- Finding specific files
- Any task requiring accurate file names""",
        category=ToolCategory.LOCAL,
    )
    async def desktop_screenshot(
        region: Optional[Tuple[int, int, int, int]] = None,
        save_path: Optional[str] = None,
    ) -> str:
        """
        C1.5: Take desktop screenshot.
        
        Args:
            region: Optional (x, y, width, height) tuple for partial screenshot
            save_path: Optional path to save screenshot
            
        Returns:
            Base64 encoded image or path if saved
        """
        if not PIL_AVAILABLE:
            return "Error: PIL not installed"
        
        try:
            # Use PIL ImageGrab for better compatibility
            if region:
                x, y, w, h = region
                screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            else:
                screenshot = ImageGrab.grab()
            
            if save_path:
                screenshot.save(save_path)
                return f"Screenshot saved to: {save_path}"
            else:
                # Return base64 encoded
                buffer = BytesIO()
                screenshot.save(buffer, format='PNG')
                b64 = base64.b64encode(buffer.getvalue()).decode()
                return f"data:image/png;base64,{b64[:100]}... (truncated)"
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"
    
    @registry.action(
        description="Get current mouse position",
        category=ToolCategory.LOCAL,
    )
    async def desktop_get_position() -> str:
        """Get current mouse cursor position."""
        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"
        
        try:
            pos = pyautogui.position()
            return f"Mouse position: ({pos.x}, {pos.y})"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @registry.action(
        description="Get screen size",
        category=ToolCategory.LOCAL,
    )
    async def desktop_get_screen_size() -> str:
        """Get screen dimensions."""
        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"
        
        try:
            width, height = pyautogui.size()
            return f"Screen size: {width}x{height}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @registry.action(
        description="Move mouse to coordinates",
        category=ToolCategory.LOCAL,
    )
    async def desktop_move_to(
        x: int,
        y: int,
        duration: float = 0.2,
    ) -> str:
        """
        Move mouse cursor to coordinates.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Movement duration in seconds
        """
        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return f"Moved mouse to ({x}, {y})"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @registry.action(
        description="Scroll the mouse wheel",
        category=ToolCategory.LOCAL,
    )
    async def desktop_scroll(
        clicks: int,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> str:
        """
        Scroll the mouse wheel.
        
        Args:
            clicks: Number of scroll clicks (positive = up, negative = down)
            x: X coordinate to scroll at (optional)
            y: Y coordinate to scroll at (optional)
        """
        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"
        
        try:
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x, y)
                return f"Scrolled {clicks} clicks at ({x}, {y})"
            else:
                pyautogui.scroll(clicks)
                return f"Scrolled {clicks} clicks"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # ========================================================================
    # C2: Window Operations (Windows only)
    # ========================================================================
    
    @registry.action(
        description="List all open windows",
        category=ToolCategory.LOCAL,
    )
    async def desktop_list_windows() -> str:
        """
        C2.2: List all visible windows.
        
        Returns:
            List of window titles and handles
        """
        if not PYWINAUTO_AVAILABLE:
            return "Error: pywinauto not available (Windows only)"
        
        try:
            desktop = Desktop(backend="uia")
            windows = desktop.windows()
            
            result = []
            for i, win in enumerate(windows[:20]):  # Limit to 20
                try:
                    title = win.window_text()
                    if title:  # Only show windows with titles
                        result.append(f"{i+1}. {title}")
                except:
                    pass
            
            if not result:
                return "No windows found"
            
            return "Open windows:\n" + "\n".join(result)
        except Exception as e:
            return f"Error listing windows: {str(e)}"
    
    @registry.action(
        description="Focus a window by title",
        category=ToolCategory.LOCAL,
    )
    async def desktop_focus_window(title: str) -> str:
        """
        C2.3: Focus a window by title (partial match).
        
        Args:
            title: Window title or partial match
            
        Returns:
            Success message
        """
        if not PYWINAUTO_AVAILABLE:
            return "Error: pywinauto not available (Windows only)"
        
        try:
            app = Application(backend="uia").connect(title_re=f".*{title}.*")
            window = app.top_window()
            window.set_focus()
            return f"Focused window: {window.window_text()}"
        except Exception as e:
            return f"Error focusing window '{title}': {str(e)}"
    
    @registry.action(
        description="Get the currently active window",
        category=ToolCategory.LOCAL,
    )
    async def desktop_get_active_window() -> str:
        """
        C2.4: Get currently active window info.
        
        Returns:
            Active window title and info
        """
        if not PYWINAUTO_AVAILABLE:
            return "Error: pywinauto not available (Windows only)"
        
        try:
            desktop = Desktop(backend="uia")
            active = desktop.get_active()
            if active:
                title = active.window_text()
                rect = active.rectangle()
                return f"Active window: {title}\nPosition: ({rect.left}, {rect.top})\nSize: {rect.width()}x{rect.height()}"
            return "No active window found"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # ========================================================================
    # C3: Visual Positioning
    # ========================================================================
    
    @registry.action(
        description="Find image on screen and return coordinates. Use 'image_path' parameter for the path to the image file.",
        category=ToolCategory.LOCAL,
    )
    async def desktop_locate_image(
        image_path: Optional[str] = None,
        confidence: float = 0.8,
        # Common aliases AI might use
        filename: Optional[str] = None,
        path: Optional[str] = None,
        image: Optional[str] = None,
        file: Optional[str] = None,
        image_pattern: Optional[str] = None,
        pattern: Optional[str] = None,
        name: Optional[str] = None,
        target: Optional[str] = None,
        template: Optional[str] = None,
    ) -> str:
        """
        C3.1: Find image on screen.

        Args:
            image_path: Path to image file to find
            confidence: Match confidence (0.0-1.0)

        Returns:
            Center coordinates if found, error otherwise
        """
        # Support multiple parameter names
        actual_path = image_path or filename or path or image or file or image_pattern or pattern or name or target or template
        if not actual_path:
            return "Error: Must provide image_path (or filename/path/image/file)"
        image_path = actual_path

        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"

        if not os.path.exists(image_path):
            return f"Error: Image not found: {image_path}"
        
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return f"Found at: ({center.x}, {center.y})"
            return "Image not found on screen"
        except Exception as e:
            return f"Error locating image: {str(e)}"
    
    @registry.action(
        description="Wait for image to appear on screen. Use 'image_path' parameter for the path to the image file.",
        category=ToolCategory.LOCAL,
    )
    async def desktop_wait_for_image(
        image_path: Optional[str] = None,
        timeout: float = 10.0,
        confidence: float = 0.8,
        # Common aliases AI might use
        image: Optional[str] = None,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        file: Optional[str] = None,
        name: Optional[str] = None,
        target: Optional[str] = None,
        template: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> str:
        """
        C3.2: Wait for image to appear.

        Args:
            image_path: Path to image file
            timeout: Maximum wait time in seconds
            confidence: Match confidence

        Returns:
            Center coordinates when found, timeout error otherwise
        """
        # Support multiple parameter names
        actual_path = image_path or image or filename or path or file or name or target or template or pattern
        if not actual_path:
            return "Error: Must provide image_path (or image/filename/path/file)"
        image_path = actual_path

        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"

        if not os.path.exists(image_path):
            return f"Error: Image not found: {image_path}"
        
        try:
            start = time.time()
            while time.time() - start < timeout:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location:
                    center = pyautogui.center(location)
                    return f"Found at: ({center.x}, {center.y}) after {time.time() - start:.1f}s"
                time.sleep(0.5)
            
            return f"Timeout: Image not found after {timeout}s"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @registry.action(
        description="Find image and click on it. Use 'image_path' for image file path and 'confidence' (0.0-1.0) for match threshold.",
        category=ToolCategory.LOCAL,
    )
    async def desktop_click_image(
        image_path: Optional[str] = None,
        confidence: float = 0.8,
        timeout: float = 5.0,
        # Common aliases AI might use
        image: Optional[str] = None,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        file: Optional[str] = None,
        image_match_threshold: Optional[float] = None,
        threshold: Optional[float] = None,
        match_confidence: Optional[float] = None,
        name: Optional[str] = None,
        target: Optional[str] = None,
        template: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> str:
        """
        C3.3: Click on image when found.

        Args:
            image_path: Path to image file
            confidence: Match confidence (0.0-1.0)
            timeout: Maximum wait time

        Returns:
            Success message with click location
        """
        # Support multiple parameter names for image path
        actual_path = image_path or image or filename or path or file or name or target or template or pattern
        if not actual_path:
            return "Error: Must provide image_path (or image/filename/path/file)"
        image_path = actual_path

        # Support multiple parameter names for confidence
        actual_confidence = image_match_threshold or threshold or match_confidence
        if actual_confidence is not None:
            confidence = actual_confidence

        if not PYAUTOGUI_AVAILABLE:
            return "Error: pyautogui not installed"

        if not os.path.exists(image_path):
            return f"Error: Image not found: {image_path}"
        
        try:
            start = time.time()
            while time.time() - start < timeout:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location:
                    center = pyautogui.center(location)
                    pyautogui.click(center)
                    return f"Clicked image at ({center.x}, {center.y})"
                time.sleep(0.3)
            
            return f"Timeout: Image not found after {timeout}s"
        except Exception as e:
            return f"Error: {str(e)}"
    
    logger.info("[Desktop] All desktop tools registered")

