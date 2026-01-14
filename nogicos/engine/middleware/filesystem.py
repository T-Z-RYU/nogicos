# -*- coding: utf-8 -*-
"""
Filesystem Middleware - Deep Agents pattern for file management

Reference: Deep Agents FilesystemMiddleware
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ..tools.base import ToolRegistry, ToolCategory, get_registry

logger = logging.getLogger(__name__)


@dataclass
class VirtualFile:
    """A virtual file stored in agent state"""
    path: str
    content: str
    is_persisted: bool = False


class FilesystemBackend:
    """
    Backend for filesystem operations.
    Can be in-memory (virtual) or persistent (real disk).
    """
    
    def __init__(self, root_dir: Optional[str] = None, persist: bool = False):
        """
        Args:
            root_dir: Root directory for file operations. If None, uses current directory.
            persist: Whether to persist files to disk.
        """
        self.root_dir = root_dir or os.getcwd()
        self.persist = persist
        self._virtual_files: Dict[str, VirtualFile] = {}
    
    def _resolve_path(self, path: str) -> str:
        """Resolve path relative to root_dir"""
        if os.path.isabs(path):
            return path
        return os.path.join(self.root_dir, path)
    
    async def read(self, path: str) -> str:
        """Read a file"""
        # Check virtual files first
        if path in self._virtual_files:
            return self._virtual_files[path].content
        
        # Read from disk
        full_path = self._resolve_path(path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        
        raise FileNotFoundError(f"File not found: {path}")
    
    async def write(self, path: str, content: str) -> None:
        """Write a file"""
        # Store in virtual files
        self._virtual_files[path] = VirtualFile(
            path=path,
            content=content,
            is_persisted=False
        )
        
        # Persist to disk if enabled
        if self.persist:
            await self.persist_file(path)
    
    async def persist_file(self, path: str) -> None:
        """Persist a virtual file to disk"""
        if path not in self._virtual_files:
            return
        
        vfile = self._virtual_files[path]
        full_path = self._resolve_path(path)
        
        # Create parent directories
        parent = os.path.dirname(full_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(vfile.content)
        
        vfile.is_persisted = True
        logger.info(f"Persisted file: {path}")
    
    async def persist_all(self) -> List[str]:
        """Persist all virtual files to disk"""
        persisted = []
        for path in self._virtual_files:
            await self.persist_file(path)
            persisted.append(path)
        return persisted
    
    async def list_virtual(self) -> List[str]:
        """List all virtual files"""
        return list(self._virtual_files.keys())
    
    async def exists(self, path: str) -> bool:
        """Check if file exists (virtual or on disk)"""
        if path in self._virtual_files:
            return True
        full_path = self._resolve_path(path)
        return os.path.exists(full_path)
    
    def get_state(self) -> Dict[str, str]:
        """Get current virtual filesystem state"""
        return {path: vf.content for path, vf in self._virtual_files.items()}
    
    def load_state(self, state: Dict[str, str]) -> None:
        """Load virtual filesystem state"""
        for path, content in state.items():
            self._virtual_files[path] = VirtualFile(path=path, content=content)


class FilesystemMiddleware:
    """
    Middleware that provides filesystem tools to the agent.
    
    Follows Deep Agents pattern:
    - Automatic tool injection
    - Virtual filesystem for context management
    - Optional persistence to disk
    """
    
    SYSTEM_PROMPT_ADDITION = """
You have access to a virtual filesystem for managing context and storing results.
When you need to save large amounts of data or create files, use the filesystem tools.
Files can be persisted to disk when explicitly requested.
"""
    
    def __init__(
        self,
        backend: Optional[FilesystemBackend] = None,
        registry: Optional[ToolRegistry] = None,
        auto_persist: bool = False
    ):
        """
        Args:
            backend: Filesystem backend to use
            registry: Tool registry to register tools in
            auto_persist: Whether to auto-persist files
        """
        self.backend = backend or FilesystemBackend()
        self.registry = registry or get_registry()
        self.auto_persist = auto_persist
        
        # Register filesystem tools
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register filesystem-specific tools"""
        
        @self.registry.action(
            description="Read a file from the virtual filesystem or disk.",
            category=ToolCategory.LOCAL
        )
        async def fs_read(path: str) -> str:
            """Read file via middleware"""
            try:
                content = await self.backend.read(path)
                return content
            except Exception as e:
                return f"Error reading file: {str(e)}"
        
        @self.registry.action(
            description="Write content to a file in the virtual filesystem.",
            category=ToolCategory.LOCAL
        )
        async def fs_write(path: str, content: str) -> str:
            """Write file via middleware"""
            try:
                await self.backend.write(path, content)
                if self.auto_persist:
                    await self.backend.persist_file(path)
                    return f"Wrote and persisted: {path}"
                return f"Wrote to virtual file: {path}"
            except Exception as e:
                return f"Error writing file: {str(e)}"
        
        @self.registry.action(
            description="List all virtual files created during this session.",
            category=ToolCategory.LOCAL
        )
        async def fs_list_virtual() -> str:
            """List virtual files"""
            try:
                files = await self.backend.list_virtual()
                if not files:
                    return "No virtual files created yet."
                return "Virtual files:\n" + "\n".join(f"- {f}" for f in files)
            except Exception as e:
                return f"Error listing files: {str(e)}"
        
        @self.registry.action(
            description="Persist all virtual files to disk.",
            category=ToolCategory.LOCAL
        )
        async def fs_persist_all() -> str:
            """Persist all virtual files"""
            try:
                persisted = await self.backend.persist_all()
                if not persisted:
                    return "No files to persist."
                return f"Persisted {len(persisted)} files:\n" + "\n".join(f"- {f}" for f in persisted)
            except Exception as e:
                return f"Error persisting files: {str(e)}"
        
        logger.info("FilesystemMiddleware tools registered")
    
    def get_state(self) -> Dict[str, str]:
        """Get current filesystem state for serialization"""
        return self.backend.get_state()
    
    def load_state(self, state: Dict[str, str]) -> None:
        """Load filesystem state"""
        self.backend.load_state(state)
    
    def get_system_prompt_addition(self) -> str:
        """Get additional system prompt for filesystem context"""
        return self.SYSTEM_PROMPT_ADDITION


