# -*- coding: utf-8 -*-
"""
File Hook - FileSystem感知

ListenFile变化、剪贴板Inner容、最近File
"""

import asyncio
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .base_hook import BaseHook, HookConfig
from ..store import HookType, FileContext

logger = logging.getLogger(__name__)

# OptionalDependency
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object  # Fallback base class
    FileModifiedEvent = None
    FileCreatedEvent = None
    logger.debug("[FileHook] watchdog not available, file watching disabled")


class FileChangeHandler(FileSystemEventHandler):
    """File变化Handle器"""
    
    def __init__(self, callback):
        self.callback = callback
        self._recent_events: Set[str] = set()
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path, "modified")
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path, "created")
    
    def _handle_event(self, path: str, event_type: str):
        # Dedupe（sameFileShortTimeInnermultipletimeTrigger）
        key = f"{path}:{event_type}"
        if key not in self._recent_events:
            self._recent_events.add(key)
            self.callback(path, event_type)
            
            # 5SecondAfterClear
            asyncio.get_event_loop().call_later(
                5.0,
                lambda: self._recent_events.discard(key)
            )


class FileHook(BaseHook):
    """
    File Hook
    
    ListenFile变化、剪贴板、最近File
    """
    
    # Ignore's FileExtendname
    IGNORED_EXTENSIONS = {
        ".pyc", ".pyo", ".log", ".tmp", ".temp",
        ".swp", ".swo", ".bak", ".cache",
        ".git", ".svn", ".hg",
    }
    
    # Ignore's Directoryname
    IGNORED_DIRS = {
        "__pycache__", "node_modules", ".git", ".svn",
        ".idea", ".vscode", "venv", ".venv",
        "dist", "build", ".next", ".nuxt",
    }
    
    def __init__(
        self,
        hook_id: str = "file",
        config: Optional[HookConfig] = None,
    ):
        super().__init__(hook_id, HookType.FILE, config)
        
        self._watched_dirs: List[str] = []
        self._observer: Optional[Any] = None  # watchdog Observer
        self._recent_files: List[str] = []
        self._max_recent_files = 20
        self._last_clipboard = ""
        self._last_context: Optional[FileContext] = None
    
    async def _connect(self, target: Optional[str] = None) -> bool:
        """
        Connect到Directory
        
        Args:
            target: 要Listen的DirectoryPath，多个Directory用分号分隔
        """
        if not target:
            # DefaultListenUserdesktop
            target = str(Path.home() / "Desktop")
        
        # ParsemultipleaDirectory
        dirs = [d.strip() for d in target.split(";") if d.strip()]
        
        # VerifyDirectorystorein
        valid_dirs = []
        for d in dirs:
            if os.path.isdir(d):
                valid_dirs.append(d)
            else:
                logger.warning(f"[FileHook] Directory not found: {d}")
        
        if not valid_dirs:
            logger.error("[FileHook] No valid directories to watch")
            return False
        
        self._watched_dirs = valid_dirs
        
        # StartFileListen
        if WATCHDOG_AVAILABLE:
            try:
                self._observer = Observer()
                handler = FileChangeHandler(self._on_file_change)
                
                for dir_path in valid_dirs:
                    self._observer.schedule(handler, dir_path, recursive=True)
                    logger.info(f"[FileHook] Watching: {dir_path}")
                
                self._observer.start()
            except Exception as e:
                logger.error(f"[FileHook] Failed to start file watcher: {e}")
        
        return True
    
    async def _disconnect(self) -> bool:
        """DisconnectConnect"""
        if self._observer:
            try:
                self._observer.stop()
                self._observer.join(timeout=2.0)
            except Exception as e:
                logger.error(f"[FileHook] Failed to stop observer: {e}")
            self._observer = None
        
        self._watched_dirs = []
        self._recent_files = []
        self._last_context = None
        return True
    
    async def capture(self) -> Optional[FileContext]:
        """
        捕获FileUpDown文
        
        Returns:
            FileContext 或 None
        """
        try:
            # GetclipboardInnercontent
            clipboard = await self._get_clipboard()
            
            context = FileContext(
                watched_dirs=self._watched_dirs,
                recent_files=self._recent_files.copy(),
                clipboard=clipboard,
                last_updated=datetime.now().isoformat(),
            )
            
            self._last_context = context
            return context
            
        except Exception as e:
            logger.error(f"[FileHook] Capture failed: {e}")
            return self._last_context
    
    def _on_file_change(self, path: str, event_type: str):
        """File变化Callback"""
        # FilterIgnore's File
        if self._should_ignore(path):
            return
        
        # AddtomostnearFileList
        if path in self._recent_files:
            self._recent_files.remove(path)
        self._recent_files.insert(0, path)
        
        # LimitListLength
        if len(self._recent_files) > self._max_recent_files:
            self._recent_files = self._recent_files[:self._max_recent_files]
        
        logger.debug(f"[FileHook] File {event_type}: {path}")
    
    def _should_ignore(self, path: str) -> bool:
        """JudgeYesNo应该Ignore该File"""
        # CheckExtendname
        ext = Path(path).suffix.lower()
        if ext in self.IGNORED_EXTENSIONS:
            return True
        
        # CheckDirectory
        parts = Path(path).parts
        for part in parts:
            if part in self.IGNORED_DIRS:
                return True
        
        return False
    
    async def _get_clipboard(self) -> str:
        """Get剪贴板Inner容"""
        try:
            if sys.platform == "win32":
                return await self._get_clipboard_windows()
            else:
                return ""
        except Exception as e:
            logger.debug(f"[FileHook] Get clipboard failed: {e}")
            return ""
    
    async def _get_clipboard_windows(self) -> str:
        """Windows Get剪贴板"""
        try:
            import ctypes
            
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            
            CF_UNICODETEXT = 13
            
            if not user32.OpenClipboard(0):
                return self._last_clipboard
            
            try:
                if not user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                    return self._last_clipboard
                
                handle = user32.GetClipboardData(CF_UNICODETEXT)
                if not handle:
                    return self._last_clipboard
                
                kernel32.GlobalLock.restype = ctypes.c_wchar_p
                text = kernel32.GlobalLock(handle)
                
                if text:
                    result = str(text)
                    kernel32.GlobalUnlock(handle)
                    self._last_clipboard = result
                    return result
                
            finally:
                user32.CloseClipboard()
            
            return self._last_clipboard
            
        except Exception as e:
            logger.debug(f"[FileHook] Windows clipboard error: {e}")
            return self._last_clipboard
    
    def add_watched_dir(self, dir_path: str) -> bool:
        """AddListenDirectory"""
        if not os.path.isdir(dir_path):
            return False
        
        if dir_path in self._watched_dirs:
            return True
        
        self._watched_dirs.append(dir_path)
        
        if WATCHDOG_AVAILABLE and self._observer:
            try:
                handler = FileChangeHandler(self._on_file_change)
                self._observer.schedule(handler, dir_path, recursive=True)
                logger.info(f"[FileHook] Added watch: {dir_path}")
                return True
            except Exception as e:
                logger.error(f"[FileHook] Failed to add watch: {e}")
                return False
        
        return True
    
    def get_recent_files(self, limit: int = 10) -> List[str]:
        """Get最近FileList"""
        return self._recent_files[:limit]

