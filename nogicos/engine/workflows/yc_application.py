# -*- coding: utf-8 -*-
"""
YC Application Workflow - Preset workflow for filling YC application forms

Trigger phrase: "Help me fill out these two questions"

Workflow:
1. Organize desktop (move NogicOS/YC files to YC Application folder)
2. Read product documentation (PITCH_CONTEXT.md)
3. Show confirmation dialog with answer preview
4. Fill YC form via CDP
5. Send WhatsApp notification to ZinoT
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger("nogicos.workflows.yc_application")

# Trigger phrase for this workflow
YC_WORKFLOW_TRIGGER = "help me fill out these two questions"

# Preset answers
ANSWER_FIRST_RUN = """NogicOS is an AI copilot for knowledge workers. Unlike ChatGPT or Cursor, it sees everything on your screen - browser tabs, local files, any app - and helps you work across all of them without copy-pasting context."""

ANSWER_SECOND_RUN = """We're building NogicOS, a desktop AI assistant for knowledge workers (PMs, analysts, researchers) that can read and act across a complete work environment: an embedded browser, user-approved local folders, and desktop apps."""

# WhatsApp messages
WHATSAPP_FIRST = "YC Application Updated ✅"
WHATSAPP_SECOND = "YC Application Updated (2nd revision) ✅"


