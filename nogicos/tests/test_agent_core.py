# -*- coding: utf-8 -*-
"""
Core Agent Tests - Coverage for Critical Paths

These tests ensure the ReActAgent core functionality works correctly.
Run before any refactoring to establish baseline.

Usage:
    cd nogicos
    pytest tests/test_agent_core.py -v
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from dataclasses import dataclass


# =============================================================================
# Test: Agent Imports Module
# =============================================================================

class TestImportsModule:
    """Tests for the centralized imports module"""
    
    def test_imports_module_exists(self):
        """Verify imports module can be imported"""
        from engine.agent import imports
        assert hasattr(imports, 'ANTHROPIC_AVAILABLE')
        assert hasattr(imports, 'create_anthropic_client')
    
    def test_get_available_features(self):
        """Test feature availability summary"""
        from engine.agent.imports import get_available_features
        
        features = get_available_features()
        
        assert isinstance(features, dict)
        assert 'anthropic' in features
        assert 'knowledge' in features
        assert 'planner' in features
        assert 'classifier' in features
    
    def test_create_client_without_key(self):
        """Test client creation fails gracefully without API key"""
        from engine.agent.imports import create_anthropic_client
        
        # Temporarily clear API key
        import os
        old_key = os.environ.pop('ANTHROPIC_API_KEY', None)
        
        try:
            client = create_anthropic_client()
            # Should return None without API key (if anthropic is available)
            # or None if anthropic is not installed
        finally:
            if old_key:
                os.environ['ANTHROPIC_API_KEY'] = old_key


# =============================================================================
# Test: AgentResult
# =============================================================================

class TestAgentResult:
    """Tests for AgentResult dataclass"""
    
    def test_success_result(self):
        """Test successful result creation"""
        from engine.agent.react_agent import AgentResult
        
        result = AgentResult(
            success=True,
            response="Task completed",
            iterations=3,
            tool_calls=[{"name": "test_tool", "success": True}]
        )
        
        assert result.success is True
        assert result.response == "Task completed"
        assert result.iterations == 3
        assert len(result.tool_calls) == 1
        assert result.error is None
    
    def test_failure_result(self):
        """Test failure result creation"""
        from engine.agent.react_agent import AgentResult
        
        result = AgentResult(
            success=False,
            response="",
            error="API key missing",
            iterations=0
        )
        
        assert result.success is False
        assert result.error == "API key missing"


# =============================================================================
# Test: Session History
# =============================================================================

class TestSessionHistory:
    """Tests for session history management"""
    
    def setup_method(self):
        """Clear history before each test"""
        from engine.agent.react_agent import _session_histories
        _session_histories.clear()
    
    def test_empty_history(self):
        """Test getting empty session history"""
        from engine.agent.react_agent import get_session_history
        
        history = get_session_history("new_session")
        assert history == []
    
    def test_add_single_operation(self):
        """Test adding single operation to history"""
        from engine.agent.react_agent import (
            add_to_session_history,
            get_session_history
        )
        
        add_to_session_history("test_session", {
            "tool": "move_file",
            "args": {"source": "a.txt", "destination": "b/a.txt"},
            "success": True
        })
        
        history = get_session_history("test_session")
        assert len(history) == 1
        assert history[0]["tool"] == "move_file"
    
    def test_history_limit(self):
        """Test history is limited to 20 entries"""
        from engine.agent.react_agent import (
            add_to_session_history,
            get_session_history
        )
        
        # Add 25 entries
        for i in range(25):
            add_to_session_history("limit_test", {
                "tool": f"tool_{i}",
                "success": True
            })
        
        history = get_session_history("limit_test")
        assert len(history) == 20
        # Should keep the most recent
        assert history[0]["tool"] == "tool_5"
    
    def test_format_history_with_references(self):
        """Test history formatting includes reference targets"""
        from engine.agent.react_agent import (
            add_to_session_history,
            format_operation_history
        )
        
        add_to_session_history("format_test", {
            "tool": "move_file",
            "args": {"source": "/path/to/file.txt", "destination": "/dest/"},
            "success": True
        })
        
        formatted = format_operation_history("format_test")
        
        assert "Reference Targets" in formatted
        assert "file.txt" in formatted or "它" in formatted


# =============================================================================
# Test: ReActAgent Initialization
# =============================================================================

class TestAgentInit:
    """Tests for ReActAgent initialization"""
    
    def test_basic_init(self):
        """Test basic agent initialization"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent(max_iterations=10)
        
        assert agent.max_iterations == 10
        assert agent.registry is not None
        assert agent.model == "claude-opus-4-5-20251101"
    
    def test_custom_model(self):
        """Test agent with custom model"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent(model="claude-sonnet-4-20250514")
        
        assert agent.model == "claude-sonnet-4-20250514"
    
    def test_tool_registry_populated(self):
        """Test tool registry is populated"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        tools = agent.registry.get_all()
        
        assert len(tools) > 0
        # Should have at least some local tools
        tool_names = [t.name for t in tools]
        assert "list_directory" in tool_names or "read_file" in tool_names
    
    def test_tool_categories_cache(self):
        """Test tool categories are cached"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        
        assert len(agent._tool_categories_cache) > 0
        # Should contain tool name -> category value mapping
        assert all(isinstance(v, str) for v in agent._tool_categories_cache.values())


# =============================================================================
# Test: Task Classification
# =============================================================================

class TestTaskClassification:
    """Tests for task classification in agent"""
    
    def test_classify_local_task(self):
        """Test classification of local file task"""
        from engine.agent.imports import CLASSIFIER_AVAILABLE
        
        if not CLASSIFIER_AVAILABLE:
            pytest.skip("Classifier not available")
        
        from engine.agent.classifier import TaskClassifier
        
        classifier = TaskClassifier()
        result = classifier.classify("整理桌面Up的File")
        
        assert result.task_type.value == "local"
        assert result.confidence > 0.5
    
    def test_classify_browser_task(self):
        """Test classification of browser task"""
        from engine.agent.imports import CLASSIFIER_AVAILABLE
        
        if not CLASSIFIER_AVAILABLE:
            pytest.skip("Classifier not available")
        
        from engine.agent.classifier import TaskClassifier
        
        classifier = TaskClassifier()
        # Use clear browser keywords
        result = classifier.classify("navigate to https://google.com and click the search button")
        
        assert result.task_type.value == "browser"
    
    def test_agent_tool_filtering_local(self):
        """Test agent filters tools for local tasks"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        tools = agent._get_tools_by_task_type("local")
        
        # Should return tools (not empty)
        assert len(tools) > 0
        
        # All should be in local/plan category
        for tool in tools:
            cat = agent._tool_categories_cache.get(tool["name"])
            assert cat in ("local", "plan", None)  # None for unlisted
    
    def test_agent_tool_filtering_browser(self):
        """Test agent filters tools for browser tasks"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        tools = agent._get_tools_by_task_type("browser")
        
        # All should be in browser/plan category
        for tool in tools:
            cat = agent._tool_categories_cache.get(tool["name"])
            assert cat in ("browser", "plan", None)
    
    def test_agent_tool_filtering_mixed(self):
        """Test agent returns all tools for mixed tasks"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        all_tools = agent.registry.to_anthropic_format()
        mixed_tools = agent._get_tools_by_task_type("mixed")
        
        # Mixed should return all tools
        assert len(mixed_tools) == len(all_tools)


