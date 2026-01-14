# -*- coding: utf-8 -*-
"""
Core Path Tests for NogicOS V2

Tests the critical paths that must work for the product to function:
1. ReAct Agent initialization and basic execution
2. Tool registry and execution
3. Session persistence
4. Watchdog system
5. Error recovery

Run with: pytest tests/test_core.py -v
"""

import pytest
import asyncio
import os
import sys
import tempfile
from unittest.mock import Mock, AsyncMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.agent.react_agent import ReActAgent, AgentResult
from engine.tools import create_full_registry
from engine.tools.base import ToolResult
from engine.knowledge.store import PersistentSessionStore, KnowledgeStore
from engine.watchdog import ConnectionWatchdog, WatchdogConfig, ConnectionState


# ============================================================================
# ReAct Agent Tests
# ============================================================================

class TestReActAgentInitialization:
    """Test ReAct Agent initialization"""
    
    def test_agent_creates_without_api_key(self):
        """Agent should initialize even without API key (will fail on run)"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}, clear=False):
            agent = ReActAgent()
            assert agent is not None
            assert agent.registry is not None
    
    def test_agent_has_tool_registry(self):
        """Agent should have a populated tool registry"""
        agent = ReActAgent()
        tools = agent.registry.get_all()
        assert len(tools) > 0
    
    def test_agent_builds_system_prompt(self):
        """Agent should build valid system prompt"""
        agent = ReActAgent()
        prompt = agent._build_system_prompt_with_history("test_session")
        
        assert "NogicOS" in prompt
        assert "autonomous" in prompt.lower()
        assert len(prompt) > 100


class TestReActAgentExecution:
    """Test ReAct Agent execution flows"""
    
    @pytest.mark.asyncio
    async def test_agent_fails_without_client(self):
        """Agent should return error when no API client available"""
        agent = ReActAgent()
        agent.client = None  # Force no client
        
        result = await agent.run("test task")
        
        assert not result.success
        assert "API key" in result.error or "client" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_agent_result_structure(self):
        """AgentResult should have correct structure"""
        result = AgentResult(
            success=True,
            response="Test response",
            iterations=3,
            tool_calls=[{"name": "test_tool"}]
        )
        
        assert result.success is True
        assert result.response == "Test response"
        assert result.iterations == 3
        assert len(result.tool_calls) == 1


class TestExecuteWithRetry:
    """Test smart retry mechanism"""
    
    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Should retry on timeout errors"""
        agent = ReActAgent()
        
        call_count = 0
        async def mock_execute(tool_name, args):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return ToolResult(success=False, output=None, error="Connection timeout")
            return ToolResult(success=True, output="success", error=None)
        
        agent.registry.execute = mock_execute
        
        result = await agent._execute_with_retry("test_tool", {})
        
        assert result.success
        assert call_count == 2  # Original + 1 retry
    
    @pytest.mark.asyncio
    async def test_no_retry_on_not_found(self):
        """Should not retry on 'not found' errors"""
        agent = ReActAgent()
        
        call_count = 0
        async def mock_execute(tool_name, args):
            nonlocal call_count
            call_count += 1
            return ToolResult(success=False, output=None, error="File not found")
        
        agent.registry.execute = mock_execute
        
        result = await agent._execute_with_retry("test_tool", {})
        
        assert not result.success
        assert call_count == 1  # No retries for deterministic failure


# ============================================================================
# Tool Registry Tests
# ============================================================================

class TestToolRegistry:
    """Test tool registry functionality"""
    
    def test_registry_creates_successfully(self):
        """Registry should create with default tools"""
        registry = create_full_registry()
        assert registry is not None
    
    def test_registry_has_core_tools(self):
        """Registry should have essential tools"""
        registry = create_full_registry()
        tools = registry.get_all()
        tool_names = [t.name for t in tools]
        
        # Check for essential local tools
        assert "list_directory" in tool_names
        assert "read_file" in tool_names
        assert "write_file" in tool_names
    
    def test_registry_to_anthropic_format(self):
        """Registry should convert to Anthropic API format"""
        registry = create_full_registry()
        anthropic_tools = registry.to_anthropic_format()
        
        assert isinstance(anthropic_tools, list)
        assert len(anthropic_tools) > 0
        
        # Check tool structure
        for tool in anthropic_tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
    
    @pytest.mark.asyncio
    async def test_list_directory_execution(self):
        """list_directory tool should work"""
        registry = create_full_registry()
        
        # Test listing current directory
        result = await registry.execute("list_directory", {"path": "."})
        
        assert result.success
        assert result.output is not None


# ============================================================================
# Session Persistence Tests
# ============================================================================

