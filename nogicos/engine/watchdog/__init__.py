# -*- coding: utf-8 -*-
"""
NogicOS Watchdog System

Monitors WebSocket and API connections, automatically recovers from failures.
Inspired by browser-use's production-ready architecture.

Features:
- Connection health monitoring (WebSocket + HTTP)
- Automatic reconnection with exponential backoff
- Graceful degradation when services are unavailable
- Event emission for UI feedback
"""

import asyncio
import time
import aiohttp
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

from engine.observability import get_logger

logger = get_logger("watchdog")


class ConnectionState(Enum):
    """Connection health states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DISCONNECTED = "disconnected"
    RECOVERING = "recovering"


@dataclass
class HealthStatus:
    """Current health status of monitored services"""
    websocket: ConnectionState = ConnectionState.DISCONNECTED
    api: ConnectionState = ConnectionState.DISCONNECTED
    last_check: float = 0
    recovery_attempts: int = 0
    

@dataclass
class WatchdogConfig:
    """Configuration for watchdog behavior"""
    check_interval: float = 5.0  # Seconds between health checks
    max_retries: int = 5  # Maximum recovery attempts before giving up
    base_backoff: float = 1.0  # Base backoff time in seconds
    max_backoff: float = 30.0  # Maximum backoff time
    api_url: str = "http://localhost:8080"
    ws_url: str = "ws://localhost:8765"


class ConnectionWatchdog:
    """
    Monitors connections and automatically recovers from failures.
    
    Usage:
        watchdog = ConnectionWatchdog(
            on_state_change=lambda state: print(f"State: {state}"),
            on_recovery=lambda service: print(f"Recovered: {service}"),
        )
        await watchdog.start()
    """
    
    def __init__(
        self,
        config: Optional[WatchdogConfig] = None,
        on_state_change: Optional[Callable[[HealthStatus], None]] = None,
        on_recovery: Optional[Callable[[str, bool], None]] = None,
        on_failure: Optional[Callable[[str, str], None]] = None,
    ):
        """
        Initialize ConnectionWatchdog.
        
        Args:
            config: Watchdog configuration
            on_state_change: Callback when health state changes
            on_recovery: Callback when a service recovers (service_name, success)
            on_failure: Callback when a service fails (service_name, error)
        """
        self.config = config or WatchdogConfig()
        self.on_state_change = on_state_change
        self.on_recovery = on_recovery
        self.on_failure = on_failure
        
        self._running = False
        self._status = HealthStatus()
        self._recovery_tasks: Dict[str, asyncio.Task] = {}
        self._last_states: Dict[str, ConnectionState] = {}
        
        # External components to control
        self._ws_server = None
        self._http_session: Optional[aiohttp.ClientSession] = None
    
    def set_ws_server(self, ws_server):
        """Set the WebSocket server instance to monitor/control"""
        self._ws_server = ws_server
    
    @property
    def status(self) -> HealthStatus:
        """Get current health status"""
        return self._status
    
    @property
    def is_healthy(self) -> bool:
        """Check if all services are healthy"""
        return (
            self._status.websocket == ConnectionState.HEALTHY and
            self._status.api == ConnectionState.HEALTHY
        )
    
    async def start(self):
        """Start the watchdog monitoring loop"""
        if self._running:
            logger.warning("Watchdog already running")
            return
        
        self._running = True
        self._http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))
        
        logger.info(f"Watchdog started (interval={self.config.check_interval}s)")
        
        try:
            while self._running:
                await self._check_all_connections()
                await asyncio.sleep(self.config.check_interval)
        except asyncio.CancelledError:
            logger.info("Watchdog stopped")
        finally:
            await self._cleanup()
    
    async def stop(self):
        """Stop the watchdog"""
        self._running = False
        
        # Cancel any ongoing recovery tasks
        for task in self._recovery_tasks.values():
            task.cancel()
        self._recovery_tasks.clear()
        
        logger.info("Watchdog stopping...")
    
    async def _cleanup(self):
        """Cleanup resources"""
        if self._http_session:
            await self._http_session.close()
            self._http_session = None
    
    async def _check_all_connections(self):
        """Check health of all monitored connections"""
        self._status.last_check = time.time()
        
        # Check in parallel
        await asyncio.gather(
            self._check_api_health(),
            self._check_websocket_health(),
            return_exceptions=True
        )
        
        # Notify state change if changed
        self._notify_state_change()
    
    async def _check_api_health(self):
        """Check HTTP API health"""
        try:
            if not self._http_session:
                self._status.api = ConnectionState.DISCONNECTED
                return
            
            async with self._http_session.get(f"{self.config.api_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") in ["healthy", "busy"]:
                        self._status.api = ConnectionState.HEALTHY
                    else:
                        self._status.api = ConnectionState.DEGRADED
                else:
                    self._status.api = ConnectionState.DEGRADED
                    
        except aiohttp.ClientError as e:
            logger.debug(f"API health check failed: {e}")
            self._status.api = ConnectionState.DISCONNECTED
            
            # Trigger recovery if not already in progress
            if "api" not in self._recovery_tasks:
                self._start_recovery("api")
                
        except Exception as e:
            logger.error(f"Unexpected API health error: {e}")
            self._status.api = ConnectionState.DISCONNECTED
    
    async def _check_websocket_health(self):
        """Check WebSocket server health"""
        try:
            if self._ws_server is None:
                self._status.websocket = ConnectionState.DISCONNECTED
                return
            
            # Check if WS server reports healthy
            if hasattr(self._ws_server, 'is_healthy'):
                if self._ws_server.is_healthy():
                    self._status.websocket = ConnectionState.HEALTHY
                else:
                    self._status.websocket = ConnectionState.DEGRADED
            elif hasattr(self._ws_server, 'connections'):
                # Fallback: check if server has active connections support
                self._status.websocket = ConnectionState.HEALTHY
            else:
                self._status.websocket = ConnectionState.DISCONNECTED
                
        except Exception as e:
            logger.error(f"WebSocket health check failed: {e}")
            self._status.websocket = ConnectionState.DISCONNECTED
            
            if "websocket" not in self._recovery_tasks:
                self._start_recovery("websocket")
    
    def _start_recovery(self, service: str):
        """Start recovery task for a service"""
        if service in self._recovery_tasks:
            return
        
        self._status.recovery_attempts += 1
        
        if service == "websocket":
            self._status.websocket = ConnectionState.RECOVERING
        elif service == "api":
            self._status.api = ConnectionState.RECOVERING
        
        task = asyncio.create_task(self._recover_service(service))
        self._recovery_tasks[service] = task
        
        logger.info(f"Started recovery for {service}")
    
    async def _recover_service(self, service: str):
        """Attempt to recover a failed service with exponential backoff"""
        attempt = 0
        
        while attempt < self.config.max_retries and self._running:
            attempt += 1
            
            # Calculate backoff with exponential increase
            backoff = min(
                self.config.base_backoff * (2 ** (attempt - 1)),
                self.config.max_backoff
            )
            
            logger.info(f"Recovery attempt {attempt}/{self.config.max_retries} for {service} "
                       f"(backoff: {backoff:.1f}s)")
            
            try:
                success = await self._attempt_recovery(service)
                
                if success:
                    logger.info(f"✓ {service} recovered after {attempt} attempt(s)")
                    
                    if self.on_recovery:
                        self.on_recovery(service, True)
                    
                    break
                    
            except Exception as e:
                logger.warning(f"Recovery attempt {attempt} for {service} failed: {e}")
            
            await asyncio.sleep(backoff)
        
        else:
            # Max retries exhausted
            logger.error(f"✗ {service} recovery failed after {self.config.max_retries} attempts")
            
            if self.on_failure:
                self.on_failure(service, f"Max retries ({self.config.max_retries}) exhausted")
        
        # Clean up task reference
        self._recovery_tasks.pop(service, None)
    
    async def _attempt_recovery(self, service: str) -> bool:
        """Single recovery attempt for a service"""
        if service == "websocket":
            return await self._recover_websocket()
        elif service == "api":
            return await self._recover_api()
        return False
    
    async def _recover_websocket(self) -> bool:
        """Attempt to recover WebSocket server"""
        if self._ws_server is None:
            return False
        
        try:
            # Try to restart WebSocket server
            if hasattr(self._ws_server, 'restart'):
                await self._ws_server.restart()
                return True
            elif hasattr(self._ws_server, 'stop') and hasattr(self._ws_server, 'start'):
                await self._ws_server.stop()
                await asyncio.sleep(0.5)
                await self._ws_server.start()
                return True
            
            # If no restart capability, just check if it's now healthy
            await asyncio.sleep(1)
            if hasattr(self._ws_server, 'is_healthy'):
                return self._ws_server.is_healthy()
            
            return False
            
        except Exception as e:
            logger.error(f"WebSocket recovery failed: {e}")
            return False
    
    async def _recover_api(self) -> bool:
        """Attempt to recover API connection"""
        # For API, we just try to reconnect/ping
        try:
            if not self._http_session or self._http_session.closed:
                self._http_session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=5)
                )
            
            async with self._http_session.get(f"{self.config.api_url}/health") as response:
                if response.status == 200:
                    self._status.api = ConnectionState.HEALTHY
                    return True
                    
        except Exception as e:
            logger.debug(f"API recovery ping failed: {e}")
        
        return False
    
    def _notify_state_change(self):
        """Notify listeners if state changed"""
        current_states = {
            "websocket": self._status.websocket,
            "api": self._status.api,
        }
        
        if current_states != self._last_states:
            self._last_states = current_states.copy()
            
            if self.on_state_change:
                self.on_state_change(self._status)
            
            # Log state change
            logger.info(f"Connection state: WS={self._status.websocket.value}, "
                       f"API={self._status.api.value}")


# Singleton instance
_watchdog: Optional[ConnectionWatchdog] = None


def get_watchdog() -> ConnectionWatchdog:
    """Get or create the global watchdog instance"""
    global _watchdog
    if _watchdog is None:
        _watchdog = ConnectionWatchdog()
    return _watchdog


async def start_watchdog(
    ws_server=None,
    config: Optional[WatchdogConfig] = None,
    on_state_change: Optional[Callable] = None,
) -> ConnectionWatchdog:
    """Start the global watchdog with optional configuration"""
    global _watchdog
    
    _watchdog = ConnectionWatchdog(
        config=config,
        on_state_change=on_state_change,
    )
    
    if ws_server:
        _watchdog.set_ws_server(ws_server)
    
    # Start in background
    asyncio.create_task(_watchdog.start())
    
    return _watchdog

