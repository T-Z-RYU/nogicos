# -*- coding: utf-8 -*-
"""
User Scenario Test Runner

This script provides a framework for running and evaluating user scenario tests.
Since these tests require human evaluation of "intelligence" and "user experience",
this provides the structure for manual evaluation.

Usage:
    python run_scenario_test.py [--auto] [--scenario SCENARIO_ID]

Options:
    --auto: Run in automated mode (logs results without human rating)
    --scenario: Run specific scenario by ID
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


def load_scenarios() -> List[Dict[str, Any]]:
    """Load scenarios from JSON file"""
    scenario_file = Path(__file__).parent / "scenarios.json"
    with open(scenario_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["scenarios"]


def print_scenario(scenario: Dict[str, Any]) -> None:
    """Print scenario details"""
    print(f"\n{'='*60}")
    print(f"Scenario: {scenario['id']} - {scenario['name']}")
    print(f"Category: {scenario['category']}")
    print(f"{'='*60}")
    print(f"\nUser Input: {scenario['user_input']}")
    if scenario.get("setup"):
        print(f"Setup: {scenario['setup']}")
    print(f"\nExpected Behavior:")
    print(f"  {scenario['expected_behavior']}")
    print(f"\nEvaluation Dimensions: {', '.join(scenario['evaluation_dimensions'])}")


def get_human_rating() -> int:
    """Get human rating for scenario"""
    print("\nRating Scale:")
    print("  5 = 完美理解并Execute")
    print("  4 = 理解正确，Execute略有瑕疵")
    print("  3 = 基本Complete，需要澄清")
    print("  2 = 需要多次澄清")
    print("  1 = 完全Error或无Response")
    
    while True:
        try:
            rating = int(input("\nEnter rating (1-5): "))
            if 1 <= rating <= 5:
                return rating
            print("Please enter a number between 1 and 5")
        except ValueError:
            print("Please enter a valid number")


# Global agent instance for memory tests (to preserve session state)
_memory_test_agent = None


async def run_scenario_with_agent(scenario: Dict[str, Any]) -> Optional[str]:
    """
    Run a scenario with the NogicOS agent.
    
    Returns the agent's response for manual evaluation.
    """
    global _memory_test_agent
    
    try:
        from engine.agent.react_agent import ReActAgent
        import asyncio
        
        # Use consistent session_id to share memories across scenarios
        # Memory scenarios (memory_*) need to share state AND same agent instance
        if scenario["id"].startswith("memory_"):
            session_id = "memory_test_session"
            
            # Use shared agent instance for memory tests
            if _memory_test_agent is None:
                _memory_test_agent = ReActAgent()
            agent = _memory_test_agent
            
            # If this is memory_002, wait a bit for memory_001's async save to complete
            if scenario["id"] == "memory_002":
                await asyncio.sleep(2)  # Wait for background memory extraction
        else:
            session_id = f"scenario_test_{scenario['id']}"
            agent = ReActAgent()
        
        result = await agent.run(
            task=scenario["user_input"],
            session_id=session_id,
        )
        
        return result.response if result.success else f"Error: {result.error}"
    except Exception as e:
        return f"Failed to run agent: {e}"


def save_results(results: List[Dict[str, Any]], output_path: Path) -> None:
    """Save test results to JSON file"""
    rated_results = [r for r in results if r.get("rating") is not None]
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_scenarios": len(results),
        "rated_scenarios": len(rated_results),
        "average_rating": sum(r["rating"] for r in rated_results) / len(rated_results) if rated_results else None,
        "pass_rate": sum(1 for r in rated_results if r["rating"] >= 3.5) / len(rated_results) if rated_results else None,
        "results": results,
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_path}")


async def main():
    parser = argparse.ArgumentParser(description="Run user scenario tests")
    parser.add_argument("--auto", action="store_true", help="Run in automated mode")
    parser.add_argument("--scenario", type=str, help="Run specific scenario by ID")
    args = parser.parse_args()
    
    scenarios = load_scenarios()
    
    # Filter scenarios if specific one requested
    if args.scenario:
        scenarios = [s for s in scenarios if s["id"] == args.scenario]
        if not scenarios:
            print(f"Scenario not found: {args.scenario}")
            return
    
    print("="*60)
    print("NogicOS User Scenario Test")
    print("="*60)
    print(f"Total scenarios: {len(scenarios)}")
    print(f"Mode: {'Automated' if args.auto else 'Manual evaluation'}")
    
    results = []
    
    for scenario in scenarios:
        print_scenario(scenario)
        
        # Run with agent
        print("\n[Running with NogicOS Agent...]")
        response = await run_scenario_with_agent(scenario)
        
        print(f"\nAgent Response:")
        print("-"*40)
        # Handle Unicode encoding for Windows console
        resp_text = response[:500] if response else "(No response)"
        try:
            print(resp_text)
        except UnicodeEncodeError:
            print(resp_text.encode('ascii', 'replace').decode('ascii'))
        if response and len(response) > 500:
            print("... (truncated)")
        print("-"*40)
        
        result = {
            "scenario_id": scenario["id"],
            "scenario_name": scenario["name"],
            "category": scenario["category"],
            "response": response[:1000] if response else None,
        }
        
        if not args.auto:
            # Get human rating
            rating = get_human_rating()
            result["rating"] = rating
            notes = input("Notes (optional): ").strip()
            if notes:
                result["notes"] = notes
        else:
            # Automated mode - log response only
            result["rating"] = None
            print("(Automated mode - skipping rating)")
        
        results.append(result)
        
        # Ask to continue
        if not args.auto and scenario != scenarios[-1]:
            cont = input("\nContinue to next scenario? (y/n): ").lower()
            if cont != "y":
                break
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    rated_results = [r for r in results if r.get("rating") is not None]
    if rated_results:
        avg_rating = sum(r["rating"] for r in rated_results) / len(rated_results)
        print(f"Scenarios tested: {len(results)}")
        print(f"Scenarios rated: {len(rated_results)}")
        print(f"Average rating: {avg_rating:.2f}/5")
        print(f"Pass rate (>=3.5): {sum(1 for r in rated_results if r['rating'] >= 3.5) / len(rated_results) * 100:.1f}%")
        
        # By category
        categories = {}
        for r in rated_results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r["rating"])
        
        print("\nBy Category:")
        for cat, ratings in categories.items():
            print(f"  {cat}: {sum(ratings)/len(ratings):.2f}/5 ({len(ratings)} scenarios)")
    else:
        print("No scenarios were rated.")
    
    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"scenario_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_results(results, output_file)


if __name__ == "__main__":
    asyncio.run(main())

