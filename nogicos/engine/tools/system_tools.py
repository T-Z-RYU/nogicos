# -*- coding: utf-8 -*-
"""
System Tools - 任务控制Tool

提供System级别的任务控制功能:
- set_task_status: Set任务State (参考 ByteBot)
- get_system_info: GetSystemInfo
- list_windows: Column出所有Window
- find_window: FindWindow
"""

import asyncio
import ctypes
from ctypes import wintypes
import platform
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json as _json
from pathlib import Path as _Path
import time

logger = logging.getLogger("nogicos.tools.system_tools")

# #region agent log helper (debug mode)
_DEBUG_LOG_PATH = _Path(r"c:\Users\WIN\Desktop\Cursor Project\.cursor\debug.log")

def _sys_dbg_log(hypothesis_id: str, location: str, message: str, data: dict):
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
        with _DEBUG_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(_json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass
# #endregion


@dataclass
class TaskStatus:
    """任务State"""
    status: str  # "completed" | "needs_help" | "in_progress" | "failed"
    description: str
    progress: float = 0.0  # 0.0 - 1.0


class SystemTools:
    """SystemTool"""
    
    def __init__(self):
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self._setup_functions()
        self._current_task_status: Optional[TaskStatus] = None
    
    def _setup_functions(self):
        """Set Windows API FunctionSignature"""
        # EnumWindows
        self.WNDENUMPROC = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
        )
        self.user32.EnumWindows.argtypes = [self.WNDENUMPROC, wintypes.LPARAM]
        self.user32.EnumWindows.restype = wintypes.BOOL
        
        # GetWindowTextW
        self.user32.GetWindowTextW.argtypes = [
            wintypes.HWND, wintypes.LPWSTR, ctypes.c_int
        ]
        self.user32.GetWindowTextW.restype = ctypes.c_int
        
        # GetWindowTextLengthW
        self.user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        self.user32.GetWindowTextLengthW.restype = ctypes.c_int
        
        # IsWindowVisible
        self.user32.IsWindowVisible.argtypes = [wintypes.HWND]
        self.user32.IsWindowVisible.restype = wintypes.BOOL
        
        # GetClassName
        self.user32.GetClassNameW.argtypes = [
            wintypes.HWND, wintypes.LPWSTR, ctypes.c_int
        ]
        self.user32.GetClassNameW.restype = ctypes.c_int
        
        # FindWindowW
        self.user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        self.user32.FindWindowW.restype = wintypes.HWND
    
    def set_task_status(
        self, 
        status: str, 
        description: str,
        progress: float = 0.0
    ) -> TaskStatus:
        """
        Set任务State - 参考 ByteBot
        
        Args:
            status: "completed" | "needs_help" | "in_progress" | "failed"
            description: State描述
            progress: 进度 (0.0 - 1.0)
            
        Returns:
            TaskStatus Object
        """
        valid_statuses = ["completed", "needs_help", "in_progress", "failed"]
        if status not in valid_statuses:
            status = "in_progress"
        
        self._current_task_status = TaskStatus(
            status=status,
            description=description,
            progress=min(max(progress, 0.0), 1.0)
        )
        
        logger.info(f"Task status: {status} - {description} ({progress*100:.0f}%)")
        return self._current_task_status
    
    def get_task_status(self) -> Optional[TaskStatus]:
        """Get当Before任务State"""
        return self._current_task_status
    
    def get_system_info(self) -> Dict[str, Any]:
        """GetSystemInfo"""
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
        
        # Windows specific info
        if platform.system() == "Windows":
            info["windows_edition"] = platform.win32_edition() if hasattr(platform, 'win32_edition') else "N/A"
            
            # Screen info
            info["screen_width"] = self.user32.GetSystemMetrics(0)  # SM_CXSCREEN
            info["screen_height"] = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN
            info["virtual_screen_width"] = self.user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
            info["virtual_screen_height"] = self.user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
            info["monitor_count"] = self.user32.GetSystemMetrics(80)  # SM_CMONITORS
        
        return info
    
    def list_windows(self, visible_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all windows
        
        Args:
            visible_only: Whether to list only visible windows
            
        Returns:
            List of windows
        """
        windows = []
        
        def enum_callback(hwnd, lparam):
            # Check visibility
            if visible_only and not self.user32.IsWindowVisible(hwnd):
                return True
            
            # Get title
            length = self.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True  # Skip windows without title
            
            buffer = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value
            
            # Get class name
            class_buffer = ctypes.create_unicode_buffer(256)
            self.user32.GetClassNameW(hwnd, class_buffer, 256)
            class_name = class_buffer.value
            
            windows.append({
                "hwnd": hwnd,
                "title": title,
                "class_name": class_name,
            })
            
            return True
        
        try:
            # [Segfault fix] Must keep callback instance reference, otherwise GC causes crash
            callback_instance = self.WNDENUMPROC(enum_callback)
            self.user32.EnumWindows(callback_instance, 0)
        except Exception as e:
            logger.error(f"EnumWindows failed: {e}")
        
        # Debug log: record top few windows
        try:
            top = windows[:5]
            _sys_dbg_log(
                hypothesis_id="H4",
                location="system_tools:list_windows",
                message="Enumerated windows",
                data={
                    "count": len(windows),
                    "top": [{"hwnd": w.get("hwnd"), "title": w.get("title"), "class": w.get("class_name")} for w in top],
                },
            )
        except Exception:
            pass

        return windows
    
    def find_window(
        self,
        title: Optional[str] = None,
        class_name: Optional[str] = None,
        partial_match: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find window
        
        Args:
            title: Window title (supports partial matching)
            class_name: Window class name (supports partial matching)
            partial_match: Whether to use partial matching
            
        Returns:
            List of matching windows
        """
        # Exact match
        if not partial_match and title:
            hwnd = self.user32.FindWindowW(
                class_name if class_name else None,
                title
            )
            if hwnd:
                return [{"hwnd": hwnd, "title": title, "class_name": class_name or ""}]
            return []
        
        # Partial match
        all_windows = self.list_windows(visible_only=True)
        results = []
        
        for win in all_windows:
            match = True
            
            if title:
                if partial_match:
                    match = match and title.lower() in win["title"].lower()
                else:
                    match = match and win["title"] == title
            
            if class_name:
                if partial_match:
                    match = match and class_name.lower() in win["class_name"].lower()
                else:
                    match = match and win["class_name"] == class_name
            
            if match:
                results.append(win)
        
        return results
    
    async def wait_for_window(
        self, 
        title: str, 
        timeout: float = 30.0,
        interval: float = 0.5
    ) -> Optional[int]:
        """
        Wait for window to appear
        
        Args:
            title: Window title (partial match)
            timeout: Timeout in seconds
            interval: Check interval in seconds
            
        Returns:
            Window handle, or None (timeout)
        """
        import time
        start = time.time()
        
        while time.time() - start < timeout:
            windows = self.find_window(title=title, partial_match=True)
            if windows:
                return windows[0]["hwnd"]
            await asyncio.sleep(interval)
        
        return None


# Global singleton
_global_system_tools: Optional[SystemTools] = None


def get_system_tools() -> SystemTools:
    """Get global system tools"""
    global _global_system_tools
    if _global_system_tools is None:
        _global_system_tools = SystemTools()
    return _global_system_tools


def register_system_tools(registry):
    """Register system tools to Registry"""
    from .base import ToolCategory
    
    system_tools = get_system_tools()
    
    @registry.action(
        description="""Set task status - for reporting task progress.

Args:
- status: Status value
  - "completed": Task completed
  - "needs_help": Needs user help
  - "in_progress": In progress
  - "failed": Task failed
- description: Status description

Examples:
- set_task_status("completed", "Successfully opened browser and navigated to target page")
- set_task_status("needs_help", "Cannot find login button, please confirm page is correct")""",
        category=ToolCategory.SYSTEM,
    )
    async def set_task_status(status: str, description: str) -> str:
        result = system_tools.set_task_status(status, description)
        return f"Status set to {result.status}: {result.description}"
    
    @registry.action(
        description="""Get system information.

Returns: OS, screen resolution, monitor count and other info""",
        category=ToolCategory.SYSTEM,
    )
    async def get_system_info() -> str:
        import json
        info = system_tools.get_system_info()
        return json.dumps(info, indent=2, ensure_ascii=False)
    
    @registry.action(
        description="""List all visible windows.

Returns: Window list containing hwnd, title, class name""",
        category=ToolCategory.SYSTEM,
    )
    async def list_windows() -> str:
        import json
        windows = system_tools.list_windows(visible_only=True)
        # Only return first 20
        if len(windows) > 20:
            windows = windows[:20]
            windows.append({"note": f"... and {len(windows) - 20} more"})
        return json.dumps(windows, indent=2, ensure_ascii=False)
    
    @registry.action(
        description="""Find window.

Args:
- title: Window title (supports partial matching)
- class_name: Window class name (optional)

Returns: List of matching windows""",
        category=ToolCategory.SYSTEM,
    )
    async def find_window(
        title: str, 
        class_name: Optional[str] = None
    ) -> str:
        import json
        windows = system_tools.find_window(
            title=title, 
            class_name=class_name,
            partial_match=True
        )
        return json.dumps(windows, indent=2, ensure_ascii=False)
    
    @registry.action(
        description="""WaitWindow出现。

Argument:
- title: Windowtitle (部分Match)
- timeout: TimeoutTime (Second，Default 30)

Return: Window句柄，或TimeoutError""",
        category=ToolCategory.SYSTEM,
    )
    async def wait_for_window(
        title: str, 
        timeout: float = 30.0
    ) -> str:
        hwnd = await system_tools.wait_for_window(title, timeout)
        if hwnd:
            return f"Found window: hwnd={hwnd}"
        else:
            return f"Timeout: Window '{title}' not found after {timeout}s"
    
    @registry.action(
        description="""Request user confirmation ONLY for truly destructive actions.

USE SPARINGLY - Only for:
- Deleting files permanently
- Making purchases or payments
- Sending messages to EXTERNAL contacts (not team notifications)

DO NOT use for:
- Filling forms (user already requested this)
- Team notifications via WhatsApp
- Reading files
- Normal workflow execution

For "Complete YC Application Flow" - DO NOT request confirmation, just execute.

Args:
    action_description: What you're about to do
    content_preview: The content involved

Returns:
    "confirmed" or "cancelled" """,
        category=ToolCategory.SYSTEM,
    )
    async def request_confirmation(
        action_description: str,
        content_preview: str
    ) -> str:
        """Request user confirmation via UI dialog."""
        import uuid
        
        # Get the status server from registry context (set by hive_server)
        status_server = registry.get_context("status_server")
        
        if not status_server:
            logger.warning("[Confirmation] No status server available, auto-confirming")
            return "confirmed"
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Send confirmation request to frontend
        logger.info(f"[Confirmation] Requesting user confirmation: {action_description}")
        
        try:
            # Use the status server's confirmation mechanism
            confirmed = await status_server.stream_confirm(
                request_id=request_id,
                action=action_description,
                content=content_preview,
                timeout=120  # 2 minutes to respond
            )
            
            if confirmed:
                logger.info(f"[Confirmation] User confirmed: {action_description}")
                return "confirmed"
            else:
                logger.info(f"[Confirmation] User cancelled: {action_description}")
                return "cancelled"
                
        except asyncio.TimeoutError:
            logger.warning(f"[Confirmation] Timeout waiting for user response")
            return "cancelled"
        except Exception as e:
            logger.error(f"[Confirmation] Error: {e}")
            return "cancelled"
    
    logger.info("[SystemTools] All system tools registered")


# Exports
__all__ = [
    'TaskStatus',
    'SystemTools',
    'get_system_tools',
    'register_system_tools',
]
