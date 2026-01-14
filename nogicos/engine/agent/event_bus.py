"""
NogicOS Event总线
================

提供Event发布/订阅机制，解耦Component通信。

特性:
- 支持Sync和AsyncHandle器
- 背压控制（Optional，在 Phase 0.25 增强）
- Global订阅（用于Log、追踪）
- Priority级Queue支持

参考:
- UFO Agent Interaction Protocol (AIP)
- Node.js EventEmitter
"""

from typing import Callable, Dict, List, Set, Optional, Union, Awaitable
from collections import defaultdict, deque
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum

from .events import AgentEvent, EventType, EventPriority

logger = logging.getLogger(__name__)


# Handler Classtypedefine
EventHandler = Callable[[AgentEvent], Union[None, Awaitable[None]]]


@dataclass
class HandlerInfo:
    """Handle器Info"""
    handler: EventHandler
    is_async: bool
    priority: int = 0  # NumbermoreLargePrioritylevelmoreHigh
    name: str = ""     # forDebug


class EventBus:
    """
    Event总线 - 解耦Component通信
    
    UsageExample:
    ```python
    bus = EventBus()
    
    # SubscribespecificEvent
    async def handle_task_started(event: AgentEvent):
        print(f"Task started: {event.task_id}")
    
    bus.subscribe(EventType.TASK_STARTED, handle_task_started)
    
    # SubscribeallEvent（forLog）
    bus.subscribe_all(lambda e: logger.info(f"Event: {e.type}"))
    
    # PublishEvent
    await bus.publish(AgentEvent.create(
        EventType.TASK_STARTED,
        task_id="123",
        payload={"description": "Test task"}
    ))
    ```
    """
    
    def __init__(self, max_queue_size: int = 1000):
        """
        InitializeEvent总线
        
        Args:
            max_queue_size: MaxQueueSize（用于背压控制，Phase 0.25 Enable）
        """
        self._handlers: Dict[EventType, List[HandlerInfo]] = defaultdict(list)
        self._global_handlers: List[HandlerInfo] = []
        self._max_queue_size = max_queue_size
        self._event_count = 0
        self._error_count = 0
        self._paused = False
        self._lock = asyncio.Lock()
    
    def subscribe(
        self, 
        event_type: EventType, 
        handler: EventHandler,
        priority: int = 0,
        name: str = "",
    ) -> Callable[[], None]:
        """
        订阅特定EventClass型
        
        Args:
            event_type: 要订阅的EventClass型
            handler: EventHandleFunction（Sync或Async）
            priority: Priority级（Number越大越先Execute）
            name: Handle器名称（用于Debug）
        
        Returns:
            Cancel订阅的Function
        """
        is_async = asyncio.iscoroutinefunction(handler)
        info = HandlerInfo(
            handler=handler,
            is_async=is_async,
            priority=priority,
            name=name or handler.__name__ if hasattr(handler, '__name__') else "anonymous",
        )
        
        self._handlers[event_type].append(info)
        # byPrioritylevelSort（HighPrioritylevelinBefore）
        self._handlers[event_type].sort(key=lambda h: -h.priority)
        
        logger.debug(f"Subscribed handler '{info.name}' to {event_type.value}")
        
        # ReturnCancelSubscribeFunction
        def unsubscribe():
            self._handlers[event_type].remove(info)
            logger.debug(f"Unsubscribed handler '{info.name}' from {event_type.value}")
        
        return unsubscribe
    
    def subscribe_all(
        self, 
        handler: EventHandler,
        priority: int = 0,
        name: str = "",
    ) -> Callable[[], None]:
        """
        订阅所有Event（用于Log、追踪）
        
        Args:
            handler: EventHandleFunction
            priority: Priority级
            name: Handle器名称
        
        Returns:
            Cancel订阅的Function
        """
        is_async = asyncio.iscoroutinefunction(handler)
        info = HandlerInfo(
            handler=handler,
            is_async=is_async,
            priority=priority,
            name=name or handler.__name__ if hasattr(handler, '__name__') else "global_handler",
        )
        
        self._global_handlers.append(info)
        self._global_handlers.sort(key=lambda h: -h.priority)
        
        logger.debug(f"Subscribed global handler '{info.name}'")
        
        def unsubscribe():
            self._global_handlers.remove(info)
            logger.debug(f"Unsubscribed global handler '{info.name}'")
        
        return unsubscribe
    
    async def publish(self, event: AgentEvent) -> bool:
        """
        发布Event
        
        Args:
            event: 要发布的Event
        
        Returns:
            YesNoSuccess发布（背压时可能Return False）
        """
        if self._paused:
            logger.warning(f"EventBus paused, dropping event: {event.type.value}")
            return False
        
        self._event_count += 1
        
        # GlobalHandleerfirstExecute
        for handler_info in self._global_handlers:
            try:
                await self._call_handler(handler_info, event)
            except Exception as e:
                self._error_count += 1
                logger.error(f"Global handler '{handler_info.name}' error: {e}")
        
        # specificClasstypeHandleer
        for handler_info in self._handlers[event.type]:
            try:
                await self._call_handler(handler_info, event)
            except Exception as e:
                self._error_count += 1
                logger.error(f"Handler '{handler_info.name}' error for {event.type.value}: {e}")
        
        return True
    
    async def _call_handler(self, handler_info: HandlerInfo, event: AgentEvent):
        """调用Handle器（支持Sync和Async）"""
        if handler_info.is_async:
            await handler_info.handler(event)
        else:
            handler_info.handler(event)
    
    def pause(self):
        """PauseEventHandle"""
        self._paused = True
        logger.info("EventBus paused")
    
    def resume(self):
        """ResumeEventHandle"""
        self._paused = False
        logger.info("EventBus resumed")
    
    def get_stats(self) -> Dict:
        """GetStatisticsInfo"""
        return {
            "event_count": self._event_count,
            "error_count": self._error_count,
            "handler_count": sum(len(h) for h in self._handlers.values()),
            "global_handler_count": len(self._global_handlers),
            "paused": self._paused,
        }
    
    def clear(self):
        """Clear所有Handle器"""
        self._handlers.clear()
        self._global_handlers.clear()
        logger.info("EventBus cleared")


