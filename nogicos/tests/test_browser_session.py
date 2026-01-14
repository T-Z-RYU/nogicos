# -*- coding: utf-8 -*-
"""
Browser Session Diagnostic Test

Verify:
1. Playwright availability
2. BrowserSession startup
3. Registry context injection
4. Browser Tools session access
"""

import asyncio
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_browser_session():
    print("=" * 60)
    print("Browser Session 诊断Test")
    print("=" * 60)
    
    # Test 1: Playwright Availableproperty
    print("\n[Test 1] Playwright Available性")
    try:
        from playwright.async_api import async_playwright
        print("  [OK] Playwright 已安装")
    except ImportError as e:
        print(f"  [FAIL] Playwright 未安装: {e}")
        print("  Running: pip install playwright && playwright install chromium")
        return False
    
    # Test 2: BrowserSession ModuleImport
    print("\n[Test 2] BrowserSession ModuleImport")
    try:
        from engine.browser import (
            BrowserSession,
            get_browser_session,
            close_browser_session,
            PLAYWRIGHT_AVAILABLE
        )
        print(f"  [OK] ImportSuccess")
        print(f"  PLAYWRIGHT_AVAILABLE = {PLAYWRIGHT_AVAILABLE}")
    except ImportError as e:
        print(f"  [FAIL] ImportFailed: {e}")
        return False
    
    # Test 3: BrowserSession Start
    print("\n[Test 3] BrowserSession Start")
    session = BrowserSession(headless=True)
    started = await session.start()
    if started:
        print("  [OK] Session StartSuccess")
        print(f"  is_started = {session.is_started}")
    else:
        print("  [FAIL] Session StartFailed")
        return False
    
    # Test 4: NavigationTest
    print("\n[Test 4] 导航Test")
    try:
        navigated = await session.navigate("https://example.com", timeout=10.0)
        if navigated:
            title = await session.get_title()
            url = await session.get_current_url()
            print(f"  [OK] 导航Success")
            print(f"  URL: {url}")
            print(f"  Title: {title}")
        else:
            print("  [FAIL] 导航Failed")
    except Exception as e:
        print(f"  [FAIL] 导航Exception: {e}")
    
    # Test 5: InnercontentExtraction
    print("\n[Test 5] Inner容提取")
    try:
        content = await session.get_page_content()
        print(f"  [OK] 提取Success")
        print(f"  Inner容Length: {len(content)} Character")
        print(f"  Before 100 Character: {content[:100]}...")
    except Exception as e:
        print(f"  [FAIL] 提取Failed: {e}")
    
    # Test 6: Registry Context Test
    print("\n[Test 6] Registry Context 注入Test")
    try:
        from engine.tools import create_full_registry
        
        registry = create_full_registry()
        print(f"  Create Registry, ToolCount: {len(registry.get_all())}")
        
        # inject session
        registry.set_context("browser_session", session)
        
        # VerifyGet
        ctx_session = registry.get_context("browser_session")
        if ctx_session is session:
            print("  [OK] Context 注入Success")
        else:
            print(f"  [FAIL] Context 注入Failed: got {ctx_session}")
    except Exception as e:
        print(f"  [FAIL] Registry TestFailed: {e}")
    
    # Test 7: Browser Tool CallTest
    print("\n[Test 7] Browser Tool 调用Test")
    try:
        result = await registry.execute("browser_get_url", {})
        if result.success:
            print(f"  [OK] Tool调用Success")
            print(f"  Result: {result.output}")
        else:
            print(f"  [FAIL] Tool调用Failed: {result.error}")
    except Exception as e:
        print(f"  [FAIL] Tool调用Exception: {e}")
    
    # Cleanup
    print("\n[Cleanup] Close Session")
    await session.stop()
    print("  [OK] Session 已Close")
    
    print("\n" + "=" * 60)
    print("诊断Complete")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    asyncio.run(test_browser_session())

