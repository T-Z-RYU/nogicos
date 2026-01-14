"""
NogicOS ChatKit Server - OpenAI ChatKit Integration

Implement ChatKitServer Interface，将 NogicOS ReAct Agent 与 ChatKit UI FrameworkConnect。
支持流式Response、Widget Render、ClientTool等High级功能。

Architecture:
    ChatKit Frontend → HTTP Stream → ChatKitServer → ReActAgent → Tools
                  ↑___________ Widget/Text Events _____|
"""

from __future__ import annotations

import logging
import asyncio
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

# ChatKit imports
try:
    from chatkit.server import ChatKitServer, stream_widget
    from chatkit.store import NotFoundError
    from chatkit.types import (
        Action,
        AssistantMessageContent,
        AssistantMessageContentPartTextDelta,
        AssistantMessageItem,
        Attachment,
        Page,
        StreamOptions,
        ThreadItem,
        ThreadItemAddedEvent,
        ThreadItemUpdatedEvent,
        ThreadItemDoneEvent,
        ThreadMetadata,
        ThreadStreamEvent,
        UserMessageItem,
        WidgetItem,
    )
    # Widget components for streaming text with animation
    from chatkit.widgets import Card, Markdown, Text
    CHATKIT_AVAILABLE = True
except ImportError:
    CHATKIT_AVAILABLE = False
    ChatKitServer = object  # Fallback for type hints
    Page = None
    NotFoundError = Exception
    stream_widget = None
    Card = None
    Markdown = None
    Text = None

# OpenAI types for message content
try:
    from openai.types.responses import ResponseInputContentParam
except ImportError:
    ResponseInputContentParam = Any

# Local imports
from engine.observability import get_logger
from engine.agent.react_agent import ReActAgent, AgentResult
from engine.server.widgets import (
    build_progress_widget,
    ProgressState,
    format_progress_text,
    build_tool_card_widget,
    ToolCardState,
    format_tool_text,
)

logger = get_logger("chatkit_server")


class InMemoryStore:
    """
    Simple in-memory store for ChatKit threads and items.
    
    基于官方 MemoryStore Implement，Usage正确的 Page Class型。
    ProductionEnvironment应Replace为持久化存储（Redis, PostgreSQL等）。
    """
    
    def __init__(self):
        self._threads: Dict[str, ThreadMetadata] = {}
        self._items: Dict[str, List[Any]] = {}  # thread_id -> items
        self._counter = 0
    
    def generate_item_id(self, prefix: str, thread: ThreadMetadata, context: Dict[str, Any]) -> str:
        """Generate unique item ID."""
        self._counter += 1
        return f"{prefix}-{thread.id}-{self._counter}"
    
    def generate_thread_id(self, context: Dict[str, Any]) -> str:
        """Generate unique thread ID."""
        import uuid
        return f"thread-{uuid.uuid4().hex[:12]}"
    
    def _paginate(self, rows: list, after: Optional[str], limit: int, order: str, sort_key, cursor_key):
        """通用分页Method，Return Page Class型"""
        sorted_rows = sorted(rows, key=sort_key, reverse=(order == "desc"))
        start = 0
        if after:
            for idx, row in enumerate(sorted_rows):
                if cursor_key(row) == after:
                    start = idx + 1
                    break
        data = sorted_rows[start:start + limit] if limit else sorted_rows[start:]
        has_more = (start + limit < len(sorted_rows)) if limit else False
        next_after = cursor_key(data[-1]) if has_more and data else None
        return Page(data=data, has_more=has_more, after=next_after)
    
    async def load_thread(self, thread_id: str, context: Dict[str, Any]) -> ThreadMetadata:
        """Load thread by ID."""
        if thread_id not in self._threads:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self._threads[thread_id]
    
    async def load_threads(
        self,
        limit: int,
        after: Optional[str],
        order: str,
        context: Dict[str, Any],
    ):
        """Load all threads with pagination."""
        threads = list(self._threads.values())
        return self._paginate(
            threads, after, limit, order,
            sort_key=lambda t: getattr(t, 'created_at', datetime.min),
            cursor_key=lambda t: t.id
        )
    
    async def save_thread(self, thread: ThreadMetadata, context: Dict[str, Any]) -> None:
        """Save or update thread."""
        self._threads[thread.id] = thread
    
    async def load_thread_items(
        self,
        thread_id: str,
        after: Optional[str],
        limit: int,
        order: str,
        context: Dict[str, Any],
    ):
        """Load thread items with pagination."""
        items = self._items.get(thread_id, [])
        return self._paginate(
            items, after, limit, order,
            sort_key=lambda i: getattr(i, 'created_at', datetime.min),
            cursor_key=lambda i: i.id
        )
    
    async def add_thread_item(
        self,
        thread_id: str,
        item: Any,
        context: Dict[str, Any],
    ) -> None:
        """Add item to thread."""
        if thread_id not in self._items:
            self._items[thread_id] = []
        self._items[thread_id].append(item)
    
    async def save_item(self, thread_id: str, item: Any, context: Dict[str, Any]) -> None:
        """Save or update item."""
        items = self._items.get(thread_id, [])
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item
                return
        if thread_id not in self._items:
            self._items[thread_id] = []
        self._items[thread_id].append(item)
    
    async def delete_thread(self, thread_id: str, context: Dict[str, Any]) -> None:
        """Delete a thread and its items."""
        self._threads.pop(thread_id, None)
        self._items.pop(thread_id, None)


