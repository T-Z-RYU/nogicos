# -*- coding: utf-8 -*-
"""
RAG (Retrieval Augmented Generation) Module

This module provides codebase indexing and retrieval for NogicOS,
enabling Cursor-style code-aware responses.

Components:
- CodebaseIndexer: Indexes code files using LangChain + Chroma
- CodeSearcher: Searches indexed code for relevant snippets
"""

from .indexer import CodebaseIndexer, get_codebase_indexer
from .searcher import CodeSearcher, search_codebase

__all__ = [
    "CodebaseIndexer",
    "get_codebase_indexer",
    "CodeSearcher",
    "search_codebase",
]

