# -*- coding: utf-8 -*-
"""
Base Hook - Hook 基Class

所有 Hook 的Abstract基Class，定义统一Interface
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from ..store import HookType, HookStatus, HookState

logger = logging.getLogger(__name__)


@dataclass
class HookConfig:
    """Hook Config"""
    # Catchinterval（Second）
    capture_interval: float = 1.0
    
    # YesNoEnable Vision Analyze
    enable_vision: bool = False
    
    # YesNoEnablelocal OCR
    enable_ocr: bool = True
    
    # MaxHistorynumber
    max_history: int = 100
    
    # quotaOuterConfig
    extra: Dict[str, Any] = field(default_factory=dict)


class BaseHook(ABC):
    """
    Hook 基Class
    
    所有 Hook 需要Implement的Interface：
    - start(): Start Hook
    - stop(): Stop Hook
    - capture(): 捕获当BeforeUpDown文
    """
    
    def __init__(
        self,
        hook_id: str,
        hook_type: HookType,
        config: Optional[HookConfig] = None,
    ):
        """
        Initialize Hook
        
        Args:
            hook_id: Hook 唯一标识
            hook_type: Hook Class型
            config: Hook Config
        """
        self.hook_id = hook_id
        self.hook_type = hook_type
        self.config = config or HookConfig()
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._state = HookState(type=hook_type)
        
        # CallbackFunction
        self._on_state_change: Optional[Callable[[HookState], None]] = None
        self._on_context_update: Optional[Callable[[Any], None]] = None
        
        logger.info(f"[{self.__class__.__name__}] Initialized: {hook_id}")
    
    @property
    def state(self) -> HookState:
        """当BeforeState"""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """YesNo正在Running"""
        return self._running
    
    def set_callbacks(
        self,
        on_state_change: Optional[Callable[[HookState], None]] = None,
        on_context_update: Optional[Callable[[Any], None]] = None,
    ):
        """SetCallbackFunction"""
        self._on_state_change = on_state_change
        self._on_context_update = on_context_update
    
    def _update_state(
        self,
        status: Optional[HookStatus] = None,
        target: Optional[str] = None,
        context: Optional[Any] = None,
        error: Optional[str] = None,
    ):
        """UpdateState"""
        if status is not None:
            self._state.status = status
        if target is not None:
            self._state.target = target
        if context is not None:
            self._state.context = context
        if error is not None:
            self._state.error = error
        
        if status == HookStatus.CONNECTED and self._state.connected_at is None:
            self._state.connected_at = datetime.now().isoformat()
        
        # TriggerCallback
        if self._on_state_change:
            try:
                self._on_state_change(self._state)
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] State change callback error: {e}")
    
    def _notify_context_update(self, context: Any):
        """NotifyUpDown文Update"""
        self._state.context = context
        
        if self._on_context_update:
            try:
                self._on_context_update(context)
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Context update callback error: {e}")
    
    async def start(self, target: Optional[str] = None) -> bool:
        """
        Start Hook
        
        Args:
            target: Target（如特定浏览器、特定Directory）
        
        Returns:
            YesNoSuccessStart
        """
        if self._running:
            logger.warning(f"[{self.__class__.__name__}] Already running")
            return True
        
        try:
            self._update_state(status=HookStatus.CONNECTING, target=target or "")
            
            # ChildClassImplement's Connectlogic
            success = await self._connect(target)
            
            if success:
                self._running = True
                self._update_state(status=HookStatus.CONNECTED)
                
                # StartCatchLoop
                self._task = asyncio.create_task(self._capture_loop())
                
                logger.info(f"[{self.__class__.__name__}] Started: {self.hook_id}")
                return True
            else:
                self._update_state(status=HookStatus.ERROR, error="Connection failed")
                return False
                
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Start failed: {e}")
            self._update_state(status=HookStatus.ERROR, error=str(e))
            return False
    
    async def stop(self) -> bool:
        """
        Stop Hook
        
        Returns:
            YesNoSuccessStop
        """
        if not self._running:
            return True
        
        try:
            self._running = False
            
            # CancelCatchTask
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
                self._task = None
            
            # ChildClassImplement's Disconnectlogic
            await self._disconnect()
            
            self._update_state(status=HookStatus.DISCONNECTED)
            self._state.connected_at = None
            
            logger.info(f"[{self.__class__.__name__}] Stopped: {self.hook_id}")
            return True
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Stop failed: {e}")
            return False
    
    async def _capture_loop(self):
        """捕获Loop"""
        while self._running:
            try:
                context = await self.capture()
                if context:
                    self._notify_context_update(context)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Capture error: {e}")
            
            await asyncio.sleep(self.config.capture_interval)
    
    @abstractmethod
    async def _connect(self, target: Optional[str] = None) -> bool:
        """
        Connect到Target（ChildClassImplement）
        
        Args:
            target: Target标识
            
        Returns:
            YesNoSuccessConnect
        """
        pass
    
    @abstractmethod
    async def _disconnect(self) -> bool:
        """
        DisconnectConnect（ChildClassImplement）
        
        Returns:
            YesNoSuccessDisconnect
        """
        pass
    
    @abstractmethod
    async def capture(self) -> Optional[Any]:
        """
        捕获当BeforeUpDown文（ChildClassImplement）
        
        Returns:
            UpDown文数据，None Table示捕获Failed
        """
        pass

