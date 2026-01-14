# -*- coding: utf-8 -*-
"""
Evaluators - Based on WebArena/OSWorld evaluation standards

Evaluator Types:
- StringEvaluator: Text matching (exact, must_include, fuzzy)
- URLEvaluator: URL validation
- FileEvaluator: File existence and content validation
- HTMLContentEvaluator: DOM content validation
"""

import os
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path


@dataclass
class EvaluationResult:
    """Result of an evaluation"""
    score: float  # 0.0 to 1.0
    passed: bool
    message: str
    details: Dict[str, Any]


class BaseEvaluator(ABC):
    """Base class for all evaluators"""
    
    @abstractmethod
    def evaluate(self, result: Any, expected: Any = None) -> EvaluationResult:
        """Evaluate the result against expected value"""
        pass


class StringEvaluator(BaseEvaluator):
    """
    String-based evaluation (WebArena style)
    
    Modes:
    - exact_match: Exact string match (case-insensitive)
    - must_include: All expected phrases must be in result
    - contains: Result must contain expected string
    - regex: Result must match regex pattern
    """
    
    def __init__(self, mode: str = "contains"):
        self.mode = mode
    
    def evaluate(self, result: str, expected: Any = None) -> EvaluationResult:
        if result is None:
            return EvaluationResult(
                score=0.0,
                passed=False,
                message="Result is None",
                details={"mode": self.mode}
            )
        
        result_clean = str(result).strip().lower()
        
        if self.mode == "exact_match":
            expected_clean = str(expected).strip().lower()
            passed = result_clean == expected_clean
            score = 1.0 if passed else 0.0
            message = "Exact match" if passed else f"Expected '{expected}', got '{result[:100]}...'"
            
        elif self.mode == "must_include":
            # expected is a list of phrases that must all be present
            if isinstance(expected, str):
                expected = [expected]
            
            missing = []
            for phrase in expected:
                if phrase.lower() not in result_clean:
                    missing.append(phrase)
            
            passed = len(missing) == 0
            score = 1.0 - (len(missing) / len(expected)) if expected else 1.0
            message = "All phrases found" if passed else f"Missing: {missing}"
            
        elif self.mode == "contains":
            expected_clean = str(expected).strip().lower()
            passed = expected_clean in result_clean
            score = 1.0 if passed else 0.0
            message = "Contains expected" if passed else f"'{expected}' not in result"
            
        elif self.mode == "regex":
            pattern = re.compile(expected, re.IGNORECASE)
            passed = bool(pattern.search(result))
            score = 1.0 if passed else 0.0
            message = "Regex matched" if passed else f"Pattern '{expected}' not found"
            
        else:
            passed = False
            score = 0.0
            message = f"Unknown mode: {self.mode}"
        
        return EvaluationResult(
            score=score,
            passed=passed,
            message=message,
            details={"mode": self.mode, "result_length": len(result)}
        )


class URLEvaluator(BaseEvaluator):
    """
    URL-based evaluation (WebArena style)
    
    Modes:
    - exact: URL must match exactly
    - contains: URL must contain expected string
    - base_path: Base path must match (ignoring query params)
    """
    
    def __init__(self, mode: str = "contains"):
        self.mode = mode
    
    def evaluate(self, result: str, expected: str = None) -> EvaluationResult:
        if result is None:
            return EvaluationResult(
                score=0.0,
                passed=False,
                message="URL is None",
                details={"mode": self.mode}
            )
        
        result_url = str(result).strip().lower()
        expected_url = str(expected).strip().lower() if expected else ""
        
        if self.mode == "exact":
            passed = result_url == expected_url
            score = 1.0 if passed else 0.0
            message = "URL exact match" if passed else f"Expected '{expected}', got '{result}'"
            
        elif self.mode == "contains":
            passed = expected_url in result_url
            score = 1.0 if passed else 0.0
            message = "URL contains expected" if passed else f"'{expected}' not in URL"
            
        elif self.mode == "base_path":
            # Extract base path (remove query string and fragment)
            from urllib.parse import urlparse
            result_parsed = urlparse(result_url)
            expected_parsed = urlparse(expected_url)
            
            result_base = f"{result_parsed.scheme}://{result_parsed.netloc}{result_parsed.path}"
            expected_base = f"{expected_parsed.scheme}://{expected_parsed.netloc}{expected_parsed.path}"
            
            passed = result_base == expected_base
            score = 1.0 if passed else 0.0
            message = "Base path matches" if passed else f"Expected base '{expected_base}', got '{result_base}'"
            
        else:
            passed = False
            score = 0.0
            message = f"Unknown mode: {self.mode}"
        
        return EvaluationResult(
            score=score,
            passed=passed,
            message=message,
            details={"mode": self.mode, "url": result}
        )


