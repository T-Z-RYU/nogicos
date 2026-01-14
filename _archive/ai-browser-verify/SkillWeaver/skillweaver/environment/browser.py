import asyncio
import os
import time
import uuid
from tempfile import TemporaryDirectory

import PIL.Image
from aioconsole import aprint
from playwright.async_api import Browser as PlaywrightBrowser
from playwright.async_api import BrowserContext, Page, Playwright

from skillweaver.environment.a11y import capture_accessibility_tree
from skillweaver.environment.state import State

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"


def unique_id():
    return uuid.uuid4().hex


scount = 0


class Browser:
    def __init__(
        self,
        playwright_browser: PlaywrightBrowser,
        context: BrowserContext,
        active_page: Page,
        screen_size: tuple[int, int],
    ):
        """
        Use the `make_browser` helper method instead.
        """

        self.playwright_browser = playwright_browser
        self.context = context
        self.active_page = active_page
        self.temp_dir = TemporaryDirectory()
        self.dialog = None
        self.cdp_sessions = {}
        self.screen_size = screen_size

    async def _get_dom(self, page: Page):
        if page not in self.cdp_sessions:
            cdp = await self.context.new_cdp_session(page)
            self.cdp_sessions[page] = cdp
        else:
            cdp = self.cdp_sessions[page]
        dom_snapshot = await cdp.send(
            "DOMSnapshot.captureSnapshot",
            {
                "computedStyles": ["visibility", "display"],
                # Provides clientRect, scrollRect, etc.
                "includeDOMRects": True,
            },  # type: ignore (DOMSnapshot)
        )
        return dom_snapshot

    async def _screenshot(self, page: Page) -> tuple[PIL.Image.Image, PIL.Image.Image]:
        global scount
        assert (
            self.dialog is None
        ), "Cannot take any action while a dialog is open (action: screenshot)."

        # Returns the full and cropped screenshot paths
        scount += 1
        screenshot_path_full = os.path.join(
            self.temp_dir.name, f"screenshot_full{scount}.png"
        )
        screenshot_path = os.path.join(self.temp_dir.name, f"screenshot{scount}.png")
        await page.screenshot(full_page=True, path=screenshot_path_full, timeout=15000)
        await page.screenshot(full_page=False, path=screenshot_path, timeout=15000)
        
        # Read image and copy to memory, then close file handle
        with PIL.Image.open(screenshot_path) as img:
            screenshot = img.copy()
        with PIL.Image.open(screenshot_path_full) as img_full:
            screenshot_full = img_full.copy()

        # On Windows, need to wait for file handle release
        import sys
        if sys.platform == 'win32':
            import gc
            gc.collect()
            try:
                os.remove(screenshot_path_full)
            except PermissionError:
                pass  # Ignore Windows file lock issues
            try:
                os.remove(screenshot_path)
            except PermissionError:
                pass
        else:
            os.remove(screenshot_path_full)
            os.remove(screenshot_path)

        return (screenshot, screenshot_full)

    async def _observe(self) -> State:
        await self.active_page.wait_for_load_state("load")
        return State(
            id=unique_id(),
            url=self.active_page.url,
            title=await self.active_page.title(),
            timestamp=time.time(),
            screenshot=(await self._screenshot(self.active_page))[0],  # BUG
            dom=await self._get_dom(self.active_page),
            dialog=self.dialog,
            accessibility_tree=await capture_accessibility_tree(self.active_page),
        )

    async def observe(self) -> State:
        exc = None
        for attempt in range(3):
            try:
                return await self._observe()
            except Exception as e:
                if (
                    "Execution context was destroyed, most likely because of a navigation"
                    in str(e)
                    and attempt < 2
                ):
                    await aprint("Page navigated after action completed. Retrying.")
                    await asyncio.sleep(2)
                    exc = e
                    continue
                else:
                    raise e

        raise exc  # type: ignore

    async def close(self):
        await self.active_page.close()
        await self.context.close()
        await self.playwright_browser.close()


