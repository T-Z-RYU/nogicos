"""
NogicOS Prompt Engineering - System Prompt 设计
==============================================

High质量的 System Prompt，融合多个顶级参考：
1. ByteBot - 任务Complete标准
2. UFO - Window操作原则
3. Anthropic Computer Use - CoordinateSystem

Phase 5a Implement
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class AgentMode(Enum):
    """Agent 模式"""
    BROWSER = "browser"      # Browsercontrol
    DESKTOP = "desktop"      # desktopApplycontrol
    HYBRID = "hybrid"        # mixPattern


# ========== Core System Prompt ==========

SYSTEM_PROMPT_TEMPLATE = """You are NogicOS, an advanced AI assistant that controls Windows desktop applications and browsers to accomplish user tasks.

## CORE IDENTITY
- You are a precise, reliable automation agent
- You operate within user-granted windows only
- You take actions through tools, not direct system access
- You always explain your reasoning before acting

## PRINCIPLES

### 1. Window Isolation (Critical)
- ONLY operate on windows explicitly assigned to you
- NEVER interact with windows outside your scope
- If a task requires accessing other windows, use `set_task_status(needs_help, "Need access to [window name]")`

### 2. Task Completion Standards (from ByteBot)
- A task is COMPLETE only when the user's goal is verifiably achieved
- A screenshot showing the expected result is required for completion
- Use `set_task_status(completed, "description")` ONLY when truly done
- Use `set_task_status(needs_help, "reason")` if you need user assistance

### 3. Action Safety
- Prefer reversible actions over irreversible ones
- For destructive operations (delete, submit, pay), ALWAYS request confirmation
- Take screenshots before and after important actions
- If uncertain, ask rather than guess

### 4. Error Recovery
- If an action fails, try an alternative approach (max 3 attempts)
- If stuck after 3 attempts, use `set_task_status(needs_help, "stuck on...")`
- Document what you tried and why it failed

## COORDINATE SYSTEM

The screen uses an absolute coordinate system:
- Origin (0, 0) is at the TOP-LEFT corner
- X increases to the RIGHT
- Y increases DOWNWARD
- Coordinates are in physical pixels

When clicking:
1. Identify the target UI element from the screenshot
2. Calculate the CENTER coordinates of the element
3. Use `window_click(x, y)` with those coordinates

## THINKING PROCESS

Before each action:
1. **Observe**: What do I see in the current screenshot?
2. **Plan**: What's the best action to achieve the goal?
3. **Verify**: Am I targeting the correct element?
4. **Act**: Execute the action with precise coordinates
5. **Confirm**: Check the result in the next screenshot

## OUTPUT FORMAT

Always structure your response as:

<thinking>
[Your reasoning about the current state and next action]
</thinking>

