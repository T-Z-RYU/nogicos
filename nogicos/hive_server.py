# -*- coding: utf-8 -*-
"""
NogicOS Hive Server - V2 Architecture

Simplified HTTP + WebSocket API using Pure ReAct Agent.

Architecture:
    HTTP (8080)          WebSocket (8765)
        |                     |
        v                     v
    /v2/execute  ───────►  broadcast status
    /v2/tools                 |
    /health                   v
                         Electron UI

Usage:
    python hive_server.py
"""

# [Fix] Ensure user-installed packages can be found
import sys
import os
_user_site = os.path.expanduser("~\\AppData\\Roaming\\Python\\Python314\\site-packages")
if _user_site not in sys.path:
    sys.path.insert(0, _user_site)

# [Debug] Enable faulthandler to capture Segmentation Fault stack traces
import faulthandler
faulthandler.enable(file=sys.stderr, all_threads=True)

import warnings
import asyncio
import os
import sys
import json
import time
import logging
import aiohttp
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

# Filter known deprecation warnings
warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality isn't compatible")
warnings.filterwarnings("ignore", message="ForwardRef._evaluate is a private API")
warnings.filterwarnings("ignore", message="websockets.server.WebSocketServerProtocol is deprecated")
warnings.filterwarnings("ignore", message="websockets.legacy is deprecated")

# Ensure UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Setup logging
from engine.observability import setup_logging, get_logger
setup_logging(level="INFO")
logger = get_logger("hive_server")

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import Response, StreamingResponse, JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    logger.error("FastAPI not installed. Run: pip install fastapi uvicorn")
    sys.exit(1)

# ChatKit Server (optional - graceful degradation if not available)
try:
    from chatkit.server import StreamingResult
    from engine.server.chatkit_server import create_chatkit_server, NogicOSChatServer
    CHATKIT_AVAILABLE = True
except ImportError:
    CHATKIT_AVAILABLE = False
    StreamingResult = None
    create_chatkit_server = None
    NogicOSChatServer = None
    logger.warning("ChatKit SDK not available. Install with: pip install openai-chatkit")

# V2 imports
from engine.server.websocket import StatusServer
from engine.agent.react_agent import ReActAgent
from engine.tools import create_full_registry
from engine.watchdog import start_watchdog, get_watchdog, ConnectionState
from engine.knowledge.store import get_session_store

# Phase 6: HostAgent removed, replaced by UnifiedAgentManager
HOST_AGENT_AVAILABLE = False
from engine.agent.events import EventType, AgentEvent
from engine.agent.event_bus import get_event_bus
from engine.agent.state_manager import TaskStatus

# Phase 7: UnifiedAgentManager - unified Agent entry point
try:
    from engine.agent.unified_manager import UnifiedAgentManager, get_unified_manager
    UNIFIED_AGENT_AVAILABLE = True
    logger.info("UnifiedAgentManager available - using ReActAgent as core")
except ImportError as e:
    UNIFIED_AGENT_AVAILABLE = False
    UnifiedAgentManager = None
    get_unified_manager = None
    logger.warning(f"UnifiedAgentManager not available: {e}")


# ============================================================================
# Request/Response Models
# ============================================================================

class ExecuteRequest(BaseModel):
    """Task execution request"""
    task: Optional[str] = None      # New field name (preferred)
    message: Optional[str] = None   # Legacy field name (alias)
    session_id: str = "default"
    max_steps: int = 20
    mode: str = "agent"             # Agent mode: "agent", "ask", "plan"
    confirmed_plan: Optional[dict] = None  # Confirmed plan for Plan mode execution
    
    @property
    def task_content(self) -> str:
        """Get the task content, supporting both 'task' and 'message' fields"""
        return self.task or self.message or ""


# ============================================================================
# Phase 6: Agent Control API Models
# ============================================================================

class AgentStartRequest(BaseModel):
    """Agent task start request - Phase 6"""
    task: str                          # Task description
    target_hwnds: Optional[List[int]] = None  # Target window handles list
    max_iterations: int = 50           # Maximum iterations
    session_id: str = "default"        # Session ID
    
    model_config = {"extra": "allow"}  # Allow extra fields


class AgentStopRequest(BaseModel):
    """Agent task stop request - Phase 6"""
    task_id: str
    reason: str = "User requested"


class AgentResumeRequest(BaseModel):
    """Agent task resume request - Phase 6"""
    task_id: str


class AgentStatusResponse(BaseModel):
    """Agent status response - Phase 6"""
    task_id: str
    status: str                        # idle, running, paused, completed, failed, etc.
    iteration: int = 0
    max_iterations: int = 50
    current_action: Optional[str] = None
    error: Optional[str] = None
    progress: float = 0.0              # 0.0 - 1.0
    elapsed_seconds: float = 0.0
    tool_calls_count: int = 0


class AgentEventType(str):
    """Agent event types for WebSocket streaming"""
    THINKING = "thinking"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    PROGRESS = "progress"
    CONFIRM_REQUIRED = "confirm_required"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"


class ExecuteResponse(BaseModel):
    """Task execution response"""
    success: bool
    response: str
    session_id: str
    time_seconds: float
    error: Optional[str] = None


class StatusResponse(BaseModel):
    """Server status response"""
    status: str
    version: str
    engine_ready: bool


class StatsResponse(BaseModel):
    """Server statistics"""
    tasks_executed: int
    tasks_succeeded: int
    tasks_failed: int
    uptime_seconds: float


# ============================================================================
# Engine - Simplified V2
# ============================================================================

class NogicEngine:
    """Simplified engine for V2 architecture"""

    def __init__(self):
        self.status_server: Optional[StatusServer] = None
        self.chatkit_server: Optional["NogicOSChatServer"] = None  # ChatKit Server
        self.agent: Optional[ReActAgent] = None  # Reusable agent instance
        self._agent_lock = asyncio.Lock()  # Lock for agent access
        self._executing = False
        self._current_task: Optional[str] = None
        self._stats = {
            "executed": 0,
            "succeeded": 0,
            "failed": 0,
        }
        self._start_time = time.time()

    async def get_agent(self) -> ReActAgent:
        """Get agent instance with lock protection for thread safety"""
        async with self._agent_lock:
            if self.agent is None:
                self.agent = ReActAgent(
                    status_server=self.status_server,
                    max_iterations=20,
                )
            return self.agent

    async def start_websocket(self):
        """Start WebSocket server"""
        self.status_server = StatusServer(port=8765)
        await self.status_server.start()
        logger.info("WebSocket server started on port 8765")
        
        # Initialize reusable ReAct Agent (avoids 1-2s init overhead per request)
        logger.info("Initializing ReAct Agent...")
        init_start = time.time()
        self.agent = ReActAgent(
            status_server=self.status_server,
            max_iterations=20,
        )
        logger.info(f"ReAct Agent initialized in {time.time() - init_start:.2f}s")
        
        # Initialize ChatKit Server
        if CHATKIT_AVAILABLE and create_chatkit_server:
            self.chatkit_server = create_chatkit_server(status_server=self.status_server)
            if self.chatkit_server:
                logger.info("ChatKit server initialized")
    
    async def stop_websocket(self):
        """Stop WebSocket server"""
        if self.status_server:
            await self.status_server.stop()
            logger.info("WebSocket server stopped")
    
    async def execute(self, request: ExecuteRequest) -> ExecuteResponse:
        """Execute task using ReAct Agent with mode support"""
        # [P0-5 FIX] Use lock for thread-safe execution check with guaranteed cleanup
        async with self._agent_lock:
            if self._executing:
                raise HTTPException(status_code=429, detail="Another task is executing")
            self._executing = True

        task_content = request.task_content
        self._current_task = task_content[:100]
        start_time = time.time()

        # [P0-5 FIX] Wrap everything in try-finally to ensure state cleanup
        try:
            return await self._execute_task(request, task_content, start_time)
        finally:
            # [P0-5 FIX] Always reset execution state, even on unexpected errors
            self._executing = False
            self._current_task = None

    async def _execute_task(self, request: ExecuteRequest, task_content: str, start_time: float) -> ExecuteResponse:
        """Internal task execution logic - separated for clean error handling"""
        
        # Parse mode
        from engine.agent.modes import AgentMode
        try:
            mode = AgentMode(request.mode)
        except ValueError:
            mode = AgentMode.AGENT
        
        logger.info(f"[Engine] Executing in {mode.value} mode: {task_content[:50]}...")
        
        # Parse confirmed plan if provided (for Plan mode execution)
        confirmed_plan = None
        if request.confirmed_plan and mode == AgentMode.AGENT:
            # User confirmed a plan, execute it
            from engine.agent.planner import Plan, PlanStep
            try:
                plan_data = request.confirmed_plan
                steps = [s.get("description", "") for s in plan_data.get("steps", [])]
                confirmed_plan = Plan(
                    steps=steps,
                    detailed_steps=[
                        PlanStep(
                            description=s.get("description", ""),
                            suggested_tool=s.get("tool"),
                        )
                        for s in plan_data.get("steps", [])
                    ],
                )
                logger.info(f"[Engine] Executing confirmed plan with {len(steps)} steps")
            except Exception as e:
                logger.warning(f"[Engine] Failed to parse confirmed plan: {e}")
        
        try:
            # [P1 FIX] Reuse existing agent instance instead of creating new one each time
            # This saves 1-2s initialization overhead per request
            agent = await self.get_agent()
            # Update max_iterations if different from default
            if agent.max_iterations != request.max_steps:
                agent.max_iterations = request.max_steps

            # Execute based on mode
            if confirmed_plan:
                # Execute confirmed plan
                result = await agent.run(
                    task=task_content,
                    session_id=request.session_id,
                    mode=AgentMode.AGENT,
                    confirmed_plan=confirmed_plan,
                )
            elif mode == AgentMode.PLAN:
                # Plan mode: generate plan without executing
                result = await agent.run(
                    task=task_content,
                    session_id=request.session_id,
                    mode=mode,
                )
            elif mode == AgentMode.ASK:
                # Ask mode: read-only exploration
                result = await agent.run(
                    task=task_content,
                    session_id=request.session_id,
                    mode=mode,
                )
            else:
                # Agent mode: full execution
                result = await agent.run_with_planning(
                    task=task_content,
                    session_id=request.session_id,
                )
            
            elapsed = time.time() - start_time
            
            # Update stats
            self._stats["executed"] += 1
            if result.success:
                self._stats["succeeded"] += 1
            else:
                self._stats["failed"] += 1
            
            return ExecuteResponse(
                success=result.success,
                response=result.response,
                session_id=request.session_id,
                time_seconds=elapsed,
                error=result.error,
            )
            
        except Exception as e:
            logger.error(f"Execution error: {e}", exc_info=True)
            self._stats["executed"] += 1
            self._stats["failed"] += 1
            return ExecuteResponse(
                success=False,
                response="",
                session_id=request.session_id,
                time_seconds=time.time() - start_time,
                error=str(e),
            )
        # [P0-5 FIX] finally block removed - cleanup now handled in outer execute() method
    
    def get_stats(self) -> StatsResponse:
        """Get server statistics"""
        return StatsResponse(
            tasks_executed=self._stats["executed"],
            tasks_succeeded=self._stats["succeeded"],
            tasks_failed=self._stats["failed"],
            uptime_seconds=time.time() - self._start_time,
        )


# Global engine instance
engine: Optional[NogicEngine] = None
server_start_time = time.time()


# ============================================================================
# Phase 6: Global HostAgent Manager (Review Fixed v2)
# ============================================================================

# Phase 6 Fix v2: Enhanced security with HMAC, Origin validation, IP whitelist
from collections import defaultdict
from dataclasses import dataclass, field
import uuid as uuid_module
import hmac
import hashlib


# ============================================================================
# Event Priority System (for backpressure handling)
# ============================================================================

class EventPriority:
    """Event priority levels - High priority events are never dropped during backpressure"""
    CRITICAL = 0   # confirm_required, failed, error - never dropped
    HIGH = 1       # completed, stopped, cancelled, needs_help
    NORMAL = 2     # tool_start, tool_end, progress
    LOW = 3        # thinking, heartbeat, backpressure_warning


# Event type to priority level mapping
EVENT_PRIORITY_MAP: Dict[str, int] = {
    # Critical - never dropped
    "confirm_required": EventPriority.CRITICAL,
    "failed": EventPriority.CRITICAL,
    "error": EventPriority.CRITICAL,
    "auth_error": EventPriority.CRITICAL,
    
    # High - only dropped in extreme situations
    "completed": EventPriority.HIGH,
    "stopped": EventPriority.HIGH,
    "cancelled": EventPriority.HIGH,
    "needs_help": EventPriority.HIGH,
    "started": EventPriority.HIGH,
    "resumed": EventPriority.HIGH,
    "connected": EventPriority.HIGH,
    "connection_closing": EventPriority.HIGH,
    "pending_confirmations": EventPriority.HIGH,
    
    # Normal - can be dropped
    "tool_start": EventPriority.NORMAL,
    "tool_end": EventPriority.NORMAL,
    "progress": EventPriority.NORMAL,
    "status": EventPriority.NORMAL,
    
    # Low - dropped first
    "thinking": EventPriority.LOW,
    "heartbeat": EventPriority.LOW,
    "backpressure_warning": EventPriority.LOW,
}


def _get_default_event_priority() -> int:
    """
    Get default event priority level - Review Fix v6
    
    Configurable via environment variable NOGICOS_DEFAULT_EVENT_PRIORITY:
    - CRITICAL: never dropped
    - HIGH: only dropped in extreme situations (default)
    - NORMAL: can be dropped
    - LOW: dropped first
    """
    priority_str = os.environ.get("NOGICOS_DEFAULT_EVENT_PRIORITY", "HIGH").upper()
    priority_map = {
        "CRITICAL": EventPriority.CRITICAL,
        "HIGH": EventPriority.HIGH,
        "NORMAL": EventPriority.NORMAL,
        "LOW": EventPriority.LOW,
    }
    return priority_map.get(priority_str, EventPriority.HIGH)


def get_event_priority(event_type: str) -> int:
    """
    Get event priority level - Review Fix v6
    
    Unregistered event types use NOGICOS_DEFAULT_EVENT_PRIORITY value (default HIGH)
    """
    return EVENT_PRIORITY_MAP.get(event_type, _get_default_event_priority())


# ============================================================================
# Enhanced Rate Limiter with IP Whitelist and Logging
# ============================================================================

@dataclass
class RateLimitState:
    """Rate limit state"""
    requests: List[float] = field(default_factory=list)
    blocked_count: int = 0
    last_blocked_at: Optional[float] = None
    
    def is_allowed(self, max_requests: int, window_seconds: float) -> bool:
        """Check if request is allowed"""
        now = time.time()
        # Clean up expired records
        self.requests = [t for t in self.requests if now - t < window_seconds]
        if len(self.requests) >= max_requests:
            self.blocked_count += 1
            self.last_blocked_at = now
            return False
        self.requests.append(now)
        return True


