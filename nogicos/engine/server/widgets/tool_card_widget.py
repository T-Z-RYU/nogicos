"""
Tool Card Widget - ToolExecute卡片

DisplayToolExecuteState的 Widget，支持：
- Tool名称和Argument
- ExecuteState（executing, success, error）
- ExecuteResult或ErrorInfo
- ExecuteTime
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class ToolCardState:
    """Tool卡片State"""
    tool_id: str
    tool_name: str
    args: Dict[str, Any]
    status: str = "executing"  # executing, success, error
    result: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration_ms(self) -> Optional[int]:
        """计算Execute时长（毫Second）"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() * 1000)
        return None
    
    @property
    def status_icon(self) -> str:
        """StateGraph标"""
        return {
            "executing": "⏳",
            "success": "✓",
            "error": "✗",
        }.get(self.status, "•")
    
    @property
    def display_name(self) -> str:
        """ToolDisplay名称（Medium文化）"""
        name_map = {
            "navigate": "导航到webpage",
            "click": "点击元素",
            "type_text": "Input文本",
            "screenshot": "截取屏幕",
            "list_directory": "Column出Directory",
            "move_file": "MoveFile",
            "create_directory": "CreateFile夹",
            "delete_file": "DeleteFile",
            "read_file": "ReadFile",
            "write_file": "WriteFile",
        }
        return name_map.get(self.tool_name, self.tool_name)


def build_tool_card_widget(state: ToolCardState) -> dict:
    """
    构建Tool卡片 Widget。
    
    Return格式：
    {
        "type": "nogicos_tool_card",
        "data": {
            "tool_id": "abc123",
            "tool_name": "navigate",
            "display_name": "导航到webpage",
            "args": {"url": "https://..."},
            "status": "success",
            "status_icon": "✓",
            "result": "导航Success",
            "error": null,
            "duration_ms": 1234
        }
    }
    """
    return {
        "type": "nogicos_tool_card",
        "data": {
            "tool_id": state.tool_id,
            "tool_name": state.tool_name,
            "display_name": state.display_name,
            "args": state.args,
            "status": state.status,
            "status_icon": state.status_icon,
            "result": state.result,
            "error": state.error,
            "duration_ms": state.duration_ms,
        }
    }


def format_tool_text(state: ToolCardState) -> str:
    """
    格式化ToolExecute为文本（用于纯文本Response）。
    
    Example:
        ✓ 导航到webpage (234ms)
          url: https://taobao.com
          Result: 导航Success
    """
    lines = []
    
    # StateRow
    duration_str = f" ({state.duration_ms}ms)" if state.duration_ms else ""
    lines.append(f"{state.status_icon} {state.display_name}{duration_str}")
    
    # Argument（simpleizeDisplay）
    if state.args:
        for key, value in list(state.args.items())[:3]:  # most3aArgument
            value_str = str(value)[:50]  # TruncateLongValue
            lines.append(f"  {key}: {value_str}")
    
    # ResultorError
    if state.status == "success" and state.result:
        result_preview = state.result[:100] if len(state.result) > 100 else state.result
        lines.append(f"  Result: {result_preview}")
    elif state.status == "error" and state.error:
        lines.append(f"  Error: {state.error}")
    
    return "\n".join(lines)


