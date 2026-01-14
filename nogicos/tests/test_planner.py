# -*- coding: utf-8 -*-
"""
Tests for Task Planner and Plan-Execute Architecture

Tests cover:
- Task complexity detection
- Plan generation
- Replanning on errors
- Integration with ReAct agent
"""

import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.agent.planner import (
    TaskPlanner, Plan, PlanExecuteState, TaskComplexity,
    is_simple_task, create_plan
)


class TestTaskComplexity:
    """Tests for task complexity detection"""
    
    def test_simple_list_task(self):
        """List tasks should be simple"""
        planner = TaskPlanner()
        
        assert planner.is_simple_task("list files") == True
        assert planner.is_simple_task("看看桌面有什么File") == True
        assert planner.is_simple_task("show files in folder") == True
    
    def test_simple_read_task(self):
        """Read tasks should be simple"""
        planner = TaskPlanner()
        
        assert planner.is_simple_task("read file.txt") == True
        assert planner.is_simple_task("ReadFileInner容") == True
        assert planner.is_simple_task("Openreadme") == True
    
    def test_simple_question(self):
        """Questions should be simple"""
        planner = TaskPlanner()
        
        assert planner.is_simple_task("what is Python?") == True
        assert planner.is_simple_task("what is机器学习") == True
        assert planner.is_simple_task("help me") == True
    
    def test_short_task_is_simple(self):
        """Short tasks should be simple"""
        planner = TaskPlanner()
        
        assert planner.is_simple_task("hi") == True
        assert planner.is_simple_task("test") == True
    
    def test_complex_multi_step(self):
        """Multi-step tasks should be complex"""
        planner = TaskPlanner()
        
        # Contains "thenAfter" indicating sequence
        assert planner.is_simple_task("先整理桌面，然After生成Report") == False
        
        # Contains "and" indicating multiple actions
        assert planner.is_simple_task("整理File和CreateBackup") == False
        
        # Contains multiple action words
        assert planner.is_simple_task("整理桌面File并DeleteTemporaryFile") == False
    
    def test_complex_organization_task(self):
        """Organization tasks are usually complex"""
        planner = TaskPlanner()
        
        # Long task description
        task = "帮我整理桌面Up的所有File，按Class型分Class到不同File夹，并生成一份整理Report"
        assert planner.is_simple_task(task) == False


class TestPlan:
    """Tests for Plan model"""
    
    def test_plan_creation(self):
        """Test creating a plan"""
        plan = Plan(
            steps=["Step 1", "Step 2", "Step 3"],
            complexity=TaskComplexity.MODERATE,
        )
        
        assert len(plan) == 3
        assert plan.remaining == 3
        assert plan.complexity == TaskComplexity.MODERATE
    
    def test_plan_pop_first(self):
        """Test popping steps from plan"""
        plan = Plan(steps=["A", "B", "C"])
        
        assert plan.pop_first() == "A"
        assert plan.remaining == 2
        
        assert plan.pop_first() == "B"
        assert plan.remaining == 1
        
        assert plan.pop_first() == "C"
        assert plan.remaining == 0
        
        assert plan.pop_first() is None
    
    def test_plan_iteration(self):
        """Test iterating over plan steps"""
        plan = Plan(steps=["X", "Y", "Z"])
        
        steps = list(plan)
        assert steps == ["X", "Y", "Z"]


class TestPlanExecuteState:
    """Tests for PlanExecuteState"""
    
    def test_state_creation(self):
        """Test creating execution state"""
        state = PlanExecuteState(
            input="Organize desktop",
            plan=Plan(steps=["List files", "Create folders", "Move files"]),
        )
        
        assert state.input == "Organize desktop"
        assert len(state.plan) == 3
        assert state.past_steps == []
        assert state.response is None
    
    def test_state_with_past_steps(self):
        """Test state with completed steps"""
        state = PlanExecuteState(
            input="Test task",
            plan=Plan(steps=["Step 3"]),
            past_steps=[
                ("Step 1", "Result 1"),
                ("Step 2", "Result 2"),
            ],
        )
        
        assert len(state.past_steps) == 2
        assert state.past_steps[0] == ("Step 1", "Result 1")


