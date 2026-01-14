# -*- coding: utf-8 -*-
"""
Knowledge Store Data Models

B1.1 SQLite Table Design:
- user_profiles: User preferences and frequently used paths
- trajectories: Operation history for learning
- learned_skills: Extracted skills from successful trajectories
"""

import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class UserProfile:
    """
    User profile for persistent context (B1.2).
    
    Stores:
    - Frequently used folders
    - Frequently visited websites
    - User preferences
    - Operation patterns
    """
    id: str = "default"
    
    # Frequently used paths (auto-learned)
    frequent_folders: List[str] = field(default_factory=list)
    frequent_websites: List[str] = field(default_factory=list)
    
    # User preferences
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Operation patterns (for personalization)
    common_tasks: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """Create from dictionary"""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "UserProfile":
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))
    
    def add_frequent_folder(self, path: str, max_items: int = 10):
        """Add a folder to frequent list (auto-dedupe, limit size)"""
        if path in self.frequent_folders:
            self.frequent_folders.remove(path)
        self.frequent_folders.insert(0, path)
        self.frequent_folders = self.frequent_folders[:max_items]
        self.updated_at = datetime.now().isoformat()
    
    def add_frequent_website(self, url: str, max_items: int = 10):
        """Add a website to frequent list"""
        # Normalize URL (remove trailing slash, etc.)
        url = url.rstrip('/')
        if url in self.frequent_websites:
            self.frequent_websites.remove(url)
        self.frequent_websites.insert(0, url)
        self.frequent_websites = self.frequent_websites[:max_items]
        self.updated_at = datetime.now().isoformat()
    
    def get_context_for_prompt(self) -> str:
        """Generate context string for system prompt injection (B2.3)"""
        lines = ["## User Context"]
        
        if self.frequent_folders:
            lines.append("\n**Frequently used folders:**")
            for folder in self.frequent_folders[:5]:
                lines.append(f"- {folder}")
        
        if self.frequent_websites:
            lines.append("\n**Frequently visited websites:**")
            for site in self.frequent_websites[:5]:
                lines.append(f"- {site}")
        
        if self.common_tasks:
            lines.append("\n**Common tasks:**")
            for task in self.common_tasks[:5]:
                lines.append(f"- {task}")
        
        return "\n".join(lines) if len(lines) > 1 else ""


@dataclass
class Trajectory:
    """
    Operation trajectory for learning (B1.3).
    
    Records:
    - Task description
    - Tool calls sequence
    - Success/failure status
    - Context at execution time
    """
    id: str = ""
    session_id: str = "default"
    
    # Task info
    task: str = ""
    url: Optional[str] = None
    
    # Execution trace
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = False
    error: Optional[str] = None
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: float = 0.0
    iterations: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Trajectory":
        """Create from dictionary"""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Trajectory":
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))


@dataclass  
class LearnedSkill:
    """
    Extracted skill from successful trajectories.
    
    A skill is a parameterized action sequence that can be
    replayed for similar tasks.
    """
    id: str = ""
    name: str = ""
    description: str = ""
    
    # Pattern matching
    task_pattern: str = ""  # Regex or keywords for matching
    domain: str = ""  # e.g., "browser", "file_system"
    
    # Execution template
    tool_sequence: List[Dict[str, Any]] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)  # Extractable params
    
    # Stats
    success_count: int = 0
    failure_count: int = 0
    avg_duration_ms: float = 0.0
    
    # Source
    source_trajectory_ids: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "LearnedSkill":
        """Create from dictionary"""
        return cls(**data)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


# SQL Schema for SQLite
SQL_SCHEMA = """
-- User profiles table (B1.2)
CREATE TABLE IF NOT EXISTS user_profiles (
    id TEXT PRIMARY KEY,
    frequent_folders TEXT,  -- JSON array
    frequent_websites TEXT, -- JSON array
    preferences TEXT,       -- JSON object
    common_tasks TEXT,      -- JSON array
    created_at TEXT,
    updated_at TEXT
);

-- Trajectories table (B1.3)
CREATE TABLE IF NOT EXISTS trajectories (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    task TEXT,
    url TEXT,
    tool_calls TEXT,        -- JSON array
    success INTEGER,
    error TEXT,
    context TEXT,           -- JSON object
    created_at TEXT,
    duration_ms REAL,
    iterations INTEGER
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_trajectories_session ON trajectories(session_id);
CREATE INDEX IF NOT EXISTS idx_trajectories_task ON trajectories(task);
CREATE INDEX IF NOT EXISTS idx_trajectories_created ON trajectories(created_at);

-- Learned skills table
CREATE TABLE IF NOT EXISTS learned_skills (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    task_pattern TEXT,
    domain TEXT,
    tool_sequence TEXT,     -- JSON array
    parameters TEXT,        -- JSON array
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_duration_ms REAL DEFAULT 0,
    source_trajectory_ids TEXT,  -- JSON array
    created_at TEXT,
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_skills_domain ON learned_skills(domain);
CREATE INDEX IF NOT EXISTS idx_skills_pattern ON learned_skills(task_pattern);

-- ============================================================
-- Semantic Memory Tables (Long-term Memory System)
-- ============================================================

-- Semantic memories table (subject-predicate-object triples)
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    memory_type TEXT DEFAULT 'fact',
    importance TEXT DEFAULT 'medium',
    context TEXT,
    source_task TEXT,
    version INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT
);

-- Embeddings table (separate for efficiency)
CREATE TABLE IF NOT EXISTS memory_embeddings (
    memory_id TEXT PRIMARY KEY,
    embedding BLOB NOT NULL,
    model TEXT DEFAULT 'text-embedding-3-small',
    created_at TEXT,
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
);

-- Episodes table (episodic memory)
CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    observation TEXT,
    thoughts TEXT,
    action TEXT,
    result TEXT,
    task TEXT,
    success INTEGER DEFAULT 1,
    importance TEXT DEFAULT 'medium',
    created_at TEXT
);

-- Indexes for fast retrieval
CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_active ON memories(is_active);
CREATE INDEX IF NOT EXISTS idx_memories_subject ON memories(subject);

CREATE INDEX IF NOT EXISTS idx_episodes_session ON episodes(session_id);
CREATE INDEX IF NOT EXISTS idx_episodes_success ON episodes(success);
"""

