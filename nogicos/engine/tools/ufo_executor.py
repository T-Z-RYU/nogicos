# -*- coding: utf-8 -*-
"""
UFO Executor - Wraps Microsoft UFO as desktop automation backend

UFO (UI-Focused Agent) is Microsoft's open-source Windows UI automation framework,
using visual understanding + LLM to execute complex desktop operation tasks.

Integration methods:
1. As tool call: execute_desktop_task("send hello to WeChat")
2. As backend replacement: fully use UFO for all desktop operations

Advantages:
- Visual understanding: automatically identifies UI element positions
- Multi-step reasoning: automatically decomposes complex tasks
- Error recovery: auto-retry on failures
- Generality: works with any Windows application
"""

import os
import sys
import json
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("nogicos.tools.ufo_executor")

# UFO installation path - prioritize environment variable, otherwise check common locations
def _find_ufo_path() -> Path:
    """Find UFO installation path"""
    # 1. Environment variable
    if os.environ.get("UFO_PATH"):
        return Path(os.environ["UFO_PATH"])
    
    # 2. Common installation locations
    candidates = [
        Path.home() / "Desktop" / "UFO",
        Path.home() / "UFO",
        Path(r"C:\UFO"),
        Path(r"D:\UFO"),
    ]
    for p in candidates:
        if p.exists():
            return p
    
    # 3. Default fallback
    return Path.home() / "Desktop" / "UFO"

UFO_PATH = _find_ufo_path()
PYTHON_PATH = Path(sys.executable)  # Use current Python


