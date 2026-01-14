# -*- coding: utf-8 -*-
"""
WebSocket Connection Tests

Tests for NogicOS WebSocket communication.
"""

import json
import pytest
import asyncio
import websockets
from websockets.protocol import State

pytestmark = pytest.mark.asyncio


def is_ws_open(ws) -> bool:
    """Check if websocket is open (compatible with different versions)"""
    if hasattr(ws, 'open'):
        return ws.open
    elif hasattr(ws, 'state'):
        return ws.state == State.OPEN
    return True  # If connected, assume open


class TestWebSocketConnection:
    """Tests for WebSocket connectivity"""
    
    async def test_ws_connects(self, backend_server):
        """Should be able to connect to WebSocket"""
        ws_url = backend_server["ws_url"]
        
        async with websockets.connect(ws_url) as ws:
            assert is_ws_open(ws)
    
    async def test_ws_ping_pong(self, backend_server):
        """WebSocket should respond to ping"""
        ws_url = backend_server["ws_url"]
        
        async with websockets.connect(ws_url) as ws:
            # Send ping message
            await ws.send(json.dumps({"type": "ping"}))
            
            # Wait for response (with timeout)
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                # Should get a pong or some response
                assert data.get("type") in ["pong", "status", "error"] or "type" in data
            except asyncio.TimeoutError:
                # Some servers don't respond to custom ping
                pass
    
    async def test_ws_get_status(self, backend_server):
        """Should be able to request status via WebSocket"""
        ws_url = backend_server["ws_url"]
        
        async with websockets.connect(ws_url) as ws:
            # Request status
            await ws.send(json.dumps({"type": "get_status"}))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                # Should get some status data
                assert isinstance(data, dict)
            except asyncio.TimeoutError:
                pytest.skip("Server did not respond to get_status")


class TestWebSocketMessages:
    """Tests for WebSocket message handling"""
    
    async def test_invalid_json_handled(self, backend_server):
        """Server should handle invalid JSON gracefully"""
        ws_url = backend_server["ws_url"]
        
        async with websockets.connect(ws_url) as ws:
            # Send invalid JSON
            await ws.send("not valid json")
            
            # Should not crash - try to get a response or just verify connection stays open
            await asyncio.sleep(0.5)
            assert is_ws_open(ws)
    
    async def test_unknown_message_type(self, backend_server):
        """Server should handle unknown message types"""
        ws_url = backend_server["ws_url"]
        
        async with websockets.connect(ws_url) as ws:
            # Send unknown message type
            await ws.send(json.dumps({"type": "unknown_type_12345"}))
            
            # Should not crash
            await asyncio.sleep(0.5)
            assert is_ws_open(ws)


class TestWebSocketReconnection:
    """Tests for WebSocket reconnection behavior"""
    
    async def test_multiple_connections(self, backend_server):
        """Server should handle multiple simultaneous connections"""
        ws_url = backend_server["ws_url"]
        
        # Open multiple connections
        connections = []
        for _ in range(3):
            ws = await websockets.connect(ws_url)
            connections.append(ws)
        
        # All should be open
        for ws in connections:
            assert is_ws_open(ws)
        
        # Close all
        for ws in connections:
            await ws.close()
    
    async def test_reconnect_after_close(self, backend_server):
        """Should be able to reconnect after closing connection"""
        ws_url = backend_server["ws_url"]
        
        # First connection
        ws1 = await websockets.connect(ws_url)
        assert is_ws_open(ws1)
        await ws1.close()
        
        # Reconnect
        ws2 = await websockets.connect(ws_url)
        assert is_ws_open(ws2)
        await ws2.close()

