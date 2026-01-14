"""
NogicOS Concurrent管理器
==================

控制 Agent System的Concurrent资Source，Package括：
1. 任务槽位管理 - Limit同时Running的任务数
2. Window独占Lock - 防止多任务同时操作同一Window
3. API 调用限流 - 避免Trigger速率Limit

参考:
- ByteBot Concurrent控制
- asyncio Semaphore + Lock
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Optional, Dict, Set, TYPE_CHECKING
from datetime import datetime, timedelta

# alreadyDelete: host_agent Dependency，changeuseIndependent's  ConcurrencyConfig

logger = logging.getLogger(__name__)


@dataclass
class ConcurrencyConfig:
    """
    ConcurrentConfig
    
    独立ConfigClass，可与 AgentConfig DetachUsage
    """
    # TaskConcurrent
    max_concurrent_tasks: int = 3
    
    # API Rate Limit
    max_api_concurrency: int = 5
    
    # WindowLockTimeout
    window_lock_timeout_s: float = 300.0  # 5 Minute
    
    # API Callinterval（avoidTriggerspeedrateLimit）
    min_api_interval_ms: int = 100


@dataclass
class TaskSlotInfo:
    """任务槽位Info"""
    task_id: str
    acquired_at: datetime
    target_hwnds: Set[int] = field(default_factory=set)


@dataclass
class WindowLockInfo:
    """WindowLockInfo"""
    hwnd: int
    task_id: str
    acquired_at: datetime


class ConcurrencyManager:
    """
    Concurrent管理器
    
    负责管理：
    1. 任务槽位 - Limit同时Running的任务Count
    2. WindowLock - 确保同一Window不被多个任务同时操作
    3. API 限流 - Usage Semaphore LimitConcurrent API 调用
    
    UsageExample:
    ```python
    manager = ConcurrencyManager(config)
    
    # GetTaskslot
    if await manager.acquire_task_slot(task_id):
        try:
            # GetWindowLock
            await manager.acquire_window(hwnd)
            
            # Execute API Call（withRate Limit）
            async with manager.api_slot():
                result = await llm_call()
        finally:
            manager.release_window(hwnd)
            manager.release_task_slot(task_id)
    ```
    """
    
    def __init__(
        self, 
        config: Optional[ConcurrencyConfig] = None,
    ):
        """
        InitializeConcurrent管理器
        
        Args:
            config: ConcurrentConfig（Optional）
        """
        self.config = config or ConcurrencyConfig()
        
        # Taskslot
        self._active_tasks: Dict[str, TaskSlotInfo] = {}
        self._task_lock = asyncio.Lock()
        
        # WindowLock
        self._window_locks: Dict[int, asyncio.Lock] = {}
        self._window_owners: Dict[int, WindowLockInfo] = {}
        self._window_meta_lock = asyncio.Lock()
        
        # API Rate Limit
        self._api_semaphore = asyncio.Semaphore(self.config.max_api_concurrency)
        self._last_api_call: Optional[datetime] = None
        self._api_call_lock = asyncio.Lock()
        
        logger.info(
            f"ConcurrencyManager initialized: "
            f"max_tasks={self.config.max_concurrent_tasks}, "
            f"max_api={self.config.max_api_concurrency}"
        )
    
    # ========== Taskslotmanage ==========
    
    async def acquire_task_slot(
        self, 
        task_id: str,
        target_hwnds: Optional[Set[int]] = None,
    ) -> bool:
        """
        Get任务槽位
        
        Args:
            task_id: 任务 ID
            target_hwnds: TargetWindowSet
            
        Returns:
            YesNoSuccessGet槽位
        """
        async with self._task_lock:
            # CheckYesNoalreadyhavethisTask
            if task_id in self._active_tasks:
                logger.warning(f"Task {task_id} already has a slot")
                return True
            
            # CheckslotCount
            if len(self._active_tasks) >= self.config.max_concurrent_tasks:
                logger.info(
                    f"No available task slots: "
                    f"{len(self._active_tasks)}/{self.config.max_concurrent_tasks}"
                )
                return False
            
            # Allocateslot
            self._active_tasks[task_id] = TaskSlotInfo(
                task_id=task_id,
                acquired_at=datetime.now(),
                target_hwnds=target_hwnds or set(),
            )
            
            logger.debug(
                f"Task slot acquired: {task_id} "
                f"({len(self._active_tasks)}/{self.config.max_concurrent_tasks})"
            )
            return True
    
    def release_task_slot(self, task_id: str):
        """
        Release任务槽位
        
        Args:
            task_id: 任务 ID
        """
        if task_id in self._active_tasks:
            del self._active_tasks[task_id]
            logger.debug(
                f"Task slot released: {task_id} "
                f"({len(self._active_tasks)}/{self.config.max_concurrent_tasks})"
            )
    
    def get_active_tasks(self) -> Dict[str, TaskSlotInfo]:
        """Get活动任务List"""
        return dict(self._active_tasks)
    
    @property
    def available_slots(self) -> int:
        """Available槽位数"""
        return self.config.max_concurrent_tasks - len(self._active_tasks)
    
    # ========== WindowLockmanage ==========
    
    async def acquire_window(
        self, 
        hwnd: int,
        task_id: str = "",
        timeout: Optional[float] = None,
    ) -> bool:
        """
        GetWindow独占Lock
        
        Args:
            hwnd: Window句柄
            task_id: Request的任务 ID
            timeout: TimeoutTime（Second），None Table示UsageDefault值
            
        Returns:
            YesNoSuccessGetLock
        """
        timeout = timeout or self.config.window_lock_timeout_s
        
        # GetorCreateWindowLock
        async with self._window_meta_lock:
            if hwnd not in self._window_locks:
                self._window_locks[hwnd] = asyncio.Lock()
            lock = self._window_locks[hwnd]
        
        try:
            # tryGetLock
            acquired = await asyncio.wait_for(
                lock.acquire(),
                timeout=timeout,
            )
            
            if acquired:
                self._window_owners[hwnd] = WindowLockInfo(
                    hwnd=hwnd,
                    task_id=task_id,
                    acquired_at=datetime.now(),
                )
                logger.debug(f"Window lock acquired: hwnd={hwnd}, task={task_id}")
            
            return acquired
            
        except asyncio.TimeoutError:
            owner = self._window_owners.get(hwnd)
            owner_task = owner.task_id if owner else "unknown"
            logger.warning(
                f"Window lock timeout: hwnd={hwnd}, "
                f"current_owner={owner_task}"
            )
            return False
    
    def release_window(self, hwnd: int):
        """
        ReleaseWindowLock
        
        Args:
            hwnd: Window句柄
        """
        if hwnd in self._window_locks:
            lock = self._window_locks[hwnd]
            if lock.locked():
                lock.release()
                self._window_owners.pop(hwnd, None)
                logger.debug(f"Window lock released: hwnd={hwnd}")
    
    def get_window_owner(self, hwnd: int) -> Optional[str]:
        """
        GetWindow当Before所有者
        
        Args:
            hwnd: Window句柄
            
        Returns:
            拥有该WindowLock的任务 ID，或 None
        """
        info = self._window_owners.get(hwnd)
        return info.task_id if info else None
    
    def is_window_locked(self, hwnd: int) -> bool:
        """CheckWindowYesNo被Lock定"""
        if hwnd in self._window_locks:
            return self._window_locks[hwnd].locked()
        return False
    
    @asynccontextmanager
    async def window_lock(self, hwnd: int, task_id: str = ""):
        """
        WindowLockUpDown文管理器
        
        UsageExample:
        ```python
        async with manager.window_lock(hwnd, task_id):
            # exclusiveActionWindow
            await perform_action(hwnd)
        ```
        """
        acquired = await self.acquire_window(hwnd, task_id)
        if not acquired:
            raise RuntimeError(f"Failed to acquire window lock: hwnd={hwnd}")
        try:
            yield
        finally:
            self.release_window(hwnd)
    
    # ========== API Rate Limit ==========
    
    @asynccontextmanager
    async def api_slot(self):
        """
        API 调用槽位（限流）
        
        Usage Semaphore LimitConcurrent API 调用Count，
        并确保调用间隔不小于 min_api_interval_ms
        
        UsageExample:
        ```python
        async with manager.api_slot():
            result = await claude_api.call()
        ```
        """
        await self._api_semaphore.acquire()
        try:
            # ensureCallinterval
            async with self._api_call_lock:
                if self._last_api_call is not None:
                    elapsed = (datetime.now() - self._last_api_call).total_seconds() * 1000
                    if elapsed < self.config.min_api_interval_ms:
                        wait_ms = self.config.min_api_interval_ms - elapsed
                        await asyncio.sleep(wait_ms / 1000)
                
                self._last_api_call = datetime.now()
            
            yield
            
        finally:
            self._api_semaphore.release()
    
    @property
    def available_api_slots(self) -> int:
        """Available API 槽位数（近似值）"""
        # Semaphore nodirectlyGetwhenBeforeValue's Method，thisYesnearsimilarValue
        return self._api_semaphore._value  # type: ignore
    
    # ========== BatchAction ==========
    
    async def acquire_windows(
        self, 
        hwnds: Set[int],
        task_id: str,
    ) -> bool:
        """
        批量GetWindowLock
        
        要么全部GetSuccess，要么全部不Get（原Child性）
        
        Args:
            hwnds: Window句柄Set
            task_id: 任务 ID
            
        Returns:
            YesNo全部GetSuccess
        """
        acquired_hwnds: Set[int] = set()
        
        try:
            for hwnd in hwnds:
                if await self.acquire_window(hwnd, task_id, timeout=10.0):
                    acquired_hwnds.add(hwnd)
                else:
                    # GetFailed，Rollback
                    raise RuntimeError(f"Failed to acquire window: {hwnd}")
            
            return True
            
        except Exception:
            # RollbackalreadyGet's Lock
            for hwnd in acquired_hwnds:
                self.release_window(hwnd)
            return False
    
    def release_windows(self, hwnds: Set[int]):
        """批量ReleaseWindowLock"""
        for hwnd in hwnds:
            self.release_window(hwnd)
    
    # ========== resourceSourceCleanup ==========
    
    async def cleanup_stale_locks(self, max_age_s: float = 600.0):
        """
        Cleanup过期的WindowLock
        
        防止任务ExceptionExit导致的Lock泄漏
        
        Args:
            max_age_s: MaxLock持有Time（Second）
        """
        now = datetime.now()
        stale_hwnds = []
        
        for hwnd, info in self._window_owners.items():
            age = (now - info.acquired_at).total_seconds()
            if age > max_age_s:
                stale_hwnds.append(hwnd)
                logger.warning(
                    f"Releasing stale window lock: hwnd={hwnd}, "
                    f"task={info.task_id}, age={age:.1f}s"
                )
        
        for hwnd in stale_hwnds:
            self.release_window(hwnd)
    
    def reset(self):
        """
        Reset所有State（用于Test）
        
        Warning：会Release所有Lock和槽位
        """
        self._active_tasks.clear()
        
        for hwnd in list(self._window_locks.keys()):
            self.release_window(hwnd)
        self._window_locks.clear()
        self._window_owners.clear()
        
        self._last_api_call = None
        
        logger.info("ConcurrencyManager reset")
    
    def get_stats(self) -> Dict:
        """GetConcurrentStatisticsInfo"""
        return {
            "active_tasks": len(self._active_tasks),
            "max_tasks": self.config.max_concurrent_tasks,
            "locked_windows": len(self._window_owners),
            "api_semaphore_value": self._api_semaphore._value,  # type: ignore
            "max_api_concurrency": self.config.max_api_concurrency,
        }
    
    def __repr__(self) -> str:
        return (
            f"ConcurrencyManager("
            f"tasks={len(self._active_tasks)}/{self.config.max_concurrent_tasks}, "
            f"windows={len(self._window_owners)})"
        )


# ========== SingletonPattern ==========

_concurrency_manager: Optional[ConcurrencyManager] = None


def get_concurrency_manager(
    config: Optional[ConcurrencyConfig] = None,
) -> ConcurrencyManager:
    """GetGlobalConcurrent管理器（Singleton）"""
    global _concurrency_manager
    if _concurrency_manager is None:
        _concurrency_manager = ConcurrencyManager(config)
    return _concurrency_manager


def set_concurrency_manager(manager: ConcurrencyManager):
    """SetGlobalConcurrent管理器（用于Test）"""
    global _concurrency_manager
    _concurrency_manager = manager