# ========== SingletonPattern ==========

_default_bus: Optional[EventBus] = None
_use_backpressure: bool = False  # YesNoUsagebackpressurebus


def configure_event_bus(use_backpressure: bool = False):
    """
    ConfigEvent总线Class型（必须在First次调用 get_event_bus Before调用）
    
    Args:
        use_backpressure: YesNoUsage背压Event总线
    """
    global _use_backpressure, _default_bus
    if _default_bus is not None:
        logger.warning("Event bus already initialized, configuration ignored")
        return
    _use_backpressure = use_backpressure


def get_event_bus() -> EventBus:
    """
    GetDefaultEvent总线（Singleton）
    
    Root据ConfigReturn普通 EventBus 或 BackpressureEventBus。
    Usage configure_event_bus() 在Start时Config。
    """
    global _default_bus
    if _default_bus is None:
        if _use_backpressure:
            # DelayedImportavoidLoopDependency
            _default_bus = BackpressureEventBus()
            logger.info("Using BackpressureEventBus")
        else:
            _default_bus = EventBus()
            logger.info("Using standard EventBus")
    return _default_bus


def set_event_bus(bus: EventBus):
    """SetDefaultEvent总线（用于Test）"""
    global _default_bus
    _default_bus = bus


# ========== Decorator ==========

