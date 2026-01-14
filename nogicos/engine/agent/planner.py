# -*- coding: utf-8 -*-
"""
Task Planner - Plan-Execute Architecture for Complex Tasks

Based on LangGraph's plan-and-execute pattern:
- Decompose complex tasks into steps
- Execute steps sequentially
- Replan when errors occur
- Dynamic tool discovery from registry

Architecture:
    User Task → Planner → [Step 1 → Step 2 → ...] → Response
                   ↑              ↓ (on error)
                   └── Replanner ←┘
"""

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

# Anthropic client
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

from ..observability import get_logger
logger = get_logger("planner")

# Type checking imports
if TYPE_CHECKING:
    from ..tools.base import ToolRegistry, ToolDefinition


class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"      # Single tool call (list, read, etc.)
    MODERATE = "moderate"  # 2-3 tool calls
    COMPLEX = "complex"    # 4+ tool calls or multi-stage


@dataclass
class PlanStep:
    """A single step in a plan"""
    description: str
    suggested_tool: Optional[str] = None
    tool_args_hint: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    details: Optional[str] = None  # Additional details, file paths, etc.
    editable: bool = True  # Whether user can edit this step


@dataclass
class EditablePlanStep:
    """A detailed step for Plan mode with full metadata"""
    step_number: int
    description: str
    tool: Optional[str] = None
    details: Optional[str] = None
    file_paths: List[str] = field(default_factory=list)
    code_references: List[str] = field(default_factory=list)
    editable: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "description": self.description,
            "tool": self.tool,
            "details": self.details,
            "file_paths": self.file_paths,
            "code_references": self.code_references,
            "editable": self.editable,
        }


@dataclass
class EditablePlan:
    """
    Detailed, editable plan for Plan mode (Cursor-style).
    
    Includes:
    - Summary of what will be done
    - Clarifying questions for user
    - Detailed steps with tool suggestions
    - Risks and considerations
    - Estimated time
    """
    summary: str
    steps: List[EditablePlanStep] = field(default_factory=list)
    clarifying_questions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    estimated_time: str = ""
    complexity: TaskComplexity = TaskComplexity.MODERATE
    confirmed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "steps": [s.to_dict() for s in self.steps],
            "clarifying_questions": self.clarifying_questions,
            "risks": self.risks,
            "estimated_time": self.estimated_time,
            "complexity": self.complexity.value,
            "confirmed": self.confirmed,
        }
    
    def to_markdown(self) -> str:
        """Convert plan to editable Markdown format"""
        lines = []
        
        # Header
        lines.append("# Execution Plan")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append(self.summary)
        lines.append("")
        
        # Clarifying questions (if any)
        if self.clarifying_questions:
            lines.append("## Clarifying Questions")
            lines.append("")
            lines.append("Please answer these questions before I proceed:")
            lines.append("")
            for i, q in enumerate(self.clarifying_questions, 1):
                lines.append(f"{i}. {q}")
            lines.append("")
        
        # Steps
        lines.append("## Steps")
        lines.append("")
        for step in self.steps:
            lines.append(f"### Step {step.step_number}: {step.description}")
            if step.tool:
                lines.append(f"- **Tool:** `{step.tool}`")
            if step.details:
                lines.append(f"- **Details:** {step.details}")
            if step.file_paths:
                lines.append(f"- **Files:** {', '.join(f'`{p}`' for p in step.file_paths)}")
            if step.code_references:
                lines.append(f"- **Code refs:** {', '.join(step.code_references)}")
            lines.append("")
        
        # Risks
        if self.risks:
            lines.append("## Risks & Considerations")
            lines.append("")
            for risk in self.risks:
                lines.append(f"- {risk}")
            lines.append("")
        
        # Metadata
        lines.append("---")
        lines.append(f"*Complexity: {self.complexity.value} | Estimated time: {self.estimated_time}*")
        
        return "\n".join(lines)
    
    def to_simple_plan(self) -> "Plan":
        """Convert to simple Plan for execution"""
        return Plan(
            steps=[s.description for s in self.steps],
            complexity=self.complexity,
            estimated_tools=len(self.steps),
            detailed_steps=[
                PlanStep(
                    description=s.description,
                    suggested_tool=s.tool,
                    details=s.details,
                )
                for s in self.steps
            ],
        )


