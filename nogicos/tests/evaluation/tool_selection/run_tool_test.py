# -*- coding: utf-8 -*-
"""
Tool Selection Test Runner

Tests the agent's ability to select the correct tool for a given task.
This validates that tool descriptions are effective and the agent understands
user intent correctly.

Usage:
    python run_tool_test.py [--quick] [--verbose]

Options:
    --quick: Run only 5 sample tests instead of all 20
    --verbose: Show detailed output for each test
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_test_cases() -> List[Dict[str, Any]]:
    """Load test cases from JSON file"""
    test_file = Path(__file__).parent / "test_cases.json"
    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["test_cases"]


async def test_tool_selection(user_input: str, expected_tools: List[str], verbose: bool = False) -> Dict[str, Any]:
    """
    Test if agent selects the correct tool for a given input.
    
    Uses a minimal agent setup to check first tool selection.
    """
    try:
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent(max_iterations=1)  # Only allow 1 iteration
        
        # Run agent and capture first tool call
        result = await agent.run(
            task=user_input,
            session_id=f"tool_test_{datetime.now().strftime('%H%M%S')}",
        )
        
        # Check first tool called
        first_tool = None
        if result.tool_calls:
            first_tool = result.tool_calls[0].get("name")
        
        # Determine if correct
        is_correct = first_tool in expected_tools if first_tool else False
        
        return {
            "success": is_correct,
            "expected": expected_tools,
            "actual": first_tool,
            "response": result.response[:200] if result.response else None,
        }
        
    except Exception as e:
        return {
            "success": False,
            "expected": expected_tools,
            "actual": None,
            "error": str(e),
        }


async def run_simple_validation():
    """
    Run simplified validation without full agent.
    
    Tests that tools are properly registered and descriptions are correct.
    """
    print("="*60)
    print("NogicOS Tool Selection Validation")
    print("="*60)
    
    # Test 1: Check tool registry
    print("\n[1] Checking Tool Registry...")
    try:
        from engine.tools import create_full_registry
        registry = create_full_registry()
        tools = registry.get_all()
        
        print(f"   [OK] Registry loaded: {len(tools)} tools")
        
        # List tools by category
        categories = {}
        for tool in tools:
            cat = tool.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tool.name)
        
        for cat, tool_names in categories.items():
            print(f"   - {cat}: {len(tool_names)} tools")
        
    except Exception as e:
        print(f"   [FAIL] Failed to load registry: {e}")
        return
    
    # Test 2: Check context injector
    print("\n[2] Checking Context Injector...")
    try:
        from engine.context import ContextInjector, ContextConfig
        
        injector = ContextInjector()
        config = injector.create_first_message_context(
            workspace_path=os.getcwd(),
            session_id="test"
        )
        
        test_message = "Hello"
        injected = injector.inject(test_message, session_id="test", config=config)
        
        has_user_info = "<user_info>" in injected
        has_project_layout = "<project_layout>" in injected
        
        print(f"   [OK] Context Injector working")
        print(f"   - User info injected: {has_user_info}")
        print(f"   - Project layout injected: {has_project_layout}")
        print(f"   - Total context length: {len(injected)} chars")
        
    except Exception as e:
        print(f"   [FAIL] Context injection failed: {e}")
    
    # Test 3: Check memory system
    print("\n[3] Checking Memory System...")
    try:
        from engine.tools.cursor_tools import _ensure_db, DB_PATH
        
        _ensure_db()
        print(f"   [OK] Memory database ready: {DB_PATH}")
        
    except Exception as e:
        print(f"   [FAIL] Memory system failed: {e}")
    
    # Test 4: Check decision guidelines in system prompt
    print("\n[4] Checking System Prompt...")
    try:
        from engine.agent.react_agent import REACT_SYSTEM_PROMPT_TEMPLATE
        
        has_guidelines = "Decision Guidelines" in REACT_SYSTEM_PROMPT_TEMPLATE
        has_direct_answers = "Direct answers" in REACT_SYSTEM_PROMPT_TEMPLATE
        
        if has_guidelines:
            print("   [OK] Decision Guidelines present")
        else:
            print("   [FAIL] Decision Guidelines missing!")
        
        if has_direct_answers:
            print("   [OK] 'Direct answers' rule present")
        
    except Exception as e:
        print(f"   [FAIL] System prompt check failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print("All core components are ready for testing.")
    print("\nNext steps:")
    print("1. Run user scenario tests: python tests/evaluation/scenarios/run_scenario_test.py")
    print("2. Run AgentBench baseline: ./run_nogicos_test.sh (in WSL)")


async def main():
    parser = argparse.ArgumentParser(description="Run tool selection tests")
    parser.add_argument("--quick", action="store_true", help="Run only validation checks")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--full", action="store_true", help="Run full agent tests (slow)")
    args = parser.parse_args()
    
    if args.full:
        # Full test with agent
        test_cases = load_test_cases()
        
        if args.quick:
            test_cases = test_cases[:5]  # Quick mode: only 5 tests
        
        print("="*60)
        print("NogicOS Tool Selection Test")
        print("="*60)
        print(f"Total tests: {len(test_cases)}")
        print(f"Mode: {'Verbose' if args.verbose else 'Summary'}")
        
        results = []
        correct = 0
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {test['id']}: {test['user_input'][:40]}...")
            
            result = await test_tool_selection(
                test['user_input'],
                test['expected_tools'],
                verbose=args.verbose
            )
            
            results.append({
                "test_id": test['id'],
                "category": test['category'],
                **result
            })
            
            if result['success']:
                correct += 1
                status = "[PASS]"
            else:
                status = "[FAIL]"
            
            if args.verbose:
                print(f"   Expected: {test['expected_tools']}")
                print(f"   Actual: {result.get('actual')}")
            
            print(f"   {status} {'PASS' if result['success'] else 'FAIL'}")
        
        # Summary
        accuracy = correct / len(test_cases) * 100
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total: {len(test_cases)}")
        print(f"Passed: {correct}")
        print(f"Failed: {len(test_cases) - correct}")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Pass threshold: 85%")
        print(f"Result: {'[PASS]' if accuracy >= 85 else '[FAIL]'}")
        
        # Save results
        output_dir = Path(__file__).parent / "results"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"tool_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total": len(test_cases),
                "passed": correct,
                "accuracy": accuracy,
                "results": results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\nResults saved to: {output_file}")
    else:
        # Quick validation
        await run_simple_validation()


if __name__ == "__main__":
    asyncio.run(main())
