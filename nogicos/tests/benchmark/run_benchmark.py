# -*- coding: utf-8 -*-
"""
NogicOS Benchmark Runner

Based on WebArena/OSWorld evaluation standards.
Runs all benchmark tasks and generates a comprehensive report.

Integrated with:
- DeepEval for automated LLM evaluation
- MLflow for experiment tracking
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

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.benchmark.evaluators import create_evaluator, EvaluationResult

# Optional: MLflow tracking
try:
    from tests.evaluation.mlflow_tracker import MLflowTracker, TrackerConfig
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

# Optional: DeepEval metrics
try:
    from tests.evaluation.metrics import TrajectoryAccuracyMetric, ToolCallCorrectnessMetric
    DEEPEVAL_METRICS_AVAILABLE = True
except ImportError:
    DEEPEVAL_METRICS_AVAILABLE = False


@dataclass
class TaskResult:
    """Result of a single task execution"""
    task_id: str
    category: str
    difficulty: str
    task: str
    success: bool
    score: float
    steps_taken: int
    optimal_steps: int
    time_seconds: float
    timeout_seconds: float
    evaluation: Dict[str, Any]
    error: Optional[str]
    agent_response: str


@dataclass
class BenchmarkReport:
    """Complete benchmark report"""
    timestamp: str
    version: str
    overall_score: float
    level: str
    categories: Dict[str, Dict[str, Any]]
    metrics: Dict[str, float]
    tasks: List[Dict[str, Any]]


class BenchmarkRunner:
    """
    Runs benchmark tasks against NogicOS Agent
    
    Features:
    - WebArena/OSWorld standard evaluation
    - Optional MLflow experiment tracking
    - Optional DeepEval metrics integration
    """
    
    LEVELS = [
        (0.30, "L1", "Prototype"),
        (0.50, "L2", "Alpha"),
        (0.70, "L3", "Beta"),
        (0.85, "L4", "Launch"),
        (1.01, "L5", "Growth"),  # > 100% impossible, so this is max
    ]
    
    CATEGORY_WEIGHTS = {
        "browser": 0.35,
        "local": 0.35,
        "mixed": 0.30,
    }
    
    def __init__(
        self,
        test_cases_path: str = None,
        enable_tracking: bool = False,
        experiment_name: str = "NogicOS-Benchmark",
    ):
        self.test_cases_path = test_cases_path or str(
            Path(__file__).parent / "test_cases.json"
        )
        self.results: List[TaskResult] = []
        self.agent = None
        
        # MLflow tracking
        self.enable_tracking = enable_tracking and MLFLOW_AVAILABLE
        self.tracker = None
        if self.enable_tracking:
            self.tracker = MLflowTracker(TrackerConfig(
                experiment_name=experiment_name,
            ))
        
        # DeepEval metrics
        self.trajectory_metric = None
        self.tool_call_metric = None
        if DEEPEVAL_METRICS_AVAILABLE:
            self.trajectory_metric = TrajectoryAccuracyMetric(threshold=0.6)
            self.tool_call_metric = ToolCallCorrectnessMetric(threshold=0.7)
    
    async def setup(self):
        """Initialize the agent"""
        try:
            from engine.agent.react_agent import ReActAgent
            self.agent = ReActAgent(max_iterations=10)
            print("[Benchmark] Agent initialized")
            return True
        except Exception as e:
            print(f"[Benchmark] Failed to initialize agent: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup after benchmark"""
        if self.agent:
            try:
                await self.agent.cleanup_browser_session()
            except:
                pass
    
    def load_test_cases(self) -> List[Dict]:
        """Load test cases from JSON file"""
        with open(self.test_cases_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("tasks", [])
    
    async def run_single_task(self, task_config: Dict) -> TaskResult:
        """Run a single benchmark task"""
        task_id = task_config["task_id"]
        task = task_config["task"]
        category = task_config["category"]
        difficulty = task_config["difficulty"]
        timeout = task_config.get("timeout_seconds", 60)
        max_steps = task_config.get("max_steps", 10)
        optimal_steps = task_config.get("optimal_steps", 1)
        
        print(f"\n[{task_id}] Running: {task[:50]}...")
        
        start_time = time.time()
        error = None
        agent_response = ""
        steps_taken = 0
        
        try:
            # Run the task with timeout
            result = await asyncio.wait_for(
                self.agent.run(task=task, session_id=f"benchmark_{task_id}"),
                timeout=timeout
            )
            
            agent_response = result.response if result else ""
            steps_taken = result.iterations if hasattr(result, 'iterations') else 0
            success = result.success if result else False
            
            if not success:
                error = result.error if result else "Unknown error"
                
        except asyncio.TimeoutError:
            error = f"Task timed out after {timeout}s"
            success = False
        except Exception as e:
            error = str(e)
            success = False
        
        elapsed_time = time.time() - start_time
        
        # Run evaluator
        evaluator_config = task_config.get("evaluator", {})
        evaluator = create_evaluator(evaluator_config)
        
        # Determine what to evaluate
        eval_type = evaluator_config.get("type", "string")
        if eval_type == "file":
            # For file evaluator, use the file path
            eval_input = evaluator_config.get("path", "")
        elif eval_type == "url":
            # For URL evaluator, try to extract URL from response
            eval_input = agent_response
        else:
            # For string evaluator, use agent response
            eval_input = agent_response
        
        expected = evaluator_config.get("expected")
        eval_result = evaluator.evaluate(eval_input, expected)
        
        # Calculate final score with efficiency bonus
        base_score = eval_result.score
        efficiency = min(1.0, optimal_steps / max(1, steps_taken)) if steps_taken > 0 else 0.5
        time_bonus = min(1.0, timeout / max(1, elapsed_time)) if elapsed_time > 0 else 1.0
        
        final_score = base_score * 0.7 + efficiency * 0.2 + time_bonus * 0.1
        
        # Cleanup if needed
        for cleanup_path in task_config.get("cleanup", []):
            try:
                cleanup_full = os.path.expanduser(cleanup_path)
                if os.path.exists(cleanup_full):
                    os.remove(cleanup_full)
            except:
                pass
        
        result = TaskResult(
            task_id=task_id,
            category=category,
            difficulty=difficulty,
            task=task,
            success=eval_result.passed and success,
            score=final_score,
            steps_taken=steps_taken,
            optimal_steps=optimal_steps,
            time_seconds=elapsed_time,
            timeout_seconds=timeout,
            evaluation=asdict(eval_result) if hasattr(eval_result, '__dict__') else eval_result.__dict__,
            error=error,
            agent_response=agent_response[:500] if agent_response else ""
        )
        
        status = "[PASS]" if result.success else "[FAIL]"
        print(f"  {status} Score: {final_score:.2f}, Time: {elapsed_time:.1f}s, Steps: {steps_taken}")
        
        return result
    
    async def run_all(
        self,
        categories: List[str] = None,
        run_name: str = None,
    ) -> BenchmarkReport:
        """Run all benchmark tasks"""
        print("=" * 60)
        print("NogicOS Benchmark")
        print("Based on WebArena/OSWorld Standards")
        if self.enable_tracking:
            print("MLflow Tracking: ENABLED")
        print("=" * 60)
        
        # Setup
        if not await self.setup():
            raise RuntimeError("Failed to setup benchmark")
        
        # Load test cases
        test_cases = self.load_test_cases()
        
        # Filter by category if specified
        if categories:
            test_cases = [t for t in test_cases if t["category"] in categories]
        
        print(f"\nRunning {len(test_cases)} tasks...")
        
        # Start MLflow tracking if enabled
        if self.enable_tracking and self.tracker:
            name = run_name or f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.tracker.start_run(run_name=name, tags={
                "benchmark_type": "full" if not categories else ",".join(categories),
                "num_tasks": str(len(test_cases)),
            })
            self.tracker.log_params({
                "categories": categories or ["all"],
                "num_tasks": len(test_cases),
            })
        
        # Run tasks
        self.results = []
        for i, task_config in enumerate(test_cases):
            result = await self.run_single_task(task_config)
            self.results.append(result)
            
            # Log per-task metrics to MLflow
            if self.enable_tracking and self.tracker:
                self.tracker.log_metrics({
                    f"task_{result.task_id}_score": result.score,
                    f"task_{result.task_id}_time": result.time_seconds,
                    f"task_{result.task_id}_success": 1.0 if result.success else 0.0,
                }, step=i)
        
        # Cleanup
        await self.cleanup()
        
        # Generate report
        report = self.generate_report()
        
        # Log final results to MLflow
        if self.enable_tracking and self.tracker:
            self.tracker.log_benchmark_results(asdict(report))
            self.tracker.end_run()
            print("\n[MLflow] Results logged. View with: mlflow ui --port 5000")
        
        return report
    
    def generate_report(self) -> BenchmarkReport:
        """Generate benchmark report from results"""
        # Calculate category scores
        category_results = {}
        for cat in ["browser", "local", "mixed"]:
            cat_tasks = [r for r in self.results if r.category == cat]
            if cat_tasks:
                passed = sum(1 for t in cat_tasks if t.success)
                score = sum(t.score for t in cat_tasks) / len(cat_tasks)
                category_results[cat] = {
                    "score": round(score, 3),
                    "passed": passed,
                    "total": len(cat_tasks),
                    "success_rate": round(passed / len(cat_tasks), 3)
                }
            else:
                category_results[cat] = {"score": 0, "passed": 0, "total": 0, "success_rate": 0}
        
        # Calculate overall score (weighted)
        overall = 0.0
        for cat, weight in self.CATEGORY_WEIGHTS.items():
            if cat in category_results and category_results[cat]["total"] > 0:
                overall += weight * category_results[cat]["score"]
        
        # Determine level
        level = "L1"
        level_name = "Prototype"
        for threshold, lvl, name in self.LEVELS:
            if overall < threshold:
                level = lvl
                level_name = name
                break
        
        # Calculate metrics
        total_tasks = len(self.results)
        passed_tasks = sum(1 for r in self.results if r.success)
        avg_steps = sum(r.steps_taken for r in self.results) / max(1, total_tasks)
        avg_time = sum(r.time_seconds for r in self.results) / max(1, total_tasks)
        
        # Error analysis
        errors = [r for r in self.results if r.error]
        error_types = {}
        for r in errors:
            error_key = r.error[:50] if r.error else "unknown"
            error_types[error_key] = error_types.get(error_key, 0) + 1
        
        report = BenchmarkReport(
            timestamp=datetime.now().isoformat(),
            version="2.0.0",
            overall_score=round(overall, 3),
            level=f"{level} ({level_name})",
            categories=category_results,
            metrics={
                "success_rate": round(passed_tasks / max(1, total_tasks), 3),
                "avg_steps": round(avg_steps, 2),
                "avg_time_seconds": round(avg_time, 2),
                "total_tasks": total_tasks,
                "passed_tasks": passed_tasks,
            },
            tasks=[asdict(r) for r in self.results]
        )
        
        return report
    
    def print_report(self, report: BenchmarkReport):
        """Print formatted report"""
        print("\n" + "=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)
        
        print(f"\nOverall Score: {report.overall_score:.1%}")
        print(f"Level: {report.level}")
        
        print("\n--- Categories ---")
        for cat, data in report.categories.items():
            if data["total"] > 0:
                print(f"  {cat:8}: {data['score']:.1%} ({data['passed']}/{data['total']} passed)")
        
        print("\n--- Metrics ---")
        print(f"  Success Rate: {report.metrics['success_rate']:.1%}")
        print(f"  Avg Steps: {report.metrics['avg_steps']:.1f}")
        print(f"  Avg Time: {report.metrics['avg_time_seconds']:.1f}s")
        
        print("\n--- Task Results ---")
        for task in report.tasks:
            status = "[PASS]" if task["success"] else "[FAIL]"
            print(f"  {task['task_id']:5} {status} {task['score']:.2f} - {task['task'][:40]}...")
        
        print("\n" + "=" * 60)
    
    def save_report(self, report: BenchmarkReport, output_path: str):
        """Save report to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)
        print(f"\nReport saved to: {output_path}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NogicOS Benchmark Runner")
    parser.add_argument("--output", "-o", default="benchmark_results.json",
                        help="Output file path")
    parser.add_argument("--categories", "-c", nargs="+",
                        choices=["browser", "local", "mixed"],
                        help="Run specific categories only")
    parser.add_argument("--with-tracking", "-t", action="store_true",
                        help="Enable MLflow experiment tracking")
    parser.add_argument("--experiment", "-e", default="NogicOS-Benchmark",
                        help="MLflow experiment name")
    parser.add_argument("--run-name", "-r", default=None,
                        help="MLflow run name (auto-generated if not specified)")
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner(
        enable_tracking=args.with_tracking,
        experiment_name=args.experiment,
    )
    
    try:
        report = await runner.run_all(
            categories=args.categories,
            run_name=args.run_name,
        )
        runner.print_report(report)
        runner.save_report(report, args.output)
    except Exception as e:
        print(f"\n[ERROR] Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


