# -*- coding: utf-8 -*-
"""
Agent Modes - Cursor-style interaction modes for NogicOS

Three modes:
- Agent: Autonomous execution, all tools available
- Ask: Read-only exploration, restricted tools
- Plan: Generate editable plan, user confirms before execution

Based on Cursor's Agent/Ask/Plan modes.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from ..observability import get_logger
logger = get_logger("modes")


class AgentMode(Enum):
    """Agent interaction modes"""
    AGENT = "agent"  # Autonomous execution, all tools available
    ASK = "ask"      # Read-only mode, restricted to read-only tools
    PLAN = "plan"    # Planning mode, generates plan for user to edit/confirm


@dataclass
class ModeConfig:
    """Configuration for each mode"""
    name: str
    description: str
    allowed_tool_categories: Set[str]
    read_only: bool = False
    requires_confirmation: bool = False
    system_prompt_modifier: str = ""


# Mode configurations
MODE_CONFIGS: Dict[AgentMode, ModeConfig] = {
    AgentMode.AGENT: ModeConfig(
        name="Agent",
        description="Autonomous execution mode. Can edit files, run commands, and complete tasks end-to-end.",
        allowed_tool_categories={"browser", "local", "plan", "vision"},
        read_only=False,
        requires_confirmation=False,
        system_prompt_modifier="",
    ),
    AgentMode.ASK: ModeConfig(
        name="Ask",
        description="Read-only exploration mode. Can search and analyze but cannot make any changes.",
        allowed_tool_categories={"browser", "local"},  # Will be filtered to read-only tools
        read_only=True,
        requires_confirmation=False,
        system_prompt_modifier="""
## MODE: ASK (Read-Only)

You are in ASK mode. This is a READ-ONLY mode for learning and exploration.

**CRITICAL RULES:**
1. You can ONLY use read-only tools (list, read, navigate, extract, screenshot)
2. You CANNOT modify anything (no write, delete, move, click, type)
3. Focus on understanding and explaining, not executing
4. If user asks you to modify something, explain what you would do but don't do it

Your job is to explore, analyze, and explain - NOT to make changes.
""",
    ),
    AgentMode.PLAN: ModeConfig(
        name="Plan",
        description="Planning mode. Analyzes task, generates detailed plan, asks clarifying questions.",
        allowed_tool_categories={"browser", "local"},  # Read-only for planning
        read_only=True,  # During planning phase
        requires_confirmation=True,
        system_prompt_modifier="""
## MODE: PLAN (Planning)

You are in PLAN mode. Your job is to create a detailed, actionable plan.

**WORKFLOW:**
1. Analyze the user's request
2. Explore the codebase/files to understand context (read-only)
3. Ask clarifying questions if needed
4. Generate a step-by-step plan with:
   - Clear descriptions for each step
   - Suggested tools to use
   - File paths and code references where relevant
5. Wait for user to review, edit, and confirm the plan

**PLAN FORMAT:**
Return your plan as a JSON object with this structure:
```json
{
  "summary": "Brief summary of what will be done",
  "clarifying_questions": ["Question 1?", "Question 2?"],
  "steps": [
    {
      "step": 1,
      "description": "What this step does",
      "tool": "suggested_tool_name",
      "details": "Additional details, file paths, etc."
    }
  ],
  "risks": ["Potential risk 1", "Risk 2"],
  "estimated_time": "5-10 minutes"
}
```