class TaskStatus(Enum):
    """Task status"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    PENDING = "pending"


@dataclass
class UFOResult:
    """UFO execution result"""
    status: TaskStatus
    message: str
    steps: List[Dict[str, Any]]
    cost: float = 0.0
    duration: float = 0.0
    log_path: Optional[str] = None


class UFOExecutor:
    """
    UFO Executor - Wraps UFO command line calls
    
    Usage example:
    ```python
    executor = UFOExecutor()
    
    # Sync call
    result = executor.execute("send hello to WeChat")
    
    # Async call
    result = await executor.execute_async("open notepad and type hello")
    ```
    """
    
    def __init__(
        self,
        ufo_path: Path = UFO_PATH,
        python_path: Path = PYTHON_PATH,
        timeout: int = 300,  # 5 minute timeout
    ):
        self.ufo_path = ufo_path
        self.python_path = python_path
        self.timeout = timeout
        
        # Verify UFO installation
        if not self._verify_installation():
            raise RuntimeError(f"UFO not found at {ufo_path}")
    
    def _verify_installation(self) -> bool:
        """Verify UFO installation"""
        return (
            self.ufo_path.exists() and
            (self.ufo_path / "ufo" / "__main__.py").exists() and
            self.python_path.exists()
        )
    
    def _build_command(self, task: str) -> List[str]:
        """Build UFO command"""
        return [
            str(self.python_path),
            "-m", "ufo",
            "--request", task,
        ]
    
    def _parse_result(self, stdout: str, stderr: str, returncode: int, duration: float) -> UFOResult:
        """Parse UFO output"""
        # Find latest log directory
        logs_dir = self.ufo_path / "logs"
        if logs_dir.exists():
            log_dirs = sorted(logs_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            if log_dirs:
                latest_log = log_dirs[0]
                result_file = latest_log / "result.json"
                response_file = latest_log / "response.log"
                
                # Try to read result
                steps = []
                if response_file.exists():
                    try:
                        with open(response_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.strip():
                                    steps.append(json.loads(line))
                    except:
                        pass
                
                # Determine status
                if returncode == 0:
                    status = TaskStatus.SUCCESS
                    message = "Task completed successfully"
                elif "FINISH" in stdout:
                    status = TaskStatus.SUCCESS
                    message = "Task finished"
                else:
                    status = TaskStatus.FAILED
                    message = stderr or "Task failed"
                
                return UFOResult(
                    status=status,
                    message=message,
                    steps=steps,
                    duration=duration,
                    log_path=str(latest_log),
                )
        
        # Unable to find logs
        return UFOResult(
            status=TaskStatus.FAILED if returncode != 0 else TaskStatus.SUCCESS,
            message=stderr or stdout or "Unknown result",
            steps=[],
            duration=duration,
        )
    
    def execute(self, task: str) -> UFOResult:
        """
        Synchronously execute desktop task
        
        Args:
            task: Natural language task description, e.g. "send hello to WeChat"
            
        Returns:
            UFOResult: Execution result
        """
        import time
        start_time = time.time()
        
        cmd = self._build_command(task)
        logger.info(f"[UFO] Executing: {task}")
        
        try:
            env = os.environ.copy()
            # Set UTF-8 encoding to avoid Windows GBK encoding issues
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            env["PYTHONLEGACYWINDOWSSTDIO"] = "1"
            # Disable colorama to avoid emoji encoding issues
            env["NO_COLOR"] = "1"
            env["TERM"] = "dumb"
            
            result = subprocess.run(
                cmd,
                cwd=str(self.ufo_path),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
                encoding='utf-8',
                errors='replace',
            )
            
            duration = time.time() - start_time
            return self._parse_result(
                result.stdout, 
                result.stderr, 
                result.returncode,
                duration
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.error(f"[UFO] Task timed out after {self.timeout}s")
            return UFOResult(
                status=TaskStatus.TIMEOUT,
                message=f"Task timed out after {self.timeout} seconds",
                steps=[],
                duration=duration,
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[UFO] Execution error: {e}")
            return UFOResult(
                status=TaskStatus.FAILED,
                message=str(e),
                steps=[],
                duration=duration,
            )
    
    async def execute_async(self, task: str) -> UFOResult:
        """
        Asynchronously execute desktop task
        
        Args:
            task: Natural language task description
            
        Returns:
            UFOResult: Execution result
        """
        import time
        start_time = time.time()
        
        cmd = self._build_command(task)
        logger.info(f"[UFO] Executing async: {task}")
        
        try:
            env = os.environ.copy()
            # Set UTF-8 encoding to avoid Windows GBK encoding issues
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            env["PYTHONLEGACYWINDOWSSTDIO"] = "1"
            # Disable colorama to avoid emoji encoding issues
            env["NO_COLOR"] = "1"
            env["TERM"] = "dumb"
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.ufo_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout
            )
            
            duration = time.time() - start_time
            return self._parse_result(
                stdout.decode('utf-8', errors='ignore'),
                stderr.decode('utf-8', errors='ignore'),
                proc.returncode,
                duration
            )
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            proc.kill()
            logger.error(f"[UFO] Task timed out after {self.timeout}s")
            return UFOResult(
                status=TaskStatus.TIMEOUT,
                message=f"Task timed out after {self.timeout} seconds",
                steps=[],
                duration=duration,
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[UFO] Execution error: {e}")
            return UFOResult(
                status=TaskStatus.FAILED,
                message=str(e),
                steps=[],
                duration=duration,
            )


# ============================================================================
# Convenience functions - for direct NogicOS Agent calls
# ============================================================================

_executor: Optional[UFOExecutor] = None

def get_executor() -> UFOExecutor:
    """Get global UFO executor instance"""
    global _executor
    if _executor is None:
        _executor = UFOExecutor()
    return _executor


def execute_desktop_task(task: str) -> Dict[str, Any]:
    """
    Execute desktop automation task (for Agent tool calls)
    
    Args:
        task: Natural language task description
        
    Returns:
        Dictionary containing execution result
        
    Example:
        >>> result = execute_desktop_task("send hello to WeChat")
        >>> print(result["status"])  # "success" or "failed"
    """
    executor = get_executor()
    result = executor.execute(task)
    
    return {
        "status": result.status.value,
        "message": result.message,
        "steps_count": len(result.steps),
        "duration": result.duration,
        "log_path": result.log_path,
    }


async def execute_desktop_task_async(task: str) -> Dict[str, Any]:
    """Async version of desktop task execution"""
    executor = get_executor()
    result = await executor.execute_async(task)
    
    return {
        "status": result.status.value,
        "message": result.message,
        "steps_count": len(result.steps),
        "duration": result.duration,
        "log_path": result.log_path,
    }


# ============================================================================
# Tool definition - for LangChain/LangGraph use
# ============================================================================

TOOL_DEFINITION = {
    "name": "execute_desktop_task",
    "description": """Execute a desktop automation task using natural language.
    
This tool uses Microsoft UFO (UI-Focused Agent) to perform complex desktop operations.
It can interact with any Windows application by understanding the UI visually.

Examples:
- "send hello to WeChat"
- "open notepad and type hello world"
- "click the Send button in WhatsApp"
- "search for python in Windows start menu"
- "close the current browser tab"

The tool will automatically:
1. Take screenshots to understand the current state
2. Identify UI elements and their positions
3. Execute the required actions (click, type, etc.)
4. Verify the result

Args:
    task: Natural language description of the task to perform
    