async def make_browser(
    playwright: Playwright,
    start_url: str,
    storage_state: str | None = None,
    headless=True,
    width=1280,
    height=1440,
    # height=720, # NOTE
    locale="en-US",
    args=(),
    video_dir=None,
    navigation_timeout=16000,
    timeout=5000,
):
    browser = await playwright.chromium.launch(
        traces_dir=None,
        headless=headless,
        args=[
            "--incognito",
            "--disable-blink-features=AutomationControlled",
            "--ignore-certificate-errors",
            "--disable-features=CrossSiteDocumentBlockingAlways,CrossSiteDocumentBlockingIfIsolating",
            *args,
        ],
        chromium_sandbox=True if not os.getenv("DOCKER") else False,
        ignore_default_args=["--hide-scrollbars"],
    )
    context = await browser.new_context(
        storage_state=storage_state,
        user_agent=USER_AGENT,
        viewport={"width": width, "height": height},
        locale=locale,
        record_video_dir=video_dir,
        # record_har_path=har_path,
        # geolocation=geolocation,
    )
    context.set_default_timeout(timeout)
    context.set_default_navigation_timeout(navigation_timeout)
    # BUG in Playwright:
    page = await context.new_page()
    await page.goto(start_url)  # state_url
    content = await page.content()
    await aprint("went to", start_url)
    return Browser(browser, context, page, screen_size=(height, width))


async def make_browser_cdp(
    playwright: Playwright,
    cdp_url: str = "http://localhost:9222",
    target_url_filter: str = None,
    width=1280,
    height=720,
    timeout=5000,
    navigation_timeout=16000,
):
    """
    Connect to existing browser instance (via CDP)
    Used to connect to NogicOS embedded webview
    
    Args:
        playwright: Playwright instance
        cdp_url: CDP endpoint URL, default http://localhost:9222
        target_url_filter: Target page URL filter (to locate webview)
        width: Viewport width
        height: Viewport height
    
    Returns:
        Browser instance
    """
    import urllib.request
    import json
    
    await aprint(f"[CDP] Connecting to {cdp_url}...")
    
    try:
        # Step 1: Get CDP targets list, find webview WebSocket URL
        webview_ws_url = None
        try:
            with urllib.request.urlopen(f"{cdp_url}/json", timeout=5) as response:
                targets = json.loads(response.read().decode('utf-8', errors='replace'))
                await aprint(f"[CDP] Found {len(targets)} targets")
                
                for target in targets:
                    target_type = target.get('type', '')
                    target_url = target.get('url', '')
                    ws_url = target.get('webSocketDebuggerUrl', '')
                    
                    await aprint(f"[CDP] Target: type={target_type}, url={target_url[:60] if target_url else 'N/A'}...")
                    
                    # Find webview type or non- file://  pages
                    if target_type == 'webview':
                        webview_ws_url = ws_url
                        await aprint(f"[CDP] Found webview target: {target_url}")
                        break
                    elif target_type == 'page' and not target_url.startswith('file://'):
                        if target_url_filter is None or target_url_filter in target_url:
                            webview_ws_url = ws_url
                            await aprint(f"[CDP] Found matching page target: {target_url}")
                            break
        except Exception as e:
            await aprint(f"[CDP] Failed to get targets: {e}")
        
        if not webview_ws_url:
            await aprint("[CDP] No webview target found, falling back to browser connection")
            # Fallback to original method
            browser = await playwright.chromium.connect_over_cdp(cdp_url)
            contexts = browser.contexts
            if contexts and contexts[0].pages:
                page = contexts[0].pages[0]
                return Browser(browser, contexts[0], page, screen_size=(height, width))
            raise RuntimeError("No suitable webview page found")
        
        # Step 2: Connect to browser, then get webview page via CDP session
        await aprint(f"[CDP] Connecting to browser and targeting webview...")
        
        # Connect at browser level
        browser = await playwright.chromium.connect_over_cdp(cdp_url)
        await aprint("[CDP] Connected to browser")
        
        # Use CDP to directly connect to webview target
        # Extract target ID from webview_ws_url
        # Format: ws://localhost:9222/devtools/page/TARGET_ID
        target_id = webview_ws_url.split('/')[-1]
        await aprint(f"[CDP] Target ID: {target_id}")
        
        # Create new context to connect to webview
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        context.set_default_timeout(timeout)
        context.set_default_navigation_timeout(navigation_timeout)
        
        # Try to attach to webview target via CDP session
        try:
            cdp_session = await context.new_cdp_session(context.pages[0] if context.pages else None)
            # Get all targets
            targets_result = await cdp_session.send("Target.getTargets")
            await aprint(f"[CDP] Targets: {len(targets_result.get('targetInfos', []))}")
            
            # Find webview target and attach
            for target_info in targets_result.get('targetInfos', []):
                if target_info.get('type') == 'page' and target_info.get('targetId') == target_id:
                    await aprint(f"[CDP] Found target, attaching...")
                    attach_result = await cdp_session.send("Target.attachToTarget", {
                        "targetId": target_id,
                        "flatten": True
                    })
                    await aprint(f"[CDP] Attached: {attach_result}")
                    break
        except Exception as cdp_err:
            await aprint(f"[CDP] CDP session error (non-fatal): {cdp_err}")
        
        # Iterate all pages to find webview
        page = None
        for ctx in browser.contexts:
            for p in ctx.pages:
                if not p.url.startswith('file://') and p.url != 'about:blank':
                    page = p
                    context = ctx
                    await aprint(f"[CDP] Found webview page: {p.url}")
                    break
            if page:
                break
        
        if not page:
            # If still not found, use the first available page
            if browser.contexts and browser.contexts[0].pages:
                page = browser.contexts[0].pages[0]
                context = browser.contexts[0]
                await aprint(f"[CDP] Using fallback page: {page.url}")
            else:
                raise RuntimeError("No pages found")
        
        await aprint(f"[CDP] Final page URL: {page.url}")
        
        return Browser(browser, context, page, screen_size=(height, width))
        
    except Exception as e:
        await aprint(f"[CDP] Connection failed: {e}")
        raise


