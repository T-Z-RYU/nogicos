# -*- coding: utf-8 -*-
"""
SkillWeaver 技术可行性验证 (Spike Test)

目标：回答一个问题 - SkillWeaver 能否作为产品核心引擎？

通过标准：
- 成功率 >= 70%
- 单步延迟 < 5s
- 端到端耗时 < 60s
- 崩溃次数 = 0
"""
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Windows UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Setup API keys from api_keys.py
try:
    from api_keys import setup_env
    setup_env()
except ImportError:
    print("Warning: api_keys.py not found")

# Add SkillWeaver to path
sys.path.insert(0, str(Path(__file__).parent / "SkillWeaver"))

from playwright.async_api import async_playwright

# ============================================================
# Configuration
# ============================================================

TEST_URL = "https://news.ycombinator.com"

TEST_TASKS = [
    {
        "id": "task1",
        "description": "Get the title of the first news item on the homepage",
        "task": {
            "type": "prod",
            "task": "Get the title of the first news item on this page. Return only the title text.",
        }
    },
    {
        "id": "task2", 
        "description": "Search for 'AI' and get the first result title",
        "task": {
            "type": "prod",
            "task": "Click on the search/hn search link, search for 'AI', and return the title of the first search result.",
        }
    },
    {
        "id": "task3",
        "description": "Go to 'new' page and get the first item title",
        "task": {
            "type": "prod",
            "task": "Click on the 'new' link in the navigation, then return the title of the first news item.",
        }
    },
]

RUNS_PER_TASK = 1  # Quick test first
MAX_STEPS = 10
TIMEOUT = 60  # seconds

# Pass/Fail thresholds
PASS_SUCCESS_RATE = 0.70
FAIL_SUCCESS_RATE = 0.50
PASS_AVG_TIME = 60
FAIL_AVG_TIME = 120

# ============================================================
# Data Classes
# ============================================================

@dataclass
class TestResult:
    task_id: str
    task_description: str
    run_number: int
    success: bool
    duration: float
    steps: int
    result: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass 
class TestSummary:
    total_tests: int
    successful: int
    failed: int
    success_rate: float
    avg_duration: float
    avg_steps: float
    crashes: int
    verdict: str  # "PASS", "FAIL", "NEEDS_INVESTIGATION"


# ============================================================
# Test Runner
# ============================================================

async def run_single_test(task_config: dict, run_number: int) -> TestResult:
    """Run a single test and return the result."""
    task_id = task_config["id"]
    task_description = task_config["description"]
    task = task_config["task"]
    
    print(f"\n  [Run {run_number}] {task_description}")
    
    start_time = time.time()
    steps = 0
    result_text = None
    error_text = None
    success = False
    
    try:
        # Import SkillWeaver components
        from skillweaver.environment import make_browser
        from skillweaver.knowledge_base.knowledge_base import KnowledgeBase
        from skillweaver.lm import LM
        from skillweaver.attempt_task import attempt_task
        
        # Create output directory
        output_dir = Path(__file__).parent / "spike_results" / f"{task_id}_run{run_number}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        async with async_playwright() as playwright:
            # Create browser
            browser = await make_browser(
                playwright,
                start_url=TEST_URL,
                headless=True,
                width=1280,
                height=720,
            )
            
            try:
                # Create LM - use Opus 4.5 for best performance
                model = os.getenv("SPIKE_MODEL", "claude-opus-4-5-20251101")
                print(f"    Using model: {model}")
                lm = LM(model=model)
                
                # Create empty knowledge base (no pre-learned skills)
                kb = KnowledgeBase()
                
                # Run the task with timeout
                try:
                    await asyncio.wait_for(
                        attempt_task(
                            browser=browser,
                            lm=lm,
                            task=task,
                            max_steps=MAX_STEPS,
                            knowledge_base=kb,
                            store_dir=str(output_dir),
                        ),
                        timeout=TIMEOUT
                    )
                    
                    # Check if task completed successfully
                    # Read action files to count steps and get result
                    action_files = sorted(output_dir.glob("*_action.json"))
                    steps = len(action_files)
                    
                    # Check each action file for termination result (last one first)
                    for action_file in reversed(action_files):
                        with open(action_file, "r", encoding="utf-8") as f:
                            action_data = json.load(f)
                            if action_data.get("terminate_with_result"):
                                result_text = action_data["terminate_with_result"]
                                success = True
                                break
                    
                    if not success:
                        error_text = "Task did not terminate with a result"
                        
                except asyncio.TimeoutError:
                    error_text = f"Timeout after {TIMEOUT}s"
                    
            finally:
                await browser.close()
                
    except ImportError as e:
        error_text = f"Import error: {e}"
    except Exception as e:
        error_text = f"Exception: {type(e).__name__}: {e}"
    
    duration = time.time() - start_time
    
    # Print result
    status = "OK" if success else "FAIL"
    print(f"    [{status}] {duration:.1f}s, {steps} steps")
    if error_text:
        print(f"    Error: {error_text[:80]}")
    if result_text:
        print(f"    Result: {result_text[:60]}...")
    
    return TestResult(
        task_id=task_id,
        task_description=task_description,
        run_number=run_number,
        success=success,
        duration=duration,
        steps=steps,
        result=result_text,
        error=error_text,
    )


