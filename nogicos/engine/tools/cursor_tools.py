# -*- coding: utf-8 -*-
"""
Cursor-style Tools - Additional tools inspired by Cursor's capabilities

Includes:
- web_search: Real-time web search using Tavily API
- todo_write: Task management
- update_memory: Persistent memory across sessions
"""

import os
import json
import sqlite3
import logging
import aiohttp
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from .base import ToolRegistry, ToolCategory, get_registry

logger = logging.getLogger(__name__)

# Database path for persistence
DB_PATH = Path(__file__).parent.parent.parent / "data" / "agent_state.db"


def _ensure_db():
    """Ensure database and tables exist"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Create todos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create memories table with namespace for scoping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            namespace TEXT DEFAULT 'default',
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for faster searches
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace)
    """)
    
    conn.commit()
    conn.close()


def register_cursor_tools(registry: Optional[ToolRegistry] = None) -> ToolRegistry:
    """Register Cursor-style tools"""
    
    if registry is None:
        registry = get_registry()
    
    # Ensure database exists
    _ensure_db()
    
    # ========================================
    # Web Search (Tavily API)
    # ========================================
    
    @registry.action(
        description="""Search the web for real-time information.

WHEN TO USE:
- Current events, news, updates
- Technical documentation lookup
- Package/library information
- Any information that might have changed recently

WHEN NOT TO USE:
- Searching local codebase → use grep_search or codebase_search
- File lookups → use glob_search
- Known static information

Parameters:
- query: Search query (be specific for better results)
- max_results: Number of results (default: 5)

Returns: Search results with snippets and URLs""",
        category=ToolCategory.LOCAL
    )
    async def web_search(query: str, max_results: int = 5) -> str:
        """Search web using Tavily API"""
        try:
            # Try to get API key
            api_key = os.environ.get("TAVILY_API_KEY")
            
            if not api_key:
                try:
                    from api_keys import TAVILY_API_KEY
                    api_key = TAVILY_API_KEY
                except ImportError:
                    pass
            
            if not api_key:
                return "Error: TAVILY_API_KEY not configured. Set it in environment or api_keys.py"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": api_key,
                        "query": query,
                        "max_results": max_results,
                        "include_answer": True,
                        "include_raw_content": False
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return f"Error: Tavily API returned {response.status}: {error_text}"
                    
                    data = await response.json()
            
            # Format results
            results = []
            
            if data.get("answer"):
                results.append(f"**Summary:** {data['answer']}\n")
            
            for i, result in enumerate(data.get("results", []), 1):
                title = result.get("title", "No title")
                url = result.get("url", "")
                snippet = result.get("content", "")[:300]
                results.append(f"{i}. **{title}**\n   {url}\n   {snippet}...")
            
            if not results:
                return f"No results found for: {query}"
            
            return '\n\n'.join(results)
            
        except aiohttp.ClientError as e:
            return f"Network error during search: {str(e)}"
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"Error performing search: {str(e)}"
    
    # ========================================
    # Todo Management
    # ========================================
    
    @registry.action(
        description="""Manage task list for current session.

WHEN TO USE:
- Complex multi-step tasks (3+ steps)
- User provides multiple tasks
- Need to track progress on work

WHEN NOT TO USE:
- Single simple tasks
- Trivial operations
- Purely conversational requests

Parameters:
- action: 'list', 'add', 'update', or 'clear'
- todos: List of {id, content, status} for add/update
- merge: If True, merge with existing (default: True)

Status values: pending, in_progress, completed, cancelled""",
        category=ToolCategory.LOCAL
    )
    async def todo_write(
        action: str = "list",
        todos: List[Dict[str, str]] = None,
        merge: bool = True
    ) -> str:
        """Manage todo list"""
        # #region agent log H3
        import json as _json; open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"H3","location":"cursor_tools.py:todo_write:entry","message":"todo_write called","data":{"action":action,"todos_type":str(type(todos)),"todos_sample":str(todos)[:200] if todos else None,"merge":merge},"timestamp":__import__('time').time()})+'\n')
        # #endregion
        try:
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                
                if action == "list":
                    cursor.execute("SELECT id, content, status, created_at FROM todos ORDER BY created_at")
                    rows = cursor.fetchall()
                    
                    if not rows:
                        return "No todos found. Use action='add' to create tasks."
                    
                    result = ["Current TODOs:"]
                    for row in rows:
                        status_emoji = {
                            'pending': '⬜',
                            'in_progress': '🔄',
                            'completed': '✅',
                            'cancelled': '❌'
                        }.get(row[2], '⬜')
                        result.append(f"{status_emoji} [{row[0]}] {row[1]} ({row[2]})")
                    
                    return '\n'.join(result)
                
                elif action == "add" and todos:
                    for idx, todo in enumerate(todos):
                        # #region agent log H3
                        open(r'c:\Users\TE\532-CorporateHell-Git\nogicos\.cursor\debug.log','a',encoding='utf-8').write(_json.dumps({"hypothesisId":"H3","location":"cursor_tools.py:todo_write:add_item","message":"Processing todo item","data":{"idx":idx,"todo_type":str(type(todo)),"todo_value":str(todo)[:100]},"timestamp":__import__('time').time()})+'\n')
                        # #endregion
                        if isinstance(todo, str):
                            # AI passed string instead of dict - convert to dict
                            todo = {"content": todo, "status": "pending"}
                        todo_id = todo.get('id', f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                        content = todo.get('content', '')
                        status = todo.get('status', 'pending')
                        
                        if merge:
                            cursor.execute("""
                                INSERT OR REPLACE INTO todos (id, content, status, updated_at)
                                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                            """, (todo_id, content, status))
                        else:
                            cursor.execute("""
                                INSERT INTO todos (id, content, status)
                                VALUES (?, ?, ?)
                            """, (todo_id, content, status))
                    
                    conn.commit()
                    return f"Added/updated {len(todos)} todo(s)"
                
                elif action == "update" and todos:
                    for todo in todos:
                        todo_id = todo.get('id')
                        if not todo_id:
                            continue
                        
                        updates = []
                        params = []
                        
                        if 'content' in todo:
                            updates.append("content = ?")
                            params.append(todo['content'])
                        if 'status' in todo:
                            updates.append("status = ?")
                            params.append(todo['status'])
                        
                        if updates:
                            updates.append("updated_at = CURRENT_TIMESTAMP")
                            params.append(todo_id)
                            cursor.execute(f"""
                                UPDATE todos SET {', '.join(updates)} WHERE id = ?
                            """, params)
                    
                    conn.commit()
                    return f"Updated {len(todos)} todo(s)"
                
                elif action == "clear":
                    cursor.execute("DELETE FROM todos")
                    conn.commit()
                    return "Cleared all todos"
                
                else:
                    return "Invalid action. Use: list, add, update, or clear"
            
        except Exception as e:
            logger.error(f"Todo operation failed: {e}")
            return f"Error managing todos: {str(e)}"
    
    # ========================================
    # Memory Management
    # ========================================
    
    @registry.action(
        description="""Create, update, or delete persistent memory.

WHEN TO USE:
- User explicitly asks to remember something
- Storing user preferences
- Saving important context for future sessions

WHEN NOT TO USE:
- Task-specific temporary information
- Implementation details
- Don't create memories unless user asks

Actions:
- create: Store new memory (requires title + content)
- update: Modify existing (requires id + content)
- delete: Remove memory (requires id)
- list: Show all memories

Parameters:
- action: 'create', 'update', 'delete', or 'list'
- memory_id: Memory ID (for update/delete)
- title: Memory title (for create)
- content: Memory content (for create/update)""",
        category=ToolCategory.LOCAL
    )
    async def update_memory(
        action: str = "list",
        memory_id: str = None,
        title: str = None,
        content: str = None
    ) -> str:
        """Manage persistent memory"""
        try:
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                
                if action == "list":
                    cursor.execute("SELECT id, title, content, created_at FROM memories ORDER BY created_at DESC")
                    rows = cursor.fetchall()
                    
                    if not rows:
                        return "No memories stored."
                    
                    result = ["Stored Memories:"]
                    for row in rows:
                        result.append(f"[{row[0]}] **{row[1]}**\n   {row[2][:100]}...")
                    
                    return '\n\n'.join(result)
                
                elif action == "create":
                    if not title or not content:
                        return "Error: 'create' requires both title and content"
                    
                    new_id = memory_id or f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    cursor.execute("""
                        INSERT INTO memories (id, title, content)
                        VALUES (?, ?, ?)
                    """, (new_id, title, content))
                    
                    conn.commit()
                    return f"Created memory: [{new_id}] {title}"
                
                elif action == "update":
                    if not memory_id:
                        return "Error: 'update' requires memory_id"
                    
                    # Check if exists
                    cursor.execute("SELECT id FROM memories WHERE id = ?", (memory_id,))
                    if not cursor.fetchone():
                        return f"Error: Memory '{memory_id}' not found"
                    
                    updates = ["updated_at = CURRENT_TIMESTAMP"]
                    params = []
                    
                    if title:
                        updates.append("title = ?")
                        params.append(title)
                    if content:
                        updates.append("content = ?")
                        params.append(content)
                    
                    params.append(memory_id)
                    cursor.execute(f"""
                        UPDATE memories SET {', '.join(updates)} WHERE id = ?
                    """, params)
                    
                    conn.commit()
                    return f"Updated memory: {memory_id}"
                
                elif action == "delete":
                    if not memory_id:
                        return "Error: 'delete' requires memory_id"
                    
                    cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                    
                    if cursor.rowcount == 0:
                        return f"Error: Memory '{memory_id}' not found"
                    
                    conn.commit()
                    return f"Deleted memory: {memory_id}"
                
                else:
                    return "Invalid action. Use: list, create, update, or delete"
            
        except Exception as e:
            logger.error(f"Memory operation failed: {e}")
            return f"Error managing memory: {str(e)}"
    
    # ========================================
    # Memory Search (Keyword-based)
    # ========================================
    
    @registry.action(
        description="""Search memories by keyword.

WHEN TO USE:
- Retrieving stored user preferences
- Finding previously saved information
- Context retrieval for current task

Parameters:
- query: Search query (matches title and content)
- namespace: Memory namespace (default: 'default')
- limit: Max results (default: 5)

Returns: Matching memories with relevance""",
        category=ToolCategory.LOCAL
    )
    async def search_memory(
        query: str,
        namespace: str = "default",
        limit: int = 5
    ) -> str:
        """Search memories by keyword"""
        try:
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                
                # Simple keyword search (LIKE query)
                # For semantic search, would use vector embeddings
                search_pattern = f"%{query}%"
                cursor.execute("""
                    SELECT id, title, content, created_at 
                    FROM memories 
                    WHERE (namespace = ? OR namespace = 'default')
                      AND (title LIKE ? OR content LIKE ?)
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (namespace, search_pattern, search_pattern, limit))
                
                rows = cursor.fetchall()
                
                if not rows:
                    return f"No memories found matching: {query}"
                
                results = [f"Found {len(rows)} matching memories:"]
                for row in rows:
                    results.append(f"\n[{row[0]}] **{row[1]}**\n{row[2][:200]}...")
                
                return '\n'.join(results)
                
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return f"Error searching memories: {str(e)}"
    
    # ========================================
    # Get All Memories for Context Injection
    # ========================================
    
    def get_memories_for_prompt(namespace: str = "default", limit: int = 5) -> List[Dict[str, str]]:
        """
        Get memories for prompt injection (non-async, for context injector).
        
        Returns list of {id, title, content} dictionaries.
        """
        try:
            _ensure_db()
            with sqlite3.connect(str(DB_PATH)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, content 
                    FROM memories 
                    WHERE namespace = ? OR namespace = 'default'
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (namespace, limit))
                
                rows = cursor.fetchall()
                return [{"id": r[0], "title": r[1], "content": r[2]} for r in rows]
                
        except Exception as e:
            logger.warning(f"Failed to get memories: {e}")
            return []
    
    # Export helper function
    registry._memory_getter = get_memories_for_prompt
    
    logger.info(f"Registered Cursor-style tools")
    return registry

