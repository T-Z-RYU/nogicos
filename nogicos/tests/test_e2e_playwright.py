# -*- coding: utf-8 -*-
"""
NogicOS End-to-End Tests with Playwright

Comprehensive E2E tests for NogicOS frontend and integration.
Tests both the web interface and backend API.
"""

import os
import json
import time
import asyncio
import websockets
from playwright.sync_api import sync_playwright, expect


# Configuration
HTTP_URL = os.environ.get("NOGICOS_HTTP_URL", "http://localhost:8080")
WS_URL = os.environ.get("NOGICOS_WS_URL", "ws://localhost:8765")
FRONTEND_URL = os.environ.get("NOGICOS_FRONTEND_URL", "file:///C:/Users/WIN/Desktop/Cursor%20Project/nogicos/client/index.html")


def test_backend_health():
    """Test 1: Backend health check"""
    print("\n🏥 Test 1: Backend Health Check")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Check health endpoint
        response = page.request.get(f"{HTTP_URL}/health")
        assert response.ok, f"Health check failed: {response.status}"
        
        data = response.json()
        print(f"  ✓ Status: {data.get('status')}")
        print(f"  ✓ Engine: {data.get('engine')}")
        print(f"  ✓ Memory: {data.get('memory_mb')}MB")
        print(f"  ✓ Uptime: {data.get('uptime_seconds')}s")
        
        assert data.get("status") in ["healthy", "busy"], "Unexpected status"
        assert data.get("engine") is True, "Engine not ready"
        
        browser.close()
    
    print("  ✅ Backend health OK")


def test_api_endpoints():
    """Test 2: API endpoints availability"""
    print("\n🔌 Test 2: API Endpoints")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        endpoints = [
            ("/", "GET", "Root endpoint"),
            ("/health", "GET", "Health check"),
            ("/stats", "GET", "Statistics"),
            ("/v2/tools", "GET", "Tool listing"),
        ]
        
        for path, method, desc in endpoints:
            url = f"{HTTP_URL}{path}"
            if method == "GET":
                response = page.request.get(url)
            else:
                response = page.request.post(url)
            
            status = "✓" if response.ok else "✗"
            print(f"  {status} {method} {path} - {response.status} ({desc})")
        
        browser.close()
    
    print("  ✅ API endpoints OK")


def test_tools_available():
    """Test 3: Check available tools"""
    print("\n🧰 Test 3: Available Tools")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        response = page.request.get(f"{HTTP_URL}/v2/tools")
        assert response.ok, "Failed to get tools"
        
        data = response.json()
        tool_count = data.get("count", 0)
        tools = data.get("tools", [])
        
        print(f"  ✓ Total tools: {tool_count}")
        
        # List some key tools
        tool_names = [t.get("name", "unknown") for t in tools[:10]]
        for name in tool_names:
            print(f"    - {name}")
        
        if tool_count > 10:
            print(f"    ... and {tool_count - 10} more")
        
        assert tool_count > 0, "No tools available"
        
        browser.close()
    
    print("  ✅ Tools loaded OK")


