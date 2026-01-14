#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NogicOS Evaluation Runner

Run automated evaluations against the NogicOS agent.

Usage:
    # Create golden dataset
    python -m engine.evaluation.run_evaluation --create-golden
    
    # Run evaluation
    python -m engine.evaluation.run_evaluation --evaluate nogicos_golden
    
    # Create dataset from recent runs
    python -m engine.evaluation.run_evaluation --create-from-runs --limit 20
"""

import os
import sys
import time
import asyncio
import argparse
from typing import Optional, List, Dict, Any

# Note: Module uses standard import paths - ensure PYTHONPATH is configured correctly

from engine.observability import get_logger, setup_logging
logger = get_logger("evaluation_runner")

# LangSmith evaluation
try:
    from langsmith.evaluation import evaluate
    LANGSMITH_EVAL_AVAILABLE = True
except ImportError:
    LANGSMITH_EVAL_AVAILABLE = False
    logger.warning("[Evaluation] LangSmith evaluation not available")

# Local imports
from engine.evaluation.evaluators import (
    # RuleEvaluateer（objective metrics）
    latency_evaluator,
    token_count_evaluator,
    tool_call_count_evaluator,
    error_rate_evaluator,
    # UX Evaluateer（Userexperience）
    ttft_evaluator,
    follow_up_evaluator,
    content_richness_evaluator,
    # LLM-as-judge Evaluateer（semantic understanding）
    task_completion_llm_evaluator,
    tool_selection_llm_evaluator,
    correctness_evaluator,
    hallucination_evaluator,
    conciseness_evaluator,
    # EvaluateerSet
    get_rule_evaluators,
    get_llm_evaluators,
    get_all_evaluators,
    get_fast_evaluators,
    get_quality_evaluators,
    get_essential_evaluators,
    get_ux_evaluators,
)
from engine.evaluation.dataset_manager import (
    DatasetManager,
    create_golden_dataset,
    create_comprehensive_dataset,
    create_dataset_from_runs,
    COMPREHENSIVE_EXAMPLES,
)


def get_agent_function():
    """
    Get the NogicOS agent function for evaluation.
    
    Returns a callable that takes inputs dict and returns outputs dict.
    """
    from engine.agent.react_agent import ReActAgent
    
    # Create agent once and reuse
    agent = None
    
    def agent_fn(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper for sync evaluation."""
        nonlocal agent
        
        task = inputs.get("task", "")
        session_id = inputs.get("session_id", f"eval_{int(time.time())}")
        
        # Lazy init agent (avoid issues with module loading)
        if agent is None:
            agent = ReActAgent()
        
        # Run async agent in sync context
        try:
            # Try to get existing loop or create new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                agent.run(task=task, session_id=session_id)
            )
            
            return {
                "success": result.success,
                "response": result.response,
                "error": result.error,
                "iterations": result.iterations,
                "tool_calls": result.tool_calls,
            }
            
        except Exception as e:
            logger.error(f"[Evaluation] Agent execution failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "response": "",
                "error": str(e),
                "iterations": 0,
                "tool_calls": [],
            }
    
    return agent_fn


