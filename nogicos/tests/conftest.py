# -*- coding: utf-8 -*-
"""
Pytest Configuration

Fixtures and configuration for NogicOS tests.
"""

import os
import sys
import pytest
import asyncio
import aiohttp

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Default ports for testing (must match hive_server.py)
DEFAULT_HTTP_PORT = 8080  # HTTP/REST API
DEFAULT_WS_PORT = 8765    # WebSocket for real-time updates


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def tool_registry():
    """Create a fresh tool registry for testing"""
    from engine.tools.base import ToolRegistry
    return ToolRegistry()


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic client for testing without API key"""
    from unittest.mock import Mock, AsyncMock
    
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="Test response")]
    mock_response.stop_reason = "end_turn"
    
    mock_client.messages.create = Mock(return_value=mock_response)
    
    return mock_client


# =============================================================================
# Integration Test Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def http_url():
    """URL for HTTP API tests"""
    port = os.environ.get("TEST_HTTP_PORT", DEFAULT_HTTP_PORT)
    return f"http://localhost:{port}"


@pytest.fixture(scope="module")
def ws_url():
    """URL for WebSocket tests"""
    port = os.environ.get("TEST_WS_PORT", DEFAULT_WS_PORT)
    return f"ws://localhost:{port}/ws"


@pytest.fixture
async def http_client():
    """Async HTTP client for API tests"""
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        yield session


@pytest.fixture(scope="module")
async def backend_server():
    """
    Start backend server for integration tests.
    
    Note: This fixture expects the server to be started externally
    or skips tests if server is not available.
    """
    import socket
    
    http_port = int(os.environ.get("TEST_HTTP_PORT", DEFAULT_HTTP_PORT))
    ws_port = int(os.environ.get("TEST_WS_PORT", DEFAULT_WS_PORT))
    
    # Check if server is running
    def is_port_open(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result == 0
        finally:
            sock.close()
    
    if not is_port_open(ws_port):
        pytest.skip(
            f"Backend server not running on port {ws_port}. "
            "Start with: python hive_server.py"
        )
    
    yield {
        "http_url": f"http://localhost:{http_port}",
        "ws_url": f"ws://localhost:{ws_port}/ws",
        "http_port": http_port,
        "ws_port": ws_port,
    }


@pytest.fixture
def knowledge_store(tmp_path):
    """Create a temporary knowledge store for testing"""
    from engine.knowledge.store import KnowledgeStore
    
    db_path = tmp_path / "test_knowledge.db"
    store = KnowledgeStore(str(db_path))
    return store
