# -*- coding: utf-8 -*-
"""
Stream Protocol v2.0

Real-time streaming protocol for AI interaction.
Based on Vercel AI SDK Data Stream Protocol and LangChain astream_events.

Event Types:
- thinking_start: Start of thinking block
- thinking_delta: Incremental thinking content
- thinking_end: End of thinking block
- content_delta: Incremental text content
- tool_start: Tool call started
- tool_input_delta: Tool input streaming
- tool_result: Tool execution result
- complete: Message complete
- error: Error occurred
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Any, Dict
import json
import time


class ChunkType(Enum):
    """Stream chunk types following Vercel AI SDK conventions."""
    
    # Thinking/Reasoning
    THINKING = "thinking"
    THINKING_START = "thinking_start"
    THINKING_DELTA = "thinking_delta"
    THINKING_END = "thinking_end"
    
    # Content
    CONTENT = "content"
    CONTENT_DELTA = "content_delta"
    CONTENT_END = "content_end"
    
    # Tools
    TOOL_START = "tool_start"
    TOOL_INPUT_DELTA = "tool_input_delta"
    TOOL_RESULT = "tool_result"
    
    # Plan
    PLAN = "plan"
    PLAN_STEP = "plan_step"
    
    # Artifacts
    ARTIFACT = "artifact"
    
    # Control
    COMPLETE = "complete"
    ERROR = "error"
    CONFIRM = "confirm"


class ToolCallStatus(Enum):
    """Status of a tool call."""
    PENDING = "pending"
    EXECUTING = "executing"
    GENERATING = "generating"  # Tool is generating args
    GENERATED = "generated"    # Tool args generated
    SUCCESS = "success"
    DONE = "done"
    ERROR = "error"
    ERRORED = "errored"


class PlanStepStatus(Enum):
    """Status of a plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class ArtifactType(Enum):
    """Type of artifact."""
    CODE = "code"
    FILE = "file"
    IMAGE = "image"
    TEXT = "text"
    JSON = "json"


@dataclass
class ThinkingContent:
    """Content for thinking chunks."""
    text: str = ""
    is_complete: bool = False
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"text": self.text, "is_complete": self.is_complete}
        if self.duration_ms is not None:
            result["duration_ms"] = self.duration_ms
        return result


@dataclass
class ToolContent:
    """Content for tool-related chunks."""
    id: str
    name: str
    args: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"id": self.id, "name": self.name}
        if self.args is not None:
            result["args"] = self.args
        if self.result is not None:
            result["result"] = self.result
        if self.error is not None:
            result["error"] = self.error
        if self.duration_ms is not None:
            result["duration_ms"] = self.duration_ms
        return result


@dataclass
class StreamChunk:
    """
    A single stream chunk.
    
    This is the core unit of the streaming protocol.
    Each chunk represents an incremental update to the UI.
    """
    type: ChunkType
    message_id: str
    data: Any = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "type": self.type.value,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
        }
        
        if self.data is not None:
            if hasattr(self.data, "to_dict"):
                result["data"] = self.data.to_dict()
            elif isinstance(self.data, dict):
                result["data"] = self.data
            else:
                result["data"] = str(self.data)
        
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class StreamBuilder:
    """
    Helper class for building stream chunks.
    
    Usage:
        builder = StreamBuilder(message_id="msg_123")
        await ws.send(builder.thinking_start().to_json())
        await ws.send(builder.thinking_delta("Let me think...").to_json())
        await ws.send(builder.thinking_end(duration_ms=1500).to_json())
    """
    
    def __init__(self, message_id: str):
        self.message_id = message_id
        self._thinking_start_time: Optional[float] = None
    
    def thinking_start(self) -> StreamChunk:
        """Create a thinking_start chunk."""
        self._thinking_start_time = time.time()
        return StreamChunk(
            type=ChunkType.THINKING_START,
            message_id=self.message_id,
            data={"started": True},
        )
    
    def thinking_delta(self, text: str) -> StreamChunk:
        """Create a thinking_delta chunk with incremental thinking text."""
        return StreamChunk(
            type=ChunkType.THINKING_DELTA,
            message_id=self.message_id,
            data=ThinkingContent(text=text),
        )
    
    def thinking_end(self, duration_ms: Optional[int] = None) -> StreamChunk:
        """Create a thinking_end chunk."""
        if duration_ms is None and self._thinking_start_time:
            duration_ms = int((time.time() - self._thinking_start_time) * 1000)
        
        return StreamChunk(
            type=ChunkType.THINKING_END,
            message_id=self.message_id,
            data=ThinkingContent(is_complete=True, duration_ms=duration_ms),
        )
    
    def content_delta(self, text: str) -> StreamChunk:
        """Create a content_delta chunk with incremental text."""
        return StreamChunk(
            type=ChunkType.CONTENT_DELTA,
            message_id=self.message_id,
            data={"text": text},
        )
    
    def content_end(self) -> StreamChunk:
        """Create a content_end chunk."""
        return StreamChunk(
            type=ChunkType.CONTENT_END,
            message_id=self.message_id,
        )
    
    def tool_start(self, tool_id: str, tool_name: str) -> StreamChunk:
        """Create a tool_start chunk."""
        return StreamChunk(
            type=ChunkType.TOOL_START,
            message_id=self.message_id,
            data=ToolContent(id=tool_id, name=tool_name),
        )
    
    def tool_result(
        self,
        tool_id: str,
        tool_name: str,
        result: Optional[str] = None,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> StreamChunk:
        """Create a tool_result chunk."""
        return StreamChunk(
            type=ChunkType.TOOL_RESULT,
            message_id=self.message_id,
            data=ToolContent(
                id=tool_id,
                name=tool_name,
                result=result,
                error=error,
                duration_ms=duration_ms,
            ),
        )
    
    def complete(self) -> StreamChunk:
        """Create a complete chunk signaling end of message."""
        return StreamChunk(
            type=ChunkType.COMPLETE,
            message_id=self.message_id,
        )
    
    def error(self, message: str, code: Optional[str] = None) -> StreamChunk:
        """Create an error chunk."""
        return StreamChunk(
            type=ChunkType.ERROR,
            message_id=self.message_id,
            data={"message": message, "code": code},
        )


def create_stream_builder(message_id: str) -> StreamBuilder:
    """Factory function for creating StreamBuilder instances."""
    return StreamBuilder(message_id)

