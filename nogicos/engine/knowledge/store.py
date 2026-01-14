# -*- coding: utf-8 -*-
"""
Knowledge Store - SQLite-based Persistent Storage

B1: Knowledge Storage Architecture
- SQLite database for persistence
- UserProfile management
- Trajectory storage and retrieval
- Learned skill extraction
"""

import os
import json
import sqlite3
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from .models import UserProfile, Trajectory, LearnedSkill, SQL_SCHEMA

logger = logging.getLogger("nogicos.knowledge")


class KnowledgeStore:
    """
    SQLite-based knowledge store for persistent context.
    
    Features:
    - User profile management (B1.2)
    - Trajectory storage (B1.3)
    - Learned skill management
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize knowledge store.
        
        Args:
            db_path: Path to SQLite database file.
                     Defaults to ~/.nogicos/knowledge.db
        """
        if db_path is None:
            # Default to user home directory
            home = os.path.expanduser("~")
            nogicos_dir = os.path.join(home, ".nogicos")
            os.makedirs(nogicos_dir, exist_ok=True)
            db_path = os.path.join(nogicos_dir, "knowledge.db")
        
        self.db_path = db_path
        self._init_database()
        
        logger.info(f"[Knowledge] Initialized store at {db_path}")
    
    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            conn.executescript(SQL_SCHEMA)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # ========================================================================
    # User Profile Management (B1.2)
    # ========================================================================
    
    def get_profile(self, profile_id: str = "default") -> UserProfile:
        """
        Get user profile by ID. Creates default if not exists.
        
        Args:
            profile_id: Profile ID (default: "default")
            
        Returns:
            UserProfile instance
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM user_profiles WHERE id = ?",
                (profile_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                # Create default profile
                profile = UserProfile(id=profile_id)
                self.save_profile(profile)
                return profile
            
            return UserProfile(
                id=row["id"],
                frequent_folders=json.loads(row["frequent_folders"] or "[]"),
                frequent_websites=json.loads(row["frequent_websites"] or "[]"),
                preferences=json.loads(row["preferences"] or "{}"),
                common_tasks=json.loads(row["common_tasks"] or "[]"),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
    
    def save_profile(self, profile: UserProfile):
        """
        Save user profile.
        
        Args:
            profile: UserProfile instance
        """
        profile.updated_at = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_profiles 
                (id, frequent_folders, frequent_websites, preferences, 
                 common_tasks, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.id,
                json.dumps(profile.frequent_folders, ensure_ascii=False),
                json.dumps(profile.frequent_websites, ensure_ascii=False),
                json.dumps(profile.preferences, ensure_ascii=False),
                json.dumps(profile.common_tasks, ensure_ascii=False),
                profile.created_at,
                profile.updated_at,
            ))
            conn.commit()
        
        logger.debug(f"[Knowledge] Saved profile: {profile.id}")
    
    def update_profile_from_execution(
        self,
        profile_id: str,
        task: str,
        tool_calls: List[Dict[str, Any]],
    ):
        """
        Update profile based on execution history (B2.4 Preference Learning).
        
        Extracts patterns from tool calls to update:
        - Frequent folders (from file operations)
        - Frequent websites (from browser operations)
        - Common tasks
        
        Args:
            profile_id: Profile ID
            task: Task description
            tool_calls: List of tool calls made
        """
        profile = self.get_profile(profile_id)
        
        # Extract paths and URLs from tool calls
        for call in tool_calls:
            tool_name = call.get("name", "")
            args = call.get("args", {})
            success = call.get("success", False)
            
            if not success:
                continue
            
            # File operations → frequent folders
            if tool_name in ["list_directory", "read_file", "write_file", "move_file"]:
                path = args.get("path") or args.get("source") or args.get("directory")
                if path:
                    # Extract folder from path
                    folder = os.path.dirname(path) if os.path.isfile(path) else path
                    if folder:
                        profile.add_frequent_folder(folder)
            
            # Browser operations → frequent websites
            if tool_name == "browser_navigate":
                url = args.get("url")
                if url:
                    profile.add_frequent_website(url)
        
        # Add task to common tasks (if not duplicate)
        task_normalized = task.strip().lower()
        if task_normalized and task_normalized not in [t.lower() for t in profile.common_tasks]:
            profile.common_tasks.insert(0, task)
            profile.common_tasks = profile.common_tasks[:20]  # Keep last 20
        
        self.save_profile(profile)
    
    # ========================================================================
    # Trajectory Management (B1.3)
    # ========================================================================
    
    def save_trajectory(self, trajectory: Trajectory) -> str:
        """
        Save execution trajectory.
        
        Args:
            trajectory: Trajectory instance
            
        Returns:
            Trajectory ID
        """
        if not trajectory.id:
            trajectory.id = str(uuid.uuid4())[:8]
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO trajectories
                (id, session_id, task, url, tool_calls, success, error,
                 context, created_at, duration_ms, iterations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trajectory.id,
                trajectory.session_id,
                trajectory.task,
                trajectory.url,
                json.dumps(trajectory.tool_calls, ensure_ascii=False),
                1 if trajectory.success else 0,
                trajectory.error,
                json.dumps(trajectory.context, ensure_ascii=False),
                trajectory.created_at,
                trajectory.duration_ms,
                trajectory.iterations,
            ))
            conn.commit()
        
        logger.debug(f"[Knowledge] Saved trajectory: {trajectory.id}")
        return trajectory.id
    
    def get_trajectory(self, trajectory_id: str) -> Optional[Trajectory]:
        """
        Get trajectory by ID.
        
        Args:
            trajectory_id: Trajectory ID
            
        Returns:
            Trajectory instance or None
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM trajectories WHERE id = ?",
                (trajectory_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_trajectory(row)
    
    def search_trajectories(
        self,
        query: str = "",
        session_id: Optional[str] = None,
        success_only: bool = False,
        limit: int = 10,
    ) -> List[Trajectory]:
        """
        Search trajectories.
        
        Args:
            query: Search query (matches task description)
            session_id: Filter by session ID
            success_only: Only return successful trajectories
            limit: Maximum results
            
        Returns:
            List of matching trajectories
        """
        conditions = []
        params = []
        
        if query:
            conditions.append("task LIKE ?")
            params.append(f"%{query}%")
        
        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)
        
        if success_only:
            conditions.append("success = 1")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._get_connection() as conn:
            cursor = conn.execute(f"""
                SELECT * FROM trajectories
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
            """, params + [limit])
            
            return [self._row_to_trajectory(row) for row in cursor.fetchall()]
    
    def get_recent_trajectories(
        self,
        session_id: str,
        limit: int = 10,
    ) -> List[Trajectory]:
        """
        Get recent trajectories for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum results
            
        Returns:
            List of recent trajectories
        """
        return self.search_trajectories(
            session_id=session_id,
            limit=limit,
        )
    
    def _row_to_trajectory(self, row) -> Trajectory:
        """Convert database row to Trajectory"""
        return Trajectory(
            id=row["id"],
            session_id=row["session_id"],
            task=row["task"],
            url=row["url"],
            tool_calls=json.loads(row["tool_calls"] or "[]"),
            success=bool(row["success"]),
            error=row["error"],
            context=json.loads(row["context"] or "{}"),
            created_at=row["created_at"],
            duration_ms=row["duration_ms"] or 0.0,
            iterations=row["iterations"] or 0,
        )
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge store statistics"""
        with self._get_connection() as conn:
            # Count trajectories
            cursor = conn.execute("SELECT COUNT(*) FROM trajectories")
            trajectory_count = cursor.fetchone()[0]
            
            # Count successful
            cursor = conn.execute("SELECT COUNT(*) FROM trajectories WHERE success = 1")
            success_count = cursor.fetchone()[0]
            
            # Count profiles
            cursor = conn.execute("SELECT COUNT(*) FROM user_profiles")
            profile_count = cursor.fetchone()[0]
            
            # Count skills
            cursor = conn.execute("SELECT COUNT(*) FROM learned_skills")
            skill_count = cursor.fetchone()[0]
        
        return {
            "trajectory_count": trajectory_count,
            "success_count": success_count,
            "success_rate": success_count / trajectory_count if trajectory_count > 0 else 0,
            "profile_count": profile_count,
            "skill_count": skill_count,
            "db_path": self.db_path,
        }


# Global instance
_store: Optional[KnowledgeStore] = None


def get_store() -> KnowledgeStore:
    """Get or create global knowledge store instance"""
    global _store
    if _store is None:
        _store = KnowledgeStore()
    return _store


# ============================================================================
# Session Persistence (Plan: 2.2 SessionPersistence)
# ============================================================================

class PersistentSessionStore:
    """
    Simple session persistence for cross-session memory.
    
    Stores:
    - Session history (messages)
    - User preferences per session
    - Last active timestamp
    
    This allows users to "resume" previous sessions and maintain context.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize persistent session store.
        
        Args:
            db_path: Path to SQLite database.
                     Defaults to ~/.nogicos/sessions.db
        """
        if db_path is None:
            home = os.path.expanduser("~")
            nogicos_dir = os.path.join(home, ".nogicos")
            os.makedirs(nogicos_dir, exist_ok=True)
            db_path = os.path.join(nogicos_dir, "sessions.db")
        
        self.db_path = db_path
        self._init_database()
        
        logger.info(f"[Sessions] Initialized store at {db_path}")
    
    def _init_database(self):
        """Initialize session database schema"""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    history TEXT NOT NULL DEFAULT '[]',
                    preferences TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0
                );
                
                CREATE INDEX IF NOT EXISTS idx_sessions_updated 
                ON sessions(updated_at DESC);
                
                CREATE TABLE IF NOT EXISTS session_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tool_calls TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON session_messages(session_id);
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_session(
        self,
        session_id: str,
        history: List[Dict[str, Any]],
        preferences: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
    ):
        """
        Save or update a session.
        
        Args:
            session_id: Unique session identifier
            history: List of message dictionaries
            preferences: Optional user preferences for this session
            title: Optional session title (auto-generated from first message if None)
        """
        now = datetime.now().isoformat()
        
        # Auto-generate title from first user message if not provided
        if title is None and history:
            for msg in history:
                if msg.get("role") == "user":
                    content = msg.get("content", "")
                    title = content[:50] + ("..." if len(content) > 50 else "")
                    break
        
        title = title or f"Session {session_id[:8]}"
        preferences = preferences or {}
        
        with self._get_connection() as conn:
            # Check if session exists
            cursor = conn.execute(
                "SELECT id, created_at FROM sessions WHERE id = ?",
                (session_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing session
                conn.execute("""
                    UPDATE sessions 
                    SET history = ?, preferences = ?, title = ?, 
                        updated_at = ?, message_count = ?
                    WHERE id = ?
                """, (
                    json.dumps(history, ensure_ascii=False),
                    json.dumps(preferences, ensure_ascii=False),
                    title,
                    now,
                    len(history),
                    session_id,
                ))
            else:
                # Insert new session
                conn.execute("""
                    INSERT INTO sessions 
                    (id, title, history, preferences, created_at, updated_at, message_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    title,
                    json.dumps(history, ensure_ascii=False),
                    json.dumps(preferences, ensure_ascii=False),
                    now,
                    now,
                    len(history),
                ))
            
            conn.commit()
        
        logger.debug(f"[Sessions] Saved session {session_id} ({len(history)} messages)")
    
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """
        Load a session by ID.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            Dictionary with 'history', 'preferences', 'title', etc.
            Returns empty history if session doesn't exist.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return {
                    "id": session_id,
                    "title": f"New Session",
                    "history": [],
                    "preferences": {},
                    "created_at": None,
                    "updated_at": None,
                }
            
            return {
                "id": row["id"],
                "title": row["title"],
                "history": json.loads(row["history"] or "[]"),
                "preferences": json.loads(row["preferences"] or "{}"),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"],
            }
    
    def list_sessions(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List recent sessions.
        
        Args:
            limit: Maximum sessions to return
            offset: Offset for pagination
            
        Returns:
            List of session summaries (without full history)
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, title, created_at, updated_at, message_count
                FROM sessions
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            return [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "message_count": row["message_count"],
                }
                for row in cursor.fetchall()
            ]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if session was deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM sessions WHERE id = ?",
                (session_id,)
            )
            conn.commit()
            
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"[Sessions] Deleted session {session_id}")
            
            return deleted
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
    ):
        """
        Add a single message to a session (incremental update).
        
        Args:
            session_id: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
            tool_calls: Optional tool calls for assistant messages
        """
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            # Insert message
            conn.execute("""
                INSERT INTO session_messages 
                (session_id, role, content, tool_calls, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                role,
                content,
                json.dumps(tool_calls, ensure_ascii=False) if tool_calls else None,
                now,
            ))
            
            # Update session timestamp and count
            conn.execute("""
                UPDATE sessions 
                SET updated_at = ?, message_count = message_count + 1
                WHERE id = ?
            """, (now, session_id))
            
            conn.commit()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session store statistics"""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            session_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT SUM(message_count) FROM sessions")
            total_messages = cursor.fetchone()[0] or 0
            
            cursor = conn.execute("""
                SELECT MAX(updated_at) FROM sessions
            """)
            last_activity = cursor.fetchone()[0]
        
        return {
            "session_count": session_count,
            "total_messages": total_messages,
            "last_activity": last_activity,
            "db_path": self.db_path,
        }


# Global session store instance
_session_store: Optional[PersistentSessionStore] = None


def get_session_store() -> PersistentSessionStore:
    """Get or create global session store instance"""
    global _session_store
    if _session_store is None:
        _session_store = PersistentSessionStore()
    return _session_store


# ============================================================================
# Semantic Memory Store (Long-term Memory System)
# ============================================================================

class SemanticMemoryStore:
    """
    Semantic memory store with embedding-based retrieval.
    
    Based on LangMem + Mem0 architecture:
    - Store memories as subject-predicate-object triples
    - Use embeddings for semantic search
    - Support conflict detection and resolution
    
    Features:
    - Add/update/delete memories
    - Semantic search with cosine similarity
    - Session-scoped memory isolation
    - Importance-based prioritization
    """
    
    EMBEDDING_DIM = 1536  # text-embedding-3-small dimension
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize semantic memory store.
        
        Args:
            db_path: Path to SQLite database.
                     Defaults to ~/.nogicos/memory.db
        """
        if db_path is None:
            home = os.path.expanduser("~")
            nogicos_dir = os.path.join(home, ".nogicos")
            os.makedirs(nogicos_dir, exist_ok=True)
            db_path = os.path.join(nogicos_dir, "memory.db")
        
        self.db_path = db_path
        self._embedding_client = None
        self._init_database()
        
        logger.info(f"[Memory] Initialized store at {db_path}")
    
    def _init_database(self):
        """Initialize memory database schema"""
        # Import schema from memory module
        from .memory import MEMORY_SQL_SCHEMA
        
        with self._get_connection() as conn:
            conn.executescript(MEMORY_SQL_SCHEMA)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _get_embedding_client(self):
        """Lazy-load OpenAI client for embeddings"""
        if self._embedding_client is None:
            try:
                import openai
                # Try api_keys.py first, then environment variable
                api_key = None
                try:
                    import api_keys
                    api_key = api_keys.OPENAI_API_KEY
                except (ImportError, AttributeError):
                    api_key = os.environ.get("OPENAI_API_KEY")
                
                if api_key:
                    self._embedding_client = openai.OpenAI(api_key=api_key)
                else:
                    logger.warning("[Memory] OPENAI_API_KEY not set, embeddings disabled")
            except ImportError:
                logger.warning("[Memory] openai package not installed, embeddings disabled")
        return self._embedding_client
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            1536-dim embedding vector or None if unavailable
        """
        client = self._get_embedding_client()
        if client is None:
            return None
        
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"[Memory] Embedding error: {e}")
            return None
    
    def _embedding_to_bytes(self, embedding: List[float]) -> bytes:
        """Convert embedding list to bytes for storage"""
        import struct
        return struct.pack(f'{len(embedding)}f', *embedding)
    
    def _bytes_to_embedding(self, data: bytes) -> List[float]:
        """Convert bytes back to embedding list"""
        import struct
        count = len(data) // 4  # 4 bytes per float
        return list(struct.unpack(f'{count}f', data))
    
    async def add_memory(
        self,
        subject: str,
        predicate: str,
        obj: str,
        session_id: str = "default",
        memory_type: str = "fact",
        importance: str = "medium",
        context: Optional[str] = None,
        source_task: Optional[str] = None,
    ) -> str:
        """
        Add a new memory.
        
        Handles conflict detection: if a memory with same subject+predicate
        exists, it will be superseded (marked inactive).
        
        Args:
            subject: Memory subject (e.g., "user")
            predicate: Relationship (e.g., "prefers")
            obj: Object (e.g., "dark mode")
            session_id: Session ID for scoping
            memory_type: Type (fact/preference/event/relationship/instruction)
            importance: Importance level (high/medium/low)
            context: Additional context
            source_task: Task that generated this memory
            
        Returns:
            Memory ID
        """
        from .memory import Memory, MemoryType, Importance
        
        memory_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            # Check for conflicting memories (same subject + predicate)
            cursor = conn.execute("""
                SELECT id FROM memories 
                WHERE session_id = ? AND subject = ? AND predicate = ? AND is_active = 1
            """, (session_id, subject.lower(), predicate.lower()))
            
            existing = cursor.fetchall()
            
            # Mark existing conflicting memories as inactive
            if existing:
                for row in existing:
                    conn.execute("""
                        UPDATE memories SET is_active = 0, updated_at = ?
                        WHERE id = ?
                    """, (now, row["id"]))
                logger.debug(f"[Memory] Superseded {len(existing)} existing memories")
            
            # Insert new memory
            conn.execute("""
                INSERT INTO memories 
                (id, session_id, subject, predicate, object, memory_type, 
                 importance, context, source_task, version, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
            """, (
                memory_id,
                session_id,
                subject.lower(),
                predicate.lower(),
                obj,
                memory_type,
                importance,
                context,
                source_task,
                now,
                now,
            ))
            conn.commit()
        
        # Generate and store embedding asynchronously
        memory_text = f"{subject} {predicate} {obj}"
        embedding = await self.get_embedding(memory_text)
        
        if embedding:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memory_embeddings 
                    (memory_id, embedding, model, created_at)
                    VALUES (?, ?, 'text-embedding-3-small', ?)
                """, (memory_id, self._embedding_to_bytes(embedding), now))
                conn.commit()
        
        logger.debug(f"[Memory] Added: {subject} {predicate} {obj} (id={memory_id})")
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory by ID"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memories WHERE id = ?",
                (memory_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return dict(row)
    
    def list_memories(
        self,
        session_id: str = "default",
        memory_type: Optional[str] = None,
        importance: Optional[str] = None,
        active_only: bool = True,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List memories with optional filtering.
        
        Args:
            session_id: Filter by session
            memory_type: Filter by type
            importance: Filter by importance
            active_only: Only return active memories
            limit: Maximum results
            
        Returns:
            List of memory dictionaries
        """
        conditions = ["session_id = ?"]
        params: List[Any] = [session_id]
        
        if active_only:
            conditions.append("is_active = 1")
        
        if memory_type:
            conditions.append("memory_type = ?")
            params.append(memory_type)
        
        if importance:
            conditions.append("importance = ?")
            params.append(importance)
        
        where_clause = " AND ".join(conditions)
        
        with self._get_connection() as conn:
            cursor = conn.execute(f"""
                SELECT * FROM memories
                WHERE {where_clause}
                ORDER BY 
                    CASE importance 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        ELSE 3 
                    END,
                    updated_at DESC
                LIMIT ?
            """, params + [limit])
            
            return [dict(row) for row in cursor.fetchall()]
    
    async def search_memories(
        self,
        query: str,
        session_id: str = "default",
        limit: int = 5,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant memories.
        
        Args:
            query: Search query
            session_id: Filter by session
            limit: Maximum results
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of memories with similarity scores
        """
        # Get query embedding
        query_embedding = await self.get_embedding(query)
        
        if query_embedding is None:
            # Fallback to keyword search if embeddings unavailable
            return self._keyword_search(query, session_id, limit)
        
        # Get all active memories with embeddings
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT m.*, e.embedding
                FROM memories m
                JOIN memory_embeddings e ON m.id = e.memory_id
                WHERE m.session_id = ? AND m.is_active = 1
            """, (session_id,))
            
            rows = cursor.fetchall()
        
        if not rows:
            return []
        
        # Calculate cosine similarities
        results = []
        for row in rows:
            memory_embedding = self._bytes_to_embedding(row["embedding"])
            score = self._cosine_similarity(query_embedding, memory_embedding)
            
            if score >= threshold:
                memory_dict = dict(row)
                del memory_dict["embedding"]  # Don't return raw embedding
                memory_dict["score"] = score
                results.append(memory_dict)
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:limit]
    
    def _keyword_search(
        self,
        query: str,
        session_id: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Fallback keyword search when embeddings unavailable"""
        keywords = query.lower().split()
        
        with self._get_connection() as conn:
            # Simple LIKE search on subject, predicate, object
            conditions = []
            params = [session_id]
            
            for keyword in keywords[:5]:  # Limit keywords
                conditions.append(
                    "(subject LIKE ? OR predicate LIKE ? OR object LIKE ?)"
                )
                pattern = f"%{keyword}%"
                params.extend([pattern, pattern, pattern])
            
            if conditions:
                keyword_clause = " OR ".join(conditions)
                query_sql = f"""
                    SELECT * FROM memories
                    WHERE session_id = ? AND is_active = 1 AND ({keyword_clause})
                    ORDER BY importance, updated_at DESC
                    LIMIT ?
                """
            else:
                query_sql = """
                    SELECT * FROM memories
                    WHERE session_id = ? AND is_active = 1
                    ORDER BY importance, updated_at DESC
                    LIMIT ?
                """
            
            params.append(limit)
            cursor = conn.execute(query_sql, params)
            
            results = []
            for row in cursor.fetchall():
                memory_dict = dict(row)
                memory_dict["score"] = 0.5  # Default score for keyword matches
                results.append(memory_dict)
            
            return results
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory (soft delete - mark as inactive).
        
        Args:
            memory_id: Memory ID to delete
            
        Returns:
            True if deleted
        """
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE memories SET is_active = 0, updated_at = ?
                WHERE id = ?
            """, (now, memory_id))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM memories WHERE is_active = 1"
            )
            active_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            total_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM memory_embeddings")
            embedding_count = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT importance, COUNT(*) as count
                FROM memories WHERE is_active = 1
                GROUP BY importance
            """)
            by_importance = {row["importance"]: row["count"] for row in cursor.fetchall()}
        
        return {
            "active_memories": active_count,
            "total_memories": total_count,
            "embeddings": embedding_count,
            "by_importance": by_importance,
            "db_path": self.db_path,
        }


# Global semantic memory store instance
_memory_store: Optional[SemanticMemoryStore] = None


def get_memory_store() -> SemanticMemoryStore:
    """Get or create global semantic memory store instance"""
    global _memory_store
    if _memory_store is None:
        _memory_store = SemanticMemoryStore()
    return _memory_store