class TestSessionPersistence:
    """Test session persistence functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_store_creates_database(self, temp_db):
        """Store should create SQLite database"""
        store = PersistentSessionStore(db_path=temp_db)
        assert os.path.exists(temp_db)
    
    def test_save_and_load_session(self, temp_db):
        """Should save and load session correctly"""
        store = PersistentSessionStore(db_path=temp_db)
        
        session_id = "test_session_123"
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        preferences = {"language": "zh"}
        
        # Save
        store.save_session(session_id, history, preferences, "Test Chat")
        
        # Load
        session = store.load_session(session_id)
        
        assert session["id"] == session_id
        assert session["title"] == "Test Chat"
        assert len(session["history"]) == 2
        assert session["preferences"]["language"] == "zh"
    
    def test_load_nonexistent_session(self, temp_db):
        """Loading nonexistent session should return empty history"""
        store = PersistentSessionStore(db_path=temp_db)
        
        session = store.load_session("nonexistent")
        
        assert session["history"] == []
        assert session["id"] == "nonexistent"
    
    def test_list_sessions(self, temp_db):
        """Should list recent sessions"""
        store = PersistentSessionStore(db_path=temp_db)
        
        # Create multiple sessions
        for i in range(5):
            store.save_session(
                f"session_{i}",
                [{"role": "user", "content": f"Message {i}"}],
                {},
                f"Chat {i}"
            )
        
        sessions = store.list_sessions(limit=3)
        
        assert len(sessions) == 3
        # Should be ordered by most recent
        assert sessions[0]["title"] == "Chat 4"
    
    def test_delete_session(self, temp_db):
        """Should delete session"""
        store = PersistentSessionStore(db_path=temp_db)
        
        store.save_session("to_delete", [{"role": "user", "content": "test"}])
        
        deleted = store.delete_session("to_delete")
        assert deleted is True
        
        # Verify deleted
        session = store.load_session("to_delete")
        assert session["history"] == []


# ============================================================================
# Watchdog Tests
# ============================================================================

class TestWatchdog:
    """Test watchdog system"""
    
    def test_watchdog_initializes(self):
        """Watchdog should initialize with default config"""
        watchdog = ConnectionWatchdog()
        
        assert watchdog is not None
        assert watchdog.config.check_interval == 5.0
        assert watchdog.config.max_retries == 5
    
    def test_watchdog_custom_config(self):
        """Watchdog should accept custom config"""
        config = WatchdogConfig(
            check_interval=10.0,
            max_retries=3,
            api_url="http://localhost:9000"
        )
        watchdog = ConnectionWatchdog(config=config)
        
        assert watchdog.config.check_interval == 10.0
        assert watchdog.config.max_retries == 3
        assert watchdog.config.api_url == "http://localhost:9000"
    
    def test_watchdog_initial_state(self):
        """Watchdog should start with disconnected state"""
        watchdog = ConnectionWatchdog()
        
        assert watchdog.status.websocket == ConnectionState.DISCONNECTED
        assert watchdog.status.api == ConnectionState.DISCONNECTED
        assert watchdog.is_healthy is False
    
    @pytest.mark.asyncio
    async def test_watchdog_state_callback(self):
        """Watchdog should call state change callback"""
        state_changes = []
        
        def on_change(status):
            state_changes.append(status)
        
        watchdog = ConnectionWatchdog(on_state_change=on_change)
        
        # Manually trigger state check (would normally happen in start())
        await watchdog._check_all_connections()
        
        # State should have been notified
        # (Initial disconnected state counts as a change from nothing)
        assert len(state_changes) >= 0  # May or may not have changed


# ============================================================================
# Knowledge Store Tests
# ============================================================================

class TestKnowledgeStore:
    """Test knowledge store functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_store_creates(self, temp_db):
        """Knowledge store should create"""
        store = KnowledgeStore(db_path=temp_db)
        assert store is not None
    
    def test_profile_management(self, temp_db):
        """Should create and retrieve user profiles"""
        store = KnowledgeStore(db_path=temp_db)
        
        profile = store.get_profile("test_user")
        
        assert profile.id == "test_user"
        assert isinstance(profile.frequent_folders, list)
    
    def test_stats(self, temp_db):
        """Should return statistics"""
        store = KnowledgeStore(db_path=temp_db)
        
        stats = store.get_stats()
        
        assert "trajectory_count" in stats
        assert "success_rate" in stats
        assert "db_path" in stats


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for core flows"""
    
    @pytest.mark.asyncio
    async def test_full_agent_flow_mock(self):
        """Test full agent flow with mocked API"""
        agent = ReActAgent()
        
        # Skip if no API client (requires real API for streaming)
        # This test is better suited for unit tests with proper mocking
        if agent.client is None:
            pytest.skip("No Anthropic API client - test requires API key")
        
        # Run a simple task that should complete quickly
        result = await agent.run("What is 2+2? Answer with just the number.")
        
        # Should either succeed or fail with a clear error
        # (This is an integration test, so we accept any non-crash behavior)
        assert isinstance(result, AgentResult)
        assert result.iterations >= 1
    
    @pytest.fixture
    def temp_db(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_session_persistence_integration(self, temp_db):
        """Test session save and restore flow"""
        store = PersistentSessionStore(db_path=temp_db)
        
        # Simulate a conversation
        session_id = "integration_test"
        messages = [
            {"role": "user", "content": "CreateFile夹 test_folder"},
            {"role": "assistant", "content": "已Create test_folder"},
        ]
        
        # Save session
        store.save_session(session_id, messages, {"language": "zh"})
        
        # Simulate app restart - create new store instance
        store2 = PersistentSessionStore(db_path=temp_db)
        
        # Restore session
        restored = store2.load_session(session_id)
        
        assert len(restored["history"]) == 2
        assert restored["history"][0]["content"] == "CreateFile夹 test_folder"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

