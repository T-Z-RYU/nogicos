# -*- coding: utf-8 -*-
"""
MLflow Tracker for NogicOS Agent Evaluation

Provides experiment tracking and evaluation using MLflow 3's GenAI capabilities:
- Automatic experiment logging
- Custom scorers for agent evaluation
- Trace recording for debugging
- Results visualization
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import mlflow
    from mlflow.genai.scorers import scorer
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("[Warning] MLflow not installed. Run: pip install mlflow")
    
    # Stub decorator for when MLflow is not available
    def scorer(func):
        return func


@dataclass
class TrackerConfig:
    """Configuration for MLflow tracking"""
    experiment_name: str = "NogicOS-Agent-Eval"
    tracking_uri: Optional[str] = None  # None = local ./mlruns
    run_name: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    log_artifacts: bool = True


class MLflowTracker:
    """
    MLflow tracking for NogicOS agent evaluations.
    
    Example:
        tracker = MLflowTracker()
        with tracker.start_run("benchmark_v1"):
            results = await run_benchmark()
            tracker.log_results(results)
    """
    
    def __init__(self, config: Optional[TrackerConfig] = None):
        self.config = config or TrackerConfig()
        self._run = None
        self._setup_mlflow()
    
    def _setup_mlflow(self):
        """Initialize MLflow tracking"""
        if not MLFLOW_AVAILABLE:
            return
        
        # Set tracking URI if specified
        if self.config.tracking_uri:
            mlflow.set_tracking_uri(self.config.tracking_uri)
        
        # Set or create experiment
        mlflow.set_experiment(self.config.experiment_name)
    
    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Start an MLflow run (context manager).
        
        Args:
            run_name: Name for this run
            tags: Additional tags for the run
        
        Returns:
            Self for use as context manager
        """
        if not MLFLOW_AVAILABLE:
            return self
        
        name = run_name or self.config.run_name or f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        all_tags = {**(self.config.tags or {}), **(tags or {})}
        
        self._run = mlflow.start_run(run_name=name, tags=all_tags)
        return self
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_run()
        return False
    
    def end_run(self):
        """End the current MLflow run"""
        if MLFLOW_AVAILABLE and self._run:
            mlflow.end_run()
            self._run = None
    
    def log_params(self, params: Dict[str, Any]):
        """Log parameters to current run"""
        if not MLFLOW_AVAILABLE:
            return
        
        # Flatten nested dicts and convert to strings
        flat_params = {}
        for key, value in params.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    flat_params[f"{key}.{k}"] = str(v)
            else:
                flat_params[key] = str(value) if not isinstance(value, (int, float, str, bool)) else value
        
        mlflow.log_params(flat_params)
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics to current run"""
        if not MLFLOW_AVAILABLE:
            return
        
        # Filter to numeric values only
        numeric_metrics = {
            k: float(v) for k, v in metrics.items()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        
        mlflow.log_metrics(numeric_metrics, step=step)
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """Log an artifact file to current run"""
        if not MLFLOW_AVAILABLE or not self.config.log_artifacts:
            return
        
        mlflow.log_artifact(local_path, artifact_path)
    
    def log_dict(self, data: Dict, filename: str):
        """Log a dictionary as a JSON artifact"""
        if not MLFLOW_AVAILABLE or not self.config.log_artifacts:
            return
        
        import json
        import tempfile
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8'
        ) as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            temp_path = f.name
        
        mlflow.log_artifact(temp_path, artifact_path="results")
        os.unlink(temp_path)
    
    def log_benchmark_results(self, results: Dict[str, Any]):
        """
        Log complete benchmark results.
        
        Args:
            results: Benchmark results dict with metrics and task results
        """
        # Log overall metrics
        metrics = {
            "overall_score": results.get("overall_score", 0.0),
            "success_rate": results.get("metrics", {}).get("success_rate", 0.0),
            "avg_steps": results.get("metrics", {}).get("avg_steps", 0.0),
            "avg_time_seconds": results.get("metrics", {}).get("avg_time_seconds", 0.0),
            "total_tasks": results.get("metrics", {}).get("total_tasks", 0),
            "passed_tasks": results.get("metrics", {}).get("passed_tasks", 0),
        }
        
        # Log category scores
        for cat, data in results.get("categories", {}).items():
            if isinstance(data, dict):
                metrics[f"category_{cat}_score"] = data.get("score", 0.0)
                metrics[f"category_{cat}_success_rate"] = data.get("success_rate", 0.0)
        
        self.log_metrics(metrics)
        
        # Log full results as artifact
        self.log_dict(results, "benchmark_results.json")
    
    def log_deepeval_results(self, results: Dict[str, Any]):
        """
        Log DeepEval evaluation results.
        
        Args:
            results: DeepEval results dict
        """
        metrics = {
            "deepeval_success_rate": results.get("success_rate", 0.0),
            "deepeval_total": results.get("total", 0),
            "deepeval_passed": results.get("passed", 0),
        }
        
        # Log average scores per metric
        for metric_name, avg_score in results.get("average_scores", {}).items():
            metrics[f"deepeval_{metric_name.lower()}"] = avg_score
        
        self.log_metrics(metrics)
        self.log_dict(results, "deepeval_results.json")


# Custom MLflow scorers for GenAI evaluation
@scorer
def task_success(outputs: str, expectations: Optional[Dict] = None) -> bool:
    """Check if task was completed successfully based on output"""
    if not outputs:
        return False
    
    # Check for error indicators
    error_indicators = ["error", "failed", "cannot", "unable", "exception"]
    output_lower = outputs.lower()
    
    for indicator in error_indicators:
        if indicator in output_lower and "no error" not in output_lower:
            return False
    
    # Check against expected output if provided
    if expectations and "expected_output" in expectations:
        expected = expectations["expected_output"].lower()
        return expected in output_lower
    
    return len(outputs) > 10  # Non-trivial output


@scorer
def response_quality(outputs: str) -> float:
    """Score the quality of agent response (0.0 to 1.0)"""
    if not outputs:
        return 0.0
    
    score = 0.0
    
    # Length check (not too short, not too long)
    length = len(outputs)
    if 50 <= length <= 2000:
        score += 0.3
    elif 10 <= length < 50 or 2000 < length <= 5000:
        score += 0.15
    
    # Structure check (has sentences/paragraphs)
    if ". " in outputs or "\n" in outputs:
        score += 0.2
    
    # Completeness check (doesn't end mid-sentence)
    if outputs.rstrip().endswith(('.', '!', '?', ')', ']', '"', "'")):
        score += 0.2
    
    # No error messages
    error_indicators = ["error:", "traceback", "exception"]
    if not any(e in outputs.lower() for e in error_indicators):
        score += 0.3
    
    return min(score, 1.0)


@scorer
def tool_usage_efficiency(trace) -> float:
    """Score efficiency of tool usage based on trace (if available)"""
    if trace is None:
        return 0.5  # No trace info
    
    try:
        # Get tool call spans
        spans = trace.search_spans(name="tool_call") if hasattr(trace, "search_spans") else []
        num_tools = len(spans)
        
        if num_tools == 0:
            return 0.5  # No tools used, neutral
        elif num_tools <= 3:
            return 1.0  # Efficient
        elif num_tools <= 6:
            return 0.7  # Moderate
        else:
            return 0.4  # Too many tool calls
    except:
        return 0.5


# Convenience function for running MLflow GenAI evaluation
async def track_experiment(
    eval_dataset: List[Dict[str, Any]],
    predict_fn: Callable,
    experiment_name: str = "NogicOS-Agent-Eval",
    run_name: Optional[str] = None,
    custom_scorers: Optional[List] = None,
) -> Dict[str, Any]:
    """
    Run MLflow GenAI evaluation with tracking.
    
    Args:
        eval_dataset: List of dicts with 'inputs' and optional 'expectations'
        predict_fn: Function that takes inputs and returns outputs
        experiment_name: MLflow experiment name
        run_name: Optional run name
        custom_scorers: Additional scorer functions
    
    Returns:
        Evaluation results dict
    """
    if not MLFLOW_AVAILABLE:
        print("[Warning] MLflow not available, returning empty results")
        return {"error": "MLflow not installed"}
    
    # Setup experiment
    mlflow.set_experiment(experiment_name)
    
    # Default scorers
    scorers = [task_success, response_quality]
    if custom_scorers:
        scorers.extend(custom_scorers)
    
    # Format dataset for MLflow
    formatted_data = []
    for item in eval_dataset:
        formatted_data.append({
            "inputs": item.get("inputs", {"query": item.get("input", "")}),
            "expectations": item.get("expectations", {}),
        })
    
    # Run evaluation
    name = run_name or f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    with mlflow.start_run(run_name=name):
        try:
            results = mlflow.genai.evaluate(
                data=formatted_data,
                predict_fn=predict_fn,
                scorers=scorers,
            )
            return {
                "status": "success",
                "metrics": results.metrics if hasattr(results, "metrics") else {},
                "tables": results.tables if hasattr(results, "tables") else {},
            }
        except Exception as e:
            mlflow.log_param("error", str(e))
            return {"status": "error", "error": str(e)}


# Entry point for CLI
if __name__ == "__main__":
    import json
    
    async def main():
        # Example usage
        tracker = MLflowTracker(TrackerConfig(
            experiment_name="NogicOS-Test",
            run_name="test_run",
        ))
        
        with tracker.start_run():
            # Log some test metrics
            tracker.log_params({
                "model": "claude-3-opus",
                "max_iterations": 10,
            })
            
            tracker.log_metrics({
                "success_rate": 0.85,
                "avg_time": 2.5,
            })
            
            # Log test results
            tracker.log_dict(
                {"test": "data", "results": [1, 2, 3]},
                "test_results.json"
            )
        
        print("MLflow tracking test complete!")
        print(f"View results at: mlflow ui --port 5000")
    
    asyncio.run(main())



