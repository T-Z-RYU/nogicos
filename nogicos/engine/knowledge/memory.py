# -*- coding: utf-8 -*-
"""
Semantic Memory Models

Long-term memory system for NogicOS Agent.
Based on LangMem + Mem0 best practices.

Features:
- Structured memory with subject-predicate-object triples
- Importance scoring for retrieval prioritization
- Embedding vectors for semantic search
- Conflict detection and resolution
"""

import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Literal
from enum import Enum


class MemoryType(str, Enum):
    """Types of memories"""
    FACT = "fact"           # User facts (name, preferences)
    PREFERENCE = "preference"  # User preferences (likes, dislikes)
    EVENT = "event"         # Past events/operations
    RELATIONSHIP = "relationship"  # Relationships between entities
    INSTRUCTION = "instruction"    # User-specific instructions


class Importance(str, Enum):
    """Memory importance levels"""
    HIGH = "high"       # Core preferences, explicit instructions
    MEDIUM = "medium"   # Learned patterns, frequent behaviors
    LOW = "low"         # Incidental information


@dataclass
class Memory:
    """
    Structured memory unit using subject-predicate-object triple.
    
    Examples:
    - ("user", "prefers", "dark mode") 
    - ("user", "frequently_uses", "/Users/WIN/Desktop")
    - ("user", "last_organized", "desktop files by type")
    
    Based on LangMem's Triple schema pattern.
    """
    # Core triple structure
    subject: str            # Who/what (e.g., "user", "system")
    predicate: str          # Relationship (e.g., "prefers", "uses", "created")
    object: str             # Target (e.g., "dark mode", "folder path")
    
    # Metadata
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memory_type: MemoryType = MemoryType.FACT
    importance: Importance = Importance.MEDIUM
    
    # Context
    context: Optional[str] = None   # Additional context
    source_task: Optional[str] = None  # Task that generated this memory
    session_id: str = "default"
    
    # Embedding (stored separately, not in this dataclass for efficiency)
    # embedding: Optional[List[float]] = None  # 1536-dim vector
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Conflict resolution
    version: int = 1
    is_active: bool = True  # False if superseded by newer memory
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['memory_type'] = self.memory_type.value
        data['importance'] = self.importance.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Memory":
        """Create from dictionary"""
        # Convert string enums back to enum types
        if isinstance(data.get('memory_type'), str):
            data['memory_type'] = MemoryType(data['memory_type'])
        if isinstance(data.get('importance'), str):
            data['importance'] = Importance(data['importance'])
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Memory":
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))
    
    def to_text(self) -> str:
        """Convert to natural language for prompt injection"""
        return f"{self.subject} {self.predicate} {self.object}"
    
    def matches(self, other: "Memory") -> bool:
        """Check if this memory conflicts with another (same subject+predicate)"""
        return (
            self.subject.lower() == other.subject.lower() and
            self.predicate.lower() == other.predicate.lower()
        )
    
    def __str__(self) -> str:
        return f"Memory({self.subject} {self.predicate} {self.object})"
    
    def __repr__(self) -> str:
        return f"Memory(id={self.id}, {self.subject} {self.predicate} {self.object}, importance={self.importance.value})"


@dataclass
class Episode:
    """
    Episodic memory capturing a complete interaction.
    
    Based on LangMem's Episode schema for capturing 
    successful interaction patterns.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    session_id: str = "default"
    
    # Episode content
    observation: str = ""      # What happened (context/setup)
    thoughts: str = ""         # Internal reasoning
    action: str = ""           # What was done
    result: str = ""           # Outcome
    
    # Metadata
    task: str = ""             # Original task
    success: bool = True
    importance: Importance = Importance.MEDIUM
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['importance'] = self.importance.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Episode":
        """Create from dictionary"""
        if isinstance(data.get('importance'), str):
            data['importance'] = Importance(data['importance'])
        return cls(**data)
    
    def to_text(self) -> str:
        """Convert to natural language summary"""
        return f"When {self.observation}, I {self.action} which resulted in {self.result}"


@dataclass
class MemorySearchResult:
    """Search result with relevance score"""
    memory: Memory
    score: float  # Cosine similarity score (0-1)
    
    def __str__(self) -> str:
        return f"[{self.score:.2f}] {self.memory}"


# SQL Schema extension for memories
MEMORY_SQL_SCHEMA = """
-- Semantic memories table
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
    embedding BLOB NOT NULL,  -- 1536-dim float32 vector as bytes
    model TEXT DEFAULT 'text-embedding-3-small',
    created_at TEXT,
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
);

-- Episodes table
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


def format_memories_for_prompt(memories: List[Memory], max_items: int = 10) -> str:
    """
    Format memories for injection into system prompt.
    
    Groups memories by type and formats as readable context.
    """
    if not memories:
        return ""
    
    # Sort by importance (high first) then by recency
    sorted_memories = sorted(
        memories[:max_items],
        key=lambda m: (
            0 if m.importance == Importance.HIGH else 1 if m.importance == Importance.MEDIUM else 2,
            m.updated_at
        ),
        reverse=True
    )
    
    lines = ["## Long-term Memory"]
    
    # Group by type
    by_type: Dict[MemoryType, List[Memory]] = {}
    for m in sorted_memories:
        if m.memory_type not in by_type:
            by_type[m.memory_type] = []
        by_type[m.memory_type].append(m)
    
    # Format each type
    type_labels = {
        MemoryType.FACT: "Known Facts",
        MemoryType.PREFERENCE: "User Preferences", 
        MemoryType.EVENT: "Past Events",
        MemoryType.RELATIONSHIP: "Relationships",
        MemoryType.INSTRUCTION: "User Instructions",
    }
    
    for mem_type, mems in by_type.items():
        if mems:
            lines.append(f"\n**{type_labels.get(mem_type, mem_type.value)}:**")
            for m in mems:
                importance_marker = "⭐" if m.importance == Importance.HIGH else ""
                lines.append(f"- {m.to_text()} {importance_marker}")
    
    return "\n".join(lines)

