# -*- coding: utf-8 -*-
"""
Code Searcher - Search indexed codebase for relevant snippets

Provides a simple interface for RAG-based code retrieval.
"""

import logging
from typing import Optional, List, Dict, Any

from .indexer import get_codebase_indexer, CodebaseIndexer

logger = logging.getLogger("nogicos.rag.searcher")


class CodeSearcher:
    """
    Search indexed codebase for relevant code snippets.
    
    This is a wrapper around CodebaseIndexer that provides
    a simpler interface for searching.
    
    Usage:
        searcher = CodeSearcher(workspace_path="/path/to/project")
        results = await searcher.search("authentication logic")
        for result in results:
            print(f"{result['source']}: {result['content'][:100]}")
    """
    
    def __init__(
        self,
        workspace_path: Optional[str] = None,
        indexer: Optional[CodebaseIndexer] = None,
    ):
        """
        Initialize code searcher.
        
        Args:
            workspace_path: Workspace to search in
            indexer: Optional pre-configured indexer
        """
        self._indexer = indexer or get_codebase_indexer(workspace_path)
    
    async def ensure_indexed(self) -> bool:
        """
        Ensure codebase is indexed.
        
        Returns:
            True if indexing succeeded or already done
        """
        if not self._indexer:
            logger.warning("[CodeSearcher] No indexer configured")
            return False
        
        stats = self._indexer.get_stats()
        if stats["indexed_files"] == 0:
            logger.info("[CodeSearcher] Indexing codebase...")
            await self._indexer.index()
        
        return True
    
    async def search(
        self,
        query: str,
        k: int = 5,
        language: Optional[str] = None,
        auto_index: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search codebase for relevant code.
        
        Args:
            query: Search query (natural language or code pattern)
            k: Number of results to return
            language: Optional filter by language (e.g., "PYTHON", "TS")
            auto_index: If True, index codebase if not already done
            
        Returns:
            List of results with content, source, language, and score
        """
        if not self._indexer:
            return []
        
        if auto_index:
            await self.ensure_indexed()
        
        return await self._indexer.search(query, k=k, filter_language=language)
    
    def format_for_prompt(self, results: List[Dict[str, Any]], max_chars: int = 2000) -> str:
        """
        Format search results for inclusion in LLM prompt.
        
        Args:
            results: Search results from search()
            max_chars: Maximum total characters
            
        Returns:
            Formatted string for prompt injection
        """
        if not results:
            return ""
        
        lines = ["## Relevant Code from Codebase\n"]
        total_chars = 0
        
        for result in results:
            source = result.get("source", "unknown")
            content = result.get("content", "")
            language = result.get("language", "").lower()
            score = result.get("score", 0)
            
            # Format as code block
            block = f"\n### {source} (relevance: {score:.2f})\n```{language}\n{content}\n```\n"
            
            if total_chars + len(block) > max_chars:
                break
            
            lines.append(block)
            total_chars += len(block)
        
        return "".join(lines)


# Convenience function
async def search_codebase(
    query: str,
    workspace_path: Optional[str] = None,
    k: int = 5,
    language: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search codebase for relevant code (convenience function).
    
    Args:
        query: Search query
        workspace_path: Workspace to search in
        k: Number of results
        language: Optional language filter
        
    Returns:
        List of search results
    """
    searcher = CodeSearcher(workspace_path=workspace_path)
    return await searcher.search(query, k=k, language=language)