DO NOT execute anything. Only generate the plan and wait for confirmation.
""",
    ),
}


# Read-only tools allowed in ASK and PLAN modes
READ_ONLY_TOOLS: Set[str] = {
    # Local tools (read-only)
    "list_directory",
    "read_file",
    "search_files",
    "get_file_info",
    "search_text",
    
    # Browser tools (read-only)
    "browser_navigate",
    "browser_extract",
    "browser_screenshot",
    "browser_scroll",
    "browser_get_page_info",
    
    # Vision tools (read-only)
    "desktop_screenshot",
}

# Write/modify tools NOT allowed in read-only modes
WRITE_TOOLS: Set[str] = {
    # Local tools (write)
    "write_file",
    "delete_file",
    "move_file",
    "copy_file",
    "create_directory",
    "shell_execute",
    
    # Browser tools (write/interact)
    "browser_click",
    "browser_type",
    "browser_send_keys",
    "browser_select_option",
    "browser_upload_file",
    "browser_clear",
}


class ModeRouter:
    """
    Routes requests based on agent mode.
    
    Responsibilities:
    - Filter tools based on mode
    - Modify system prompts
    - Handle mode-specific logic
    """
    
    def __init__(self):
        self.configs = MODE_CONFIGS
        self.read_only_tools = READ_ONLY_TOOLS
        self.write_tools = WRITE_TOOLS
    
    def get_config(self, mode: AgentMode) -> ModeConfig:
        """Get configuration for a mode"""
        return self.configs.get(mode, self.configs[AgentMode.AGENT])
    
    def get_allowed_tools(
        self, 
        mode: AgentMode, 
        all_tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter tools based on mode.
        
        Args:
            mode: Current agent mode
            all_tools: List of all tools in Anthropic format
            
        Returns:
            Filtered list of tools allowed in this mode
        """
        config = self.get_config(mode)
        
        if mode == AgentMode.AGENT:
            # Agent mode: all tools allowed
            return all_tools
        
        # ASK and PLAN modes: only read-only tools
        allowed = []
        for tool in all_tools:
            tool_name = tool.get("name", "")
            if tool_name in self.read_only_tools:
                allowed.append(tool)
            elif tool_name not in self.write_tools:
                # Unknown tool - check if it looks safe (no write/delete/modify in name)
                name_lower = tool_name.lower()
                if not any(w in name_lower for w in ["write", "delete", "move", "create", "execute", "click", "type", "send", "upload", "clear"]):
                    allowed.append(tool)
        
        logger.info(f"[ModeRouter] Mode {mode.value}: {len(allowed)}/{len(all_tools)} tools allowed")
        return allowed
    
    def get_system_prompt_modifier(self, mode: AgentMode) -> str:
        """Get system prompt modifier for a mode"""
        config = self.get_config(mode)
        return config.system_prompt_modifier
    
    def is_read_only(self, mode: AgentMode) -> bool:
        """Check if mode is read-only"""
        config = self.get_config(mode)
        return config.read_only
    
    def requires_confirmation(self, mode: AgentMode) -> bool:
        """Check if mode requires user confirmation before execution"""
        config = self.get_config(mode)
        return config.requires_confirmation
    
    def validate_tool_call(
        self, 
        mode: AgentMode, 
        tool_name: str
    ) -> tuple[bool, str]:
        """
        Validate if a tool call is allowed in the current mode.
        
        Returns:
            Tuple of (allowed, reason)
        """
        if mode == AgentMode.AGENT:
            return (True, "")
        
        # Read-only modes
        if tool_name in self.read_only_tools:
            return (True, "")
        
        if tool_name in self.write_tools:
            return (False, f"Tool '{tool_name}' is not allowed in {mode.value} mode (read-only)")
        
        # Unknown tool - be conservative
        return (False, f"Tool '{tool_name}' is not in the allowed list for {mode.value} mode")


# Singleton instance
_mode_router: Optional[ModeRouter] = None


def get_mode_router() -> ModeRouter:
    """Get the singleton ModeRouter instance"""
    global _mode_router
    if _mode_router is None:
        _mode_router = ModeRouter()
    return _mode_router


# Export all
__all__ = [
    "AgentMode",
    "ModeConfig",
    "ModeRouter",
    "get_mode_router",
    "READ_ONLY_TOOLS",
    "WRITE_TOOLS",
    "MODE_CONFIGS",
]