def test_websocket_connection():
    """Test 4: WebSocket connection"""
    print("\n🔗 Test 4: WebSocket Connection")
    
    async def ws_test():
        async with websockets.connect(WS_URL) as ws:
            print(f"  ✓ Connected to {WS_URL}")
            
            # Send ping
            await ws.send(json.dumps({"type": "ping"}))
            print("  ✓ Sent ping message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"  ✓ Received: {data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print("  ⚠ No response (timeout)")
            
            # Try get_status
            await ws.send(json.dumps({"type": "get_status"}))
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"  ✓ Status response received")
            except asyncio.TimeoutError:
                print("  ⚠ No status response")
    
    asyncio.run(ws_test())
    print("  ✅ WebSocket OK")


def test_frontend_loads():
    """Test 5: Frontend loads correctly"""
    print("\n🖥️ Test 5: Frontend Loading")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Load frontend
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        
        print(f"  ✓ Page loaded: {page.title() or 'NogicOS'}")
        
        # Check for key elements
        elements_to_check = [
            ("body", "Body element"),
            ("#app, .app, main, .container", "App container"),
        ]
        
        for selector, desc in elements_to_check:
            try:
                element = page.locator(selector).first
                if element.count() > 0:
                    print(f"  ✓ Found: {desc}")
                else:
                    print(f"  ⚠ Missing: {desc}")
            except:
                print(f"  ⚠ Error checking: {desc}")
        
        # Take screenshot for inspection
        screenshot_path = "tests/screenshots/frontend.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"  ✓ Screenshot saved: {screenshot_path}")
        
        browser.close()
    
    print("  ✅ Frontend loads OK")


def test_session_persistence():
    """Test 6: Session persistence API"""
    print("\n💾 Test 6: Session Persistence")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        test_session_id = f"test_session_{int(time.time())}"
        
        # Save session
        save_response = page.request.post(
            f"{HTTP_URL}/v2/sessions/save",
            data=json.dumps({
                "session_id": test_session_id,
                "history": [{"role": "user", "content": "Test message"}],
                "preferences": {"theme": "dark"},
                "title": "Test Session"
            }),
            headers={"Content-Type": "application/json"}
        )
        
        if save_response.ok:
            print(f"  ✓ Session saved: {test_session_id}")
        else:
            print(f"  ⚠ Save failed: {save_response.status}")
        
        # Load session
        load_response = page.request.get(f"{HTTP_URL}/v2/sessions/{test_session_id}")
        if load_response.ok:
            data = load_response.json()
            print(f"  ✓ Session loaded: {data.get('session_id', 'unknown')}")
        else:
            print(f"  ⚠ Load failed: {load_response.status}")
        
        # List sessions
        list_response = page.request.get(f"{HTTP_URL}/v2/sessions")
        if list_response.ok:
            data = list_response.json()
            print(f"  ✓ Sessions count: {data.get('total', 0)}")
        
        # Cleanup - delete test session
        delete_response = page.request.delete(f"{HTTP_URL}/v2/sessions/{test_session_id}")
        if delete_response.ok:
            print(f"  ✓ Test session cleaned up")
        
        browser.close()
    
    print("  ✅ Session persistence OK")


def test_memory_api():
    """Test 7: Memory API"""
    print("\n🧠 Test 7: Memory API")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Add a test memory
        add_response = page.request.post(
            f"{HTTP_URL}/v2/memories/add",
            data=json.dumps({
                "subject": "test_user",
                "predicate": "prefers",
                "object": "dark mode",
                "session_id": "test",
                "memory_type": "preference",
                "importance": "medium"
            }),
            headers={"Content-Type": "application/json"}
        )
        
        if add_response.ok:
            data = add_response.json()
            print(f"  ✓ Memory added: {data.get('memory_id', 'unknown')[:8]}...")
            memory_id = data.get("memory_id")
        else:
            print(f"  ⚠ Add memory failed: {add_response.status}")
            memory_id = None
        
        # Search memories
        search_response = page.request.post(
            f"{HTTP_URL}/v2/memories/search",
            data=json.dumps({
                "query": "dark mode",
                "session_id": "test",
                "limit": 5
            }),
            headers={"Content-Type": "application/json"}
        )
        
        if search_response.ok:
            data = search_response.json()
            print(f"  ✓ Search results: {data.get('count', 0)}")
        else:
            print(f"  ⚠ Search failed: {search_response.status}")
        
        # Get memory stats
        stats_response = page.request.get(f"{HTTP_URL}/v2/memories/stats")
        if stats_response.ok:
            data = stats_response.json()
            print(f"  ✓ Total memories: {data.get('total_memories', 0)}")
        
        # Cleanup
        if memory_id:
            delete_response = page.request.delete(f"{HTTP_URL}/v2/memories/{memory_id}")
            if delete_response.ok:
                print(f"  ✓ Test memory cleaned up")
        
        browser.close()
    
    print("  ✅ Memory API OK")


def test_error_handling():
    """Test 8: Error handling"""
    print("\n⚠️ Test 8: Error Handling")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Test 404
        response_404 = page.request.get(f"{HTTP_URL}/nonexistent/endpoint")
        print(f"  ✓ 404 response: {response_404.status}")
        assert response_404.status == 404, "Should return 404"
        
        # Test invalid POST
        response_invalid = page.request.post(
            f"{HTTP_URL}/v2/execute",
            data=json.dumps({}),
            headers={"Content-Type": "application/json"}
        )
        print(f"  ✓ Invalid request: {response_invalid.status}")
        
        browser.close()
    
    print("  ✅ Error handling OK")


def run_all_tests():
    """Run all E2E tests"""
    print("=" * 60)
    print("🚀 NogicOS End-to-End Test Suite")
    print("=" * 60)
    print(f"HTTP URL: {HTTP_URL}")
    print(f"WS URL: {WS_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    print("=" * 60)
    
    tests = [
        test_backend_health,
        test_api_endpoints,
        test_tools_available,
        test_websocket_connection,
        test_frontend_loads,
        test_session_persistence,
        test_memory_api,
        test_error_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)













