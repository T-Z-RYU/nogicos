"""
NogicOS 截GraphInner存管理
====================

防止截Graph导致的Inner存泄漏。

Policy:
1. 压缩存储 (JPEG 85%)
2. LRU 淘汰
3. Inner存Up限控制
4. DelayedConvert base64

参考:
- Anthropic Computer Use 截GraphHandle
- ByteBot UpDown文压缩
"""

import base64
import uuid
import asyncio
import logging
import time
from io import BytesIO
from typing import Dict, Optional
from collections import OrderedDict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScreenshotEntry:
    """截Graph条目"""
    id: str
    data: bytes           # CompressAfter's GraphpieceData
    size: int             # byteSize
    timestamp: float      # CreateTime
    hwnd: int             # fromSourceWindow
    width: int = 0        # GraphpieceWidth
    height: int = 0       # GraphpieceHeight


class ScreenshotManager:
    """
    截Graph管理器 - Inner存Security的截Graph存储
    
    特性:
    - 压缩存储，减少 50-70% Inner存
    - LRU 淘汰Policy
    - Inner存Up限控制
    - 按需Convert base64
    
    UsageExample:
    ```python
    manager = get_screenshot_manager()
    
    # StoragecaptureGraph
    screenshot_id = await manager.store(image_bytes, hwnd=12345)
    
    # Get base64（byneedConvert）
    base64_data = await manager.get_base64(screenshot_id)
    
    # CheckInnerstoreUsage
    stats = manager.get_stats()
    print(f"Memory usage: {stats['total_size_mb']:.2f} MB")
    ```
    """
    
    # DefaultConfig
    MAX_MEMORY_MB = 50
    MAX_ENTRIES = 100
    JPEG_QUALITY = 85
    
    def __init__(self, max_memory_mb: int = None, max_entries: int = None):
        """
        Initialize截Graph管理器
        
        Args:
            max_memory_mb: MaxInner存Usage (MB)
            max_entries: Max截GraphCount
        """
        self.max_memory_bytes = (max_memory_mb or self.MAX_MEMORY_MB) * 1024 * 1024
        self.max_entries = max_entries or self.MAX_ENTRIES
        
        self._cache: OrderedDict[str, ScreenshotEntry] = OrderedDict()
        self._total_size = 0
        self._lock = asyncio.Lock()
        
        # Statistics
        self._store_count = 0
        self._evict_count = 0
    
    async def store(
        self, 
        image_data: bytes, 
        hwnd: int = 0,
        compress: bool = True,
    ) -> str:
        """
        存储截Graph
        
        Args:
            image_data: OriginalGraph片数据 (PNG/BMP/JPEG)
            hwnd: 来SourceWindow句柄
            compress: YesNo压缩 (Default True)
            
        Returns:
            截Graph ID
        """
        # CompressGraphpiece
        if compress:
            compressed, width, height = await self._compress(image_data)
        else:
            compressed = image_data
            width, height = 0, 0
        
        screenshot_id = str(uuid.uuid4())[:8]
        entry = ScreenshotEntry(
            id=screenshot_id,
            data=compressed,
            size=len(compressed),
            timestamp=time.time(),
            hwnd=hwnd,
            width=width,
            height=height,
        )
        
        async with self._lock:
            # AddtoCache
            self._cache[screenshot_id] = entry
            self._total_size += entry.size
            
            # MovetoLastTail (LRU)
            self._cache.move_to_end(screenshot_id)
            
            # Checkandeliminate
            await self._evict_if_needed()
            
            self._store_count += 1
        
        logger.debug(f"Screenshot stored: {screenshot_id} ({entry.size / 1024:.1f} KB)")
        return screenshot_id
    
    async def get_base64(self, screenshot_id: str) -> Optional[str]:
        """
        Get base64 编码的截Graph
        
        按需Convert，避免预先OccupyInner存
        
        Args:
            screenshot_id: 截Graph ID
            
        Returns:
            base64 编码的Character串，或 None
        """
        async with self._lock:
            entry = self._cache.get(screenshot_id)
            if not entry:
                return None
            
            # Update LRU Order
            self._cache.move_to_end(screenshot_id)
        
        return base64.b64encode(entry.data).decode('utf-8')
    
    async def get_raw(self, screenshot_id: str) -> Optional[bytes]:
        """GetOriginal压缩数据"""
        async with self._lock:
            entry = self._cache.get(screenshot_id)
            if entry:
                self._cache.move_to_end(screenshot_id)
                return entry.data
        return None
    
    async def get_entry(self, screenshot_id: str) -> Optional[ScreenshotEntry]:
        """Get完整的截Graph条目"""
        async with self._lock:
            entry = self._cache.get(screenshot_id)
            if entry:
                self._cache.move_to_end(screenshot_id)
                return entry
        return None
    
    async def delete(self, screenshot_id: str) -> bool:
        """Delete截Graph"""
        async with self._lock:
            entry = self._cache.pop(screenshot_id, None)
            if entry:
                self._total_size -= entry.size
                logger.debug(f"Screenshot deleted: {screenshot_id}")
                return True
        return False
    
    async def delete_by_hwnd(self, hwnd: int) -> int:
        """DeleteSpecifyWindow的所有截Graph"""
        async with self._lock:
            to_delete = [
                sid for sid, entry in self._cache.items()
                if entry.hwnd == hwnd
            ]
            
            for sid in to_delete:
                entry = self._cache.pop(sid)
                self._total_size -= entry.size
            
            return len(to_delete)
    
    async def _compress(self, image_data: bytes) -> tuple[bytes, int, int]:
        """
        压缩Graph片为 JPEG
        
        Returns:
            (compressed_data, width, height)
        """
        try:
            from PIL import Image
        except ImportError:
            logger.warning("PIL not installed, skipping compression")
            return image_data, 0, 0
        
        loop = asyncio.get_event_loop()
        
        def _do_compress():
            img = Image.open(BytesIO(image_data))
            width, height = img.size
            
            # Convertfor RGB (JPEG Not Support RGBA)
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Compressfor JPEG
            output = BytesIO()
            img.save(output, format='JPEG', quality=self.JPEG_QUALITY, optimize=True)
            return output.getvalue(), width, height
        
        return await loop.run_in_executor(None, _do_compress)
    
    async def _evict_if_needed(self):
        """淘汰过期条目"""
        evicted = 0
        
        # byCounteliminate
        while len(self._cache) > self.max_entries:
            oldest_id, oldest_entry = self._cache.popitem(last=False)
            self._total_size -= oldest_entry.size
            evicted += 1
        
        # byInnerstoreeliminate
        while self._total_size > self.max_memory_bytes and self._cache:
            oldest_id, oldest_entry = self._cache.popitem(last=False)
            self._total_size -= oldest_entry.size
            evicted += 1
        
        if evicted > 0:
            self._evict_count += evicted
            logger.debug(f"Evicted {evicted} screenshots")
    
    def get_stats(self) -> dict:
        """GetStatisticsInfo"""
        return {
            "count": len(self._cache),
            "total_size_mb": self._total_size / (1024 * 1024),
            "max_size_mb": self.max_memory_bytes / (1024 * 1024),
            "usage_percent": (self._total_size / self.max_memory_bytes * 100) if self.max_memory_bytes > 0 else 0,
            "store_count": self._store_count,
            "evict_count": self._evict_count,
        }
    
    async def clear(self):
        """清Empty所有截Graph"""
        async with self._lock:
            self._cache.clear()
            self._total_size = 0
            logger.info("Screenshot cache cleared")
    
    def get_recent(self, count: int = 5) -> list[str]:
        """Get最近的截Graph ID List"""
        return list(self._cache.keys())[-count:]


# ========== SingletonPattern ==========

_screenshot_manager: Optional[ScreenshotManager] = None


def get_screenshot_manager() -> ScreenshotManager:
    """GetGlobal截Graph管理器（Singleton）"""
    global _screenshot_manager
    if _screenshot_manager is None:
        _screenshot_manager = ScreenshotManager()
    return _screenshot_manager


def set_screenshot_manager(manager: ScreenshotManager):
    """SetGlobal截Graph管理器（用于Test）"""
    global _screenshot_manager
    _screenshot_manager = manager
