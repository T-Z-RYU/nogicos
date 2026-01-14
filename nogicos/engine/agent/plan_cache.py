# -*- coding: utf-8 -*-
"""
Plan Cache - Intelligent Plan Caching System

Makes NogicOS smarter over time by caching successful execution patterns.
When a similar task is encountered, the agent can reuse the cached plan
for faster execution.

Key Features:
- Semantic similarity matching using embeddings
- Only caches successful plans
- Tracks execution time for speedup metrics
- Thread-safe and persistent (SQLite)
"""

import os
import json
import time
import hashlib
import sqlite3
import threading
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Logging
try:
    from ..observability import get_logger
    logger = get_logger("plan_cache")
except ImportError:
    import logging
    logger = logging.getLogger("plan_cache")

# Anthropic for embeddings (using voyage or fallback to simple hashing)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("[PlanCache] Anthropic not available, using hash-based matching")


@dataclass
class CachedPlan:
    """A cached execution plan with metadata"""
    task: str                          # Original task text
    task_hash: str                     # Hash for quick lookup
    plan_steps: List[Dict[str, Any]]   # List of execution steps
    execution_time: float              # How long it took (seconds)
    success: bool                      # Whether it succeeded
    created_at: str                    # ISO timestamp
    use_count: int = 0                 # How many times reused
    last_used_at: Optional[str] = None # Last reuse timestamp
    embedding: Optional[List[float]] = None  # Semantic embedding (optional)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "CachedPlan":
        return cls(**data)


