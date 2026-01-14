# -*- coding: utf-8 -*-
"""
Direct Tool Testing - Tests tools without LLM involvement

This script directly tests tool functionality to establish
a baseline before testing the full agent.
"""

import asyncio
import os
import sys
import json
import time
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.benchmark.evaluators import (
    StringEvaluator, URLEvaluator, FileEvaluator, 
    create_evaluator, EvaluationResult
)


async def run_direct_tool_tests():
    """Run direct tool tests without LLM"""
    print("=" * 60)
    print("NogicOS Direct Tool Testing")
    print("Based on WebArena/OSWorld Standards")
    print("=" * 60)
    
    # Import tools
    try:
        from engine.tools import create_full_registry
        from engine.browser.session import get_browser_session, close_browser_session, PLAYWRIGHT_AVAILABLE
        registry = create_full_registry()
        print(f"\n[Setup] Registry created with {len(registry.get_all())} tools")
    except Exception as e:
        print(f"[FAIL] Failed to create registry: {e}")
        return
    
    results = []
    
    # ========================================
    # Section 1: Local Tools
    # ========================================
    print("\n" + "=" * 40)
    print("SECTION 1: Local Tools")
    print("=" * 40)
    
    # Test L001: list_directory
    print("\n[L001] list_directory")
    try:
        result = await registry.execute("list_directory", {"path": "."})
        evaluator = StringEvaluator(mode="regex")
        eval_result = evaluator.evaluate(result.output, r"\[FILE\]|\[DIR\]")
        status = "[PASS]" if eval_result.passed else "[FAIL]"
        print(f"  {status} {eval_result.message}")
        print(f"  Output: {str(result.output)[:100]}...")
        results.append(("L001", "list_directory", eval_result.passed, result.success))
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        results.append(("L001", "list_directory", False, False))
    
    # Test L002: read_file
    print("\n[L002] read_file")
    try:
        result = await registry.execute("read_file", {"path": "README.md"})
        evaluator = StringEvaluator(mode="must_include")
        eval_result = evaluator.evaluate(result.output, ["nogic"])
        status = "[PASS]" if result.success else "[FAIL]"
        print(f"  {status} Tool execution: {result.success}")
        print(f"  Evaluator: {eval_result.message}")
        print(f"  Output length: {len(str(result.output))} chars")
        results.append(("L002", "read_file", eval_result.passed, result.success))
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        results.append(("L002", "read_file", False, False))
    
    # Test L003: write_file
    print("\n[L003] write_file")
    test_file = "./benchmark_direct_test.txt"
    test_content = "Hello Direct Benchmark Test"
    try:
        result = await registry.execute("write_file", {"path": test_file, "content": test_content})
        # Check file exists and content matches
        evaluator = FileEvaluator(checks=[
            {"type": "exists"},
            {"type": "content_match", "expected": test_content}
        ])
        eval_result = evaluator.evaluate(test_file)
        status = "[PASS]" if eval_result.passed else "[FAIL]"
        print(f"  {status} {eval_result.message}")
        print(f"  Tool result: {result.output if result.success else result.error}")
        results.append(("L003", "write_file", eval_result.passed, result.success))
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        results.append(("L003", "write_file", False, False))
        if os.path.exists(test_file):
            os.remove(test_file)
    
    # Test L004: glob_search
    print("\n[L004] glob_search")
    try:
        result = await registry.execute("glob_search", {"pattern": "*.py", "root": "engine"})
        evaluator = StringEvaluator(mode="must_include")
        eval_result = evaluator.evaluate(result.output, [".py"])
        status = "[PASS]" if result.success and eval_result.passed else "[FAIL]"
        print(f"  {status} Tool: {result.success}, Eval: {eval_result.message}")
        print(f"  Output: {str(result.output)[:150]}...")
        results.append(("L004", "glob_search", eval_result.passed, result.success))
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        results.append(("L004", "glob_search", False, False))
    
    # Test L005: shell_execute
    print("\n[L005] shell_execute")
    try:
        result = await registry.execute("shell_execute", {"command": "python --version"})
        evaluator = StringEvaluator(mode="regex")
        eval_result = evaluator.evaluate(result.output, r"Python \d+\.\d+")
        status = "[PASS]" if result.success and eval_result.passed else "[FAIL]"
        print(f"  {status} Tool: {result.success}, Eval: {eval_result.message}")
        print(f"  Output: {result.output}")
        results.append(("L005", "shell_execute", eval_result.passed, result.success))
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        results.append(("L005", "shell_execute", False, False))
    
    # Test L006: grep_search
    print("\n[L006] grep_search")
    try:
        result = await registry.execute("grep_search", {"pattern": "import", "path": "engine"})
        evaluator = StringEvaluator(mode="regex")
        eval_result = evaluator.evaluate(result.output, r"import|\d+ match")
        status = "[PASS]" if result.success else "[FAIL]"
        print(f"  {status} Tool: {result.success}")
        print(f"  Output: {str(result.output)[:150]}...")
        results.append(("L006", "grep_search", result.success, result.success))
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        results.append(("L006", "grep_search", False, False))
    
    # ========================================
    # Section 2: Browser Tools
    # ========================================
    print("\n" + "=" * 40)
    print("SECTION 2: Browser Tools")
    print("=" * 40)
    
    if not PLAYWRIGHT_AVAILABLE:
        print("[SKIP] Playwright not available")
    else:
        # Initialize browser session
        try:
            browser_session = await get_browser_session()
            registry.set_context("browser_session", browser_session)
            print("[Setup] Browser session initialized")
            
            # Test B001: browser_navigate
            print("\n[B001] browser_navigate")
            try:
                result = await registry.execute("browser_navigate", {"url": "https://example.com"})
                status = "[PASS]" if result.success else "[FAIL]"
                print(f"  {status} {result.output if result.success else result.error}")
                results.append(("B001", "browser_navigate", result.success, result.success))
            except Exception as e:
                print(f"  [FAIL] Exception: {e}")
                results.append(("B001", "browser_navigate", False, False))
            
            # Test B002: browser_get_url
            print("\n[B002] browser_get_url")
            try:
                result = await registry.execute("browser_get_url", {})
                evaluator = URLEvaluator(mode="contains")
                eval_result = evaluator.evaluate(result.output, "example.com")
                status = "[PASS]" if result.success and eval_result.passed else "[FAIL]"
                print(f"  {status} URL: {result.output}")
                results.append(("B002", "browser_get_url", eval_result.passed, result.success))
            except Exception as e:
                print(f"  [FAIL] Exception: {e}")
                results.append(("B002", "browser_get_url", False, False))
            
            # Test B003: browser_get_title
            print("\n[B003] browser_get_title")
            try:
                result = await registry.execute("browser_get_title", {})
                evaluator = StringEvaluator(mode="must_include")
                eval_result = evaluator.evaluate(result.output, ["example"])
                status = "[PASS]" if result.success else "[FAIL]"
                print(f"  {status} Title: {result.output}")
                results.append(("B003", "browser_get_title", result.success, result.success))
            except Exception as e:
                print(f"  [FAIL] Exception: {e}")
                results.append(("B003", "browser_get_title", False, False))
            
            # Test B004: browser_get_content
            print("\n[B004] browser_get_content")
            try:
                result = await registry.execute("browser_get_content", {})
                evaluator = StringEvaluator(mode="must_include")
                eval_result = evaluator.evaluate(result.output, ["Example Domain"])
                status = "[PASS]" if result.success and eval_result.passed else "[FAIL]"
                print(f"  {status} Content length: {len(str(result.output))} chars")
                results.append(("B004", "browser_get_content", eval_result.passed, result.success))
            except Exception as e:
                print(f"  [FAIL] Exception: {e}")
                results.append(("B004", "browser_get_content", False, False))
            
            # Cleanup browser
            await close_browser_session()
            print("[Cleanup] Browser session closed")
            
        except Exception as e:
            print(f"[FAIL] Browser setup failed: {e}")
    
    # ========================================
    # Summary
    # ========================================
    print("\n" + "=" * 60)
    print("DIRECT TOOL TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for r in results if r[2])
    total = len(results)
    success_rate = passed / total if total > 0 else 0
    
    print(f"\nOverall: {passed}/{total} passed ({success_rate:.1%})")
    
    # Group by section
    local_results = [r for r in results if r[0].startswith("L")]
    browser_results = [r for r in results if r[0].startswith("B")]
    
    print(f"\nLocal Tools: {sum(1 for r in local_results if r[2])}/{len(local_results)}")
    for r in local_results:
        status = "[PASS]" if r[2] else "[FAIL]"
        print(f"  {r[0]} {r[1]:20} {status}")
    
    print(f"\nBrowser Tools: {sum(1 for r in browser_results if r[2])}/{len(browser_results)}")
    for r in browser_results:
        status = "[PASS]" if r[2] else "[FAIL]"
        print(f"  {r[0]} {r[1]:20} {status}")
    
    # Level assessment based on tool pass rate
    if success_rate >= 0.85:
        level = "L4 (Launch Ready)"
    elif success_rate >= 0.70:
        level = "L3 (Beta)"
    elif success_rate >= 0.50:
        level = "L2 (Alpha)"
    else:
        level = "L1 (Prototype)"
    
    print(f"\nTool Layer Maturity: {level}")
    print("=" * 60)
    
    # Return results for further analysis
    return {
        "success_rate": success_rate,
        "passed": passed,
        "total": total,
        "results": results,
        "level": level,
    }


if __name__ == "__main__":
    asyncio.run(run_direct_tool_tests())