# =============================================================================
# Test: Error Classification
# =============================================================================

class TestErrorClassification:
    """Tests for error classification in retry logic"""
    
    def test_classify_not_found(self):
        """Test classification of not found errors"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        
        error_type, retryable, _ = agent._classify_error("File not found: /path/to/file")
        
        assert error_type == "not_found"
        assert retryable is False
    
    def test_classify_timeout(self):
        """Test classification of timeout errors"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        
        error_type, retryable, _ = agent._classify_error("Operation timed out after 30s")
        
        assert error_type == "timeout"
        assert retryable is True
    
    def test_classify_permission(self):
        """Test classification of permission errors"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        
        error_type, retryable, _ = agent._classify_error("Permission denied: /protected/file")
        
        assert error_type == "permission"
        assert retryable is False
    
    def test_classify_rate_limit(self):
        """Test classification of rate limit errors"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        
        error_type, retryable, _ = agent._classify_error("Rate limit exceeded, 429 error")
        
        assert error_type == "rate_limit"
        assert retryable is True
    
    def test_classify_unknown(self):
        """Test classification of unknown errors"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        
        error_type, retryable, _ = agent._classify_error("Something weird happened")
        
        assert error_type == "unknown"
        assert retryable is True  # Default to retryable for unknown


# =============================================================================
# Test: Agent Run (No Client)
# =============================================================================

class TestAgentRunNoClient:
    """Tests for agent run without Anthropic client"""
    
    @pytest.mark.asyncio
    async def test_run_without_client(self):
        """Test run returns error without client"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        agent.client = None  # Simulate no client
        
        result = await agent.run("Test task")
        
        assert result.success is False
        assert "client not available" in result.error.lower()


# =============================================================================
# Test: System Prompt Building
# =============================================================================

class TestSystemPromptBuilding:
    """Tests for system prompt construction"""
    
    def test_prompt_contains_core_elements(self):
        """Test system prompt has essential elements"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        prompt = agent._build_system_prompt_with_history("test")
        
        assert "NogicOS" in prompt
        assert "autonomous" in prompt.lower() or "AUTONOMOUS" in prompt
        assert "tool" in prompt.lower()
    
    def test_prompt_includes_history_placeholder(self):
        """Test prompt processes history placeholder"""
        from engine.agent.react_agent import (
            ReActAgent,
            add_to_session_history,
            _session_histories
        )
        
        _session_histories.clear()
        
        add_to_session_history("prompt_test", {
            "tool": "list_directory",
            "args": {"path": "/test"},
            "success": True
        })
        
        agent = ReActAgent()
        prompt = agent._build_system_prompt_with_history("prompt_test")
        
        # Should have replaced placeholder with actual history
        assert "{operation_history}" not in prompt
        # History content should be present
        assert "list" in prompt.lower() or "directory" in prompt.lower() or "Recent" in prompt


# =============================================================================
# Test: Cache Warming
# =============================================================================

class TestCacheWarming:
    """Tests for prompt cache warming"""
    
    def test_cache_not_warm_initially(self):
        """Test cache is not warm for new session"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        
        assert agent._is_cache_warm("new_session") is False
    
    def test_cache_ttl(self):
        """Test cache TTL is set"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        
        assert agent._cache_ttl == 300  # 5 minutes


# =============================================================================
# Test: Browser Session Management
# =============================================================================

class TestBrowserSessionManagement:
    """Tests for browser session lifecycle"""
    
    def test_browser_session_initially_inactive(self):
        """Test browser session is inactive on init"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        
        assert agent._browser_session is None
        assert agent._browser_session_active is False
    
    @pytest.mark.asyncio
    async def test_cleanup_browser_session(self):
        """Test browser session cleanup"""
        from engine.agent.react_agent import ReActAgent
        
        agent = ReActAgent()
        # Simulate active session
        agent._browser_session_active = True
        agent._browser_session = Mock()
        
        await agent.cleanup_browser_session()
        
        assert agent._browser_session is None
        assert agent._browser_session_active is False

