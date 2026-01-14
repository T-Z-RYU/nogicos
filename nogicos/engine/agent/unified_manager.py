# -*- coding: utf-8 -*-
"""
NogicOS Unified Agent Manager
=============================

统一的 Agent 管理器，Usage ReActAgent 作为Core。
串联所有已有Module：PlanCache、Memory、ContextStore、Verification。

这Yes NogicOS 的"大脑"，负责：
1. 任务调度和生命Cycle管理
2. UpDown文注入（从 Hook SystemGet）
3. 计划Cache（复用Success模式）
4. 记忆管理（长期学习）
5. ExecuteVerify（确保Result正确）
"""

import asyncio
import logging
import time
import uuid
from typing import Optional, Dict, List, Any, Callable, Awaitable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Core Agent
from .react_agent import ReActAgent, AgentResult
from .modes import AgentMode

# alreadyhaveModule - nowneedstringconnectstartfrom
# Plan Cache
try:
    from .plan_cache import PlanCache, get_plan_cache, CachedPlan
    PLAN_CACHE_AVAILABLE = True
except ImportError as e:
    PLAN_CACHE_AVAILABLE = False
    PlanCache = None
    get_plan_cache = None
    CachedPlan = None
    logger.warning(f"[UnifiedManager] PlanCache not available: {e}")

# Context Store - Hook System's UpDowntext
try:
    from ..context import get_context_store, ContextStore, get_context_injector, ContextConfig
    CONTEXT_STORE_AVAILABLE = True
except ImportError:
    CONTEXT_STORE_AVAILABLE = False
    get_context_store = None
    get_context_injector = None
    ContextConfig = None
    logger.warning("[UnifiedManager] ContextStore not available")

# Memory - Longterm memory
try:
    from ..knowledge.store import SemanticMemoryStore, get_memory_store
    MEMORY_AVAILABLE = True
    get_memory_manager = get_memory_store  # othername
except ImportError:
    try:
        from .imports import MEMORY_AVAILABLE, get_memory_store
        if MEMORY_AVAILABLE:
            get_memory_manager = get_memory_store
        else:
            get_memory_manager = None
    except ImportError:
        MEMORY_AVAILABLE = False
        get_memory_manager = None
        logger.warning("[UnifiedManager] Memory not available")

# Verification - ResultVerify
try:
    from .verification import AnswerVerifier, VerifyResult
    VERIFICATION_AVAILABLE = True
except ImportError:
    VERIFICATION_AVAILABLE = False
    AnswerVerifier = None
    logger.warning("[UnifiedManager] Verification not available")

# WebSocket Broadcast
try:
    from ..server.websocket import StatusServer
except ImportError:
    StatusServer = None


@dataclass
class TaskInfo:
    """任务Info"""
    task_id: str
    task_text: str
    target_hwnds: Optional[List[int]] = None
    session_id: str = "default"
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # ExecuteStatistics
    cache_hit: bool = False
    iterations: int = 0
    verification_passed: bool = False