class AgentAPIRateLimiter:
    """
    Agent API Rate Limiter - Review Fix v3
    
    Enhanced features:
    - IP whitelist support
    - Log rate limiting (avoid log explosion)
    - Statistics info
    - Optional Redis backend (multi-process/distributed deployment)
    """
    
    def __init__(
        self, 
        max_requests: int = 20, 
        window_seconds: float = 60.0,
        log_interval_seconds: float = 60.0,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.log_interval_seconds = log_interval_seconds
        self._states: Dict[str, RateLimitState] = defaultdict(RateLimitState)
        self._last_log_time: Dict[str, float] = {}
        
        # IP Whitelist
        whitelist_str = os.environ.get("NOGICOS_RATE_LIMIT_WHITELIST", "")
        self._whitelist: set = set(w.strip() for w in whitelist_str.split(",") if w.strip())
        self._whitelist.update({"127.0.0.1", "localhost", "::1"})
        
        # Review Fix v3: Optional Redis backend
        self._redis_client = None
        self._use_redis = False
        redis_url = os.environ.get("NOGICOS_REDIS_URL", "")
        if redis_url:
            try:
                import redis
                self._redis_client = redis.from_url(redis_url)
                self._redis_client.ping()  # Test connection
                self._use_redis = True
                logger.info(f"[RateLimit] Using Redis backend: {redis_url.split('@')[-1]}")
            except ImportError:
                logger.warning("[RateLimit] redis package not installed, using memory backend")
            except Exception as e:
                logger.warning(f"[RateLimit] Redis connection failed: {e}, using memory backend")
    
    def check(self, client_id: str) -> bool:
        """Check if client request is allowed"""
        if client_id in self._whitelist:
            return True
        
        if self._use_redis and self._redis_client:
            return self._check_redis(client_id)
        else:
            return self._check_memory(client_id)
    
    def _check_memory(self, client_id: str) -> bool:
        """In-memory rate check"""
        allowed = self._states[client_id].is_allowed(self.max_requests, self.window_seconds)
        
        if not allowed:
            self._log_blocked(client_id, self._states[client_id].blocked_count)
        
        return allowed
    
    def _check_redis(self, client_id: str) -> bool:
        """Redis rate check (sliding window)"""
        try:
            key = f"nogicos:ratelimit:{client_id}"
            now = time.time()
            window_start = now - self.window_seconds
            
            pipe = self._redis_client.pipeline()
            # Remove expired records
            pipe.zremrangebyscore(key, 0, window_start)
            # Get request count in current window
            pipe.zcard(key)
            # Add current request
            pipe.zadd(key, {str(now): now})
            # Set expiry time
            pipe.expire(key, int(self.window_seconds) + 1)
            
            results = pipe.execute()
            current_count = results[1]
            
            if current_count >= self.max_requests:
                # Remove the just-added request (over limit)
                self._redis_client.zrem(key, str(now))
                
                # Get cumulative blocked count
                blocked_key = f"nogicos:ratelimit:blocked:{client_id}"
                blocked_count = self._redis_client.incr(blocked_key)
                self._redis_client.expire(blocked_key, 3600)  # 1 hour expiry
                
                self._log_blocked(client_id, blocked_count)
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"[RateLimit] Redis error: {e}, falling back to allow")
            return True
    
    def _log_blocked(self, client_id: str, blocked_count: int):
        """Rate-limited logging"""
        now = time.time()
        last_log = self._last_log_time.get(client_id, 0)
        if now - last_log >= self.log_interval_seconds:
            logger.warning(f"[RateLimit] Client {client_id} blocked (total: {blocked_count})")
            self._last_log_time[client_id] = now
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limit statistics - Review Fix v4
        
        Uses SCAN instead of KEYS to avoid blocking Redis
        """
        if self._use_redis and self._redis_client:
            try:
                # Review Fix v4: Use SCAN instead of KEYS to avoid blocking
                total_blocked = 0
                client_count = 0
                cursor = 0
                pattern = "nogicos:ratelimit:blocked:*"
                
                while True:
                    cursor, keys = self._redis_client.scan(
                        cursor=cursor,
                        match=pattern,
                        count=100  # Max 100 per batch
                    )
                    
                    if keys:
                        # Use MGET to batch get values
                        values = self._redis_client.mget(keys)
                        for v in values:
                            if v:
                                total_blocked += int(v)
                        client_count += len(keys)
                    
                    # cursor 0 indicates scan complete
                    if cursor == 0:
                        break
                
                return {
                    "backend": "redis",
                    "total_clients": client_count,
                    "total_blocked_requests": total_blocked,
                    "whitelist_size": len(self._whitelist),
                }
            except Exception:
                pass
        
        total_blocked = sum(s.blocked_count for s in self._states.values())
        return {
            "backend": "memory",
            "total_clients": len(self._states),
            "total_blocked_requests": total_blocked,
            "whitelist_size": len(self._whitelist),
        }


# Global rate limiter for Agent API
_agent_rate_limiter = AgentAPIRateLimiter(max_requests=20, window_seconds=60.0)


# ============================================================================
# Review Fix v7: WebSocket Connection Limiter
# ============================================================================

class WebSocketConnectionLimiter:
    """
    WebSocket Connection Limiter - Review Fix v7
    
    Features:
    - Connection rate limit (prevent connection flooding)
    - Concurrent connection cap (prevent resource exhaustion)
    - Per-IP statistics
    """
    
    def __init__(
        self,
        max_connections_per_ip: int = 10,
        max_total_connections: int = 100,
        connect_rate_limit: int = 5,  # Max connections per minute
        rate_window_seconds: float = 60.0,
    ):
        self.max_connections_per_ip = int(os.environ.get(
            "NOGICOS_WS_MAX_CONN_PER_IP", max_connections_per_ip
        ))
        self.max_total_connections = int(os.environ.get(
            "NOGICOS_WS_MAX_TOTAL_CONN", max_total_connections
        ))
        self.connect_rate_limit = int(os.environ.get(
            "NOGICOS_WS_CONNECT_RATE", connect_rate_limit
        ))
        self.rate_window_seconds = rate_window_seconds
        
        # IP -> active connection count
        self._active_connections: Dict[str, int] = defaultdict(int)
        # IP -> connection timestamp list (for rate limiting)
        self._connect_times: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def try_acquire(self, client_ip: str) -> tuple[bool, str]:
        """
        Try to acquire connection permit
        
        Returns:
            (allowed, error_message)
        """
        async with self._lock:
            now = time.time()
            
            # Check total connection count
            total = sum(self._active_connections.values())
            if total >= self.max_total_connections:
                return False, f"Server connection limit reached ({self.max_total_connections})"
            
            # Check per-IP connection count
            if self._active_connections[client_ip] >= self.max_connections_per_ip:
                return False, f"Per-IP connection limit reached ({self.max_connections_per_ip})"
            
            # Check connection rate
            times = self._connect_times[client_ip]
            # Clean up expired records
            times[:] = [t for t in times if now - t < self.rate_window_seconds]
            
            if len(times) >= self.connect_rate_limit:
                return False, f"Connection rate limit exceeded ({self.connect_rate_limit}/min)"
            
            # Record connection
            self._active_connections[client_ip] += 1
            times.append(now)
            
            return True, ""
    
    async def release(self, client_ip: str):
        """Release connection"""
        async with self._lock:
            if self._active_connections[client_ip] > 0:
                self._active_connections[client_ip] -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics info"""
        return {
            "total_connections": sum(self._active_connections.values()),
            "unique_ips": len([k for k, v in self._active_connections.items() if v > 0]),
            "max_total": self.max_total_connections,
            "max_per_ip": self.max_connections_per_ip,
            "rate_limit": self.connect_rate_limit,
        }


class WebSocketMessageRateLimiter:
    """
    WebSocket Message Rate Limiter - Review Fix v8
    
    Prevents client message flooding, tracks message rate per connection
    """
    
    def __init__(
        self,
        max_messages_per_second: int = 10,
        burst_limit: int = 20,  # Allow short bursts
    ):
        self.max_messages_per_second = int(os.environ.get(
            "NOGICOS_WS_MSG_RATE", max_messages_per_second
        ))
        self.burst_limit = int(os.environ.get(
            "NOGICOS_WS_MSG_BURST", burst_limit
        ))
        
        # connection_id -> (message_times, warning_sent)
        self._message_times: Dict[str, List[float]] = {}
        self._warning_sent: Dict[str, bool] = {}
    
    def register_connection(self, connection_id: str):
        """Register new connection"""
        self._message_times[connection_id] = []
        self._warning_sent[connection_id] = False
    
    def unregister_connection(self, connection_id: str):
        """Unregister connection"""
        self._message_times.pop(connection_id, None)
        self._warning_sent.pop(connection_id, None)
    
    def check_rate(self, connection_id: str) -> tuple[bool, bool, str]:
        """
        Check message rate
        
        Returns:
            (allowed, should_warn, error_message)
            - allowed: whether message is allowed
            - should_warn: whether to send warning (first time approaching limit)
            - error_message: error info
        """
        if connection_id not in self._message_times:
            return True, False, ""
        
        now = time.time()
        times = self._message_times[connection_id]
        
        # Clean up records older than 1 second
        times[:] = [t for t in times if now - t < 1.0]
        
        # Check burst limit (hard limit)
        if len(times) >= self.burst_limit:
            return False, False, f"Message rate limit exceeded ({self.burst_limit}/s burst)"
        
        # Check sustained rate (soft limit, send warning)
        should_warn = False
        if len(times) >= self.max_messages_per_second:
            if not self._warning_sent.get(connection_id, False):
                should_warn = True
                self._warning_sent[connection_id] = True
        else:
            # Rate back to normal, reset warning state
            self._warning_sent[connection_id] = False
        
        # Record message
        times.append(now)
        
        return True, should_warn, ""
    
    def get_stats(self) -> Dict[str, Any]:
        """GetStatisticsInfo"""
        return {
            "active_connections": len(self._message_times),
            "max_rate": self.max_messages_per_second,
            "burst_limit": self.burst_limit,
        }


# Global WebSocket connection limiter
_ws_connection_limiter = WebSocketConnectionLimiter()

# Global WebSocket message rate limiter
_ws_message_limiter = WebSocketMessageRateLimiter()


# ============================================================================
# HMAC Token Generation and Validation for WebSocket
# ============================================================================

# ============================================================================
# Review Fix v3: Separate WS Secret + HTTPS Enforcement
# ============================================================================

def get_ws_secret() -> str:
    """
    Get WebSocket dedicated secret - Review Fix v3
    
    Prioritizes NOGICOS_WS_SECRET, falls back to NOGICOS_API_KEY if not configured
    """
    return os.environ.get("NOGICOS_WS_SECRET") or \
           os.environ.get("NOGICOS_API_KEY") or \
           "default_secret_for_local"


def is_https_required() -> bool:
    """Check if HTTPS/WSS is required"""
    return os.environ.get("NOGICOS_REQUIRE_HTTPS", "").lower() in ("true", "1", "yes")


def _parse_forwarded_proto(headers) -> Optional[str]:
    """
    Parse proxy protocol header - Review Fix v6
    
    Supports:
    - X-Forwarded-Proto: https / wss (common)
    - Forwarded: proto=https / proto=wss (RFC 7239 standard)
    
    Returns:
        Protocol string ("https", "wss" or None)
    """
    # Secure protocol set (Review Fix v6: supports wss)
    secure_protos = {"https", "wss"}
    
    # Prioritize X-Forwarded-Proto (more common)
    x_forwarded = headers.get("X-Forwarded-Proto", "")
    if x_forwarded.lower() in secure_protos:
        return x_forwarded.lower()
    
    # Check RFC 7239 standard Forwarded header
    # Format: Forwarded: for=192.0.2.60;proto=https;by=203.0.113.43
    forwarded = headers.get("Forwarded", "")
    if forwarded:
        # Parse proto=xxx
        for part in forwarded.split(";"):
            part = part.strip()
            if part.lower().startswith("proto="):
                proto = part[6:].strip().strip('"').lower()
                if proto in secure_protos:
                    return proto
    
    return None


def check_secure_connection(request_or_websocket, is_websocket: bool = False) -> tuple[bool, str]:
    """
    Check if connection is secure - Review Fix v5
    
    When NOGICOS_REQUIRE_HTTPS=true, enforces HTTPS/WSS
    
    Check order:
    1. url.scheme (direct connection)
    2. X-Forwarded-Proto / Forwarded header (proxy scenario)
    3. Local connection exemption
    
    Returns:
        (is_secure, error_message)
    """
    if not is_https_required():
        return True, ""
    
    # Get client address (for local exemption)
    client_host = ""
    if hasattr(request_or_websocket, 'client') and request_or_websocket.client:
        client_host = request_or_websocket.client.host or ""
    
    # Check protocol
    if is_websocket:
        # WebSocket: Check url.scheme and proxy headers
        url_scheme = ""
        if hasattr(request_or_websocket, 'url') and request_or_websocket.url:
            url_scheme = getattr(request_or_websocket.url, 'scheme', '') or ""
        
        # wss or upgraded via HTTPS proxy
        if url_scheme in ("wss", "https"):
            return True, ""
        
        # Review Fix v6: Support Forwarded standard header (https and wss)
        forwarded_proto = _parse_forwarded_proto(request_or_websocket.headers)
        if forwarded_proto in ("https", "wss"):
            return True, ""
        
        # Local connections allow non-WSS
        if client_host in ("127.0.0.1", "localhost", "::1"):
            return True, ""
        
        return False, "WSS required for non-local connections"
    else:
        # HTTP: Check scheme
        url_scheme = ""
        if hasattr(request_or_websocket, 'url') and request_or_websocket.url:
            url_scheme = getattr(request_or_websocket.url, 'scheme', '') or ""
        
        if url_scheme == "https":
            return True, ""
        
        # Review Fix v6: Support Forwarded standard header
        forwarded_proto = _parse_forwarded_proto(request_or_websocket.headers)
        if forwarded_proto == "https":
            return True, ""
        
        # Local connections allow non-HTTPS
        if client_host in ("127.0.0.1", "localhost", "::1"):
            return True, ""
        
        return False, "HTTPS required for non-local connections"


def generate_ws_token(task_id: str, expires_in_seconds: int = 300) -> str:
    """
    Generate WebSocket connection token - HMAC + timestamp - Review Fix v3
    
    Uses dedicated WS secret (NOGICOS_WS_SECRET)
    
    Args:
        task_id: Task ID
        expires_in_seconds: Token validity period (seconds)
        
    Returns:
        Format: {timestamp}.{hmac_signature}
    """
    secret = get_ws_secret()
    timestamp = int(time.time()) + expires_in_seconds
    message = f"{task_id}:{timestamp}"
    
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()[:32]
    
    return f"{timestamp}.{signature}"


