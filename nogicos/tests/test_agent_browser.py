# -*- coding: utf-8 -*-
"""
Agent Browser Integration Test

Test the full flow from Agent to Browser execution
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


async def test_agent_browser():
    print("=" * 60)
    print("Agent Browser Integration Test")
    print("=" * 60)
    
    # Test 1: Check imports
    print("\n[Test 1] Agent imports check")
    try:
        from engine.agent.imports import (
            BROWSER_SESSION_AVAILABLE,
            get_browser_session,
            close_browser_session,
            get_available_features
        )
        features = get_available_features()
        print(f"  Features: {features}")
        print(f"  BROWSER_SESSION_AVAILABLE = {BROWSER_SESSION_AVAILABLE}")
        
        if not BROWSER_SESSION_AVAILABLE:
            print("  [FAIL] Browser session not available in imports!")
            return False
        print("  [OK] Imports correct")
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False
    
    # Test 2: Classifier test
    print("\n[Test 2] Task Classification")
    try:
        from engine.agent.classifier import TaskClassifier
        
        classifier = TaskClassifier()
        
        test_tasks = [
            ("Open google.com", "browser"),
            ("List files on desktop", "local"),
            ("Search YC companies and save to file", "mixed"),
        ]
        
        for task, expected in test_tasks:
            result = classifier.classify(task)
            actual = result.task_type.value
            status = "[OK]" if actual == expected else f"[WARN] expected {expected}"
            print(f"  '{task[:30]}...' -> {actual} {status}")
    except Exception as e:
        print(f"  [FAIL] Classifier error: {e}")
    
    # Test 3: Agent with browser task
    print("\n[Test 3] Agent Browser Task Execution")
    try:
        from engine.agent.react_agent import ReActAgent
        
        # Create agent
        agent = ReActAgent(max_iterations=3)
        print(f"  Agent created")
        print(f"  Registry tools: {len(agent.registry.get_all())}")
        
        # Check browser session state before
        ctx_before = agent.registry.get_context("browser_session")
        print(f"  Context before: browser_session = {ctx_before}")
        
        # Execute a simple browser task
        print("  Executing: 'Open https://example.com and get the title'")
        result = await agent.run(
            task="Open https://example.com and get the page title",
            session_id="test_session"
        )
        
        # Check browser session state after
        ctx_after = agent.registry.get_context("browser_session")
        print(f"  Context after: browser_session = {type(ctx_after).__name__ if ctx_after else None}")
        
        # Check result
        print(f"  Result success: {result.success}")
        if result.success:
            print(f"  Response: {result.response[:200]}...")
            print("  [OK] Browser task executed")
        else:
            print(f"  Error: {result.error}")
            print("  [FAIL] Browser task failed")
        
        # Cleanup
        await agent.cleanup_browser_session()
        print("  [OK] Session cleaned up")
        
    except Exception as e:
        import traceback
        print(f"  [FAIL] Agent error: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_agent_browser())