class UnifiedAgentManager:
    """
    统一的 Agent 管理器
    
    Core：ReActAgent（已串联 PlanCache、Memory）
    增强：ContextStore 注入、Verification Verify
    """
    
    def __init__(self):
        self._initialized = False
        self._lock = asyncio.Lock()
        
        # Core Agent
        self._agent: Optional[ReActAgent] = None
        
        # alreadyhaveModule
        self._plan_cache: Optional[PlanCache] = None
        self._context_store = None
        self._memory_manager = None
        self._verifier = None
        
        # Taskmanage
        self._active_tasks: Dict[str, TaskInfo] = {}
        self._running_task: Optional[asyncio.Task] = None
        
        # WebSocket Broadcast
        self._status_server: Optional[StatusServer] = None
    
    async def initialize(self, status_server=None):
        """Initialize管理器，串联所有Module"""
        if self._initialized:
            return
        
        self._status_server = status_server
        
        # 1. InitializeCore Agent
        self._agent = ReActAgent(status_server=status_server)
        logger.info("[UnifiedManager] ReActAgent initialized")
        
        # 2. stringconnect PlanCache（ReActAgent Innerpartalreadyhave，butwealsoretainReference）
        if PLAN_CACHE_AVAILABLE:
            self._plan_cache = get_plan_cache()
            stats = self._plan_cache.get_stats()
            logger.info(f"[UnifiedManager] PlanCache connected: {stats.get('total_plans', 0)} cached plans")
        
        # 3. stringconnect ContextStore（from Hook SystemGetUpDowntext）
        if CONTEXT_STORE_AVAILABLE and get_context_store:
            self._context_store = get_context_store()
            logger.info("[UnifiedManager] ContextStore connected")
        
        # 4. stringconnect Memory（Longterm memory）
        if MEMORY_AVAILABLE and get_memory_manager:
            try:
                self._memory_manager = get_memory_manager()
                logger.info("[UnifiedManager] Memory connected")
            except Exception as e:
                logger.warning(f"[UnifiedManager] Memory init failed: {e}")
        
        # 5. stringconnect Verification（ResultVerify）
        if VERIFICATION_AVAILABLE and AnswerVerifier:
            self._verifier = AnswerVerifier()
            logger.info("[UnifiedManager] Verification connected")
        
        self._initialized = True
        logger.info("[UnifiedManager] All modules connected!")
    
    def _build_context_from_hooks(self, target_hwnds: Optional[List[int]] = None) -> str:
        """从 Hook System构建UpDown文，并Usage ContextInjector 增强"""
        context_parts = []
        
        # === 1. from Hook SystemGetrealtimeUpDowntext ===
        if self._context_store:
            try:
                # 1a. GetConnect's WindowInfo
                if hasattr(self._context_store, 'get_connected_windows'):
                    windows = self._context_store.get_connected_windows()
                    if windows:
                        context_parts.append("## alreadyConnect's ApplyWindow")
                        for w in windows:
                            context_parts.append(f"- {w.get('title', 'Unknown')} (HWND: {w.get('hwnd')})")
                
                # 1b. IfhaveTargetWindow，GetitsdetailedInfo
                if target_hwnds:
                    context_parts.append(f"\n## TargetWindow: {target_hwnds}")
                
                # 1c. Getmostnear's UpDowntext
                if hasattr(self._context_store, 'format_context_prompt'):
                    hook_context = self._context_store.format_context_prompt()
                    if hook_context:
                        context_parts.append(f"\n## EnvironmentUpDowntext\n{hook_context}")
            except Exception as e:
                logger.warning(f"[UnifiedManager] Hook context failed: {e}")
        
        # === 2. Usage ContextInjector EnhancementUpDowntext（UserInfo、memoryetc）===
        if get_context_injector is not None and ContextConfig is not None:
            try:
                injector = get_context_injector()
                config = ContextConfig(
                    include_user_info=True,
                    include_workspace_layout=False,  # avoidoverLong
                    include_terminal_info=False,  # Hook Systemalreadyhave
                    include_memories=True,
                )
                # inject("") ReturnpureUpDowntextCharacterstring
                enhanced = injector.inject("", session_id="default", config=config)
                if enhanced and enhanced.strip():
                    # RemoveEmpty's  user_query Packageinstall
                    enhanced = enhanced.replace("<user_query>\n\n</user_query>", "").strip()
                    if enhanced:
                        context_parts.append(f"\n{enhanced}")
            except Exception as e:
                logger.warning(f"[UnifiedManager] ContextInjector failed: {e}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    async def start_task(
        self,
        task: str,
        target_hwnds: Optional[List[int]] = None,
        max_iterations: int = 50,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """
        Start任务 - 入口Method
        
        流程：
        1. Read ContextStore（知道当BeforeWindowState）
        2. Query PlanCache（有Success模式？复用！）
        3. Execute任务（通过 ReActAgent）
        4. VerifyResult（通过 Verification）
        5. 学习（存入 PlanCache）
        """
        if not self._initialized:
            raise RuntimeError("UnifiedAgentManager not initialized")
        
        async with self._lock:
            # CheckYesNohaveTaskcurrentlyRunning
            if self._running_task and not self._running_task.done():
                raise RuntimeError("Agent busy with another task")
            
            # GenerationTask ID
            task_id = f"task_{uuid.uuid4().hex[:12]}"
            
            # CreateTaskInfo
            task_info = TaskInfo(
                task_id=task_id,
                task_text=task,
                target_hwnds=target_hwnds,
                session_id=session_id,
                status="starting",
            )
            self._active_tasks[task_id] = task_info
            
            # StartAfterplatformTask
            self._running_task = asyncio.create_task(
                self._execute_task(task_info),
                name=f"unified_task_{task_id}"
            )
            self._running_task.add_done_callback(
                lambda t: self._on_task_done(task_id, t)
            )
        
        return {
            "task_id": task_id,
            "status": "running",
        }
    
    async def _execute_task(self, task_info: TaskInfo):
        """Execute任务的Core流程"""
        task_id = task_info.task_id
        task = task_info.task_text
        
        try:
            task_info.status = "running"
            await self._broadcast_event(task_id, "started", {
                "task_text": task,
                "target_hwnds": task_info.target_hwnds,
            })
            
            # === 1. BuildUpDowntext（from Hook System）===
            context = self._build_context_from_hooks(task_info.target_hwnds)
            if context:
                logger.info(f"[UnifiedManager] Context injected: {len(context)} chars")
            
            # === 2. Check PlanCache（ReActAgent InnerpartalsowillCheck，hereYesquotaOuter's Log）===
            cache_hit = False
            if self._plan_cache:
                try:
                    cache_result = self._plan_cache.find_similar(task, threshold=0.80)
                    if cache_result:
                        cached_plan, similarity = cache_result  # solvePackageelementgroup
                        if cached_plan.success:
                            cache_hit = True
                            task_info.cache_hit = True
                            logger.info(f"[UnifiedManager] Cache HIT! (similarity={similarity:.2f}) Reusing plan from: {cached_plan.task[:50]}...")
                            await self._broadcast_event(task_id, "cache_hit", {
                                "original_task": cached_plan.task,
                                "use_count": cached_plan.use_count,
                                "similarity": similarity,
                            })
                except Exception as e:
                    logger.warning(f"[UnifiedManager] PlanCache lookup failed: {e}")
            
            # === 3. ExecuteTask（through ReActAgent.run_with_planning）===
            # Keychangemove：Usage run_with_planning Activationalreadyhave's ：
            # - complexdegreeminuteClass（Innerpartthe 3082 Row）
            # - step by stepExecute（the 3107-3143 Row）
            # - FailedheavyNewplanning（the 3137 RowCall planner.replan）
            start_time = time.time()
            
            result: AgentResult = await self._agent.run_with_planning(
                task=task,
                session_id=task_info.session_id,
                context=context if context else None,
            )
            
            execution_time = time.time() - start_time
            task_info.iterations = result.iterations if hasattr(result, 'iterations') else 0
            
            # === 4. VerifyResult ===
            verification_passed = True
            if self._verifier and result.success:
                try:
                    # ExtractionToolOutputforVerify（tool_calls Medium's Result）
                    tool_outputs = []
                    if result.tool_calls:
                        for tc in result.tool_calls:
                            if "result" in tc:
                                tool_outputs.append(str(tc["result"]))
                    
                    verify_result = self._verifier.verify(
                        answer=result.response or "",  # AgentResult use's Yes response
                        task=task,
                        tool_outputs=tool_outputs,
                    )
                    verification_passed = verify_result.is_valid
                    task_info.verification_passed = verification_passed
                    
                    if not verification_passed:
                        logger.warning(f"[UnifiedManager] Verification failed: {verify_result.message}")
                        await self._broadcast_event(task_id, "verification_failed", {
                            "message": verify_result.message,
                            "suggestions": verify_result.suggestions,
                        })
                except Exception as e:
                    logger.warning(f"[UnifiedManager] Verification error: {e}")
            
            # === 5. learning（storeenter PlanCache）===
            if result.success and verification_passed and self._plan_cache:
                try:
                    # BuildplanStep
                    plan_steps = []
                    if hasattr(result, 'tool_calls') and result.tool_calls:
                        for tc in result.tool_calls:
                            plan_steps.append({
                                "tool": tc.get("name", "unknown"),
                                "args": tc.get("input", {}),
                            })
                    
                    if plan_steps:
                        self._plan_cache.cache_plan(
                            task=task,
                            plan_steps=plan_steps,
                            execution_time=execution_time,
                            success=True,
                        )
                        logger.info(f"[UnifiedManager] Plan cached: {len(plan_steps)} steps")
                except Exception as e:
                    logger.warning(f"[UnifiedManager] Failed to cache plan: {e}")
            
            # === 6. Complete ===
            task_info.status = "completed" if result.success else "failed"
            task_info.completed_at = time.time()
            task_info.result = {
                "success": result.success,
                "response": result.response,  # AgentResult use's Yes response
                "iterations": task_info.iterations,
                "execution_time": execution_time,
                "cache_hit": cache_hit,
                "verification_passed": verification_passed,
            }
            
            await self._broadcast_event(task_id, "completed", task_info.result)
            
        except asyncio.CancelledError:
            logger.info(f"[UnifiedManager] Task {task_id} cancelled")
            task_info.status = "cancelled"
            await self._broadcast_event(task_id, "cancelled", {"reason": "Task cancelled"})
            raise
            
        except Exception as e:
            logger.error(f"[UnifiedManager] Task {task_id} failed: {e}", exc_info=True)
            task_info.status = "failed"
            task_info.error = str(e)
            await self._broadcast_event(task_id, "failed", {
                "error": str(e),
                "error_type": type(e).__name__,
            })
    
    def _on_task_done(self, task_id: str, task: asyncio.Task):
        """任务CompleteCallback"""
        try:
            exc = task.exception()
            if exc and not isinstance(exc, asyncio.CancelledError):
                logger.error(f"[UnifiedManager] Task {task_id} exception: {exc}")
        except asyncio.InvalidStateError:
            pass
    
    async def _broadcast_event(self, task_id: str, event_type: str, data: Dict[str, Any]):
        """广播Event到 WebSocket"""
        if self._status_server:
            try:
                await self._status_server.broadcast({
                    "type": f"agent_{event_type}",
                    "task_id": task_id,
                    "timestamp": time.time(),
                    **data,
                })
            except Exception as e:
                logger.warning(f"[UnifiedManager] Broadcast failed: {e}")
    
    async def stop_task(self, task_id: str, reason: str = "User requested") -> Dict[str, Any]:
        """Stop任务"""
        async with self._lock:
            if task_id not in self._active_tasks:
                return {"success": False, "message": f"Task {task_id} not found"}
            
            if self._running_task and not self._running_task.done():
                self._running_task.cancel()
                try:
                    await self._running_task
                except asyncio.CancelledError:
                    pass
            
            self._active_tasks[task_id].status = "stopped"
            return {"success": True, "status": "stopped", "reason": reason}
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get任务State"""
        if task_id not in self._active_tasks:
            return {"error": f"Task {task_id} not found"}
        
        task_info = self._active_tasks[task_id]
        return {
            "task_id": task_info.task_id,
            "status": task_info.status,
            "task_text": task_info.task_text,
            "started_at": task_info.started_at,
            "completed_at": task_info.completed_at,
            "result": task_info.result,
            "error": task_info.error,
            "cache_hit": task_info.cache_hit,
            "iterations": task_info.iterations,
            "verification_passed": task_info.verification_passed,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """GetStatisticsInfo"""
        stats = {
            "initialized": self._initialized,
            "modules": {
                "plan_cache": PLAN_CACHE_AVAILABLE,
                "context_store": CONTEXT_STORE_AVAILABLE,
                "memory": MEMORY_AVAILABLE,
                "verification": VERIFICATION_AVAILABLE,
            },
            "total_tasks": len(self._active_tasks),
        }
        
        if self._plan_cache:
            stats["plan_cache_stats"] = self._plan_cache.get_stats()
        
        return stats
    
    async def close(self):
        """Close管理器"""
        if self._running_task and not self._running_task.done():
            self._running_task.cancel()
            try:
                await self._running_task
            except asyncio.CancelledError:
                pass
        
        self._initialized = False
        logger.info("[UnifiedManager] Closed")


# GlobalInstance
_unified_manager: Optional[UnifiedAgentManager] = None


def get_unified_manager() -> UnifiedAgentManager:
    """GetGlobal UnifiedAgentManager Instance"""
    global _unified_manager
    if _unified_manager is None:
        _unified_manager = UnifiedAgentManager()
    return _unified_manager
