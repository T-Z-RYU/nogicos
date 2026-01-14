# -*- coding: utf-8 -*-
"""
Browser Tools - Web automation tools for NogicOS Agent

Reference: browser-use/actor/page.py, browser-use/dom/service.py
"""

import logging
import base64
from typing import Optional, Dict, Any, List

from .base import ToolRegistry, ToolCategory, get_registry
from .descriptions import (
    BROWSER_NAVIGATE, BROWSER_CLICK, BROWSER_TYPE, 
    BROWSER_SCREENSHOT, BROWSER_GET_CONTENT, BROWSER_SCROLL, BROWSER_EXTRACT,
    BROWSER_GET_URL, BROWSER_GET_TITLE, BROWSER_BACK, BROWSER_WAIT, BROWSER_SEND_KEYS
)

logger = logging.getLogger(__name__)


def register_browser_tools(registry: Optional[ToolRegistry] = None) -> ToolRegistry:
    """
    Register all browser tools to the registry.
    
    Args:
        registry: Optional registry to use. If None, uses global registry.
        
    Returns:
        The registry with browser tools registered.
    """
    if registry is None:
        registry = get_registry()
    
    @registry.action(
        description=BROWSER_NAVIGATE,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_navigate(url: str, browser_session=None) -> str:
        """Navigate to a URL"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            # Use the existing CDP session to navigate
            await browser_session.navigate(url)
            title = await browser_session.get_title()
            return f"Navigated to {url}. Page title: {title}"
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return f"Error navigating to {url}: {str(e)}"
    
    @registry.action(
        description=BROWSER_CLICK,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_click(selector: str, browser_session=None) -> str:
        """Click an element"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            await browser_session.click(selector)
            return f"Clicked element: {selector}"
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return f"Error clicking {selector}: {str(e)}"
    
    @registry.action(
        description=BROWSER_TYPE,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_type(selector: str, text: str, browser_session=None) -> str:
        """Type text into an element"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            await browser_session.type(selector, text)
            return f"Typed '{text}' into {selector}"
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return f"Error typing into {selector}: {str(e)}"
    
    @registry.action(
        description=BROWSER_SCREENSHOT,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_screenshot(browser_session=None) -> Dict[str, Any]:
        """
        Take a screenshot and return structured data for multimodal LLM.
        
        Returns:
            Dict with:
            - type: "browser_screenshot" (for Agent to detect)
            - image_base64: PNG screenshot as base64
            - page_content: Text content of the page (for context)
            - url: Current page URL
            - title: Page title
        """
        if browser_session is None:
            return {"type": "error", "message": "No browser session available"}
        
        try:
            # Take screenshot
            screenshot_data = await browser_session.screenshot()
            if isinstance(screenshot_data, bytes):
                screenshot_b64 = base64.b64encode(screenshot_data).decode('utf-8')
            else:
                screenshot_b64 = screenshot_data
            
            # Also extract page content for LLM understanding
            try:
                page_content = await browser_session.get_page_content()
                # Truncate to avoid token explosion
                page_content = page_content[:3000] if len(page_content) > 3000 else page_content
            except Exception:
                page_content = "(Could not extract page content)"
            
            # Get URL and title
            try:
                url = await browser_session.get_current_url()
                title = await browser_session.get_title()
            except Exception:
                url = "(unknown)"
                title = "(unknown)"
            
            logger.info(f"[Browser] Screenshot captured: {len(screenshot_b64)} bytes, URL: {url}")
            
            return {
                "type": "browser_screenshot",
                "image_base64": screenshot_b64,
                "page_content": page_content,
                "url": url,
                "title": title,
            }
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {"type": "error", "message": f"Error taking screenshot: {str(e)}"}
    
    @registry.action(
        description=BROWSER_EXTRACT,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_extract(selector: str = "", browser_session=None) -> str:
        """Extract text from page or element"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            if selector:
                content = await browser_session.extract_text(selector)
            else:
                content = await browser_session.get_page_content()
            return content[:5000] if len(content) > 5000 else content  # Limit output
        except Exception as e:
            logger.error(f"Extract failed: {e}")
            return f"Error extracting content: {str(e)}"
    
    @registry.action(
        description=BROWSER_GET_URL,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_get_url(browser_session=None) -> str:
        """Get current URL"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            url = await browser_session.get_current_url()
            return url
        except Exception as e:
            logger.error(f"Get URL failed: {e}")
            return f"Error getting URL: {str(e)}"
    
    @registry.action(
        description=BROWSER_GET_TITLE,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_get_title(browser_session=None) -> str:
        """Get current page title"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            title = await browser_session.get_title()
            return title if title else "(No title)"
        except Exception as e:
            logger.error(f"Get title failed: {e}")
            return f"Error getting title: {str(e)}"
    
    @registry.action(
        description=BROWSER_GET_CONTENT,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_get_content(browser_session=None) -> str:
        """Get page text content"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            content = await browser_session.get_page_content()
            return content[:5000] if len(content) > 5000 else content
        except Exception as e:
            logger.error(f"Get content failed: {e}")
            return f"Error getting content: {str(e)}"
    
    @registry.action(
        description=BROWSER_SCROLL,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_scroll(direction: str = "down", browser_session=None) -> str:
        """Scroll the page"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            await browser_session.scroll(direction)
            return f"Scrolled {direction}"
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return f"Error scrolling: {str(e)}"
    
    @registry.action(
        description=BROWSER_BACK,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_back(browser_session=None) -> str:
        """Go back"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            await browser_session.go_back()
            return "Navigated back"
        except Exception as e:
            logger.error(f"Back navigation failed: {e}")
            return f"Error going back: {str(e)}"
    
    @registry.action(
        description=BROWSER_WAIT,
        category=ToolCategory.BROWSER
    )
    async def browser_wait(seconds: int = 1) -> str:
        """Wait for seconds"""
        import asyncio
        await asyncio.sleep(seconds)
        return f"Waited {seconds} seconds"
    
    @registry.action(
        description=BROWSER_SEND_KEYS,
        category=ToolCategory.BROWSER,
        requires_context=["browser_session"]
    )
    async def browser_send_keys(keys: str, browser_session=None) -> str:
        """Send keyboard keys"""
        if browser_session is None:
            return "Error: No browser session available"
        
        try:
            await browser_session.send_keys(keys)
            return f"Sent keys: {keys}"
        except Exception as e:
            logger.error(f"Send keys failed: {e}")
            return f"Error sending keys: {str(e)}"
    
    logger.info(f"Registered {len(registry.get_by_category(ToolCategory.BROWSER))} browser tools")
    return registry


