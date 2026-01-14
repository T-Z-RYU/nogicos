# -*- coding: utf-8 -*-
"""
Quick Browser Test - Verify Browser Session YesNo工作
"""
import asyncio
import sys
import os

# Set UTF-8 Encode
os.environ["PYTHONIOENCODING"] = "utf-8"

async def test_browser():
    print("=" * 50)
    print("NogicOS Browser Test")
    print("=" * 50)
    
    # Step 1: Check Playwright YesNoAvailable
    print("\n[1/4] Checking Playwright...")
    try:
        from playwright.async_api import async_playwright
        print("[OK] Playwright installed")
    except ImportError:
        print("[FAIL] Playwright not installed")
        print("   Run: pip install playwright && playwright install")
        return False
    
    # Step 2: Check BrowserSession Module
    print("\n[2/4] Checking BrowserSession module...")
    try:
        from engine.browser.session import BrowserSession, get_browser_session
        print("[OK] BrowserSession module available")
    except ImportError as e:
        print(f"[FAIL] BrowserSession import failed: {e}")
        return False
    
    # Step 3: Initialize Browser Session
    print("\n[3/4] Initializing Browser Session...")
    try:
        session = BrowserSession(headless=True)
        started = await session.start()
        if started:
            print("[OK] Browser Session started")
        else:
            print("[FAIL] Browser Session failed to start")
            return False
    except Exception as e:
        print(f"[FAIL] Browser Session init error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: TestBrowserAction
    print("\n[4/4] Testing browser operations...")
    try:
        # Navigationto YC official website
        print("   -> Navigating to https://www.ycombinator.com ...")
        nav_result = await session.navigate("https://www.ycombinator.com")
        if nav_result:
            print("   [OK] Navigation successful")
        else:
            print("   [FAIL] Navigation failed")
            await session.stop()
            return False
        
        # GetpageInfo
        url = await session.get_current_url()
        title = await session.get_title()
        print(f"   [OK] URL: {url}")
        print(f"   [OK] Title: {title}")
        
        # ExtractionpageInnercontent
        content = await session.get_page_content()
        content_len = len(content) if content else 0
        print(f"   [OK] Content length: {content_len} chars")
        if content:
            # onlyDisplay ASCII Security's Innercontent
            safe_preview = ''.join(c if ord(c) < 128 else '?' for c in content[:100])
            print(f"   [OK] Content preview: {safe_preview}...")
        
        # captureGraph
        print("   -> Taking screenshot...")
        screenshot = await session.screenshot()
        if screenshot:
            print(f"   [OK] Screenshot: {len(screenshot)} bytes")
            # SavecaptureGraph
            with open("test_screenshot.png", "wb") as f:
                f.write(screenshot)
            print("   [OK] Screenshot saved: test_screenshot.png")
        else:
            print("   [FAIL] Screenshot failed")
        
        # Cleanup
        await session.stop()
        print("\n[OK] Browser Session closed")
        
    except Exception as e:
        print(f"   [FAIL] Browser operation error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await session.stop()
        except:
            pass
        return False
    
    print("\n" + "=" * 50)
    print("[SUCCESS] All tests passed! Browser works!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    result = asyncio.run(test_browser())
    sys.exit(0 if result else 1)
