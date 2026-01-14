"""
NogicOS Async数据Library封装
======================

解决 SQLite Sync阻塞问题。

方案:
1. aiosqlite - 纯Async，推荐
2. Connect池管理
3. 批量Write优化

参考:
- LangGraph Checkpointer 持久化Policy
- UFO Blackboard State管理
"""

import asyncio
import json
import logging
from typing import Optional, List, Dict, Any, Union, TYPE_CHECKING
from contextlib import asynccontextmanager
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# tryImport aiosqlite
try:
    import aiosqlite
    HAS_AIOSQLITE = True
    DBConnection = aiosqlite.Connection
except ImportError:
    HAS_AIOSQLITE = False
    aiosqlite = None  # type: ignore
    DBConnection = Any  # type: ignore
    logger.warning("aiosqlite not installed - AsyncTaskStore will not work")


class AiosqliteNotInstalledError(Exception):
    """aiosqlite 未安装Error"""
    pass


@dataclass
class TaskRecord:
    """任务记录"""
    id: str
    status: str
    task_text: str
    target_hwnds: str
    created_at: str
    updated_at: str


class AsyncTaskStore:
    """
    Async任务存储 - 替代原Sync TaskStore
    
    特性:
    - 完全Async，不阻塞EventLoop
    - Connect池管理
    - 批量Write优化 (缓冲区)
    - WAL 模式提升ConcurrentPerformance
    """
    
    def __init__(self, db_path: str = "nogicos_tasks.db", pool_size: int = 3):
        """
        InitializeAsync任务存储
        
        Args:
            db_path: 数据LibraryFilePath
            pool_size: Connect池Size
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool: List[DBConnection] = []
        self._pool_lock = asyncio.Lock()
        self._write_buffer: List[tuple] = []
        self._buffer_lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task[None]] = None
        self._initialized = False
    
    async def initialize(self):
        """
        InitializeConnect池和Table结构
        
        Raises:
            AiosqliteNotInstalledError: 如果 aiosqlite 未安装
        """
        if self._initialized:
            return
        
        if not HAS_AIOSQLITE:
            raise AiosqliteNotInstalledError(
                "aiosqlite is required for AsyncTaskStore. "
                "Install it with: pip install aiosqlite"
            )
        
        # CreateConnectpool
        for _ in range(self.pool_size):
            conn = await aiosqlite.connect(self.db_path)
            await conn.execute("PRAGMA journal_mode=WAL")  # mentionupgradeConcurrentPerformance
            await conn.execute("PRAGMA synchronous=NORMAL")
            await conn.execute("PRAGMA cache_size=10000")
            self._pool.append(conn)
        
        # CreateTablestructure
        async with self._get_connection() as conn:
            await conn.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    task_text TEXT,
                    target_hwnds TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    iteration INTEGER,
                    state_json TEXT,
                    screenshot_id TEXT,
                    is_full INTEGER DEFAULT 1,
                    created_at TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_checkpoints_task 
                ON checkpoints(task_id, iteration DESC);
                
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_messages_task
                ON messages(task_id, timestamp);
            """)
            await conn.commit()
        
        # StartperiodicRefreshTask
        self._flush_task = asyncio.create_task(self._periodic_flush())
        self._initialized = True
        logger.info(f"AsyncTaskStore initialized: {self.db_path}")
    
    @asynccontextmanager
    async def _get_connection(self):
        """从Connect池GetConnect"""
        async with self._pool_lock:
            if self._pool:
                conn = self._pool.pop()
            else:
                # poolEmptytimeCreateTemporaryConnect
                conn = await aiosqlite.connect(self.db_path)
        
        try:
            yield conn
        finally:
            async with self._pool_lock:
                if len(self._pool) < self.pool_size:
                    self._pool.append(conn)
                else:
                    await conn.close()
    
    # ========== TaskAction ==========
    
    async def create_task(
        self, 
        task_id: str, 
        task_text: str,
        target_hwnds: Optional[List[int]] = None,
    ) -> bool:
        """CreateNew任务"""
        now = datetime.now().isoformat()
        hwnds_str = json.dumps(target_hwnds or [])
        
        async with self._get_connection() as conn:
            await conn.execute(
                """INSERT INTO tasks (id, status, task_text, target_hwnds, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (task_id, "pending", task_text, hwnds_str, now, now)
            )
            await conn.commit()
        
        return True
    
    async def update_status(self, task_id: str, status: str) -> bool:
        """Update任务State"""
        now = datetime.now().isoformat()
        
        async with self._get_connection() as conn:
            await conn.execute(
                "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, task_id)
            )
            await conn.commit()
        
        return True
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get任务Info"""
        async with self._get_connection() as conn:
            async with conn.execute(
                "SELECT id, status, task_text, target_hwnds, created_at, updated_at FROM tasks WHERE id = ?",
                (task_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "status": row[1],
                        "task_text": row[2],
                        "target_hwnds": json.loads(row[3]) if row[3] else [],
                        "created_at": row[4],
                        "updated_at": row[5],
                    }
        return None
    
    # ========== CheckPointAction ==========
    
    async def save_checkpoint(
        self, 
        task_id: str, 
        iteration: int, 
        state: dict,
        screenshot_id: str = None,
        is_full: bool = True,
    ):
        """
        AsyncSaveCheck点 - 带缓冲批量Write
        
        Args:
            task_id: 任务 ID
            iteration: Iterate次数
            state: StateDict
            screenshot_id: Off联的截Graph ID
            is_full: YesNo全量Check点
        """
        now = datetime.now().isoformat()
        
        async with self._buffer_lock:
            self._write_buffer.append((
                "checkpoint",
                (task_id, iteration, json.dumps(state), screenshot_id, 1 if is_full else 0, now)
            ))
        
        # BufferareaFulltimeImmediateRefresh
        if len(self._write_buffer) >= 10:
            await self._flush_buffer()
    
    async def restore_checkpoint(self, task_id: str) -> Optional[dict]:
        """Resume最NewCheck点"""
        async with self._get_connection() as conn:
            async with conn.execute(
                """SELECT state_json FROM checkpoints 
                   WHERE task_id = ? ORDER BY iteration DESC LIMIT 1""",
                (task_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return json.loads(row[0]) if row else None
    
    async def get_all_checkpoints(self, task_id: str) -> List[Dict[str, Any]]:
        """Get所有Check点（用于增量Resume）"""
        async with self._get_connection() as conn:
            async with conn.execute(
                """SELECT iteration, state_json, is_full FROM checkpoints 
                   WHERE task_id = ? ORDER BY iteration ASC""",
                (task_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {"iteration": r[0], "state": json.loads(r[1]), "is_full": bool(r[2])}
                    for r in rows
                ]
    
    # ========== MessageAction ==========
    
    async def save_message(self, task_id: str, role: str, content: str):
        """SaveMessage"""
        now = datetime.now().isoformat()
        
        async with self._buffer_lock:
            self._write_buffer.append((
                "message",
                (task_id, role, content, now)
            ))
    
    async def get_messages(self, task_id: str) -> List[Dict[str, Any]]:
        """Get任务的所有Message"""
        async with self._get_connection() as conn:
            async with conn.execute(
                "SELECT role, content, timestamp FROM messages WHERE task_id = ? ORDER BY timestamp",
                (task_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows]
    
    # ========== Bufferareamanage ==========
    
    # RetryConfig
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_BASE = 0.5  # baseDelayed（Second）
    
    async def _flush_buffer(self, max_retries: int = None) -> bool:
        """
        RefreshWrite缓冲区（带retry mechanism）
        
        Args:
            max_retries: MaxRetry次数（DefaultUsageClassConstant）
            
        Returns:
            YesNoSuccessRefresh
        """
        max_retries = max_retries or self.MAX_RETRY_ATTEMPTS
        
        async with self._buffer_lock:
            if not self._write_buffer:
                return True
            
            buffer = self._write_buffer.copy()
            self._write_buffer.clear()
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                async with self._get_connection() as conn:
                    for item_type, data in buffer:
                        if item_type == "checkpoint":
                            await conn.execute(
                                """INSERT INTO checkpoints 
                                   (task_id, iteration, state_json, screenshot_id, is_full, created_at) 
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                data
                            )
                        elif item_type == "message":
                            await conn.execute(
                                """INSERT INTO messages (task_id, role, content, timestamp)
                                   VALUES (?, ?, ?, ?)""",
                                data
                            )
                    await conn.commit()
                    return True
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Flush attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    # pointernumberbackoff
                    delay = self.RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(delay)
        
        # allRetryallFailed，toDataput backBufferarea
        async with self._buffer_lock:
            self._write_buffer = buffer + self._write_buffer
            
        logger.error(f"Flush failed after {max_retries} attempts: {last_error}")
        return False
    
    async def _periodic_flush(self):
        """定期Refresh缓冲区（每 5 Second，带Retry和背压控制）"""
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while True:
            # DynamicResizeinterval：Failedtimeincreaseaddinterval
            interval = 5 * (1 + consecutive_failures)
            await asyncio.sleep(min(interval, 30))  # Max 30 Second
            
            try:
                success = await self._flush_buffer()
                
                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(
                            f"Periodic flush failed {consecutive_failures} times consecutively. "
                            f"Buffer size: {len(self._write_buffer)}"
                        )
                        # notMediumbreak，continuetry
                        
            except asyncio.CancelledError:
                # normalCancel，trymostAfteronceRefresh
                logger.info("Periodic flush cancelled, attempting final flush...")
                await self._flush_buffer(max_retries=1)
                raise
                
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Unexpected error in periodic flush: {e}")
    
    async def close(self):
        """CloseConnect池"""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # RefreshremainingData
        await self._flush_buffer()
        
        # CloseConnect
        async with self._pool_lock:
            for conn in self._pool:
                await conn.close()
            self._pool.clear()
        
        self._initialized = False
        logger.info("AsyncTaskStore closed")


# ========== SingletonPattern ==========

_default_store: Optional[AsyncTaskStore] = None


async def get_task_store() -> AsyncTaskStore:
    """GetDefault任务存储（Singleton）"""
    global _default_store
    if _default_store is None:
        _default_store = AsyncTaskStore()
        await _default_store.initialize()
    return _default_store


def set_task_store(store: AsyncTaskStore):
    """SetDefault任务存储（用于Test）"""
    global _default_store
    _default_store = store
