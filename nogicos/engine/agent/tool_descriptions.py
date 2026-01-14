"""
NogicOS Tool Descriptions - 增强版Tool描述
==========================================

High质量的Tool描述，help LLM 正确理解和UsageTool。

设计原则：
1. 清晰的功能说明
2. 明确的Usage场景
3. 详细的Argument说明
4. 具体的UsageExample
5. 常见Error提示

参考:
- Anthropic Computer Use Tool Specs
- UFO Action Registry
- ByteBot Tool Definitions

Phase 5a Implement
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class ToolDescription:
    """
    增强版Tool描述
    
    比简单的 JSON schema 更丰富，Package含Usage指南和Example
    """
    name: str
    summary: str
    when_to_use: List[str]
    when_not_to_use: List[str]
    parameters: Dict[str, Dict[str, Any]]
    examples: List[Dict[str, Any]]
    returns: str
    common_mistakes: Optional[List[str]] = None
    tips: Optional[List[str]] = None
    requires_screenshot: bool = False
    is_sensitive: bool = False
    category: str = "general"
    
    def to_claude_tool_schema(self) -> Dict[str, Any]:
        """Convert为 Claude API Tool定义格式"""
        # BuildEnhancementversiondescribe
        description_parts = [self.summary]
        
        description_parts.append("\n\n**When to use:**")
        for item in self.when_to_use:
            description_parts.append(f"- {item}")
        
        description_parts.append("\n**When NOT to use:**")
        for item in self.when_not_to_use:
            description_parts.append(f"- {item}")
        
        if self.tips:
            description_parts.append("\n**Tips:**")
            for tip in self.tips:
                description_parts.append(f"- {tip}")
        
        if self.common_mistakes:
            description_parts.append("\n**Common mistakes:**")
            for mistake in self.common_mistakes:
                description_parts.append(f"- ❌ {mistake}")
        
        description = "\n".join(description_parts)
        
        # BuildArgument schema
        properties = {}
        required = []
        
        for param_name, param_info in self.parameters.items():
            prop = {
                "type": param_info.get("type", "string"),
                "description": param_info.get("description", ""),
            }
            
            if "enum" in param_info:
                prop["enum"] = param_info["enum"]
            if "minimum" in param_info:
                prop["minimum"] = param_info["minimum"]
            if "maximum" in param_info:
                prop["maximum"] = param_info["maximum"]
            
            properties[param_name] = prop
            
            if param_info.get("required", False):
                required.append(param_name)
        
        return {
            "name": self.name,
            "description": description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }


# ========== Tooldescribedefine ==========

TOOL_DESCRIPTIONS: Dict[str, ToolDescription] = {
    # ========== captureGraphTool ==========
    "window_screenshot": ToolDescription(
        name="window_screenshot",
        summary="Capture a screenshot of the specified window to see its current state.",
        category="observation",
        requires_screenshot=False,
        when_to_use=[
            "At the start of a task to understand the current state",
            "After any action to verify the result",
            "When uncertain about what's visible on screen",
            "Before clicking to verify target element position",
        ],
        when_not_to_use=[
            "Repeatedly without taking action (wastes time)",
            "When you already have a recent screenshot and nothing changed",
        ],
        parameters={
            "hwnd": {
                "type": "integer",
                "description": "Window handle (hwnd) to capture. Use the hwnd from your assigned windows.",
                "required": True,
            }
        },
        examples=[
            {
                "scenario": "Check browser state",
                "call": {"hwnd": 12345},
                "result": "Returns base64 encoded screenshot of the browser window",
            }
        ],
        returns="A screenshot of the window as a base64 encoded image.",
        tips=[
            "Always take a screenshot after navigation or clicking",
            "Use to verify that UI elements are in expected positions",
        ],
    ),
    
    # ========== ClickTool ==========
    "window_click": ToolDescription(
        name="window_click",
        summary="Click at the specified coordinates within a window. Use to interact with buttons, links, and form fields.",
        category="action",
        requires_screenshot=True,
        when_to_use=[
            "Click buttons to perform actions",
            "Click input fields before typing",
            "Click links to navigate",
            "Click checkboxes or radio buttons",
            "Click dropdowns to open them",
        ],
        when_not_to_use=[
            "Without first taking a screenshot to verify coordinates",
            "When you need to type (click field first, then use window_type)",
            "For scrolling (use window_scroll instead)",
        ],
        parameters={
            "hwnd": {
                "type": "integer",
                "description": "Window handle (hwnd) to click in.",
                "required": True,
            },
            "x": {
                "type": "integer",
                "description": "X coordinate in pixels from the LEFT edge of the window.",
                "required": True,
                "minimum": 0,
            },
            "y": {
                "type": "integer",
                "description": "Y coordinate in pixels from the TOP edge of the window.",
                "required": True,
                "minimum": 0,
            },
            "button": {
                "type": "string",
                "description": "Mouse button to click.",
                "enum": ["left", "right", "middle"],
                "required": False,
            },
            "click_type": {
                "type": "string",
                "description": "Type of click action.",
                "enum": ["single", "double", "hold"],
                "required": False,
            },
        },
        examples=[
            {
                "scenario": "Click a submit button at (500, 300)",
                "call": {"hwnd": 12345, "x": 500, "y": 300},
                "result": "Clicks the button and returns success status",
            },
            {
                "scenario": "Double-click to select a word",
                "call": {"hwnd": 12345, "x": 200, "y": 150, "click_type": "double"},
                "result": "Double-clicks to select the word at that position",
            },
        ],
        returns="Success or failure status of the click action.",
        common_mistakes=[
            "Clicking without verifying the target is visible in screenshot",
            "Using wrong coordinates (off by large amount)",
            "Not waiting for page/app to load before clicking",
            "Clicking a disabled button",
        ],
        tips=[
            "Calculate coordinates from the CENTER of the target element",
            "Take a screenshot after clicking to verify the result",
            "If click doesn't work, try clicking again or nearby coordinates",
        ],
    ),
    
    # ========== InputTool ==========
    "window_type": ToolDescription(
        name="window_type",
        summary="Type text into the currently focused field in a window. Always click the target field first!",
        category="action",
        requires_screenshot=True,
        when_to_use=[
            "Enter text into input fields (after clicking them)",
            "Fill in forms",
            "Type search queries",
            "Enter URLs in address bar",
        ],
        when_not_to_use=[
            "Without clicking the target field first",
            "For pressing special keys (use window_key_press)",
            "For pasting content (use window_paste if available)",
        ],
        parameters={
            "hwnd": {
                "type": "integer",
                "description": "Window handle (hwnd) to type in.",
                "required": True,
            },
            "text": {
                "type": "string",
                "description": "Text to type. Will be typed character by character.",
                "required": True,
            },
            "clear_first": {
                "type": "boolean",
                "description": "If true, clears the field before typing (Ctrl+A, Delete).",
                "required": False,
            },
            "press_enter": {
                "type": "boolean",
                "description": "If true, presses Enter after typing (useful for search/submit).",
                "required": False,
            },
        },
        examples=[
            {
                "scenario": "Type a search query",
                "call": {"hwnd": 12345, "text": "Python tutorial", "press_enter": True},
                "result": "Types the text and presses Enter to search",
            },
            {
                "scenario": "Clear and type new content",
                "call": {"hwnd": 12345, "text": "new content", "clear_first": True},
                "result": "Clears the field and types new content",
            },
        ],
        returns="Success or failure status of the typing action.",
        common_mistakes=[
            "Typing without clicking the input field first",
            "Not clearing existing content when needed",
            "Forgetting to press Enter for search forms",
        ],
        tips=[
            "Always click the input field before typing",
            "Use clear_first=true when replacing existing content",
            "Check the result with a screenshot after typing",
        ],
    ),
    
    # ========== ScrollTool ==========
    "window_scroll": ToolDescription(
        name="window_scroll",
        summary="Scroll within a window to reveal more content.",
        category="action",
        when_to_use=[
            "Load more content in infinite scroll pages",
            "Reveal elements below the fold",
            "Navigate long pages or lists",
            "Scroll to a specific section",
        ],
        when_not_to_use=[
            "When the target is already visible",
            "For horizontal navigation (consider arrow keys)",
        ],
        parameters={
            "hwnd": {
                "type": "integer",
                "description": "Window handle (hwnd) to scroll in.",
                "required": True,
            },
            "direction": {
                "type": "string",
                "description": "Direction to scroll.",
                "enum": ["up", "down", "left", "right"],
                "required": True,
            },
            "amount": {
                "type": "integer",
                "description": "Amount to scroll in pixels. Default is ~300 (one page).",
                "required": False,
                "minimum": 50,
                "maximum": 2000,
            },
            "x": {
                "type": "integer",
                "description": "X coordinate for scroll position (for nested scrollable areas).",
                "required": False,
            },
            "y": {
                "type": "integer",
                "description": "Y coordinate for scroll position (for nested scrollable areas).",
                "required": False,
            },
        },
        examples=[
            {
                "scenario": "Scroll down to see more content",
                "call": {"hwnd": 12345, "direction": "down", "amount": 500},
                "result": "Scrolls down 500 pixels",
            },
        ],
        returns="Success or failure status of the scroll action.",
        tips=[
            "Scroll in increments and take screenshots to check progress",
            "For infinite scroll, scroll until desired content appears",
        ],
    ),
    
    # ========== KeyboardTool ==========
    "window_key_press": ToolDescription(
        name="window_key_press",
        summary="Press a keyboard key or key combination.",
        category="action",
        when_to_use=[
            "Press Enter to submit forms",
            "Press Escape to close dialogs",
            "Use keyboard shortcuts (Ctrl+C, Ctrl+V, etc.)",
            "Navigate with arrow keys",
            "Press Tab to move between fields",
        ],
        when_not_to_use=[
            "For typing regular text (use window_type)",
        ],
        parameters={
            "hwnd": {
                "type": "integer",
                "description": "Window handle (hwnd) to send keys to.",
                "required": True,
            },
            "key": {
                "type": "string",
                "description": "Key to press. Examples: 'enter', 'escape', 'tab', 'ctrl+c', 'alt+f4'",
                "required": True,
            },
        },
        examples=[
            {
                "scenario": "Press Enter to submit",
                "call": {"hwnd": 12345, "key": "enter"},
                "result": "Presses Enter key",
            },
            {
                "scenario": "Copy selected text",
                "call": {"hwnd": 12345, "key": "ctrl+c"},
                "result": "Copies selection to clipboard",
            },
        ],
        returns="Success or failure status of the key press.",
        tips=[
            "Use 'enter' for submitting forms",
            "Use 'escape' to close popups and dialogs",
            "Key combinations use '+' (e.g., 'ctrl+shift+n')",
        ],
    ),
    
    # ========== TaskStateTool ==========
    "set_task_status": ToolDescription(
        name="set_task_status",
        summary="Set the task status to indicate completion or request help. This is the ONLY way to end a task.",
        category="control",
        is_sensitive=False,
        when_to_use=[
            "Task is fully completed and verified",
            "Stuck and need user assistance",
            "Encountered an unrecoverable error",
            "Missing information needed to proceed",
        ],
        when_not_to_use=[
            "Task is not actually complete",
            "You haven't tried alternative approaches yet",
            "There are still steps remaining",
        ],
        parameters={
            "status": {
                "type": "string",
                "description": "Task status to set.",
                "enum": ["completed", "needs_help"],
                "required": True,
            },
            "description": {
                "type": "string",
                "description": "Detailed description of what was accomplished or what help is needed.",
                "required": True,
            },
        },
        examples=[
            {
                "scenario": "Task completed successfully",
                "call": {
                    "status": "completed",
                    "description": "Successfully searched for 'Python tutorial' and opened the first result. The tutorial page is now displayed."
                },
            },
            {
                "scenario": "Need user help",
                "call": {
                    "status": "needs_help",
                    "description": "Login required to proceed. Please log in and restart the task."
                },
            },
        ],
        returns="Confirmation of status update.",
        common_mistakes=[
            "Marking as completed before verifying the result",
            "Not providing detailed description",
            "Giving up too early without trying alternatives",
        ],
        tips=[
            "Always take a final screenshot before marking as completed",
            "Be specific about what was accomplished in the description",
            "For needs_help, explain what you tried and what's blocking",
        ],
    ),
}


# ========== ToolRegisterTable ==========

class ToolRegistry:
    """
    ToolRegisterTable
    
    管理所有AvailableTool的描述和 schema
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDescription] = dict(TOOL_DESCRIPTIONS)
    
    def register(self, tool: ToolDescription):
        """RegisterTool"""
        self._tools[tool.name] = tool
    
    def unregister(self, name: str):
        """UnregisterTool"""
        self._tools.pop(name, None)
    
    def get(self, name: str) -> Optional[ToolDescription]:
        """GetTool描述"""
        return self._tools.get(name)
    
    def get_all(self) -> List[ToolDescription]:
        """Get所有Tool"""
        return list(self._tools.values())
    
    def get_by_category(self, category: str) -> List[ToolDescription]:
        """按Class别GetTool"""
        return [t for t in self._tools.values() if t.category == category]
    
    def to_claude_tools(
        self,
        tool_names: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Convert为 Claude API Tool定义格式
        
        Args:
            tool_names: 要Package含的Tool名称List（Default全部）
            
        Returns:
            Claude API 格式的Tool定义List
        """
        if tool_names is None:
            tools = self._tools.values()
        else:
            tools = [self._tools[name] for name in tool_names if name in self._tools]
        
        return [t.to_claude_tool_schema() for t in tools]


# ========== GlobalInstance ==========

_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """GetGlobalToolRegisterTable"""
    global _registry
    
    if _registry is None:
        _registry = ToolRegistry()
    
    return _registry


def get_tool_schemas(tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """便捷Function：GetTool schema List"""
    return get_tool_registry().to_claude_tools(tool_names)
