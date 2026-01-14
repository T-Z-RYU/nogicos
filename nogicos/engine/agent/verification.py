# -*- coding: utf-8 -*-
"""
Answer Verification Module for NogicOS Agent

Provides verification logic to validate agent answers before submission:
- Format verification (numeric, path, etc.)
- Consistency checks
- Cross-verification with alternative methods

This module is used by the Reflection mechanism in react_agent.py
"""

import re
import os
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum


class VerifyStatus(Enum):
    """Verification result status"""
    VALID = "valid"
    INVALID = "invalid"
    UNCERTAIN = "uncertain"


@dataclass
class VerifyResult:
    """Result of answer verification"""
    status: VerifyStatus
    message: str
    confidence: float = 1.0
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
    
    @property
    def is_valid(self) -> bool:
        return self.status == VerifyStatus.VALID


class AnswerVerifier:
    """
    Verifies agent answers before submission.
    
    Provides multiple verification strategies:
    1. Format verification - checks if answer matches expected format
    2. Range verification - checks if numeric answers are reasonable
    3. Consistency verification - cross-checks with tool outputs
    
    Example:
        verifier = AnswerVerifier()
        result = verifier.verify(
            answer="42",
            task="How many files are in /etc?",
            tool_outputs=["220 files found"]
        )
        if not result.is_valid:
            print(result.message)
    """
    
    def __init__(self):
        # Patterns for detecting expected answer types from task
        self.numeric_patterns = [
            r"how many", r"count", r"number of", r"total",
            r"多少", r"Count", r"Statistics", r"计算",
            r"integer", r"lines", r"files", r"bytes", r"kb", r"mb"
        ]
        
        self.path_patterns = [
            r"which file", r"which directory", r"path to", r"where is",
            r"哪个File", r"Path", r"Position"
        ]
        
        self.boolean_patterns = [
            r"does .* exist", r"is there", r"YesNo", r"有没有"
        ]
    
    def verify(
        self,
        answer: str,
        task: str,
        tool_outputs: List[str] = None,
        context: Dict[str, Any] = None
    ) -> VerifyResult:
        """
        Main verification entry point.
        
        Args:
            answer: The agent's proposed answer
            task: The original task/question
            tool_outputs: List of outputs from tools used
            context: Additional context for verification
            
        Returns:
            VerifyResult with status and details
        """
        results = []
        
        # Run all applicable verifications
        format_result = self.verify_format(answer, task)
        results.append(format_result)
        
        if tool_outputs:
            consistency_result = self.verify_consistency(answer, tool_outputs)
            results.append(consistency_result)
        
        # Aggregate results
        return self._aggregate_results(results)
    
    def verify_format(self, answer: str, task: str) -> VerifyResult:
        """
        Verify answer format matches task expectations.
        
        Args:
            answer: The proposed answer
            task: The original task
            
        Returns:
            VerifyResult for format check
        """
        task_lower = task.lower()
        answer_stripped = answer.strip()
        
        # Check if task expects numeric answer
        if self._expects_numeric(task_lower):
            return self._verify_numeric_format(answer_stripped, task_lower)
        
        # Check if task expects path
        if self._expects_path(task_lower):
            return self._verify_path_format(answer_stripped)
        
        # Check if task expects boolean
        if self._expects_boolean(task_lower):
            return self._verify_boolean_format(answer_stripped)
        
        # Default: accept any non-empty answer
        if answer_stripped:
            return VerifyResult(
                status=VerifyStatus.VALID,
                message="Answer format acceptable",
                confidence=0.8
            )
        else:
            return VerifyResult(
                status=VerifyStatus.INVALID,
                message="Answer is empty",
                confidence=1.0,
                suggestions=["Provide a non-empty answer"]
            )
    
    def verify_consistency(
        self,
        answer: str,
        tool_outputs: List[str]
    ) -> VerifyResult:
        """
        Verify answer is consistent with tool outputs.
        
        Args:
            answer: The proposed answer
            tool_outputs: List of tool output strings
            
        Returns:
            VerifyResult for consistency check
        """
        if not tool_outputs:
            return VerifyResult(
                status=VerifyStatus.UNCERTAIN,
                message="No tool outputs to verify against",
                confidence=0.5
            )
        
        answer_stripped = answer.strip()
        
        # Extract numbers from answer
        answer_numbers = re.findall(r'\d+', answer_stripped)
        
        if answer_numbers:
            # Check if any answer number appears in tool outputs
            for output in tool_outputs:
                for num in answer_numbers:
                    if num in str(output):
                        return VerifyResult(
                            status=VerifyStatus.VALID,
                            message=f"Answer '{num}' found in tool output",
                            confidence=0.9
                        )
            
            # Number not found in outputs
            return VerifyResult(
                status=VerifyStatus.UNCERTAIN,
                message=f"Answer numbers {answer_numbers} not found in tool outputs",
                confidence=0.4,
                suggestions=["Verify the answer matches the tool output"]
            )
        
        # Non-numeric answer - check for substring match
        for output in tool_outputs:
            if answer_stripped.lower() in str(output).lower():
                return VerifyResult(
                    status=VerifyStatus.VALID,
                    message="Answer found in tool output",
                    confidence=0.8
                )
        
        return VerifyResult(
            status=VerifyStatus.UNCERTAIN,
            message="Could not verify answer against tool outputs",
            confidence=0.5
        )
    
    def verify_numeric(self, answer: str, min_val: int = 0, max_val: int = None) -> VerifyResult:
        """
        Verify a numeric answer is within expected range.
        
        Args:
            answer: The proposed answer
            min_val: Minimum acceptable value
            max_val: Maximum acceptable value (None for no limit)
            
        Returns:
            VerifyResult for range check
        """
        try:
            # Extract first number from answer
            numbers = re.findall(r'-?\d+', answer.strip())
            if not numbers:
                return VerifyResult(
                    status=VerifyStatus.INVALID,
                    message="No numeric value found in answer",
                    confidence=1.0,
                    suggestions=["Provide a numeric answer"]
                )
            
            value = int(numbers[0])
            
            if value < min_val:
                return VerifyResult(
                    status=VerifyStatus.INVALID,
                    message=f"Value {value} is below minimum {min_val}",
                    confidence=0.9,
                    suggestions=[f"Value should be >= {min_val}"]
                )
            
            if max_val is not None and value > max_val:
                return VerifyResult(
                    status=VerifyStatus.INVALID,
                    message=f"Value {value} exceeds maximum {max_val}",
                    confidence=0.9,
                    suggestions=[f"Value should be <= {max_val}"]
                )
            
            return VerifyResult(
                status=VerifyStatus.VALID,
                message=f"Numeric value {value} is within acceptable range",
                confidence=0.95
            )
            
        except ValueError:
            return VerifyResult(
                status=VerifyStatus.INVALID,
                message="Could not parse numeric value",
                confidence=1.0,
                suggestions=["Ensure answer contains a valid number"]
            )
    
    def verify_path(self, path: str) -> VerifyResult:
        """
        Verify a path answer looks valid.
        
        Args:
            path: The proposed path
            
        Returns:
            VerifyResult for path check
        """
        path_stripped = path.strip()
        
        # Check for common path patterns
        if not path_stripped:
            return VerifyResult(
                status=VerifyStatus.INVALID,
                message="Empty path",
                confidence=1.0
            )
        
        # Windows or Unix path pattern
        is_valid_path = (
            path_stripped.startswith("/") or  # Unix
            path_stripped.startswith("C:") or  # Windows
            path_stripped.startswith("~") or  # Home
            path_stripped.startswith("./") or  # Relative
            path_stripped.startswith("..\\")  # Windows relative
        )
        
        if is_valid_path:
            return VerifyResult(
                status=VerifyStatus.VALID,
                message="Path format is valid",
                confidence=0.8
            )
        
        return VerifyResult(
            status=VerifyStatus.UNCERTAIN,
            message="Path format may be invalid",
            confidence=0.5,
            suggestions=["Verify the path format"]
        )
    
    # === Private helper methods ===
    
    def _expects_numeric(self, task_lower: str) -> bool:
        """Check if task expects a numeric answer"""
        return any(re.search(p, task_lower) for p in self.numeric_patterns)
    
    def _expects_path(self, task_lower: str) -> bool:
        """Check if task expects a path answer"""
        return any(re.search(p, task_lower) for p in self.path_patterns)
    
    def _expects_boolean(self, task_lower: str) -> bool:
        """Check if task expects a boolean answer"""
        return any(re.search(p, task_lower) for p in self.boolean_patterns)
    
    def _verify_numeric_format(self, answer: str, task_lower: str) -> VerifyResult:
        """Verify answer has numeric format"""
        # Extract numbers
        numbers = re.findall(r'-?\d+\.?\d*', answer)
        
        if not numbers:
            return VerifyResult(
                status=VerifyStatus.INVALID,
                message="Task expects a number but answer contains none",
                confidence=0.9,
                suggestions=["Provide a numeric answer"]
            )
        
        # Check if answer is just the number (clean format)
        if answer.strip() == numbers[0]:
            return VerifyResult(
                status=VerifyStatus.VALID,
                message="Clean numeric answer",
                confidence=0.95
            )
        
        # Answer contains number but with extra text
        return VerifyResult(
            status=VerifyStatus.UNCERTAIN,
            message=f"Found number {numbers[0]} but answer has extra text",
            confidence=0.7,
            suggestions=["Consider providing just the number"]
        )
    
    def _verify_path_format(self, answer: str) -> VerifyResult:
        """Verify answer has path format"""
        return self.verify_path(answer)
    
    def _verify_boolean_format(self, answer: str) -> VerifyResult:
        """Verify answer has boolean format"""
        answer_lower = answer.lower().strip()
        
        boolean_yes = ["yes", "true", "Yes", "有", "存在", "1"]
        boolean_no = ["no", "false", "No", "没有", "不存在", "0"]
        
        if answer_lower in boolean_yes + boolean_no:
            return VerifyResult(
                status=VerifyStatus.VALID,
                message="Boolean answer format",
                confidence=0.95
            )
        
        return VerifyResult(
            status=VerifyStatus.UNCERTAIN,
            message="Expected yes/no answer",
            confidence=0.6,
            suggestions=["Provide a clear yes/no answer"]
        )
    
    def _aggregate_results(self, results: List[VerifyResult]) -> VerifyResult:
        """Aggregate multiple verification results"""
        if not results:
            return VerifyResult(
                status=VerifyStatus.UNCERTAIN,
                message="No verification performed",
                confidence=0.5
            )
        
        # Check for any invalid results
        invalid_results = [r for r in results if r.status == VerifyStatus.INVALID]
        if invalid_results:
            messages = [r.message for r in invalid_results]
            suggestions = []
            for r in invalid_results:
                suggestions.extend(r.suggestions)
            
            return VerifyResult(
                status=VerifyStatus.INVALID,
                message="; ".join(messages),
                confidence=max(r.confidence for r in invalid_results),
                suggestions=suggestions
            )
        
        # All valid or uncertain
        valid_results = [r for r in results if r.status == VerifyStatus.VALID]
        if valid_results:
            avg_confidence = sum(r.confidence for r in valid_results) / len(valid_results)
            return VerifyResult(
                status=VerifyStatus.VALID,
                message="All verifications passed",
                confidence=avg_confidence
            )
        
        # All uncertain
        return VerifyResult(
            status=VerifyStatus.UNCERTAIN,
            message="Could not definitively verify answer",
            confidence=0.5
        )


# === Utility functions for quick verification ===

def verify_answer(
    answer: str,
    task: str,
    tool_outputs: List[str] = None
) -> Tuple[bool, str]:
    """
    Quick verification utility function.
    
    Args:
        answer: The proposed answer
        task: The original task
        tool_outputs: Optional tool outputs
        
    Returns:
        Tuple of (is_valid, message)
    """
    verifier = AnswerVerifier()
    result = verifier.verify(answer, task, tool_outputs)
    return (result.is_valid, result.message)


def extract_numeric_answer(text: str) -> Optional[int]:
    """
    Extract a numeric answer from text.
    
    Args:
        text: Text containing a number
        
    Returns:
        Extracted integer or None
    """
    numbers = re.findall(r'-?\d+', text.strip())
    if numbers:
        try:
            return int(numbers[0])
        except ValueError:
            return None
    return None