Returns:
    Result dictionary with status, message, and execution details
""",
    "parameters": {
        "type": "object",
        "properties": {
            "task": {
                "type": "string",
                "description": "Natural language task description"
            }
        },
        "required": ["task"]
    }
}


# ============================================================================
# NogicOS Tool Registration
# ============================================================================

def register_ufo_tools(registry):
    """
    Register UFO desktop automation tools to NogicOS Registry.
    
    Args:
        registry: ToolRegistry instance
    """
    from .base import ToolCategory
    
    @registry.action(
        description="""Execute a desktop automation task using Microsoft UFO (AI-powered).

UFO uses visual understanding + LLM to perform multi-step desktop operations automatically.
It automatically uses the window that the user has connected via APP CONNECTOR.

⚡ **When to use this tool:**
- Send messages in chat apps (WeChat, WhatsApp, Telegram, etc.)
- Any desktop UI interaction task
- When you need to click, type, or interact with applications

📋 **Examples:**
- "send hello" → Sends "hello" in the connected chat app
- "type test123 and press enter" → Types and sends in connected window
- "click the Send button" → Finds and clicks Send button

⚠️ **Notes:**
- Automatically targets the window connected via APP CONNECTOR
- Takes 30-90 seconds per task (LLM reasoning + screenshot analysis)

Args:
    task: Natural language description of what you want to do
    hwnd: (Optional) Target window handle - used to get window info for context
    
Returns:
    Result with status ("success"/"failed"/"timeout"), message, and execution details""",
        category=ToolCategory.LOCAL,
    )
    async def ufo_desktop_task(task: str, hwnd: Optional[int] = None) -> Dict[str, Any]:
        """Execute a desktop task using Microsoft UFO, with Hook context awareness."""
        
        # Use the user's task directly - no hardcoded override
        enhanced_task = task
        
        # Try to add context about the connected app
        try:
            from ..context import get_context_store
            store = get_context_store()
            ctx = store.get_context_for_agent()
            connected_windows = ctx.get("connected_windows", [])
            
            if connected_windows:
                win = connected_windows[0]
                app_name = win.get('app_name', '') or win.get('app_display_name', '') or ''
                app_lower = app_name.lower()
                
                # Add app context if not already in task
                if app_name and app_name.lower() not in task.lower():
                    if 'chrome' in app_lower or 'browser' in app_lower:
                        enhanced_task = f"In Chrome browser: {task}"
                    elif 'whatsapp' in app_lower:
                        enhanced_task = f"In WhatsApp: {task}"
                    elif 'wechat' in app_lower or 'weixin' in app_lower:
                        enhanced_task = f"In WeChat: {task}"
                    else:
                        enhanced_task = f"In {app_name}: {task}"
                
                logger.info(f"[UFO Tool] Enhanced task with app context: {enhanced_task}")
        except Exception as e:
            logger.warning(f"[UFO Tool] Could not get Hook context: {e}")
        
        logger.info(f"[UFO Tool] Executing: {enhanced_task}")
        
        try:
            executor = get_executor()
        except RuntimeError as e:
            # UFO not installed
            logger.error(f"[UFO Tool] UFO not installed: {e}")
            return {
                "success": False,
                "status": "not_installed",
                "message": f"UFO is not installed or not found. Error: {e}. Please install UFO from https://github.com/microsoft/UFO",
                "steps_count": 0,
                "duration_seconds": 0,
            }
        
        try:
            result = await executor.execute_async(enhanced_task)
            
            return {
                "success": result.status == TaskStatus.SUCCESS,
                "status": result.status.value,
                "message": result.message,
                "steps_count": len(result.steps),
                "duration_seconds": round(result.duration, 1),
                "log_path": result.log_path,
            }
        except Exception as e:
            logger.error(f"[UFO Tool] Execution error: {e}")
            import traceback
            return {
                "success": False,
                "status": "error",
                "message": f"UFO execution failed: {str(e)[:200]}",
                "steps_count": 0,
                "duration_seconds": 0,
            }
    
    logger.info("[UFO] UFO desktop tools registered")


# ============================================================================
# Test
# ============================================================================

if __name__ == "__main__":
    # Simple test
    print("Testing UFO Executor...")
    
    try:
        executor = UFOExecutor()
        print("✓ UFO installation verified")
        
        # Test simple task
        result = executor.execute("click the start button")
        print(f"Status: {result.status.value}")
        print(f"Message: {result.message}")
        print(f"Duration: {result.duration:.2f}s")
        
    except Exception as e:
        print(f"✗ Error: {e}")
