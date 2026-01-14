"""
NogicOS WebSocket Event适配器
============================

统一BeforeAfter端通信，将 WebSocket MessageConvert为 AgentEvent。

Security特性:
- LimitBefore端只能Send特定EventClass型
- VerifyMessage结构和Inner容
- 防止注入Attack

参考:
- Electron IPC Security最佳实践
- OWASP WebSocket Security指南
"""

from typing import Dict, Set, Optional, Any, Callable
import logging
import json
from dataclasses import dataclass

from .events import AgentEvent, EventType
from .event_bus import EventBus, get_event_bus

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """SecurityError - 检测到恶意或非法操作"""
    pass


class ValidationError(Exception):
    """VerifyError - Message格式或Inner容不合法"""
    pass


@dataclass
class WebSocketConnection:
    """WebSocket ConnectInfo"""
    task_id: str
    websocket: Any  # FastAPI WebSocket orOtherImplement
    authenticated: bool = False
    created_at: float = 0.0


class WebSocketEventAdapter:
    """
    WebSocket Event适配器 - 统一BeforeAfter端通信（含SecurityVerify）
    
    职责:
    1. 将After端Event转发到Before端 WebSocket
    2. 将Before端MessageVerify并Convert为 AgentEvent
    3. 管理 WebSocket Connect生命Cycle
    
    Security原则:
    - 永远不要信任来自RenderProcess/Before端的数据
    - LimitBefore端只能Send特定EventClass型
    - Verify所有Message结构和Inner容
    """
    
    # 🔴 Key：LimitBeforeendonlycanSendspecificEventClasstype
    ALLOWED_FROM_RENDERER: Set[EventType] = {
        EventType.USER_CONFIRM_RESPONSE,  # UserConfirmResponse
        EventType.USER_TAKEOVER,          # Usertakeover
        EventType.USER_INPUT,             # UserInput
    }
    
    # Allow's  payload Field（byEventClasstype）
    ALLOWED_PAYLOAD_FIELDS: Dict[EventType, Set[str]] = {
        EventType.USER_CONFIRM_RESPONSE: {"action_id", "approved", "reason"},
        EventType.USER_TAKEOVER: {"reason"},
        EventType.USER_INPUT: {"text", "files"},
    }
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize适配器
        
        Args:
            event_bus: Event总线Instance（DefaultUsageGlobalSingleton）
        """
        self.event_bus = event_bus or get_event_bus()
        self._connections: Dict[str, WebSocketConnection] = {}  # task_id -> connection
        self._message_count = 0
        self._rejected_count = 0
        
        # SubscribeallEvent，Forwardto WebSocket
        self.event_bus.subscribe_all(
            self._forward_to_websocket,
            priority=-100,  # mostLowPrioritylevel，ensureOtherHandleerfirstExecute
            name="ws_forward",
        )
    
    async def _forward_to_websocket(self, event: AgentEvent):
        """将Event转发到对应的 WebSocket"""
        conn = self._connections.get(event.task_id)
        if conn and conn.websocket:
            try:
                await conn.websocket.send_json(event.to_dict())
            except Exception as e:
                logger.warning(f"Failed to send event to WebSocket: {e}")
    
    async def handle_ws_message(
        self, 
        task_id: str, 
        message: Dict[str, Any],
    ) -> AgentEvent:
        """
        Handle来自Before端的 WebSocket Message（含SecurityVerify）
        
        Args:
            task_id: 任务 ID（从 URL ArgumentGet，已在路由层Verify）
            message: OriginalMessage（从 WebSocket Receive）
        
        Returns:
            Verify通过的 AgentEvent
        
        Raises:
            SecurityError: Security检测Failed
            ValidationError: Message格式或Inner容不合法
        """
        self._message_count += 1
        
        # 1. VerifyMessagestructure
        if not self._validate_schema(message):
            self._rejected_count += 1
            raise ValidationError("Invalid message schema: missing required fields")
        
        # 2. Verify task_id Match（preventcrossTaskAttack）
        if message.get("task_id") != task_id:
            self._rejected_count += 1
            raise SecurityError(
                f"Task ID mismatch: URL={task_id}, message={message.get('task_id')}"
            )
        
        # 3. 🔴 LimitAllow's EventClasstype（BeforeendonlycanemitspecificClasstype）
        try:
            event_type = EventType(message.get("type"))
        except ValueError:
            self._rejected_count += 1
            raise SecurityError(f"Unknown event type: {message.get('type')}")
        
        if event_type not in self.ALLOWED_FROM_RENDERER:
            self._rejected_count += 1
            raise SecurityError(
                f"Event type '{event_type.value}' not allowed from renderer. "
                f"Allowed: {[e.value for e in self.ALLOWED_FROM_RENDERER]}"
            )
        
        # 4. Verify payload Innercontent（preventinject）
        payload = message.get("payload", {})
        if not self._validate_payload(event_type, payload):
            self._rejected_count += 1
            raise ValidationError(f"Invalid payload for event type '{event_type.value}'")
        
        # 5. Cleanup payload（RemovenotAllow's Field）
        cleaned_payload = self._sanitize_payload(event_type, payload)
        
        # 6. throughVerify，CreateEvent
        event = AgentEvent.create(
            event_type=event_type,
            task_id=task_id,
            payload=cleaned_payload,
            source="renderer",  # MarkfromSourceforBeforeend
        )
        
        # 7. PublishtoEventbus
        await self.event_bus.publish(event)
        
        logger.debug(f"Processed message from renderer: {event_type.value}")
        return event
    
    def _validate_schema(self, message: Dict[str, Any]) -> bool:
        """VerifyMessage基本结构"""
        required_fields = {"type", "task_id"}
        return all(field in message for field in required_fields)
    
    def _validate_payload(self, event_type: EventType, payload: Dict[str, Any]) -> bool:
        """Verify payload Inner容"""
        if event_type == EventType.USER_CONFIRM_RESPONSE:
            # ConfirmResponseMusthave action_id and approved Field
            if "action_id" not in payload:
                return False
            if "approved" not in payload or not isinstance(payload["approved"], bool):
                return False
        
        elif event_type == EventType.USER_TAKEOVER:
            # Usertakeover，payload CanforEmptyorPackagecontain reason
            pass
        
        elif event_type == EventType.USER_INPUT:
            # UserInputMusthave text Field
            if "text" not in payload:
                return False
        
        return True
    
    def _sanitize_payload(self, event_type: EventType, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleanup payload，只保留Allow的Field
        
        这Yes最After一道防线，即使Before面的Verify通过，也只保留WhitelistField
        """
        allowed_fields = self.ALLOWED_PAYLOAD_FIELDS.get(event_type, set())
        if not allowed_fields:
            return {}
        
        return {k: v for k, v in payload.items() if k in allowed_fields}
    
    # ========== Connectmanage ==========
    
    def register_connection(self, task_id: str, websocket: Any):
        """
        Register任务的 WebSocket Connect
        
        Args:
            task_id: 任务 ID
            websocket: WebSocket Object
        """
        import time
        self._connections[task_id] = WebSocketConnection(
            task_id=task_id,
            websocket=websocket,
            authenticated=True,
            created_at=time.time(),
        )
        logger.info(f"WebSocket connection registered for task: {task_id}")
    
    def unregister_connection(self, task_id: str):
        """
        Unregister任务的 WebSocket Connect
        
        Args:
            task_id: 任务 ID
        """
        if task_id in self._connections:
            del self._connections[task_id]
            logger.info(f"WebSocket connection unregistered for task: {task_id}")
    
    def get_connection(self, task_id: str) -> Optional[WebSocketConnection]:
        """Get任务的 WebSocket Connect"""
        return self._connections.get(task_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """GetStatisticsInfo"""
        return {
            "active_connections": len(self._connections),
            "message_count": self._message_count,
            "rejected_count": self._rejected_count,
            "rejection_rate": self._rejected_count / max(self._message_count, 1),
        }


# ========== SingletonPattern ==========

_default_adapter: Optional[WebSocketEventAdapter] = None


def get_ws_adapter() -> WebSocketEventAdapter:
    """GetDefault WebSocket 适配器（Singleton）"""
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = WebSocketEventAdapter()
    return _default_adapter


def set_ws_adapter(adapter: WebSocketEventAdapter):
    """SetDefault WebSocket 适配器（用于Test）"""
    global _default_adapter
    _default_adapter = adapter
