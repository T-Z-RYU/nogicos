# -*- coding: utf-8 -*-
"""
Windows Compatibility Layer - PostMessage + Fallback Strategy

Reference: Windows System工程师 Review 最佳实践

应用Class型兼容性:
- 传统 Win32 应用: ✅ PostMessage Valid
- Electron 应用: ⚠️ 部分Valid (Chromium 自己HandleInput)
- UWP 应用: ❌ Invalid (不同的Message模型)
- DirectX 游戏: ❌ Invalid (直接Read硬件Input)
"""

import ctypes
from ctypes import wintypes
import asyncio
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("nogicos.tools.windows_compat")

# ============================================================================
# DPI awareness setup - must be set before any pyautogui/UIA operations
# Otherwise coordinates will be wrong on high DPI screens (e.g. 1.75x scaling)
# ============================================================================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    logger.info("DPI awareness set to PROCESS_PER_MONITOR_DPI_AWARE")
except Exception as e:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Legacy Windows fallback
        logger.info("DPI awareness set via SetProcessDPIAware (legacy)")
    except Exception:
        logger.warning(f"Failed to set DPI awareness: {e}")

# #region agent log helper (debug mode)
import json as _json
import os as _os
import time as _time
from pathlib import Path as _Path
_DEBUG_LOG_PATH = _Path(r"c:\Users\WIN\Desktop\Cursor Project\.cursor\debug.log")

def _win_compat_dbg_log(hypothesis_id: str, location: str, message: str, data: dict):
    """Write a single NDJSON debug line to debug.log (append-only)."""
    try:
        payload = {
            "sessionId": "debug-session",
            "runId": "pre-fix-1",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(_time.time() * 1000),
        }
        _DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(_json.dumps(payload, ensure_ascii=False) + "\n")
            f.flush()
            _os.fsync(f.fileno())
    except Exception:
        pass
# #endregion


class InputMethod(Enum):
    """Input method enum"""
    POST_MESSAGE = "post_message"      # Non-invasive, doesn't steal focus
    SEND_INPUT = "send_input"          # Requires focus, more reliable
    UI_AUTOMATION = "ui_automation"    # UIA, suitable for modern apps


@dataclass
class InputResult:
    """Input operation result"""
    success: bool
    method_used: InputMethod
    fallback_count: int = 0
    error: Optional[str] = None


# Windows MessageConstant
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEMOVE = 0x0200
WM_CHAR = 0x0102
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002
MK_MBUTTON = 0x0010


