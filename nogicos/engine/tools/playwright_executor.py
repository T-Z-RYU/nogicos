# -*- coding: utf-8 -*-
"""
NogicOS Playwright Executor - Browser automation using Playwright

Capabilities aligned with Cursor's Playwright MCP:
- Connect to existing Chrome (via Hook system + CDP)
- Get page snapshot (accessibility tree)
- Click, type, scroll operations
- Execute JavaScript code
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Playwright imports
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("[Playwright] playwright not installed. Run: pip install playwright && playwright install")


@dataclass
class PlaywrightSnapshot:
    """Page snapshot result"""
    url: str
    title: str
    snapshot_yaml: str  # Accessibility tree in YAML format
    elements: List[Dict[str, Any]]  # Parsed elements with refs


class NogicPlaywrightExecutor:
    """
    NogicOS Playwright Executor
    
    Capabilities:
    - Connect to hooked Chrome via CDP
    - Get page accessibility snapshot (same as Cursor MCP)
    - Execute various browser operations
    """
    
    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._connected = False
        self._cdp_url = "http://localhost:9222"
    
    async def connect(self, cdp_url: str = "http://localhost:9222") -> bool:
        """
        Connect to an open Chrome instance via CDP
        
        Args:
            cdp_url: Chrome DevTools Protocol URL
            
        Returns:
            Whether connection was successful
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("[Playwright] playwright not available")
            return False
        
        try:
            self._cdp_url = cdp_url
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)
            
            contexts = self._browser.contexts
            if contexts:
                self._context = contexts[0]
                pages = self._context.pages
                if pages:
                    self._page = pages[0]
            
            self._connected = True
            logger.info(f"[Playwright] Connected to Chrome via CDP: {cdp_url}")
            return True
            
        except Exception as e:
            logger.error(f"[Playwright] Failed to connect: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from browser"""
        if self._browser:
            # Only disconnect, don't close the browser
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._connected = False
        logger.info("[Playwright] Disconnected")
    
    async def get_snapshot(self) -> Optional[PlaywrightSnapshot]:
        """
        Get snapshot of current page (via JavaScript extraction)
        
        Since CDP-connected Page lacks accessibility attribute, using JS extraction instead
        """
        if not self._connected or not self._page:
            logger.error("[Playwright] Not connected")
            return None
        
        try:
            # Use JavaScript to extract page elements (replacing accessibility.snapshot)
            js_extract = """
            () => {
                const elements = [];
                let refCounter = 0;
                
                // Extract all input elements
                document.querySelectorAll('input, textarea, select, button, a, [role="button"], [role="textbox"]').forEach(el => {
                    const ref = 'e' + refCounter++;
                    const rect = el.getBoundingClientRect();
                    
                    // Skip invisible elements
                    if (rect.width === 0 || rect.height === 0) return;
                    
                    const label = el.labels?.[0]?.textContent?.trim() || 
                                  el.getAttribute('aria-label') || 
                                  el.getAttribute('placeholder') ||
                                  el.closest('label')?.textContent?.trim() ||
                                  '';
                    
                    elements.push({
                        ref: ref,
                        tag: el.tagName.toLowerCase(),
                        type: el.type || '',
                        name: el.name || '',
                        id: el.id || '',
                        label: label.slice(0, 100),
                        value: el.value || '',
                        role: el.getAttribute('role') || el.tagName.toLowerCase(),
                        placeholder: el.placeholder || '',
                        isEmpty: !el.value || el.value.trim() === '',
                        selector: el.id ? '#' + el.id : (el.name ? `[name="${el.name}"]` : null)
                    });
                });
                
                return elements;
            }
            """
            
            elements_data = await self._page.evaluate(js_extract)
            
            # #region agent log
            with open(r"c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log", "a") as _f:
                _f.write(_json2.dumps({"location":"playwright_executor.py:get_snapshot","message":"JS extraction completed","data":{"elements_count":len(elements_data) if elements_data else 0},"timestamp":__import__("time").time()*1000,"hypothesisId":"E1"}) + "\n")
            # #endregion
            
            # Convert to YAML format
            yaml_lines = []
            elements = []
            
            for el in (elements_data or []):
                ref = el.get('ref', '')
                role = el.get('role', 'input')
                label = el.get('label', '')
                value = el.get('value', '')
                
                # Build YAML line
                line_parts = [f"- {role}"]
                if label:
                    line_parts.append(f' "{label}"')
                if value:
                    line_parts.append(f': "{value[:50]}"')
                line_parts.append(f" [ref={ref}]")
                
                yaml_lines.append("".join(line_parts))
                elements.append(el)
            
            return PlaywrightSnapshot(
                url=self._page.url,
                title=await self._page.title(),
                snapshot_yaml="\n".join(yaml_lines),
                elements=elements,
            )
            
        except Exception as e:
            # #region agent log
            import json as _json3
            import traceback
            with open(r"c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log", "a") as _f:
                _f.write(_json3.dumps({"location":"playwright_executor.py:get_snapshot","message":"EXCEPTION in get_snapshot","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()[:500]},"timestamp":__import__("time").time()*1000,"hypothesisId":"E1"}) + "\n")
            # #endregion
            logger.error(f"[Playwright] Snapshot failed: {e}")
            return None
    
    async def click(self, ref: str, element_description: str = "") -> bool:
        """
        点击元素
        
        Args:
            ref: 元素引用（如 "e12"）或Select器
            element_description: 元素描述（用于Log）
        """
        if not self._connected or not self._page:
            return False
        
        try:
            # Get current snapshot to find element
            snapshot = await self.get_snapshot()
            if not snapshot:
                return False
            
            # Find matching ref in element list
            target_element = None
            for el in snapshot.elements:
                if el.get('ref') == ref:
                    target_element = el
                    break
            
            if target_element:
                selector = target_element.get('selector')
                if selector:
                    await self._page.locator(selector).click()
                    logger.info(f"[Playwright] Clicked: {element_description or selector}")
                    return True
                
                # Try clicking by label
                label = target_element.get('label', '')
                if label:
                    await self._page.get_by_text(label).click()
                    logger.info(f"[Playwright] Clicked: {element_description or label}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"[Playwright] Click failed: {e}")
            return False
    
    async def type_text(self, ref: str, text: str, element_description: str = "") -> bool:
        """
        在元素MediumInput文本
        
        Args:
            ref: 元素引用（如 "e12"）或Select器
            text: 要Input的文本
            element_description: 元素描述
        """
        if not self._connected or not self._page:
            return False
        
        try:
            # Get current snapshot to find element
            snapshot = await self.get_snapshot()
            if not snapshot:
                return False
            
            # Find matching ref in element list
            target_element = None
            for el in snapshot.elements:
                if el.get('ref') == ref:
                    target_element = el
                    break
            
            if target_element:
                selector = target_element.get('selector')
                if selector:
                    await self._page.locator(selector).fill(text)
                    logger.info(f"[Playwright] Typed into: {element_description or selector}")
                    return True
                
                # Try locating by name
                name = target_element.get('name')
                if name:
                    await self._page.locator(f"[name='{name}']").fill(text)
                    logger.info(f"[Playwright] Typed into: {element_description or name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"[Playwright] Type failed: {e}")
            return False
    
    async def evaluate(self, script: str) -> Any:
        """
        Execute JavaScript 代码
        
        Args:
            script: JavaScript 代码
            
        Returns:
            ExecuteResult
        """
        if not self._connected or not self._page:
            return None
        
        try:
            result = await self._page.evaluate(script)
            return result
        except Exception as e:
            logger.error(f"[Playwright] Evaluate failed: {e}")
            return None
    
    async def navigate(self, url: str) -> bool:
        """导航到 URL"""
        if not self._connected or not self._page:
            return False
        
        try:
            await self._page.goto(url)
            logger.info(f"[Playwright] Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"[Playwright] Navigate failed: {e}")
            return False
    
    async def find_empty_fields(self) -> List[Dict[str, Any]]:
        """
        Find页面Up的Empty白Table单Field
        
        Returns:
            Empty白FieldList，每个Package含 label, ref, placeholder
        """
        # #region agent log H1
        import json as _json; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"H1","location":"playwright_executor.py:find_empty_fields:entry","message":"find_empty_fields called","data":{"connected":self._connected,"has_page":bool(self._page)},"timestamp":__import__('time').time()})+'\n')
        # #endregion
        
        if not self._connected or not self._page:
            return []
        
        try:
            # Execute JavaScript to find empty fields - improved version for YC forms
            result = await self._page.evaluate("""
                () => {
                    // Extended selector: input, textarea, contenteditable
                    const textboxes = document.querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="submit"]):not([type="button"]), textarea, [contenteditable="true"]');
                    const emptyFields = [];
                    const allFields = [];  // Debug: record all fields
                    
                    textboxes.forEach((field, index) => {
                        const value = field.value || field.textContent || '';
                        
                        // Improved label lookup logic
                        let label = '';
                        
                        // 1. Try to find associated <label>
                        if (field.id) {
                            const labelEl = document.querySelector(`label[for="${field.id}"]`);
                            if (labelEl) label = labelEl.textContent;
                        }
                        
                        // 2. Try to find label text in parent element
                        if (!label) {
                            const parent = field.closest('div, section, fieldset');
                            if (parent) {
                                const labelEl = parent.querySelector('label, h3, h4, [class*="label"], [class*="Label"]');
                                if (labelEl) label = labelEl.textContent;
                            }
                        }
                        
                        // 3. Try placeholder or name
                        if (!label) {
                            label = field.getAttribute('placeholder') || field.getAttribute('name') || `Field ${index}`;
                        }
                        
                        allFields.push({
                            label: label.substring(0, 100).trim(),
                            value: value.substring(0, 50),
                            tagName: field.tagName,
                            type: field.type || 'N/A',
                            name: field.name || '',
                        });
                        
                        // Check if empty: empty value, https:// default, or whitespace only
                        const isEmpty = value.trim() === '' || 
                                       value.trim() === 'https://' || 
                                       value.trim() === 'http://';
                        
                        if (isEmpty) {
                            emptyFields.push({
                                label: label.substring(0, 100).trim(),
                                placeholder: field.placeholder || '',
                                value: value,
                                tagName: field.tagName,
                                name: field.name || '',
                            });
                        }
                    });
                    
                    return { emptyFields, allFields, totalCount: textboxes.length };
                }
            """)
            
            empty_fields = result.get('emptyFields', [])
            all_fields = result.get('allFields', [])
            
            # #region agent log H4
            open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"H4","location":"playwright_executor.py:find_empty_fields:result","message":"JS evaluation result","data":{"total_fields":result.get('totalCount',0),"empty_count":len(empty_fields),"all_fields_sample":all_fields[:5]},"timestamp":__import__('time').time()})+'\n')
            # #endregion
            
            logger.info(f"[Playwright] Found {len(empty_fields)} empty fields out of {result.get('totalCount', 0)} total")
            return empty_fields
            
        except Exception as e:
            logger.error(f"[Playwright] Find empty fields failed: {e}")
            # #region agent log H5
            open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"H5","location":"playwright_executor.py:find_empty_fields:exception","message":"Exception in find_empty_fields","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":__import__('time').time()})+'\n')
            # #endregion
            return []
    
    async def fill_field_by_label(self, label_contains: str, text: str) -> bool:
        """
        Root据 label 填WriteField
        
        Args:
            label_contains: label Package含的文本
            text: 要填Write的Inner容
        """
        # #region agent log
        import json, time; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(json.dumps({"location":"playwright_executor.py:fill_field_by_label:entry","message":"Fill field called","data":{"label":label_contains,"text_len":len(text),"text_preview":text[:100]},"timestamp":time.time(),"hypothesisId":"H2,H4"})+'\n')
        # #endregion
        
        if not self._connected or not self._page:
            # #region agent log
            import json, time; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(json.dumps({"location":"playwright_executor.py:fill_field_by_label:not_connected","message":"Not connected","data":{"connected":self._connected,"has_page":bool(self._page)},"timestamp":time.time(),"hypothesisId":"H1"})+'\n')
            # #endregion
            return False
        
        try:
            # Use smarter locating strategy - fixed version v4 (tight matching)
            result = await self._page.evaluate("""
                (labelText) => {
                    const searchLower = labelText.toLowerCase();
                    
                    // Strategy 1: Direct exact match with name attribute
                    let field = document.querySelector(`input[name="${labelText}"], textarea[name="${labelText}"]`);
                    if (field) {
                        return { found: true, tagName: field.tagName.toLowerCase(), name: field.name, strategy: 'name_exact' };
                    }
                    
                    // Strategy 2: Find smallest container with label text, then find empty input inside
                    // Key: Find "tightest" match, not any parent container containing text
                    
                    // First, find all DOM nodes containing search text (parent of text nodes)
                    const treeWalker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        { acceptNode: (node) => 
                            node.textContent.toLowerCase().includes(searchLower) 
                                ? NodeFilter.FILTER_ACCEPT 
                                : NodeFilter.FILTER_SKIP 
                        }
                    );
                    
                    let bestMatch = null;
                    let bestContainerSize = Infinity;
                    
                    while (treeWalker.nextNode()) {
                        const textNode = treeWalker.currentNode;
                        // Find the closest block-level container of this text node
                        let container = textNode.parentElement;
                        while (container && !['DIV', 'SECTION', 'FIELDSET', 'LI', 'ARTICLE'].includes(container.tagName)) {
                            container = container.parentElement;
                        }
                        
                        if (!container) continue;
                        
                        // Find input fields within this container
                        const fieldsInContainer = container.querySelectorAll('textarea, input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="submit"])');
                        
                        if (fieldsInContainer.length === 0) continue;
                        
                        // Select smallest container (tightest match)
                        const containerSize = container.textContent.length;
                        if (containerSize < bestContainerSize) {
                            // In this tight container, find first empty field or only field
                            for (const f of fieldsInContainer) {
                                const isEmpty = f.value.trim() === '' || f.value.trim() === 'https://';
                                if (fieldsInContainer.length === 1 || isEmpty) {
                                    bestMatch = {
                                        found: true,
                                        tagName: f.tagName.toLowerCase(),
                                        name: f.name || '',
                                        strategy: 'tight_container',
                                        containerSize: containerSize,
                                        isEmpty: isEmpty
                                    };
                                    bestContainerSize = containerSize;
                                    break;
                                }
                            }
                        }
                    }
                    
                    if (bestMatch) {
                        return bestMatch;
                    }
                    
                    // Strategy 3: Check if placeholder or name contains search term
                    const allFields = document.querySelectorAll('textarea, input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="submit"])');
                    for (const f of allFields) {
                        if ((f.placeholder || '').toLowerCase().includes(searchLower) || 
                            (f.name || '').toLowerCase().includes(searchLower)) {
                            return { found: true, tagName: f.tagName.toLowerCase(), name: f.name || '', strategy: 'placeholder_name' };
                        }
                    }
                    
                    return { found: false, strategy: 'none', searched: searchLower.substring(0, 50) };
                }
            """, label_contains)
            
            # #region agent log
            import json, time; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(json.dumps({"location":"playwright_executor.py:fill_field_by_label:js_result","message":"JS lookup result","data":{"label":label_contains,"result":result},"timestamp":time.time(),"hypothesisId":"H4"})+'\n')
            # #endregion
            
            if result.get('found'):
                # Select locator based on strategy
                strategy = result.get('strategy', 'name_attr')
                
                if result.get('name'):
                    locator = self._page.locator(f"textarea[name='{result['name']}'], input[name='{result['name']}']")
                elif result.get('id'):
                    locator = self._page.locator(f"#{result['id']}")
                else:
                    locator = self._page.get_by_label(label_contains, exact=False)
                
                await locator.fill(text)
                # #region agent log
                import json, time; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(json.dumps({"location":"playwright_executor.py:fill_field_by_label:success","message":"Field filled successfully","data":{"label":label_contains,"strategy":strategy,"name":result.get('name','')},"timestamp":time.time(),"hypothesisId":"H2"})+'\n')
                # #endregion
                logger.info(f"[Playwright] Filled field '{label_contains}' using strategy: {strategy}")
                return True
            
            # #region agent log
            import json, time; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(json.dumps({"location":"playwright_executor.py:fill_field_by_label:not_found","message":"Field NOT found","data":{"label":label_contains,"result":result},"timestamp":time.time(),"hypothesisId":"H4"})+'\n')
            # #endregion
            return False
            
        except Exception as e:
            # #region agent log
            import json, time; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(json.dumps({"location":"playwright_executor.py:fill_field_by_label:exception","message":"Fill field exception","data":{"label":label_contains,"error":str(e)},"timestamp":time.time(),"hypothesisId":"H2"})+'\n')
            # #endregion
            logger.error(f"[Playwright] Fill field failed: {e}")
            return False
    
    def _find_element_by_ref(self, snapshot: Dict, target_ref: str, current_ref: List[int] = None) -> Optional[Dict]:
        """Recursively find element by ref"""
        if current_ref is None:
            current_ref = [0]
        
        if not snapshot:
            return None
        
        ref = f"e{current_ref[0]}"
        current_ref[0] += 1
        
        if ref == target_ref:
            return snapshot
        
        for child in snapshot.get('children', []):
            result = self._find_element_by_ref(child, target_ref, current_ref)
            if result:
                return result
        
        return None


