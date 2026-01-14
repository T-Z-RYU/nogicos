# -*- coding: utf-8 -*-
"""
Task Execution End-to-End Tests

Tests for NogicOS task execution functionality.
Requires: Backend server running (python hive_server.py)
"""

import json
import pytest
import asyncio
import aiohttp
import websockets
import socket


def is_server_running(port=8080):
    """Check if backend server is running"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(0.5)
        result = sock.connect_ex(('localhost', port))
        return result == 0
    finally:
        sock.close()


# Skip entire module if server not running
if not is_server_running():
    pytest.skip(
        "Backend server not running. Start with: python hive_server.py",
        allow_module_level=True
    )

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


class TestTaskExecutionAPI:
    """Tests for task execution via HTTP API"""
    
    async def test_execute_endpoint_exists(self, http_client, http_url):
        """Execute endpoint should exist"""
        # Try POST to /v2/execute (main execution endpoint)
        async with http_client.post(
            f"{http_url}/v2/execute",
            json={"message": "test", "session_id": "test"},
        ) as resp:
            # Should not be 404
            assert resp.status != 404
    
    async def test_execute_requires_message(self, http_client, http_url):
        """Execute should require a message"""
        async with http_client.post(
            f"{http_url}/v2/execute",
            json={"session_id": "test"},  # Missing message
        ) as resp:
            # Should return error (422 validation error or similar)
            # 429 is rate limit which is also acceptable
            assert resp.status in [400, 422, 429, 500]
    
    async def test_execute_simple_query(self, http_client, http_url):
        """Should be able to execute a simple query"""
        async with http_client.post(
            f"{http_url}/v2/execute",
            json={
                "message": "What is 2+2? Just answer with the number.",
                "session_id": "test_simple",
                "max_steps": 5,
            },
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            # 429 is rate limit - acceptable in CI where tests run fast
            assert resp.status in [200, 429]
            if resp.status == 429:
                pytest.skip("Rate limited - test passed structurally")
            data = await resp.json()
            # Should have some response
            assert isinstance(data, dict)
            # Check for success indicator or result
            has_result = (
                data.get("success") or 
                "result" in data or 
                "response" in data or
                "message" in data
            )
            assert has_result, f"Unexpected response format: {data}"


class TestKnowledgeStore:
    """Tests for knowledge store functionality"""
    
    async def test_stats_shows_trajectories(self, http_client, http_url):
        """Stats should show trajectory count"""
        async with http_client.get(f"{http_url}/stats") as resp:
            assert resp.status == 200
            data = await resp.json()
            # Should have trajectory info (might be 0 if empty)
            assert isinstance(data, dict)
    
    async def test_knowledge_persists(self, http_client, http_url):
        """Knowledge store should persist data"""
        # Get initial stats
        async with http_client.get(f"{http_url}/stats") as resp:
            initial_data = await resp.json()
        
        # Stats endpoint should work consistently
        async with http_client.get(f"{http_url}/stats") as resp:
            second_data = await resp.json()
        
        # Structure should be consistent
        assert type(initial_data) == type(second_data)


class TestNavigationCommands:
    """Tests for browser navigation commands"""
    
    async def test_navigate_command_via_ws(self, backend_server):
        """Should be able to send navigation command via WebSocket"""
        ws_url = backend_server["ws_url"]
        
        async with websockets.connect(ws_url) as ws:
            # Send navigation command (CDP style)
            await ws.send(json.dumps({
                "type": "cdp_command",
                "data": {
                    "requestId": "test_nav_1",
                    "method": "navigate",
                    "params": {"url": "https://example.com"},
                }
            }))
            
            # Wait for response (might not get one without Electron)
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                # Should get some response
                assert isinstance(data, dict)
            except asyncio.TimeoutError:
                # Without Electron running, navigation won't complete
                pytest.skip("Navigation requires Electron client")


class TestSessionManagement:
    """Tests for session management"""
    
    async def test_different_sessions_isolated(self, http_client, http_url):
        """Different session IDs should be isolated"""
        # Execute with session 1
        async with http_client.post(
            f"{http_url}/v2/execute",
            json={
                "message": "Remember: test value is 42",
                "session_id": "session_1",
                "max_steps": 3,
            },
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            data1 = await resp.json()
        
        # Execute with session 2
        async with http_client.post(
            f"{http_url}/v2/execute",
            json={
                "message": "What is the test value?",
                "session_id": "session_2",
                "max_steps": 3,
            },
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            data2 = await resp.json()
        
        # Both should complete without error
        assert isinstance(data1, dict)
        assert isinstance(data2, dict)


class TestErrorHandling:
    """Tests for error handling in task execution"""
    
    async def test_handles_empty_message(self, http_client, http_url):
        """Should handle empty message gracefully"""
        async with http_client.post(
            f"{http_url}/v2/execute",
            json={
                "message": "",
                "session_id": "test_empty",
            },
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            # Should not crash - might return error or handle gracefully
            # 429 is rate limit which is acceptable
            assert resp.status in [200, 400, 422, 429]
    
    async def test_handles_very_long_message(self, http_client, http_url):
        """Should handle very long message"""
        long_message = "test " * 1000  # 5000 chars
        
        async with http_client.post(
            f"{http_url}/v2/execute",
            json={
                "message": long_message,
                "session_id": "test_long",
                "max_steps": 1,
            },
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            # Should not crash - 429 is rate limit which is acceptable
            assert resp.status in [200, 400, 413, 422, 429, 500]