class WorkflowStep(Enum):
    """Workflow step status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class WorkflowState:
    """State tracking for the workflow"""
    execution_count: int = 0
    desktop_organized: bool = False
    last_answer: str = ""
    steps_completed: Dict[str, WorkflowStep] = field(default_factory=dict)


class YCApplicationWorkflow:
    """
    YC Application preset workflow.
    
    This workflow demonstrates NogicOS's ability to:
    - Read and understand documents
    - Organize files intelligently
    - Fill forms across applications
    - Send notifications
    - Learn from previous executions (smart skip)
    """
    
    DESKTOP_PATH = Path(os.path.expanduser("~")) / "Desktop"
    YC_FOLDER_NAME = "YC Application"
    KEYWORDS = ["nogicos", "yc", "ycombinator", "y combinator"]
    DOCUMENT_PATH = "nogicos/PITCH_CONTEXT.md"
    
    def __init__(self):
        self.state = WorkflowState()
        self._load_state()
    
    def _load_state(self):
        """Load workflow state from persistent storage"""
        # For now, use in-memory state
        # TODO: Persist to disk or database
        pass
    
    def _save_state(self):
        """Save workflow state to persistent storage"""
        pass
    
    def is_trigger_phrase(self, text: str) -> bool:
        """Check if the text matches the trigger phrase"""
        return YC_WORKFLOW_TRIGGER in text.lower()
    
    def get_current_answer(self) -> str:
        """Get the answer based on execution count"""
        if self.state.execution_count == 0:
            return ANSWER_FIRST_RUN
        else:
            return ANSWER_SECOND_RUN
    
    def get_whatsapp_message(self) -> str:
        """Get WhatsApp message based on execution count"""
        if self.state.execution_count == 0:
            return WHATSAPP_FIRST
        else:
            return WHATSAPP_SECOND
    
    def should_skip_desktop_organization(self) -> bool:
        """Check if desktop organization should be skipped"""
        if not self.state.desktop_organized:
            return False
        
        # Check if there are still files to organize
        return not self._has_files_to_organize()
    
    def _has_files_to_organize(self) -> bool:
        """Check if desktop has files matching keywords"""
        if not self.DESKTOP_PATH.exists():
            return False
        
        for item in self.DESKTOP_PATH.iterdir():
            name_lower = item.name.lower()
            for keyword in self.KEYWORDS:
                if keyword in name_lower:
                    # Skip the YC Application folder itself
                    if item.name != self.YC_FOLDER_NAME:
                        return True
        return False
    
    def get_files_to_organize(self) -> list:
        """Get list of files to organize"""
        files = []
        if not self.DESKTOP_PATH.exists():
            return files
        
        for item in self.DESKTOP_PATH.iterdir():
            name_lower = item.name.lower()
            for keyword in self.KEYWORDS:
                if keyword in name_lower and item.name != self.YC_FOLDER_NAME:
                    files.append(item)
                    break
        return files
    
    async def execute_step_organize_desktop(self) -> Dict[str, Any]:
        """Step 1: Organize desktop files"""
        logger.info("[YC Workflow] Step 1: Organizing desktop...")
        
        if self.should_skip_desktop_organization():
            logger.info("[YC Workflow] Desktop already organized, skipping")
            return {
                "status": "skipped",
                "message": "⚡ Desktop already organized, skipping",
                "files_moved": 0,
            }
        
        # Create YC Application folder
        yc_folder = self.DESKTOP_PATH / self.YC_FOLDER_NAME
        yc_folder.mkdir(exist_ok=True)
        
        # Move files
        files_to_move = self.get_files_to_organize()
        moved_files = []
        
        for file in files_to_move:
            try:
                dest = yc_folder / file.name
                file.rename(dest)
                moved_files.append(file.name)
                logger.info(f"[YC Workflow] Moved: {file.name}")
            except Exception as e:
                logger.error(f"[YC Workflow] Failed to move {file.name}: {e}")
        
        self.state.desktop_organized = True
        self._save_state()
        
        return {
            "status": "completed",
            "message": f"📁 Organized {len(moved_files)} files to {self.YC_FOLDER_NAME}/",
            "files_moved": len(moved_files),
            "files": moved_files,
        }
    
    async def execute_step_read_document(self) -> Dict[str, Any]:
        """Step 2: Read product documentation"""
        logger.info("[YC Workflow] Step 2: Reading document...")
        
        try:
            # Read the document
            doc_path = Path(self.DOCUMENT_PATH)
            if not doc_path.exists():
                # Try relative to current directory
                doc_path = Path.cwd() / self.DOCUMENT_PATH
            
            if doc_path.exists():
                content = doc_path.read_text(encoding='utf-8')
                # Extract key sections for display
                lines = content.split('\n')[:30]  # First 30 lines for preview
                preview = '\n'.join(lines)
                
                return {
                    "status": "completed",
                    "message": "📖 Read PITCH_CONTEXT.md",
                    "preview": preview,
                    "full_content": content,
                }
            else:
                return {
                    "status": "completed",
                    "message": "📖 Document path configured",
                    "preview": "(Document will be read from Cursor)",
                }
        except Exception as e:
            logger.error(f"[YC Workflow] Failed to read document: {e}")
            return {
                "status": "failed",
                "message": f"Failed to read document: {e}",
            }
    
    def get_confirmation_data(self) -> Dict[str, Any]:
        """Get data for confirmation dialog"""
        answer = self.get_current_answer()
        is_first_run = self.state.execution_count == 0
        
        return {
            "type": "workflow_confirmation",
            "workflow": "yc_application",
            "title": "NogicOS - Confirm YC Update" + ("" if is_first_run else " (2nd)"),
            "question": "What is your company going to make?",
            "answer": answer,
            "execution_count": self.state.execution_count + 1,
            "skipped_steps": [] if is_first_run else ["desktop_organization"],
            "actions": ["cancel", "confirm"],
        }
    
    async def execute_step_fill_form(self, browser_session) -> Dict[str, Any]:
        """Step 4: Fill YC form via CDP"""
        logger.info("[YC Workflow] Step 4: Filling form...")
        
        answer = self.get_current_answer()
        
        try:
            if browser_session and browser_session.is_started:
                # Find the input field and type
                # The field is for "What is your company going to make?"
                await browser_session.type(
                    'textarea[name="what"], input[name="what"], textarea:has(+ label:contains("What")), textarea',
                    answer
                )
                return {
                    "status": "completed",
                    "message": "✅ Filled YC form",
                    "answer": answer,
                }
            else:
                return {
                    "status": "failed",
                    "message": "No browser session available",
                }
        except Exception as e:
            logger.error(f"[YC Workflow] Failed to fill form: {e}")
            return {
                "status": "failed",
                "message": f"Failed to fill form: {e}",
            }
    
    async def execute_step_whatsapp(self) -> Dict[str, Any]:
        """Step 5: Send WhatsApp notification"""
        logger.info("[YC Workflow] Step 5: Sending WhatsApp notification...")
        
        message = self.get_whatsapp_message()
        
        # This will be executed via desktop tools
        return {
            "status": "pending",
            "message": f"📱 Will send to ZinoT: {message}",
            "whatsapp_message": message,
            "contact": "ZinoT",
        }
    
    def mark_execution_complete(self):
        """Mark workflow execution as complete"""
        self.state.execution_count += 1
        self.state.last_answer = self.get_current_answer()
        self._save_state()
        logger.info(f"[YC Workflow] Execution #{self.state.execution_count} complete")
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get workflow execution summary"""
        is_first_run = self.state.execution_count == 0
        
        return {
            "trigger": YC_WORKFLOW_TRIGGER,
            "execution_count": self.state.execution_count,
            "is_first_run": is_first_run,
            "answer": self.get_current_answer(),
            "whatsapp_message": self.get_whatsapp_message(),
            "will_skip_desktop": self.should_skip_desktop_organization(),
            "steps": [
                {
                    "name": "Organize Desktop",
                    "will_skip": self.should_skip_desktop_organization(),
                },
                {
                    "name": "Read Document",
                    "will_skip": False,
                },
                {
                    "name": "Confirm",
                    "will_skip": False,
                },
                {
                    "name": "Fill Form",
                    "will_skip": False,
                },
                {
                    "name": "WhatsApp",
                    "will_skip": False,
                },
            ],
        }


# Global workflow instance
_workflow_instance: Optional[YCApplicationWorkflow] = None


def get_yc_workflow() -> YCApplicationWorkflow:
    """Get or create the YC Application workflow instance"""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = YCApplicationWorkflow()
    return _workflow_instance
