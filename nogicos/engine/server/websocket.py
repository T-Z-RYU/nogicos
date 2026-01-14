# -*- coding: utf-8 -*-
"""
WebSocket Server - Real-time status broadcast to Electron client

Architecture:
    Python Engine → WebSocket Server → Electron Client
    
Message Types:
    - status: Agent state, learning state, knowledge stats
    - action: Current action being executed
    - result: Task completion result
    - error: Error notification

Usage:
    server = StatusServer()
    await server.start()
    await server.broadcast_status({"agent": "thinking"})
"""

import asyncio
import json
import logging
from typing import Set, Dict, Any, Optional, AsyncGenerator, List
from dataclasses import dataclass, asdict, field
from datetime import datetime

logger = logging.getLogger("nogicos.server")

# Import stream protocol
try:
    from engine.stream.protocol import (
        StreamChunk, StreamBuilder, ChunkType, 
        ToolCallStatus, PlanStepStatus, ArtifactType,
        create_stream_builder
    )
    STREAM_PROTOCOL_AVAILABLE = True
except ImportError:
    STREAM_PROTOCOL_AVAILABLE = False
    logger.warning("[Server] Stream protocol not available")

# Try to import websockets, gracefully handle if not installed
try:
    import websockets
    # Use TYPE_CHECKING to avoid deprecation warning at runtime
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("[Server] websockets not installed. Run: pip install websockets")