def on_event(event_type: EventType, priority: int = 0):
    """
    EventHandle器装饰器
    
    UsageExample:
    ```python
    @on_event(EventType.TASK_STARTED)
    async def handle_task_started(event: AgentEvent):
        print(f"Task started: {event.task_id}")
    ```
    """
    def decorator(func: EventHandler) -> EventHandler:
        bus = get_event_bus()
        bus.subscribe(event_type, func, priority=priority, name=func.__name__)
        return func
    return decorator


def on_all_events(priority: int = 0):
    """
    GlobalEventHandle器装饰器
    
    UsageExample:
    ```python
    @on_all_events()
    async def log_all_events(event: AgentEvent):
        logger.info(f"Event: {event.type}")
    ```
    """
    def decorator(func: EventHandler) -> EventHandler:
        bus = get_event_bus()
        bus.subscribe_all(func, priority=priority, name=func.__name__)
        return func
    return decorator


# ========== backpressureEventbus (Phase 0.25) ==========

class EventBusOverflowError(Exception):
    """Event总线溢出Error"""
    pass


class BackpressureEventBus(EventBus):
    """
    带背压控制的Event总线
    
    特性:
    - Priority级Queue：HighPriority级EventPriorityHandle
    - 背压控制：QueueFull时丢弃LowPriority级Event
    - 批量Handle：Worker 批量消费Event
    - StatisticsMonitor：丢弃率、Delayed等指标
    
    UsageExample:
    ```python
    bus = BackpressureEventBus(max_queue_size=1000)
    await bus.start()  # Start worker
    
    # PublishEvent（HighPrioritylevelnotwillbeDiscard）
    await bus.publish(AgentEvent.create(
        EventType.TASK_FAILED,
        task_id="123",
        payload={"error": "..."},
        priority=EventPriority.CRITICAL,
    ))
    
    await bus.stop()  # Stop worker
    ```
    """
    
    # EventPrioritylevelMap（NumbermoreSmallPrioritylevelmoreHigh）
    # CompleteOverrideall EventType，avoidUsageDefaultValue
    PRIORITY_MAP: Dict[EventType, int] = {
        # ========== mostHighPrioritylevel (0) - notcanDiscard ==========
        EventType.TASK_FAILED: 0,
        EventType.USER_TAKEOVER: 0,
        EventType.USER_CONFIRM_REQUIRED: 0,
        EventType.USER_CONFIRM_RESPONSE: 0,
        EventType.USER_INPUT: 0,  # UserInputMustHandle
        EventType.LLM_ERROR: 0,   # LLM ErrorMustHandle
        
        # ========== HighPrioritylevel (1) - TaskStateChanged ==========
        EventType.TASK_COMPLETED: 1,
        EventType.TASK_INTERRUPTED: 1,
        EventType.TASK_PAUSED: 1,
        EventType.TASK_RESUMED: 1,
        EventType.TASK_CANCELLED: 1,
        EventType.TOOL_ERROR: 1,
        
        # ========== normalPrioritylevel (2) - normalAction ==========
        EventType.TASK_CREATED: 2,
        EventType.TASK_STARTED: 2,
        EventType.TOOL_START: 2,
        EventType.TOOL_END: 2,
        EventType.TOOL_RETRY: 2,
        EventType.AGENT_EXECUTING: 2,
        EventType.LLM_REQUEST_START: 2,
        EventType.LLM_RESPONSE_END: 2,
        EventType.OVERLAY_CONNECTED: 2,
        EventType.OVERLAY_DISCONNECTED: 2,
        EventType.OVERLAY_STATUS_UPDATE: 2,
        
        # ========== LowPrioritylevel (3) - canDiscard ==========
        EventType.AGENT_THINKING: 3,
        EventType.AGENT_PLANNING: 3,
        EventType.AGENT_WAITING: 3,
        EventType.AGENT_IDLE: 3,
        EventType.LLM_RESPONSE_CHUNK: 3,  # streamingOutputCanlostPartial
        
        # ========== mostLowPrioritylevel (4) - PriorityDiscard ==========
        EventType.SCREENSHOT_CAPTURED: 4,
        EventType.CHECKPOINT_SAVED: 4,
        EventType.CHECKPOINT_RESTORED: 4,
        EventType.CONTEXT_COMPRESSED: 4,
    }
    
    # canDiscard's PrioritylevelThreshold
    DROPPABLE_THRESHOLD = 3
    
    # BatchHandleSize
    BATCH_SIZE = 10
    
    # WaitTimeStatisticsWindowSize
    WAIT_TIME_WINDOW = 100
    
    def __init__(self, max_queue_size: int = 1000):
        super().__init__(max_queue_size)
        
        # PrioritylevelQueue：(priority, timestamp, event)
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_queue_size)
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Statistics
        self._events_queued = 0
        self._events_dropped = 0
        self._events_processed = 0
        self._overflow_count = 0  # HighPrioritylevelEventOverflowCount
        # Usage deque LimitInnerstore，onlyretainmostnear N aSample
        self._queue_wait_times: deque = deque(maxlen=self.WAIT_TIME_WINDOW)
        
        # Overflow Callback（forAlert）
        self._overflow_callback: Optional[Callable] = None
    
    async def start(self):
        """Start worker"""
        if self._running:
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(self._worker())
        logger.info("BackpressureEventBus worker started")
    
    async def stop(self):
        """Stop worker"""
        self._running = False
        
        if self._worker_task:
            # SendsentinelEventTerminate worker
            try:
                self._queue.put_nowait((999, 0, None))
            except asyncio.QueueFull:
                pass
            
            try:
                await asyncio.wait_for(self._worker_task, timeout=5.0)
            except asyncio.TimeoutError:
                self._worker_task.cancel()
            
            self._worker_task = None
        
        logger.info("BackpressureEventBus worker stopped")
    
    async def publish(self, event: AgentEvent) -> bool:
        """
        发布Event到Queue
        
        Args:
            event: 要发布的Event
            
        Returns:
            YesNoSuccess入队
            
        Note:
            QueueFull时：
            - LowPriority级Event被静默丢弃
            - HighPriority级EventTrigger overflow Callback，记录严重Error，但不抛Exception
        """
        if self._paused:
            logger.warning(f"EventBus paused, dropping event: {event.type.value}")
            return False
        
        import time
        priority = self._get_priority(event)
        timestamp = time.time()
        
        try:
            self._queue.put_nowait((priority, timestamp, event))
            self._events_queued += 1
            self._event_count += 1
            return True
            
        except asyncio.QueueFull:
            # QueueFull，CheckYesNocanDiscard
            if priority >= self.DROPPABLE_THRESHOLD:
                self._events_dropped += 1
                logger.debug(f"Dropped low-priority event: {event.type.value}")
                return False
            
            # HighPrioritylevelEventnotcanDiscard
            # Policy：RecordError + TriggerCallback，butnotthrowExceptiontoavoidMediumbreakmainLoop
            self._events_dropped += 1
            self._overflow_count += 1
            logger.critical(
                f"CRITICAL: Queue overflow, dropped high-priority event: {event.type.value} "
                f"(priority={priority}). Consider increasing max_queue_size or optimizing handlers."
            )
            
            # Trigger overflow Callback（IfRegister）
            if self._overflow_callback:
                try:
                    if asyncio.iscoroutinefunction(self._overflow_callback):
                        await self._overflow_callback(event)
                    else:
                        self._overflow_callback(event)
                except Exception as e:
                    logger.error(f"Overflow callback error: {e}")
            
            return False
    
    def _get_priority(self, event: AgentEvent) -> int:
        """GetEventPriority级"""
        # firstCheckEventselfwith's Prioritylevel
        if event.priority == EventPriority.CRITICAL:
            return 0
        elif event.priority == EventPriority.HIGH:
            return 1
        elif event.priority == EventPriority.LOW:
            return 4
        
        # UsageClasstypeMap
        return self.PRIORITY_MAP.get(event.type, 2)
    
    async def _worker(self):
        """Worker 协程：批量HandleEvent"""
        import time
        
        while self._running:
            batch: List[AgentEvent] = []
            
            try:
                # GetFirstaEvent（Blocked）
                priority, enqueue_time, event = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0
                )
                
                # sentinelEvent
                if event is None:
                    break
                
                batch.append(event)
                wait_time = time.time() - enqueue_time
                self._queue_wait_times.append(wait_time)
                
                # tryGetMoreEvent（Non-block）
                while len(batch) < self.BATCH_SIZE:
                    try:
                        priority, enqueue_time, event = self._queue.get_nowait()
                        if event is None:
                            break
                        batch.append(event)
                    except asyncio.QueueEmpty:
                        break
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker error getting events: {e}")
                continue
            
            # BatchHandle
            await self._process_batch(batch)
    
    async def _process_batch(self, batch: List[AgentEvent]):
        """批量HandleEvent"""
        for event in batch:
            try:
                # CallParentClass's Handlelogic
                await self._dispatch_event(event)
                self._events_processed += 1
            except Exception as e:
                self._error_count += 1
                logger.error(f"Error processing event {event.type.value}: {e}")
    
    async def _dispatch_event(self, event: AgentEvent):
        """分发Event到Handle器"""
        # GlobalHandleer
        for handler_info in self._global_handlers:
            try:
                await self._call_handler(handler_info, event)
            except Exception as e:
                logger.error(f"Global handler '{handler_info.name}' error: {e}")
        
        # specificClasstypeHandleer
        for handler_info in self._handlers[event.type]:
            try:
                await self._call_handler(handler_info, event)
            except Exception as e:
                logger.error(f"Handler '{handler_info.name}' error: {e}")
    
    def on_overflow(self, callback: Callable):
        """
        RegisterQueue溢出Callback（用于Alert或Downgrade）
        
        Args:
            callback: CallbackFunction，Receive被丢弃的Event
        
        Usage:
            bus.on_overflow(lambda event: alert_critical(f"Dropped: {event.type}"))
        """
        self._overflow_callback = callback
    
    def get_stats(self) -> Dict:
        """GetStatisticsInfo"""
        base_stats = super().get_stats()
        
        # calculateQueueWaitTime（deque alreadyAutoLimitSize）
        avg_wait = sum(self._queue_wait_times) / len(self._queue_wait_times) if self._queue_wait_times else 0
        
        return {
            **base_stats,
            "queue_size": self._queue.qsize(),
            "max_queue_size": self._max_queue_size,
            "events_queued": self._events_queued,
            "events_dropped": self._events_dropped,
            "events_processed": self._events_processed,
            "overflow_count": self._overflow_count,  # HighPrioritylevelEventOverflow
            "drop_rate": self._events_dropped / max(self._events_queued, 1),
            "avg_queue_wait_ms": avg_wait * 1000,
            "running": self._running,
        }
    
    async def drain(self, timeout: float = 5.0):
        """WaitQueue清Empty"""
        import time
        start = time.time()
        
        while not self._queue.empty():
            if time.time() - start > timeout:
                logger.warning(f"Drain timeout, {self._queue.qsize()} events remaining")
                break
            await asyncio.sleep(0.1)


# ========== FactoryFunction ==========

_backpressure_bus: Optional[BackpressureEventBus] = None


def get_backpressure_bus() -> BackpressureEventBus:
    """Get背压Event总线（Singleton）"""
    global _backpressure_bus
    if _backpressure_bus is None:
        _backpressure_bus = BackpressureEventBus()
    return _backpressure_bus


async def init_backpressure_bus() -> BackpressureEventBus:
    """Initialize并Start背压Event总线"""
    bus = get_backpressure_bus()
    await bus.start()
    return bus
