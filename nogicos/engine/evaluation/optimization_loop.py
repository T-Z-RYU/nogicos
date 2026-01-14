# -*- coding: utf-8 -*-
"""
NogicOS Optimization Loop - 闭环优化System（整合 LangSmith）

完整流程：
1. Evaluate当BeforePerformance (baseline) - Usage LangSmith + NewEvaluate器
2. DSPy 优化
3. Evaluate优化AfterPerformance
4. A/B 对比
5. 如果更好则Save，No则Rollback

用法：
    # CompleteOptimizationLoop（Usage LangSmith Dataset）
    python -m engine.evaluation.optimization_loop --full-cycle
    
    # onlyRunningEvaluate（notOptimization）
    python -m engine.evaluation.optimization_loop --evaluate-only
    
    # ViewHistory
    python -m engine.evaluation.optimization_loop --history
    
    # UsageFastPattern（onlyuseRuleEvaluateer）
    python -m engine.evaluation.optimization_loop --full-cycle --mode fast
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Fix encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add parent path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from engine.observability import get_logger, setup_logging
setup_logging()
logger = get_logger("optimization_loop")


class OptimizationLoop:
    """
    闭环优化System（整合 LangSmith）
    
    Core原则：优化必须可Verify，No则不部署
    
    支持两种Evaluate模式：
    1. LangSmith 模式（推荐）：Usage LangSmith 数据集和New的Evaluate器体系
    2. Legacy 模式：Usage原来的 auto_data_collector 生成任务
    """
    
    DEFAULT_DATASET = "nogicos_comprehensive"
    
    def __init__(self, output_dir: str = "data/optimization_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # RecordeachtimeOptimization's Result
        self.history_file = self.output_dir / "optimization_history.json"
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def run_langsmith_evaluation(
        self,
        label: str,
        dataset_name: str = None,
        evaluator_mode: str = "essential",
        max_concurrency: int = 2,
    ) -> Dict[str, Any]:
        """
        Usage LangSmith RunningEvaluate（推荐）
        
        Args:
            label: Evaluate标签 (baseline/optimized)
            dataset_name: 数据集名称
            evaluator_mode: Evaluate器模式 (all/fast/quality/essential)
            max_concurrency: Concurrent数
            
        Returns:
            EvaluateResult
        """
        from engine.evaluation.run_evaluation import run_evaluation
        
        dataset_name = dataset_name or self.DEFAULT_DATASET
        
        logger.info(f"[{label}] Usage LangSmith Evaluate...")
        logger.info(f"  数据集: {dataset_name}")
        logger.info(f"  模式: {evaluator_mode}")
        
        try:
            results = run_evaluation(
                dataset_name=dataset_name,
                experiment_prefix=f"opt_{label}",
                evaluator_mode=evaluator_mode,
                max_concurrency=max_concurrency,
            )
            
            # ExtractionCoremetric
            scores = results.get("scores", {})
            
            # calculateoverallminute
            composite_score = self._calculate_composite_score(scores)
            
            eval_result = {
                "label": label,
                "timestamp": datetime.now().isoformat(),
                "dataset": dataset_name,
                "evaluator_mode": evaluator_mode,
                "experiment_name": results.get("experiment_name", ""),
                "total_examples": results.get("total_examples", 0),
                "scores": scores,
                "composite_score": composite_score,
            }
            
            logger.info(f"[{label}] LangSmith EvaluateComplete:")
            logger.info(f"  总Sample数: {eval_result['total_examples']}")
            logger.info(f"  综合得分: {composite_score:.3f}")
            for key, stat in scores.items():
                if isinstance(stat, dict):
                    logger.info(f"  {key}: {stat.get('avg', 0):.3f}")
            
            return eval_result
            
        except Exception as e:
            logger.error(f"[{label}] LangSmith EvaluateFailed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "label": label,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "composite_score": 0.0,
            }
    
    def _calculate_composite_score(self, scores: Dict[str, Any]) -> float:
        """
        计算综合得分
        
        WeightAllocate（基于最佳实践）：
        - task_completion_llm: 0.30 (任务CompleteYes最Important的)
        - hallucination: 0.20 (幻觉检测)
        - error_rate: 0.15 (Error率)
        - latency: 0.15 (Delayed)
        - correctness: 0.10 (正确性)
        - conciseness: 0.05 (简洁性)
        - tool_selection_llm: 0.05 (ToolSelect)
        """
        weights = {
            "task_completion_llm": 0.30,
            "hallucination": 0.20,
            "error_rate": 0.15,
            "latency": 0.15,
            "correctness": 0.10,
            "conciseness": 0.05,
            "tool_selection_llm": 0.05,
        }
        
        total_weight = 0
        total_score = 0
        
        for key, weight in weights.items():
            if key in scores:
                stat = scores[key]
                avg = stat.get("avg", 0) if isinstance(stat, dict) else stat
                total_score += avg * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        
        # Fallback: UsageallAvailable's minutenumber
        all_avgs = []
        for key, stat in scores.items():
            if isinstance(stat, dict):
                all_avgs.append(stat.get("avg", 0))
        
        return sum(all_avgs) / len(all_avgs) if all_avgs else 0.5
    
    async def run_legacy_evaluation(self, label: str, test_count: int = 20) -> Dict[str, Any]:
        """
        Usage原来的方式RunningEvaluate（Legacy 模式）
        
        保留此Method以支持向After兼容
        """
        from engine.evaluation.auto_data_collector import (
            generate_tasks,
            quick_quality_check,
            run_task_and_collect,
        )
        from engine.agent.react_agent import ReActAgent
        
        logger.info(f"[{label}] Usage Legacy Evaluate方式...")
        
        agent = ReActAgent()
        
        results = {
            "label": label,
            "timestamp": datetime.now().isoformat(),
            "test_count": test_count,
            "success_count": 0,
            "high_quality_count": 0,
            "total_latency_ms": 0,
            "errors": [],
        }
        
        tasks = generate_tasks(test_count)
        
        for i, task in enumerate(tasks):
            logger.info(f"  [{i+1}/{test_count}] {task[:40]}...")
            
            result = await run_task_and_collect(agent, task, f"eval_{label}_{i}")
            
            if result.get("success"):
                results["success_count"] += 1
                results["total_latency_ms"] += result.get("duration_ms", 0)
                
                is_quality, reason = quick_quality_check(result)
                if is_quality:
                    results["high_quality_count"] += 1
            else:
                results["errors"].append({
                    "task": task[:50],
                    "error": str(result.get("error", "unknown"))[:100]
                })
        
        # calculatemetric
        results["success_rate"] = results["success_count"] / test_count
        results["quality_rate"] = results["high_quality_count"] / test_count
        results["avg_latency_ms"] = (
            results["total_latency_ms"] / results["success_count"]
            if results["success_count"] > 0 else 0
        )
        
        # overallminute
        results["composite_score"] = (
            results["success_rate"] * 0.4 +
            results["quality_rate"] * 0.4 +
            min(1.0, 10000 / max(results["avg_latency_ms"], 1)) * 0.2
        )
        
        logger.info(f"[{label}] Legacy EvaluateComplete:")
        logger.info(f"  Success率: {results['success_rate']:.1%}")
        logger.info(f"  质量率: {results['quality_rate']:.1%}")
        logger.info(f"  综合得分: {results['composite_score']:.2f}")
        
        return results
    
    async def run_dspy_optimization(self) -> bool:
        """
        Running DSPy 优化
        """
        try:
            from engine.agent.dspy_optimizer import (
                DSPyClassifier,
                optimize_classifier,
                DSPY_AVAILABLE,
            )
            
            if not DSPY_AVAILABLE:
                logger.error("DSPy 不Available，请安装: pip install dspy-ai")
                return False
            
            logger.info("[DSPy] Begin优化...")
            
            # CreateminuteClasserInstance
            classifier = DSPyClassifier()
            
            # RunningOptimization
            optimized = optimize_classifier(classifier, auto="light")
            
            # SaveOptimizationAfter's minuteClasser
            if optimized:
                save_path = Path("data/dspy_cache/optimized_classifier.json")
                save_path.parent.mkdir(parents=True, exist_ok=True)
                optimized.save(str(save_path))
                logger.info(f"[DSPy] 优化Complete，已Save到: {save_path}")
                return True
            
            return False
        except ImportError as e:
            logger.error(f"[DSPy] ModuleImportFailed: {e}")
            logger.error("请确保已安装 dspy-ai: pip install dspy-ai")
            return False
        except Exception as e:
            logger.error(f"[DSPy] 优化Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def full_cycle(
        self,
        use_langsmith: bool = True,
        dataset_name: str = None,
        evaluator_mode: str = "essential",
        test_count: int = 20,
        min_improvement: float = 0.05,
        max_concurrency: int = 2,
    ) -> Dict[str, Any]:
        """
        完整优化Loop
        
        Args:
            use_langsmith: Usage LangSmith Evaluate（推荐）
            dataset_name: 数据集名称（LangSmith 模式）
            evaluator_mode: Evaluate器模式
            test_count: TestCount（Legacy 模式）
            min_improvement: Min提升Threshold
            max_concurrency: Concurrent数
            
        Returns:
            LoopResult
        """
        cycle_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info("=" * 60)
        logger.info(f"优化LoopBegin: {cycle_id}")
        logger.info(f"模式: {'LangSmith' if use_langsmith else 'Legacy'}")
        logger.info("=" * 60)
        
        cycle_result = {
            "cycle_id": cycle_id,
            "timestamp": datetime.now().isoformat(),
            "mode": "langsmith" if use_langsmith else "legacy",
            "evaluator_mode": evaluator_mode,
            "min_improvement": min_improvement,
        }
        
        # Step 1: Baseline Evaluate
        logger.info("\n[Step 1/4] Evaluate当BeforePerformance (Baseline)...")
        if use_langsmith:
            baseline = self.run_langsmith_evaluation(
                "baseline",
                dataset_name=dataset_name,
                evaluator_mode=evaluator_mode,
                max_concurrency=max_concurrency,
            )
        else:
            baseline = await self.run_legacy_evaluation("baseline", test_count)
        
        cycle_result["baseline"] = baseline
        
        if baseline.get("error"):
            cycle_result["decision"] = "SKIP"
            cycle_result["reason"] = f"Baseline EvaluateFailed: {baseline.get('error')}"
            self.history.append(cycle_result)
            self._save_history()
            return cycle_result
        
        # Step 2: DSPy Optimization
        logger.info("\n[Step 2/4] Running DSPy 优化...")
        optimization_success = await self.run_dspy_optimization()
        cycle_result["optimization_success"] = optimization_success
        
        if not optimization_success:
            cycle_result["decision"] = "SKIP"
            cycle_result["reason"] = "DSPy 优化Failed"
            self.history.append(cycle_result)
            self._save_history()
            return cycle_result
        
        # Step 3: OptimizationAfterEvaluate
        logger.info("\n[Step 3/4] Evaluate优化AfterPerformance...")
        if use_langsmith:
            optimized = self.run_langsmith_evaluation(
                "optimized",
                dataset_name=dataset_name,
                evaluator_mode=evaluator_mode,
                max_concurrency=max_concurrency,
            )
        else:
            optimized = await self.run_legacy_evaluation("optimized", test_count)
        
        cycle_result["optimized"] = optimized
        
        if optimized.get("error"):
            cycle_result["decision"] = "SKIP"
            cycle_result["reason"] = f"优化AfterEvaluateFailed: {optimized.get('error')}"
            self.history.append(cycle_result)
            self._save_history()
            return cycle_result
        
        # Step 4: Compare & decide
        logger.info("\n[Step 4/4] CompareResult...")
        baseline_score = baseline.get("composite_score", 0)
        optimized_score = optimized.get("composite_score", 0)
        improvement = optimized_score - baseline_score
        improvement_pct = improvement / max(baseline_score, 0.01)
        
        cycle_result["improvement"] = improvement
        cycle_result["improvement_pct"] = improvement_pct
        
        logger.info("\n" + "=" * 60)
        logger.info("优化Result对比")
        logger.info("=" * 60)
        logger.info(f"  Baseline 得分:  {baseline_score:.3f}")
        logger.info(f"  Optimized 得分: {optimized_score:.3f}")
        logger.info(f"  提升: {improvement:+.3f} ({improvement_pct:+.1%})")
        
        if improvement >= min_improvement:
            cycle_result["decision"] = "DEPLOY"
            cycle_result["reason"] = f"提升 {improvement_pct:.1%} >= {min_improvement:.0%}"
            logger.info(f"\n[OK] 决策: DEPLOY - 优化Valid，SaveNewConfig")
        else:
            cycle_result["decision"] = "ROLLBACK"
            cycle_result["reason"] = f"提升 {improvement_pct:.1%} < {min_improvement:.0%}"
            logger.info(f"\n[SKIP] 决策: ROLLBACK - 提升不足，保持原Config")
        
        # SaveHistory
        self.history.append(cycle_result)
        self._save_history()
        
        # Save this timedetailedResult
        result_file = self.output_dir / f"cycle_{cycle_id}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(cycle_result, f, ensure_ascii=False, indent=2)
        logger.info(f"\n详细Result已Save: {result_file}")
        
        return cycle_result
    
    def show_history(self):
        """Display优化历史"""
        if not self.history:
            print("没有优化历史记录")
            return
        
        print("\n" + "=" * 80)
        print("优化历史")
        print("=" * 80)
        print(f"{'Time':<20} {'模式':<10} {'Baseline':<10} {'Optimized':<10} {'提升':<10} {'决策':<10}")
        print("-" * 80)
        
        for h in self.history[-10:]:  # mostnear 10 item
            timestamp = h.get("timestamp", "")[:16]
            mode = h.get("mode", "legacy")[:8]
            baseline_score = h.get("baseline", {}).get("composite_score", 0)
            optimized_score = h.get("optimized", {}).get("composite_score", 0)
            improvement = h.get("improvement_pct", 0)
            decision = h.get("decision", "N/A")
            
            print(f"{timestamp:<20} {mode:<10} {baseline_score:<10.3f} {optimized_score:<10.3f} {improvement:+.1%}     {decision:<10}")
        
        print("=" * 80)


async def main():
    # Load API Keys
    try:
        import api_keys
        api_keys.setup_env()
    except ImportError:
        logger.warning("[Optimization] api_keys.py not found")
    
    parser = argparse.ArgumentParser(description="NogicOS 闭环优化System（整合 LangSmith）")
    
    # mainlyCommand
    parser.add_argument("--full-cycle", action="store_true", help="Running完整优化Loop")
    parser.add_argument("--evaluate-only", action="store_true", help="只RunningEvaluate（不优化）")
    parser.add_argument("--history", action="store_true", help="Display优化历史")
    
    # EvaluateConfig
    parser.add_argument("--dataset", type=str, default="nogicos_comprehensive", help="数据集名称")
    parser.add_argument("--mode", type=str, default="essential", 
                       choices=["all", "fast", "quality", "essential", "llm", "rule"],
                       help="Evaluate器模式")
    parser.add_argument("--concurrency", type=int, default=2, help="Concurrent数")
    parser.add_argument("--min-improvement", type=float, default=0.05, help="Min提升Threshold")
    
    # Legacy Pattern
    parser.add_argument("--legacy", action="store_true", help="Usage Legacy Evaluate模式")
    parser.add_argument("--test-count", type=int, default=20, help="TestCount（Legacy 模式）")
    
    args = parser.parse_args()
    
    loop = OptimizationLoop()
    
    if args.history:
        loop.show_history()
    
    elif args.evaluate_only:
        logger.info("Running单次Evaluate（不优化）...")
        if args.legacy:
            result = await loop.run_legacy_evaluation("evaluate", args.test_count)
        else:
            result = loop.run_langsmith_evaluation(
                "evaluate",
                dataset_name=args.dataset,
                evaluator_mode=args.mode,
                max_concurrency=args.concurrency,
            )
        
        print("\n" + "=" * 50)
        print("[RESULT] EvaluateComplete")
        print("=" * 50)
        print(f"综合得分: {result.get('composite_score', 0):.3f}")
        if "scores" in result:
            print("\n详细分数:")
            for key, stat in result["scores"].items():
                if isinstance(stat, dict):
                    print(f"  {key}: {stat.get('avg', 0):.3f}")
    
    elif args.full_cycle:
        await loop.full_cycle(
            use_langsmith=not args.legacy,
            dataset_name=args.dataset,
            evaluator_mode=args.mode,
            test_count=args.test_count,
            min_improvement=args.min_improvement,
            max_concurrency=args.concurrency,
        )
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
