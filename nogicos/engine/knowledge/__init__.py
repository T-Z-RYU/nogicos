# -*- coding: utf-8 -*-
"""
NogicOS Knowledge Store - Persistent Context System

Phase B: Persistent user context, operation history, and learning.

Architecture:
    SQLite Database
    ├── user_profiles    - User preferences and context
    ├── trajectories     - Operation history for learning
    ├── learned_skills   - Extracted skills from trajectories
    ├── memories         - Long-term semantic memory (subject-predicate-object)
    ├── memory_embeddings - Embedding vectors for semantic search
    └── episodes         - Episodic memory for interaction patterns
"""

from .store import KnowledgeStore, PersistentSessionStore, SemanticMemoryStore
from .store import get_store, get_session_store, get_memory_store
from .models import UserProfile, Trajectory, LearnedSkill
from .memory import Memory, Episode, MemoryType, Importance, MemorySearchResult
from .memory import format_memories_for_prompt
from .extractor import MemoryExtractor, BackgroundMemoryProcessor
from .extractor import extract_memories_from_conversation
from .search import SemanticMemorySearch, SearchConfig
from .search import search_memories, get_memory_context

__all__ = [
    # Stores
    "KnowledgeStore",
    "PersistentSessionStore", 
    "SemanticMemoryStore",
    "get_store",
    "get_session_store",
    "get_memory_store",
    # Legacy models
    "UserProfile",
    "Trajectory",
    "LearnedSkill",
    # Memory models
    "Memory",
    "Episode",
    "MemoryType",
    "Importance",
    "MemorySearchResult",
    "format_memories_for_prompt",
    # Extraction
    "MemoryExtractor",
    "BackgroundMemoryProcessor",
    "extract_memories_from_conversation",
    # Search
    "SemanticMemorySearch",
    "SearchConfig",
    "search_memories",
    "get_memory_context",
]