def verify_ws_token(task_id: str, token: str) -> tuple[bool, str]:
    """
    Verify WebSocket Token - Review Fix v3
    
    Uses dedicated WS secret (NOGICOS_WS_SECRET)
    
    Args:
        task_id: Task ID
        token: Token string
        
    Returns:
        (is_valid, error_message)
    """
    if not token:
        return False, "Missing token"
    
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return False, "Invalid token format"
        
        timestamp_str, signature = parts
        timestamp = int(timestamp_str)
        
        # Check expiry
        if timestamp < time.time():
            return False, "Token expired"
        
        # Verify signature (using dedicated secret)
        secret = get_ws_secret()
        message = f"{task_id}:{timestamp}"
        expected_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()[:32]
        
        if not hmac.compare_digest(signature, expected_signature):
            return False, "Invalid signature"
        
        return True, ""
        
    except (ValueError, TypeError) as e:
        return False, f"Token parse error: {e}"


# ============================================================================
# Enhanced Auth Verification
# ============================================================================

# Allowed Origins for WebSocket (from environment or defaults)
def get_allowed_origins() -> set:
    """Get allowed origins list"""
    origins_str = os.environ.get("NOGICOS_ALLOWED_ORIGINS", "")
    if origins_str:
        return set(origins_str.split(","))
    
    # Default allowed origins
    return {
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "file://",  # Electron
    }


def _get_trusted_proxies() -> set:
    """
    Get trusted proxy IP list - Review Fix v6
    
    Loaded from environment variable NOGICOS_TRUSTED_PROXIES, comma-separated
    Localhost is always trusted by default
    """
    proxies_str = os.environ.get("NOGICOS_TRUSTED_PROXIES", "")
    proxies = set(p.strip() for p in proxies_str.split(",") if p.strip())
    # Always trust localhost
    proxies.update({"127.0.0.1", "localhost", "::1"})
    return proxies


def get_real_client_ip(request_or_websocket) -> str:
    """
    Get real client IP - Review Fix v6
    
    In proxy scenarios, parses X-Forwarded-For / Forwarded header to get real IP
    
    Check order:
    1. X-Forwarded-For (most common)
    2. Forwarded: for=xxx (RFC 7239)
    3. X-Real-IP (Nginx common)
    4. request.client.host (direct connection)
    
    Security measures (Review Fix v6):
    - NOGICOS_TRUST_PROXY=true enables proxy trust
    - NOGICOS_TRUSTED_PROXIES=ip1,ip2 limits trusted proxy IPs
    - Only parses forwarded headers when connection is from trusted proxy
    """
    # Get connection IP
    direct_ip = ""
    if hasattr(request_or_websocket, 'client') and request_or_websocket.client:
        direct_ip = request_or_websocket.client.host or ""
    
    # If proxy trust is not enabled, return connection IP directly
    if os.environ.get("NOGICOS_TRUST_PROXY", "").lower() not in ("true", "1", "yes"):
        return direct_ip or "unknown"
    
    # Review Fix v6: Check if connection is from trusted proxy
    trusted_proxies = _get_trusted_proxies()
    if direct_ip and direct_ip not in trusted_proxies:
        # Connection is not from trusted proxy, ignore forwarded headers (prevent spoofing)
        logger.debug(f"[Security] Ignoring forwarded headers from untrusted IP: {direct_ip}")
        return direct_ip
    
    headers = request_or_websocket.headers
    
    # 1. X-Forwarded-For: client, proxy1, proxy2
    x_forwarded_for = headers.get("X-Forwarded-For", "")
    if x_forwarded_for:
        # Take first one (leftmost is original client)
        client_ip = x_forwarded_for.split(",")[0].strip()
        if client_ip:
            return client_ip
    
    # 2. Forwarded: for="[2001:db8::1]";proto=https
    forwarded = headers.get("Forwarded", "")
    if forwarded:
        for part in forwarded.split(";"):
            part = part.strip()
            if part.lower().startswith("for="):
                # Remove for= and possible quotes/brackets
                client_ip = part[4:].strip().strip('"').strip("[]")
                if client_ip:
                    return client_ip
    
    # 3. X-Real-IP (Nginx)
    x_real_ip = headers.get("X-Real-IP", "")
    if x_real_ip:
        return x_real_ip.strip()
    
    return direct_ip or "unknown"


def verify_agent_api_auth(request: Request) -> str:
    """
    Verify Agent API authentication - Phase 6 Security Fix v5
    
    Enhanced features:
    - HTTPS enforcement (NOGICOS_REQUIRE_HTTPS=true)
    - Origin validation (optional)
    - Real IP detection (NOGICOS_TRUST_PROXY=true)
    - Rate limiting (based on real IP)
    
    Returns:
        client_id: Client identifier for rate limiting (real IP)
        
    Raises:
        HTTPException: Authentication failed or rate limited
    """
    # Get configured API Key
    expected_key = os.environ.get("NOGICOS_API_KEY", "")
    
    # Review Fix v5: Get real client IP (proxy scenario)
    client_ip = get_real_client_ip(request)
    direct_ip = request.client.host if request.client else "unknown"
    
    # Review Fix v5: HTTPS enforcement check (REST endpoint)
    is_secure, https_error = check_secure_connection(request, is_websocket=False)
    if not is_secure:
        logger.warning(f"[Security] REST API insecure connection from {client_ip}: {https_error}")
        raise HTTPException(status_code=403, detail=https_error)
    
    # Origin validation (if enabled)
    if os.environ.get("NOGICOS_CHECK_ORIGIN", "").lower() == "true":
        origin = request.headers.get("Origin", "")
        allowed_origins = get_allowed_origins()
        if origin and origin not in allowed_origins:
            logger.warning(f"[Security] Blocked request from disallowed origin: {origin}")
            raise HTTPException(status_code=403, detail="Origin not allowed")
    
    if not expected_key:
        # When key not configured, only allow localhost
        # Note: Check direct IP not proxied IP, prevent spoofing
        if direct_ip not in ("127.0.0.1", "localhost", "::1"):
            logger.warning(f"[Security] Agent API blocked non-local request from {client_ip}")
            raise HTTPException(status_code=403, detail="Agent API only available locally")
        client_id = client_ip
    else:
        # Verify API Key
        auth_header = request.headers.get("Authorization", "")
        api_key_header = request.headers.get("X-API-Key", "")
        
        is_valid = (
            auth_header == f"Bearer {expected_key}" or
            api_key_header == expected_key
        )
        
        if not is_valid:
            logger.warning(f"[Security] Agent API unauthorized request from {client_ip}")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Review Fix v5: Use real IP as client ID
        client_id = client_ip
    
    # Rate limit check (based on real IP)
    if not _agent_rate_limiter.check(client_id):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    return client_id


# HostAgentManager removed - replaced by UnifiedAgentManager
# Removal date: 2026-01-07
# Reason: HostAgent was an empty shell, actual capabilities are in ReActAgent

# Global UnifiedAgentManager (new - Phase 7)
unified_agent_manager: Optional[UnifiedAgentManager] = None


# ============================================================================
# FastAPI App
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan manager"""
    global engine, server_start_time, unified_agent_manager
    
    logger.info("=" * 60)
    logger.info("NogicOS Hive Server V2 Starting...")
    logger.info("=" * 60)
    
    server_start_time = time.time()
    
    # Initialize engine
    engine = NogicEngine()
    await engine.start_websocket()
    
    # Initialize UnifiedAgentManager (the only Agent manager)
    if UNIFIED_AGENT_AVAILABLE:
        unified_agent_manager = UnifiedAgentManager()
        await unified_agent_manager.initialize(status_server=engine.status_server)
        stats = unified_agent_manager.get_stats()
        logger.info("=" * 40)
        logger.info("UnifiedAgentManager initialized!")
        logger.info(f"  Modules connected:")
        for module, available in stats.get("modules", {}).items():
            status = "OK" if available else "N/A"
            logger.info(f"    - {module}: {status}")
        logger.info("=" * 40)
    else:
        logger.warning("UnifiedAgentManager not available, Agent API will be disabled")
    
    # Start watchdog for connection monitoring
    def on_state_change(status):
        logger.info(f"[Watchdog] State change: WS={status.websocket.value}, API={status.api.value}")
    
    watchdog = await start_watchdog(
        ws_server=engine.status_server,
        on_state_change=on_state_change,
    )
    logger.info("Watchdog started")
    
    logger.info("Server ready!")
    logger.info(f"  HTTP: http://localhost:8080")
    logger.info(f"  WebSocket: ws://localhost:8765")
    if UNIFIED_AGENT_AVAILABLE:
        logger.info(f"  Agent API: /api/agent/*")
    logger.info("=" * 60)
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    
    # Close UnifiedAgentManager
    if unified_agent_manager:
        await unified_agent_manager.close()
    
    # Stop watchdog
    watchdog = get_watchdog()
    if watchdog:
        await watchdog.stop()
    
    if engine:
        await engine.stop_websocket()
    logger.info("Shutdown complete")


app = FastAPI(
    title="NogicOS Hive Server",
    description="AI Agent execution server with ReAct architecture",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS - Security: Limit allowed origins
# In production, set ALLOWED_ORIGINS env var
# Note: file:// removed for security - use proper Electron protocol handling
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",") if os.environ.get("ALLOWED_ORIGINS") else [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:5174",   # Vite alternative port
    "http://localhost:5175",   # Vite alternative port
    "http://localhost:5176",   # Vite alternative port
    "http://localhost:5177",   # Vite alternative port
    "http://localhost:3000",   # React dev server
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5176",
    "http://127.0.0.1:3000",
    "http://localhost:8080",   # Local server
    "http://127.0.0.1:8080",   # Local server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Session-ID"],
)


# ============================================================================
# Review Fix v7: Global HTTPS Enforcement Middleware
# ============================================================================

@app.middleware("http")
async def https_enforcement_middleware(request: Request, call_next):
    """
    Global HTTPS enforcement middleware - Review Fix v7
    
    When NOGICOS_REQUIRE_HTTPS=true:
    - Enforces HTTPS for all non-local requests
    - Exempt paths: /health, /ready (health check)
    
    Config:
    - NOGICOS_REQUIRE_HTTPS=true to enable
    - NOGICOS_HTTPS_EXEMPT_PATHS=/health,/ready exempt paths
    """
    # Check if HTTPS enforcement is enabled
    if not is_https_required():
        return await call_next(request)
    
    # Get exempt paths
    exempt_paths_str = os.environ.get("NOGICOS_HTTPS_EXEMPT_PATHS", "/health,/ready")
    exempt_paths = set(p.strip() for p in exempt_paths_str.split(",") if p.strip())
    
    # Check if exempt path
    if request.url.path in exempt_paths:
        return await call_next(request)
    
    # Check secure connection
    is_secure, error = check_secure_connection(request, is_websocket=False)
    if not is_secure:
        client_host = request.client.host if request.client else "unknown"
        logger.warning(f"[Security] HTTP blocked insecure request from {client_host} to {request.url.path}")
        return JSONResponse(
            status_code=403,
            content={"detail": error, "path": request.url.path}
        )
    
    return await call_next(request)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=StatusResponse)
async def root():
    """Server status"""
    return StatusResponse(
        status="running",
        version="2.0.0",
        engine_ready=engine is not None,
    )


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get server statistics"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not ready")
    return engine.get_stats()


@app.post("/v2/execute", response_model=ExecuteResponse)
@app.post("/execute", response_model=ExecuteResponse)  # Legacy route alias
async def execute_v2(request: ExecuteRequest):
    """
    Execute task using Pure ReAct Agent.
    
    Features:
    - Pure ReAct loop (no pre-planning)
    - Autonomous decision-making
    - Dynamic tool selection
    - Streaming via WebSocket
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not ready")
    
    return await engine.execute(request)


@app.get("/v2/tools")
async def list_v2_tools():
    """List all available tools"""
    registry = create_full_registry()
    tools = registry.to_anthropic_format()
    
    return {
        "count": len(tools),
        "tools": tools,
    }


class QuickSearchRequest(BaseModel):
    """Quick search request - bypasses Agent for speed"""
    query: str
    max_results: int = 5


@app.post("/v2/quick-search")
async def quick_search(request: QuickSearchRequest, req: Request):
    """
    Fast Search - Direct Tavily API call, skips Agent flow

    Speed: 1-3 seconds (vs Agent's 20-30 seconds)
    Use case: Simple search queries

    Security: Requires authentication via Authorization header or X-API-Key
    """
    # Security: Verify authentication
    auth_header = req.headers.get("Authorization", "")
    api_key_header = req.headers.get("X-API-Key", "")
    expected_key = os.environ.get("NOGICOS_API_KEY", "")

    if expected_key:
        is_valid = (
            auth_header == f"Bearer {expected_key}" or
            api_key_header == expected_key
        )
        if not is_valid:
            raise HTTPException(status_code=401, detail="Unauthorized")

    start = time.time()
    
    # Get API key
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        try:
            from api_keys import TAVILY_API_KEY
            api_key = TAVILY_API_KEY
        except ImportError:
            pass
    
    if not api_key:
        raise HTTPException(status_code=500, detail="TAVILY_API_KEY not configured")
    
    # [P1 FIX] Direct Tavily API call with enhanced error handling and timeout
    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": request.query[:500],  # [P1 FIX] Limit query length
                    "max_results": min(request.max_results, 10),  # [P1 FIX] Limit results
                    "include_answer": True,
                    "include_raw_content": False,
                }
            ) as resp:
                if resp.status != 200:
                    # [P1 FIX] Log error details but don't expose to client
                    error_text = await resp.text()
                    logger.error(f"[Tavily] API error {resp.status}: {error_text[:200]}")
                    raise HTTPException(status_code=502, detail="External search service error")
                data = await resp.json()
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Search request timeout")
    except aiohttp.ClientError as e:
        logger.error(f"[Tavily] Client error: {e}")
        raise HTTPException(status_code=502, detail="Search service unavailable")
    
    elapsed = time.time() - start
    
    return {
        "success": True,
        "query": request.query,
        "answer": data.get("answer", ""),
        "results": [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", "")[:200],
            }
            for r in data.get("results", [])
        ],
        "time_seconds": round(elapsed, 2),
    }


# =============================================================================
# Smart Search - Cursor style (Query optimization + Search + Result consolidation)
# =============================================================================

class SmartSearchRequest(BaseModel):
    """Smart search request - Cursor style"""
    query: str
    max_results: int = 5
    force_search: bool = False  # Skip judgment, force search


@app.post("/v2/smart-search")
async def smart_search_endpoint(request: SmartSearchRequest):
    """
    Smart Search - Cursor style
    
    Features:
    1. Precision - Auto judge if search is needed
    2. Query optimization - LLM optimizes search terms
    3. Result consolidation - LLM merges sources with citations
    
    Args:
    - force_search: True skips judgment and forces search
    """
    from engine.tools.smart_search import smart_search
    
    result = await smart_search(request.query, request.max_results, request.force_search)
    return result


class WarmCacheRequest(BaseModel):
    """Cache warming request"""
    session_id: str = "default"


