# -*- coding: utf-8 -*-
"""
DeepEval Runner for NogicOS Agent Evaluation

Provides automated evaluation using DeepEval framework with:
- TaskCompletionMetric for end-to-end agent performance
- Custom trajectory metrics for tool call evaluation
- Integration with existing benchmark infrastructure
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from deepeval import evaluate
    from deepeval.tracing import observe, update_current_span
    from deepeval.test_case import LLMTestCase, ToolCall
    from deepeval.dataset import EvaluationDataset, Golden
    from deepeval.metrics import TaskCompletionMetric, AnswerRelevancyMetric
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False
    print("[Warning] DeepEval not installed. Run: pip install deepeval")


@dataclass
class EvaluationConfig:
    """Configuration for DeepEval evaluation"""
    model: str = "gpt-4o-mini"
    threshold: float = 0.7
    strict_mode: bool = False
    async_mode: bool = True
    include_reason: bool = True


class DeepEvalRunner:
    """
    Runs DeepEval evaluations on NogicOS Agent
    
    Example:
        runner = DeepEvalRunner()
        results = await runner.evaluate_agent(queries)
    """
    
    def __init__(self, config: Optional[EvaluationConfig] = None):
        self.config = config or EvaluationConfig()
        self.agent = None
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Initialize evaluation metrics"""
        if not DEEPEVAL_AVAILABLE:
            self.metrics = []
            return
        
        self.task_completion_metric = TaskCompletionMetric(
            threshold=self.config.threshold,
            model=self.config.model,
            strict_mode=self.config.strict_mode,
            async_mode=self.config.async_mode,
            include_reason=self.config.include_reason,
        )
        
        self.answer_relevancy_metric = AnswerRelevancyMetric(
            threshold=self.config.threshold,
            model=self.config.model,
            strict_mode=self.config.strict_mode,
            async_mode=self.config.async_mode,
            include_reason=self.config.include_reason,
        )
        
        self.metrics = [
            self.task_completion_metric,
            self.answer_relevancy_metric,
        ]
    
    async def setup_agent(self):
        """Initialize the NogicOS agent"""
        try:
            from engine.agent.react_agent import ReActAgent
            self.agent = ReActAgent(max_iterations=10)
            return True
        except Exception as e:
            print(f"[Error] Failed to initialize agent: {e}")
            return False
    
    async def cleanup_agent(self):
        """Cleanup agent resources"""
        if self.agent:
            try:
                await self.agent.cleanup_browser_session()
            except:
                pass
    
    def create_test_case(
        self,
        input_query: str,
        actual_output: str,
        expected_output: Optional[str] = None,
        tools_called: Optional[List[Dict]] = None,
        retrieval_context: Optional[List[str]] = None,
    ) -> "LLMTestCase":
        """Create a DeepEval test case from agent output"""
        if not DEEPEVAL_AVAILABLE:
            return None
        
        # Convert tool calls to DeepEval format
        deepeval_tools = []
        if tools_called:
            for tool in tools_called:
                deepeval_tools.append(ToolCall(
                    name=tool.get("name", "unknown"),
                    input=tool.get("arguments", {}),
                    output=tool.get("result", ""),
                ))
        
        return LLMTestCase(
            input=input_query,
            actual_output=actual_output,
            expected_output=expected_output,
            retrieval_context=retrieval_context,
            tools_called=deepeval_tools if deepeval_tools else None,
        )
    
    async def evaluate_single(
        self,
        query: str,
        expected_output: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a single query against the agent
        
        Returns:
            dict with keys: passed, scores, response, error
        """
        if not self.agent:
            await self.setup_agent()
        
        result = {
            "query": query,
            "passed": False,
            "scores": {},
            "response": "",
            "tools_called": [],
            "error": None,
        }
        
        try:
            # Run agent
            agent_result = await asyncio.wait_for(
                self.agent.run(task=query, session_id=session_id or "eval"),
                timeout=120
            )
            
            result["response"] = agent_result.response if agent_result else ""
            result["tools_called"] = getattr(agent_result, "tool_calls", [])
            
            if not DEEPEVAL_AVAILABLE:
                result["passed"] = bool(result["response"])
                return result
            
            # Create test case
            test_case = self.create_test_case(
                input_query=query,
                actual_output=result["response"],
                expected_output=expected_output,
                tools_called=result["tools_called"],
            )
            
            # Run metrics
            for metric in self.metrics:
                try:
                    metric.measure(test_case)
                    result["scores"][metric.__class__.__name__] = {
                        "score": metric.score,
                        "passed": metric.is_successful(),
                        "reason": getattr(metric, "reason", None),
                    }
                except Exception as e:
                    result["scores"][metric.__class__.__name__] = {
                        "score": 0.0,
                        "passed": False,
                        "error": str(e),
                    }
            
            # Determine overall pass/fail
            result["passed"] = all(
                s.get("passed", False) for s in result["scores"].values()
            )
            
        except asyncio.TimeoutError:
            result["error"] = "Timeout"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def evaluate_dataset(
        self,
        dataset: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluate multiple queries from a dataset
        
        Args:
            dataset: List of dicts with 'input' and optional 'expected_output'
        
        Returns:
            Aggregated results with overall metrics
        """
        await self.setup_agent()
        
        results = []
        for i, item in enumerate(dataset):
            query = item.get("input") or item.get("query")
            expected = item.get("expected_output") or item.get("expected")
            
            print(f"[{i+1}/{len(dataset)}] Evaluating: {query[:50]}...")
            
            result = await self.evaluate_single(
                query=query,
                expected_output=expected,
                session_id=f"eval_{i}",
            )
            results.append(result)
        
        await self.cleanup_agent()
        
        # Aggregate results
        passed_count = sum(1 for r in results if r["passed"])
        total_count = len(results)
        
        # Aggregate scores by metric
        metric_scores = {}
        for result in results:
            for metric_name, score_data in result.get("scores", {}).items():
                if metric_name not in metric_scores:
                    metric_scores[metric_name] = []
                metric_scores[metric_name].append(score_data.get("score", 0.0))
        
        avg_scores = {
            name: sum(scores) / len(scores) if scores else 0.0
            for name, scores in metric_scores.items()
        }
        
        return {
            "total": total_count,
            "passed": passed_count,
            "success_rate": passed_count / total_count if total_count > 0 else 0.0,
            "average_scores": avg_scores,
            "results": results,
        }
    
    def create_evaluation_dataset(
        self,
        goldens: List[Dict[str, Any]],
    ) -> "EvaluationDataset":
        """Create a DeepEval EvaluationDataset from golden examples"""
        if not DEEPEVAL_AVAILABLE:
            return None
        
        golden_objects = []
        for item in goldens:
            golden_objects.append(Golden(
                input=item.get("input") or item.get("query"),
                expected_output=item.get("expected_output") or item.get("expected"),
            ))
        
        return EvaluationDataset(goldens=golden_objects)


# Convenience function for standalone evaluation
async def run_evaluation(
    queries: List[str],
    config: Optional[EvaluationConfig] = None,
) -> Dict[str, Any]:
    """
    Run evaluation on a list of queries
    
    Example:
        results = await run_evaluation([
            "List files in current directory",
            "Search for Python files",
        ])
    """
    runner = DeepEvalRunner(config=config)
    dataset = [{"input": q} for q in queries]
    return await runner.evaluate_dataset(dataset)


# Entry point for CLI
if __name__ == "__main__":
    import json
    
    # Example evaluation
    test_queries = [
        {"input": "What is the current directory?"},
        {"input": "List all Python files in the project"},
        {"input": "Read the README.md file"},
    ]
    
    async def main():
        runner = DeepEvalRunner()
        results = await runner.evaluate_dataset(test_queries)
        
        print("\n" + "=" * 60)
        print("DEEPEVAL RESULTS")
        print("=" * 60)
        print(f"Success Rate: {results['success_rate']:.1%}")
        print(f"Passed: {results['passed']}/{results['total']}")
        print("\nAverage Scores:")
        for name, score in results["average_scores"].items():
            print(f"  {name}: {score:.3f}")
        
        # Save results
        output_path = Path(__file__).parent / "deepeval_results.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nResults saved to: {output_path}")
    
    asyncio.run(main())



