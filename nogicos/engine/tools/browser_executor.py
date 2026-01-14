# -*- coding: utf-8 -*-
"""
NogicOS Browser Executor - 基于 Browser Use 的浏览器Auto化

Integration Browser Use 到 NogicOS，Disable所有第三方品牌标识
"""

# Ensure user site-packages is in path (for browser-use installed via pip --user)
import sys
import site
_user_site = site.getusersitepackages()
if _user_site and _user_site not in sys.path:
    sys.path.insert(0, _user_site)

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BrowserTaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class BrowserTaskResult:
    status: BrowserTaskStatus
    message: str
    extracted_content: Optional[str] = None
    duration: float = 0.0
    steps_count: int = 0


class NogicBrowserExecutor:
    """
    NogicOS 浏览器Execute器 - 封装 Browser Use，移除所有品牌标识
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._agent = None
        self._browser_session = None
        self._initialized = False
        self._branding_disabled = False
    
    def _disable_branding(self):
        """Disable all Browser Use branding and animations"""
        if self._branding_disabled:
            return
            
        try:
            # Disable DVD screensaver animation on about:blank page
            from browser_use.browser.watchdogs import aboutblank_watchdog
            
            # Replace animation injection method with noop
            async def _noop_animation(*args, **kwargs):
                pass
            
            aboutblank_watchdog.AboutBlankWatchdog._show_dvd_screensaver_loading_animation_cdp = _noop_animation
            aboutblank_watchdog.AboutBlankWatchdog._show_dvd_screensaver_on_about_blank_tabs = _noop_animation
            
            logger.info("[NogicBrowser] Disabled Browser Use branding (DVD screensaver)")
            self._branding_disabled = True
            
        except Exception as e:
            logger.warning(f"[NogicBrowser] Could not disable branding: {e}")
        
    async def _ensure_initialized(self):
        """Lazy initialization"""
        if self._initialized:
            return
            
        try:
            # Import Browser Use components
            from browser_use import Agent, ChatAnthropic
            from browser_use.browser import BrowserProfile, BrowserSession
            
            # === Disable Browser Use branding ===
            self._disable_branding()
            
            # Set API Key
            if self.api_key:
                os.environ["ANTHROPIC_API_KEY"] = self.api_key
            
            # Create clean BrowserProfile - disable all visual effects
            self._profile = BrowserProfile(
                headless=False,
                # Disable element highlighting
                highlight_elements=False,
                # Disable security restrictions for automation
                disable_security=True,
            )
            
            # Create LLM
            self._llm = ChatAnthropic(
                model='claude-sonnet-4-20250514',
                temperature=0.0
            )
            
            self._initialized = True
            logger.info("[NogicBrowser] Browser executor initialized (clean mode)")
            
        except ImportError as e:
            logger.error(f"[NogicBrowser] Failed to import browser-use: {e}")
            raise RuntimeError("browser-use not installed. Run: pip install browser-use")
    
    async def execute(
        self, 
        task: str, 
        start_url: Optional[str] = None,
        cdp_url: Optional[str] = None,
        timeout: int = 120
    ) -> BrowserTaskResult:
        """
        Execute browser task
        
        Args:
            task: Task description
            start_url: Starting URL (if launching new browser)
            cdp_url: CDP URL to connect to existing Chrome (e.g. http://localhost:9222)
            timeout: Timeout in seconds
        """
        import time
        start_time = time.time()
        browser_session = None  # Initialize before try block
        
        try:
            await self._ensure_initialized()
            
            from browser_use import Agent
            from browser_use.browser import BrowserSession, BrowserProfile
            
            # Decide connection method based on CDP URL
            if cdp_url:
                # Connect to existing Chrome (via CDP)
                logger.info(f"[NogicBrowser] Connecting to existing browser via CDP: {cdp_url}")
                cdp_profile = BrowserProfile(
                    cdp_url=cdp_url,
                    headless=False,
                    highlight_elements=False,
                )
                browser_session = BrowserSession(browser_profile=cdp_profile)
                full_task = task  # No navigation needed, user is already on target page
            else:
                # Launch new browser
                browser_session = BrowserSession(browser_profile=self._profile)
                full_task = task
                if start_url:
                    full_task = f"First navigate to {start_url}, then: {task}"
            
            # Create Agent
            agent = Agent(
                task=full_task,
                llm=self._llm,
                browser_session=browser_session,
            )
            
            logger.info(f"[NogicBrowser] Executing task: {task[:50]}...")
            
            # Execute task
            result = await asyncio.wait_for(
                agent.run(),
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            # Parse result (Browser Use 0.11.x API)
            success = result.is_successful() if hasattr(result, 'is_successful') else True
            extracted = result.extracted_content() if hasattr(result, 'extracted_content') else ""
            final = result.final_result() if hasattr(result, 'final_result') else None
            steps = result.number_of_steps() if hasattr(result, 'number_of_steps') else 0
            
            message = final or extracted or "Task completed"
            if isinstance(message, str) and len(message) > 500:
                message = message[:500] + "..."
            
            return BrowserTaskResult(
                status=BrowserTaskStatus.SUCCESS if success else BrowserTaskStatus.FAILED,
                message=str(message),
                extracted_content=str(extracted) if extracted else None,
                duration=duration,
                steps_count=steps
            )
            
        except asyncio.TimeoutError:
            return BrowserTaskResult(
                status=BrowserTaskStatus.TIMEOUT,
                message=f"Task timed out after {timeout}s",
                duration=timeout
            )
        except Exception as e:
            logger.error(f"[NogicBrowser] Task failed: {e}")
            return BrowserTaskResult(
                status=BrowserTaskStatus.FAILED,
                message=str(e),
                duration=time.time() - start_time
            )
        finally:
            # Clean up browser session
            if browser_session:
                try:
                    await browser_session.close()
                except:
                    pass


# Global singleton
_executor: Optional[NogicBrowserExecutor] = None


def get_browser_executor(api_key: Optional[str] = None) -> NogicBrowserExecutor:
    """Get浏览器Execute器Singleton"""
    global _executor
    if _executor is None:
        _executor = NogicBrowserExecutor(api_key)
    return _executor


def register_browser_executor_tools(registry):
    """
    Register Browser Use 浏览器Auto化Tool到 NogicOS Registry
    （AI 视觉驱动，用于复杂webpage操作）
    
    DefaultConnect到已有的 Chrome（CDP），不StartNew浏览器
    """
    from .base import ToolCategory
    
    # Default CDP URL - connect to user's already open Chrome
    DEFAULT_CDP_URL = "http://localhost:9222"
    
    @registry.action(
        description="""Execute a browser automation task using AI vision on the ALREADY OPEN Chrome browser.
        
IMPORTANT: This tool connects to the user's existing Chrome browser (via CDP).
It does NOT open a new browser window.
        
Use this for:
- Filling forms on the currently open page
- Clicking buttons and links
- Extracting information from web pages
- Any task requiring browser interaction

Args:
    task: Natural language description of what to do in the browser
    
Returns:
    Result with success status, extracted content, and execution details
    
Note: Chrome must be started with --remote-debugging-port=9222""",
        category=ToolCategory.LOCAL,
    )
    async def browser_task(task: str) -> Dict[str, Any]:
        """Execute a browser task on the already open Chrome browser."""
        logger.info(f"[Browser Tool] Executing on existing Chrome: {task}")
        
        try:
            executor = get_browser_executor()
            
            # Default: connect to existing browser via CDP, don't launch new browser
            result = await executor.execute(
                task=task,
                cdp_url=DEFAULT_CDP_URL  # Connect to existing Chrome
            )
            
            return {
                "success": result.status == BrowserTaskStatus.SUCCESS,
                "status": result.status.value,
                "message": result.message,
                "extracted_content": result.extracted_content,
                "steps_count": result.steps_count,
                "duration_seconds": round(result.duration, 1),
            }
        except Exception as e:
            logger.error(f"[Browser Tool] Error: {e}")
            return {
                "success": False,
                "status": "error",
                "message": str(e),
            }
    
    logger.info("[NogicBrowser] Browser tools registered (CDP mode - connects to existing Chrome)")


# Test function
async def test_browser():
    """FastTest浏览器Execute器"""
    import sys
    sys.path.insert(0, r"C:\Users\WIN\Desktop\Cursor Project\nogicos")
    from api_keys import ANTHROPIC_API_KEY
    
    executor = NogicBrowserExecutor(api_key=ANTHROPIC_API_KEY)
    result = await executor.execute(
        task="Search for 'NogicOS' on Google",
        start_url="https://google.com"
    )
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(test_browser())
