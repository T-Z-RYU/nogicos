# -*- coding: utf-8 -*-
"""
D2.2: Tool Unit Tests

Tests for ToolRegistry and tool execution.
"""

import pytest
import asyncio
from engine.tools.base import ToolRegistry, ToolCategory, ToolResult


class TestToolRegistry:
    """Tests for ToolRegistry class"""
    
    def test_registry_creation(self):
        """Test creating a new registry"""
        registry = ToolRegistry()
        assert registry is not None
        assert len(registry.get_all()) == 0
    
    def test_tool_registration(self):
        """Test registering a tool via decorator"""
        registry = ToolRegistry()
        
        @registry.action("Test action", category=ToolCategory.LOCAL)
        async def test_action(message: str) -> str:
            return f"Received: {message}"
        
        tools = registry.get_all()
        assert len(tools) == 1
        assert tools[0].name == "test_action"
        assert tools[0].category == ToolCategory.LOCAL
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test executing a registered tool"""
        registry = ToolRegistry()
        
        @registry.action("Echo message", category=ToolCategory.LOCAL)
        async def echo(message: str) -> str:
            return f"Echo: {message}"
        
        result = await registry.execute("echo", {"message": "hello"})
        
        assert result.success is True
        assert result.output == "Echo: hello"
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_tool_not_found(self):
        """Test executing non-existent tool"""
        registry = ToolRegistry()
        
        result = await registry.execute("nonexistent", {})
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_tool_retry_on_failure(self):
        """Test retry logic on transient failures"""
        registry = ToolRegistry()
        call_count = 0
        
        @registry.action("Flaky action", category=ToolCategory.LOCAL)
        async def flaky_action() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Transient error")
            return "Success on attempt 3"
        
        result = await registry.execute("flaky_action", {}, max_retries=3)
        
        assert result.success is True
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_tool_timeout(self):
        """Test timeout handling"""
        registry = ToolRegistry()
        
        @registry.action("Slow action", category=ToolCategory.LOCAL)
        async def slow_action() -> str:
            await asyncio.sleep(5)
            return "Done"
        
        result = await registry.execute(
            "slow_action", {},
            max_retries=1,
            timeout_seconds=0.1
        )
        
        assert result.success is False
        # Error message is user-friendly, check for "too long" instead of "timed out"
        assert "too long" in result.error.lower() or "timed out" in result.error.lower()
    
    def test_anthropic_format(self):
        """Test conversion to Anthropic tool format"""
        registry = ToolRegistry()
        
        @registry.action("Test tool", category=ToolCategory.LOCAL)
        async def test_tool(arg1: str, arg2: int = 10) -> str:
            return "test"
        
        tools = registry.to_anthropic_format()
        
        assert len(tools) == 1
        tool = tools[0]
        assert tool["name"] == "test_tool"
        assert "description" in tool
        assert "input_schema" in tool
        assert "arg1" in tool["input_schema"]["properties"]
        assert "arg2" in tool["input_schema"]["properties"]
    
    def test_context_injection(self):
        """Test context injection into tools"""
        registry = ToolRegistry()
        registry.set_context("test_value", "injected")
        
        assert registry.get_context("test_value") == "injected"
        assert registry.get_context("nonexistent") is None


class TestFriendlyErrors:
    """Tests for user-friendly error messages"""
    
    def test_timeout_error(self):
        """Test timeout error message"""
        registry = ToolRegistry()
        error = registry._make_friendly_error("test_tool", "operation timed out")
        assert "too long" in error.lower()
    
    def test_not_found_error(self):
        """Test not found error message"""
        registry = ToolRegistry()
        error = registry._make_friendly_error("test_tool", "file not found")
        assert "could not find" in error.lower()
    
    def test_permission_error(self):
        """Test permission error message"""
        registry = ToolRegistry()
        error = registry._make_friendly_error("test_tool", "permission denied")
        assert "permission" in error.lower()