class NogicOSChatServer(ChatKitServer if CHATKIT_AVAILABLE else object):
    """
    NogicOS ChatKit Server - Integration ReAct Agent。
    
    功能:
    - 流式ResponseUserMessage
    - 支持ClientTool（show_visualization, highlight_element等）
    - Widget Render（进度、截Graph等）
    - Session历史管理
    
    ClientTool (Client Tools):
    - show_visualization: TriggerDisplay可视化面板
    - highlight_element: High亮Specify元素区域
    - move_cursor: Move AI 光标到SpecifyPosition
    - play_sound: 播放提示音
    """
    
    # ClientTooldefine
    CLIENT_TOOLS = [
        {
            "name": "show_visualization",
            "description": "Display可视化面板，展示 AI 操作的实时画面",
            "parameters": {},
        },
        {
            "name": "highlight_element",
            "description": "High亮页面Up的Specify区域",
            "parameters": {
                "x": {"type": "number", "description": "High亮区域LeftUp角 X Coordinate"},
                "y": {"type": "number", "description": "High亮区域LeftUp角 Y Coordinate"},
                "width": {"type": "number", "description": "High亮区域Width"},
                "height": {"type": "number", "description": "High亮区域Height"},
                "label": {"type": "string", "description": "High亮标签（Optional）"},
            },
        },
        {
            "name": "move_cursor",
            "description": "Move AI 光标到SpecifyPosition",
            "parameters": {
                "x": {"type": "number", "description": "Target X Coordinate"},
                "y": {"type": "number", "description": "Target Y Coordinate"},
            },
        },
        {
            "name": "play_sound",
            "description": "播放提示音",
            "parameters": {
                "type": {"type": "string", "description": "提示音Class型：complete, error, notification"},
            },
        },
    ]
    
    def __init__(self, status_server=None):
        """
        Initialize ChatKit Service器。
        
        Args:
            status_server: WebSocket StateService器，用于可视化面板Sync
        """
        self.store = InMemoryStore()
        
        if CHATKIT_AVAILABLE:
            super().__init__(self.store)
        
        self.status_server = status_server
        
        # Create ReAct Agent（DelayedInitializetoavoidLoopDependency）
        self._agent: Optional[ReActAgent] = None
        
        logger.info("[ChatKit] NogicOS ChatKit Server initialized")
    
    @property
    def agent(self) -> ReActAgent:
        """Get或Create ReAct Agent（DelayedInitialize）。"""
        if self._agent is None:
            self._agent = ReActAgent(status_server=self.status_server)
        return self._agent
    
    # ============================================================
    # canvisualizationPanelconnectmoveMethod
    # ============================================================
    
    async def _broadcast_visualization_event(self, event_type: str, data: Dict[str, Any] = None):
        """
        通过 WebSocket 广播可视化Event到Before端。
        
        这使得 ChatKit Response可以Trigger VisualizationPanel 的Animation。
        
        Args:
            event_type: EventClass型（cursor_move, highlight, glow 等）
            data: Event数据
        """
        if self.status_server:
            await self.status_server.broadcast({
                "type": event_type,
                "data": data or {},
            })
    
    async def trigger_show_visualization(self):
        """TriggerDisplay可视化面板。"""
        await self._broadcast_visualization_event("screen_glow", {"intensity": "medium"})
        logger.debug("[ChatKit] Triggered show_visualization")
    
    async def trigger_highlight(self, x: int, y: int, width: int, height: int, label: str = None):
        """TriggerHigh亮Specify区域。"""
        await self._broadcast_visualization_event("highlight", {
            "rect": {"x": x, "y": y, "width": width, "height": height},
            "label": label,
        })
        logger.debug(f"[ChatKit] Triggered highlight at ({x}, {y})")
    
    async def trigger_cursor_move(self, x: int, y: int):
        """Trigger光标Move。"""
        await self._broadcast_visualization_event("cursor_move", {
            "x": x,
            "y": y,
            "duration": 0.5,
        })
        logger.debug(f"[ChatKit] Triggered cursor_move to ({x}, {y})")
    
    async def trigger_task_complete(self):
        """Trigger任务CompleteAnimation。"""
        await self._broadcast_visualization_event("task_complete", {})
        logger.debug("[ChatKit] Triggered task_complete")
    
    # ============================================================
    # Required ChatKitServer Overrides
    # ============================================================
    
    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: Optional[WidgetItem],
        context: Dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Handle来自 Widget 的动作（如按钮点击）。
        
        Args:
            thread: 当BeforeSession
            action: Trigger的动作
            sender: Send动作的 Widget
            context: RequestUpDown文
        """
        logger.info(f"[ChatKit] Action received: {action.type}")
        
        # Handledifferent's actionClasstype
        if action.type == "nogicos.stop_execution":
            # StopwhenBeforeExecute
            # TODO: ImplementStoplogic
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=self.store.generate_item_id("message", thread, context),
                    thread_id=thread.id,
                    created_at=datetime.now(),
                    content=[AssistantMessageContent(text="Execute已Stop。")],
                )
            )
            return
        
        # Default：notHandleUnknownaction
        return
    
    async def respond(
        self,
        thread: ThreadMetadata,
        item: Optional[UserMessageItem],
        context: Dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        ResponseUserMessage - Package含 Thinking + Response 双区域流式展示！
        
        复刻 Cursor 的Effect：
        1. Thinking 区域：Display AI 思考过程（灰色斜体）
        2. Response 区域：DisplayFinal回复（Markdown 流式）
        
        Key：只有带 id 的 <Text>/<Markdown> Component才会有流式Animation。
        """
        if not item or not item.content:
            return
        
        # ExtractionUserMessagetext
        user_message = ""
        for content_part in item.content:
            if hasattr(content_part, 'text'):
                user_message += content_part.text
        
        if not user_message:
            return
        
        logger.info(f"[ChatKit] Processing message: {user_message[:50]}...")
        
        # accumulated text（minuteotherStorage thinking and response）
        thinking_text = ""
        response_text = ""
        is_thinking = True  # MarkwhenBeforeYesNoin thinking Stage
        
        # Usage asyncio.Queue passEvent，Format：("thinking", delta) or ("response", delta) or None
        event_queue: asyncio.Queue[tuple[str, str] | None] = asyncio.Queue()
        agent_result: Optional[Any] = None
        
        # ============================================
        # definestreamingCallbackFunction
        # ============================================
        
        async def on_thinking_delta(delta: str):
            """Claude Extended Thinking 每Output一段思考就调用此Callback"""
            await event_queue.put(("thinking", delta))
        
        async def on_text_delta(delta: str):
            """Claude 每Output一段文字就调用此Callback"""
            await event_queue.put(("response", delta))
        
        async def on_tool_start(tool_id: str, tool_name: str):
            """ToolBeginExecute时调用"""
            await event_queue.put(("response", f"\n🔧 正在Execute {tool_name}..."))
        
        async def on_tool_end(tool_id: str, success: bool, result: str):
            """ToolExecuteComplete时调用"""
            status = "✓" if success else "✗"
            await event_queue.put(("response", f" {status}\n"))
        
        # ============================================
        # AsyncExecute Agent（AfterplatformTask）
        # ============================================
        
        async def run_agent():
            """After台Execute Agent，传递 thinking Callback"""
            nonlocal agent_result
            try:
                agent_result = await self.agent.run(
                    task=user_message,
                    session_id=thread.id,
                    on_thinking_delta=on_thinking_delta,  # Newincrease：thinking Callback
                    on_text_delta=on_text_delta,
                    on_tool_start=on_tool_start,
                    on_tool_end=on_tool_end,
                )
                
                if agent_result.success:
                    await self.trigger_task_complete()
                
            except Exception as e:
                logger.error(f"[ChatKit] Agent error: {e}")
                await event_queue.put(("response", f"\n⚠️ 出错了: {str(e)}"))
            finally:
                # SendEndSignal
                await event_queue.put(None)
        
        # ============================================
        # Widget Generator - generate Thinking + Response doubleLocale
        # ============================================
        
        async def widget_generator():
            """
            Async生成器：构建 Thinking + Response 双区域 Widget。
            
            Widget 结构:
            Card
            ├── Text (id="thinking", 灰色斜体，Display思考过程)
            └── Markdown (id="response", DisplayFinal回复)
            """
            nonlocal thinking_text, response_text
            
            while True:
                try:
                    # Wait for new event（withTimeoutavoid deadlock）
                    event = await asyncio.wait_for(event_queue.get(), timeout=120.0)
                    
                    if event is None:
                        # Agent Complete
                        break
                    
                    event_type, delta = event
                    
                    if event_type == "thinking":
                        thinking_text += delta
                    else:  # response
                        response_text += delta
                    
                    # Build Widget：Thinking inUp，Response inDown，visual separator
                    children = []
                    
                    # Thinking area（gray small text，FoldDisplay）
                    if thinking_text:
                        # TruncateDisplay，onlyDisplayBefore 200 Character
                        truncated = thinking_text[:200] + "..." if len(thinking_text) > 200 else thinking_text
                        children.append(
                            Text(
                                id="thinking-text",
                                value=f"💭 Thinking...",
                                size="sm",
                                color="secondary",  # gray
                                streaming=True,
                            )
                        )
                    
                    # separator line（Ifhave thinking）
                    if thinking_text and response_text:
                        children.append(
                            Text(
                                id="divider",
                                value="───────────────",
                                size="sm",
                                color="secondary",
                            )
                        )
                    
                    # Response Locale
                    if response_text:
                        children.append(
                            Markdown(
                                id="response-text",
                                value=response_text,
                                streaming=True,
                            )
                        )
                    
                    # IftwoaallEmpty，DisplayWaitState
                    if not children:
                        children.append(
                            Text(
                                id="status-text",
                                value="⏳ 正在思考...",
                                size="sm",
                                color="secondary",
                                streaming=True,
                            )
                        )
                    
                    yield Card(children=children)
                    
                except asyncio.TimeoutError:
                    logger.warning("[ChatKit] Timeout waiting for event")
                    break
            
            # Final Widget - onlyDisplay Response，Thinking alreadyComplete
            final_children = []
            
            # Thinking CompleteMark（simpleShort）
            if thinking_text:
                final_children.append(
                    Text(
                        id="thinking-text",
                        value=f"💭 Thought for {len(thinking_text)} chars",
                        size="sm",
                        color="secondary",
                        streaming=False,
                    )
                )
                final_children.append(
                    Text(
                        id="divider",
                        value="───────────────",
                        size="sm",
                        color="secondary",
                    )
                )
            
            # Response Locale
            final_response = response_text
            if not final_response.strip() and agent_result and agent_result.response:
                final_response = agent_result.response
            elif not final_response.strip():
                final_response = "✅ 任务Complete！"
            
            final_children.append(
                Markdown(
                    id="response-text",
                    value=final_response,
                    streaming=False,
                )
            )
            
            yield Card(children=final_children)
        
        # Start Agent（Afterplatform）
        agent_task = asyncio.create_task(run_agent())
        
        # ============================================
        # Usage stream_widget streamingSend Widget
        # ============================================
        try:
            async for event in stream_widget(
                thread,
                widget_generator(),
                copy_text=response_text,  # CopytimeonlyCopy response
                generate_id=lambda item_type: self.store.generate_item_id(
                    item_type, thread, context
                ),
            ):
                yield event
        finally:
            # ensure Agent TaskComplete
            if not agent_task.done():
                agent_task.cancel()
                try:
                    await agent_task
                except asyncio.CancelledError:
                    pass
    
    def get_stream_options(
        self,
        thread: ThreadMetadata,
        context: Dict[str, Any],
    ) -> StreamOptions:
        """
        Config流式Options。
        
        Returns:
            StreamOptions Config
        """
        return StreamOptions(allow_cancel=True)
    
    async def to_message_content(
        self,
        attachment: Attachment,
    ) -> ResponseInputContentParam:
        """
        Handle附件（Graph片、File等）。
        
        当Before版本不支持附件，Aftercontinued可扩展。
        """
        raise NotImplementedError("附件功能暂未Implement。请直接描述您的需求。")


def create_chatkit_server(status_server=None) -> Optional[NogicOSChatServer]:
    """
    Create ChatKit Service器Instance。
    
    Args:
        status_server: WebSocket StateService器（Optional）
        
    Returns:
        NogicOSChatServer Instance，如果依赖不Available则Return None
    """
    if not CHATKIT_AVAILABLE:
        logger.warning("[ChatKit] ChatKit SDK not available. Install with: pip install openai-chatkit")
        return None
    
    return NogicOSChatServer(status_server=status_server)

