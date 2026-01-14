"""
Progress Widget - 任务进度Display

Display任务Execute进度的 Widget，支持：
- 当Before步骤/总步骤
- 进度百分比
- State描述
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

# ChatKit widget imports
try:
    from chatkit.widgets import WidgetRoot
    CHATKIT_WIDGETS_AVAILABLE = True
except ImportError:
    CHATKIT_WIDGETS_AVAILABLE = False
    WidgetRoot = dict  # Fallback


@dataclass
class ProgressState:
    """进度State"""
    current_step: int
    total_steps: int
    status: str = "active"  # active, completed, error
    description: str = ""
    
    @property
    def percentage(self) -> int:
        """计算进度百分比"""
        if self.total_steps == 0:
            return 0
        return min(100, int((self.current_step / self.total_steps) * 100))
    
    @property
    def progress_bar(self) -> str:
        """生成 ASCII 进度条"""
        filled = int(self.percentage / 10)
        empty = 10 - filled
        return "█" * filled + "░" * empty


def build_progress_widget(state: ProgressState) -> dict:
    """
    构建进度 Widget。
    
    由于 ChatKit Widget TemplateSystem较复杂，
    这里Usage简化的 JSON 结构Return进度Info，
    Before端可以Root据此结构Render自定义 UI。
    
    Return格式：
    {
        "type": "nogicos_progress",
        "data": {
            "current": 2,
            "total": 4,
            "percentage": 50,
            "status": "active",
            "description": "正在Execute...",
            "progress_bar": "█████░░░░░"
        }
    }
    """
    return {
        "type": "nogicos_progress",
        "data": {
            "current": state.current_step,
            "total": state.total_steps,
            "percentage": state.percentage,
            "status": state.status,
            "description": state.description,
            "progress_bar": state.progress_bar,
        }
    }


def format_progress_text(state: ProgressState) -> str:
    """
    格式化进度文本（用于纯文本Response）。
    
    Example:
        [█████░░░░░] 50% | 步骤 2/4: 正在InputSearch词
    """
    status_icon = {
        "active": "⏳",
        "completed": "✓",
        "error": "✗",
    }.get(state.status, "•")
    
    return (
        f"{status_icon} [{state.progress_bar}] {state.percentage}% | "
        f"步骤 {state.current_step}/{state.total_steps}"
        + (f": {state.description}" if state.description else "")
    )


