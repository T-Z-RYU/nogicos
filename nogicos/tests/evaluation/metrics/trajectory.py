# -*- coding: utf-8 -*-
"""
Trajectory Accuracy Metric for NogicOS Agent Evaluation

Evaluates whether the agent's tool call sequence matches expected trajectory.
Based on LangSmith trajectory evaluation approach.
"""

from typing import Any, Dict, List, Optional

try:
    from deepeval.metrics import BaseMetric
    from deepeval.test_case import LLMTestCase
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False
    # Provide stub classes for when DeepEval is not installed
    class BaseMetric:
        pass
    class LLMTestCase:
        pass


class TrajectoryAccuracyMetric(BaseMetric if DEEPEVAL_AVAILABLE else object):
    """
    Evaluates the accuracy of agent's tool call trajectory.
    
    Compares the sequence of tools called by the agent against
    an expected trajectory. Supports both strict sequence matching
    and set-based matching (tools called regardless of order).
    
    Attributes:
        threshold: Minimum score to pass (0.0 to 1.0)
        strict_order: If True, order of tool calls must match exactly
        include_reason: Include explanation for score
    
    Example:
        metric = TrajectoryAccuracyMetric(threshold=0.7, strict_order=False)
        test_case = LLMTestCase(
            input="Find Python files",
            actual_output="Found 10 files",
            tools_called=[ToolCall(name="glob_search", ...)],
        )
        metric.measure(test_case)
        print(metric.score)  # 0.85
    """
    
    def __init__(
        self,
        threshold: float = 0.7,
        strict_order: bool = False,
        include_reason: bool = True,
        expected_trajectory: Optional[List[str]] = None,
    ):
        if DEEPEVAL_AVAILABLE:
            super().__init__()
        
        self.threshold = threshold
        self.strict_order = strict_order
        self.include_reason = include_reason
        self.expected_trajectory = expected_trajectory or []
        
        # Results
        self.score: float = 0.0
        self.reason: str = ""
        self._success: bool = False
    
    @property
    def name(self) -> str:
        return "TrajectoryAccuracyMetric"
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure trajectory accuracy for a test case.
        
        Args:
            test_case: LLMTestCase with tools_called attribute
        
        Returns:
            Score between 0.0 and 1.0
        """
        # Get actual tool calls from test case
        tools_called = getattr(test_case, "tools_called", []) or []
        actual_tools = [
            tool.name if hasattr(tool, "name") else str(tool)
            for tool in tools_called
        ]
        
        # Get expected trajectory (from test case context or instance)
        expected_tools = self.expected_trajectory
        if hasattr(test_case, "context") and test_case.context:
            if isinstance(test_case.context, dict):
                expected_tools = test_case.context.get("expected_trajectory", expected_tools)
        
        if not expected_tools:
            # No expected trajectory defined - check if any tools were called
            self.score = 1.0 if actual_tools else 0.5
            self.reason = "No expected trajectory defined"
            self._success = self.score >= self.threshold
            return self.score
        
        if self.strict_order:
            self.score = self._calculate_sequence_score(actual_tools, expected_tools)
        else:
            self.score = self._calculate_set_score(actual_tools, expected_tools)
        
        self._success = self.score >= self.threshold
        return self.score
    
    def _calculate_sequence_score(
        self,
        actual: List[str],
        expected: List[str],
    ) -> float:
        """Calculate score based on exact sequence matching (LCS-based)"""
        if not expected:
            return 1.0 if not actual else 0.5
        
        # Longest Common Subsequence approach
        m, n = len(actual), len(expected)
        if m == 0 or n == 0:
            return 0.0
        
        # Build LCS matrix
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if actual[i-1].lower() == expected[j-1].lower():
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        lcs_length = dp[m][n]
        score = lcs_length / max(m, n)
        
        self.reason = (
            f"Sequence match: {lcs_length}/{max(m, n)} tools in correct order. "
            f"Expected: {expected}, Got: {actual}"
        )
        
        return score
    
    def _calculate_set_score(
        self,
        actual: List[str],
        expected: List[str],
    ) -> float:
        """Calculate score based on set matching (tools called regardless of order)"""
        if not expected:
            return 1.0 if not actual else 0.5
        
        actual_set = set(t.lower() for t in actual)
        expected_set = set(t.lower() for t in expected)
        
        # Calculate intersection and union
        intersection = actual_set & expected_set
        union = actual_set | expected_set
        
        if not union:
            return 1.0
        
        # Jaccard similarity
        jaccard = len(intersection) / len(union)
        
        # Also consider recall (how many expected tools were called)
        recall = len(intersection) / len(expected_set) if expected_set else 1.0
        
        # Weighted average favoring recall
        score = 0.6 * recall + 0.4 * jaccard
        
        missing = expected_set - actual_set
        extra = actual_set - expected_set
        
        self.reason = (
            f"Set match: {len(intersection)}/{len(expected_set)} expected tools called. "
            f"Missing: {list(missing) if missing else 'none'}. "
            f"Extra: {list(extra) if extra else 'none'}."
        )
        
        return score
    
    def is_successful(self) -> bool:
        """Check if the metric passed"""
        return self._success
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async version of measure (for compatibility)"""
        return self.measure(test_case)