@dataclass
class AgentStatus:
    """Current agent status"""
    state: str = "idle"  # idle, thinking, acting, done, error
    task: str = ""
    step: int = 0
    max_steps: int = 10
    progress: float = 0.0
    last_action: str = ""
    error: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring (A3.1)"""
    ttft_ms: Optional[float] = None  # Time to First Token
    total_time_ms: Optional[float] = None  # Total execution time
    tokens_generated: int = 0
    tool_calls: int = 0
    iterations: int = 0


@dataclass
class LearningStatus:
    """Passive learning status"""
    state: str = "idle"  # idle, recording, saved
    action_count: int = 0
    last_saved: Optional[str] = None


@dataclass
class KnowledgeStats:
    """Knowledge store statistics"""
    trajectory_count: int = 0
    domain_count: int = 0
    domains: list[str] = field(default_factory=list)


@dataclass
class FullStatus:
    """Complete status for broadcast"""
    agent: AgentStatus
    learning: LearningStatus
    knowledge: KnowledgeStats
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "type": "status",
            "data": {
                "agent": asdict(self.agent),
                "learning": asdict(self.learning),
                "knowledge": asdict(self.knowledge),
                "timestamp": self.timestamp,
            }
        }


class StatusServer:
    """
    WebSocket server for broadcasting status to Electron client
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self._clients: Set = set()
        self._server = None
        self._running = False
        
        # Current status
        self._agent_status = AgentStatus()
        self._learning_status = LearningStatus()
        self._knowledge_stats = KnowledgeStats()

        # CDP response callbacks (for Python → Electron → Python bidirectional communication)
        self._cdp_response_handlers: Dict[str, Any] = {}
        self._cdp_handler_timestamps: Dict[str, float] = {}  # Track creation time for cleanup

        # Tool response callbacks (for Tool calls to Electron)
        self._tool_response_handlers: Dict[str, Any] = {}
        self._tool_handler_timestamps: Dict[str, float] = {}  # Track creation time for cleanup

        # Handler timeout in seconds (default: 5 minutes)
        self._handler_timeout_seconds: float = 300.0

        # Start background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
    
        # Confirmation responses (for YC Workflow etc.)
        # Maps request_id -> {"confirmed": bool, "timestamp": float}
        self.confirm_responses: Dict[str, Dict[str, Any]] = {}
    
    @property
    def client_count(self) -> int:
        return len(self._clients)
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    async def start(self):
        """Start WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("[Server] Cannot start: websockets not installed")
            return False

        if self._running:
            logger.warning("[Server] Already running")
            return True

        try:
            self._server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port,
            )
            self._running = True

            # Start background cleanup task for stale handlers
            self._cleanup_task = asyncio.create_task(self._cleanup_stale_handlers())

            logger.info(f"[Server] WebSocket server started at ws://{self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"[Server] Failed to start: {e}")
            return False

    async def _cleanup_stale_handlers(self):
        """Background task to clean up stale response handlers to prevent memory leaks"""
        import time
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute
                current_time = time.time()

                # Clean up stale CDP handlers
                stale_cdp = [
                    request_id for request_id, timestamp in self._cdp_handler_timestamps.items()
                    if current_time - timestamp > self._handler_timeout_seconds
                ]
                for request_id in stale_cdp:
                    self._cdp_response_handlers.pop(request_id, None)
                    self._cdp_handler_timestamps.pop(request_id, None)
                    logger.debug(f"[Server] Cleaned up stale CDP handler: {request_id[:8]}...")

                # Clean up stale tool handlers
                stale_tool = [
                    call_id for call_id, timestamp in self._tool_handler_timestamps.items()
                    if current_time - timestamp > self._handler_timeout_seconds
                ]
                for call_id in stale_tool:
                    self._tool_response_handlers.pop(call_id, None)
                    self._tool_handler_timestamps.pop(call_id, None)
                    logger.debug(f"[Server] Cleaned up stale tool handler: {call_id[:8]}...")

                if stale_cdp or stale_tool:
                    logger.info(f"[Server] Cleaned up {len(stale_cdp)} CDP + {len(stale_tool)} tool stale handlers")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"[Server] Handler cleanup error: {e}")
    
    async def stop(self):
        """Stop WebSocket server"""
        if not self._running:
            return

        self._running = False

        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

        # Clear all pending handlers to prevent memory leaks
        self._cdp_response_handlers.clear()
        self._cdp_handler_timestamps.clear()
        self._tool_response_handlers.clear()
        self._tool_handler_timestamps.clear()

        # Close all client connections with timeout
        if self._clients:
            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        *[client.close() for client in self._clients],
                        return_exceptions=True
                    ),
                    timeout=5.0  # 5 second timeout for graceful close
                )
            except asyncio.TimeoutError:
                logger.warning("[Server] Timeout closing client connections")
            self._clients.clear()
        
        # Close server
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        
        logger.info("[Server] WebSocket server stopped")
    
    async def _handle_client(self, websocket):
        """Handle new client connection"""
        self._clients.add(websocket)
        client_id = id(websocket)
        logger.info(f"[Server] Client connected: {client_id} (total: {len(self._clients)})")
        
        try:
            # Send current status on connect
            await self._send_full_status(websocket)
            
            # Handle incoming messages
            async for message in websocket:
                await self._handle_message(websocket, message)
                
        except websockets.ConnectionClosed:
            logger.info(f"[Server] Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"[Server] Client error: {e}")
        finally:
            self._clients.discard(websocket)
            logger.info(f"[Server] Client removed: {client_id} (remaining: {len(self._clients)})")
    
    # Security: Maximum message size (1MB) to prevent DoS
    MAX_MESSAGE_SIZE = 1 * 1024 * 1024

    # [P0-3 FIX] Security: Maximum JSON nesting depth to prevent DoS
    MAX_JSON_DEPTH = 20

    # Security: Allowed tool names whitelist (use frozenset for immutability)
    # [P0 FIX Round 2] REMOVED shell_execute - too dangerous for remote execution
    # shell_execute can run arbitrary commands, should never be exposed via WebSocket
    ALLOWED_TOOLS = frozenset({
        "browser_navigate", "browser_click", "browser_type", "browser_scroll",
        "browser_screenshot", "browser_read", "browser_close",
        "file_read", "file_list", "file_search",  # REMOVED file_write - potential data loss
        "search_web", "search_tavily",
        "desktop_screenshot", "desktop_click", "desktop_type",
        "memory_add", "memory_search", "memory_list",
    })

    @staticmethod
    def _check_json_depth(obj, current_depth: int = 0, max_depth: int = 20) -> bool:
        """
        [P0-3 FIX] Check if JSON object exceeds maximum nesting depth.
        Returns True if depth is within limits, False otherwise.
        """
        if current_depth > max_depth:
            return False

        if isinstance(obj, dict):
            for value in obj.values():
                if not StatusServer._check_json_depth(value, current_depth + 1, max_depth):
                    return False
        elif isinstance(obj, list):
            for item in obj:
                if not StatusServer._check_json_depth(item, current_depth + 1, max_depth):
                    return False

        return True

    async def _handle_message(self, websocket, message: str):
        """Handle incoming message from client"""
        # Security: Check message size
        if len(message) > self.MAX_MESSAGE_SIZE:
            logger.warning(f"[Server] Message too large: {len(message)} bytes (max: {self.MAX_MESSAGE_SIZE})")
            await websocket.send(json.dumps({"type": "error", "message": "Message too large"}))
            return

        try:
            # [P0-3 FIX] Parse JSON with depth limit protection
            data = json.loads(message)

            # [P0-3 FIX] Validate JSON nesting depth to prevent stack overflow
            if not self._check_json_depth(data, max_depth=self.MAX_JSON_DEPTH):
                logger.warning(f"[Server] JSON nesting depth exceeds limit: {self.MAX_JSON_DEPTH}")
                await websocket.send(json.dumps({"type": "error", "message": "JSON too deeply nested"}))
                return
            msg_type = data.get("type", "")
            
            if msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
            
            elif msg_type == "get_status":
                await self._send_full_status(websocket)
            
            elif msg_type == "command":
                # Handle commands from client (future use)
                cmd = data.get("command", "")
                logger.info(f"[Server] Received command: {cmd}")
            
            # CDP command forwarding (Option A)
            elif msg_type == "cdp_command":
                # Forward CDP command to all other clients (mainly Electron)
                await self._forward_cdp_message(websocket, data)
            
            elif msg_type == "cdp_response":
                # Forward CDP response to all other clients
                await self._forward_cdp_message(websocket, data)
            
            elif msg_type == "cdp_ready":
                # Forward CDP ready status
                await self._forward_cdp_message(websocket, data)
            
            # Tool response handling (from Electron)
            elif msg_type == "tool_response":
                logger.info(f"[Server] Received tool_response: {data.get('call_id', 'unknown')[:8]}...")
                await self._handle_tool_response(data)
            
            # Confirmation response (from frontend, for YC Workflow etc.)
            elif msg_type == "confirm_response":
                request_id = data.get("request_id")
                confirmed = data.get("confirmed", False)
                if request_id:
                    import time
                    self.confirm_responses[request_id] = {
                        "confirmed": confirmed,
                        "timestamp": time.time(),
                    }
                    logger.info(f"[Server] Confirmation response: {request_id[:8]}... = {confirmed}")
            
        except json.JSONDecodeError:
            logger.warning(f"[Server] Invalid JSON: {message}")
    
    async def _forward_cdp_message(self, sender, data: dict):
        """Forward CDP messages to all other clients"""
        msg_str = json.dumps(data)
        
        # Send to all clients except sender
        for client in self._clients:
            if client != sender:
                try:
                    await client.send(msg_str)
                except Exception as e:
                    logger.error(f"[Server] CDP forward error: {e}")
        
        # If cdp_response, also notify internal handlers
        msg_type = data.get("type")
        if msg_type == "cdp_response":
            request_id = data.get("requestId")
            if request_id and request_id in self._cdp_response_handlers:
                handler = self._cdp_response_handlers[request_id]
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"[Server] CDP response handler error: {e}")
    
    async def _handle_tool_response(self, data: dict):
        """Handle tool response from Electron"""
        call_id = data.get("call_id")
        result = data.get("result")
        error = data.get("error")
        
        logger.info(f"[Server] Processing tool_response: call_id={call_id[:8] if call_id else 'None'}..., has_handler={call_id in self._tool_response_handlers if call_id else False}")
        
        if call_id and call_id in self._tool_response_handlers:
            handler = self._tool_response_handlers[call_id]
            try:
                handler(result, error)
                logger.info(f"[Server] Tool handler called for {call_id[:8]}...")
            except Exception as e:
                logger.error(f"[Server] Tool response handler error: {e}")
        else:
            logger.warning(f"[Server] No handler found for tool_response: {call_id}")
    
    async def send_tool_call(self, tool_name: str, args: dict, timeout: float = 30.0) -> Any:
        """
        Send tool call to Electron and wait for response

        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments
            timeout: Timeout in seconds

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool_name is not in ALLOWED_TOOLS whitelist
        """
        # Security: Validate tool name against whitelist
        if tool_name not in self.ALLOWED_TOOLS:
            logger.warning(f"[Server] Blocked tool call to non-whitelisted tool: {tool_name}")
            raise ValueError(f"Tool '{tool_name}' is not allowed")

        import uuid
        call_id = str(uuid.uuid4())
        
        # Create Future to wait for response
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def on_response(result, error):
            logger.info(f"[Server] on_response called: done={future.done()}, error={error}")
            if not future.done():
                if error:
                    logger.info(f"[Server] Setting future exception: {error}")
                    future.set_exception(Exception(error))
                else:
                    logger.info(f"[Server] Setting future result: {type(result)}")
                    future.set_result(result)
            else:
                logger.warning(f"[Server] Future already done, ignoring response")
        
        # Register response handler with timestamp for cleanup
        import time
        self._tool_response_handlers[call_id] = on_response
        self._tool_handler_timestamps[call_id] = time.time()

        try:
            # Send tool call to all clients (Electron will execute)
            tool_msg = {
                "type": "tool_call",
                "call_id": call_id,
                "tool_name": tool_name,
                "args": args,
            }
            logger.info(f"[Server] Sending tool_call: {tool_name} (call_id: {call_id[:8]}...)")
            await self.broadcast(tool_msg)
            logger.info(f"[Server] Tool call broadcast complete: {tool_name}")
            
            # Wait for response
            logger.info(f"[Server] Waiting for future (timeout={timeout}s)...")
            result = await asyncio.wait_for(future, timeout=timeout)
            logger.info(f"[Server] Future resolved! Result type: {type(result)}")
            return result
            
        except asyncio.TimeoutError:
            raise Exception(f"Tool call timeout: {tool_name}")
        finally:
            # Clean up handler and timestamp
            self._tool_response_handlers.pop(call_id, None)
            self._tool_handler_timestamps.pop(call_id, None)

    async def send_cdp_command(self, method: str, params: dict = None, timeout: float = 30.0) -> dict:
        """
        Send CDP command and wait for response (for Python internal calls)
        
        Args:
            method: CDP command method name
            params: Command parameters
            timeout: Timeout in seconds
            
        Returns:
            CDP command response
        """
        import uuid
        request_id = str(uuid.uuid4())
        
        # Create Future to wait for response
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def on_response(data):
            if not future.done():
                error = data.get("error")
                if error:
                    future.set_exception(Exception(error))
                else:
                    future.set_result(data.get("result"))
        
        # Register response handler with timestamp for cleanup
        import time
        self._cdp_response_handlers[request_id] = on_response
        self._cdp_handler_timestamps[request_id] = time.time()

        try:
            # Send command to all clients (Electron will handle cdp_command)
            await self.broadcast({
                "type": "cdp_command",
                "data": {
                    "requestId": request_id,
                    "method": method,
                    "params": params or {},
                }
            })

            # Wait for response
            result = await asyncio.wait_for(future, timeout=timeout)
            return result

        except asyncio.TimeoutError:
            raise Exception(f"CDP command timeout: {method}")
        finally:
            # Clean up handler and timestamp
            self._cdp_response_handlers.pop(request_id, None)
            self._cdp_handler_timestamps.pop(request_id, None)
    
    async def _send_full_status(self, websocket):
        """Send full status to a specific client"""
        status = FullStatus(
            agent=self._agent_status,
            learning=self._learning_status,
            knowledge=self._knowledge_stats,
        )
        await websocket.send(json.dumps(status.to_dict()))
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self._clients:
            logger.warning(f"[Server] No clients to broadcast: {message.get('type')}")
            return
        
        msg_str = json.dumps(message)
        msg_type = message.get('type', 'unknown')
        logger.debug(f"[Server] Broadcasting {msg_type} to {len(self._clients)} clients")
        
        results = await asyncio.gather(
            *[client.send(msg_str) for client in self._clients],
            return_exceptions=True
        )
        
        # Check for any send errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[Server] Broadcast error to client {i}: {result}")
    
    async def broadcast_status(self):
        """Broadcast current status to all clients"""
        status = FullStatus(
            agent=self._agent_status,
            learning=self._learning_status,
            knowledge=self._knowledge_stats,
        )
        await self.broadcast(status.to_dict())
    
    # Status update methods
    
    def update_agent(
        self,
        state: str = None,
        task: str = None,
        step: int = None,
        max_steps: int = None,
        last_action: str = None,
        error: str = None,
        progress: float = None,
    ):
        """Update agent status"""
        if state is not None:
            self._agent_status.state = state
        if task is not None:
            self._agent_status.task = task
        if step is not None:
            self._agent_status.step = step
            if self._agent_status.max_steps > 0:
                self._agent_status.progress = step / self._agent_status.max_steps
        if max_steps is not None:
            self._agent_status.max_steps = max_steps
        if last_action is not None:
            self._agent_status.last_action = last_action
        if error is not None:
            self._agent_status.error = error
        if progress is not None:
            self._agent_status.progress = progress
    
    def update_learning(
        self,
        state: str = None,
        action_count: int = None,
    ):
        """Update learning status"""
        if state is not None:
            self._learning_status.state = state
            if state == "saved":
                self._learning_status.last_saved = datetime.now().isoformat()
        if action_count is not None:
            self._learning_status.action_count = action_count
    
    def update_knowledge(
        self,
        trajectory_count: int = None,
        domain_count: int = None,
        domains: list = None,
    ):
        """Update knowledge stats"""
        if trajectory_count is not None:
            self._knowledge_stats.trajectory_count = trajectory_count
        if domain_count is not None:
            self._knowledge_stats.domain_count = domain_count
        if domains is not None:
            self._knowledge_stats.domains = domains
    
    async def broadcast_frame(
        self,
        image_base64: str,
        action: str = None,
        step: int = 0,
        total_steps: int = 0,
    ):
        """
        Broadcast screenshot frame to all clients.
        
        Used by screenshot streamer to send real-time browser visuals.
        
        Args:
            image_base64: JPEG image as base64 string
            action: Current action description
            step: Current step number
            total_steps: Total steps in task
        """
        if not self._clients:
            return
        
        message = {
            "type": "frame",
            "data": {
                "image": image_base64,
                "action": action,
                "step": step,
                "total_steps": total_steps,
            }
        }
        
        msg_str = json.dumps(message)
        await asyncio.gather(
            *[client.send(msg_str) for client in self._clients],
            return_exceptions=True
        )
    
    async def broadcast_action(self, action: str, step: int = 0, total_steps: int = 0):
        """Broadcast action update (without frame)"""
        message = {
            "type": "action",
            "data": {
                "action": action,
                "step": step,
                "total_steps": total_steps,
            }
        }
        await self.broadcast(message)
    
    async def request_confirmation(
        self,
        title: str,
        question: str,
        answer: str,
        execution_count: int = 1,
        source_file: str = "",
        timeout: float = 300.0,  # 5 minutes
    ) -> bool:
        """
        Request user confirmation via UI dialog.
        
        Sends a confirm_request message to the frontend and waits for confirm_response.
        
        Args:
            title: Dialog title
            question: The question/field being confirmed
            answer: The proposed answer to confirm
            execution_count: Execute次数（1 = First次，2+ = Aftercontinued）
            source_file: 来SourceFilePath
            timeout: Timeout in seconds
            
        Returns:
            True if user confirmed, False if cancelled or timeout
        """
        import uuid
        import time
        
        request_id = str(uuid.uuid4())
        
        # Send confirmation request to frontend
        await self.broadcast({
            "type": "confirm_request",
            "data": {
                "request_id": request_id,
                "title": title,
                "question": question,
                "answer": answer,
                "execution_count": execution_count,
                "source_file": source_file,
            }
        })
        
        logger.info(f"[Server] Confirmation request sent: {request_id[:8]}...")
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if request_id in self.confirm_responses:
                response = self.confirm_responses.pop(request_id)
                confirmed = response.get("confirmed", False)
                logger.info(f"[Server] Confirmation result: {request_id[:8]}... = {confirmed}")
                return confirmed
            
            await asyncio.sleep(0.1)  # Check every 100ms
        
        logger.warning(f"[Server] Confirmation timeout: {request_id[:8]}...")
        return False
    
    async def broadcast_workflow_status(self, message: str):
        """
        Broadcast workflow status message to frontend.
        
        Args:
            message: Status message to display
        """
        await self.broadcast({
            "type": "workflow_status",
            "data": {
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
        })
    
    # ========================================================================
    # Stream Protocol Methods (v2.0)
    # ========================================================================
    
    async def broadcast_stream_chunk(self, chunk: "StreamChunk"):
        """
        Broadcast a stream chunk to all clients.
        
        This is the new streaming protocol for real-time AI interaction.
        
        Args:
            chunk: StreamChunk object containing type and data
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            logger.warning("[Server] Stream protocol not available")
            return
        
        if not self._clients:
            return
        
        # Send JSON serialized chunk
        msg_str = chunk.to_json()
        await asyncio.gather(
            *[client.send(msg_str) for client in self._clients],
            return_exceptions=True
        )
    
    async def stream_thinking(
        self,
        message_id: str,
        text: str,
        is_complete: bool = False,
        duration_ms: Optional[int] = None,
    ):
        """
        Send thinking/reasoning chunk (Chain of Thought).
        
        Args:
            message_id: Message ID for this conversation turn
            text: Thinking text content
            is_complete: Whether thinking is complete
            duration_ms: Total thinking duration (if complete)
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        from engine.stream.protocol import ThinkingContent
        
        chunk = StreamChunk(
            type=ChunkType.THINKING,
            message_id=message_id,
            data=ThinkingContent(
                text=text,
                is_complete=is_complete,
                duration_ms=duration_ms,
            ),
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_content(self, message_id: str, text: str):
        """
        Send content chunk (streaming response text).
        
        Args:
            message_id: Message ID
            text: Content text (appended to existing content)
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        chunk = StreamChunk(
            type=ChunkType.CONTENT,
            message_id=message_id,
            data={"text": text},
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_tool_start(
        self,
        message_id: str,
        tool_id: str,
        tool_name: str,
        tool_args: dict = None,
    ):
        """
        Send tool call start notification.
        
        Args:
            message_id: Message ID
            tool_id: Unique tool call ID
            tool_name: Name of the tool being called
            tool_args: Optional tool arguments (for frontend visualization)
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        data = {
                "id": tool_id,
                "name": tool_name,
                "status": ToolCallStatus.GENERATING.value,
        }
        if tool_args:
            data["args"] = tool_args
        
        chunk = StreamChunk(
            type=ChunkType.TOOL_START,
            message_id=message_id,
            data=data,
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_tool_args(
        self,
        message_id: str,
        tool_id: str,
        args_text: str,
        is_complete: bool = False,
    ):
        """
        Send tool arguments chunk (streaming).
        
        Args:
            message_id: Message ID
            tool_id: Tool call ID
            args_text: Arguments text chunk (appended)
            is_complete: Whether arguments are complete
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        chunk = StreamChunk(
            type=ChunkType.TOOL_ARGS,
            message_id=message_id,
            data={
                "toolId": tool_id,
                "argsText": args_text,
                "isComplete": is_complete,
                "status": ToolCallStatus.GENERATED.value if is_complete else ToolCallStatus.GENERATING.value,
            },
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_tool_result(
        self,
        message_id: str,
        tool_id: str,
        result: Any = None,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ):
        """
        Send tool execution result.
        
        Args:
            message_id: Message ID
            tool_id: Tool call ID
            result: Execution result (if success)
            error: Error message (if failed)
            duration_ms: Execution duration
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        status = ToolCallStatus.ERRORED if error else ToolCallStatus.DONE
        
        chunk = StreamChunk(
            type=ChunkType.TOOL_RESULT,
            message_id=message_id,
            data={
                "toolId": tool_id,
                "status": status.value,
                "result": result,
                "error": error,
                "durationMs": duration_ms,
            },
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_artifact(
        self,
        message_id: str,
        artifact_id: str,
        title: str,
        content: str,
        artifact_type: str = "file",
        language: Optional[str] = None,
        file_path: Optional[str] = None,
    ):
        """
        Send artifact (generated file/output).
        
        Args:
            message_id: Message ID
            artifact_id: Unique artifact ID
            title: Artifact title
            content: Artifact content
            artifact_type: Type (code, file, chart, table, markdown, json)
            language: Programming language (for code)
            file_path: File path (for file artifacts)
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        chunk = StreamChunk(
            type=ChunkType.ARTIFACT,
            message_id=message_id,
            data={
                "id": artifact_id,
                "type": artifact_type,
                "title": title,
                "content": content,
                "language": language,
                "filePath": file_path,
                "preview": True,
            },
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_plan(
        self,
        message_id: str,
        plan_id: str,
        title: str,
        steps: list,
    ):
        """
        Send execution plan.
        
        Args:
            message_id: Message ID
            plan_id: Unique plan ID
            title: Plan title
            steps: List of step dicts with 'title' and 'description'
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        formatted_steps = [
            {
                "id": f"{plan_id}-{i}",
                "index": i,
                "title": step.get("title", f"Step {i+1}"),
                "description": step.get("description", ""),
                "status": "pending",
                "progress": 0.0,
            }
            for i, step in enumerate(steps)
        ]
        
        chunk = StreamChunk(
            type=ChunkType.PLAN_UPDATE,
            message_id=message_id,
            data={
                "id": plan_id,
                "title": title,
                "steps": formatted_steps,
                "currentStep": 0,
                "progress": 0.0,
            },
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_plan_step_update(
        self,
        message_id: str,
        plan_id: str,
        step_index: int,
        status: str,
        progress: float = 0.0,
        result: Optional[str] = None,
    ):
        """
        Update plan step status.
        
        Args:
            message_id: Message ID
            plan_id: Plan ID
            step_index: Step index (0-based)
            status: Step status (pending, in_progress, completed, failed)
            progress: Step progress (0-1)
            result: Step result text
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        chunk = StreamChunk(
            type=ChunkType.PLAN_UPDATE,
            message_id=message_id,
            data={
                "id": plan_id,
                "stepUpdate": {
                    "index": step_index,
                    "status": status,
                    "progress": progress,
                    "result": result,
                },
            },
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_confirm(
        self,
        message_id: str,
        message: str,
        options: list = None,
        default: str = "continue",
    ):
        """
        Request user confirmation.
        
        Args:
            message_id: Message ID
            message: Confirmation message
            options: Available options (default: ["continue", "cancel"])
            default: Default option
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        chunk = StreamChunk(
            type=ChunkType.CONFIRM,
            message_id=message_id,
            data={
                "message": message,
                "options": options or ["continue", "cancel"],
                "default": default,
            },
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_error(
        self,
        message_id: str,
        error_message: str,
        details: Optional[str] = None,
    ):
        """
        Send error notification.
        
        Args:
            message_id: Message ID
            error_message: Error message
            details: Error details
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        chunk = StreamChunk(
            type=ChunkType.ERROR,
            message_id=message_id,
            data={
                "message": error_message,
                "details": details,
            },
        )
        await self.broadcast_stream_chunk(chunk)
    
    async def stream_complete(
        self,
        message_id: str,
        summary: Optional[str] = None,
    ):
        """
        Send completion notification.
        
        Args:
            message_id: Message ID
            summary: Completion summary
        """
        if not STREAM_PROTOCOL_AVAILABLE:
            return
        
        chunk = StreamChunk(
            type=ChunkType.COMPLETE,
            message_id=message_id,
            data={
                "summary": summary,
            },
        )
        await self.broadcast_stream_chunk(chunk)
    
    # ========================================================================
    # Visualization Events (for AI operation visualization panel)
    # ========================================================================
    
    async def viz_cursor_move(
        self,
        x: float,
        y: float,
        duration: float = 0.8,
    ):
        """
        Move AI cursor to target position.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Animation duration in seconds
        """
        await self.broadcast({
            "type": "cursor_move",
            "data": {
                "x": x,
                "y": y,
                "duration": duration,
            }
        })
    
    async def viz_cursor_click(self):
        """Trigger click animation on AI cursor."""
        await self.broadcast({"type": "cursor_click"})
    
    async def viz_cursor_type(self):
        """Start typing animation on AI cursor."""
        await self.broadcast({"type": "cursor_type"})
    
    async def viz_cursor_stop_type(self):
        """Stop typing animation on AI cursor."""
        await self.broadcast({"type": "cursor_stop_type"})
    
    async def viz_highlight(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        label: Optional[str] = None,
    ):
        """
        Highlight a rectangular area on the simulated screen.
        
        Args:
            x: X coordinate of highlight area
            y: Y coordinate of highlight area
            width: Width of highlight area
            height: Height of highlight area
            label: Optional label text
        """
        await self.broadcast({
            "type": "highlight",
            "data": {
                "rect": {"x": x, "y": y, "width": width, "height": height},
                "label": label,
            }
        })
    
    async def viz_highlight_hide(self):
        """Hide the current highlight."""
        await self.broadcast({"type": "highlight_hide"})
    
    async def viz_screen_glow(self, intensity: str = "medium"):
        """
        Set screen glow effect.
        
        Args:
            intensity: Glow intensity (off, low, medium, high, success, error)
        """
        await self.broadcast({
            "type": "screen_glow",
            "data": {"intensity": intensity}
        })
    
    async def viz_screen_glow_stop(self):
        """Stop screen glow effect."""
        await self.broadcast({"type": "screen_glow_stop"})
    
    async def viz_task_start(
        self,
        max_steps: int = 0,
        url: Optional[str] = None,
    ):
        """
        Notify visualization panel that a task is starting.
        
        Args:
            max_steps: Maximum number of steps (for progress indicator)
            url: URL to display in simulated browser
        """
        await self.broadcast({
            "type": "task_start",
            "data": {
                "max_steps": max_steps,
                "url": url,
            }
        })
    
    async def viz_step_start(self, step: int):
        """
        Notify visualization panel that a step is starting.
        
        Args:
            step: Step index (0-based)
        """
        await self.broadcast({
            "type": "step_start",
            "data": {"step": step}
        })
    
    async def viz_step_complete(self, step: int, success: bool = True):
        """
        Notify visualization panel that a step completed.
        
        Args:
            step: Step index (0-based)
            success: Whether step completed successfully
        """
        await self.broadcast({
            "type": "step_complete",
            "data": {"step": step, "success": success}
        })
    
    async def viz_task_complete(self):
        """Notify visualization panel that task completed successfully."""
        await self.broadcast({"type": "task_complete"})
    
    async def viz_task_error(self):
        """Notify visualization panel that task failed."""
        await self.broadcast({"type": "task_error"})
    
    # ========================================================================
    # Performance Metrics (A3.1 - TTFT Monitoring)
    # ========================================================================
    
    async def broadcast_performance(
        self,
        message_id: str,
        ttft_ms: Optional[float] = None,
        total_time_ms: Optional[float] = None,
        tokens_generated: int = 0,
        tool_calls: int = 0,
        iterations: int = 0,
    ):
        """
        Broadcast performance metrics to all clients.
        
        Args:
            message_id: Message ID for this task
            ttft_ms: Time to First Token in milliseconds
            total_time_ms: Total execution time in milliseconds
            tokens_generated: Number of tokens generated
            tool_calls: Number of tool calls made
            iterations: Number of ReAct iterations
        """
        metrics = PerformanceMetrics(
            ttft_ms=ttft_ms,
            total_time_ms=total_time_ms,
            tokens_generated=tokens_generated,
            tool_calls=tool_calls,
            iterations=iterations,
        )
        
        message = {
            "type": "performance",
            "message_id": message_id,
            "data": asdict(metrics),
        }
        
        await self.broadcast(message)
        
        # Also log for monitoring
        if ttft_ms is not None and total_time_ms is not None:
            logger.info(f"[Perf] TTFT: {ttft_ms:.0f}ms | Total: {total_time_ms:.0f}ms | Iterations: {iterations} | Tools: {tool_calls}")


# Global server instance
_server: Optional[StatusServer] = None


def get_server() -> StatusServer:
    """Get or create global server instance"""
    global _server
    if _server is None:
        _server = StatusServer()
    return _server


async def start_server(host: str = "localhost", port: int = 8765) -> StatusServer:
    """Start global server"""
    global _server
    _server = StatusServer(host, port)
    await _server.start()
    return _server


# Quick test
if __name__ == "__main__":
    async def test_server():
        print("=" * 50)
        print("WebSocket Server Test")
        print("=" * 50)
        
        if not WEBSOCKETS_AVAILABLE:
            print("[ERROR] websockets not installed!")
            print("Run: pip install websockets")
            return
        
        server = StatusServer()
        await server.start()
        
        print(f"\n[Server] Running at ws://{server.host}:{server.port}")
        print("[Server] Connect with a WebSocket client to test")
        print("[Server] Press Ctrl+C to stop\n")
        
        # Simulate status updates
        try:
            for i in range(100):
                await asyncio.sleep(2)
                
                # Update agent status
                server.update_agent(
                    state="thinking" if i % 2 == 0 else "acting",
                    step=i % 5,
                    task="Demo task",
                )
                
                # Broadcast
                await server.broadcast_status()
                print(f"[Server] Broadcast #{i+1} (clients: {server.client_count})")
                
        except KeyboardInterrupt:
            print("\n[Server] Stopping...")
        
        await server.stop()
        print("[Server] Done")
    
    asyncio.run(test_server())

