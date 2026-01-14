# -*- coding: utf-8 -*-
"""
Workspace Information Collector

Collects workspace structure and metadata for context injection.
Similar to Cursor's <project_layout> injection.
"""

import os
from pathlib import Path
from typing import Optional, List, Set
from dataclasses import dataclass, field


# Directories to always skip (common in projects)
SKIP_DIRS = {
    "__pycache__",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    ".env",
    "dist",
    "build",
    ".next",
    ".cache",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    "egg-info",
}

# File patterns to skip
SKIP_PATTERNS = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".lock",
}


@dataclass
class WorkspaceInfo:
    """Information about a workspace directory"""
    path: str
    name: str
    files: List[str] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    total_files: int = 0
    total_dirs: int = 0
    
    def to_tree(self, max_depth: int = 2, max_items: int = 50) -> str:
        """Convert to tree-like string representation"""
        lines = [f"{self.name}/"]
        
        # Add directories
        for i, d in enumerate(self.directories[:max_items // 2]):
            prefix = "├── " if i < len(self.directories) - 1 or self.files else "└── "
            lines.append(f"{prefix}{d}/")
        
        if len(self.directories) > max_items // 2:
            lines.append(f"├── ... ({len(self.directories) - max_items // 2} more directories)")
        
        # Add files
        for i, f in enumerate(self.files[:max_items // 2]):
            prefix = "├── " if i < len(self.files) - 1 else "└── "
            lines.append(f"{prefix}{f}")
        
        if len(self.files) > max_items // 2:
            lines.append(f"└── ... ({len(self.files) - max_items // 2} more files)")
        
        return "\n".join(lines)


def get_workspace_layout(
    workspace_path: str,
    max_depth: int = 2,
    max_items_per_level: int = 20,
) -> str:
    """
    Get a tree-like layout of the workspace directory.
    
    Similar to Cursor's <project_layout> section.
    
    Args:
        workspace_path: Root directory to scan
        max_depth: Maximum depth to traverse
        max_items_per_level: Maximum items to show per directory level
        
    Returns:
        Tree-like string representation of workspace
    """
    if not os.path.isdir(workspace_path):
        return f"Workspace not found: {workspace_path}"
    
    root = Path(workspace_path)
    root_name = root.name or str(root)
    
    lines = [f"{root_name}/"]
    
    def scan_dir(path: Path, depth: int, prefix: str = "") -> None:
        """Recursively scan directory"""
        if depth > max_depth:
            return
        
        try:
            items = sorted(path.iterdir())
        except PermissionError:
            return
        
        # Separate dirs and files
        dirs = []
        files = []
        
        for item in items:
            name = item.name
            
            # Skip hidden and known skip dirs
            if name.startswith(".") or name in SKIP_DIRS:
                continue
            
            # Skip by pattern
            if any(name.endswith(p) for p in SKIP_PATTERNS):
                continue
            
            if item.is_dir():
                dirs.append(item)
            else:
                files.append(item)
        
        # Limit items
        total_items = len(dirs) + len(files)
        show_dirs = dirs[:max_items_per_level // 2]
        show_files = files[:max_items_per_level // 2]
        
        all_items = show_dirs + show_files
        
        for i, item in enumerate(all_items):
            is_last = i == len(all_items) - 1
            connector = "└── " if is_last else "├── "
            
            if item.is_dir():
                lines.append(f"{prefix}{connector}{item.name}/")
                
                # Recurse into subdirs
                if depth < max_depth:
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    scan_dir(item, depth + 1, new_prefix)
            else:
                lines.append(f"{prefix}{connector}{item.name}")
        
        # Show "more" indicators
        hidden = total_items - len(all_items)
        if hidden > 0:
            lines.append(f"{prefix}    ... ({hidden} more items)")
    
    scan_dir(root, 1)
    
    return "\n".join(lines)


def get_important_files(workspace_path: str) -> List[str]:
    """
    Get list of important project files (configs, READMEs, etc.)
    
    Args:
        workspace_path: Root directory to scan
        
    Returns:
        List of important file paths relative to workspace
    """
    important_patterns = [
        "README.md",
        "README.txt",
        "package.json",
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "Cargo.toml",
        "go.mod",
        "Makefile",
        "docker-compose.yml",
        "Dockerfile",
        ".env.example",
    ]
    
    root = Path(workspace_path)
    found = []
    
    for pattern in important_patterns:
        # Check root
        if (root / pattern).exists():
            found.append(pattern)
        
        # Check one level deep for monorepos
        for subdir in root.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("."):
                if (subdir / pattern).exists():
                    found.append(f"{subdir.name}/{pattern}")
    
    return found[:10]  # Limit to 10 most important








