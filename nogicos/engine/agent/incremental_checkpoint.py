"""
NogicOS 增量Check点
==================

减少SerializeOn销，优化State持久化Performance。

Policy:
1. 计算State差异，只Save变化部分
2. 定期做全量Check点
3. Resume时Merge增量

参考:
- LangGraph Checkpointer
- Git 增量Commit
"""

import json
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CheckpointDelta:
    """Check点增量"""
    iteration: int
    new_messages: List[dict] = field(default_factory=list)
    status_change: Optional[str] = None
    last_tool_result: Optional[dict] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert为Dict"""
        result = {"iteration": self.iteration}
        if self.new_messages:
            result["new_messages"] = self.new_messages
        if self.status_change:
            result["status_change"] = self.status_change
        if self.last_tool_result:
            result["last_tool_result"] = self.last_tool_result
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class IncrementalCheckpointer:
    """
    增量Check点管理器
    
    减少Serialize和存储On销:
    - 每次只Save变化的Message
    - 每 N 次增量After做一次全量
    - Resume时AutoMerge
    
    UsageExample:
    ```python
    checkpointer = IncrementalCheckpointer(task_store)
    
    # SaveCheckPoint（AutoSelectincreaseamount/full）
    await checkpointer.save(task_id, current_state)
    
    # ResumeCheckPoint
    state = await checkpointer.restore(task_id)
    ```
    """
    
    # each 10 timeincreaseamountAfterdofull
    FULL_CHECKPOINT_INTERVAL = 10
    
    def __init__(self, task_store):
        """
        Initialize增量Check点管理器
        
        Args:
            task_store: 任务存储Instance (AsyncTaskStore)
        """
        self.task_store = task_store
        self._last_state: Dict[str, dict] = {}  # task_id -> last_state
        self._delta_count: Dict[str, int] = {}  # task_id -> delta_count
    
    async def save(self, task_id: str, state: dict) -> bool:
        """
        SaveCheck点（AutoSelect增量/全量）
        
        Args:
            task_id: 任务 ID
            state: 当BeforeState
            
        Returns:
            YesNoSaveSuccess
        """
        last_state = self._last_state.get(task_id, {})
        delta_count = self._delta_count.get(task_id, 0)
        
        # JudgeYesNoNeedfull
        needs_full = (
            delta_count >= self.FULL_CHECKPOINT_INTERVAL or
            task_id not in self._last_state
        )
        
        if needs_full:
            # fullSave
            await self.task_store.save_checkpoint(
                task_id,
                state.get("iteration", 0),
                state,
                is_full=True
            )
            self._last_state[task_id] = self._deep_copy(state)
            self._delta_count[task_id] = 0
            logger.debug(f"Full checkpoint saved for task {task_id}")
        else:
            # calculateandSaveincreaseamount
            delta = self._compute_delta(last_state, state)
            
            if delta:
                await self.task_store.save_checkpoint(
                    task_id,
                    state.get("iteration", 0),
                    delta,
                    is_full=False
                )
                # UpdatelocalCache
                self._apply_delta(self._last_state[task_id], delta)
                self._delta_count[task_id] = delta_count + 1
                logger.debug(f"Incremental checkpoint saved for task {task_id} (delta #{delta_count + 1})")
            else:
                logger.debug(f"No changes to checkpoint for task {task_id}")
        
        return True
    
    def _compute_delta(self, old_state: dict, new_state: dict) -> Optional[dict]:
        """
        计算State差异
        
        Args:
            old_state: OldState
            new_state: NewState
            
        Returns:
            差异Dict，如果无变化则Return None
        """
        delta = {}
        
        # CheckMessageincreaseamount
        old_messages = old_state.get("messages", [])
        new_messages = new_state.get("messages", [])
        
        if len(new_messages) > len(old_messages):
            delta["new_messages"] = new_messages[len(old_messages):]
        
        # CheckStatechange
        for key in ["status", "iteration", "last_tool_result", "current_hwnd"]:
            old_val = old_state.get(key)
            new_val = new_state.get(key)
            if new_val != old_val:
                delta[key] = new_val
        
        # Check agent_status change
        old_agent_status = old_state.get("agent_status")
        new_agent_status = new_state.get("agent_status")
        if new_agent_status != old_agent_status:
            delta["agent_status"] = new_agent_status
        
        return delta if delta else None
    
    def _apply_delta(self, state: dict, delta: dict):
        """
        将增量应用到State
        
        Args:
            state: 要Update的State（原地Modify）
            delta: 增量数据
        """
        if "new_messages" in delta:
            if "messages" not in state:
                state["messages"] = []
            state["messages"].extend(delta["new_messages"])
        
        for key in ["status", "iteration", "last_tool_result", "current_hwnd", "agent_status"]:
            if key in delta:
                state[key] = delta[key]
    
    def _deep_copy(self, obj: Any) -> Any:
        """深拷贝（Usage JSON Serialize）"""
        return json.loads(json.dumps(obj))
    
    async def restore(self, task_id: str) -> Optional[dict]:
        """
        ResumeCheck点（Merge全量 + 增量）
        
        Args:
            task_id: 任务 ID
            
        Returns:
            Resume的State，如果没有Check点则Return None
        """
        checkpoints = await self.task_store.get_all_checkpoints(task_id)
        
        if not checkpoints:
            return None
        
        # findtomostnear's fullCheckPoint
        full_checkpoint = None
        deltas = []
        
        for cp in reversed(checkpoints):
            if cp.get("is_full"):
                full_checkpoint = cp.get("state")
                break
            else:
                deltas.insert(0, cp.get("state"))
        
        if not full_checkpoint:
            # nofullCheckPoint，tryUsageFirstaincreaseamount
            if deltas:
                logger.warning(f"No full checkpoint found for task {task_id}, using first delta")
                full_checkpoint = deltas[0]
                deltas = deltas[1:]
            else:
                return None
        
        # Applyallincreaseamount
        state = self._deep_copy(full_checkpoint)
        for delta in deltas:
            self._apply_delta(state, delta)
        
        # UpdatelocalCache
        self._last_state[task_id] = state
        self._delta_count[task_id] = len(deltas)
        
        logger.info(f"Restored checkpoint for task {task_id} (full + {len(deltas)} deltas)")
        return state
    
    def clear_cache(self, task_id: str = None):
        """
        Clear本地Cache
        
        Args:
            task_id: Specify任务 ID，或 None Clear所有
        """
        if task_id:
            self._last_state.pop(task_id, None)
            self._delta_count.pop(task_id, None)
        else:
            self._last_state.clear()
            self._delta_count.clear()
    
    def get_stats(self) -> dict:
        """GetStatisticsInfo"""
        return {
            "cached_tasks": len(self._last_state),
            "delta_counts": dict(self._delta_count),
        }


# ========== FactoryFunction ==========

def create_checkpointer(task_store) -> IncrementalCheckpointer:
    """Create增量Check点管理器"""
    return IncrementalCheckpointer(task_store)
