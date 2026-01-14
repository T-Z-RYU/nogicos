# -*- coding: utf-8 -*-
"""
Codebase Indexer - Index code files for RAG retrieval

Uses LangChain's RecursiveCharacterTextSplitter for language-aware chunking
and Chroma for vector storage.

P2 Optimization: Enables Cursor-style codebase search.
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("nogicos.rag.indexer")

# LangChain imports (optional)
LANGCHAIN_AVAILABLE = False
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    LANGCHAIN_AVAILABLE = True
    logger.info("[RAG] LangChain available")
except ImportError:
    logger.warning("[RAG] LangChain not installed. Run: pip install langchain langchain-community chromadb sentence-transformers")
    RecursiveCharacterTextSplitter = None
    Language = None
    Chroma = None


@dataclass
class IndexedFile:
    """Metadata for an indexed file"""
    path: str
    hash: str
    chunks: int
    language: str
    last_indexed: float


class CodebaseIndexer:
    """
    Index codebase files for RAG retrieval.
    
    Features:
    - Language-aware code splitting (Python, TypeScript, JavaScript, etc.)
    - Incremental indexing (only re-index changed files)
    - Vector storage with Chroma
    - Local embeddings (no API calls)
    
    Usage:
        indexer = CodebaseIndexer(workspace_path="/path/to/project")
        await indexer.index()  # Index all files
        results = await indexer.search("authentication logic")
    """
    
    # Language mapping for file extensions
    LANGUAGE_MAP = {
        ".py": "PYTHON",
        ".ts": "TS",
        ".tsx": "TS",
        ".js": "JS",
        ".jsx": "JS",
        ".go": "GO",
        ".rs": "RUST",
        ".java": "JAVA",
        ".cpp": "CPP",
        ".c": "C",
        ".cs": "CSHARP",
        ".rb": "RUBY",
        ".php": "PHP",
        ".md": "MARKDOWN",
        ".html": "HTML",
        ".css": "CSS",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
    }
    
    # Files/directories to ignore
    IGNORE_PATTERNS = {
        "node_modules", ".git", "__pycache__", ".venv", "venv",
        "dist", "build", ".next", ".cache", "coverage",
        ".pytest_cache", ".mypy_cache", ".tox",
        "*.pyc", "*.pyo", "*.egg-info",
    }
    
    def __init__(
        self,
        workspace_path: str,
        persist_dir: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize codebase indexer.
        
        Args:
            workspace_path: Root directory to index
            persist_dir: Directory to store vector database (default: ~/.nogicos/rag)
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.persist_dir = Path(persist_dir or os.path.expanduser("~/.nogicos/rag"))
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Track indexed files
        self._indexed_files: Dict[str, IndexedFile] = {}
        
        # Initialize components (lazy)
        self._embeddings = None
        self._vectorstore = None
        self._splitters: Dict[str, Any] = {}
    
    def _get_embeddings(self):
        """Get or create embeddings model (lazy initialization)"""
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain not available. Install with: pip install langchain langchain-community chromadb sentence-transformers")
        
        if self._embeddings is None:
            # Use local embeddings (no API calls)
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
            logger.info("[RAG] Initialized local embeddings model")
        return self._embeddings
    
    def _get_vectorstore(self):
        """Get or create vector store (lazy initialization)"""
        if self._vectorstore is None:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            collection_name = hashlib.md5(str(self.workspace_path).encode()).hexdigest()[:16]
            
            self._vectorstore = Chroma(
                collection_name=f"codebase_{collection_name}",
                embedding_function=self._get_embeddings(),
                persist_directory=str(self.persist_dir),
            )
            logger.info(f"[RAG] Initialized Chroma vectorstore at {self.persist_dir}")
        return self._vectorstore
    
    def _get_splitter(self, language: str):
        """Get language-specific text splitter"""
        if language not in self._splitters:
            if language in ["PYTHON", "TS", "JS", "GO", "RUST", "JAVA", "CPP", "C", "CSHARP", "RUBY", "PHP", "MARKDOWN", "HTML"]:
                # Use language-aware splitter
                try:
                    lang_enum = getattr(Language, language)
                    self._splitters[language] = RecursiveCharacterTextSplitter.from_language(
                        language=lang_enum,
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap,
                    )
                except (AttributeError, ValueError):
                    # Fallback to generic splitter
                    self._splitters[language] = RecursiveCharacterTextSplitter(
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap,
                    )
            else:
                # Generic splitter
                self._splitters[language] = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
        return self._splitters[language]
    
    def _should_index(self, path: Path) -> bool:
        """Check if file should be indexed"""
        # Check ignore patterns
        for pattern in self.IGNORE_PATTERNS:
            if pattern in path.parts:
                return False
            if path.match(pattern):
                return False
        
        # Check if it's a code file
        return path.suffix.lower() in self.LANGUAGE_MAP
    
    def _get_file_hash(self, path: Path) -> str:
        """Get hash of file contents for change detection"""
        content = path.read_bytes()
        return hashlib.md5(content).hexdigest()
    
    def _get_language(self, path: Path) -> str:
        """Get language from file extension"""
        return self.LANGUAGE_MAP.get(path.suffix.lower(), "TEXT")
    
    async def index_file(self, file_path: Path) -> int:
        """
        Index a single file.
        
        Args:
            file_path: Path to file to index
            
        Returns:
            Number of chunks created
        """
        if not LANGCHAIN_AVAILABLE:
            logger.warning("[RAG] LangChain not available, skipping indexing")
            return 0
        
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                return 0
            
            # Get language and splitter
            language = self._get_language(file_path)
            splitter = self._get_splitter(language)
            
            # Split into chunks
            chunks = splitter.split_text(content)
            
            if not chunks:
                return 0
            
            # Create documents with metadata
            rel_path = file_path.relative_to(self.workspace_path)
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    "source": str(rel_path),
                    "language": language,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "workspace": str(self.workspace_path),
                })
            
            # Add to vectorstore
            vectorstore = self._get_vectorstore()
            vectorstore.add_texts(texts=documents, metadatas=metadatas)
            
            # Track indexed file
            self._indexed_files[str(rel_path)] = IndexedFile(
                path=str(rel_path),
                hash=self._get_file_hash(file_path),
                chunks=len(chunks),
                language=language,
                last_indexed=os.path.getmtime(file_path),
            )
            
            logger.debug(f"[RAG] Indexed {rel_path}: {len(chunks)} chunks")
            return len(chunks)
            
        except Exception as e:
            logger.warning(f"[RAG] Failed to index {file_path}: {e}")
            return 0
    
    async def index(self, force: bool = False) -> Dict[str, int]:
        """
        Index all code files in workspace.
        
        Args:
            force: If True, re-index all files even if unchanged
            
        Returns:
            Statistics dict with indexed/skipped/error counts
        """
        if not LANGCHAIN_AVAILABLE:
            return {"error": "LangChain not available"}
        
        stats = {"indexed": 0, "skipped": 0, "chunks": 0, "errors": 0}
        
        # Find all code files
        for file_path in self.workspace_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            if not self._should_index(file_path):
                continue
            
            # Check if file changed
            rel_path = str(file_path.relative_to(self.workspace_path))
            if not force and rel_path in self._indexed_files:
                current_hash = self._get_file_hash(file_path)
                if current_hash == self._indexed_files[rel_path].hash:
                    stats["skipped"] += 1
                    continue
            
            # Index file
            try:
                chunks = await self.index_file(file_path)
                if chunks > 0:
                    stats["indexed"] += 1
                    stats["chunks"] += chunks
            except Exception as e:
                logger.error(f"[RAG] Error indexing {file_path}: {e}")
                stats["errors"] += 1
        
        logger.info(f"[RAG] Indexing complete: {stats}")
        return stats
    
    async def search(
        self,
        query: str,
        k: int = 5,
        filter_language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search indexed codebase.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_language: Optional language filter (e.g., "PYTHON")
            
        Returns:
            List of search results with content and metadata
        """
        if not LANGCHAIN_AVAILABLE:
            return []
        
        try:
            vectorstore = self._get_vectorstore()
            
            # Build filter
            filter_dict = None
            if filter_language:
                filter_dict = {"language": filter_language}
            
            # Search
            results = vectorstore.similarity_search_with_score(
                query, k=k, filter=filter_dict
            )
            
            # Format results
            formatted = []
            for doc, score in results:
                formatted.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "language": doc.metadata.get("language", "TEXT"),
                    "score": float(score),
                    "chunk_index": doc.metadata.get("chunk_index", 0),
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"[RAG] Search error: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        return {
            "workspace": str(self.workspace_path),
            "indexed_files": len(self._indexed_files),
            "total_chunks": sum(f.chunks for f in self._indexed_files.values()),
            "languages": list(set(f.language for f in self._indexed_files.values())),
        }


# Global instance
_indexer: Optional[CodebaseIndexer] = None


def get_codebase_indexer(workspace_path: Optional[str] = None) -> CodebaseIndexer:
    """Get or create global codebase indexer"""
    global _indexer
    if _indexer is None and workspace_path:
        _indexer = CodebaseIndexer(workspace_path)
    return _indexer

