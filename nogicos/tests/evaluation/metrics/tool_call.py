# -*- coding: utf-8 -*-
"""
Tool Call Correctness Metric for NogicOS Agent Evaluation

Evaluates whether the agent's tool call parameters are correct and valid.
"""

from typing import Any, Dict, List, Optional
import json

try:
    from deepeval.metrics import BaseMetric
    from deepeval.test_case import LLMTestCase
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False
    class BaseMetric:
        pass
    class LLMTestCase:
        pass


class ToolCallCorrectnessMetric(BaseMetric if DEEPEVAL_AVAILABLE else object):
    """
    Evaluates the correctness of agent's tool call parameters.
    
    Checks:
    - Tool name is valid (in allowed tools list)
    - Required parameters are present
    - Parameter types are correct
    - Parameter values are reasonable
    
    Attributes:
        threshold: Minimum score to pass (0.0 to 1.0)
        allowed_tools: List of valid tool names
        strict_params: If True, extra parameters count as errors
        include_reason: Include explanation for score
    
    Example:
        metric = ToolCallCorrectnessMetric(
            threshold=0.8,
            allowed_tools=["read_file", "write_file", "shell_execute"],
        )
        metric.measure(test_case)
    """
    
    # Default tool schemas for NogicOS
    DEFAULT_TOOL_SCHEMAS = {
        "read_file": {
            "required": ["path"],
            "optional": ["encoding"],
            "param_types": {"path": str, "encoding": str},
        },
        "write_file": {
            "required": ["path", "content"],
            "optional": ["encoding", "append"],
            "param_types": {"path": str, "content": str, "encoding": str, "append": bool},
        },
        "list_directory": {
            "required": ["path"],
            "optional": ["recursive", "pattern"],
            "param_types": {"path": str, "recursive": bool, "pattern": str},
        },
        "shell_execute": {
            "required": ["command"],
            "optional": ["working_dir", "timeout"],
            "param_types": {"command": str, "working_dir": str, "timeout": (int, float)},
        },
        "glob_search": {
            "required": ["pattern"],
            "optional": ["path", "recursive"],
            "param_types": {"pattern": str, "path": str, "recursive": bool},
        },
        "grep_search": {
            "required": ["pattern"],
            "optional": ["path", "case_sensitive", "context_lines"],
            "param_types": {"pattern": str, "path": str, "case_sensitive": bool, "context_lines": int},
        },
        "browser_navigate": {
            "required": ["url"],
            "optional": ["wait_until"],
            "param_types": {"url": str, "wait_until": str},
        },
        "browser_click": {
            "required": ["selector"],
            "optional": ["timeout"],
            "param_types": {"selector": str, "timeout": (int, float)},
        },
        "browser_type": {
            "required": ["selector", "text"],
            "optional": ["delay"],
            "param_types": {"selector": str, "text": str, "delay": (int, float)},
        },
        "browser_get_content": {
            "required": [],
            "optional": ["selector"],
            "param_types": {"selector": str},
        },
    }
    
    def __init__(
        self,
        threshold: float = 0.8,
        allowed_tools: Optional[List[str]] = None,
        tool_schemas: Optional[Dict[str, Dict]] = None,
        strict_params: bool = False,
        include_reason: bool = True,
    ):
        if DEEPEVAL_AVAILABLE:
            super().__init__()
        
        self.threshold = threshold
        self.allowed_tools = allowed_tools or list(self.DEFAULT_TOOL_SCHEMAS.keys())
        self.tool_schemas = tool_schemas or self.DEFAULT_TOOL_SCHEMAS
        self.strict_params = strict_params
        self.include_reason = include_reason
        
        # Results
        self.score: float = 0.0
        self.reason: str = ""
        self._success: bool = False
        self._errors: List[str] = []
    
    @property
    def name(self) -> str:
        return "ToolCallCorrectnessMetric"
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure tool call correctness for a test case.
        
        Args:
            test_case: LLMTestCase with tools_called attribute
        
        Returns:
            Score between 0.0 and 1.0
        """
        self._errors = []
        
        # Get tool calls from test case
        tools_called = getattr(test_case, "tools_called", []) or []
        
        if not tools_called:
            self.score = 1.0  # No tools called, nothing to validate
            self.reason = "No tool calls to validate"
            self._success = True
            return self.score
        
        total_checks = 0
        passed_checks = 0
        
        for tool in tools_called:
            tool_name = tool.name if hasattr(tool, "name") else str(tool)
            tool_input = tool.input if hasattr(tool, "input") else {}
            
            # Parse input if it's a string
            if isinstance(tool_input, str):
                try:
                    tool_input = json.loads(tool_input)
                except:
                    tool_input = {}
            
            # Check 1: Valid tool name
            total_checks += 1
            if tool_name.lower() in [t.lower() for t in self.allowed_tools]:
                passed_checks += 1
            else:
                self._errors.append(f"Unknown tool: {tool_name}")
            
            # Get schema for this tool
            schema = self.tool_schemas.get(tool_name.lower(), {})
            if not schema:
                # No schema defined, skip parameter validation
                continue
            
            required_params = schema.get("required", [])
            optional_params = schema.get("optional", [])
            param_types = schema.get("param_types", {})
            
            # Check 2: Required parameters present
            for param in required_params:
                total_checks += 1
                if param in tool_input:
                    passed_checks += 1
                else:
                    self._errors.append(f"{tool_name}: Missing required param '{param}'")
            
            # Check 3: Parameter types
            for param, value in tool_input.items():
                if param in param_types:
                    total_checks += 1
                    expected_type = param_types[param]
                    
                    if isinstance(expected_type, tuple):
                        if isinstance(value, expected_type):
                            passed_checks += 1
                        else:
                            self._errors.append(
                                f"{tool_name}.{param}: Expected {expected_type}, got {type(value)}"
                            )
                    elif isinstance(value, expected_type):
                        passed_checks += 1
                    else:
                        self._errors.append(
                            f"{tool_name}.{param}: Expected {expected_type.__name__}, got {type(value).__name__}"
                        )
            
            # Check 4: Extra parameters (if strict)
            if self.strict_params:
                all_params = set(required_params + optional_params)
                extra_params = set(tool_input.keys()) - all_params
                if extra_params:
                    total_checks += 1
                    self._errors.append(f"{tool_name}: Extra params {extra_params}")
        
        # Calculate score
        self.score = passed_checks / total_checks if total_checks > 0 else 1.0
        self._success = self.score >= self.threshold
        
        # Build reason
        if self._errors:
            self.reason = f"Passed {passed_checks}/{total_checks} checks. Errors: {'; '.join(self._errors[:3])}"
            if len(self._errors) > 3:
                self.reason += f" (+{len(self._errors) - 3} more)"
        else:
            self.reason = f"All {total_checks} checks passed"
        
        return self.score
    
    def is_successful(self) -> bool:
        """Check if the metric passed"""
        return self._success
    
    def get_errors(self) -> List[str]:
        """Get list of validation errors"""
        return self._errors.copy()
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async version of measure (for compatibility)"""
        return self.measure(test_case)