async def run_all_tests() -> List[TestResult]:
    """Run all tests and collect results."""
    results = []
    
    print("=" * 60)
    print("  SkillWeaver Spike Test")
    print("=" * 60)
    print(f"URL: {TEST_URL}")
    print(f"Tasks: {len(TEST_TASKS)}")
    print(f"Runs per task: {RUNS_PER_TASK}")
    print(f"Total tests: {len(TEST_TASKS) * RUNS_PER_TASK}")
    print("=" * 60)
    
    for task_config in TEST_TASKS:
        print(f"\n[Task] {task_config['id']}: {task_config['description']}")
        
        for run in range(1, RUNS_PER_TASK + 1):
            result = await run_single_test(task_config, run)
            results.append(result)
    
    return results


def analyze_results(results: List[TestResult]) -> TestSummary:
    """Analyze test results and determine verdict."""
    total = len(results)
    successful = sum(1 for r in results if r.success)
    failed = total - successful
    success_rate = successful / total if total > 0 else 0
    
    durations = [r.duration for r in results]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    steps_list = [r.steps for r in results if r.steps > 0]
    avg_steps = sum(steps_list) / len(steps_list) if steps_list else 0
    
    # Count crashes (exceptions that aren't timeouts)
    crashes = sum(1 for r in results if r.error and "Exception" in r.error)
    
    # Determine verdict
    if success_rate >= PASS_SUCCESS_RATE and avg_duration <= PASS_AVG_TIME and crashes == 0:
        verdict = "PASS"
    elif success_rate < FAIL_SUCCESS_RATE or crashes >= 2:
        verdict = "FAIL"
    else:
        verdict = "NEEDS_INVESTIGATION"
    
    return TestSummary(
        total_tests=total,
        successful=successful,
        failed=failed,
        success_rate=success_rate,
        avg_duration=avg_duration,
        avg_steps=avg_steps,
        crashes=crashes,
        verdict=verdict,
    )


def print_summary(summary: TestSummary, results: List[TestResult]):
    """Print test summary."""
    print("\n")
    print("=" * 60)
    print("  SPIKE TEST RESULTS")
    print("=" * 60)
    print(f"Total tests:    {summary.total_tests}")
    print(f"Successful:     {summary.successful}")
    print(f"Failed:         {summary.failed}")
    print(f"Success rate:   {summary.success_rate:.1%}")
    print(f"Avg duration:   {summary.avg_duration:.1f}s")
    print(f"Avg steps:      {summary.avg_steps:.1f}")
    print(f"Crashes:        {summary.crashes}")
    print("-" * 60)
    
    # Verdict with explanation
    if summary.verdict == "PASS":
        print("VERDICT: PASS")
        print("  -> SkillWeaver can be used as the product core engine.")
        print("  -> Next step: Begin modular architecture design.")
    elif summary.verdict == "FAIL":
        print("VERDICT: FAIL")
        print("  -> SkillWeaver is NOT suitable for production use.")
        print("  -> Options:")
        print("     1. Analyze failure reasons and attempt fixes")
        print("     2. Implement core logic yourself")
        print("     3. Evaluate alternative frameworks")
    else:
        print("VERDICT: NEEDS_INVESTIGATION")
        print("  -> Results are inconclusive.")
        print("  -> Recommend: Analyze failures and run more targeted tests.")
    
    print("=" * 60)
    
    # Save detailed results
    output_dir = Path(__file__).parent / "spike_results"
    output_dir.mkdir(exist_ok=True)
    
    report = {
        "summary": asdict(summary),
        "results": [asdict(r) for r in results],
        "timestamp": datetime.now().isoformat(),
        "config": {
            "url": TEST_URL,
            "tasks": len(TEST_TASKS),
            "runs_per_task": RUNS_PER_TASK,
            "max_steps": MAX_STEPS,
            "timeout": TIMEOUT,
        }
    }
    
    report_path = output_dir / f"spike_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: {report_path}")


# ============================================================
# Main
# ============================================================

async def main():
    """Main entry point."""
    results = await run_all_tests()
    summary = analyze_results(results)
    print_summary(summary, results)
    
    # Return exit code based on verdict
    if summary.verdict == "PASS":
        return 0
    elif summary.verdict == "FAIL":
        return 1
    else:
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

