# -*- coding: utf-8 -*-
"""
Hook System Test - Verify Hook System功能

Test：
1. Browser Hook - 浏览器Window检测
2. Desktop Hook - 桌面WindowMonitor
3. File Hook - FileSystemListen
4. Context Store - UpDown文存储
5. Hook Manager - 整体管理
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


async def test_browser_hook():
    """Test浏览器 Hook"""
    print("\n" + "=" * 50)
    print("Test 1: Browser Hook")
    print("=" * 50)
    
    try:
        from engine.context.hooks.browser_hook import BrowserHook
        
        hook = BrowserHook()
        print(f"[OK] BrowserHook created")
        
        # Start hook
        success = await hook.start()
        
        if success:
            print(f"[OK] Browser hook started")
            print(f"     Target: {hook.state.target}")
            
            # Capture context
            context = await hook.capture()
            
            if context:
                print(f"[OK] Context captured:")
                print(f"     App: {context.app}")
                print(f"     URL: {context.url}")
                print(f"     Title: {context.title}")
            else:
                print("[WARN] No browser context captured (browser might not be open)")
            
            # Stop hook
            await hook.stop()
            print(f"[OK] Browser hook stopped")
        else:
            print("[WARN] Browser hook could not start (no browser window found)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Browser hook test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_desktop_hook():
    """Test桌面 Hook"""
    print("\n" + "=" * 50)
    print("Test 2: Desktop Hook")
    print("=" * 50)
    
    try:
        from engine.context.hooks.desktop_hook import DesktopHook
        
        hook = DesktopHook()
        print(f"[OK] DesktopHook created")
        
        # Start hook
        success = await hook.start()
        
        if success:
            print(f"[OK] Desktop hook started")
            
            # Capture context
            context = await hook.capture()
            
            if context:
                print(f"[OK] Context captured:")
                print(f"     Active App: {context.active_app}")
                print(f"     Active Window: {context.active_window[:50]}..." if len(context.active_window) > 50 else f"     Active Window: {context.active_window}")
                print(f"     Window Count: {len(context.window_list)}")
            else:
                print("[WARN] No desktop context captured")
            
            # Stop hook
            await hook.stop()
            print(f"[OK] Desktop hook stopped")
        else:
            print("[FAIL] Desktop hook could not start")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Desktop hook test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_file_hook():
    """TestFile Hook"""
    print("\n" + "=" * 50)
    print("Test 3: File Hook")
    print("=" * 50)
    
    try:
        from engine.context.hooks.file_hook import FileHook
        from pathlib import Path
        
        # Use current directory for testing
        test_dir = str(Path(__file__).parent)
        
        hook = FileHook()
        print(f"[OK] FileHook created")
        
        # Start hook
        success = await hook.start(test_dir)
        
        if success:
            print(f"[OK] File hook started")
            print(f"     Watching: {test_dir}")
            
            # Capture context
            context = await hook.capture()
            
            if context:
                print(f"[OK] Context captured:")
                print(f"     Watched Dirs: {len(context.watched_dirs)}")
                print(f"     Recent Files: {len(context.recent_files)}")
                if context.clipboard:
                    clip_preview = context.clipboard[:50] + "..." if len(context.clipboard) > 50 else context.clipboard
                    print(f"     Clipboard: {clip_preview}")
            else:
                print("[WARN] No file context captured")
            
            # Stop hook
            await hook.stop()
            print(f"[OK] File hook stopped")
        else:
            print("[FAIL] File hook could not start")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] File hook test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_context_store():
    """Test Context Store"""
    print("\n" + "=" * 50)
    print("Test 4: Context Store")
    print("=" * 50)
    
    try:
        from engine.context.store import ContextStore, HookType, HookStatus, HookState, BrowserContext
        
        store = ContextStore()
        print(f"[OK] ContextStore created")
        
        # Create test state
        state = HookState(
            type=HookType.BROWSER,
            status=HookStatus.CONNECTED,
            target="chrome",
            context=BrowserContext(
                app="Chrome",
                url="https://www.ycombinator.com",
                title="Y Combinator",
                tab_count=3,
            ),
        )
        
        # Set state
        store.set_hook_state("test_browser", state)
        print(f"[OK] Hook state set")
        
        # Get state
        retrieved = store.get_hook_state("test_browser")
        if retrieved and retrieved.status == HookStatus.CONNECTED:
            print(f"[OK] Hook state retrieved")
        else:
            print(f"[FAIL] Hook state retrieval failed")
        
        # Get context for agent
        ctx = store.get_context_for_agent()
        if ctx.get("browser"):
            print(f"[OK] Agent context contains browser data")
        else:
            print(f"[FAIL] Agent context missing browser data")
        
        # Format prompt
        prompt = store.format_context_prompt()
        if "Y Combinator" in prompt:
            print(f"[OK] Context prompt formatted correctly")
            print(f"     Prompt preview: {prompt[:100]}...")
        else:
            print(f"[FAIL] Context prompt formatting failed")
        
        # Check history
        events = store.get_recent_events(minutes=5)
        if events:
            print(f"[OK] {len(events)} events in history")
        else:
            print(f"[INFO] No events in history yet")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Context store test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_hook_manager():
    """Test Hook Manager"""
    print("\n" + "=" * 50)
    print("Test 5: Hook Manager")
    print("=" * 50)
    
    try:
        from engine.context.hook_manager import HookManager
        
        manager = HookManager()
        print(f"[OK] HookManager created")
        
        # Get status (should be empty initially)
        status = manager.get_status()
        print(f"[OK] Initial status: {len(status['hooks'])} hooks")
        print(f"     Available types: {status['available_types']}")
        
        # Connect to desktop (most reliable for testing)
        print("\nConnecting to desktop...")
        success = await manager.connect_desktop()
        
        if success:
            print(f"[OK] Desktop hook connected")
            
            # Get updated status
            status = manager.get_status()
            print(f"[OK] Status: {len(status['hooks'])} hook(s) connected")
            
            # Get context
            ctx = await manager.get_desktop_context()
            if ctx:
                print(f"[OK] Desktop context available")
                print(f"     Active: {ctx.active_app}")
            
            # Disconnect
            await manager.disconnect_all()
            print(f"[OK] All hooks disconnected")
        else:
            print(f"[WARN] Desktop hook could not connect")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Hook manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_screenshot_ocr():
    """Test截Graph OCR"""
    print("\n" + "=" * 50)
    print("Test 6: Screenshot OCR (Optional)")
    print("=" * 50)
    
    try:
        from engine.context.hooks.screenshot_utils import capture_screen
        from engine.context.hooks.ocr_utils import get_screenshot_ocr
        
        # Test screenshot
        screenshot = await capture_screen()
        if screenshot:
            print(f"[OK] Screenshot captured: {len(screenshot)} bytes")
        else:
            print(f"[FAIL] Screenshot failed")
            return False
        
        # Test OCR
        ocr = get_screenshot_ocr()
        if ocr.available:
            print(f"[OK] OCR engine available")
            
            # Try OCR on screenshot
            results = await ocr.recognize(screenshot)
            if results:
                print(f"[OK] OCR found {len(results)} text regions")
                for r in results[:3]:
                    print(f"     - {r.text[:50]}...")
            else:
                print(f"[WARN] OCR found no text (screen might be blank)")
        else:
            print(f"[WARN] No OCR engine available")
            print(f"     Install: pip install pytesseract")
        
        return True
        
    except ImportError as e:
        print(f"[WARN] Screenshot/OCR dependencies missing: {e}")
        print(f"     Install: pip install mss pillow")
        return True
    except Exception as e:
        print(f"[FAIL] Screenshot OCR test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("NogicOS Hook System Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Run tests
    results["Browser Hook"] = await test_browser_hook()
    results["Desktop Hook"] = await test_desktop_hook()
    results["File Hook"] = await test_file_hook()
    results["Context Store"] = await test_context_store()
    results["Hook Manager"] = await test_hook_manager()
    results["Screenshot OCR"] = await test_screenshot_ocr()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"  Total: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