class FileEvaluator(BaseEvaluator):
    """
    File-based evaluation (OSWorld style)
    
    Checks:
    - exists: File must exist
    - content_match: File content must match expected
    - json_valid: File must be valid JSON
    - json_has_key: JSON must have specified key
    - csv_rows: CSV must have expected number of rows
    """
    
    def __init__(self, checks: List[Dict[str, Any]] = None):
        self.checks = checks or [{"type": "exists"}]
    
    def evaluate(self, result: str, expected: Any = None) -> EvaluationResult:
        """
        Args:
            result: File path to evaluate
            expected: Expected content or validation rules
        """
        file_path = os.path.expanduser(str(result))
        
        results = []
        all_passed = True
        
        for check in self.checks:
            check_type = check.get("type", "exists")
            check_result = self._run_check(file_path, check_type, check, expected)
            results.append(check_result)
            if not check_result["passed"]:
                all_passed = False
        
        passed_count = sum(1 for r in results if r["passed"])
        score = passed_count / len(results) if results else 0.0
        
        return EvaluationResult(
            score=score,
            passed=all_passed,
            message="All checks passed" if all_passed else f"Failed {len(results) - passed_count}/{len(results)} checks",
            details={"checks": results}
        )
    
    def _run_check(self, file_path: str, check_type: str, check: Dict, expected: Any) -> Dict:
        """Run a single check"""
        try:
            if check_type == "exists":
                passed = os.path.exists(file_path)
                return {"type": check_type, "passed": passed, "message": "File exists" if passed else "File not found"}
            
            elif check_type == "content_match":
                if not os.path.exists(file_path):
                    return {"type": check_type, "passed": False, "message": "File not found"}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                expected_content = check.get("expected", expected)
                passed = content.strip() == str(expected_content).strip()
                return {"type": check_type, "passed": passed, "message": "Content matches" if passed else "Content mismatch"}
            
            elif check_type == "json_valid":
                if not os.path.exists(file_path):
                    return {"type": check_type, "passed": False, "message": "File not found"}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                return {"type": check_type, "passed": True, "message": "Valid JSON"}
            
            elif check_type == "json_has_key":
                if not os.path.exists(file_path):
                    return {"type": check_type, "passed": False, "message": "File not found"}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                key = check.get("key", "")
                passed = key in data
                return {"type": check_type, "passed": passed, "message": f"Key '{key}' found" if passed else f"Key '{key}' missing"}
            
            elif check_type == "not_empty":
                if not os.path.exists(file_path):
                    return {"type": check_type, "passed": False, "message": "File not found"}
                
                size = os.path.getsize(file_path)
                passed = size > 0
                return {"type": check_type, "passed": passed, "message": f"File size: {size} bytes"}
            
            else:
                return {"type": check_type, "passed": False, "message": f"Unknown check type: {check_type}"}
                
        except Exception as e:
            return {"type": check_type, "passed": False, "message": f"Error: {str(e)}"}


class CombinedEvaluator(BaseEvaluator):
    """
    Combine multiple evaluators (WebArena EvaluatorComb style)
    
    Modes:
    - all: All evaluators must pass (score = product of scores)
    - any: Any evaluator can pass (score = max of scores)
    - average: Average of all scores
    """
    
    def __init__(self, evaluators: List[BaseEvaluator], mode: str = "all"):
        self.evaluators = evaluators
        self.mode = mode
    
    def evaluate(self, result: Any, expected: Any = None) -> EvaluationResult:
        if not self.evaluators:
            return EvaluationResult(score=1.0, passed=True, message="No evaluators", details={})
        
        results = []
        for evaluator in self.evaluators:
            eval_result = evaluator.evaluate(result, expected)
            results.append(eval_result)
        
        if self.mode == "all":
            # Product of scores (all must be 1.0 for full score)
            score = 1.0
            for r in results:
                score *= r.score
            passed = all(r.passed for r in results)
            
        elif self.mode == "any":
            # Max of scores (any can pass)
            score = max(r.score for r in results)
            passed = any(r.passed for r in results)
            
        else:  # average
            score = sum(r.score for r in results) / len(results)
            passed = score >= 0.5
        
        return EvaluationResult(
            score=score,
            passed=passed,
            message=f"{self.mode}: {sum(1 for r in results if r.passed)}/{len(results)} passed",
            details={"mode": self.mode, "sub_results": [r.__dict__ for r in results]}
        )


def create_evaluator(config: Dict[str, Any]) -> BaseEvaluator:
    """
    Factory function to create evaluator from config
    
    Config format:
    {
        "type": "string|url|file|combined",
        "mode": "...",
        "checks": [...],  # for file evaluator
        "evaluators": [...]  # for combined evaluator
    }
    """
    eval_type = config.get("type", "string")
    
    if eval_type == "string":
        return StringEvaluator(mode=config.get("mode", "contains"))
    
    elif eval_type == "url":
        return URLEvaluator(mode=config.get("mode", "contains"))
    
    elif eval_type == "file":
        return FileEvaluator(checks=config.get("checks", [{"type": "exists"}]))
    
    elif eval_type == "combined":
        sub_evaluators = [create_evaluator(e) for e in config.get("evaluators", [])]
        return CombinedEvaluator(sub_evaluators, mode=config.get("mode", "all"))
    
    else:
        raise ValueError(f"Unknown evaluator type: {eval_type}")


