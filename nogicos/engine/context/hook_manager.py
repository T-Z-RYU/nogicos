# -*- coding: utf-8 -*-
"""
Hook Manager - Hook 管理器

管理所有 Hook 的生命Cycle：
- Connect/Disconnect
- StateSync到 Context Store
- WebSocket Event推送
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .store import (
    ContextStore, 
    get_context_store,
    HookType, 
    HookStatus, 
    HookState,
    BrowserContext,
    DesktopContext,
    FileContext,
    AppContext,
    AppType,
)
from .hooks import BaseHook, HookConfig, BrowserHook, DesktopHook, FileHook
from .hooks.desktop_hook import get_all_windows, BROWSER_PROCESSES

logger = logging.getLogger(__name__)


@dataclass
class ConnectionTarget:
    """ConnectTarget"""
    type: str           # browser, desktop, file
    target: str = ""    # ConcreteTarget（like chrome, DirectoryPath）
    config: Optional[HookConfig] = None


class HookManager:
    """
    Hook 管理器
    
    统一管理所有 Hook 的生命Cycle
    """
    
    # Hook ClasstypetoClass's Map
    HOOK_CLASSES = {
        "browser": BrowserHook,
        "desktop": DesktopHook,
        "file": FileHook,
    }
    
    def __init__(self, context_store: Optional[ContextStore] = None):
        """
        Initialize Hook Manager
        
        Args:
            context_store: Context Store Instance，None 则UsageSingleton
        """
        self._store = context_store or get_context_store()
        self._hooks: Dict[str, BaseHook] = {}
        self._lock = asyncio.Lock()
        
        # EventCallback（for WebSocket Push）
        self._on_state_change: Optional[Callable[[str, Dict], None]] = None
        
        logger.info("[HookManager] Initialized")
    
    def set_state_change_callback(self, callback: Callable[[str, Dict], None]):
        """
        SetState变更Callback
        
        用于 WebSocket 推送State变更到Before端
        
        Args:
            callback: CallbackFunction (hook_id, state_dict) -> None
        """
        self._on_state_change = callback
    
    async def connect(self, target: ConnectionTarget) -> bool:
        """
        Connect到Target
        
        Args:
            target: ConnectTargetConfig
            
        Returns:
            YesNoSuccessConnect
        """
        async with self._lock:
            hook_id = f"{target.type}_{target.target}" if target.target else target.type
            
            # CheckYesNoalreadyConnect
            if hook_id in self._hooks:
                existing_hook = self._hooks[hook_id]
                if existing_hook.is_running:
                    logger.warning(f"[HookManager] Hook already connected: {hook_id}")
                    return True
            
            # Create Hook Instance
            hook_class = self.HOOK_CLASSES.get(target.type)
            if not hook_class:
                logger.error(f"[HookManager] Unknown hook type: {target.type}")
                return False
            
            hook = hook_class(
                hook_id=hook_id,
                config=target.config or HookConfig(),
            )
            
            # SetCallback
            hook.set_callbacks(
                on_state_change=lambda state: self._handle_state_change(hook_id, state),
                on_context_update=lambda ctx: self._handle_context_update(hook_id, ctx),
            )
            
            # Start Hook
            success = await hook.start(target.target)
            
            if success:
                self._hooks[hook_id] = hook
                logger.info(f"[HookManager] Connected: {hook_id}")
                return True
            else:
                logger.error(f"[HookManager] Failed to connect: {hook_id}")
                return False
    
    async def disconnect(self, hook_id: str) -> bool:
        """
        DisconnectConnect
        
        Args:
            hook_id: Hook ID
            
        Returns:
            YesNoSuccessDisconnect
        """
        async with self._lock:
            if hook_id not in self._hooks:
                logger.warning(f"[HookManager] Hook not found: {hook_id}")
                return True
            
            hook = self._hooks[hook_id]
            success = await hook.stop()
            
            if success:
                del self._hooks[hook_id]
                self._store.remove_hook(hook_id)
                logger.info(f"[HookManager] Disconnected: {hook_id}")
            
            return success
    
    async def disconnect_all(self) -> bool:
        """Disconnect所有Connect"""
        async with self._lock:
            results = []
            for hook_id in list(self._hooks.keys()):
                hook = self._hooks[hook_id]
                success = await hook.stop()
                results.append(success)
                if success:
                    del self._hooks[hook_id]
                    self._store.remove_hook(hook_id)
            
            logger.info(f"[HookManager] Disconnected all hooks")
            return all(results)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get所有 Hook State
        
        Returns:
            StateDict
        """
        status = {
            "hooks": {},
            "available_types": list(self.HOOK_CLASSES.keys()),
        }
        
        for hook_id, hook in self._hooks.items():
            status["hooks"][hook_id] = {
                "type": hook.hook_type.value,
                "status": hook.state.status.value,
                "target": hook.state.target,
                "connected_at": hook.state.connected_at,
                "context": hook.state.context.__dict__ if hook.state.context else None,
            }
        
        return status
    
    def get_hook(self, hook_id: str) -> Optional[BaseHook]:
        """Get Hook Instance"""
        return self._hooks.get(hook_id)
    
    def is_connected(self, hook_type: str) -> bool:
        """Check某Class型的 Hook YesNo已Connect"""
        # [Repair #15]Not NeedaddLockbecauseonlyYesRead，butneedensureTraverseSecurity
        for hook_id, hook in list(self._hooks.items()):
            if hook.hook_type.value == hook_type and hook.is_running:
                return True
        return False
    
    def _handle_state_change(self, hook_id: str, state: HookState):
        """HandleState变更"""
        # Syncto Context Store
        self._store.set_hook_state(hook_id, state)

        # [Repair #16]CallbackExceptionnotBlockedmainstreamprocess
        if self._on_state_change:
            try:
                self._on_state_change(hook_id, state.to_dict())
            except Exception as e:
                logger.error(f"[HookManager] State change callback error: {e}")
                # continueExecute，notBlocked
    
    def _handle_context_update(self, hook_id: str, context: Any):
        """HandleUpDown文Update"""
        # Syncto Context Store
        self._store.update_context(hook_id, context)
        
        # TriggerCallback（WebSocket Push）
        if self._on_state_change:
            try:
                hook = self._hooks.get(hook_id)
                if hook:
                    self._on_state_change(hook_id, hook.state.to_dict())
            except Exception as e:
                logger.error(f"[HookManager] Context update callback error: {e}")
    
    # ============== convenientMethod ==============
    
    async def connect_browser(self, browser: Optional[str] = None, config: Optional[HookConfig] = None) -> bool:
        """
        Connect浏览器
        
        Args:
            browser: 浏览器Class型（chrome, firefox, edge），None Auto检测
            config: Hook Config
        """
        return await self.connect(ConnectionTarget(
            type="browser",
            target=browser or "",
            config=config,
        ))
    
    async def connect_desktop(self, config: Optional[HookConfig] = None) -> bool:
        """Connect桌面感知"""
        return await self.connect(ConnectionTarget(
            type="desktop",
            target="",
            config=config,
        ))
    
    async def connect_file(self, directories: Optional[str] = None, config: Optional[HookConfig] = None) -> bool:
        """
        ConnectFileListen
        
        Args:
            directories: 要Listen的Directory，多个用分号分隔
            config: Hook Config
        """
        return await self.connect(ConnectionTarget(
            type="file",
            target=directories or "",
            config=config,
        ))
    
    async def get_browser_context(self) -> Optional[BrowserContext]:
        """Get浏览器UpDown文"""
        for hook_id, hook in self._hooks.items():
            if hook.hook_type == HookType.BROWSER and hook.state.context:
                return hook.state.context
        return None
    
    async def get_desktop_context(self) -> Optional[DesktopContext]:
        """Get桌面UpDown文"""
        for hook_id, hook in self._hooks.items():
            if hook.hook_type == HookType.DESKTOP and hook.state.context:
                return hook.state.context
        return None
    
    async def get_file_context(self) -> Optional[FileContext]:
        """GetFileUpDown文"""
        for hook_id, hook in self._hooks.items():
            if hook.hook_type == HookType.FILE and hook.state.context:
                return hook.state.context
        return None
    
    # ============== generalApplyConnect（NewversionInterface） ==============
    
    async def connect_to_window(self, hwnd: int, window_title: str = "") -> Optional[AppContext]:
        """
        Connect到SpecifyWindow（通用应用Connect器）
        
        这YesNew版的统一Interface，可以Connect任意应用Window。
        Root据应用Class型AutoSelect合适的 Hook Policy。
        
        Args:
            hwnd: Window句柄
            window_title: Windowtitle（Optional，用于Display）
            
        Returns:
            AppContext 或 None
        """
        # fromWindowListMediumFindWindowInfo
        windows = get_all_windows()
        target_window = None
        for w in windows:
            if w.hwnd == hwnd:
                target_window = w
                break
        
        if not target_window:
            logger.warning(f"[HookManager] Window not found: HWND={hwnd}")
            return None
        
        # OKApplyClasstype
        app_name_lower = target_window.app_name.lower()
        if app_name_lower in BROWSER_PROCESSES:
            app_type = AppType.BROWSER.value
            hook_type = "browser"
        elif app_name_lower in ["code.exe", "cursor.exe"]:
            app_type = AppType.IDE.value
            hook_type = "desktop"
        elif app_name_lower in ["figma.exe", "sketch.exe"]:
            app_type = AppType.DESIGN.value
            hook_type = "desktop"
        else:
            app_type = AppType.OTHER.value
            hook_type = "desktop"
        
        # Connecttoshould's  Hook
        success = await self.connect(ConnectionTarget(
            type=hook_type,
            target=target_window.app_name,
        ))
        
        if not success:
            return None
        
        # Creategeneral AppContext
        app_context = AppContext(
            hwnd=target_window.hwnd,
            title=target_window.title,
            app_name=target_window.app_name,
            app_display_name=target_window.app_display_name,
            app_type=app_type,
            x=target_window.x,
            y=target_window.y,
            width=target_window.width,
            height=target_window.height,
        )
        
        # IfYesBrowser，tryGetMoreInfo
        if app_type == AppType.BROWSER.value:
            browser_hook = self.get_hook(hook_type)
            if browser_hook and browser_hook.state.context:
                browser_ctx = browser_hook.state.context
                if hasattr(browser_ctx, 'url'):
                    app_context.url = browser_ctx.url
                if hasattr(browser_ctx, 'tab_count'):
                    app_context.tab_count = browser_ctx.tab_count
        
        logger.info(f"[HookManager] Connected to window: {target_window.title} ({app_type})")
        return app_context
    
    def get_connected_windows(self) -> List[AppContext]:
        """
        Get所有已Connect的Window（通用Interface）
        
        Returns:
            AppContext List
        """
        result = []
        
        for hook_id, hook in self._hooks.items():
            if hook.is_running and hook.state.context:
                ctx = hook.state.context
                
                # Convertfor AppContext
                if isinstance(ctx, BrowserContext):
                    result.append(AppContext(
                        hwnd=ctx.hwnd if hasattr(ctx, 'hwnd') else 0,
                        title=ctx.title,
                        app_name=ctx.app,
                        app_display_name=ctx.app,
                        app_type=AppType.BROWSER.value,
                        url=ctx.url,
                        tab_count=ctx.tab_count,
                    ))
                elif isinstance(ctx, DesktopContext):
                    result.append(AppContext(
                        hwnd=0,
                        title=ctx.active_window,
                        app_name=ctx.active_app,
                        app_display_name=ctx.active_app,
                        app_type=AppType.OTHER.value,
                    ))
        
        return result


# GlobalSingleton
_hook_manager: Optional[HookManager] = None
_manager_lock: Optional[asyncio.Lock] = None


def _get_manager_lock() -> asyncio.Lock:
    """DelayedCreate Lock，确保在EventLoopMediumCreate"""
    global _manager_lock
    if _manager_lock is None:
        _manager_lock = asyncio.Lock()
    return _manager_lock


async def get_hook_manager() -> HookManager:
    """Get Hook Manager Singleton"""
    global _hook_manager
    lock = _get_manager_lock()
    async with lock:
        if _hook_manager is None:
            _hook_manager = HookManager()
        return _hook_manager