@dataclass
class Plan:
    """Execution plan with steps"""
    steps: List[str]
    complexity: TaskComplexity = TaskComplexity.MODERATE
    estimated_tools: int = 0
    detailed_steps: List[PlanStep] = field(default_factory=list)
    
    def __len__(self):
        return len(self.steps)
    
    def __iter__(self):
        return iter(self.steps)
    
    def pop_first(self) -> Optional[str]:
        """Get and remove first step"""
        if self.steps:
            return self.steps.pop(0)
        return None
    
    @property
    def remaining(self) -> int:
        return len(self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "steps": self.steps,
            "complexity": self.complexity.value,
            "estimated_tools": self.estimated_tools,
        }


@dataclass
class PlanExecuteState:
    """State for plan-execute loop"""
    input: str                                    # Original task
    plan: Plan = field(default_factory=lambda: Plan([]))
    past_steps: List[Tuple[str, str]] = field(default_factory=list)  # (step, result)
    response: Optional[str] = None
    error: Optional[str] = None


# Dynamic planning prompt template
PLANNER_PROMPT_TEMPLATE = """You are a task planner for an AI agent. Your job is to break down complex tasks into simple, executable steps.

## Available Tools
{tools_description}

## Task
{task}

## Instructions
1. Analyze the task carefully
2. Break it into 2-7 simple, executable steps
3. Each step should map to ONE tool call
4. Steps should be in order of execution
5. Do not add unnecessary steps
6. The final step should complete the objective
7. For each step, suggest which tool to use

## Output Format
Return a JSON object:
```json
{{
  "complexity": "simple|moderate|complex",
  "steps": [
    {{"description": "Step 1 description", "tool": "suggested_tool_name"}},
    {{"description": "Step 2 description", "tool": "suggested_tool_name"}}
  ]
}}
```

If the task is simple (single action), return:
```json
{{
  "complexity": "simple",
  "steps": [{{"description": "Execute the action", "tool": "tool_name"}}]
}}
```
"""

# Plan mode prompt for detailed, editable plans (Cursor-style)
PLAN_MODE_PROMPT = """You are a task planner for an AI agent in PLAN mode. Your job is to create a detailed, actionable plan that the user can review and edit before execution.

## Available Tools
{tools_description}

## Task
{task}

## Context (if available)
{context}

## Instructions
1. Analyze the task thoroughly
2. Explore what information/files might be needed
3. Identify any ambiguities that need clarification
4. Generate a detailed plan with 2-10 steps
5. For each step, specify:
   - Clear description
   - Which tool to use
   - Any relevant file paths or code references
   - Additional details if needed
6. Identify potential risks
7. Estimate completion time

## Output Format
Return a JSON object:
```json
{{
  "summary": "Brief summary of what will be done",
  "clarifying_questions": ["Question 1?", "Question 2?"],
  "steps": [
    {{
      "step": 1,
      "description": "What this step does",
      "tool": "suggested_tool_name",
      "details": "Additional context",
      "file_paths": ["path/to/file1", "path/to/file2"],
      "code_references": ["function_name", "class_name"]
    }}
  ],
  "risks": ["Potential risk 1", "Risk 2"],
  "estimated_time": "5-10 minutes",
  "complexity": "simple|moderate|complex"
}}
```

Be thorough but practical. Ask clarifying questions if the task is ambiguous.
"""

# Smart replanning prompt with error analysis
REPLANNER_PROMPT = """You are replanning a task after an error occurred. Analyze the error and choose the best recovery strategy.

## Original Task
{task}

## Available Tools
{tools_description}

## Original Plan
{plan}

## Completed Steps
{past_steps}

## Error on Current Step
Step: {current_step}
Error: {error}

## Error Analysis Guidelines
1. **Permission Error**: Suggest alternative path or ask user for permission
2. **File Not Found**: Use list_directory first to find the file
3. **Network Error**: Retry with exponential backoff or use cached data
4. **Invalid Input**: Correct the input and retry
5. **Tool Not Available**: Find alternative tool or approach
6. **Timeout**: Simplify the step or break it down further

## Instructions
1. Analyze what went wrong (classify the error type)
2. Decide if the task can continue with a different approach
3. If continuing: provide updated steps with specific tool suggestions
4. If complete: summarize results
5. If failed: explain why clearly

## Output Format
```json
{{
  "action": "continue|respond|fail",
  "error_type": "permission|not_found|network|invalid_input|timeout|other",
  "analysis": "Brief analysis of what went wrong",
  "steps": [{{"description": "Step", "tool": "tool_name"}}],
  "response": "Final answer or error message",
  "reason": "Why this action"
}}
```
"""