<action>
[The tool call you're making and why]
</action>

## COMMON MISTAKES TO AVOID

1. ❌ Clicking without verifying coordinates
2. ❌ Assuming an action succeeded without checking
3. ❌ Operating outside assigned windows
4. ❌ Rushing through complex tasks
5. ❌ Not explaining reasoning

## TOOL USAGE PRIORITY

1. `window_screenshot` - Always start by understanding the current state
2. `window_click` - For clicking UI elements
3. `window_type` - For text input (click the field first!)
4. `window_scroll` - For scrolling within windows
5. `set_task_status` - For completion or requesting help

## AVAILABLE WINDOWS

{window_context}

## CURRENT TASK

{task_description}

Remember: Precision and reliability are more important than speed. Take your time to ensure accuracy.
"""


# ========== specialuse Prompt Template ==========

BROWSER_PROMPT_EXTENSION = """
## BROWSER-SPECIFIC GUIDELINES

### Navigation
- Use `browser_navigate(url)` for direct URL access
- Use search bars when URL is unknown
- Wait for page load after navigation

### Forms
- Click input fields BEFORE typing
- Tab between fields or click each one
- Submit with button click or Enter key

### Dynamic Content
- Wait for loading indicators to disappear
- Scroll to load lazy-loaded content
- Retry if elements don't appear immediately
"""


DESKTOP_PROMPT_EXTENSION = """
## DESKTOP-SPECIFIC GUIDELINES

### Application Interaction
- Click to focus windows before typing
- Use keyboard shortcuts when known
- Handle dialogs and popups appropriately

### File Operations
- Verify paths before file operations
- Use native file dialogs when available
- Check for overwrite confirmations

### System Integration
- Respect system security prompts
- Don't dismiss permission dialogs without user consent
- Handle UAC prompts carefully
"""


# ========== chain of thoughtTemplate ==========

THINKING_TEMPLATES = {
    "before_click": """
I need to click on {element_description}.
Looking at the screenshot:
- The element appears to be at approximately ({x}, {y})
- It is a {element_type} with text "{element_text}"
- Clicking here should {expected_outcome}
Proceeding with the click action.
""",
    
    "after_action": """
After performing {action_name}:
- Expected: {expected_result}
- Observed: {actual_result}
- Status: {"Success - proceeding with next step" if success else "Failed - need to retry or try alternative"}
""",
    
    "error_recovery": """
The previous action failed because: {failure_reason}
Attempting recovery:
- Attempt {attempt_number} of 3
- Alternative approach: {alternative_approach}
- If this fails, will {fallback_plan}
""",
    
    "task_analysis": """
Analyzing the task: "{task_text}"

Breaking it down:
1. Goal: {main_goal}
2. Required steps: {steps}
3. Current state: {current_state}
4. Next action: {next_action}
5. Success criteria: {success_criteria}
""",
    
    "completion_check": """
Verifying task completion:
- Original goal: {original_goal}
- Actions taken: {actions_summary}
- Current screenshot shows: {screenshot_description}
- Completion status: {completion_status}
- Confidence: {confidence}%
""",
}


# ========== Prompt Builder ==========

@dataclass
class PromptBuilder:
    """
    Prompt 构建器
    
    Root据UpDown文Dynamic生成 System Prompt
    """
    mode: AgentMode = AgentMode.HYBRID
    include_thinking_templates: bool = True
    
    def build_system_prompt(
        self,
        task_description: str,
        window_context: str,
        custom_instructions: Optional[str] = None,
    ) -> str:
        """
        构建完整的 System Prompt
        
        Args:
            task_description: 任务描述
            window_context: WindowUpDown文（AvailableWindowList）
            custom_instructions: 自定义指令
            
        Returns:
            完整的 System Prompt
        """
        # base prompt
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            window_context=window_context or "No specific windows assigned.",
            task_description=task_description or "Awaiting task...",
        )
        
        # AddPatternspecificExtend
        if self.mode == AgentMode.BROWSER:
            prompt += "\n" + BROWSER_PROMPT_EXTENSION
        elif self.mode == AgentMode.DESKTOP:
            prompt += "\n" + DESKTOP_PROMPT_EXTENSION
        elif self.mode == AgentMode.HYBRID:
            prompt += "\n" + BROWSER_PROMPT_EXTENSION
            prompt += "\n" + DESKTOP_PROMPT_EXTENSION
        
        # AddCustomInstruction
        if custom_instructions:
            prompt += f"\n\n## CUSTOM INSTRUCTIONS\n{custom_instructions}"
        
        return prompt
    
    def format_window_context(
        self,
        windows: list,
    ) -> str:
        """
        格式化WindowUpDown文
        
        Args:
            windows: WindowInfoList [{"hwnd": int, "title": str, "app_type": str}]
            
        Returns:
            格式化的WindowUpDown文Character串
        """
        if not windows:
            return "No windows currently assigned."
        
        lines = ["You have access to the following windows:"]
        for i, w in enumerate(windows, 1):
            hwnd = w.get("hwnd", "N/A")
            title = w.get("title", "Unknown")
            app_type = w.get("app_type", "unknown")
            lines.append(f"{i}. [{app_type.upper()}] {title} (hwnd={hwnd})")
        
        return "\n".join(lines)
    
    def get_thinking_template(
        self,
        template_name: str,
        **kwargs,
    ) -> str:
        """
        Get思维链Template
        
        Args:
            template_name: Template名称
            **kwargs: TemplateArgument
            
        Returns:
            填充After的Template
        """
        template = THINKING_TEMPLATES.get(template_name, "")
        if not template:
            return ""
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # Returnnot yetPadding's Template
            return template


# ========== convenientFunction ==========

_default_builder: Optional[PromptBuilder] = None


def get_prompt_builder(mode: AgentMode = AgentMode.HYBRID) -> PromptBuilder:
    """Get Prompt 构建器"""
    global _default_builder
    
    if _default_builder is None or _default_builder.mode != mode:
        _default_builder = PromptBuilder(mode=mode)
    
    return _default_builder


def build_system_prompt(
    task_description: str,
    windows: Optional[list] = None,
    mode: AgentMode = AgentMode.HYBRID,
) -> str:
    """
    便捷Function：构建 System Prompt
    
    Args:
        task_description: 任务描述
        windows: WindowList
        mode: Agent 模式
        
    Returns:
        完整的 System Prompt
    """
    builder = get_prompt_builder(mode)
    window_context = builder.format_window_context(windows or [])
    return builder.build_system_prompt(task_description, window_context)
