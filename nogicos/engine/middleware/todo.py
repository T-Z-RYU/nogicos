# -*- coding: utf-8 -*-
"""
Todo Middleware - Deep Agents pattern for task planning

Reference: Deep Agents TodoListMiddleware
"""

import uuid
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from ..tools.base import ToolRegistry, ToolCategory, get_registry

logger = logging.getLogger(__name__)


class TodoStatus(str, Enum):
    """Todo item status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TodoItem:
    """A todo item for task planning"""
    id: str
    content: str
    status: TodoStatus = TodoStatus.PENDING
    order: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "status": self.status.value,
            "order": self.order
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoItem':
        return cls(
            id=data["id"],
            content=data["content"],
            status=TodoStatus(data.get("status", "pending")),
            order=data.get("order", 0)
        )


class TodoBackend:
    """Backend for managing todo items"""
    
    def __init__(self):
        self._todos: Dict[str, TodoItem] = {}
        self._order_counter = 0
    
    def add(self, content: str, todo_id: Optional[str] = None) -> TodoItem:
        """Add a new todo item"""
        if todo_id is None:
            todo_id = str(uuid.uuid4())[:8]
        
        todo = TodoItem(
            id=todo_id,
            content=content,
            status=TodoStatus.PENDING,
            order=self._order_counter
        )
        self._order_counter += 1
        self._todos[todo_id] = todo
        return todo
    
    def update_status(self, todo_id: str, status: TodoStatus) -> Optional[TodoItem]:
        """Update todo status"""
        if todo_id in self._todos:
            self._todos[todo_id].status = status
            return self._todos[todo_id]
        return None
    
    def get(self, todo_id: str) -> Optional[TodoItem]:
        """Get a todo by ID"""
        return self._todos.get(todo_id)
    
    def get_all(self) -> List[TodoItem]:
        """Get all todos sorted by order"""
        return sorted(self._todos.values(), key=lambda t: t.order)
    
    def get_by_status(self, status: TodoStatus) -> List[TodoItem]:
        """Get todos by status"""
        return [t for t in self.get_all() if t.status == status]
    
    def remove(self, todo_id: str) -> bool:
        """Remove a todo"""
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all todos"""
        self._todos.clear()
        self._order_counter = 0
    
    def get_progress(self) -> Dict[str, int]:
        """Get progress statistics"""
        stats = {status.value: 0 for status in TodoStatus}
        for todo in self._todos.values():
            stats[todo.status.value] += 1
        stats["total"] = len(self._todos)
        return stats
    
    def get_state(self) -> List[Dict[str, Any]]:
        """Get state for serialization"""
        return [t.to_dict() for t in self.get_all()]
    
    def load_state(self, state: List[Dict[str, Any]]) -> None:
        """Load state from serialized data"""
        self.clear()
        for item in state:
            todo = TodoItem.from_dict(item)
            self._todos[todo.id] = todo
            self._order_counter = max(self._order_counter, todo.order + 1)


class TodoMiddleware:
    """
    Middleware that provides todo/planning tools to the agent.
    
    Follows Deep Agents pattern:
    - Automatic tool injection
    - Task planning and tracking
    - Progress monitoring
    """
    
    SYSTEM_PROMPT_ADDITION = """
You have access to a todo list for planning and tracking your tasks.
For complex tasks:
1. Break down the work into steps using write_todos
2. Mark each step as in_progress when starting
3. Mark each step as completed when done
4. Use read_todos to check your progress

This helps you stay organized and ensures nothing is forgotten.
"""
    
    def __init__(
        self,
        backend: Optional[TodoBackend] = None,
        registry: Optional[ToolRegistry] = None
    ):
        """
        Args:
            backend: Todo backend to use
            registry: Tool registry to register tools in
        """
        self.backend = backend or TodoBackend()
        self.registry = registry or get_registry()
        
        # Register todo tools
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register todo-specific tools"""
        
        @self.registry.action(
            description="Create one or more todo items for planning. Pass a list of task descriptions.",
            category=ToolCategory.PLAN
        )
        async def write_todos(tasks: str) -> str:
            """Write todos from a comma or newline separated list"""
            try:
                # Parse tasks (comma or newline separated)
                task_list = [t.strip() for t in tasks.replace('\n', ',').split(',') if t.strip()]
                
                if not task_list:
                    return "No tasks provided."
                
                created = []
                for task in task_list:
                    todo = self.backend.add(task)
                    created.append(f"- [{todo.id}] {todo.content}")
                
                return f"Created {len(created)} todos:\n" + "\n".join(created)
            except Exception as e:
                return f"Error creating todos: {str(e)}"
        
        @self.registry.action(
            description="Read all todo items and their current status.",
            category=ToolCategory.PLAN
        )
        async def read_todos() -> str:
            """Read all todos"""
            try:
                todos = self.backend.get_all()
                if not todos:
                    return "No todos yet. Use write_todos to create some."
                
                status_emoji = {
                    TodoStatus.PENDING: "⬜",
                    TodoStatus.IN_PROGRESS: "🔄",
                    TodoStatus.COMPLETED: "✅",
                    TodoStatus.CANCELLED: "❌"
                }
                
                lines = []
                for todo in todos:
                    emoji = status_emoji.get(todo.status, "⬜")
                    lines.append(f"{emoji} [{todo.id}] {todo.content}")
                
                progress = self.backend.get_progress()
                summary = f"\nProgress: {progress['completed']}/{progress['total']} completed"
                
                return "Todos:\n" + "\n".join(lines) + summary
            except Exception as e:
                return f"Error reading todos: {str(e)}"
        
        @self.registry.action(
            description="Update the status of a todo item. Status can be: pending, in_progress, completed, cancelled.",
            category=ToolCategory.PLAN
        )
        async def update_todo(todo_id: str, status: str) -> str:
            """Update todo status"""
            try:
                try:
                    new_status = TodoStatus(status.lower())
                except ValueError:
                    return f"Invalid status. Use: pending, in_progress, completed, cancelled"
                
                todo = self.backend.update_status(todo_id, new_status)
                if todo:
                    return f"Updated [{todo_id}] to {status}"
                return f"Todo not found: {todo_id}"
            except Exception as e:
                return f"Error updating todo: {str(e)}"
        
        @self.registry.action(
            description="Get progress statistics for todos.",
            category=ToolCategory.PLAN
        )
        async def todo_progress() -> str:
            """Get todo progress"""
            try:
                progress = self.backend.get_progress()
                total = progress["total"]
                if total == 0:
                    return "No todos yet."
                
                completed = progress["completed"]
                pct = int(completed / total * 100)
                
                return f"""Todo Progress:
- Pending: {progress['pending']}
- In Progress: {progress['in_progress']}
- Completed: {progress['completed']}
- Cancelled: {progress['cancelled']}
- Total: {total}
- Completion: {pct}%"""
            except Exception as e:
                return f"Error getting progress: {str(e)}"
        
        logger.info("TodoMiddleware tools registered")
    
    def get_state(self) -> List[Dict[str, Any]]:
        """Get current todo state for serialization"""
        return self.backend.get_state()
    
    def load_state(self, state: List[Dict[str, Any]]) -> None:
        """Load todo state"""
        self.backend.load_state(state)
    
    def get_system_prompt_addition(self) -> str:
        """Get additional system prompt for todo context"""
        return self.SYSTEM_PROMPT_ADDITION


