# -*- coding: utf-8 -*-
"""
D2.1: Agent Unit Tests

Tests for ReActAgent.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestAgentResult:
    """Tests for AgentResult dataclass"""
    
    def test_result_creation(self):
        """Test creating an AgentResult"""
        from engine.agent.react_agent import AgentResult
        
        result = AgentResult(
            success=True,
            response="Test response",
            iterations=5,
        )
        
        assert result.success is True
        assert result.response == "Test response"
        assert result.iterations == 5


class TestReActAgent:
    """Tests for ReActAgent class"""
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent(max_iterations=10)
        
        assert agent.max_iterations == 10
        assert agent.registry is not None
    
    def test_system_prompt_building(self):
        """Test system prompt includes tools"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        prompt = agent._build_system_prompt_with_history("test_session")
        
        assert "NogicOS" in prompt
        assert "autonomous" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_agent_no_client(self):
        """Test agent behavior without Anthropic client"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        agent.client = None  # Simulate no API key
        
        result = await agent.run("Test task")
        
        assert result.success is False
        assert "client not available" in result.error.lower()


class TestSessionHistory:
    """Tests for session history management"""
    
    def test_get_empty_history(self):
        """Test getting empty session history"""
        from engine.agent.react_agent import get_session_history
        
        history = get_session_history("nonexistent_session")
        
        assert history == []
    
    def test_add_to_history(self):
        """Test adding to session history"""
        from engine.agent.react_agent import (
            add_to_session_history,
            get_session_history,
            _session_histories
        )
        
        # Clear history first
        _session_histories.clear()
        
        add_to_session_history("test", {
            "tool": "move_file",
            "args": {"source": "a", "destination": "b"},
            "success": True,
        })
        
        history = get_session_history("test")
        assert len(history) == 1
        assert history[0]["tool"] == "move_file"
    
    def test_format_history(self):
        """Test formatting history for prompt"""
        from engine.agent.react_agent import (
            add_to_session_history,
            format_operation_history,
            _session_histories
        )
        
        _session_histories.clear()
        
        add_to_session_history("format_test", {
            "tool": "move_file",
            "args": {"source": "/a/b", "destination": "/c/d"},
            "success": True,
        })
        
        formatted = format_operation_history("format_test")
        
        assert "move_file" in formatted.lower() or "Moved" in formatted

