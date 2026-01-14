"""
NogicOS State管理器
==================

建立单一StateWrite点，解决State不一致问题。

设计原则:
1. 所有StateModify必须通过此Class
2. ModifyBeforeAutoVerify合法性
3. ModifyAfterAuto持久化 + Event广播

参考:
- LangGraph Checkpointer (get_state / update_state)
- UFO Blackboard (State共享)
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .events import AgentEvent, EventType
from .event_bus import EventBus, get_event_bus
from .async_db import AsyncTaskStore
from .types import TaskStatus, AgentStatus  # from types.py systemoneImport

logger = logging.getLogger(__name__)


class InvalidTransitionError(Exception):
    """非法StateConvert"""
    pass


class TaskNotFoundError(Exception):
    """任务不存在"""
    pass


@dataclass
class TaskState:
    """任务完整State"""
    task_id: str
    status: TaskStatus
    agent_status: AgentStatus
    iteration: int
    current_hwnd: Optional[int]
    messages: List[Dict[str, Any]]
    last_tool_result: Optional[Dict[str, Any]]
    error: Optional[str]


class TaskStateManager:
    """
    任务State管理器 - 唯一的StateModify入口
    
    UsageExample:
    ```python
    manager = TaskStateManager(task_store, event_bus)
    
    # StateConvert
    await manager.transition(task_id, TaskStatus.RUNNING)
    
    # GetState
    status = await manager.get_status(task_id)
    
    # GetCompleteState（Alignment LangGraph）
    state = await manager.get_state(task_id)
    ```
    """
    
    # Legal's StateConvert
    VALID_TRANSITIONS: Dict[TaskStatus, List[TaskStatus]] = {
        TaskStatus.PENDING: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
        TaskStatus.RUNNING: [
            TaskStatus.COMPLETED, 
            TaskStatus.FAILED, 
            TaskStatus.NEEDS_HELP, 
            TaskStatus.INTERRUPTED, 
            TaskStatus.PAUSED
        ],
        TaskStatus.PAUSED: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
        TaskStatus.INTERRUPTED: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
        TaskStatus.NEEDS_HELP: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
        TaskStatus.COMPLETED: [],  # final state
        TaskStatus.FAILED: [],     # final state
        TaskStatus.CANCELLED: [],  # final state
    }
    
    def __init__(
        self, 
        task_store: AsyncTaskStore, 
        event_bus: Optional[EventBus] = None,
    ):
        """
        InitializeState管理器
        
        Args:
            task_store: Async任务存储
            event_bus: Event总线（DefaultUsageGlobalSingleton）
        """
        self.task_store = task_store
        self.event_bus = event_bus or get_event_bus()
        self._cache: Dict[str, TaskStatus] = {}  # InnerstoreCache
        self._agent_status_cache: Dict[str, AgentStatus] = {}
    
    async def create_task(
        self, 
        task_id: str, 
        task_text: str,
        target_hwnds: Optional[List[int]] = None,
    ) -> bool:
        """
        CreateNew任务
        
        Args:
            task_id: 任务 ID
            task_text: 任务描述
            target_hwnds: TargetWindow句柄List
            
        Returns:
            YesNoCreateSuccess
        """
        # CreateTaskRecord
        await self.task_store.create_task(task_id, task_text, target_hwnds)
        
        # InitializeCache
        self._cache[task_id] = TaskStatus.PENDING
        self._agent_status_cache[task_id] = AgentStatus.IDLE
        
        # PublishEvent
        await self.event_bus.publish(AgentEvent.create(
            event_type=EventType.TASK_CREATED,
            task_id=task_id,
            payload={
                "task_text": task_text,
                "target_hwnds": target_hwnds or [],
            }
        ))
        
        logger.info(f"Task created: {task_id}")
        return True
    
    async def transition(
        self, 
        task_id: str, 
        new_status: TaskStatus,
        reason: Optional[str] = None,
    ) -> bool:
        """
        StateConvert - 唯一的StateModify入口
        
        Args:
            task_id: 任务 ID
            new_status: NewState
            reason: Convert原因（Optional）
            
        Returns:
            YesNoConvertSuccess
            
        Raises:
            TaskNotFoundError: 任务不存在
            InvalidTransitionError: 非法StateConvert
        """
        # 1. GetwhenBeforeState
        current = await self._get_current_status(task_id)
        if current is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        # 2. CheckYesNoYessameState（poweretc）
        if current == new_status:
            logger.debug(f"Task {task_id} already in status {new_status.value}")
            return True
        
        # 3. VerifyConvertLegalproperty
        valid_targets = self.VALID_TRANSITIONS.get(current, [])
        if new_status not in valid_targets:
            raise InvalidTransitionError(
                f"Invalid transition: {current.value} -> {new_status.value}. "
                f"Valid targets: {[s.value for s in valid_targets]}"
            )
        
        # 4. Persistence
        await self.task_store.update_status(task_id, new_status.value)
        
        # 5. UpdateCache
        self._cache[task_id] = new_status
        
        # 6. Update Agent State
        agent_status = self._derive_agent_status(new_status)
        self._agent_status_cache[task_id] = agent_status
        
        # 7. PublishEvent
        event_type = self._status_to_event_type(new_status)
        await self.event_bus.publish(AgentEvent.create(
            event_type=event_type,
            task_id=task_id,
            payload={
                "status": new_status.value,
                "previous_status": current.value,
                "reason": reason,
                "agent_status": agent_status.value,
            }
        ))
        
        logger.info(f"Task {task_id}: {current.value} -> {new_status.value}")
        return True
    
    async def get_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        Get任务State（PriorityInner存Cache）
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务State，或 None（任务不存在）
        """
        if task_id in self._cache:
            return self._cache[task_id]
        return await self._get_current_status(task_id)
    
    async def get_agent_status(self, task_id: str) -> Optional[AgentStatus]:
        """Get Agent State"""
        if task_id in self._agent_status_cache:
            return self._agent_status_cache[task_id]
        
        task_status = await self.get_status(task_id)
        if task_status:
            return self._derive_agent_status(task_status)
        return None
    
    async def get_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get完整State（对齐 LangGraph）
        
        Args:
            task_id: 任务 ID
            
        Returns:
            完整StateDict
        """
        task = await self.task_store.get_task(task_id)
        if not task:
            return None
        
        checkpoint = await self.task_store.restore_checkpoint(task_id)
        messages = await self.task_store.get_messages(task_id)
        
        # fromCacheGetState，NothenSecurityParse
        if task_id in self._cache:
            status = self._cache[task_id]
        else:
            status = await self._get_current_status(task_id) or TaskStatus.PENDING
        
        # fromCacheGet agent_status，Nothenfrom task_status derive
        if task_id in self._agent_status_cache:
            agent_status = self._agent_status_cache[task_id]
        else:
            agent_status = self._derive_agent_status(status)
            self._agent_status_cache[task_id] = agent_status  # backfillCache
        
        return {
            "task": task,
            "checkpoint": checkpoint,
            "messages": messages,
            "status": status,
            "agent_status": agent_status,
        }
    
    async def update_state(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        UpdateState（对齐 LangGraph）
        
        Args:
            task_id: 任务 ID
            updates: UpdateDict
            
        Returns:
            YesNoUpdateSuccess
        """
        # StateUpdate
        if "status" in updates:
            status = updates["status"]
            if isinstance(status, str):
                status = TaskStatus(status)
            await self.transition(task_id, status)
        
        # CheckPointUpdate
        if "checkpoint" in updates:
            await self.task_store.save_checkpoint(
                task_id, 
                updates["checkpoint"].get("iteration", 0),
                updates["checkpoint"].get("state", {})
            )
        
        # MessageUpdate
        if "messages" in updates:
            for msg in updates["messages"]:
                await self.task_store.save_message(
                    task_id,
                    msg.get("role", "user"),
                    msg.get("content", "")
                )
        
        return True
    
    async def set_agent_status(self, task_id: str, agent_status: AgentStatus):
        """
        Set Agent State（不改变任务State）
        
        用于细粒度State控制，如：WaitConfirm、思考Medium等
        """
        self._agent_status_cache[task_id] = agent_status
        
        # Rootdata AgentStatus Selectcorrect's EventClasstype
        event_type_map = {
            AgentStatus.CONFIRM: EventType.USER_CONFIRM_REQUIRED,  # explicitNeedUserConfirm
            AgentStatus.IDLE: EventType.AGENT_IDLE,
            AgentStatus.PAUSED: EventType.AGENT_WAITING,
            AgentStatus.ACTIVE: EventType.AGENT_EXECUTING,
        }
        event_type = event_type_map.get(agent_status, EventType.AGENT_EXECUTING)
        
        await self.event_bus.publish(AgentEvent.create(
            event_type=event_type,
            task_id=task_id,
            payload={"agent_status": agent_status.value}
        ))
    
    async def _get_current_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        从持久化存储GetState
        
        对未知State值进Row兜底Handle，避免版本迁移或数据Exception导致Crash
        """
        task = await self.task_store.get_task(task_id)
        if not task:
            return None
        
        status_value = task.get("status")
        if status_value is None:
            logger.warning(f"Task {task_id} has no status, defaulting to PENDING")
            status = TaskStatus.PENDING
        else:
            try:
                status = TaskStatus(status_value)
            except ValueError:
                # UnknownStateValue，RecordWarningandFallbackto FAILED
                logger.warning(
                    f"Task {task_id} has unknown status '{status_value}', "
                    f"defaulting to FAILED for safety"
                )
                status = TaskStatus.FAILED
                # PersistencerepaircorrectAfter's State
                await self.task_store.update_status(task_id, status.value)
        
        self._cache[task_id] = status
        return status
    
    def _status_to_event_type(self, status: TaskStatus) -> EventType:
        """State映射到EventClass型"""
        mapping = {
            TaskStatus.PENDING: EventType.TASK_CREATED,
            TaskStatus.RUNNING: EventType.TASK_STARTED,
            TaskStatus.COMPLETED: EventType.TASK_COMPLETED,
            TaskStatus.FAILED: EventType.TASK_FAILED,
            TaskStatus.INTERRUPTED: EventType.TASK_INTERRUPTED,
            TaskStatus.PAUSED: EventType.TASK_PAUSED,
            TaskStatus.CANCELLED: EventType.TASK_CANCELLED,
            TaskStatus.NEEDS_HELP: EventType.USER_CONFIRM_REQUIRED,  # NeedHelp -> UserConfirm
        }
        return mapping.get(status, EventType.TASK_STARTED)
    
    def _derive_agent_status(self, task_status: TaskStatus) -> AgentStatus:
        """从任务State推导 Agent State"""
        if task_status == TaskStatus.RUNNING:
            return AgentStatus.ACTIVE
        elif task_status == TaskStatus.PAUSED:
            return AgentStatus.PAUSED
        elif task_status == TaskStatus.NEEDS_HELP:
            return AgentStatus.CONFIRM
        else:
            return AgentStatus.IDLE
    
    def is_terminal(self, status: TaskStatus) -> bool:
        """CheckYesNo为终态"""
        return status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    def clear_cache(self, task_id: Optional[str] = None):
        """
        ClearCache
        
        Args:
            task_id: Specify任务 ID，或 None Clear所有
        """
        if task_id:
            self._cache.pop(task_id, None)
            self._agent_status_cache.pop(task_id, None)
        else:
            self._cache.clear()
            self._agent_status_cache.clear()


# ========== SingletonPattern ==========

_state_manager: Optional[TaskStateManager] = None


async def get_state_manager(task_store: Optional[AsyncTaskStore] = None) -> TaskStateManager:
    """GetGlobalState管理器（Singleton）"""
    global _state_manager
    if _state_manager is None:
        if task_store is None:
            from .async_db import get_task_store
            task_store = await get_task_store()
        _state_manager = TaskStateManager(task_store)
    return _state_manager


def set_state_manager(manager: TaskStateManager):
    """SetGlobalState管理器（用于Test）"""
    global _state_manager
    _state_manager = manager