class PlanCache:
    """
    Intelligent Plan Caching System

    Caches successful execution plans and retrieves them for similar tasks.
    Uses semantic similarity when available, falls back to exact matching.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize Plan Cache.

        Args:
            db_path: Path to SQLite database (default: ~/.nogicos/plan_cache.db)
        """
        if db_path is None:
            cache_dir = os.path.expanduser("~/.nogicos")
            os.makedirs(cache_dir, exist_ok=True)
            db_path = os.path.join(cache_dir, "plan_cache.db")

        self.db_path = db_path
        self._lock = threading.Lock()
        self._memory_cache: Dict[str, CachedPlan] = {}  # In-memory cache for speed
        self._embedding_cache: Dict[str, List[float]] = {}  # Task embeddings

        # Initialize database
        self._init_db()

        # Load existing plans into memory
        self._load_to_memory()

        logger.info(f"[PlanCache] Initialized with {len(self._memory_cache)} cached plans")

    def _init_db(self):
        """Initialize SQLite database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_hash TEXT UNIQUE NOT NULL,
                    task TEXT NOT NULL,
                    plan_steps TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    success INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    use_count INTEGER DEFAULT 0,
                    last_used_at TEXT,
                    embedding TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_hash ON plans(task_hash)
            """)
            conn.commit()

    def _load_to_memory(self):
        """Load all plans from database to memory cache"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT task_hash, task, plan_steps, execution_time, success,
                       created_at, use_count, last_used_at, embedding
                FROM plans WHERE success = 1
            """)
            for row in cursor:
                plan = CachedPlan(
                    task=row[1],
                    task_hash=row[0],
                    plan_steps=json.loads(row[2]),
                    execution_time=row[3],
                    success=bool(row[4]),
                    created_at=row[5],
                    use_count=row[6],
                    last_used_at=row[7],
                    embedding=json.loads(row[8]) if row[8] else None,
                )
                self._memory_cache[row[0]] = plan
                if plan.embedding:
                    self._embedding_cache[row[0]] = plan.embedding

    def _compute_hash(self, task: str) -> str:
        """Compute a hash for a task string"""
        # Normalize: lowercase, strip whitespace, remove punctuation
        normalized = task.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    def _compute_embedding(self, task: str) -> Optional[List[float]]:
        """
        Compute semantic embedding for a task.

        Uses keyword matching with stemming for better similarity detection.
        """
        # Normalize: lowercase, extract words
        words = task.lower().split()
        word_set = set(words)

        # Simple stemming: remove common suffixes
        stemmed_words = set()
        for word in words:
            stemmed_words.add(word)
            # Handle common suffixes
            if word.endswith("ing"):
                stemmed_words.add(word[:-3])
            if word.endswith("s") and len(word) > 3:
                stemmed_words.add(word[:-1])
            if word.endswith("ed") and len(word) > 3:
                stemmed_words.add(word[:-2])

        # Feature categories for better matching
        # Each category maps synonyms to the same feature
        features = [
            # Actions
            {"list", "show", "display", "view", "see", "get"},
            {"click", "tap", "press"},
            {"type", "write", "input", "enter"},
            {"open", "launch", "start", "run"},
            {"close", "exit", "quit", "stop"},
            {"send", "submit", "post"},
            {"save", "store", "download"},
            {"copy", "duplicate"},
            {"paste", "insert"},
            {"fill", "complete"},
            {"navigate", "go", "visit", "browse"},
            {"scroll", "move"},
            {"select", "choose", "pick"},
            {"search", "find", "look", "locate"},
            {"create", "make", "new", "add"},
            {"delete", "remove", "erase"},
            {"upload"},
            {"screenshot", "capture"},
            # Targets
            {"file", "document", "doc"},
            {"folder", "directory", "dir"},
            {"browser", "chrome", "edge", "firefox"},
            {"window", "app", "application"},
            {"form", "field"},
            {"button", "link"},
            {"text", "content", "message"},
            {"image", "picture", "photo"},
            {"current", "this", "here"},
            {"all", "every", "entire"},
        ]

        # Build embedding: 1.0 if any word in the task matches any word in the feature set
        embedding = []
        for feature_set in features:
            match = 1.0 if bool(stemmed_words & feature_set) else 0.0
            embedding.append(match)

        return embedding

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def find_similar(self, task: str, threshold: float = 0.85) -> Optional[Tuple[CachedPlan, float]]:
        """
        Find a similar cached plan for a task.

        Args:
            task: The task to find a match for
            threshold: Minimum similarity score (0-1)

        Returns:
            Tuple of (CachedPlan, similarity_score) if found, None otherwise
        """
        with self._lock:
            # First, try exact match
            task_hash = self._compute_hash(task)
            if task_hash in self._memory_cache:
                plan = self._memory_cache[task_hash]
                logger.info(f"[PlanCache] Exact match found for task")
                return (plan, 1.0)

            # Then, try semantic similarity
            task_embedding = self._compute_embedding(task)
            if not task_embedding:
                return None

            best_match = None
            best_score = 0.0

            logger.info(f"[PlanCache] Searching {len(self._memory_cache)} cached plans for similarity")

            for cached_hash, cached_plan in self._memory_cache.items():
                cached_embedding = self._embedding_cache.get(cached_hash)
                if not cached_embedding:
                    cached_embedding = self._compute_embedding(cached_plan.task)
                    self._embedding_cache[cached_hash] = cached_embedding

                similarity = self._cosine_similarity(task_embedding, cached_embedding)
                logger.info(f"[PlanCache] Similarity with '{cached_plan.task[:40]}...': {similarity:.3f}")
                if similarity > best_score:
                    best_score = similarity
                    best_match = cached_plan

            if best_match and best_score >= threshold:
                logger.info(f"[PlanCache] Similar plan found (score={best_score:.2f})")
                return (best_match, best_score)

            return None

    def cache_plan(
        self,
        task: str,
        plan_steps: List[Dict[str, Any]],
        execution_time: float,
        success: bool = True,
    ) -> Optional[CachedPlan]:
        """
        Cache a plan after execution.

        Args:
            task: The original task
            plan_steps: List of execution steps
            execution_time: Total execution time in seconds
            success: Whether the execution succeeded

        Returns:
            The cached plan if successful, None otherwise
        """
        if not success:
            logger.debug(f"[PlanCache] Not caching failed plan")
            return None

        with self._lock:
            task_hash = self._compute_hash(task)
            embedding = self._compute_embedding(task)

            plan = CachedPlan(
                task=task,
                task_hash=task_hash,
                plan_steps=plan_steps,
                execution_time=execution_time,
                success=success,
                created_at=datetime.now().isoformat(),
                embedding=embedding,
            )

            # Save to database
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO plans
                        (task_hash, task, plan_steps, execution_time, success, created_at, embedding)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        task_hash,
                        task,
                        json.dumps(plan_steps),
                        execution_time,
                        1 if success else 0,
                        plan.created_at,
                        json.dumps(embedding) if embedding else None,
                    ))
                    conn.commit()
            except Exception as e:
                logger.error(f"[PlanCache] Failed to save plan: {e}")
                return None

            # Update memory cache
            self._memory_cache[task_hash] = plan
            if embedding:
                self._embedding_cache[task_hash] = embedding

            logger.info(f"[PlanCache] Cached new plan (total={len(self._memory_cache)})")
            return plan

    def record_use(self, task_hash: str):
        """Record that a cached plan was used"""
        with self._lock:
            if task_hash in self._memory_cache:
                plan = self._memory_cache[task_hash]
                plan.use_count += 1
                plan.last_used_at = datetime.now().isoformat()

                # Update database
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            UPDATE plans SET use_count = ?, last_used_at = ?
                            WHERE task_hash = ?
                        """, (plan.use_count, plan.last_used_at, task_hash))
                        conn.commit()
                except Exception as e:
                    logger.error(f"[PlanCache] Failed to update use count: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_plans = len(self._memory_cache)
            total_uses = sum(p.use_count for p in self._memory_cache.values())
            avg_time = (
                sum(p.execution_time for p in self._memory_cache.values()) / total_plans
                if total_plans > 0 else 0
            )

            return {
                "total_plans": total_plans,
                "total_uses": total_uses,
                "average_execution_time": avg_time,
                "db_path": self.db_path,
            }


# Global instance
_plan_cache: Optional[PlanCache] = None
_plan_cache_lock = threading.Lock()


def get_plan_cache() -> PlanCache:
    """Get the global PlanCache instance (singleton)"""
    global _plan_cache
    if _plan_cache is None:
        with _plan_cache_lock:
            if _plan_cache is None:
                _plan_cache = PlanCache()
    return _plan_cache
