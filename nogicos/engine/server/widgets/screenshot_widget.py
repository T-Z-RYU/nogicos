"""
Screenshot Widget - 截GraphDisplay

Display操作After页面截Graph的 Widget，支持：
- Base64 或 URL Graph片
- title和描述
- High亮区域标记
"""

from __future__ import annotations
from typing import Optional, Dict, Any


def build_screenshot_widget(
    image_data: str,
    title: str = "操作Complete",
    description: str = "",
    highlight: Optional[Dict[str, int]] = None,
    is_base64: bool = True,
) -> dict:
    """
    构建截Graph Widget。
    
    Args:
        image_data: Graph片数据（Base64 或 URL）
        title: title
        description: 描述文本
        highlight: High亮区域 {"x": int, "y": int, "width": int, "height": int}
        is_base64: YesNo为 Base64 编码
        
    Returns:
        Widget 数据结构
    """
    # BuildGraphpiece URL
    if is_base64:
        image_url = f"data:image/png;base64,{image_data}"
    else:
        image_url = image_data
    
    widget_data = {
        "type": "nogicos_screenshot",
        "data": {
            "image_url": image_url,
            "title": title,
            "description": description,
        }
    }
    
    # AddHighbrightLocale
    if highlight:
        widget_data["data"]["highlight"] = highlight
    
    return widget_data


def format_screenshot_markdown(
    image_url: str,
    title: str = "截Graph",
    description: str = "",
) -> str:
    """
    格式化截Graph为 Markdown（用于纯文本Response）。
    
    Note: Base64 Graph片在 Markdown MediumDisplayEffect较差，
    建议Usage URL 或 Widget Render。
    """
    lines = [f"**{title}**"]
    
    if description:
        lines.append(description)
    
    # IfnotYes base64，CanDisplayGraphpiecelink
    if not image_url.startswith("data:"):
        lines.append(f"![{title}]({image_url})")
    else:
        lines.append("_(截Graph已Attach)_")
    
    return "\n".join(lines)