@app.post("/v2/warm-cache")
async def warm_cache(request: WarmCacheRequest):
    """
    Pre-warm the prompt cache for faster TTFT.
    
    Call this when user focuses on input field.
    Implements Speculative Prompt Caching from Anthropic Cookbook.
    Can reduce TTFT by 90%+.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not ready")
    
    # Create a temporary agent to warm the cache
    agent = ReActAgent(
        status_server=engine.status_server,
    )
    
    success = await agent.warm_cache(request.session_id)
    
    return {
        "success": success,
        "session_id": request.session_id,
        "message": "Cache warmed" if success else "Cache warming failed",
    }


@app.get("/read_file")
async def read_file(path: str):
    """Read file content (for frontend)"""
    try:
        # [P0-4 FIX] Enhanced path validation

        # 1. Input validation - reject obviously malicious inputs early
        # [P0 FIX Round 2] Block absolute paths including Windows drive letters
        if not path or '..' in path or path.startswith('/') or path.startswith('\\'):
            logger.warning(f"[Security] Blocked malicious path input: {path[:50]}")
            raise HTTPException(status_code=400, detail="Invalid path")

        # [P0 FIX Round 2] Block Windows absolute paths (C:\, D:\, etc.)
        if len(path) >= 2 and path[1] == ':':
            logger.warning(f"[Security] Blocked Windows absolute path: {path[:50]}")
            raise HTTPException(status_code=400, detail="Invalid path")

        # 2. Normalize workspace path
        workspace = os.path.realpath(os.path.dirname(__file__))

        # 3. Safely join and resolve the full path
        requested_path = os.path.normpath(path)
        full_path = os.path.realpath(os.path.join(workspace, requested_path))

        # 4. [P0-4 FIX] Use commonpath for robust path containment check
        # This works correctly on both Windows and Unix
        try:
            common = os.path.commonpath([workspace, full_path])
            if common != workspace:
                logger.warning(f"[Security] Path traversal blocked: {path} -> {full_path}")
                raise HTTPException(status_code=403, detail="Access denied")
        except ValueError:
            # Different drives on Windows
            logger.warning(f"[Security] Cross-drive access blocked: {path}")
            raise HTTPException(status_code=403, detail="Access denied")

        # 5. [P0-4 FIX] Check for symbolic links (prevent symlink attacks)
        if os.path.islink(full_path):
            logger.warning(f"[Security] Symbolic link access blocked: {full_path}")
            raise HTTPException(status_code=403, detail="Symbolic links not allowed")

        # 6. [P0-4 FIX] Block sensitive file patterns (case-insensitive)
        path_lower = full_path.lower()
        sensitive_patterns = [
            '.env', '.ssh', 'credentials', 'secrets', '.git/config',
            'api_keys', 'password', 'token', '.npmrc', '.pypirc',
            'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519',
            '.aws/credentials', '.azure', '.kube/config',
        ]
        for pattern in sensitive_patterns:
            if pattern in path_lower:
                logger.warning(f"[Security] Blocked access to sensitive file: {path}")
                raise HTTPException(status_code=403, detail="Access denied to sensitive file")

        # 7. Check file existence and type
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        if not os.path.isfile(full_path):
            raise HTTPException(status_code=400, detail="Not a file")

        # 8. [P0-4 FIX] File size limit (prevent DoS)
        file_size = os.path.getsize(full_path)
        max_file_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_file_size:
            raise HTTPException(status_code=413, detail="File too large")

        # 9. Read file safely
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {"path": requested_path, "content": content}

    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not text/UTF-8")
    except Exception as e:
        logger.error(f"[Security] File read error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# Session Persistence Endpoints
# ============================================================================

class SaveSessionRequest(BaseModel):
    """Save session request"""
    session_id: str
    history: list
    preferences: dict = {}
    title: Optional[str] = None


@app.post("/v2/sessions/save")
async def save_session(request: SaveSessionRequest):
    """
    Save session history and preferences for persistence.
    
    This enables cross-session memory - users can resume previous sessions.
    """
    try:
        store = get_session_store()
        store.save_session(
            session_id=request.session_id,
            history=request.history,
            preferences=request.preferences,
            title=request.title,
        )
        return {
            "success": True,
            "session_id": request.session_id,
            "message": "Session saved",
        }
    except Exception as e:
        logger.error(f"Failed to save session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/sessions/{session_id}")
async def load_session(session_id: str):
    """
    Load a saved session by ID.
    
    Returns session history, preferences, and metadata.
    """
    try:
        store = get_session_store()
        session = store.load_session(session_id)
        return session
    except Exception as e:
        logger.error(f"Failed to load session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/sessions")
async def list_sessions(limit: int = 20, offset: int = 0):
    """
    List recent sessions.
    
    Returns session summaries without full history for performance.
    """
    try:
        store = get_session_store()
        sessions = store.list_sessions(limit=limit, offset=offset)
        stats = store.get_session_stats()
        
        return {
            "sessions": sessions,
            "total": stats["session_count"],
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/v2/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a saved session"""
    try:
        store = get_session_store()
        deleted = store.delete_session(session_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True, "message": "Session deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Memory Management Endpoints (Long-term Semantic Memory)
# ============================================================================

# Import memory store
try:
    from engine.knowledge.store import get_memory_store
    MEMORY_STORE_AVAILABLE = True
except ImportError:
    MEMORY_STORE_AVAILABLE = False


class AddMemoryRequest(BaseModel):
    """Add memory request"""
    subject: str
    predicate: str
    object: str
    session_id: str = "default"
    memory_type: str = "fact"
    importance: str = "medium"
    context: Optional[str] = None


class SearchMemoryRequest(BaseModel):
    """Search memory request"""
    query: str
    session_id: str = "default"
    limit: int = 5
    threshold: float = 0.5


@app.post("/v2/memories/add")
async def add_memory(request: AddMemoryRequest):
    """
    Add a new memory to long-term storage.
    
    Memories are stored as subject-predicate-object triples
    with optional importance scoring and context.
    
    Example:
        {"subject": "user", "predicate": "prefers", "object": "dark mode"}
    """
    if not MEMORY_STORE_AVAILABLE:
        raise HTTPException(status_code=501, detail="Memory store not available")
    
    try:
        store = get_memory_store()
        memory_id = await store.add_memory(
            subject=request.subject,
            predicate=request.predicate,
            obj=request.object,
            session_id=request.session_id,
            memory_type=request.memory_type,
            importance=request.importance,
            context=request.context,
        )
        
        return {
            "success": True,
            "memory_id": memory_id,
            "message": f"Memory added: {request.subject} {request.predicate} {request.object}",
        }
    except Exception as e:
        logger.error(f"Failed to add memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v2/memories/search")
async def search_memories(request: SearchMemoryRequest):
    """
    Semantic search for relevant memories.
    
    Uses embedding similarity to find memories related to the query.
    Falls back to keyword search if embeddings are unavailable.
    """
    if not MEMORY_STORE_AVAILABLE:
        raise HTTPException(status_code=501, detail="Memory store not available")
    
    try:
        store = get_memory_store()
        results = await store.search_memories(
            query=request.query,
            session_id=request.session_id,
            limit=request.limit,
            threshold=request.threshold,
        )
        
        return {
            "query": request.query,
            "count": len(results),
            "memories": results,
        }
    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/memories/{session_id}")
async def list_memories(
    session_id: str,
    memory_type: Optional[str] = None,
    importance: Optional[str] = None,
    limit: int = 50,
):
    """
    List memories for a session.
    
    Optional filters:
    - memory_type: fact, preference, event, relationship, instruction
    - importance: high, medium, low
    """
    if not MEMORY_STORE_AVAILABLE:
        raise HTTPException(status_code=501, detail="Memory store not available")
    
    try:
        store = get_memory_store()
        memories = store.list_memories(
            session_id=session_id,
            memory_type=memory_type,
            importance=importance,
            limit=limit,
        )
        
        return {
            "session_id": session_id,
            "count": len(memories),
            "memories": memories,
        }
    except Exception as e:
        logger.error(f"Failed to list memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/v2/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """
    Delete a memory (soft delete - marks as inactive).
    
    The memory is retained in the database but excluded from searches.
    """
    if not MEMORY_STORE_AVAILABLE:
        raise HTTPException(status_code=501, detail="Memory store not available")
    
    try:
        store = get_memory_store()
        deleted = store.delete_memory(memory_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {"success": True, "message": "Memory deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v2/memories/stats")
async def memory_stats():
    """
    Get memory store statistics.
    
    Returns counts of active memories, embeddings, and breakdown by importance.
    """
    if not MEMORY_STORE_AVAILABLE:
        raise HTTPException(status_code=501, detail="Memory store not available")
    
    try:
        store = get_memory_store()
        stats = store.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Vercel AI SDK Chat Endpoint
# ============================================================================

class ChatRequest(BaseModel):
    """Vercel AI SDK chat request"""
    messages: Optional[list] = None  # Traditional format
    text: Optional[str] = None  # New sendMessage format
    session_id: str = "default"

    model_config = {"extra": "allow"}  # Pydantic v2: Allow extra fields like temperature


async def generate_ai_sdk_stream(
    task: str, 
    session_id: str, 
    conversation_history: list = None,
    file_context: dict = None,  # NEW: Current file context
):
    """
    Generate SSE stream compatible with Vercel AI SDK 5.0 Data Stream Protocol.
    
    Stream format (SSE with JSON):
    - Start: data: {"type":"start","messageId":"..."}
    - Text: data: {"type":"text-start/delta/end","id":"...","delta":"..."}
    - Reasoning: data: {"type":"reasoning-start/delta/end","id":"...","delta":"..."}
    - Finish: data: {"type":"finish","finishReason":"stop"}
    
    Note: Requires x-vercel-ai-ui-message-stream: v1 header for custom backends.
    
    Args:
        task: Current user message
        session_id: Session identifier
        conversation_history: Previous messages for context (optional)
        file_context: Current file context from IDE (optional)
            {
                "path": "path/to/file.py",
                "content": "file content...",
                "selected": "selected code...",
                "cursorLine": 42,
                "cursorColumn": 10,
                "visibleRange": [30, 60]
            }
    """
    import uuid

    # #region debug log D
    import json as json_lib
    with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json_lib.dumps({"location":"hive_server.py:1953","message":"Getting agent instance","data":{"engineExists":engine is not None},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+'\n')
    # #endregion

    # Reuse global agent instance with lock protection
    # This avoids 1-2s initialization overhead per request
    if engine:
        agent = await engine.get_agent()
        # #region debug log D
        with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps({"location":"hive_server.py:1957","message":"Agent retrieved from engine","data":{"agentExists":agent is not None},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+'\n')
        # #endregion
    else:
        # #region debug log D
        with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps({"location":"hive_server.py:1959","message":"Creating new ReActAgent","data":{},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+'\n')
        # #endregion
        agent = ReActAgent(
            status_server=None,
            max_iterations=20,
        )
        # #region debug log D
        with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps({"location":"hive_server.py:1963","message":"ReActAgent created","data":{"agentExists":agent is not None},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+'\n')
        # #endregion
    
    message_id = str(uuid.uuid4())
    text_id = f"text_{uuid.uuid4().hex[:8]}"
    reasoning_id = f"reasoning_{uuid.uuid4().hex[:8]}"
    text_started = False
    reasoning_started = False
    
    # 2026 Top-tier: OutputType state tracking (for frontend semantic animations)
    current_output_type = "idle"  # idle | observing | analyzing | planning | writing | sending | waiting | completed | error
    current_target_hwnd: int | None = None
    current_source_hwnd: int | None = None
    
    # Helper to format SSE - AI SDK 5.0 compatible (no custom fields in standard events)
    def sse(data: dict, include_output_type: bool = False) -> str:
        # AI SDK 5.0 Zod validation rejects unknown fields in standard events
        # Custom metadata should use "data-*" type events instead
        return f"data: {json.dumps(data)}\n\n"
    
    # Helper to send custom metadata as data-* event (AI SDK compatible)
    def sse_metadata() -> str:
        return f"data: {json.dumps({'type': 'data-metadata', 'output_type': current_output_type, 'target_hwnd': current_target_hwnd, 'source_hwnd': current_source_hwnd})}\n\n"
    
    # [Fix #8] Limit event_queue size to prevent memory explosion
    event_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
    agent_done = asyncio.Event()
    
    async def thinking_callback(delta: str):
        nonlocal reasoning_started, current_output_type
        current_output_type = "analyzing"  # Thinking = Analyzing
        if not reasoning_started:
            await event_queue.put(sse({"type": "reasoning-start", "id": reasoning_id}))
            reasoning_started = True
        await event_queue.put(sse({"type": "reasoning-delta", "id": reasoning_id, "delta": delta}))
    
    async def text_callback(delta: str):
        nonlocal text_started, current_output_type
        current_output_type = "writing"  # Output text = Writing
        if not text_started:
            await event_queue.put(sse({"type": "text-start", "id": text_id}))
            text_started = True
        await event_queue.put(sse({"type": "text-delta", "id": text_id, "delta": delta}))
    
    # Track tool names for output events
    tool_names: dict = {}
    
    # Tool name to output_type mapping
    TOOL_OUTPUT_TYPES = {
        # Read tools
        "read_file": "observing",
        "read_screen": "observing",
        "get_window_info": "observing",
        "browser_snapshot": "observing",
        "ocr": "observing",
        # Analysis tools
        "search": "analyzing",
        "analyze": "analyzing",
        "compare": "analyzing",
        # Write tools
        "write_file": "writing",
        "edit_file": "writing",
        "type_text": "writing",
        "fill_form": "writing",
        # Send tools
        "send_message": "sending",
        "send_whatsapp": "sending",
        "send_email": "sending",
        "submit": "sending",
        # Interaction tools
        "click": "acting",
        "navigate": "acting",
        "browser_click": "acting",
        "browser_navigate": "acting",
    }
    
    async def tool_start_callback(tool_id: str, tool_name: str, tool_args: dict):
        nonlocal current_output_type, current_target_hwnd, current_source_hwnd
        
        tool_names[tool_id] = tool_name
        
        # Set output_type based on tool name
        current_output_type = TOOL_OUTPUT_TYPES.get(tool_name, "acting")
        
        # Try to extract hwnd from tool arguments
        if "hwnd" in tool_args:
            current_target_hwnd = tool_args["hwnd"]
        elif "target_hwnd" in tool_args:
            current_target_hwnd = tool_args["target_hwnd"]
        if "source_hwnd" in tool_args:
            current_source_hwnd = tool_args["source_hwnd"]
        
        # AI SDK Data Stream Protocol: tool-input-start -> tool-input-available -> (execution) -> tool-output-available
        await event_queue.put(sse({
            "type": "tool-input-start",
            "toolCallId": tool_id,
            "toolName": tool_name,
        }))
        await event_queue.put(sse({
            "type": "tool-input-available",
            "toolCallId": tool_id,
            "toolName": tool_name,
            "input": tool_args,
        }))
    
    async def tool_end_callback(tool_id: str, success: bool, result: str):
        nonlocal current_output_type
        
        if success:
            # Tool success, temporarily set to waiting (awaiting next step)
            current_output_type = "waiting"
            await event_queue.put(sse({
                "type": "tool-output-available",
                "toolCallId": tool_id,
                "output": result,
            }))
        else:
            current_output_type = "error"
            await event_queue.put(sse({
                "type": "tool-output-error",
                "toolCallId": tool_id,
                "errorText": result,
            }))
    
    async def run_agent():
        try:
            # Build context from conversation history
            context = None
            if conversation_history:
                # #region debug log H1
                import json as json_lib
                with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json_lib.dumps({"location":"hive_server.py:run_agent","message":"conversation_history received","data":{"history_count":len(conversation_history),"history_preview":[{"role":m.get("role"),"content_len":len(str(m.get("content","")))} for m in conversation_history[:5]]},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"H1"})+'\n')
                # #endregion
                
                # Format previous messages as context
                context_parts = []
                for msg in conversation_history[:-1]:  # Exclude current message
                    role = msg.get("role", "")
                    
                    # #region debug log H2 - inspect message structure
                    with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json_lib.dumps({"location":"hive_server.py:msg_inspect","message":"Inspecting message","data":{"role":role,"msg_keys":list(msg.keys()),"content_type":type(msg.get("content")).__name__,"parts_exists":"parts" in msg,"content_preview":str(msg.get("content",""))[:200]},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"H2"})+'\n')
                    # #endregion
                    
                    # AI SDK 5.0 uses "parts" array instead of "content" for messages
                    content = ""
                    
                    # Try parts array first (AI SDK 5.0 format)
                    if "parts" in msg and msg["parts"]:
                        for part in msg["parts"]:
                            if isinstance(part, dict) and part.get("type") == "text":
                                content += part.get("text", "")
                    # Fallback to content field
                    elif msg.get("content"):
                        content = msg.get("content", "")
                    if isinstance(content, list):
                        # Handle parts-based format in content
                        content = " ".join(
                            p.get("text", "") for p in content 
                            if isinstance(p, dict) and p.get("type") == "text"
                        )
                    if role == "user":
                        context_parts.append(f"User: {content}")
                    elif role == "assistant":
                        # [FIX] Increased truncation limit from 500 to 2000
                        # This preserves suggested answers for confirmation flow
                        if len(content) > 2000:
                            content = content[:2000] + "..."
                        context_parts.append(f"Assistant: {content}")
                
                if context_parts:
                    context = "## Previous conversation:\n" + "\n".join(context_parts[-6:])  # Keep last 3 turns (6 messages)
                    logger.info(f"[Chat] Injecting {len(context_parts)} previous messages as context")
                    # #region debug log H1
                    with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json_lib.dumps({"location":"hive_server.py:context_built","message":"Context built from history","data":{"context_preview":context[:500] if context else "","context_parts_count":len(context_parts)},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"H1"})+'\n')
                    # #endregion
            
            # Build file context section (Cursor-style auto-injection)
            if file_context:
                file_context_parts = []
                
                if file_context.get("path"):
                    file_context_parts.append(f"Current file: {file_context['path']}")
                
                if file_context.get("cursorLine"):
                    col = file_context.get("cursorColumn", "")
                    col_str = f":{col}" if col else ""
                    file_context_parts.append(f"Cursor position: line {file_context['cursorLine']}{col_str}")
                
                if file_context.get("selected"):
                    file_context_parts.append(f"\n--- Selected code ---\n{file_context['selected']}\n--- End selection ---")
                elif file_context.get("content"):
                    content = file_context["content"]
                    lines = content.split('\n')
                    if len(lines) <= 50:
                        # Small file, include all
                        file_context_parts.append(f"\n--- File content ---\n{content}\n--- End file ---")
                    elif file_context.get("cursorLine"):
                        # Large file, show context around cursor
                        cursor_line = file_context["cursorLine"]
                        start = max(0, cursor_line - 15)
                        end = min(len(lines), cursor_line + 15)
                        context_lines = lines[start:end]
                        numbered = [f"{i+start+1:4d}|{line}" for i, line in enumerate(context_lines)]
                        file_context_parts.append(f"\n--- Code near cursor (lines {start+1}-{end}) ---\n" + "\n".join(numbered) + "\n--- End code ---")
                
                if file_context_parts:
                    file_context_str = "\n".join(file_context_parts)
                    context = f"## Current file context:\n{file_context_str}\n\n" + (context or "")
                    logger.info(f"[Chat] Injecting file context: {file_context.get('path', 'unknown')}")
            
            # #region debug log D,E
            import json as json_lib
            with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_lib.dumps({"location":"hive_server.py:2086","message":"Calling agent.run_with_planning","data":{"task":task[:50],"sessionId":session_id},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D,E"})+'\n')
            # #endregion
            
            # Use run_with_planning() to activate Plan-and-Execute architecture
            # - Simple tasks: execute directly
            # - Complex tasks: generate plan, execute step by step, re-plan on failure
            result = await agent.run_with_planning(
                task=task,
                session_id=session_id,
                context=context,  # Pass conversation history as context
                on_text_delta=text_callback,
                on_thinking_delta=thinking_callback,
                on_tool_start=tool_start_callback,
                on_tool_end=tool_end_callback,
            )
            
            # #region debug log E
            with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_lib.dumps({"location":"hive_server.py:2098","message":"Agent run completed","data":{"success":result.success if hasattr(result,'success') else None},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+'\n')
            # #endregion
            # Send text-end if text was started
            if text_started:
                await event_queue.put(sse({"type": "text-end", "id": text_id}))
            # Send reasoning-end if reasoning was started
            if reasoning_started:
                await event_queue.put(sse({"type": "reasoning-end", "id": reasoning_id}))
            
            # Set final state
            current_output_type = "completed" if result.success else "error"
            
            # Send finish message - AI SDK 5.0 expects "finish" type (not "data-finish")
            await event_queue.put(sse({
                "type": "finish",
                "finishReason": "stop" if result.success else "error",
            }))
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            # #region debug log E - error details
            import json as json_lib
            with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_lib.dumps({"location":"hive_server.py:2135","message":"Agent exception","data":{"error":str(e),"type":type(e).__name__},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+'\n')
            # #endregion
            
            # Send error message to frontend - MUST send text-start before text-delta
            error_msg = str(e)
            if "api" in error_msg.lower() and "key" in error_msg.lower():
                error_msg = "API Key configuration error, please check api_keys.py"
            
            # [Fix] First send text-start, then text-delta, finally text-end
            if not text_started:
                await event_queue.put(sse({"type": "text-start", "id": text_id}))
            await event_queue.put(sse({
                "type": "text-delta", 
                "id": text_id, 
                "delta": f"\n\n❌ Error: {error_msg}"
            }))
            await event_queue.put(sse({"type": "text-end", "id": text_id}))
            # "data-finish" is not recognized by AI SDK 5.0, use "finish" instead
            await event_queue.put(sse({"type": "finish", "finishReason": "error"}))
        finally:
            agent_done.set()
    
    # [Fix #9] Start agent in background with exception handling
    agent_task = asyncio.create_task(run_agent())
    agent_task.add_done_callback(lambda t: t.exception() if not t.cancelled() and t.exception() else None)
    
    # #region debug log E
    import json as json_lib
    with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json_lib.dumps({"location":"hive_server.py:2117","message":"Stream start (no event sent)","data":{"messageId":message_id},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+'\n')
    # #endregion
    
    # AI SDK 5.0 does NOT accept "data-start" custom events
    # The first event must be a recognized type like text-start, reasoning-start, etc.
    # We skip the start event entirely - AI SDK doesn't need it
    
    try:
        event_count = 0
        while not agent_done.is_set() or not event_queue.empty():
            try:
                # Reduced timeout for faster response (was 0.1s, now 0.01s)
                event = await asyncio.wait_for(event_queue.get(), timeout=0.01)
                event_count += 1
                # #region debug log E
                if event_count <= 5:  # Log first 5 events
                    with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json_lib.dumps({"location":"hive_server.py:2124","message":"Yielding event","data":{"eventCount":event_count,"eventPreview":event[:100] if isinstance(event,str) else str(event)[:100]},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+'\n')
                # #endregion
                yield event
            except asyncio.TimeoutError:
                continue
    finally:
        if not agent_task.done():
            agent_task.cancel()


@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """
    Vercel AI SDK compatible chat endpoint.
    
    Accepts multiple formats:
    1. New format: { text: "message" }
    2. Traditional: { messages: [{ role: "user", content: "..." }] }
    
    Returns SSE stream with:
    - Text deltas (type 0)
    - Reasoning/thinking deltas (type g, h)
    - Tool calls (type 9, a)
    - Finish signal (type d)
    
    Frontend uses @ai-sdk/react useChat hook to consume this stream.
    """
    # #region debug log B
    import json as json_lib
    with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json_lib.dumps({"location":"hive_server.py:2141","message":"chat_endpoint called","data":{},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"})+'\n')
    # #endregion
    
    if not engine:
        # #region debug log D
        with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps({"location":"hive_server.py:2159","message":"engine not ready","data":{},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+'\n')
        # #endregion
        raise HTTPException(status_code=503, detail="Engine not ready")
    
    try:
        body = await request.json()
        # #region debug log C
        with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps({"location":"hive_server.py:2163","message":"JSON parsed","data":{"bodyKeys":list(body.keys())},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+'\n')
        # #endregion
        logger.info(f"[Chat] Received request: {json.dumps(body, ensure_ascii=False)[:200]}...")
    except Exception as e:
        # #region debug log C
        with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps({"location":"hive_server.py:2167","message":"JSON parse error","data":{"error":str(e)},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+'\n')
        # #endregion
        logger.error(f"[Chat] Failed to parse JSON: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    
    # Extract user message and conversation history
    user_message = ""
    conversation_history = []
    session_id = body.get("session_id", "default")
    
    # [FIX] Always extract messages array for conversation history (AI SDK sends both)
    if "messages" in body and body["messages"]:
        conversation_history = body["messages"]
    
    # Format 1: New Vercel AI SDK format { text: "..." }
    # Note: AI SDK sends BOTH text AND messages array
    if "text" in body and body["text"]:
        user_message = body["text"]
    
    # Format 2: Messages array (traditional or new parts-based)
    elif "messages" in body and body["messages"]:
        # Keep full conversation history for context
        conversation_history = body["messages"]
        
        # Extract latest user message
        for msg in reversed(body["messages"]):
            if isinstance(msg, dict) and msg.get("role") == "user":
                # New AI SDK format: parts array
                if "parts" in msg and msg["parts"]:
                    for part in msg["parts"]:
                        if isinstance(part, dict) and part.get("type") == "text":
                            user_message = part.get("text", "")
                            break
                    if user_message:
                        break
                
                # Traditional format: content field
                content = msg.get("content", "")
                if isinstance(content, str) and content:
                    user_message = content
                    break
                elif isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            user_message = part.get("text", "")
                            break
                    if user_message:
                        break
    
    if not user_message:
        # #region debug log C
        import json as json_lib
        with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps({"location":"hive_server.py:2198","message":"No user message found","data":{"body":body},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+'\n')
        # #endregion
        logger.warning(f"[Chat] No user message found in request: {body}")
        raise HTTPException(status_code=400, detail="No user message found")
    
    # Extract file context (Cursor-style auto-injection from IDE)
    # Frontend can send: { fileContext: { path, content, selected, cursorLine, cursorColumn, visibleRange } }
    file_context = body.get("fileContext") or body.get("file_context")
    
    # Log context info
    if file_context:
        logger.info(f"[Chat] Processing: {user_message[:100]}... (file: {file_context.get('path', 'unknown')})")
    elif conversation_history:
        logger.info(f"[Chat] Processing: {user_message[:100]}... (with {len(conversation_history)} history messages)")
    else:
        logger.info(f"[Chat] Processing: {user_message[:100]}...")
    
    # #region debug log D,E
    import json as json_lib
    with open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json_lib.dumps({"location":"hive_server.py:2214","message":"Starting stream generation","data":{"userMessage":user_message[:50],"sessionId":session_id},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D,E"})+'\n')
    # #endregion
    
    return StreamingResponse(
        generate_ai_sdk_stream(user_message, session_id, conversation_history, file_context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "x-vercel-ai-ui-message-stream": "v1",  # Required for AI SDK 5.0
        }
    )


# ============================================================================
# ChatKit Endpoint (OpenAI ChatKit Protocol)
# ============================================================================

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """
    ChatKit Protocol endpoint - supports OpenAI ChatKit UI Framework.
    
    This endpoint implements the full ChatKit server protocol, supporting:
    - Streaming response
    - Widget rendering
    - Client tools
    - Session management
    
    Frontend uses @openai/chatkit-react to connect to this endpoint.
    """
    if not CHATKIT_AVAILABLE:
        return JSONResponse(
            status_code=501,
            content={
                "error": "ChatKit SDK not available",
                "detail": "Install with: pip install openai-chatkit",
            }
        )
    
    if not engine or not engine.chatkit_server:
        return JSONResponse(
            status_code=503,
            content={
                "error": "ChatKit server not ready",
                "detail": "Engine not initialized",
            }
        )
    
    try:
        payload = await request.body()
        result = await engine.chatkit_server.process(payload, {"request": request})
        
        if isinstance(result, StreamingResult):
            # SSE Response requires buffering disabled for true streaming effect
            return StreamingResponse(
                result, 
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # Disable nginx buffering
                }
            )
        
        if hasattr(result, "json"):
            return Response(content=result.json, media_type="application/json")
        
        return JSONResponse(result)
        
    except Exception as e:
        logger.error(f"ChatKit endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# ============================================================================
# Hook System API Endpoints
# ============================================================================

# Import Hook Manager
try:
    from engine.context import get_hook_manager, ConnectionTarget
    HOOK_SYSTEM_AVAILABLE = True
except ImportError:
    HOOK_SYSTEM_AVAILABLE = False
    logger.warning("Hook system not available")


class HookConnectRequest(BaseModel):
    """Hook connect request"""
    type: str  # browser, desktop, file
    target: str = ""  # Optional target (e.g., chrome, directory path)


@app.get("/api/hooks/status")
async def get_hook_status():
    """
    Get current Hook system status.
    
    Returns all connected hooks and their current context.
    """
    if not HOOK_SYSTEM_AVAILABLE:
        return {"hooks": {}, "available": False}
    
    try:
        manager = await get_hook_manager()
        status = manager.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get hook status: {e}")
        return {"hooks": {}, "error": str(e)}


@app.post("/api/hooks/connect")
async def connect_hook(request: HookConnectRequest):
    """
    Connect to an application/resource.
    
    Supported types:
    - browser: Connect to user's browser (Chrome, Firefox, Edge)
    - desktop: Monitor active windows
    - file: Watch file changes in a directory
    """
    if not HOOK_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=501, detail="Hook system not available")
    
    try:
        manager = await get_hook_manager()
        
        success = await manager.connect(ConnectionTarget(
            type=request.type,
            target=request.target,
        ))
        
        # [Fix] After connecting, immediately capture context to ensure API response contains complete data
        if success:
            hook = manager.get_hook(request.type)
            if hook:
                context = await hook.capture()  # Immediately get first context
                if context:
                    hook._notify_context_update(context)  # Manually update to state.context
        
        if success:
            return {
                "success": True,
                "message": f"Connected to {request.type}",
                "status": manager.get_status(),
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to connect to {request.type}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect hook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/hooks/disconnect/{hook_id}")
async def disconnect_hook(hook_id: str):
    """
    Disconnect a hook by ID.
    """
    if not HOOK_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=501, detail="Hook system not available")
    
    try:
        manager = await get_hook_manager()
        success = await manager.disconnect(hook_id)
        
        return {
            "success": success,
            "message": f"Disconnected {hook_id}" if success else f"Failed to disconnect {hook_id}",
        }
    except Exception as e:
        logger.error(f"Failed to disconnect hook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hooks/context")
async def get_hook_context():
    """
    Get current context from all connected hooks.
    
    This is the context that gets injected into the Agent.
    """
    if not HOOK_SYSTEM_AVAILABLE:
        return {"context": {}, "prompt": ""}
    
    try:
        from engine.context import get_context_store
        store = get_context_store()
        
        return {
            "context": store.get_context_for_agent(),
            "prompt": store.format_context_prompt(),
        }
    except Exception as e:
        logger.error(f"Failed to get hook context: {e}")
        return {"context": {}, "prompt": "", "error": str(e)}


# ============================================================================
# CDP Browser Connection API (direct control of user's browser)
# ============================================================================

class CDPConnectRequest(BaseModel):
    """CDP connection request"""
    cdp_url: str = "http://localhost:9222"


# Global browser session for CDP connection
_cdp_browser_session = None


@app.post("/api/browser/connect-cdp")
async def connect_browser_cdp(request: CDPConnectRequest):
    """
    Connect to user's browser via Chrome DevTools Protocol (CDP).
    
    This enables direct DOM manipulation without mouse simulation.
    
    User must start Chrome with: chrome.exe --remote-debugging-port=9222
    
    Args:
        cdp_url: CDP endpoint URL (default: http://localhost:9222)
    
    Returns:
        Connection status and current page info
    """
    global _cdp_browser_session
    
    try:
        from engine.browser.session import BrowserSession
        
        # Stop existing session if any
        if _cdp_browser_session:
            try:
                await _cdp_browser_session.stop()
            except Exception:
                pass
        
        # Create new session and connect via CDP
        _cdp_browser_session = BrowserSession()
        success = await _cdp_browser_session.connect_to_browser(request.cdp_url)
        
        if success:
            # Get current page info
            title = await _cdp_browser_session.get_title()
            url = await _cdp_browser_session.get_current_url()
            
            # Inject session into Agent's tool registry
            from engine.tools import get_registry
            registry = get_registry()
            registry.set_context("browser_session", _cdp_browser_session)
            
            logger.info(f"[CDP] Connected to browser: {title} ({url})")
            
            return {
                "success": True,
                "message": f"Connected to browser via CDP",
                "page": {
                    "title": title,
                    "url": url,
                },
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to connect via CDP. Make sure Chrome is running with --remote-debugging-port=9222"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CDP] Connection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/browser/cdp-status")
async def get_cdp_status():
    """
    Get CDP connection status.
    
    Returns:
        Connection status and current page info if connected
    """
    global _cdp_browser_session
    
    if not _cdp_browser_session or not _cdp_browser_session.is_started:
        return {"connected": False}
    
    try:
        title = await _cdp_browser_session.get_title()
        url = await _cdp_browser_session.get_current_url()
        
        return {
            "connected": True,
            "page": {
                "title": title,
                "url": url,
            },
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.post("/api/browser/disconnect-cdp")
async def disconnect_browser_cdp():
    """
    Disconnect from browser CDP session.
    """
    global _cdp_browser_session
    
    if _cdp_browser_session:
        try:
            await _cdp_browser_session.stop()
            _cdp_browser_session = None
            
            # Remove session from registry
            from engine.tools import get_registry
            registry = get_registry()
            registry.set_context("browser_session", None)
            
            logger.info("[CDP] Disconnected from browser")
            return {"success": True, "message": "Disconnected from CDP"}
        except Exception as e:
            logger.error(f"[CDP] Disconnect failed: {e}")
            return {"success": False, "error": str(e)}
    
    return {"success": True, "message": "No active CDP connection"}


# ============================================================================
# Window Discovery API (for universal app connector)
# ============================================================================

@app.get("/api/windows")
async def get_all_windows():
    """
    Get all visible windows for the window selector UI.
    
    Returns:
        List of windows with hwnd, title, app_name, is_browser, etc.
    
    Used by:
        - ConnectorPanel window list selector
        - Drag-and-drop connector target identification
    """
    try:
        from engine.context.hooks.desktop_hook import get_all_windows as _get_all_windows

        windows = _get_all_windows()

        # Security: Update discovered HWNDs whitelist
        global _discovered_hwnds
        _discovered_hwnds = {w.hwnd for w in windows}

        return {
            "success": True,
            "count": len(windows),
            "windows": [w.to_dict() for w in windows],
        }
    except ImportError as e:
        logger.warning(f"Window discovery not available: {e}")
        return {
            "success": False,
            "count": 0,
            "windows": [],
            "error": "Window discovery not available on this platform",
        }
    except Exception as e:
        logger.error(f"Failed to get windows: {e}")
        return {
            "success": False,
            "count": 0,
            "windows": [],
            "error": str(e),
        }


class ConnectWindowRequest(BaseModel):
    """Connect to a specific window by HWND"""
    hwnd: int
    window_title: str = ""  # Optional, for display


# Security: HWND whitelist - only allow connecting to windows that were discovered
_discovered_hwnds: set = set()


@app.post("/api/windows/connect")
async def connect_to_window(request: ConnectWindowRequest):
    """
    Connect to a specific window by HWND.
    
    This is the unified app connector - works for browsers, IDEs, and any app.
    
    Args:
        hwnd: Window handle to connect to
        window_title: Optional window title for display
    
    Returns:
        Connection status and context
    """
    if not HOOK_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=501, detail="Hook system not available")

    # Security: Validate HWND against whitelist
    global _discovered_hwnds
    if request.hwnd not in _discovered_hwnds:
        logger.warning(f"[Security] Attempted connection to non-whitelisted HWND: {request.hwnd}")
        raise HTTPException(status_code=403, detail="HWND not in discovered windows whitelist")

    try:
        from engine.context.hooks.desktop_hook import get_all_windows as _get_all_windows, BROWSER_PROCESSES

        # Find window info by HWND
        windows = _get_all_windows()
        target_window = None
        for w in windows:
            if w.hwnd == request.hwnd:
                target_window = w
                break

        if not target_window:
            raise HTTPException(status_code=404, detail=f"Window with HWND {request.hwnd} not found")
        
        # Determine hook type based on app
        hook_type = "browser" if target_window.is_browser else "desktop"
        
        # Connect using appropriate hook
        manager = await get_hook_manager()
        # Use hwnd as target, let DesktopHook lock to specific window
        success = await manager.connect(ConnectionTarget(
            type=hook_type,
            target=str(request.hwnd),  # Pass HWND, not app_name
        ))
        
        if success:
            # Get hook and update context with window info
            hook = manager.get_hook(hook_type)
            if hook:
                context = await hook.capture()
                if context:
                    # Inject HWND into context for Overlay
                    if hasattr(context, 'hwnd'):
                        context.hwnd = request.hwnd
                    hook._notify_context_update(context)
            
            return {
                "success": True,
                "hook_type": hook_type,
                "window": target_window.to_dict(),
                "status": manager.get_status(),
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to connect to window")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect to window: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Context Analysis API - Level 3 Smart Perception
# ============================================================================

class ContextAnalyzeRequest(BaseModel):
    """Analyze context of connected app"""
    hwnd: int
    app_name: str
    app_type: str = "desktop"  # desktop, browser, ide


@app.post("/api/context/analyze")
async def analyze_app_context(request: ContextAnalyzeRequest):
    """
    Analyze connected app context, return smart feedback like "I noticed...".
    
    True smart perception:
    1. Get app's real context (window title, screenshot, etc.)
    2. Use LLM to analyze context and generate specific observations and suggestions
    """
    try:
        import subprocess
        import os
        
        observations = []
        suggestions = []
        raw_context = {}  # Collect raw context for LLM analysis
        
        app_lower = request.app_name.lower()
        
        # ============ Step 1: Collect real context ============
        
        # Get window title (latest)
        try:
            from engine.context.hooks.desktop_hook import get_all_windows as _get_all_windows
            windows = _get_all_windows()
            for w in windows:
                if w.hwnd == request.hwnd:
                    raw_context['window_title'] = w.title
                    raw_context['app_name'] = w.app_display_name or w.app_name
                    raw_context['is_browser'] = w.is_browser
                    break
        except Exception as e:
            logger.warning(f"Failed to get window info: {e}")
            raw_context['window_title'] = request.app_name
        
        # For IDEs, try to read Git state
        if 'cursor' in app_lower or 'code' in app_lower or 'idea' in app_lower:
            try:
                # Get nogicos project path
                project_path = os.path.dirname(os.path.dirname(__file__))
                nogicos_path = os.path.join(project_path, 'nogicos')
                
                # Get recently modified files
                result = subprocess.run(
                    ['git', 'diff', '--name-only', 'HEAD~3'],
                    cwd=nogicos_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout:
                    raw_context['recent_changes'] = result.stdout.strip().split('\n')[:5]
                
                # Get current branch
                result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    cwd=nogicos_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout:
                    raw_context['git_branch'] = result.stdout.strip()
                    
            except Exception as e:
                logger.warning(f"Failed to get Git context: {e}")
        
        # For browsers, infer content from window title
        if raw_context.get('is_browser') or 'chrome' in app_lower or 'firefox' in app_lower or 'edge' in app_lower:
            title = raw_context.get('window_title', '')
            raw_context['page_info'] = {
                'title': title,
                'detected_site': _detect_website(title)
            }
        
        # ============ Step 2: Use LLM to analyze context ============
        
        try:
            # Import API keys
            from api_keys import ANTHROPIC_API_KEY
            import httpx
            
            # Build prompt
            context_str = json.dumps(raw_context, ensure_ascii=False, indent=2)
            
            prompt = f"""You are the NogicOS smart context module. The user just connected an app. Analyze the context and generate an "I noticed..." feedback.

Connected app: {request.app_name}
App type: {request.app_type}

Collected context:
{context_str}

Generate a JSON analysis with:
1. observations: Specific observations (max 3)
2. suggestions: Actions the user might want to take (max 2)

Requirements:
- observations should be specific, referencing actual content (file names, page titles)
- suggestions should be practical, inferred from observations
- If browser, infer user intent from page title
- If IDE, infer from recently modified files

Example response format:
{{
  "observations": [
    {{"type": "activity", "icon": "📝", "title": "Editing code", "detail": "Recently modified BubbleMode.tsx", "highlight": true}}
  ],
  "suggestions": [
    {{"id": "review_code", "label": "Code Review", "description": "Review recent changes"}}
  ]
}}

Return only JSON, no other content."""

            # Call Claude API
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-5-haiku-20241022",
                        "max_tokens": 500,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('content', [{}])[0].get('text', '{}')
                    
                    # Parse JSON
                    try:
                        analysis = json.loads(content)
                        observations = analysis.get('observations', [])
                        suggestions = analysis.get('suggestions', [])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse LLM response: {content}")
                else:
                    logger.warning(f"LLM API error: {response.status_code}")
                    
        except ImportError:
            logger.warning("API keys not available for LLM analysis")
        except Exception as e:
            logger.warning(f"LLM analysis failed: {e}")
        
        # ============ Step 3: Fallback if LLM fails ============
        
        if not observations:
            # Basic analysis from window title
            title = raw_context.get('window_title', request.app_name)
            
            observations.append({
                "type": "connected",
                "icon": "✅",
                "title": f"Connected to {request.app_name}",
                "detail": title[:50] + ('...' if len(title) > 50 else ''),
                "highlight": False
            })
            
            # Add basic suggestions based on app type
            if raw_context.get('recent_changes'):
                observations.append({
                    "type": "recent_files",
                    "icon": "📂",
                    "title": "Recently modified files",
                    "detail": ', '.join(raw_context['recent_changes'][:3]),
                    "highlight": True
                })
                suggestions.append({
                    "id": "review_changes",
                    "label": "View Changes",
                    "description": "Analyze recent code changes"
                })
            
            if raw_context.get('page_info', {}).get('detected_site'):
                site = raw_context['page_info']['detected_site']
                observations.append({
                    "type": "site_detected",
                    "icon": "🌐",
                    "title": f"Detected {site['name']}",
                    "detail": site.get('description', ''),
                    "highlight": True
                })
                if site.get('suggestions'):
                    for sug in site['suggestions'][:2]:
                        suggestions.append(sug)
        
        return {
            "success": True,
            "app_name": request.app_name,
            "hwnd": request.hwnd,
            "observations": observations,
            "suggestions": suggestions,
            "raw_context": raw_context  # For debugging
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze context: {e}")
        return {
            "success": False,
            "app_name": request.app_name,
            "hwnd": request.hwnd,
            "observations": [{
                "type": "error",
                "icon": "⚠️",
                "title": "Analysis failed",
                "detail": str(e),
                "highlight": False
            }],
            "suggestions": [],
            "error": str(e)
        }


# ============================================================================
# Multi-App Context Analysis API - Multi-app combined smart perception
# ============================================================================

class AppContextInfo(BaseModel):
    """Context info for a single app"""
    hwnd: int
    app_name: str
    app_type: str = "desktop"

class MultiContextAnalyzeRequest(BaseModel):
    """Analyze combined context of multiple connected apps"""
    apps: list[AppContextInfo]

@app.post("/api/context/analyze-multi")
async def analyze_multi_app_context(request: MultiContextAnalyzeRequest):
    """
    Analyze combined context of multiple apps, infer cross-app workflows.
    
    When user connects multiple apps, system analyzes relationships between them
    and infers workflows the user might want to complete.
    """
    try:
        import subprocess
        import os
        
        # Collect context from all apps
        all_contexts = []
        app_names = []
        
        for app_info in request.apps:
            app_context = {
                "hwnd": app_info.hwnd,
                "app_name": app_info.app_name,
                "app_type": app_info.app_type,
            }
            app_names.append(app_info.app_name)
            app_lower = app_info.app_name.lower()
            
            # Get window title
            try:
                from engine.context.hooks.desktop_hook import get_all_windows as _get_all_windows
                windows = _get_all_windows()
                for w in windows:
                    if w.hwnd == app_info.hwnd:
                        app_context['window_title'] = w.title
                        app_context['is_browser'] = w.is_browser
                        break
            except Exception as e:
                logger.warning(f"Failed to get window info for {app_info.app_name}: {e}")
            
            # For IDEs, get Git state
            if 'cursor' in app_lower or 'code' in app_lower or 'idea' in app_lower:
                try:
                    project_path = os.path.dirname(os.path.dirname(__file__))
                    nogicos_path = os.path.join(project_path, 'nogicos')
                    
                    result = subprocess.run(
                        ['git', 'diff', '--name-only', 'HEAD~3'],
                        cwd=nogicos_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.stdout:
                        app_context['recent_changes'] = result.stdout.strip().split('\n')[:5]
                    
                    result = subprocess.run(
                        ['git', 'branch', '--show-current'],
                        cwd=nogicos_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.stdout:
                        app_context['git_branch'] = result.stdout.strip()
                except Exception as e:
                    logger.warning(f"Failed to get Git context: {e}")
            
            # For browsers, detect website
            if app_context.get('is_browser') or 'chrome' in app_lower or 'firefox' in app_lower:
                title = app_context.get('window_title', '')
                app_context['detected_site'] = _detect_website(title)
            
            all_contexts.append(app_context)
        
        # Use LLM to analyze combined intent
        observations = []
        suggestions = []
        workflow_detected = None
        
        try:
            from api_keys import ANTHROPIC_API_KEY
            import httpx
            
            context_str = json.dumps(all_contexts, ensure_ascii=False, indent=2)
            
            prompt = f"""You are the NogicOS smart context module. The user has connected multiple apps. Analyze their combined context and infer the workflow they want to complete.

Connected apps:
{context_str}

Generate a JSON analysis with:
1. observations: Observations about the work environment (max 3)
2. suggestions: Cross-app workflow suggestions (max 3)
3. workflow: Detected workflow pattern (if any)

Analysis hints:
- Cursor + Chrome(YC) → Likely wants to extract info from code to fill YC application
- Chrome(YC) + WhatsApp → Likely wants to notify team about YC progress
- Cursor + Chrome(YC) + WhatsApp → Likely wants full flow: code update → fill form → notify team
- IDE + Notion → Likely wants to sync code docs
- Browser + Chat app → Likely wants to share page content

Example response format:
{{
  "observations": [
    {{"type": "workflow", "icon": "🔗", "title": "Workflow detected", "detail": "Code → YC Application → Team notification", "highlight": true}},
    {{"type": "context", "icon": "📝", "title": "Cursor editing", "detail": "BubbleMode.tsx", "highlight": false}},
    {{"type": "context", "icon": "🌐", "title": "Chrome on YC", "detail": "Application page - tech section", "highlight": false}}
  ],
  "suggestions": [
    {{"id": "full_workflow", "label": "🚀 Run full workflow", "description": "Extract code updates → Fill YC → Notify team"}},
    {{"id": "update_yc", "label": "📝 Update YC only", "description": "Update tech description from code changes"}},
    {{"id": "notify_team", "label": "💬 Notify team only", "description": "Share progress via WhatsApp"}}
  ],
  "workflow": {{
    "name": "YC Application Update Flow",
    "steps": ["Extract code updates from Cursor", "Fill YC form", "Notify team via WhatsApp"],
    "confidence": 0.85
  }}
}}

Return only JSON, no other content."""

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-5-haiku-20241022",
                        "max_tokens": 800,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('content', [{}])[0].get('text', '{}')
                    
                    try:
                        analysis = json.loads(content)
                        observations = analysis.get('observations', [])
                        suggestions = analysis.get('suggestions', [])
                        workflow_detected = analysis.get('workflow')
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse LLM response: {content}")
                else:
                    logger.warning(f"LLM API error: {response.status_code}")
                    
        except ImportError:
            logger.warning("API keys not available for LLM analysis")
        except Exception as e:
            logger.warning(f"LLM analysis failed: {e}")
        
        # Fallback if LLM fails
        if not observations:
            observations.append({
                "type": "connected",
                "icon": "🔗",
                "title": f"{len(request.apps)} apps connected",
                "detail": ', '.join(app_names),
                "highlight": True
            })
            
            # Detect common workflow patterns
            has_ide = any('cursor' in a.app_name.lower() or 'code' in a.app_name.lower() for a in request.apps)
            has_yc = any('yc' in str(c.get('detected_site', {}).get('name', '')).lower() or 
                        'y combinator' in str(c.get('window_title', '')).lower() 
                        for c in all_contexts)
            has_chat = any('whatsapp' in a.app_name.lower() or 'slack' in a.app_name.lower() 
                          for a in request.apps)
            
            if has_ide and has_yc:
                suggestions.append({
                    "id": "update_yc_from_code",
                    "label": "📝 Update YC Application",
                    "description": "Update tech description from code changes"
                })
            
            if has_yc and has_chat:
                suggestions.append({
                    "id": "notify_yc_progress",
                    "label": "💬 Notify Team",
                    "description": "Share YC application progress"
                })
            
            if has_ide and has_yc and has_chat:
                workflow_detected = {
                    "name": "YC Application Update Flow",
                    "steps": ["Extract code updates", "Fill YC form", "Notify team"],
                    "confidence": 0.7
                }
                suggestions.insert(0, {
                    "id": "full_workflow",
                    "label": "🚀 Run Full Workflow",
                    "description": "Code → YC Application → Team notification"
                })
        
        return {
            "success": True,
            "app_count": len(request.apps),
            "app_names": app_names,
            "observations": observations,
            "suggestions": suggestions,
            "workflow": workflow_detected,
            "contexts": all_contexts  # For debugging
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze multi-app context: {e}")
        return {
            "success": False,
            "app_count": len(request.apps),
            "observations": [{
                "type": "error",
                "icon": "⚠️",
                "title": "Analysis failed",
                "detail": str(e),
                "highlight": False
            }],
            "suggestions": [],
            "error": str(e)
        }


def _detect_website(title: str) -> dict:
    """Detect website type from window title"""
    title_lower = title.lower()
    
    # Common website detection rules
    sites = [
        {
            'keywords': ['y combinator', 'ycombinator', 'yc application'],
            'name': 'Y Combinator',
            'description': 'YC Application Page',
            'suggestions': [
                {'id': 'fill_form', 'label': 'Fill Form', 'description': 'Fill based on product docs'},
                {'id': 'review_answers', 'label': 'Review Answers', 'description': 'Optimize existing answers'}
            ]
        },
        {
            'keywords': ['google docs', 'google sheets', 'google slides'],
            'name': 'Google Workspace',
            'description': 'Online Document',
            'suggestions': [
                {'id': 'summarize', 'label': 'Generate Summary', 'description': 'Summarize document content'},
                {'id': 'export', 'label': 'Export', 'description': 'Export to other formats'}
            ]
        },
        {
            'keywords': ['notion'],
            'name': 'Notion',
            'description': 'Knowledge Base / Notes',
            'suggestions': [
                {'id': 'organize', 'label': 'Organize Content', 'description': 'Optimize document structure'},
                {'id': 'sync', 'label': 'Sync', 'description': 'Sync to other apps'}
            ]
        },
        {
            'keywords': ['figma'],
            'name': 'Figma',
            'description': 'Design File',
            'suggestions': [
                {'id': 'export_design', 'label': 'Export Design', 'description': 'Export as code or images'},
                {'id': 'review_design', 'label': 'Design Review', 'description': 'Analyze design elements'}
            ]
        },
        {
            'keywords': ['linear', 'jira', 'asana'],
            'name': 'Project Management',
            'description': 'Task Tracking',
            'suggestions': [
                {'id': 'create_task', 'label': 'Create Task', 'description': 'Quickly add new task'},
                {'id': 'update_status', 'label': 'Update Status', 'description': 'Batch update tasks'}
            ]
        },
        {
            'keywords': ['slack', 'discord', 'teams'],
            'name': 'Team Chat',
            'description': 'Instant Messaging',
            'suggestions': [
                {'id': 'send_update', 'label': 'Send Update', 'description': 'Notify team of progress'},
                {'id': 'summarize_chat', 'label': 'Summarize Chat', 'description': 'Generate discussion summary'}
            ]
        },
        {
            'keywords': ['whatsapp', 'telegram', 'wechat', '微信'],
            'name': 'Messaging',
            'description': 'Chat App',
            'suggestions': [
                {'id': 'send_message', 'label': 'Send Message', 'description': 'Quick update'},
                {'id': 'reply', 'label': 'Reply', 'description': 'Generate reply suggestions'}
            ]
        },
        {
            'keywords': ['github', 'gitlab', 'bitbucket'],
            'name': 'Git Platform',
            'description': 'Code Repository',
            'suggestions': [
                {'id': 'review_pr', 'label': 'Review PR', 'description': 'Analyze code changes'},
                {'id': 'create_issue', 'label': 'Create Issue', 'description': 'Report issue or suggestion'}
            ]
        },
        {
            'keywords': ['chatgpt', 'claude', 'gemini', 'copilot'],
            'name': 'AI Assistant',
            'description': 'AI Chat',
            'suggestions': [
                {'id': 'compare', 'label': 'Compare Answers', 'description': 'Compare with other AIs'},
                {'id': 'export_chat', 'label': 'Export Chat', 'description': 'Save valuable conversations'}
            ]
        }
    ]
    
    for site in sites:
        for keyword in site['keywords']:
            if keyword in title_lower:
                return site
    
    # Unknown website
    return {
        'name': 'Web Page',
        'description': title[:30] + ('...' if len(title) > 30 else ''),
        'suggestions': [
            {'id': 'extract_content', 'label': 'Extract Content', 'description': 'Extract key page info'},
            {'id': 'screenshot', 'label': 'Screenshot Analysis', 'description': 'Analyze page content'}
        ]
    }


# ============================================================================
# Phase 6: Agent Control API Endpoints
# ============================================================================

@app.post("/api/agent/start")
async def start_agent(request: AgentStartRequest, req: Request):
    """
    Start Agent 任务 - Phase 7 (UnifiedAgentManager)
    
    Start一个New的 Agent 任务，Return任务 ID 用于AftercontinuedStateQuery和控制。
    
    Phase 7 改进：
        - Usage UnifiedAgentManager 作为Core（基于 ReActAgent）
        - Auto串联 PlanCache、Memory、ContextStore、Verification
        - 支持计划复用和学习
    
    Security:
        - 需要 API Key 鉴权（或仅Allow本地Request）
        - Rate limit: 20 requests/minute
    
    Args:
        request: Contains task description and target window info
        
    Returns:
        {"task_id": str, "status": "running"}
    """
    # Security: Verify authentication and rate limit
    verify_agent_api_auth(req)
    
    # Phase 7: Prioritize UnifiedAgentManager
    if UNIFIED_AGENT_AVAILABLE and unified_agent_manager:
        try:
            result = await unified_agent_manager.start_task(
                task=request.task,
                target_hwnds=request.target_hwnds,
                max_iterations=request.max_iterations,
                session_id=request.session_id,
            )
            return result
        except RuntimeError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to start agent (unified): {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Fallback: HostAgentManager (legacy)
    if HOST_AGENT_AVAILABLE and host_agent_manager:
        try:
            result = await host_agent_manager.start_task(
                task=request.task,
                target_hwnds=request.target_hwnds,
                max_iterations=request.max_iterations,
                session_id=request.session_id,
            )
            return result
        except RuntimeError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to start agent (legacy): {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    raise HTTPException(status_code=501, detail="No Agent available")


@app.post("/api/agent/stop")
async def stop_agent(request: AgentStopRequest, req: Request):
    """
    Stop Agent task (user takeover) - Phase 7
    
    Based on ByteBot takeover mode, user can take over executing tasks.
    
    Security:
        - Requires API Key authentication (or only allow local requests)
    
    Args:
        request: Contains task ID and stop reason
        
    Returns:
        {"success": bool, "status": "stopped"}
    """
    # Security: Verify authentication
    verify_agent_api_auth(req)
    
    # Phase 7: Prioritize UnifiedAgentManager
    if UNIFIED_AGENT_AVAILABLE and unified_agent_manager:
        try:
            result = await unified_agent_manager.stop_task(
                task_id=request.task_id,
                reason=request.reason,
            )
            return result
        except RuntimeError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to stop agent: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Fallback: HostAgentManager (legacy)
    if HOST_AGENT_AVAILABLE and host_agent_manager:
        try:
            result = await host_agent_manager.stop_task(
                task_id=request.task_id,
                reason=request.reason,
            )
            return result
        except RuntimeError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to stop agent: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    raise HTTPException(status_code=501, detail="No Agent available")


@app.post("/api/agent/resume")
async def resume_agent(request: AgentResumeRequest, req: Request):
    """
    Resume Agent task - Phase 6 (Security Fixed)
    
    Based on ByteBot resume mode, resume paused or interrupted tasks from checkpoint.
    
    Security:
        - Requires API Key authentication (or only allow local requests)
    
    Args:
        request: Contains task ID to resume
        
    Returns:
        {"task_id": str, "status": "resuming"}
    """
    # Security: Verify authentication
    verify_agent_api_auth(req)
    
    if not HOST_AGENT_AVAILABLE or not host_agent_manager:
        raise HTTPException(status_code=501, detail="HostAgent not available")
    
    try:
        result = await host_agent_manager.resume_task(task_id=request.task_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to resume agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/status/{task_id}")
async def get_agent_status(task_id: str, req: Request):
    """
    Get Agent task status - Phase 7
    
    Security:
        - Requires API Key authentication (or only allow local requests)
    
    Args:
        task_id: Task ID
        
    Returns:
        AgentStatusResponse with detailed task status info
    """
    # Security: Verify authentication
    verify_agent_api_auth(req)
    
    # Phase 7: Prioritize UnifiedAgentManager
    if UNIFIED_AGENT_AVAILABLE and unified_agent_manager:
        try:
            status = await unified_agent_manager.get_task_status(task_id)
            if "error" in status:
                raise HTTPException(status_code=404, detail=status["error"])
            return status
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get agent status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Fallback: HostAgentManager (legacy)
    if HOST_AGENT_AVAILABLE and host_agent_manager:
        try:
            status = host_agent_manager.get_status(task_id)
            return status
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to get agent status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    raise HTTPException(status_code=501, detail="No Agent available")


@app.post("/api/agent/confirm/{action_id}")
async def confirm_agent_action(action_id: str, approved: bool = True, req: Request = None):
    """
    Confirm/Reject敏感操作 - Phase 6 (Security Fixed)
    
    当 Agent RequestExecute敏感操作时，User通过此端点批准或Reject。
    
    Security:
        - 需要 API Key 鉴权（或仅Allow本地Request）
    
    Args:
        action_id: 操作 ID（从 WebSocket EventGet）
        approved: True=批准, False=Reject
        
    Returns:
        {"success": bool}
    """
    # Security: Verify authentication
    if req:
        verify_agent_api_auth(req)
    
    if not HOST_AGENT_AVAILABLE or not host_agent_manager:
        raise HTTPException(status_code=501, detail="HostAgent not available")
    
    if approved:
        success = await host_agent_manager.approve_action(action_id)
    else:
        success = await host_agent_manager.deny_action(action_id)
    
    return {"success": success, "action_id": action_id, "approved": approved}


@app.get("/api/agent/confirmations")
async def get_pending_confirmations(req: Request):
    """
    Get pending sensitive operations list - Phase 6 Fix
    
    Returns all sensitive operations waiting for user confirmation.
    
    Security:
        - Requires API Key authentication (or only allow local requests)
    """
    # Security: Verify authentication
    verify_agent_api_auth(req)
    
    if not HOST_AGENT_AVAILABLE or not host_agent_manager:
        raise HTTPException(status_code=501, detail="HostAgent not available")
    
    confirmations = host_agent_manager.get_pending_confirmations()
    return {"pending": confirmations, "count": len(confirmations)}


# ============================================================================
# YC Workflow Confirmation System
# ============================================================================

# Global pending confirmations for YC workflow
_yc_pending_confirmations: Dict[str, asyncio.Future] = {}


class WorkflowConfirmRequest(BaseModel):
    """YC workflow confirmation request"""
    request_id: str
    confirmed: bool


@app.post("/api/workflow/confirm")
async def confirm_yc_workflow(request: WorkflowConfirmRequest):
    """
    Confirm or cancel YC workflow action.
    
    Called from frontend ConfirmDialog when user clicks Confirm/Cancel.
    
    Args:
        request_id: The confirmation request ID
        confirmed: True to proceed, False to cancel
        
    Returns:
        {"success": bool}
    """
    request_id = request.request_id
    confirmed = request.confirmed
    
    if request_id not in _yc_pending_confirmations:
        raise HTTPException(status_code=404, detail=f"Confirmation request {request_id} not found or expired")
    
    future = _yc_pending_confirmations.pop(request_id)
    
    if not future.done():
        future.set_result(confirmed)
        logger.info(f"[YC Workflow] Confirmation {request_id}: {'approved' if confirmed else 'rejected'}")
    
    return {"success": True, "request_id": request_id, "confirmed": confirmed}


async def request_yc_confirmation(
    status_server: StatusServer,
    title: str,
    question: str,
    answer: str,
    execution_count: int,
    source_file: str = "PITCH_CONTEXT.md",
) -> bool:
    """
    Request user confirmation for YC workflow via WebSocket.
    
    Sends a confirm_request event to frontend and waits for response.
    
    Args:
        status_server: WebSocket server for broadcasting
        title: Dialog title
        question: YC question text
        answer: Answer to fill
        execution_count: Which run this is (1st, 2nd, etc.)
        source_file: Source document filename
        
    Returns:
        True if user confirmed, False if cancelled
    """
    import uuid
    request_id = f"yc-{uuid.uuid4().hex[:8]}"
    
    # Create future for async waiting
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    _yc_pending_confirmations[request_id] = future
    
    # Send confirmation request to frontend
    await status_server.broadcast({
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
    logger.info(f"[YC Workflow] Sent confirmation request {request_id}")
    
    try:
        # Wait for user response (timeout: 5 minutes)
        confirmed = await asyncio.wait_for(future, timeout=300)
        return confirmed
    except asyncio.TimeoutError:
        _yc_pending_confirmations.pop(request_id, None)
        logger.warning(f"[YC Workflow] Confirmation {request_id} timed out")
        return False


@app.get("/api/agent/stats")
async def get_agent_stats(req: Request):
    """
    Get Agent system statistics - Phase 7
    
    Returns UnifiedAgentManager module status and statistics.
    
    Security:
        - Requires API Key authentication (or only allow local requests)
    """
    # Security: Verify authentication
    verify_agent_api_auth(req)
    
    # Phase 7: UnifiedAgentManager stats
    if UNIFIED_AGENT_AVAILABLE and unified_agent_manager:
        stats = unified_agent_manager.get_stats()
        stats["manager_type"] = "UnifiedAgentManager"
        stats["core_agent"] = "ReActAgent"
        return stats
    
    # Legacy
    if HOST_AGENT_AVAILABLE and host_agent_manager:
        return {
            "manager_type": "HostAgentManager (legacy)",
            "core_agent": "HostAgent",
            "modules": {
                "plan_cache": False,
                "context_store": False,
                "memory": False,
                "verification": False,
            },
        }
    
    raise HTTPException(status_code=501, detail="No Agent available")


# ============================================================================
# Phase 6: WebSocket Agent Event Stream
# ============================================================================

@app.get("/api/agent/ws-token/{task_id}")
async def get_ws_token(task_id: str, req: Request):
    """
    Get WebSocket connection token - Phase 6 Fix v2
    
    Returns an HMAC signed token for WebSocket connection authentication.
    Token valid for 5 minutes.
    
    Security:
        - Requires API Key authentication
    """
    # Verify API authentication
    verify_agent_api_auth(req)
    
    token = generate_ws_token(task_id, expires_in_seconds=300)
    return {
        "task_id": task_id,
        "token": token,
        "expires_in": 300,
        "ws_url": f"/ws/agent/{task_id}?token={token}",
    }


@app.websocket("/ws/agent/{task_id}")
async def agent_event_stream(websocket: WebSocket, task_id: str, token: Optional[str] = None):
    """
    WebSocket streaming Agent events - Phase 6 (Security Fixed v3)
    
    Establishes WebSocket connection for specified task, receives in real-time:
    - started: Task started
    - thinking: AI reasoning process
    - tool_start: Tool call started
    - tool_end: Tool call ended
    - progress: Progress update
    - confirm_required: Needs user confirmation
    - needs_help: Needs human intervention
    - completed: Task completed
    - failed: Task failed
    - cancelled: Task cancelled
    - stopped: Task stopped
    - backpressure_warning: Event queue backlog warning
    - heartbeat: Heartbeat
    
    Security (v3):
        - HTTPS/WSS enforcement (NOGICOS_REQUIRE_HTTPS=true)
        - HMAC signed token (separate key NOGICOS_WS_SECRET)
        - Origin validation
        - Only allow local connections (when API Key not configured)
        - Send error event before close on auth failure
    
    Args:
        task_id: Task ID
        token: HMAC signed token (passed via query parameter)
    """
    # Review Fix v5: Use real client IP
    client_host = get_real_client_ip(websocket)
    direct_host = websocket.client.host if websocket.client else "unknown"
    
    # Review Fix v7: Connection rate limit (check before accept)
    allowed, limit_error = await _ws_connection_limiter.try_acquire(client_host)
    if not allowed:
        logger.warning(f"[Security] WebSocket connection limited for {client_host}: {limit_error}")
        # When rate limited, close directly without accept
        await websocket.close(code=1008, reason=limit_error)
        return
    
    # Ensure connection quota is released when connection ends
    connection_acquired = True
    
    # Fix v7: On auth failure, first accept, send error event, then close, and release connection quota
    async def reject_with_error(code: int, reason: str, error_type: str):
        """Reject connection and send error event"""
        nonlocal connection_acquired
        try:
            await websocket.accept()
            await websocket.send_json({
                "type": "auth_error",
                "data": {
                    "error": reason,
                    "error_type": error_type,
                    "code": code,
                },
                "timestamp": time.time(),
                "task_id": task_id,
            })
            await websocket.close(code=code, reason=reason)
        finally:
            # Release connection quota
            if connection_acquired:
                await _ws_connection_limiter.release(client_host)
                connection_acquired = False
    
    # Security v3: HTTPS/WSS enforcement check
    is_secure, https_error = check_secure_connection(websocket, is_websocket=True)
    if not is_secure:
        logger.warning(f"[Security] WebSocket insecure connection from {client_host}: {https_error}")
        await reject_with_error(4003, https_error, "insecure_connection")
        return
    
    # Security v3: Origin validation
    if os.environ.get("NOGICOS_CHECK_ORIGIN", "").lower() == "true":
        origin = websocket.headers.get("Origin", "")
        allowed_origins = get_allowed_origins()
        if origin and origin not in allowed_origins:
            logger.warning(f"[Security] WebSocket blocked origin: {origin} from {client_host}")
            await reject_with_error(4003, f"Origin not allowed: {origin}", "origin_blocked")
            return
    
    # Security v3: HMAC token verification (using separate key) or local access
    ws_secret = get_ws_secret()
    if ws_secret != "default_secret_for_local":
        # Requires HMAC token verification
        is_valid, error_msg = verify_ws_token(task_id, token or "")
        if not is_valid:
            logger.warning(f"[Security] WebSocket auth failed from {client_host}: {error_msg}")
            await reject_with_error(4001, f"Authentication failed: {error_msg}", "auth_failed")
            return
    else:
        # When key not configured, only allow localhost
        # Review Fix v5: Check direct IP not proxied IP, prevent spoofing
        if direct_host not in ("127.0.0.1", "localhost", "::1"):
            logger.warning(f"[Security] WebSocket blocked non-local from {client_host} (direct: {direct_host})")
            await reject_with_error(4003, "Local access only", "local_only")
            return
    
    # Check HostAgent availability
    if not HOST_AGENT_AVAILABLE or not host_agent_manager:
        await reject_with_error(1011, "HostAgent not available", "service_unavailable")
        return
    
    # Auth success, accept connection
    await websocket.accept()
    logger.info(f"[Agent WS] Connected for task: {task_id} from {client_host}")
    
    # Send connection success event
    await websocket.send_json({
        "type": "connected",
        "data": {"task_id": task_id, "client": client_host},
        "timestamp": time.time(),
    })
    
    # Subscribe to task events
    event_queue = host_agent_manager.subscribe(task_id)
    
    # Review Fix v8: Register message rate limiter
    connection_id = f"{task_id}:{client_host}:{time.time()}"
    _ws_message_limiter.register_connection(connection_id)
    
    try:
        # Send current status
        try:
            status = host_agent_manager.get_status(task_id)
            await websocket.send_json({
                "type": "status",
                "data": status,
                "timestamp": time.time(),
            })
        except ValueError:
            # Task not found, send not_found status
            await websocket.send_json({
                "type": "status",
                "data": {"task_id": task_id, "status": "not_found"},
                "timestamp": time.time(),
            })
        
        # Send pending confirmations (if any)
        pending = host_agent_manager.get_pending_confirmations()
        task_pending = [p for p in pending if p.get("task_id") == task_id]
        if task_pending:
            await websocket.send_json({
                "type": "pending_confirmations",
                "data": task_pending,
                "timestamp": time.time(),
            })
        
        # Continuously push events
        while True:
            try:
                # Wait for event, send heartbeat on timeout
                event = await asyncio.wait_for(event_queue.get(), timeout=30.0)
                
                # Review Fix v8: Check message send rate
                event_type = event.get("type", "")
                event_priority = event.get("priority", get_event_priority(event_type))
                
                allowed, should_warn, rate_error = _ws_message_limiter.check_rate(connection_id)
                
                if not allowed:
                    # Over burst limit, skip low priority events
                    if event_priority > EventPriority.HIGH:
                        logger.debug(f"[Agent WS] Dropping {event_type} due to rate limit")
                        continue
                    # High priority events still sent, but log warning
                    logger.warning(f"[Agent WS] Rate limit exceeded but sending {event_type} (priority={event_priority})")
                
                if should_warn:
                    # Send rate warning
                    await websocket.send_json({
                        "type": "rate_warning",
                        "data": {"message": "Message rate approaching limit"},
                        "timestamp": time.time(),
                    })
                
                await websocket.send_json(event)
                
                # Check if task ended
                if event_type in ("completed", "failed", "cancelled", "stopped"):
                    logger.info(f"[Agent WS] Task {task_id} ended ({event_type}), closing")
                    # Send final status
                    await websocket.send_json({
                        "type": "connection_closing",
                        "data": {"reason": f"Task {event_type}"},
                        "timestamp": time.time(),
                    })
                    break
                    
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection
                try:
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": time.time(),
                    })
                except Exception:
                    # Send failed, connection may be disconnected
                    break
                
    except WebSocketDisconnect:
        logger.info(f"[Agent WS] Disconnected for task: {task_id}")
    except Exception as e:
        logger.error(f"[Agent WS] Error for task {task_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"message": str(e)},
                "timestamp": time.time(),
            })
        except Exception:
            pass
    finally:
        host_agent_manager.unsubscribe(task_id, event_queue)
        # Review Fix v7: Release connection quota
        if connection_acquired:
            await _ws_connection_limiter.release(client_host)
        # Review Fix v8: Unregister message rate limiter
        _ws_message_limiter.unregister_connection(connection_id)
        logger.debug(f"[Agent WS] Cleanup completed for task: {task_id}")
        logger.info(f"WebSocket cleanup for task: {task_id}")


# Debug endpoint to test pyautogui in backend process
@app.get("/test-pyautogui")
async def test_pyautogui():
    """Test pyautogui movement in backend process"""
    import pyautogui
    import ctypes
    
    results = {}
    
    # Check DPI awareness
    try:
        awareness = ctypes.c_int()
        ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
        results["dpi_awareness"] = awareness.value
    except:
        results["dpi_awareness"] = "unknown"
    
    # Current position
    before = pyautogui.position()
    results["before"] = f"({before.x}, {before.y})"
    
    # Try to move
    target_x, target_y = 500, 500
    pyautogui.moveTo(target_x, target_y)
    
    # Check after
    import time
    time.sleep(0.1)
    after = pyautogui.position()
    results["target"] = f"({target_x}, {target_y})"
    results["after"] = f"({after.x}, {after.y})"
    results["success"] = after.x == target_x and after.y == target_y
    
    # Check pyautogui settings
    results["failsafe"] = pyautogui.FAILSAFE
    results["pause"] = pyautogui.PAUSE
    results["screen_size"] = f"{pyautogui.size()}"
    
    return results


@app.get("/health")
async def health():
    """Health check endpoint"""
    memory_mb = 0
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
    except ImportError:
        pass  # psutil not installed
    except (OSError, AttributeError, Exception):
        pass  # Process or memory info not available
    
    uptime = time.time() - server_start_time
    
    status = "healthy"
    if engine is None:
        status = "unhealthy"
    elif engine._executing:
        status = "busy"
    elif memory_mb > 1024:
        status = "degraded"
    
    # Include watchdog status
    watchdog = get_watchdog()
    watchdog_status = None
    if watchdog:
        watchdog_status = {
            "websocket": watchdog.status.websocket.value,
            "api": watchdog.status.api.value,
            "recovery_attempts": watchdog.status.recovery_attempts,
            "is_healthy": watchdog.is_healthy,
        }
    
    return {
        "status": status,
        "engine": engine is not None,
        "executing": engine._executing if engine else False,
        "current_task": engine._current_task[:50] if engine and engine._current_task else None,
        "uptime_seconds": round(uptime, 1),
        "memory_mb": round(memory_mb, 1),
        "watchdog": watchdog_status,
    }


# ============================================================================
# Main Entry
# ============================================================================

if __name__ == "__main__":
    # Load API keys
    try:
        from api_keys import setup_env
        setup_env()
        logger.info("API keys loaded from api_keys.py")
    except ImportError:
        logger.info("Using environment variables for API keys")
    
    # Run server
    uvicorn.run(
        "hive_server:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info",
    )