class TaskPlanner:
    """
    Plan-Execute agent for complex tasks.
    
    Workflow:
    1. Analyze task complexity
    2. If simple: pass directly to ReAct agent
    3. If complex: generate plan, execute step by step
    4. On error: replan with intelligent error analysis
    
    Key Features:
    - Dynamic tool discovery from ToolRegistry
    - Smart error recovery with error type classification
    - Tool suggestion for each step
    """
    
    # Patterns for simple tasks (don't need planning)
    SIMPLE_PATTERNS = [
        r"^(list|show|看看|view).*File",  # Just list files
        r"^(read|Read|Open).*File",         # Just read a file
        r"^(go to|Open|visit).*网",        # Just navigate
        r"^(what|what's|what is)",         # Just questions
        r"^(help|help|how)",             # Help requests
    ]
    
    def __init__(
        self, 
        model: str = "claude-opus-4-5-20251101",
        registry: Optional["ToolRegistry"] = None
    ):
        """
        Initialize task planner.
        
        Args:
            model: Claude model for planning
            registry: ToolRegistry for dynamic tool discovery
        """
        self.model = model
        self._client = None
        self._registry = registry
        self._tools_cache: Optional[str] = None
    
    def set_registry(self, registry: "ToolRegistry") -> None:
        """Set or update the tool registry"""
        self._registry = registry
        self._tools_cache = None  # Clear cache
    
    def _get_client(self):
        """Lazy-load Anthropic client"""
        if self._client is None and ANTHROPIC_AVAILABLE:
            # Try to get API key from api_keys.py first, then environment variable
            api_key = None
            try:
                import api_keys
                api_key = api_keys.ANTHROPIC_API_KEY
            except (ImportError, AttributeError):
                api_key = os.environ.get("ANTHROPIC_API_KEY")
            
            if api_key:
                self._client = anthropic.Anthropic(api_key=api_key)
        return self._client
    
    def _build_tools_description(self, category_filter: Optional[str] = None) -> str:
        """
        Build tools description from registry.
        
        Args:
            category_filter: Optional category to filter tools (browser, local, etc.)
            
        Returns:
            Formatted string describing available tools
        """
        if self._registry is None:
            # Fallback to hardcoded list if no registry
            return """- list_directory: List files in a folder
- move_file: Move/rename a file  
- create_directory: Create a folder
- delete_file: Delete a file
- read_file: Read file content
- write_file: Write to a file
- browser_navigate: Go to a URL
- browser_click: Click on page elements
- browser_screenshot: Take a screenshot"""
        
        # Get tools from registry
        tools = self._registry.get_all()
        
        # Filter by category if specified
        if category_filter:
            from ..tools.base import ToolCategory
            try:
                cat = ToolCategory(category_filter)
                tools = [t for t in tools if t.category == cat]
            except ValueError:
                pass  # Invalid category, use all tools
        
        # Build description with examples
        lines = []
        for tool in tools:
            # Extract parameter info
            params = tool.input_schema.get("properties", {})
            param_str = ", ".join(params.keys()) if params else "none"
            
            lines.append(f"- **{tool.name}**: {tool.description}")
            lines.append(f"  Parameters: {param_str}")
        
        return "\n".join(lines)
    
    def is_simple_task(self, task: str) -> bool:
        """
        Check if task is simple enough to skip planning.
        
        Simple tasks:
        - Single action requests
        - Information queries
        - Direct commands
        """
        task_lower = task.lower().strip()
        
        # Check against simple patterns FIRST
        for pattern in self.SIMPLE_PATTERNS:
            if re.search(pattern, task_lower):
                return True
        
        # Tasks with sequence indicators are COMPLEX (check before length)
        sequence_words = ["和", "并且", "然After", "接着", "最After", "先", "再", "，然After", "之After"]
        if any(word in task for word in sequence_words):
            return False
        
        # Tasks with multiple action verbs are COMPLEX
        action_words = ["整理", "Move", "Create", "Delete", "Down载", "Save", "Analyze", "总结", "生成", "Backup", "Copy", "重命名"]
        action_count = sum(1 for word in action_words if word in task)
        if action_count >= 2:
            return False
        
        # Short tasks are usually simple (check after complexity indicators)
        if len(task) < 20:
            return True
        
        # Medium length with single action is still simple
        if len(task) < 50 and action_count <= 1:
            return True
        
        # Default: longer tasks are complex
        return len(task) < 30
    
    async def plan(
        self, 
        task: str, 
        category_filter: Optional[str] = None
    ) -> Plan:
        """
        Generate execution plan for a task.
        
        Args:
            task: User's task description
            category_filter: Optional tool category to focus on
            
        Returns:
            Plan with steps and tool suggestions
        """
        # Check for simple task
        if self.is_simple_task(task):
            logger.debug(f"Simple task detected, skipping planning: {task[:50]}")
            return Plan(
                steps=[task],  # Single step = original task
                complexity=TaskComplexity.SIMPLE,
                estimated_tools=1,
            )
        
        client = self._get_client()
        if not client:
            logger.warning("No Anthropic client, falling back to simple execution")
            return Plan(steps=[task], complexity=TaskComplexity.SIMPLE)
        
        try:
            # Build dynamic tools description from registry
            tools_description = self._build_tools_description(category_filter)
            
            # Call Claude for planning with dynamic prompt
            prompt = PLANNER_PROMPT_TEMPLATE.format(
                tools_description=tools_description,
                task=task
            )
            
            # Call with timeout protection (30 seconds)
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                timeout=30.0,  # 30 second timeout for planning
            )
            
            # Parse response
            response_text = response.content[0].text
            plan_data = self._parse_json_response(response_text)
            
            if not plan_data or "steps" not in plan_data:
                logger.warning("Failed to parse plan, using single step")
                return Plan(steps=[task], complexity=TaskComplexity.SIMPLE)
            
            complexity = TaskComplexity(plan_data.get("complexity", "moderate"))
            
            # Parse steps - now with tool suggestions
            steps_data = plan_data["steps"]
            step_descriptions = []
            detailed_steps = []
            
            for step in steps_data:
                if isinstance(step, dict):
                    desc = step.get("description", str(step))
                    tool = step.get("tool")
                    step_descriptions.append(desc)
                    detailed_steps.append(PlanStep(
                        description=desc,
                        suggested_tool=tool
                    ))
                else:
                    step_descriptions.append(str(step))
                    detailed_steps.append(PlanStep(description=str(step)))
            
            logger.info(f"Generated plan with {len(step_descriptions)} steps ({complexity.value})")
            
            return Plan(
                steps=step_descriptions,
                complexity=complexity,
                estimated_tools=len(step_descriptions),
                detailed_steps=detailed_steps,
            )
            
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return Plan(steps=[task], complexity=TaskComplexity.SIMPLE)
    
    async def generate_editable_plan(
        self,
        task: str,
        context: Optional[str] = None,
        category_filter: Optional[str] = None,
    ) -> EditablePlan:
        """
        Generate a detailed, editable plan for Plan mode.
        
        This is used in Plan mode where the user can review, edit,
        and confirm the plan before execution.
        
        Args:
            task: User's task description
            context: Optional context about codebase/files
            category_filter: Optional tool category to focus on
            
        Returns:
            EditablePlan with detailed steps, questions, risks
        """
        client = self._get_client()
        if not client:
            logger.warning("No Anthropic client, creating simple plan")
            return EditablePlan(
                summary=task,
                steps=[EditablePlanStep(
                    step_number=1,
                    description=task,
                )],
                complexity=TaskComplexity.SIMPLE,
                estimated_time="Unknown",
            )
        
        try:
            # Build tools description
            tools_description = self._build_tools_description(category_filter)
            
            # Build prompt
            prompt = PLAN_MODE_PROMPT.format(
                tools_description=tools_description,
                task=task,
                context=context or "No additional context provided.",
            )
            
            # Call Claude for detailed planning
            response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
                timeout=60.0,  # Longer timeout for detailed planning
            )
            
            # Parse response
            response_text = response.content[0].text
            plan_data = self._parse_json_response(response_text)
            
            if not plan_data:
                logger.warning("Failed to parse editable plan")
                return EditablePlan(
                    summary=task,
                    steps=[EditablePlanStep(step_number=1, description=task)],
                )
            
            # Parse steps
            steps = []
            for i, step_data in enumerate(plan_data.get("steps", []), 1):
                if isinstance(step_data, dict):
                    steps.append(EditablePlanStep(
                        step_number=step_data.get("step", i),
                        description=step_data.get("description", ""),
                        tool=step_data.get("tool"),
                        details=step_data.get("details"),
                        file_paths=step_data.get("file_paths", []),
                        code_references=step_data.get("code_references", []),
                    ))
                else:
                    steps.append(EditablePlanStep(
                        step_number=i,
                        description=str(step_data),
                    ))
            
            # Parse complexity
            complexity_str = plan_data.get("complexity", "moderate")
            try:
                complexity = TaskComplexity(complexity_str)
            except ValueError:
                complexity = TaskComplexity.MODERATE
            
            editable_plan = EditablePlan(
                summary=plan_data.get("summary", task),
                steps=steps,
                clarifying_questions=plan_data.get("clarifying_questions", []),
                risks=plan_data.get("risks", []),
                estimated_time=plan_data.get("estimated_time", "Unknown"),
                complexity=complexity,
            )
            
            logger.info(f"Generated editable plan: {len(steps)} steps, {len(editable_plan.clarifying_questions)} questions")
            return editable_plan
            
        except Exception as e:
            logger.error(f"Editable plan generation failed: {e}")
            return EditablePlan(
                summary=task,
                steps=[EditablePlanStep(step_number=1, description=task)],
                estimated_time="Unknown",
            )
    
    async def replan(
        self,
        state: PlanExecuteState,
        current_step: str,
        error: str,
        category_filter: Optional[str] = None,
    ) -> Tuple[str, Union[Plan, str], Optional[str]]:
        """
        Replan after an error with intelligent error analysis.
        
        Args:
            state: Current execution state
            current_step: Step that failed
            error: Error message
            category_filter: Optional tool category filter
            
        Returns:
            Tuple of (action, result, error_type)
            - ("continue", Plan, error_type): Continue with updated plan
            - ("respond", str, error_type): Return response to user
            - ("fail", str, error_type): Abort with error message
        """
        client = self._get_client()
        if not client:
            return ("fail", f"Step failed: {error}", "other")
        
        try:
            # Build dynamic tools description
            tools_description = self._build_tools_description(category_filter)
            
            # Format past steps
            past_steps_str = "\n".join(
                f"- {step}: {result}" for step, result in state.past_steps
            ) or "None"
            
            # Format current plan
            plan_str = "\n".join(f"- {s}" for s in state.plan.steps)
            
            prompt = REPLANNER_PROMPT.format(
                task=state.input,
                tools_description=tools_description,
                plan=plan_str,
                past_steps=past_steps_str,
                current_step=current_step,
                error=error,
            )
            
            # Call with timeout protection (30 seconds)
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                timeout=30.0,  # 30 second timeout for replanning
            )
            
            response_text = response.content[0].text
            replan_data = self._parse_json_response(response_text)
            
            if not replan_data:
                return ("fail", f"Replanning failed: {error}", "other")
            
            action = replan_data.get("action", "fail")
            error_type = replan_data.get("error_type", "other")
            analysis = replan_data.get("analysis", "")
            
            if analysis:
                logger.info(f"Error analysis: {analysis}")
            
            if action == "continue":
                steps_data = replan_data.get("steps", [])
                if steps_data:
                    # Parse steps with tool suggestions
                    step_descriptions = []
                    detailed_steps = []
                    
                    for step in steps_data:
                        if isinstance(step, dict):
                            desc = step.get("description", str(step))
                            tool = step.get("tool")
                            step_descriptions.append(desc)
                            detailed_steps.append(PlanStep(
                                description=desc,
                                suggested_tool=tool
                            ))
                        else:
                            step_descriptions.append(str(step))
                            detailed_steps.append(PlanStep(description=str(step)))
                    
                    logger.info(f"Replanned with {len(step_descriptions)} steps (error_type={error_type})")
                    new_plan = Plan(
                        steps=step_descriptions,
                        detailed_steps=detailed_steps
                    )
                    return ("continue", new_plan, error_type)
                return ("fail", "No steps to continue", error_type)
            
            elif action == "respond":
                resp = replan_data.get("response", "Task completed with partial results.")
                return ("respond", resp, error_type)
            
            else:  # fail
                reason = replan_data.get("response", error)
                return ("fail", reason, error_type)
                
        except Exception as e:
            logger.error(f"Replanning error: {e}")
            return ("fail", f"Replanning failed: {e}", "other")
    
    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response"""
        try:
            # Try to extract JSON block
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                text = text[start:end].strip()
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                text = text[start:end].strip()
            
            return json.loads(text)
            
        except json.JSONDecodeError:
            # Try to find JSON object in text
            match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return None


# Convenience functions
async def create_plan(task: str, registry: Optional["ToolRegistry"] = None) -> Plan:
    """Quick plan creation with optional registry"""
    planner = TaskPlanner(registry=registry)
    return await planner.plan(task)


def is_simple_task(task: str) -> bool:
    """Quick complexity check"""
    planner = TaskPlanner()
    return planner.is_simple_task(task)


# Export all for easy importing
__all__ = [
    "TaskPlanner",
    "Plan",
    "PlanStep",
    "EditablePlan",
    "EditablePlanStep",
    "PlanExecuteState",
    "TaskComplexity",
    "create_plan",
    "is_simple_task",
]