async def make_browsers(
    playwright: Playwright,
    start_urls: list[str],
    storage_states: list[str | None],
    headless=True,
    width=1280,
    height=1440,
    # height=720, # NOTE
    locale="en-US",
    args=(),
    video_dirs=None,
    navigation_timeout=16000,
    timeout=5000,
):
    browser = await playwright.chromium.launch(
        traces_dir=None,
        headless=headless,
        args=[
            "--incognito",
            "--disable-blink-features=AutomationControlled",
            "--ignore-certificate-errors",
            "--disable-features=CrossSiteDocumentBlockingAlways,CrossSiteDocumentBlockingIfIsolating",
            *args,
        ],
        chromium_sandbox=True if not os.getenv("DOCKER") else False,
        ignore_default_args=["--hide-scrollbars"],
    )

    async def __make(storage_state, start_url, video_dir):
        context = await browser.new_context(
            storage_state=storage_state,
            user_agent=USER_AGENT,
            viewport={"width": width, "height": height},
            locale=locale,
            record_video_dir=video_dir,
        )
        context.set_default_timeout(timeout)
        context.set_default_navigation_timeout(navigation_timeout)
        page = await context.new_page()
        await aprint("made new_page")
        await page.goto(start_url)
        await aprint("went to", start_url)
        return Browser(browser, context, page, screen_size=(height, width))

    return await asyncio.gather(
        *[
            __make(storage_state, start_url, video_dir)
            for storage_state, start_url, video_dir in zip(
                storage_states, start_urls, video_dirs or [None] * len(storage_states)
            )
        ]
    )
