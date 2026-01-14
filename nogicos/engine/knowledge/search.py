# -*- coding: utf-8 -*-
"""
Semantic Memory Search - Embedding-based retrieval for long-term memory.

Features:
- Cosine similarity search with embeddings
- Hybrid search (semantic + keyword fallback)
- Reranking by importance
- Context formatting for prompt injection

Based on Mem0's search architecture.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .memory import Memory, MemorySearchResult, Importance, format_memories_for_prompt

logger = logging.getLogger("nogicos.memory")


@dataclass
class SearchConfig:
    """Configuration for memory search"""
    limit: int = 5              # Max results
    threshold: float = 0.5      # Min similarity score (0-1)
    boost_high_importance: float = 0.1  # Score boost for high importance
    boost_medium_importance: float = 0.05  # Score boost for medium importance
    include_context: bool = True  # Include context in results


class SemanticMemorySearch:
    """
    High-level semantic search interface for memories.
    
    Provides:
    - Semantic search with relevance scoring
    - Hybrid search with keyword fallback
    - Importance-based reranking
    - Formatted output for prompt injection
    """
    
    def __init__(self, memory_store):
        """
        Initialize search with memory store.
        
        Args:
            memory_store: SemanticMemoryStore instance
        """
        self.memory_store = memory_store
    
    async def search(
        self,
        query: str,
        session_id: str = "default",
        config: Optional[SearchConfig] = None,
    ) -> List[MemorySearchResult]:
        """
        Search for relevant memories.
        
        Args:
            query: Search query (natural language)
            session_id: Session scope
            config: Search configuration
            
        Returns:
            List of MemorySearchResult with scores
        """
        config = config or SearchConfig()
        
        # Perform search
        results = await self.memory_store.search_memories(
            query=query,
            session_id=session_id,
            limit=config.limit * 2,  # Get extra for reranking
            threshold=config.threshold,
        )
        
        # Convert to MemorySearchResult and apply importance boosting
        search_results = []
        for r in results:
            score = r.get("score", 0.5)
            
            # Apply importance boost
            importance = r.get("importance", "medium")
            if importance == "high":
                score = min(1.0, score + config.boost_high_importance)
            elif importance == "medium":
                score = min(1.0, score + config.boost_medium_importance)
            
            # Convert to Memory object
            memory = Memory(
                id=r.get("id", ""),
                subject=r.get("subject", ""),
                predicate=r.get("predicate", ""),
                object=r.get("object", ""),
                importance=Importance(r.get("importance", "medium")),
                context=r.get("context") if config.include_context else None,
                session_id=r.get("session_id", session_id),
                source_task=r.get("source_task"),
                created_at=r.get("created_at", ""),
                updated_at=r.get("updated_at", ""),
            )
            
            search_results.append(MemorySearchResult(
                memory=memory,
                score=score,
            ))
        
        # Sort by score descending
        search_results.sort(key=lambda x: x.score, reverse=True)
        
        # Return limited results
        return search_results[:config.limit]
    
    async def search_for_prompt(
        self,
        query: str,
        session_id: str = "default",
        max_tokens: int = 500,
    ) -> str:
        """
        Search and format results for prompt injection.
        
        Args:
            query: Search query
            session_id: Session scope
            max_tokens: Approximate max output length
            
        Returns:
            Formatted string for prompt injection
        """
        # Estimate ~5 chars per token
        max_chars = max_tokens * 5
        
        results = await self.search(
            query=query,
            session_id=session_id,
            config=SearchConfig(limit=10),  # Get more for filtering
        )
        
        if not results:
            return ""
        
        # Extract memories
        memories = [r.memory for r in results]
        
        # Format with limit
        formatted = format_memories_for_prompt(memories)
        
        # Truncate if needed
        if len(formatted) > max_chars:
            formatted = formatted[:max_chars] + "\n..."
        
        return formatted
    
    async def get_relevant_context(
        self,
        task: str,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """
        Get relevant memory context for a task.
        
        Returns structured context with different memory types.
        
        Args:
            task: Current task description
            session_id: Session scope
            
        Returns:
            Dict with 'memories', 'formatted', 'count'
        """
        results = await self.search(
            query=task,
            session_id=session_id,
            config=SearchConfig(
                limit=10,
                threshold=0.4,  # Lower threshold for more context
            ),
        )
        
        # Group by memory type
        by_type: Dict[str, List[Memory]] = {}
        for r in results:
            mem_type = r.memory.memory_type.value if hasattr(r.memory, 'memory_type') else "fact"
            if mem_type not in by_type:
                by_type[mem_type] = []
            by_type[mem_type].append(r.memory)
        
        # Format for prompt
        formatted = format_memories_for_prompt([r.memory for r in results])
        
        return {
            "memories": [r.memory for r in results],
            "scores": [r.score for r in results],
            "by_type": by_type,
            "formatted": formatted,
            "count": len(results),
        }


async def search_memories(
    query: str,
    session_id: str = "default",
    limit: int = 5,
) -> str:
    """
    Convenience function for quick memory search.
    
    Returns formatted string for prompt injection.
    """
    from .store import get_memory_store
    
    store = get_memory_store()
    search = SemanticMemorySearch(store)
    
    return await search.search_for_prompt(
        query=query,
        session_id=session_id,
    )


async def get_memory_context(
    task: str,
    session_id: str = "default",
) -> Dict[str, Any]:
    """
    Convenience function for getting memory context.
    
    Returns dict with memories and formatted string.
    """
    from .store import get_memory_store
    
    store = get_memory_store()
    search = SemanticMemorySearch(store)
    
    return await search.get_relevant_context(
        task=task,
        session_id=session_id,
    )