class WindowInputController:
    """
    Window input controller - auto fallback strategy
    
    Priority:
    1. PostMessage (non-invasive)
    2. SendInput (requires focus)
    3. UI Automation (modern apps)
    """
    
    CLICK_DELAY_MS = 50      # Click delay
    CHAR_DELAY_MS = 20       # Character input delay
    
    def __init__(self):
        # Load user32.dll
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self._setup_functions()
    
    def _setup_functions(self):
        """Set Windows API FunctionSignature"""
        # PostMessageW
        self.user32.PostMessageW.argtypes = [
            wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
        ]
        self.user32.PostMessageW.restype = wintypes.BOOL
        
        # SetForegroundWindow
        self.user32.SetForegroundWindow.argtypes = [wintypes.HWND]
        self.user32.SetForegroundWindow.restype = wintypes.BOOL
        
        # AllowSetForegroundWindow - allows background process to set foreground window
        self.user32.AllowSetForegroundWindow.argtypes = [wintypes.DWORD]
        self.user32.AllowSetForegroundWindow.restype = wintypes.BOOL
        
        # AttachThreadInput - attach our thread to another thread's input queue
        self.user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
        self.user32.AttachThreadInput.restype = wintypes.BOOL
        
        # GetForegroundWindow - get the current foreground window
        self.user32.GetForegroundWindow.argtypes = []
        self.user32.GetForegroundWindow.restype = wintypes.HWND
        
        # GetWindowThreadProcessId - get thread ID of window
        self.user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        
        # BringWindowToTop - bring window to top of Z-order
        self.user32.BringWindowToTop.argtypes = [wintypes.HWND]
        self.user32.BringWindowToTop.restype = wintypes.BOOL
        
        # ClientToScreen
        self.user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
        self.user32.ClientToScreen.restype = wintypes.BOOL
        
        # IsWindow
        self.user32.IsWindow.argtypes = [wintypes.HWND]
        self.user32.IsWindow.restype = wintypes.BOOL

        # SetCursorPos / mouse_event for pointer control
        self.user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
        self.user32.SetCursorPos.restype = wintypes.BOOL

        # Note: dwExtraInfo uses ULONG_PTR in WinAPI; use DWORD for compatibility
        self.user32.mouse_event.argtypes = [
            wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD
        ]
        self.user32.mouse_event.restype = None
        
        # Clipboard APIs
        self.user32.OpenClipboard.argtypes = [wintypes.HWND]
        self.user32.OpenClipboard.restype = wintypes.BOOL
        
        self.user32.CloseClipboard.argtypes = []
        self.user32.CloseClipboard.restype = wintypes.BOOL
        
        self.user32.EmptyClipboard.argtypes = []
        self.user32.EmptyClipboard.restype = wintypes.BOOL
        
        self.user32.GetClipboardData.argtypes = [wintypes.UINT]
        self.user32.GetClipboardData.restype = wintypes.HANDLE
        
        self.user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
        self.user32.SetClipboardData.restype = wintypes.HANDLE
        
        self.user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
        self.user32.IsClipboardFormatAvailable.restype = wintypes.BOOL
        
        # SendInput (for Ctrl+V)
        self.user32.SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]
        self.user32.SendInput.restype = wintypes.UINT
    
    async def click(self, hwnd: int, x: int, y: int, button: str = "left") -> InputResult:
        """
        Click operation - directly using pyautogui (most reliable)
        
        For modern apps (WhatsApp/Electron etc.), PostMessage doesn't work
        Use pyautogui global click directly
        
        Args:
            hwnd: Window handle
            x: Client area X coordinate
            y: Client area Y coordinate
            button: "left", "right", "middle"
        """
        import pyautogui
        
        # Verify window validity
        if not self.user32.IsWindow(hwnd):
            return InputResult(
                success=False,
                method_used=InputMethod.POST_MESSAGE,
                error="Invalid window handle"
            )
        
        try:
            # Get window screen position
            rect = wintypes.RECT()
            if not self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return InputResult(
                    success=False,
                    method_used=InputMethod.SEND_INPUT,
                    error="Failed to get window rect"
                )
            
            # Convert client area coordinates to screen coordinates
            screen_x = rect.left + x
            screen_y = rect.top + y
            
            # #region agent log J1
            _win_compat_dbg_log("J1", "click:pyautogui", "Using pyautogui click", {
                "hwnd": hwnd, "client_x": x, "client_y": y, 
                "screen_x": screen_x, "screen_y": screen_y,
                "rect": {"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom}
            })
            # #endregion
            
            # Use pyautogui click
            pyautogui.click(screen_x, screen_y, button=button)
            await asyncio.sleep(0.1)
            
            return InputResult(success=True, method_used=InputMethod.SEND_INPUT)
            
        except Exception as e:
            # #region agent log J1
            _win_compat_dbg_log("J1", "click:error", "pyautogui click failed", {"error": str(e)})
            # #endregion
            return InputResult(
                success=False,
                method_used=InputMethod.SEND_INPUT,
                error=f"pyautogui click failed: {str(e)}"
            )
    
    async def _try_post_message_click(
        self, hwnd: int, x: int, y: int, button: str = "left"
    ) -> bool:
        """Try PostMessage click"""
        try:
            lparam = self._make_lparam(x, y)
            
            # Select message based on button type
            if button == "left":
                down_msg, up_msg, mk = WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON
            elif button == "right":
                down_msg, up_msg, mk = WM_RBUTTONDOWN, WM_RBUTTONUP, MK_RBUTTON
            else:  # middle
                down_msg, up_msg, mk = WM_MBUTTONDOWN, WM_MBUTTONUP, MK_MBUTTON
            
            # DOWN
            result = self.user32.PostMessageW(hwnd, down_msg, mk, lparam)
            if not result:
                logger.debug(f"PostMessage DOWN failed: {ctypes.get_last_error()}")
                return False
            
            await asyncio.sleep(self.CLICK_DELAY_MS / 1000)
            
            # UP
            result = self.user32.PostMessageW(hwnd, up_msg, 0, lparam)
            if not result:
                logger.debug(f"PostMessage UP failed: {ctypes.get_last_error()}")
                return False
            
            logger.debug(f"PostMessage click success at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.debug(f"PostMessage click exception: {e}")
            return False
    
    async def _fallback_send_input_click(
        self, hwnd: int, x: int, y: int, button: str = "left"
    ) -> bool:
        """Fallback: Use SendInput (requires window focus)"""
        try:
            # 0. Verify window still valid (prevent TOCTOU)
            if not self.user32.IsWindow(hwnd):
                logger.debug("Window closed before SendInput fallback")
                return False

            # 1. Get window focus (will disturb user!)
            self.user32.SetForegroundWindow(hwnd)
            await asyncio.sleep(0.1)  # Wait for window activation

            # Verify again
            if not self.user32.IsWindow(hwnd):
                return False

            # 2. Convert client area coordinates to screen coordinates
            point = wintypes.POINT(x, y)
            if not self.user32.ClientToScreen(hwnd, ctypes.byref(point)):
                logger.debug("ClientToScreen failed")
                return False

            # 3. Verify coordinate validity
            if point.x < -10000 or point.x > 50000 or point.y < -10000 or point.y > 50000:
                logger.debug(f"Invalid screen coordinates: ({point.x}, {point.y})")
                return False

            # 4. Usage pyautogui
            try:
                import pyautogui
                pyautogui.click(point.x, point.y, button=button)
                logger.debug(f"SendInput fallback success at screen ({point.x}, {point.y})")
                return True
            except ImportError:
                logger.warning("pyautogui not available for SendInput fallback")
                return False
            except Exception as e:
                # CRITICAL: Log the actual error instead of hiding it
                logger.warning(f"pyautogui.click failed at ({point.x}, {point.y}): {e}")
                return False

        except Exception as e:
            logger.warning(f"SendInput fallback exception: {e}")
            return False
    
    async def _fallback_uia_click(
        self, hwnd: int, x: int, y: int, button: str = "left"
    ) -> bool:
        """
        Fallback: Use pywinauto (if available)

        pywinauto has better support for modern apps
        """
        try:
            # 0. Verify window still valid (prevent pywinauto crash on invalid HWND)
            if not self.user32.IsWindow(hwnd):
                logger.debug("Window closed before pywinauto fallback")
                return False

            # Try using pywinauto
            from pywinauto import Desktop
            from pywinauto.controls.hwndwrapper import HwndWrapper

            # Wrap window (in try block, catch any pywinauto exception)
            wrapper = HwndWrapper(hwnd)

            # Verify window valid again
            if not self.user32.IsWindow(hwnd):
                return False

            # Get window rectangle
            rect = wrapper.rectangle()

            # Verify rectangle validity
            if rect.width() <= 0 or rect.height() <= 0:
                logger.debug(f"Invalid window rect: {rect}")
                return False

            # Verify coordinates within window bounds (with tolerance for edge cases)
            tolerance = 10  # Allow 10px outside window bounds
            if x < -tolerance or x > rect.width() + tolerance or y < -tolerance or y > rect.height() + tolerance:
                logger.debug(f"Coordinates ({x}, {y}) far outside window bounds (w={rect.width()}, h={rect.height()})")
                return False

            # Clamp coordinates to valid range (handle edge clicks gracefully)
            clamped_x = max(1, min(x, rect.width() - 1))
            clamped_y = max(1, min(y, rect.height() - 1))
            if clamped_x != x or clamped_y != y:
                logger.debug(f"Coordinates clamped: ({x}, {y}) -> ({clamped_x}, {clamped_y})")
                x, y = clamped_x, clamped_y

            # Use pywinauto click
            if button == "left":
                wrapper.click_input(coords=(x, y))
            elif button == "right":
                wrapper.right_click_input(coords=(x, y))
            else:
                wrapper.click_input(coords=(x, y), button='middle')

            logger.debug(f"pywinauto click success at ({x}, {y})")
            return True

        except ImportError:
            logger.debug("pywinauto not available for UIA fallback")
            return False
        except Exception as e:
            logger.debug(f"pywinauto fallback exception: {e}")
            return False
    
    async def double_click(self, hwnd: int, x: int, y: int, button: str = "left") -> InputResult:
        """Double click operation"""
        result1 = await self.click(hwnd, x, y, button)
        if not result1.success:
            return result1
        
        await asyncio.sleep(0.05)  # 50ms delay
        result2 = await self.click(hwnd, x, y, button)
        
        return InputResult(
            success=result2.success,
            method_used=result2.method_used,
            fallback_count=max(result1.fallback_count, result2.fallback_count),
            error=result2.error
        )
    
    async def type_text(self, hwnd: int, text: str) -> InputResult:
        """
        Type text - using pyautogui (most reliable)
        
        For modern apps (Electron/WhatsApp etc.), PostMessage doesn't work
        Use pyautogui global keyboard simulation directly
        """
        return await self._type_via_pyautogui(hwnd, text)
    
    async def _type_via_pyautogui(self, hwnd: int, text: str) -> InputResult:
        """
        Simplest direct approach: pywinauto directly operates controls (no mouse coordinates needed)
        """
        import pyperclip
        
        try:
            from pywinauto import Desktop
            from pywinauto.keyboard import send_keys
            
            _win_compat_dbg_log("SIMPLE", "start", "Direct control method", {"hwnd": hwnd})
            
            # 1. Activate window
            self.user32.SetForegroundWindow(hwnd)
            await asyncio.sleep(0.2)
            
            # 2. Use pywinauto to find window and input controls
            desktop = Desktop(backend='uia')
            target_window = None
            for win in desktop.windows():
                if win.handle == hwnd:
                    target_window = win
                    break
            
            if target_window:
                # Find Edit controls
                edits = list(target_window.descendants(control_type='Edit'))
                _win_compat_dbg_log("SIMPLE", "edits", f"Found {len(edits)} Edit controls", {})
                
                if edits:
                    # Use the bottommost Edit
                    bottom_edit = max(edits, key=lambda e: e.rectangle().top)
                    rect = bottom_edit.rectangle()
                    # #region agent log
                    _win_compat_dbg_log("F2", "edit_info", f"Selected Edit control", {"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom, "class_name": getattr(bottom_edit, 'class_name', lambda: 'unknown')()})
                    # #endregion
                    
                    # Directly set focus to control (no click needed)
                    try:
                        bottom_edit.set_focus()
                        await asyncio.sleep(0.1)
                        # #region agent log
                        _win_compat_dbg_log("F2", "focus", "Focus set successfully", {})
                        # #endregion
                    except Exception as focus_err:
                        # #region agent log
                        _win_compat_dbg_log("F2", "focus_fail", str(focus_err), {})
                        # #endregion
                    
                    # ====== Fix: Skip set_edit_text, use clipboard directly (more reliable for Electron apps) ======
                    # set_edit_text usually doesn't work for Electron/Chromium apps (like WhatsApp)
                    # #region agent log
                    _win_compat_dbg_log("F2", "strategy", "Using clipboard paste (more reliable for Electron apps)", {})
                    # #endregion
                    
                    # Clipboard paste (reliable for all apps)
                    try:
                        original = pyperclip.paste()
                    except:
                        original = ""
                    
                    pyperclip.copy(text)
                    # #region agent log
                    _win_compat_dbg_log("F2", "clipboard", f"Copied to clipboard", {"text_len": len(text), "text_preview": text[:50] if len(text) > 50 else text})
                    # #endregion
                    await asyncio.sleep(0.05)
                    
                    # Ensure target window has focus
                    try:
                        target_window.set_focus()
                        await asyncio.sleep(0.3)  # Increased delay for window to truly activate
                        # #region agent log
                        _win_compat_dbg_log("F2", "window_focus", "Window focus set before paste", {})
                        # #endregion
                    except Exception as wf_err:
                        # #region agent log
                        _win_compat_dbg_log("F2", "window_focus_fail", str(wf_err), {})
                        # #endregion
                    
                    # Click input box to ensure it truly gets focus (key for Electron apps)
                    try:
                        import pyautogui
                        edit_rect = bottom_edit.rectangle()
                        click_x = (edit_rect.left + edit_rect.right) // 2
                        click_y = (edit_rect.top + edit_rect.bottom) // 2
                        pyautogui.click(click_x, click_y)
                        await asyncio.sleep(0.2)
                        # #region agent log
                        _win_compat_dbg_log("F3", "click_edit", "Clicked edit control to ensure focus", {"x": click_x, "y": click_y})
                        # #endregion
                    except Exception as click_err:
                        # #region agent log
                        _win_compat_dbg_log("F3", "click_fail", str(click_err), {})
                        # #endregion
                    
                    # Use pyautogui.hotkey instead of send_keys (more reliable)
                    import pyautogui
                    pyautogui.hotkey('ctrl', 'v')
                    # #region agent log
                    _win_compat_dbg_log("F3", "paste_sent", "Ctrl+V sent via pyautogui.hotkey", {})
                    # #endregion
                    await asyncio.sleep(0.2)
                    
                    try:
                        pyperclip.copy(original)
                    except:
                        pass
                    
                    # #region agent log
                    _win_compat_dbg_log("F2", "done", "Clipboard paste completed", {"text": text})
                    return InputResult(success=True, method_used=InputMethod.UI_AUTOMATION)
            
            # Fallback: Direct keyboard send (assuming window has focus)
            _win_compat_dbg_log("SIMPLE", "fallback", "No Edit found, using direct keyboard", {})
            
            try:
                original = pyperclip.paste()
            except:
                original = ""
            
            pyperclip.copy(text)
            await asyncio.sleep(0.05)
            send_keys('^v')
            await asyncio.sleep(0.15)
            
            try:
                pyperclip.copy(original)
            except:
                pass
            
            return InputResult(success=True, method_used=InputMethod.SEND_INPUT)
            
        except Exception as e:
            _win_compat_dbg_log("SIMPLE", "error", str(e), {})
            return InputResult(success=False, method_used=InputMethod.SEND_INPUT, error=str(e))
    
    async def _type_via_wm_char(self, hwnd: int, text: str) -> InputResult:
        """Use WM_CHAR to input ASCII text"""
        try:
            for char in text:
                result = self.user32.PostMessageW(hwnd, WM_CHAR, ord(char), 0)
                if not result:
                    return InputResult(
                        success=False,
                        method_used=InputMethod.POST_MESSAGE,
                        error=f"Failed to type character: {char}"
                    )
                await asyncio.sleep(self.CHAR_DELAY_MS / 1000)
            
            return InputResult(success=True, method_used=InputMethod.POST_MESSAGE)
            
        except Exception as e:
            return InputResult(
                success=False,
                method_used=InputMethod.POST_MESSAGE,
                error=str(e)
            )
    
    async def _send_ctrl_v(self, hwnd: int) -> bool:
        """
        Send Ctrl+V - Usage SendInput API (更可靠)
        
        SendInput 比 PostMessage 更可靠，因为：
        - 对 Electron/Chromium 应用Valid
        - 对 UWP 应用Valid
        - 模拟True实键盘Input
        
        Cons: Requires window to have focus
        """
        import ctypes
        from ctypes import wintypes
        
        # SendInput structure
        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYUP = 0x0002
        VK_CONTROL = 0x11
        VK_V = 0x56
        
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
            ]
        
        class INPUT(ctypes.Structure):
            class _INPUT_UNION(ctypes.Union):
                _fields_ = [("ki", KEYBDINPUT)]
            _anonymous_ = ("_input",)
            _fields_ = [
                ("type", wintypes.DWORD),
                ("_input", _INPUT_UNION),
            ]
        
        try:
            # 1. Activate target window (SendInput requires window focus)
            # #region agent log H1
            _win_compat_dbg_log("H1", "send_ctrl_v:focus", "Setting foreground window", {"hwnd": hwnd})
            # #endregion
            
            # Use AttachThreadInput trick to bypass Windows focus stealing prevention
            # This works by temporarily attaching our thread to the foreground window's thread
            current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
            foreground_hwnd = self.user32.GetForegroundWindow()
            foreground_thread = self.user32.GetWindowThreadProcessId(foreground_hwnd, None)
            target_thread = self.user32.GetWindowThreadProcessId(hwnd, None)
            
            attached = False
            try:
                # Attach to foreground thread to get permission to set foreground window
                if current_thread != foreground_thread:
                    attached = bool(self.user32.AttachThreadInput(current_thread, foreground_thread, True))
                
                # Also attach to target thread
                if current_thread != target_thread:
                    self.user32.AttachThreadInput(current_thread, target_thread, True)
                
                # Now we should be able to set foreground window
                self.user32.AllowSetForegroundWindow(-1)  # ASFW_ANY = -1
                result = self.user32.SetForegroundWindow(hwnd)
                
                # Also try BringWindowToTop for good measure
                self.user32.BringWindowToTop(hwnd)
                
            finally:
                # Detach threads
                if attached and current_thread != foreground_thread:
                    self.user32.AttachThreadInput(current_thread, foreground_thread, False)
                if current_thread != target_thread:
                    self.user32.AttachThreadInput(current_thread, target_thread, False)
            
            # #region agent log H1
            _win_compat_dbg_log("H1", "send_ctrl_v:focus_result", "SetForegroundWindow result", {"success": bool(result), "hwnd": hwnd, "attached": attached})
            # #endregion
            
            if not result:
                logger.warning(f"SetForegroundWindow failed for hwnd {hwnd}")
            
            await asyncio.sleep(0.15)  # Wait for window activation (increased to 150ms)
            
            # 2. Build input sequence: Ctrl↓ V↓ V↑ Ctrl↑
            inputs = (INPUT * 4)()
            
            # Ctrl Down
            inputs[0].type = INPUT_KEYBOARD
            inputs[0].ki.wVk = VK_CONTROL
            inputs[0].ki.dwFlags = 0
            
            # V Down
            inputs[1].type = INPUT_KEYBOARD
            inputs[1].ki.wVk = VK_V
            inputs[1].ki.dwFlags = 0
            
            # V Up
            inputs[2].type = INPUT_KEYBOARD
            inputs[2].ki.wVk = VK_V
            inputs[2].ki.dwFlags = KEYEVENTF_KEYUP
            
            # Ctrl Up
            inputs[3].type = INPUT_KEYBOARD
            inputs[3].ki.wVk = VK_CONTROL
            inputs[3].ki.dwFlags = KEYEVENTF_KEYUP
            
            # 3. SendInput
            sent = self.user32.SendInput(4, ctypes.byref(inputs), ctypes.sizeof(INPUT))
            
            if sent != 4:
                logger.warning(f"SendInput only sent {sent}/4 inputs")
                return False
            
            await asyncio.sleep(0.05)  # Wait for paste to complete
            return True
            
        except Exception as e:
            logger.error(f"SendInput Ctrl+V failed: {e}")
            # Fallback: Try PostMessage method
            try:
                self.user32.PostMessageW(hwnd, WM_KEYDOWN, VK_CONTROL, 0)
                await asyncio.sleep(0.02)
                self.user32.PostMessageW(hwnd, WM_KEYDOWN, VK_V, 0)
                await asyncio.sleep(0.02)
                self.user32.PostMessageW(hwnd, WM_KEYUP, VK_V, 0)
                await asyncio.sleep(0.02)
                self.user32.PostMessageW(hwnd, WM_KEYUP, VK_CONTROL, 0)
                await asyncio.sleep(0.05)
                return True
            except Exception as e2:
                logger.error(f"PostMessage Ctrl+V fallback also failed: {e2}")
                return False
    
    async def _open_clipboard_with_retry(self, hwnd: int, max_retries: int = 5, delay: float = 0.1) -> bool:
        """
        Open clipboard with retry mechanism to prevent deadlock

        Args:
            hwnd: Window handle (can be 0)
            max_retries: Max retry attempts
            delay: Delay between retries (seconds)

        Returns:
            Whether successfully opened
        """
        for attempt in range(max_retries):
            if self.user32.OpenClipboard(hwnd):
                return True
            if hwnd != 0 and self.user32.OpenClipboard(0):
                return True
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
        return False

    async def _type_via_clipboard(self, hwnd: int, text: str) -> InputResult:
        """
        Use clipboard + Ctrl+V to input text (supports Chinese)

        Process:
        1. Save original clipboard content
        2. Set new text to clipboard
        3. Send Ctrl+V
        4. Restore original clipboard content
        """
        import ctypes
        from ctypes import wintypes

        # Clipboard API
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002

        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        
        # CRITICAL: Must set correct types for 64-bit compatibility
        # Without this, handles (pointers) overflow on 64-bit systems
        kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
        kernel32.GlobalAlloc.restype = wintypes.HANDLE
        kernel32.GlobalLock.argtypes = [wintypes.HANDLE]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]
        kernel32.GlobalUnlock.restype = wintypes.BOOL

        try:
            # 1. Open clipboard (with retry)
            if not await self._open_clipboard_with_retry(hwnd):
                return InputResult(
                    success=False,
                    method_used=InputMethod.POST_MESSAGE,
                    error="Failed to open clipboard after retries"
                )
            
            try:
                # 2. Save original clipboard content
                original_data = None
                if self.user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                    handle = self.user32.GetClipboardData(CF_UNICODETEXT)
                    if handle:
                        ptr = kernel32.GlobalLock(handle)
                        if ptr:
                            original_data = ctypes.wstring_at(ptr)
                            kernel32.GlobalUnlock(handle)
                
                # 3. Clear and set new content
                self.user32.EmptyClipboard()
                
                # Allocate memory
                text_bytes = (text + '\0').encode('utf-16-le')
                h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(text_bytes))
                if not h_mem:
                    return InputResult(
                        success=False,
                        method_used=InputMethod.POST_MESSAGE,
                        error="Failed to allocate clipboard memory"
                    )
                
                # Copy data
                ptr = kernel32.GlobalLock(h_mem)
                ctypes.memmove(ptr, text_bytes, len(text_bytes))
                kernel32.GlobalUnlock(h_mem)
                
                # Set clipboard
                self.user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                
            finally:
                self.user32.CloseClipboard()
            
            # 4. Send Ctrl+V - Use SendInput (more reliable)
            # PostMessage doesn't work for Electron apps, SendInput is more universal
            await self._send_ctrl_v(hwnd)
            
            # 5. Restore original clipboard content (optional, avoid overwriting user data)
            if original_data:
                try:
                    if self.user32.OpenClipboard(0):
                        try:
                            self.user32.EmptyClipboard()
                            orig_bytes = (original_data + '\0').encode('utf-16-le')
                            h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(orig_bytes))
                            if h_mem:
                                ptr = kernel32.GlobalLock(h_mem)
                                ctypes.memmove(ptr, orig_bytes, len(orig_bytes))
                                kernel32.GlobalUnlock(h_mem)
                                self.user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                        finally:
                            self.user32.CloseClipboard()
                except:
                    pass  # Restore failure doesn't affect main flow
            
            return InputResult(success=True, method_used=InputMethod.POST_MESSAGE)
            
        except Exception as e:
            logger.error(f"Clipboard type failed: {e}")
            return InputResult(
                success=False,
                method_used=InputMethod.POST_MESSAGE,
                error=f"Clipboard type failed: {str(e)}"
            )
    
    async def key_press(self, hwnd: int, key_code: int) -> InputResult:
        """Key press operation"""
        try:
            # KEY DOWN
            result = self.user32.PostMessageW(hwnd, WM_KEYDOWN, key_code, 0)
            if not result:
                return InputResult(
                    success=False,
                    method_used=InputMethod.POST_MESSAGE,
                    error="Failed to send key down"
                )
            
            await asyncio.sleep(self.CLICK_DELAY_MS / 1000)
            
            # KEY UP
            result = self.user32.PostMessageW(hwnd, WM_KEYUP, key_code, 0)
            if not result:
                return InputResult(
                    success=False,
                    method_used=InputMethod.POST_MESSAGE,
                    error="Failed to send key up"
                )
            
            return InputResult(success=True, method_used=InputMethod.POST_MESSAGE)
            
        except Exception as e:
            return InputResult(
                success=False,
                method_used=InputMethod.POST_MESSAGE,
                error=str(e)
            )
    
    async def drag(
        self, hwnd: int, 
        from_x: int, from_y: int, 
        to_x: int, to_y: int,
        steps: int = 10
    ) -> InputResult:
        """Drag operation - DOWN → MOVE → MOVE → UP"""
        try:
            # DOWN
            from_lparam = self._make_lparam(from_x, from_y)
            result = self.user32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, from_lparam)
            if not result:
                return InputResult(
                    success=False,
                    method_used=InputMethod.POST_MESSAGE,
                    error="Failed to send mouse down for drag"
                )
            
            # MOVE (interpolation)
            for i in range(1, steps + 1):
                progress = i / steps
                curr_x = int(from_x + (to_x - from_x) * progress)
                curr_y = int(from_y + (to_y - from_y) * progress)
                move_lparam = self._make_lparam(curr_x, curr_y)
                self.user32.PostMessageW(hwnd, WM_MOUSEMOVE, MK_LBUTTON, move_lparam)
                await asyncio.sleep(0.01)
            
            # UP
            to_lparam = self._make_lparam(to_x, to_y)
            result = self.user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, to_lparam)
            if not result:
                return InputResult(
                    success=False,
                    method_used=InputMethod.POST_MESSAGE,
                    error="Failed to send mouse up for drag"
                )
            
            return InputResult(success=True, method_used=InputMethod.POST_MESSAGE)
            
        except Exception as e:
            return InputResult(
                success=False,
                method_used=InputMethod.POST_MESSAGE,
                error=str(e)
            )
    
    async def scroll(self, hwnd: int, direction: str, amount: int = 3) -> InputResult:
        """
        Scroll operation - Use WM_MOUSEWHEEL
        
        Args:
            hwnd: Window handle
            direction: "up", "down", "left", "right"
            amount: Number of lines to scroll (120 units per line)
        """
        try:
            WM_MOUSEWHEEL = 0x020A
            WM_MOUSEHWHEEL = 0x020E  # Horizontal scroll
            
            # Calculate scroll amount (120 units per line)
            WHEEL_DELTA = 120
            
            if direction in ("up", "down"):
                msg = WM_MOUSEWHEEL
                delta = WHEEL_DELTA * amount if direction == "up" else -WHEEL_DELTA * amount
            elif direction in ("left", "right"):
                msg = WM_MOUSEHWHEEL
                delta = -WHEEL_DELTA * amount if direction == "left" else WHEEL_DELTA * amount
            else:
                return InputResult(
                    success=False,
                    method_used=InputMethod.POST_MESSAGE,
                    error=f"Invalid scroll direction: {direction}"
                )
            
            # wParam: HIWORD = wheel delta, LOWORD = key state
            wparam = (delta & 0xFFFF) << 16
            
            # lParam: Mouse position (window center)
            import ctypes
            from ctypes import wintypes
            rect = wintypes.RECT()
            self.user32.GetClientRect(hwnd, ctypes.byref(rect))
            center_x = (rect.right - rect.left) // 2
            center_y = (rect.bottom - rect.top) // 2
            lparam = (center_y << 16) | (center_x & 0xFFFF)
            
            result = self.user32.PostMessageW(hwnd, msg, wparam, lparam)
            
            if result:
                return InputResult(success=True, method_used=InputMethod.POST_MESSAGE)
            else:
                return InputResult(
                    success=False,
                    method_used=InputMethod.POST_MESSAGE,
                    error="Failed to send scroll message"
                )
                
        except Exception as e:
            return InputResult(
                success=False,
                method_used=InputMethod.POST_MESSAGE,
                error=str(e)
            )
    
    async def hotkey(self, hwnd: int, keys: str) -> InputResult:
        """
        Hotkey operation
        
        Args:
            hwnd: Window handle
            keys: Hotkey string, e.g. "ctrl+c", "alt+tab", "ctrl+shift+s"
        """
        try:
            # Parse hotkey
            key_names = [k.strip().lower() for k in keys.split("+")]
            
            # Virtual key code mapping
            VK_MAP = {
                "ctrl": 0x11, "control": 0x11,
                "alt": 0x12, "menu": 0x12,
                "shift": 0x10,
                "win": 0x5B, "windows": 0x5B,
                "tab": 0x09,
                "enter": 0x0D, "return": 0x0D,
                "esc": 0x1B, "escape": 0x1B,
                "space": 0x20,
                "backspace": 0x08, "back": 0x08,
                "delete": 0x2E, "del": 0x2E,
                "insert": 0x2D, "ins": 0x2D,
                "home": 0x24,
                "end": 0x23,
                "pageup": 0x21, "pgup": 0x21,
                "pagedown": 0x22, "pgdn": 0x22,
                "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
                "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
                "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
                "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
            }
            
            # Letters and numbers
            for c in "abcdefghijklmnopqrstuvwxyz":
                VK_MAP[c] = ord(c.upper())
            for c in "0123456789":
                VK_MAP[c] = ord(c)
            
            # Convert to virtual key codes
            vk_codes = []
            for key in key_names:
                if key in VK_MAP:
                    vk_codes.append(VK_MAP[key])
                else:
                    return InputResult(
                        success=False,
                        method_used=InputMethod.POST_MESSAGE,
                        error=f"Unknown key: {key}"
                    )
            
            # Press all keys down
            for vk in vk_codes:
                self.user32.PostMessageW(hwnd, WM_KEYDOWN, vk, 0)
                await asyncio.sleep(0.02)
            
            # Release all keys (reverse order)
            for vk in reversed(vk_codes):
                self.user32.PostMessageW(hwnd, WM_KEYUP, vk, 0)
                await asyncio.sleep(0.02)
            
            return InputResult(success=True, method_used=InputMethod.POST_MESSAGE)
            
        except Exception as e:
            return InputResult(
                success=False,
                method_used=InputMethod.POST_MESSAGE,
                error=str(e)
            )
    
    async def key_press_by_name(self, hwnd: int, key_name: str) -> InputResult:
        """
        Key press operation (by name)
        
        Args:
            hwnd: Window handle
            key_name: Key name, e.g. "enter", "tab", "escape"
        """
        # Use hotkey method to handle single key
        return await self.hotkey(hwnd, key_name)
    
    @staticmethod
    def _make_lparam(x: int, y: int) -> int:
        """Construct lParam: x in low word, y in high word"""
        return (y << 16) | (x & 0xFFFF)


class InputSimulator:
    """Input simulator - Handle message timing (simplified)"""
    
    def __init__(self):
        self.controller = WindowInputController()
    
    async def click(self, hwnd: int, x: int, y: int) -> InputResult:
        """Single click"""
        return await self.controller.click(hwnd, x, y)
    
    async def double_click(self, hwnd: int, x: int, y: int) -> InputResult:
        """Double click"""
        return await self.controller.double_click(hwnd, x, y)
    
    async def type_text(self, hwnd: int, text: str) -> InputResult:
        """Type text"""
        return await self.controller.type_text(hwnd, text)
    
    async def drag(
        self, hwnd: int, 
        from_x: int, from_y: int, 
        to_x: int, to_y: int
    ) -> InputResult:
        """拖拽"""
        return await self.controller.drag(hwnd, from_x, from_y, to_x, to_y)


# Export
__all__ = [
    'InputMethod',
    'InputResult', 
    'WindowInputController',
    'InputSimulator',
]