async def get_async_agent_function():
    """
    Get async agent function for evaluation.
    """
    from engine.agent.react_agent import ReActAgent
    
    agent = ReActAgent()
    
    async def agent_fn(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Async wrapper."""
        task = inputs.get("task", "")
        session_id = inputs.get("session_id", "evaluation")
        
        result = await agent.run(task=task, session_id=session_id)
        
        return {
            "success": result.success,
            "response": result.response,
            "error": result.error,
            "iterations": result.iterations,
            "tool_calls": result.tool_calls,
        }
    
    return agent_fn


def run_evaluation(
    dataset_name: str,
    experiment_prefix: str = "nogicos_eval",
    evaluators: Optional[List] = None,
    max_concurrency: int = 2,
    evaluator_mode: str = "all",
) -> Dict[str, Any]:
    """
    Run evaluation against a dataset.
    
    Args:
        dataset_name: Name of the dataset to evaluate against
        experiment_prefix: Prefix for the experiment name
        evaluators: List of evaluator functions (uses defaults if not provided)
        max_concurrency: Maximum concurrent evaluations
        evaluator_mode: Evaluate器模式，Optional值：
            - "all": 所有Evaluate器（Rule + LLM，最全面）
            - "fast": 只用RuleEvaluate器（Fast、免费）
            - "quality": Rule + 幻觉检测（balanced成本和质量）
            - "llm": 只用 LLM-as-judge（最准确）
        
    Returns:
        Evaluation results summary
    """
    if not LANGSMITH_EVAL_AVAILABLE:
        raise ImportError("LangSmith evaluation not available")
    
    # RootdataPatternSelectEvaluateer
    if evaluators is None:
        mode_map = {
            "all": get_all_evaluators,           # All（Rule + LLM）
            "fast": get_fast_evaluators,         # Fast（onlyhaveRule）
            "quality": get_quality_evaluators,   # balanced（Rule + hallucination + TaskComplete）
            "llm": get_llm_evaluators,           # LLM（semantic understanding）
            "rule": get_rule_evaluators,         # Rule（objective metrics）
            "essential": get_essential_evaluators, # Core（Delayed、Error、TaskComplete、hallucination）
            "ux": get_ux_evaluators,             # UX（TTFT、follow-up、richrichdegree）
        }
        
        if evaluator_mode in mode_map:
            evaluators = mode_map[evaluator_mode]()
            logger.info(f"Using evaluator mode: {evaluator_mode}")
        else:
            # DefaultUsageallEvaluateer
            evaluators = get_all_evaluators()
            logger.info(f"Unknown mode '{evaluator_mode}', using all evaluators")
    
    logger.info(f"Starting evaluation on dataset '{dataset_name}'...")
    logger.info(f"Using {len(evaluators)} evaluators")
    
    # Get agent function
    agent_fn = get_agent_function()
    
    # Run evaluation
    logger.info(f"Running evaluation with max_concurrency={max_concurrency}")
    
    try:
        results = evaluate(
            agent_fn,
            data=dataset_name,
            evaluators=evaluators,
            experiment_prefix=experiment_prefix,
            max_concurrency=max_concurrency,
            metadata={
                "agent": "NogicOS ReActAgent",
                "version": "2.0",
            },
        )
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Process results - iterate directly over ExperimentResults
    summary = {
        "experiment_name": results.experiment_name,
        "total_examples": 0,
        "scores": {},
    }
    
    # ExperimentResults is iterable, each row is an ExperimentResultRow object
    for row in results:
        summary["total_examples"] += 1
        
        # ExperimentResultRow has 'run', 'example', and 'evaluation_results' as attributes
        # Try multiple access patterns
        try:
            # Try attribute access first (newer LangSmith versions)
            if hasattr(row, 'evaluation_results'):
                eval_results = row.evaluation_results
            elif isinstance(row, dict):
                eval_results = row.get("evaluation_results", {})
            else:
                eval_results = {}
            
            # eval_results is typically a dict of {evaluator_name: EvaluationResult}
            if eval_results:
                for key, value in eval_results.items():
                    if key not in summary["scores"]:
                        summary["scores"][key] = []
                    
                    # Extract score from EvaluationResult
                    score = 0
                    if hasattr(value, 'score'):
                        score = value.score or 0
                    elif isinstance(value, dict):
                        score = value.get("score", 0)
                    elif isinstance(value, (int, float)):
                        score = value
                    
                    summary["scores"][key].append(score)
        except Exception as e:
            logger.warning(f"Failed to process row: {e}")
    
    # Calculate averages
    for key, scores in list(summary["scores"].items()):
        if scores:
            summary["scores"][key] = {
                "avg": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "count": len(scores),
            }
    
    logger.info(f"Evaluation complete: {summary['experiment_name']}")
    logger.info(f"Results: {summary['scores']}")
    
    return summary


def main():
    """Main entry point."""
    # ensure API Keys beLoad
    try:
        import api_keys
        api_keys.setup_env()
    except ImportError:
        logger.warning("[Evaluation] api_keys.py not found, ensure environment variables are set")
    
    parser = argparse.ArgumentParser(description="NogicOS Evaluation Runner")
    
    parser.add_argument(
        "--create-golden",
        action="store_true",
        help="Create golden test dataset (alias for --create-comprehensive)",
    )
    parser.add_argument(
        "--create-comprehensive",
        action="store_true",
        help="Create comprehensive test dataset (45 examples)",
    )
    parser.add_argument(
        "--create-from-runs",
        action="store_true",
        help="Create dataset from recent runs",
    )
    parser.add_argument(
        "--evaluate",
        type=str,
        metavar="DATASET",
        help="Run evaluation on specified dataset",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default="nogicos_from_runs",
        help="Dataset name for --create-from-runs",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of runs to include (for --create-from-runs)",
    )
    parser.add_argument(
        "--list-datasets",
        action="store_true",
        help="List all datasets",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="Max concurrent evaluations",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="all",
        choices=["all", "fast", "quality", "llm", "rule", "essential", "ux"],
        help="Evaluator mode: all=全部, fast=Rule, quality=Rule+幻觉+任务, llm=LLM, rule=Rule, essential=Core, ux=User体验(TTFT/追问/丰富度)",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging("INFO")
    
    try:
        if args.create_golden or args.create_comprehensive:
            logger.info("Creating comprehensive dataset (45 examples)...")
            info = create_comprehensive_dataset()
            print(f"[OK] Created: {info.name} ({info.example_count} examples)")
            print(f"     ID: {info.id}")
            print(f"\nCategories:")
            print(f"  - Simple chat: 3")
            print(f"  - File operations: 8")
            print(f"  - Browser operations: 6")
            print(f"  - Search functions: 3")
            print(f"  - Desktop operations: 5 (core)")
            print(f"  - Vision operations: 2")
            print(f"  - Shell commands: 2")
            print(f"  - Cross-domain tasks: 5 (core)")
            print(f"  - Memory/State: 3")
            print(f"  - Error recovery: 4")
            print(f"  - Security boundaries: 3")
            print(f"  - Parallel execution: 1")
        
        elif args.create_from_runs:
            logger.info(f"Creating dataset from recent runs (limit={args.limit})...")
            info = create_dataset_from_runs(
                dataset_name=args.dataset_name,
                limit=args.limit,
            )
            print(f"[OK] Created: {info.name} ({info.example_count} examples)")
            print(f"     ID: {info.id}")
        
        elif args.evaluate:
            logger.info(f"Running evaluation on '{args.evaluate}' with mode '{args.mode}'...")
            results = run_evaluation(
                dataset_name=args.evaluate,
                max_concurrency=args.concurrency,
                evaluator_mode=args.mode,
            )
            print("\n" + "="*50)
            print(f"[RESULTS] {results['experiment_name']}")
            print("="*50)
            print(f"Total examples: {results['total_examples']}")
            print("\nScores:")
            for key, stats in results["scores"].items():
                print(f"  {key}: avg={stats['avg']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}")
        
        elif args.list_datasets:
            manager = DatasetManager()
            datasets = manager.list_datasets()
            print(f"\n[DATASETS] ({len(datasets)}):")
            for ds in datasets:
                print(f"  - {ds.name}: {ds.example_count} examples")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