# Global singleton
_executor: Optional[NogicPlaywrightExecutor] = None


def get_playwright_executor() -> NogicPlaywrightExecutor:
    """Get Playwright executor singleton"""
    global _executor
    if _executor is None:
        _executor = NogicPlaywrightExecutor()
    return _executor


def register_playwright_tools(registry):
    """
    Register Playwright tools to NogicOS
    
    These tools align with Cursor Playwright MCP capabilities
    """
    from .base import ToolCategory
    
    @registry.action(
        description="""Get accessibility snapshot of the current page (like Cursor MCP browser_snapshot).
        
This returns a YAML-like structure of all interactive elements on the page.
Each element has a 'ref' that can be used for click/type operations.

Use this to:
- Understand what's on the page
- Find form fields to fill
- Locate buttons to click

Note: hwnd parameter is optional and ignored (Playwright uses CDP connection instead).""",
        category=ToolCategory.BROWSER,
    )
    async def playwright_snapshot(hwnd: str = None) -> Dict[str, Any]:
        """Get page accessibility snapshot. hwnd is optional and ignored."""
        executor = get_playwright_executor()
        
        # Enhanced health check: actually execute JS to verify connection works
        if executor._connected and executor._page:
            try:
                await executor._page.evaluate("1")  # Real health check
            except Exception as e:
                logger.warning(f"[Playwright] Connection stale ({e}), forcing reconnect")
                try:
                    await executor.disconnect()
                except Exception:
                    pass
                executor._connected = False
        elif executor._connected and not executor._page:
            executor._connected = False
        
        # Connect or reconnect
        if not executor._connected:
            success = await executor.connect()
            if not success:
                return {
                    "success": False,
                    "error": "Failed to connect to Chrome. Make sure Chrome is running with --remote-debugging-port=9222"
                }
        
        # Get snapshot with retry
        snapshot = await executor.get_snapshot()
        if snapshot:
            return {
                "success": True,
                "url": snapshot.url,
                "title": snapshot.title,
                "snapshot": snapshot.snapshot_yaml,
                "element_count": len(snapshot.elements),
            }
        
        # If first attempt fails, try reconnecting once
        logger.warning("[Playwright] First snapshot failed, attempting reconnect...")
        try:
            await executor.disconnect()
        except Exception:
            pass
        executor._connected = False
        
        success = await executor.connect()
        if success:
            snapshot = await executor.get_snapshot()
            if snapshot:
                return {
                    "success": True,
                    "url": snapshot.url,
                    "title": snapshot.title,
                    "snapshot": snapshot.snapshot_yaml,
                    "element_count": len(snapshot.elements),
                }
        
        return {
            "success": False,
            "error": "Failed to get snapshot after retry"
        }
    
    @registry.action(
        description="""Click an element on the page.
        
Args:
    element_description: Human-readable description of what to click (e.g., "Submit button", "Login link")
    ref: Optional element reference from snapshot (e.g. 'e12'). If not provided, will search by description.""",
        category=ToolCategory.BROWSER,
    )
    async def playwright_click(element_description: str, ref: str = None) -> Dict[str, Any]:
        """Click an element"""
        executor = get_playwright_executor()
        
        if not executor._connected:
            return {"success": False, "error": "Not connected to browser"}
        
        if ref:
            success = await executor.click(ref, element_description)
        else:
            # Try to click by text/label
            try:
                await executor._page.get_by_text(element_description, exact=False).first.click()
                success = True
                logger.info(f"[Playwright] Clicked by text: {element_description}")
            except Exception as e:
                logger.error(f"[Playwright] Click by text failed: {e}")
                success = False
        
        return {
            "success": success,
            "message": f"Clicked: {element_description}" if success else "Click failed"
        }
    
    @registry.action(
        description="""Type text into an input field.
        
Args:
    element_description: Human-readable description of the field (e.g., "Company name input")
    text: Text to type
    ref: Optional element reference from snapshot. If not provided, will search by description.""",
        category=ToolCategory.BROWSER,
    )
    async def playwright_type(element_description: str, text: str, ref: str = None) -> Dict[str, Any]:
        """Type text into element"""
        executor = get_playwright_executor()
        
        if not executor._connected:
            return {"success": False, "error": "Not connected to browser"}
        
        # If ref is provided, use it directly
        if ref:
            success = await executor.type_text(ref, text, element_description)
        else:
            # Try to find and fill by label/description
            success = await executor.fill_field_by_label(element_description, text)
        
        return {
            "success": success,
            "message": f"Typed into: {element_description}" if success else "Type failed"
        }
    
    async def _ensure_connected() -> tuple:
        """Helper: ensure Playwright is connected, with health check"""
        executor = get_playwright_executor()
        
        # Health check: verify connection is actually working
        if executor._connected:
            try:
                _ = executor._page.url if executor._page else None
                if not executor._page:
                    executor._connected = False
            except Exception:
                logger.warning("[Playwright] Connection stale, will reconnect")
                executor._connected = False
        
        if not executor._connected:
            success = await executor.connect()
            if not success:
                return None, {"success": False, "error": "Not connected to browser"}
        
        return executor, None
    
    @registry.action(
        description="""Find all empty form fields on the current page.
        
Returns a list of empty fields with their labels.""",
        category=ToolCategory.BROWSER,
    )
    async def playwright_find_empty_fields() -> Dict[str, Any]:
        """Find empty form fields"""
        executor, error = await _ensure_connected()
        if error:
            return error
        
        fields = await executor.find_empty_fields()
        return {
            "success": True,
            "empty_fields": fields,
            "count": len(fields),
        }
    
    @registry.action(
        description="""Fill a form field by its label text.
        
Args:
    label_contains: Text that the field's label contains
    text: Text to fill in""",
        category=ToolCategory.BROWSER,
    )
    async def playwright_fill_by_label(label_contains: str, text: str) -> Dict[str, Any]:
        """Fill field by label"""
        executor, error = await _ensure_connected()
        if error:
            return error
        
        success = await executor.fill_field_by_label(label_contains, text)
        return {
            "success": success,
            "message": f"Filled field containing '{label_contains}'" if success else "Fill failed"
        }
    
    @registry.action(
        description="""Execute JavaScript on the page.
        
Args:
    script: JavaScript code to execute (as a function body)""",
        category=ToolCategory.BROWSER,
    )
    async def playwright_evaluate(script: str) -> Dict[str, Any]:
        """Execute JavaScript"""
        executor = get_playwright_executor()
        
        if not executor._connected:
            return {"success": False, "error": "Not connected to browser"}
        
        result = await executor.evaluate(script)
        return {
            "success": True,
            "result": result,
        }
    
    logger.info("[Playwright] Playwright tools registered")


# Test function
async def test_playwright():
    """Test Playwright executor"""
    executor = NogicPlaywrightExecutor()
    
    # Connect to Chrome
    connected = await executor.connect("http://localhost:9222")
    print(f"Connected: {connected}")
    
    if connected:
        # Get snapshot
        snapshot = await executor.get_snapshot()
        if snapshot:
            print(f"URL: {snapshot.url}")
            print(f"Title: {snapshot.title}")
            print(f"Elements: {len(snapshot.elements)}")
            print("Snapshot:")
            print(snapshot.snapshot_yaml[:500])
        
        # Find empty fields
        empty = await executor.find_empty_fields()
        print(f"Empty fields: {empty}")
        
        await executor.disconnect()


if __name__ == "__main__":
    asyncio.run(test_playwright())