class TestTaskPlanner:
    """Tests for TaskPlanner class"""
    
    @pytest.mark.asyncio
    async def test_plan_simple_task(self):
        """Simple task should return single-step plan"""
        planner = TaskPlanner()
        
        plan = await planner.plan("list files")
        
        assert plan.complexity == TaskComplexity.SIMPLE
        assert len(plan) == 1
        assert plan.steps[0] == "list files"
    
    @pytest.mark.asyncio
    async def test_plan_without_api_key(self):
        """Without API key, should fallback to simple plan"""
        # Temporarily remove API key
        original_key = os.environ.get("ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]
        
        try:
            planner = TaskPlanner()
            planner._client = None  # Force no client
            
            plan = await planner.plan("complex task with multiple steps")
            
            # Should fallback to single step
            assert len(plan) >= 1
        finally:
            # Restore API key
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key
    
    def test_parse_json_response_clean(self):
        """Test parsing clean JSON"""
        planner = TaskPlanner()
        
        response = '{"complexity": "moderate", "steps": ["Step 1", "Step 2"]}'
        result = planner._parse_json_response(response)
        
        assert result is not None
        assert result["complexity"] == "moderate"
        assert len(result["steps"]) == 2
    
    def test_parse_json_response_with_markdown(self):
        """Test parsing JSON wrapped in markdown"""
        planner = TaskPlanner()
        
        response = '''Here is the plan:
```json
{"complexity": "complex", "steps": ["A", "B", "C"]}
```
'''
        result = planner._parse_json_response(response)
        
        assert result is not None
        assert result["complexity"] == "complex"
        assert result["steps"] == ["A", "B", "C"]
    
    def test_parse_json_response_embedded(self):
        """Test parsing embedded JSON"""
        planner = TaskPlanner()
        
        response = 'Some text before {"steps": ["X"]} and after'
        result = planner._parse_json_response(response)
        
        assert result is not None
        assert result["steps"] == ["X"]


class TestConvenienceFunctions:
    """Tests for convenience functions"""
    
    def test_is_simple_task_function(self):
        """Test standalone is_simple_task"""
        assert is_simple_task("list files") == True
        assert is_simple_task("整理桌面然After生成Report") == False
    
    @pytest.mark.asyncio
    async def test_create_plan_function(self):
        """Test standalone create_plan"""
        plan = await create_plan("show directory contents")
        
        assert plan is not None
        assert len(plan) >= 1


class TestContextUnderstanding:
    """Tests for enhanced context understanding in prompts"""
    
    def test_format_operation_history_empty(self):
        """Test formatting empty history"""
        from engine.agent.react_agent import format_operation_history, _session_histories
        
        # Clear history
        _session_histories.clear()
        
        result = format_operation_history("new_session")
        
        assert "No operations yet" in result
    
    def test_format_operation_history_with_ops(self):
        """Test formatting history with operations"""
        from engine.agent.react_agent import (
            format_operation_history, 
            add_to_session_history,
            _session_histories
        )
        
        # Clear and add operations
        _session_histories.clear()
        
        add_to_session_history("test_session", {
            "tool": "move_file",
            "args": {"source": "/path/to/file.txt", "destination": "/new/path/"},
            "success": True,
        })
        
        add_to_session_history("test_session", {
            "tool": "create_directory",
            "args": {"path": "/new/folder"},
            "success": True,
        })
        
        result = format_operation_history("test_session")
        
        # Should contain reference targets
        assert "Reference Targets" in result
        assert "这个File" in result or "file.txt" in result
        assert "Recent operations" in result


# Run with: pytest tests/test_planner.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-x"])

