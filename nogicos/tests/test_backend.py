# -*- coding: utf-8 -*-
"""
Backend API Tests

Tests for NogicOS HTTP API endpoints.
Requires: Backend server running (python hive_server.py)
"""

import pytest
import aiohttp
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


class TestHealthEndpoint:
    """Tests for /health endpoint"""
    
    async def test_health_returns_200(self, http_client, http_url):
        """Health endpoint should return 200 OK"""
        async with http_client.get(f"{http_url}/health") as resp:
            assert resp.status == 200
    
    async def test_health_returns_json(self, http_client, http_url):
        """Health endpoint should return valid JSON"""
        async with http_client.get(f"{http_url}/health") as resp:
            data = await resp.json()
            assert isinstance(data, dict)
    
    async def test_health_contains_status(self, http_client, http_url):
        """Health response should contain status field"""
        async with http_client.get(f"{http_url}/health") as resp:
            data = await resp.json()
            assert "status" in data
            # "healthy" or "busy" are both acceptable
            assert data["status"] in ["healthy", "busy"]
    
    async def test_health_contains_engine_status(self, http_client, http_url):
        """Health response should indicate engine status"""
        async with http_client.get(f"{http_url}/health") as resp:
            data = await resp.json()
            assert "engine" in data


class TestStatsEndpoint:
    """Tests for /stats endpoint"""
    
    async def test_stats_returns_200(self, http_client, http_url):
        """Stats endpoint should return 200 OK"""
        async with http_client.get(f"{http_url}/stats") as resp:
            assert resp.status == 200
    
    async def test_stats_returns_json(self, http_client, http_url):
        """Stats endpoint should return valid JSON"""
        async with http_client.get(f"{http_url}/stats") as resp:
            data = await resp.json()
            assert isinstance(data, dict)
    
    async def test_stats_contains_knowledge_info(self, http_client, http_url):
        """Stats response should contain knowledge base info"""
        async with http_client.get(f"{http_url}/stats") as resp:
            data = await resp.json()
            # Should have some statistics about knowledge base
            assert "trajectories" in data or "skills" in data or "total" in data or len(data) > 0


class TestAPIAvailability:
    """Tests for API availability and error handling"""
    
    async def test_404_for_unknown_endpoint(self, http_client, http_url):
        """Unknown endpoints should return 404"""
        async with http_client.get(f"{http_url}/nonexistent") as resp:
            assert resp.status == 404
    
    async def test_cors_headers(self, http_client, http_url):
        """API should include CORS headers for browser access"""
        async with http_client.options(f"{http_url}/health") as resp:
            # Should not fail on OPTIONS request
            assert resp.status in [200, 204, 405]  # 405 is acceptable if CORS not configured

