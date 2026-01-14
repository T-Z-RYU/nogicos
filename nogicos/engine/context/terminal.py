# -*- coding: utf-8 -*-
"""
Terminal State Tracker

Tracks recent terminal commands and their outputs for context injection.
Similar to Cursor's <terminal_files_information> injection.
"""

import os
import time
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from collections import deque


@dataclass
class TerminalCommand:
    """Record of a terminal command execution"""
    command: str
    cwd: str
    exit_code: Optional[int] = None
    output: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    duration_ms: Optional[float] = None


class TerminalTracker:
    """
    Tracks recent terminal commands across sessions.
    
    This provides context about what the user has been doing in the terminal,
    which helps the agent understand the current state of the system.
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize terminal tracker.
        
        Args:
            max_history: Maximum commands to keep in history
        """
        self.max_history = max_history
        # Per-session command history
        self._history: dict[str, deque] = {}
        # Current working directory per session
        self._cwd: dict[str, str] = {}
    
    def record_command(
        self,
        session_id: str,
        command: str,
        cwd: str,
        exit_code: Optional[int] = None,
        output: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> None:
        """
        Record a terminal command execution.
        
        Args:
            session_id: Session identifier
            command: The command that was executed
            cwd: Current working directory
            exit_code: Command exit code (0 = success)
            output: Command output (truncated if too long)
            duration_ms: Execution duration in milliseconds
        """
        if session_id not in self._history:
            self._history[session_id] = deque(maxlen=self.max_history)
        
        # Truncate output if too long
        if output and len(output) > 500:
            output = output[:500] + "... (truncated)"
        
        cmd = TerminalCommand(
            command=command,
            cwd=cwd,
            exit_code=exit_code,
            output=output,
            duration_ms=duration_ms,
        )
        
        self._history[session_id].append(cmd)
        self._cwd[session_id] = cwd
    
    def get_cwd(self, session_id: str) -> str:
        """Get current working directory for session"""
        return self._cwd.get(session_id, os.getcwd())
    
    def get_history(self, session_id: str, limit: int = 5) -> List[TerminalCommand]:
        """
        Get recent command history for session.
        
        Args:
            session_id: Session identifier
            limit: Maximum commands to return
            
        Returns:
            List of recent commands (most recent last)
        """
        if session_id not in self._history:
            return []
        
        history = list(self._history[session_id])
        return history[-limit:]
    
    def format_for_prompt(self, session_id: str) -> str:
        """
        Format terminal history for prompt injection.
        
        Returns XML-like format similar to Cursor's terminal_files_information.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Formatted string for prompt injection
        """
        history = self.get_history(session_id, limit=5)
        cwd = self.get_cwd(session_id)
        
        if not history:
            return f"""<terminal_info>
cwd: {cwd}
recent_commands: (none)
</terminal_info>"""
        
        lines = [f"<terminal_info>", f"cwd: {cwd}", "recent_commands:"]
        
        for cmd in history:
            # Format: command, exit_code, time
            exit_str = f"exit: {cmd.exit_code}" if cmd.exit_code is not None else ""
            duration_str = f", {cmd.duration_ms:.0f}ms" if cmd.duration_ms else ""
            
            lines.append(f"  - {cmd.command}")
            if exit_str:
                lines.append(f"    {exit_str}{duration_str}")
        
        lines.append("</terminal_info>")
        
        return "\n".join(lines)
    
    def clear_session(self, session_id: str) -> None:
        """Clear history for a session"""
        if session_id in self._history:
            del self._history[session_id]
        if session_id in self._cwd:
            del self._cwd[session_id]


# Global instance for convenience
_tracker: Optional[TerminalTracker] = None


def get_terminal_tracker() -> TerminalTracker:
    """Get or create global terminal tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = TerminalTracker()
    return _tracker








