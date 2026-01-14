# -*- coding: utf-8 -*-
"""
NogicOS STRICT Benchmark Runner

DO NOT MODIFY evaluation criteria to make tests pass.
This shows the REAL state of the system.
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.benchmark.evaluators import create_evaluator


@dataclass
class TaskResult:
    task_id: str
    category: str
    difficulty: str
    task: str
    standard: str
    success: bool
    score: float
    steps_taken: int
    time_seconds: float
    evaluation_message: str
    agent_response: str
    error: Optional[str]


class StrictBenchmarkRunner:
    """Strict benchmark - no adjustments allowed"""
    
    def __init__(self):
        self.test_cases_path = Path(__file__).parent / "test_cases_strict.json"
        self.results: List[TaskResult] = []
        self.agent = None
    
    async def setup(self):
        try:
            from engine.agent.react_agent import ReActAgent
            self.agent = ReActAgent(max_iterations=10)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to init agent: {e}")
            return False
    
    async def cleanup(self):
        if self.agent:
            try:
                await self.agent.cleanup_browser_session()
            except:
                pass
    
    def load_test_cases(self) -> List[Dict]:
        with open(self.test_cases_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("tasks", [])
    
    async def run_single_task(self, task_config: Dict) -> TaskResult:
        task_id = task_config["task_id"]
        task = task_config["task"]
        timeout = task_config.get("timeout_seconds", 60)
        standard = task_config.get("standard", "Unknown")
        
        print(f"\n[{task_id}] {task[:50]}...")
        print(f"    Standard: {standard}")
        
        start_time = time.time()
        error = None
        agent_response = ""
        steps = 0
        
        try:
            result = await asyncio.wait_for(
                self.agent.run(task=task, session_id=f"strict_{task_id}"),
                timeout=timeout
            )
            agent_response = result.response if result else ""
            steps = result.iterations if hasattr(result, 'iterations') else 0
            if not result.success:
                error = result.error
        except asyncio.TimeoutError:
            error = f"TIMEOUT after {timeout}s"
        except Exception as e:
            error = str(e)
        
        elapsed = time.time() - start_time
        
        # Evaluate
        evaluator_config = task_config.get("evaluator", {})
        evaluator = create_evaluator(evaluator_config)
        
        eval_type = evaluator_config.get("type", "string")
        if eval_type == "file":
            eval_input = evaluator_config.get("path", "")
        else:
            eval_input = agent_response
        
        expected = evaluator_config.get("expected")
        eval_result = evaluator.evaluate(eval_input, expected)
        
        # Cleanup
        for path in task_config.get("cleanup", []):
            try:
                full_path = os.path.expanduser(path)
                if os.path.exists(full_path):
                    os.remove(full_path)
            except:
                pass
        
        status = "PASS" if eval_result.passed else "FAIL"
        print(f"    [{status}] {eval_result.message}")
        print(f"    Response: {agent_response[:100]}..." if agent_response else "    Response: (empty)")
        
        return TaskResult(
            task_id=task_id,
            category=task_config["category"],
            difficulty=task_config["difficulty"],
            task=task,
            standard=standard,
            success=eval_result.passed,
            score=eval_result.score,
            steps_taken=steps,
            time_seconds=elapsed,
            evaluation_message=eval_result.message,
            agent_response=agent_response[:300] if agent_response else "",
            error=error
        )
    
    async def run_all(self, categories: List[str] = None):
        print("=" * 70)
        print("NogicOS STRICT Benchmark")
        print("Based on UNMODIFIED WebArena/OSWorld/AgentBench Standards")
        print("=" * 70)
        print("\nWARNING: Do NOT adjust test criteria to improve scores.")
        print("         This shows the TRUE state of the system.\n")
        
        if not await self.setup():
            return
        
        test_cases = self.load_test_cases()
        if categories:
            test_cases = [t for t in test_cases if t["category"] in categories]
        
        print(f"Running {len(test_cases)} tasks...\n")
        
        self.results = []
        for tc in test_cases:
            result = await self.run_single_task(tc)
            self.results.append(result)
        
        await self.cleanup()
        self.print_report()
    
    def print_report(self):
        print("\n" + "=" * 70)
        print("STRICT BENCHMARK RESULTS (UNMODIFIED STANDARDS)")
        print("=" * 70)
        
        # By category
        categories = {}
        for r in self.results:
            if r.category not in categories:
                categories[r.category] = {"passed": 0, "total": 0}
            categories[r.category]["total"] += 1
            if r.success:
                categories[r.category]["passed"] += 1
        
        total_passed = sum(c["passed"] for c in categories.values())
        total_tasks = sum(c["total"] for c in categories.values())
        overall_rate = total_passed / total_tasks if total_tasks > 0 else 0
        
        # Determine level
        if overall_rate >= 0.85:
            level = "L5 Growth"
        elif overall_rate >= 0.70:
            level = "L4 Launch"
        elif overall_rate >= 0.50:
            level = "L3 Beta"
        elif overall_rate >= 0.30:
            level = "L2 Alpha"
        else:
            level = "L1 Prototype"
        
        print(f"\n📊 Overall: {total_passed}/{total_tasks} ({overall_rate:.1%})")
        print(f"📈 Maturity Level: {level}")
        
        print("\n--- By Category ---")
        for cat, data in categories.items():
            rate = data["passed"] / data["total"] if data["total"] > 0 else 0
            print(f"  {cat:10}: {data['passed']}/{data['total']} ({rate:.1%})")
        
        print("\n--- Individual Results ---")
        for r in self.results:
            status = "✅" if r.success else "❌"
            print(f"  {status} [{r.task_id}] {r.task[:40]}...")
            print(f"      Eval: {r.evaluation_message}")
        
        print("\n--- Problems Found ---")
        problems = [r for r in self.results if not r.success]
        if problems:
            for r in problems:
                print(f"\n  ❌ {r.task_id}: {r.task}")
                print(f"     Standard: {r.standard}")
                print(f"     Problem: {r.evaluation_message}")
                print(f"     Response: {r.agent_response[:150]}..." if r.agent_response else "     Response: (empty)")
        else:
            print("  None! All tests passed.")
        
        print("\n" + "=" * 70)
        
        # Save results
        output = {
            "timestamp": datetime.now().isoformat(),
            "overall_rate": overall_rate,
            "level": level,
            "categories": categories,
            "results": [asdict(r) for r in self.results]
        }
        
        output_path = Path(__file__).parent / "strict_results.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_path}")


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--categories", nargs="+", 
                        choices=["browser", "local", "mixed"])
    args = parser.parse_args()
    
    runner = StrictBenchmarkRunner()
    await runner.run_all(categories=args.categories)


if __name__ == "__main__":
    asyncio.run(main())


