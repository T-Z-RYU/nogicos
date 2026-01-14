# -*- coding: utf-8 -*-
"""
Browser Session Manager - CDP/Playwright based browser control

Provides a unified interface for browser automation that works with:
1. Electron's WebContentsView via CDP (when available)
2. Playwright in headless mode (fallback)

This module bridges the gap between NogicOS tools and actual browser control.
"""

import asyncio
import logging
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger("nogicos.browser.session")

# ============================================================================
# Playwright Integration (Fallback for headless browser automation)
# ============================================================================

PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
    logger.info("[BrowserSession] Playwright available")
except ImportError:
    logger.warning("[BrowserSession] Playwright not installed. Run: pip install playwright && playwright install")
    Browser = None
    Page = None
    BrowserContext = None


@dataclass
class BrowserState:
    """Current state of the browser session"""
    url: str = ""
    title: str = ""
    is_loading: bool = False
    can_go_back: bool = False
    can_go_forward: bool = False


class BrowserSession:
    """
    Unified browser session manager.

    Supports:
    - Playwright-based headless browsing (default)
    - CDP-based control via Electron (when connected)

    Usage:
        session = BrowserSession()
        await session.start()
        await session.navigate("https://google.com")
        content = await session.get_page_content()
        await session.stop()
    """

    # Default configuration (can be overridden via environment variables)
    DEFAULT_VIEWPORT_WIDTH = int(os.environ.get("NOGICOS_VIEWPORT_WIDTH", "1280"))
    DEFAULT_VIEWPORT_HEIGHT = int(os.environ.get("NOGICOS_VIEWPORT_HEIGHT", "720"))

    # Pre-compiled URL validation regex (P0 optimization)
    _url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def __init__(
        self,
        headless: bool = True,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None,
    ):
        """
        Initialize browser session.

        Args:
            headless: Run browser in headless mode (default: True)
            viewport: Custom viewport size {"width": 1280, "height": 720}
            user_agent: Custom user agent string

        Environment Variables:
            NOGICOS_VIEWPORT_WIDTH: Default viewport width (default: 1280)
            NOGICOS_VIEWPORT_HEIGHT: Default viewport height (default: 720)
        """
        self.headless = headless
        self.viewport = viewport or {
            "width": self.DEFAULT_VIEWPORT_WIDTH,
            "height": self.DEFAULT_VIEWPORT_HEIGHT
        }
        self.user_agent = user_agent
        
        # Playwright objects
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        # State
        self._started = False
        self._state = BrowserState()
    
    @property
    def is_started(self) -> bool:
        """Check if browser session is started"""
        return self._started and self._page is not None
    
    @property
    def state(self) -> BrowserState:
        """Get current browser state"""
        return self._state
    
    async def start(self) -> bool:
        """
        Start the browser session.

        Returns:
            True if started successfully, False otherwise
        """
        if self._started:
            logger.warning("[BrowserSession] Already started")
            return True

        if not PLAYWRIGHT_AVAILABLE:
            logger.error("[BrowserSession] Playwright not available, cannot start")
            return False

        # Track resources for cleanup on failure
        playwright_started = False
        browser_started = False
        context_started = False

        try:
            self._playwright = await async_playwright().start()
            playwright_started = True

            # Launch browser
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                ]
            )
            browser_started = True

            # Create context with viewport and user agent
            context_options = {
                "viewport": self.viewport,
            }
            if self.user_agent:
                context_options["user_agent"] = self.user_agent

            self._context = await self._browser.new_context(**context_options)
            context_started = True

            # Create page
            self._page = await self._context.new_page()

            # Setup event listeners
            self._page.on("load", self._on_load)
            self._page.on("framenavigated", self._on_navigated)

            self._started = True
            logger.info("[BrowserSession] Started successfully")
            return True

        except Exception as e:
            logger.error(f"[BrowserSession] Failed to start: {e}")
            # [P1 FIX] Clean up resources in reverse order of creation with comprehensive handling
            cleanup_errors = []

            # Close context first
            if context_started and self._context:
                try:
                    await asyncio.wait_for(self._context.close(), timeout=5.0)
                except asyncio.TimeoutError:
                    cleanup_errors.append("context close timeout")
                except Exception as cleanup_err:
                    cleanup_errors.append(f"context: {cleanup_err}")
                finally:
                    self._context = None

            # Then close browser
            if browser_started and self._browser:
                try:
                    await asyncio.wait_for(self._browser.close(), timeout=5.0)
                except asyncio.TimeoutError:
                    cleanup_errors.append("browser close timeout")
                except Exception as cleanup_err:
                    cleanup_errors.append(f"browser: {cleanup_err}")
                finally:
                    self._browser = None

            # Finally stop playwright
            if playwright_started and self._playwright:
                try:
                    await asyncio.wait_for(self._playwright.stop(), timeout=5.0)
                except asyncio.TimeoutError:
                    cleanup_errors.append("playwright stop timeout")
                except Exception as cleanup_err:
                    cleanup_errors.append(f"playwright: {cleanup_err}")
                finally:
                    self._playwright = None

            # Log all cleanup errors at once
            if cleanup_errors:
                logger.warning(f"[BrowserSession] Cleanup errors: {', '.join(cleanup_errors)}")

            self._page = None
            self._started = False
            return False
    
    async def connect_to_browser(self, cdp_url: str = "http://localhost:9222") -> bool:
        """
        Connect to an existing browser via Chrome DevTools Protocol (CDP).
        
        This allows NogicOS to control a browser that the user has already opened,
        enabling direct DOM manipulation without mouse simulation.
        
        Args:
            cdp_url: CDP endpoint URL (default: http://localhost:9222)
                     User must start Chrome with: --remote-debugging-port=9222
        
        Returns:
            True if connected successfully, False otherwise
        """
        if self._started:
            logger.warning("[BrowserSession] Already started, call stop() first")
            return False
        
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("[BrowserSession] Playwright not available, cannot connect")
            return False
        
        try:
            # Start playwright if not already started
            if not self._playwright:
                self._playwright = await async_playwright().start()
            
            # Connect to existing browser via CDP
            logger.info(f"[BrowserSession] Connecting to browser at {cdp_url}...")
            self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)
            
            # Get existing contexts or create new one
            contexts = self._browser.contexts
            if contexts:
                self._context = contexts[0]
                logger.info(f"[BrowserSession] Using existing context with {len(contexts)} context(s)")
            else:
                self._context = await self._browser.new_context(viewport=self.viewport)
                logger.info("[BrowserSession] Created new context")
            
            # Get existing pages or create new one
            pages = self._context.pages
            if pages:
                self._page = pages[0]
                logger.info(f"[BrowserSession] Using existing page: {await self._page.title()}")
            else:
                self._page = await self._context.new_page()
                logger.info("[BrowserSession] Created new page")
            
            # Setup event listeners
            self._page.on("load", self._on_load)
            self._page.on("framenavigated", self._on_navigated)
            
            self._started = True
            logger.info(f"[BrowserSession] Connected to browser via CDP at {cdp_url}")
            return True
            
        except Exception as e:
            logger.error(f"[BrowserSession] Failed to connect via CDP: {e}")
            # Cleanup on failure
            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None
            self._browser = None
            self._context = None
            self._page = None
            self._started = False
            return False
    
    async def stop(self) -> None:
        """Stop the browser session and cleanup resources with timeout protection"""

        async def _close_with_timeout(resource, name: str, timeout: float = 5.0):
            """Helper to close a resource with timeout"""
            if resource is None:
                return
            try:
                await asyncio.wait_for(resource.close(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"[BrowserSession] Timeout closing {name}")
            except Exception as e:
                logger.debug(f"[BrowserSession] Error closing {name}: {e}")

        try:
            await _close_with_timeout(self._page, "page")
            self._page = None

            await _close_with_timeout(self._context, "context")
            self._context = None

            await _close_with_timeout(self._browser, "browser")
            self._browser = None

            if self._playwright:
                try:
                    await asyncio.wait_for(self._playwright.stop(), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("[BrowserSession] Timeout stopping playwright")
                except Exception as e:
                    logger.debug(f"[BrowserSession] Error stopping playwright: {e}")
                self._playwright = None

            self._started = False
            logger.info("[BrowserSession] Stopped")

        except Exception as e:
            logger.warning(f"[BrowserSession] Error during stop: {e}")
    
    def _on_load(self, page: Page) -> None:
        """Handle page load event"""
        self._state.is_loading = False
    
    def _on_navigated(self, frame) -> None:
        """Handle frame navigation event"""
        if self._page is not None and frame == self._page.main_frame:
            self._state.url = frame.url
    
    # ========================================================================
    # Navigation Methods
    # ========================================================================
    
    # [P0-2 FIX] Security: Enhanced SSRF prevention with comprehensive IP validation
    BLOCKED_HOSTS = {
        # Localhost variants
        "localhost", "127.0.0.1", "0.0.0.0", "::1",
        "127.0.0.0", "127.255.255.255",
        # Cloud metadata endpoints
        "169.254.169.254",              # AWS/Azure metadata
        "metadata.google.internal",     # GCP metadata
        "metadata.goog",                # GCP alternative
        "100.100.100.200",              # Alibaba metadata
        "192.0.0.192",                  # Oracle Cloud metadata
        # Kubernetes
        "kubernetes.default.svc",
        "kubernetes.default",
    }

    @staticmethod
    def _is_private_ip(host: str) -> bool:
        """
        [P0-2 FIX] Check if host is a private/internal IP address.
        Uses ipaddress module for robust validation.
        """
        import ipaddress

        try:
            # Try to parse as IP address
            ip = ipaddress.ip_address(host)

            # Check various private/special ranges
            return (
                ip.is_private or
                ip.is_loopback or
                ip.is_link_local or
                ip.is_reserved or
                ip.is_multicast or
                ip.is_unspecified
            )
        except ValueError:
            # Not a valid IP address, check for octal/hex bypass attempts
            # E.g., 0177.0.0.1 (octal), 0x7f.0.0.1 (hex)
            if any(part.startswith(('0x', '0X', '0')) and len(part) > 1
                   for part in host.split('.') if part.isalnum()):
                return True  # Suspicious IP format
            return False

    async def navigate(self, url: str, timeout: float = 15.0) -> bool:
        """
        Navigate to a URL.

        Optimized (P0):
        - Reduced default timeout: 30s → 15s
        - URL validation before navigation
        - Fast fail for invalid URLs
        - [P0-2 FIX] Enhanced SSRF protection with ipaddress module

        Args:
            url: URL to navigate to
            timeout: Navigation timeout in seconds (default: 15s)

        Returns:
            True if navigation successful
        """
        if not self._page:
            logger.error("[BrowserSession] Page not available")
            return False

        # P0: URL validation - fail fast for invalid URLs
        from urllib.parse import urlparse
        import ipaddress

        if not self._url_pattern.match(url):
            logger.warning(f"[BrowserSession] Invalid URL format: {url}")
            self._state.is_loading = False
            return False

        # [P0-2 FIX] Enhanced SSRF protection
        try:
            parsed = urlparse(url)
            host = parsed.hostname.lower() if parsed.hostname else ""

            if not host:
                logger.warning("[BrowserSession] No hostname in URL")
                return False

            # Check against blocked hosts (exact match)
            if host in self.BLOCKED_HOSTS:
                logger.warning(f"[BrowserSession] SSRF blocked (blocklist): {host}")
                return False

            # [P0-2 FIX] Check for private IP using ipaddress module
            if self._is_private_ip(host):
                logger.warning(f"[BrowserSession] SSRF blocked (private IP): {host}")
                return False

            # [P0-2 FIX] Validate IPv6 addresses
            if ':' in host or host.startswith('['):
                clean_host = host.strip('[]')
                try:
                    ipv6 = ipaddress.ip_address(clean_host)
                    if ipv6.is_private or ipv6.is_loopback or ipv6.is_link_local:
                        logger.warning(f"[BrowserSession] SSRF blocked (IPv6 private): {host}")
                        return False
                except ValueError:
                    pass

            # [P0-2 FIX] Block suspicious hostname patterns
            suspicious_patterns = [
                r'\.internal$',         # internal domains
                r'\.local$',            # .local domains
                r'\.localdomain$',      # localdomain
                r'\.corp$',             # corporate domains
                r'\.home$',             # home networks
                r'^169\.254\.',         # link-local (APIPA)
                r'^fc[0-9a-f]{2}:',     # IPv6 ULA
                r'^fe80:',              # IPv6 link-local
            ]
            for pattern in suspicious_patterns:
                if re.search(pattern, host, re.IGNORECASE):
                    logger.warning(f"[BrowserSession] SSRF blocked (suspicious pattern): {host}")
                    return False

            # [P0-2 FIX Round 1] DNS pre-resolution to prevent DNS rebinding attacks
            # Resolve hostname and verify the resolved IP is not private
            import socket
            try:
                resolved_ip = socket.gethostbyname(host)
                if self._is_private_ip(resolved_ip):
                    logger.warning(f"[BrowserSession] SSRF blocked (DNS resolves to private IP): {host} -> {resolved_ip}")
                    return False
            except socket.gaierror:
                # DNS resolution failed - allow the request (might be a valid public domain)
                # Playwright will handle the actual resolution
                pass

        except Exception as e:
            logger.warning(f"[BrowserSession] URL parsing error: {e}")
            return False

        try:
            self._state.is_loading = True
            # P0: Use domcontentloaded for faster load, reduced timeout
            await self._page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
            self._state.url = url
            self._state.title = await self._page.title()
            self._state.is_loading = False
            
            # Update navigation state
            self._state.can_go_back = await self._can_go_back()
            
            logger.info(f"[BrowserSession] Navigated to: {url} in <{timeout}s")
            return True
            
        except Exception as e:
            logger.error(f"[BrowserSession] Navigation failed: {e}")
            self._state.is_loading = False
            return False
    
    async def _can_go_back(self) -> bool:
        """Check if can go back in history"""
        try:
            # Playwright doesn't have direct history access, so we track state
            return len(self._page.url) > 0
        except Exception as e:
            return False
    
    async def go_back(self) -> bool:
        """Go back in browser history"""
        if not self._page:
            return False
        
        try:
            await self._page.go_back(timeout=10000)
            self._state.url = self._page.url
            self._state.title = await self._page.title()
            return True
        except Exception as e:
            logger.error(f"[BrowserSession] Go back failed: {e}")
            return False
    
    async def go_forward(self) -> bool:
        """Go forward in browser history"""
        if not self._page:
            return False
        
        try:
            await self._page.go_forward(timeout=10000)
            self._state.url = self._page.url
            self._state.title = await self._page.title()
            return True
        except Exception as e:
            logger.error(f"[BrowserSession] Go forward failed: {e}")
            return False
    
    async def reload(self) -> bool:
        """Reload the current page"""
        if not self._page:
            return False
        
        try:
            await self._page.reload(timeout=30000)
            return True
        except Exception as e:
            logger.error(f"[BrowserSession] Reload failed: {e}")
            return False
    
    async def get_current_url(self) -> str:
        """Get the current page URL"""
        if not self._page:
            return ""
        return self._page.url
    
    async def get_title(self) -> str:
        """Get the current page title"""
        if not self._page:
            return ""
        try:
            return await self._page.title()
        except Exception as e:
            return ""
    
    # ========================================================================
    # Interaction Methods
    # ========================================================================
    
    async def click(self, selector: str, timeout: float = 8.0, max_retries: int = 2) -> bool:
        """
        Click an element by selector.
        
        P1 优化:
        - 多Select器Policy: CSS → text → role → partial match
        - 点击BeforeWait元素Visible
        - scroll_into_view_if_needed
        - Autoretry mechanism (P1 #6)
        
        Args:
            selector: CSS selector or text selector
            timeout: Click timeout in seconds (default: 8s)
            max_retries: Maximum retry attempts (default: 2)
            
        Returns:
            True if click successful
        """
        if not self._page:
            return False
        
        # P1: multipleSelecterPolicy
        selectors_to_try = [
            selector,                           # OriginalSelecter
            f"text={selector}",                 # textMatch
            f"role=button[name='{selector}']",  # ARIA role
            f"role=link[name='{selector}']",    # link role
            f"*:has-text('{selector}')",        # PartialtextMatch
        ]
        
        # P1 #6: RetryLoop
        for attempt in range(max_retries + 1):
            for sel in selectors_to_try:
                try:
                    # P1: WaitElementsVisibleAfteragainClick
                    locator = self._page.locator(sel).first
                    
                    # WaitElementsstorein（most 2 Second）
                    try:
                        await locator.wait_for(state="visible", timeout=2000)
                    except (TimeoutError, Exception):
                        continue  # tryDownoneaSelecter
                    
                    # P1: ScrolltocanviewLocale
                    await locator.scroll_into_view_if_needed()
                    
                    # Click
                    await locator.click(timeout=timeout * 1000)
                    logger.info(f"[BrowserSession] Clicked with selector: {sel}")
                    return True
                    
                except Exception:
                    continue  # tryDownoneaSelecter
            
            # P1 #6: RetryBeforeWaitpagestable
            if attempt < max_retries:
                logger.debug(f"[BrowserSession] Click retry {attempt + 1}/{max_retries} for '{selector}'")
                await asyncio.sleep(0.5)  # ShorttempWait
                # WaitNetworkEmptyidle
                try:
                    await self._page.wait_for_load_state("networkidle", timeout=2000)
                except (TimeoutError, Exception):
                    pass
        
        logger.error(f"[BrowserSession] Click failed after {max_retries + 1} attempts for '{selector}'")
        return False
    
    async def type(self, selector: str, text: str, delay: float = 0.05, timeout: float = 8.0, max_retries: int = 2) -> bool:
        """
        Type text into an element.
        
        P1 优化:
        - 多Select器Policy: CSS → placeholder → label → role
        - InputBeforeWait元素Visible
        - 清Empty现有Inner容After再Input
        - Autoretry mechanism (P1 #6)
        
        Args:
            selector: CSS selector for input element
            text: Text to type
            delay: Delay between keystrokes in seconds
            timeout: Timeout in seconds (default: 8s)
            max_retries: Maximum retry attempts (default: 2)
            
        Returns:
            True if typing successful
        """
        if not self._page:
            return False
        
        # P1: multipleSelecterPolicy (Inputboxspecialuse)
        selectors_to_try = [
            selector,                                    # OriginalSelecter
            f"input[placeholder*='{selector}' i]",      # placeholder Packagecontain
            f"input[name*='{selector}' i]",             # name Packagecontain
            f"textarea[placeholder*='{selector}' i]",   # textarea placeholder
            f"role=textbox[name='{selector}']",         # ARIA textbox
            f"role=searchbox",                          # Searchbox (general)
            f"input[type='text']",                      # generaltextInputbox
            f"input[type='search']",                    # SearchInputbox
        ]
        
        # P1 #6: RetryLoop
        for attempt in range(max_retries + 1):
            for sel in selectors_to_try:
                try:
                    locator = self._page.locator(sel).first
                    
                    # P1: WaitElementsVisible
                    try:
                        await locator.wait_for(state="visible", timeout=2000)
                    except (TimeoutError, Exception):
                        continue
                    
                    # P1: ScrolltocanviewLocale
                    await locator.scroll_into_view_if_needed()
                    
                    # clearEmptyandPadding
                    await locator.fill(text, timeout=timeout * 1000)
                    logger.info(f"[BrowserSession] Typed into: {sel}")
                    return True
                    
                except Exception:
                    continue
            
            # P1 #6: RetryBeforeWait
            if attempt < max_retries:
                logger.debug(f"[BrowserSession] Type retry {attempt + 1}/{max_retries} for '{selector}'")
                await asyncio.sleep(0.3)
        
        # mostAftertry: ClickandKeyboardInput
        try:
            await self._page.keyboard.type(text, delay=delay * 1000)
            logger.info("[BrowserSession] Typed via keyboard fallback")
            return True
        except Exception as e:
            logger.error(f"[BrowserSession] Type failed after {max_retries + 1} attempts for '{selector}'")
            return False
    
    async def send_keys(self, keys: str) -> bool:
        """
        Send keyboard keys.
        
        Args:
            keys: Key or key combination (e.g., "Enter", "Control+A")
            
        Returns:
            True if successful
        """
        if not self._page:
            return False
        
        try:
            await self._page.keyboard.press(keys)
            return True
        except Exception as e:
            logger.error(f"[BrowserSession] Send keys failed: {e}")
            return False
    
    async def scroll(self, direction: str = "down", amount: int = 500) -> bool:
        """
        Scroll the page.
        
        Args:
            direction: "up", "down", "top", or "bottom"
            amount: Scroll amount in pixels (for up/down)
            
        Returns:
            True if successful
        """
        if not self._page:
            return False
        
        try:
            if direction == "top":
                await self._page.evaluate("window.scrollTo(0, 0)")
            elif direction == "bottom":
                await self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif direction == "up":
                await self._page.evaluate(f"window.scrollBy(0, -{amount})")
            else:  # down
                await self._page.evaluate(f"window.scrollBy(0, {amount})")
            return True
        except Exception as e:
            logger.error(f"[BrowserSession] Scroll failed: {e}")
            return False
    
    # ========================================================================
    # Content Extraction
    # ========================================================================
    
    async def get_page_content(self) -> str:
        """
        Get the full text content of the page.
        
        Returns:
            Page text content
        """
        if not self._page:
            return ""
        
        try:
            return await self._page.evaluate("document.body.innerText")
        except Exception as e:
            logger.error(f"[BrowserSession] Get content failed: {e}")
            return ""
    
    async def extract_text(self, selector: str) -> str:
        """
        Extract text from a specific element.
        
        Args:
            selector: CSS selector
            
        Returns:
            Element text content
        """
        if not self._page:
            return ""
        
        try:
            element = await self._page.query_selector(selector)
            if element:
                return await element.inner_text()
            return ""
        except Exception as e:
            logger.error(f"[BrowserSession] Extract text failed: {e}")
            return ""
    
    async def screenshot(self, full_page: bool = False) -> bytes:
        """
        Take a screenshot of the page.
        
        Args:
            full_page: Capture full scrollable page
            
        Returns:
            Screenshot as PNG bytes
        """
        if not self._page:
            return b""
        
        try:
            return await self._page.screenshot(full_page=full_page, type="png")
        except Exception as e:
            logger.error(f"[BrowserSession] Screenshot failed: {e}")
            return b""
    
    async def get_element_at(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        Get element information at specific coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Element info dict or None
        """
        if not self._page:
            return None
        
        try:
            element_info = await self._page.evaluate(f"""
                () => {{
                    const elem = document.elementFromPoint({x}, {y});
                    if (!elem) return null;
                    return {{
                        tagName: elem.tagName,
                        id: elem.id,
                        className: elem.className,
                        text: elem.innerText?.slice(0, 100),
                        href: elem.href || null,
                    }};
                }}
            """)
            return element_info
        except Exception as e:
            logger.error(f"[BrowserSession] Get element failed: {e}")
            return None
    
    async def wait_for_selector(
        self,
        selector: str,
        timeout: float = 10.0,
        state: str = "visible"
    ) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS selector
            timeout: Wait timeout in seconds
            state: "attached", "detached", "visible", or "hidden"
            
        Returns:
            True if element found within timeout
        """
        if not self._page:
            return False
        
        try:
            await self._page.wait_for_selector(
                selector,
                timeout=timeout * 1000,
                state=state
            )
            return True
        except Exception as e:
            logger.warning(f"[BrowserSession] Wait for selector timeout: {e}")
            return False


# ============================================================================
# Session Manager (Using contextvars for async-safe state)
# ============================================================================

import contextvars

# Use contextvars instead of global variable for async-safe session management
_active_session_var: contextvars.ContextVar[Optional[BrowserSession]] = contextvars.ContextVar(
    'active_browser_session', default=None
)

# [P1 FIX] Add lock for concurrent tool execution
_session_lock = asyncio.Lock()


async def get_browser_session() -> BrowserSession:
    """
    Get or create the active browser session.

    Uses contextvars for async-safe session management across coroutines.
    [P1 FIX] Uses lock to prevent race conditions during session creation.

    Returns:
        Active BrowserSession instance
    """
    # [P1 FIX] Use lock to prevent concurrent session creation
    async with _session_lock:
        session = _active_session_var.get()

        if session is None or not session.is_started:
            session = BrowserSession(headless=True)
            await session.start()
            _active_session_var.set(session)

        return session


async def close_browser_session() -> None:
    """Close the active browser session"""
    # [P1 FIX] Use lock to prevent concurrent session close
    async with _session_lock:
        session = _active_session_var.get()

        if session:
            await session.stop()
            _active_session_var.set(None)

