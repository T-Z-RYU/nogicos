# -*- coding: utf-8 -*-
"""
Local Tools - File system and shell tools for NogicOS Agent

Reference: open-interpreter/interpreter/core/computer/files/files.py
           open-interpreter/interpreter/core/computer/terminal/terminal.py
"""

import os
import glob as glob_module
import subprocess
import asyncio
import logging
import re
from typing import Optional, List
from pathlib import Path

from .base import ToolRegistry, ToolCategory, get_registry
from .descriptions import (
    APPEND_FILE, GET_CWD, PATH_EXISTS, COPY_FILE
)

logger = logging.getLogger(__name__)

# Security: Define allowed directories for file operations
ALLOWED_ROOTS = [
    os.path.expanduser("~"),  # User home
    os.getcwd(),  # Current working directory
]

# Security: Sensitive directories that should be excluded from operations
SENSITIVE_PATTERNS = [
    ".ssh",           # SSH keys and config
    ".gnupg",         # GPG keys
    ".env",           # Environment files
    ".aws",           # AWS credentials
    ".azure",         # Azure credentials
    ".gcp",           # GCP credentials
    ".kube",          # Kubernetes config
    ".docker",        # Docker config
    "credentials",    # Generic credentials
    "secrets",        # Generic secrets
    ".netrc",         # Network credentials
    ".npmrc",         # NPM auth tokens
    ".pypirc",        # PyPI auth tokens
]


def _is_sensitive_path(path: str) -> bool:
    """Check if path contains sensitive directories"""
    abs_path = os.path.realpath(path).lower()
    path_parts = abs_path.replace("\\", "/").split("/")
    for pattern in SENSITIVE_PATTERNS:
        if pattern.lower() in path_parts:
            return True
    return False

# Protected directories that should NOT be modified by file organization tasks
PROTECTED_PATTERNS = [
    "Cursor Project",  # User's main code project
    ".git",            # Git repositories
    "node_modules",    # Node.js dependencies
    "__pycache__",     # Python cache
    ".venv", "venv",   # Python virtual environments
    ".cursor",         # Cursor IDE settings
]

# Code file extensions that indicate a directory is a code project
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
    ".java", ".cpp", ".c", ".h", ".hpp", ".go", ".rs", ".rb",
    ".php", ".swift", ".kt", ".scala", ".vue", ".svelte",
}


def _is_path_allowed(path: str) -> bool:
    """Check if path is within allowed directories and not sensitive"""
    # [P1 FIX] Enhanced symlink check - detect TOCTOU race conditions
    try:
        # Get normalized path (but don't resolve symlinks yet)
        normalized_path = os.path.normpath(os.path.abspath(path))

        # Security: Reject symbolic links to prevent symlink attacks
        if os.path.islink(path):
            return False

        # Security: Also check if any parent directory is a symlink
        # Check from the path itself up to root
        current = normalized_path
        checked_paths = set()  # Prevent infinite loops from circular symlinks
        for _ in range(100):  # Prevent infinite loops
            if current in checked_paths:
                return False  # Circular reference detected
            checked_paths.add(current)

            parent = os.path.dirname(current)
            if parent == current:
                break
            # Check if parent exists and is a symlink
            if os.path.exists(parent) and os.path.islink(parent):
                return False
            current = parent

        # Now resolve the actual path (follows symlinks)
        abs_path = os.path.realpath(path)

        # [P1 FIX] Windows multi-drive security - ensure path stays on allowed drives
        # Extract drive letter for Windows
        if os.name == 'nt':
            path_drive = os.path.splitdrive(abs_path)[0].upper()
            allowed_drives = set()
            for root in ALLOWED_ROOTS:
                root_drive = os.path.splitdrive(root)[0].upper()
                if root_drive:
                    allowed_drives.add(root_drive)
            # If we have allowed drives and path drive doesn't match
            if allowed_drives and path_drive not in allowed_drives:
                return False

        # [P1 FIX] Use commonpath for secure path prefix checking
        in_allowed_root = False
        for root in ALLOWED_ROOTS:
            try:
                root_abs = os.path.realpath(root)
                # Use commonpath to prevent path traversal
                common = os.path.commonpath([abs_path, root_abs])
                if common == root_abs:
                    in_allowed_root = True
                    break
            except ValueError:
                # commonpath raises ValueError if paths are on different drives
                continue

        if not in_allowed_root:
            return False

        # Check if path is sensitive
        if _is_sensitive_path(abs_path):
            return False
        return True

    except (OSError, ValueError):
        # Any path resolution error should fail closed
        return False


def _is_protected_path(path: str) -> tuple[bool, str]:
    """
    Check if path is a protected code directory that should not be modified.
    
    Returns:
        (is_protected, reason)
    """
    abs_path = os.path.abspath(path)
    path_lower = abs_path.lower()
    
    # Check for protected patterns in path
    for pattern in PROTECTED_PATTERNS:
        if pattern.lower() in path_lower:
            return True, f"Path contains protected pattern: {pattern}"
    
    # Check if directory contains .git (it's a code repository)
    dir_to_check = abs_path if os.path.isdir(abs_path) else os.path.dirname(abs_path)
    if os.path.exists(os.path.join(dir_to_check, ".git")):
        return True, "This is a git repository (code project)"
    
    # Check parent directories for .git
    current = dir_to_check
    for _ in range(5):  # Check up to 5 levels up
        parent = os.path.dirname(current)
        if parent == current:  # Reached root
            break
        if os.path.exists(os.path.join(parent, ".git")):
            return True, "This path is inside a git repository (code project)"
        current = parent
    
    return False, ""


def _check_file_safety(path: str, operation: str) -> tuple[bool, str]:
    """
    Check if a file operation is safe to perform.
    
    Args:
        path: Path to check
        operation: Operation type (move, delete, write)
        
    Returns:
        (is_safe, error_message)
    """
    # Check basic permission
    if not _is_path_allowed(path):
        return False, f"Access denied to path: {path}"
    
    # Check for protected directories
    is_protected, reason = _is_protected_path(path)
    if is_protected:
        return False, f"PROTECTED: {reason}. This path should not be modified by file organization tasks."
    
    # Check file extension for code files
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in CODE_EXTENSIONS:
            return False, f"PROTECTED: This is a code file ({ext}). Code files should not be modified by file organization tasks."
    
    return True, ""


def register_local_tools(registry: Optional[ToolRegistry] = None) -> ToolRegistry:
    """
    Register all local system tools to the registry.
    
    Args:
        registry: Optional registry to use. If None, uses global registry.
        
    Returns:
        The registry with local tools registered.
    """
    if registry is None:
        registry = get_registry()
    
    @registry.action(
        description="""Read file content from local filesystem.

WHEN TO USE:
- Reading known file paths
- Viewing configuration, source code, or data files
- Checking file content before modification

WHEN NOT TO USE:
- Finding files by pattern → use glob_search
- Searching content across files → use grep_search
- Listing directory contents → use list_directory

Parameters:
- path: File path (relative/absolute, supports ~)
- limit: Max lines (0 = unlimited, default: 0)

Returns: File content (truncated if >50KB)""",
        category=ToolCategory.LOCAL
    )
    async def read_file(path: str, limit: int = 0) -> str:
        """Read file content"""
        try:
            if not _is_path_allowed(path):
                return f"Error: Access denied to path: {path}"
            
            if not os.path.exists(path):
                return f"Error: File not found: {path}"
            
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                if limit > 0:
                    lines = []
                    line_count = 0
                    for line_count, line in enumerate(f):
                        if line_count >= limit:
                            break
                        lines.append(line)
                    content = ''.join(lines)
                    if line_count >= limit:
                        content += f"\n... (showing first {limit} lines)"
                else:
                    content = f.read()
            
            # Limit output size
            max_size = 50000
            if len(content) > max_size:
                content = content[:max_size] + f"\n... (truncated, total {len(content)} chars)"
            
            return content
            
        except Exception as e:
            logger.error(f"Read file failed: {e}")
            return f"Error reading file: {str(e)}"
    
    @registry.action(
        description="""Write content to file (creates or overwrites).

WHEN TO USE:
- Creating new files
- Overwriting entire file content
- Saving generated code, config, or data

WHEN NOT TO USE:
- Partial text replacement → use search_replace
- Appending to file → use append_file
- Editing existing code → prefer search_replace

Parameters:
- path: Target file path
- content: Content to write

Note: Creates parent directories automatically. Overwrites existing files.""",
        category=ToolCategory.LOCAL
    )
    async def write_file(path: str, content: str) -> str:
        """Write content to file"""
        try:
            # Safety check for code files
            is_safe, error = _check_file_safety(path, "write")
            if not is_safe:
                return f"Error: {error}"
            
            # Create parent directories if needed
            parent = os.path.dirname(path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote {len(content)} characters to {path}"
            
        except Exception as e:
            logger.error(f"Write file failed: {e}")
            return f"Error writing file: {str(e)}"
    
    @registry.action(
        description=APPEND_FILE,
        category=ToolCategory.LOCAL
    )
    async def append_file(path: str, content: str) -> str:
        """Append content to file"""
        try:
            if not _is_path_allowed(path):
                return f"Error: Access denied to path: {path}"
            
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully appended {len(content)} characters to {path}"
            
        except Exception as e:
            logger.error(f"Append file failed: {e}")
            return f"Error appending to file: {str(e)}"
    
    @registry.action(
        description="""Execute shell command and return output.

WHEN TO USE:
- Installing packages (npm, pip, etc.)
- Running scripts or build commands
- Git operations
- System commands without dedicated tools

WHEN NOT TO USE:
- Listing directories → use list_directory
- Reading files → use read_file
- Searching files → use glob_search or grep_search

Parameters:
- command: Shell command to execute
- timeout: Max seconds (default: 30)

Returns: STDOUT, STDERR, exit code
Security: Enhanced command validation with whitelist approach""",
        category=ToolCategory.LOCAL
    )
    async def shell_execute(command: str, timeout: int = 30) -> str:
        """Execute shell command with enhanced security"""
        import shlex
        try:
            # [P0-1 FIX] Enhanced security: Multi-layer command validation

            # Layer 1: Normalize and detect encoding bypasses
            normalized_cmd = command.lower()
            # Detect hex/octal/base64 encoding attempts
            encoding_patterns = [
                r'\\x[0-9a-f]{2}',           # hex encoding
                r'\\[0-7]{3}',               # octal encoding
                r'\$\'\\x',                  # $'\x...' bash syntax
                r'base64\s+(-d|--decode)',   # base64 decode
                r'\$\{IFS\}',                # IFS variable bypass
            ]
            for pattern in encoding_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    logger.warning(f"[Security] Blocked encoding bypass attempt: {pattern}")
                    return "Error: Command blocked - encoding bypass detected"

            # Layer 2: Block dangerous command patterns (comprehensive)
            dangerous_patterns = [
                # Destructive file operations
                (r'\brm\s+(-[rfivd]+\s+)*[/*~]', "destructive rm"),
                (r'/bin/rm\b', "direct rm path"),
                (r'/usr/bin/rm\b', "direct rm path"),
                (r'\bdel\s+[/\\]', "Windows del"),
                (r'\brmdir\s+[/\\]', "rmdir system"),
                (r'\brd\s+/s', "Windows rd /s"),
                # Privilege escalation
                (r'\bsudo\b', "sudo"),
                (r'\bsu\s+(-|root)', "su"),
                (r'\bdoas\b', "doas"),
                (r'\brunas\b', "runas"),
                (r'\bpkexec\b', "pkexec"),
                # System control
                (r'\bshutdown\b', "shutdown"),
                (r'\breboot\b', "reboot"),
                (r'\bhalt\b', "halt"),
                (r'\bpoweroff\b', "poweroff"),
                (r'\binit\s+[06]', "init"),
                (r'\bsystemctl\s+(halt|poweroff|reboot)', "systemctl"),
                # Disk operations
                (r'\bmkfs\b', "mkfs"),
                (r'\bfdisk\b', "fdisk"),
                (r'\bformat\b', "format"),
                (r'\bdd\s+.*of=', "dd write"),
                (r'\bparted\b', "parted"),
                # Dangerous redirects
                (r'>\s*/dev/', "redirect to /dev"),
                (r'>\s*/etc/', "redirect to /etc"),
                (r'>\s*/boot/', "redirect to /boot"),
                (r'\bchmod\s+(777|a\+rwx)', "chmod 777"),
                (r'\bchown\s+root', "chown root"),
                # Network backdoors
                (r'\bnc\s+-[elpvn]*\s', "netcat"),
                (r'\bncat\b', "ncat"),
                (r'\bsocat\b', "socat"),
                (r'bash\s+-i\s*>&', "reverse shell"),
                (r'/dev/tcp/', "bash tcp"),
                (r'\bcurl\b.*\|\s*(ba)?sh', "curl to shell"),
                (r'\bwget\b.*\|\s*(ba)?sh', "wget to shell"),
                # Code injection
                (r'\beval\s+["\']', "eval"),
                (r'`[^`]+`', "backtick substitution"),
                (r'\$\([^)]+\)', "command substitution"),
            ]

            for pattern, reason in dangerous_patterns:
                if re.search(pattern, normalized_cmd, re.IGNORECASE):
                    logger.warning(f"[Security] Blocked dangerous command ({reason}): {command[:50]}...")
                    return f"Error: Command blocked for security reasons"

            # Layer 3: Validate command isn't targeting sensitive paths
            if _is_sensitive_path(command):
                return "Error: Command targets sensitive directory"

            # Layer 4: Parse command safely
            try:
                args = shlex.split(command)
                if not args:
                    return "Error: Empty command"
            except ValueError as e:
                logger.warning(f"[Security] Invalid command syntax: {e}")
                return f"Error: Invalid command syntax"

            # Layer 5: Determine execution mode
            # Prefer subprocess without shell when possible
            shell_chars = ['|', '&', ';', '>', '<', '$', '`', '(', ')', '{', '}', '*', '?']
            needs_shell = any(c in command for c in shell_chars)

            if needs_shell:
                # Additional validation for shell mode
                # Block command chaining unless to safe targets
                if re.search(r'[;&]', command):
                    # [P0-1 FIX Round 1] Only allow truly safe command chains
                    # REMOVED npm/pip/git - they can execute arbitrary code
                    # npm: npm exec, npm run-script can run arbitrary code
                    # pip: pip install -e can run setup.py
                    # git: git config core.hookspath can execute hooks
                    parts = re.split(r'[;&]', command)
                    for part in parts:
                        part = part.strip()
                        if part and not any(part.startswith(safe) for safe in
                            ['echo ', 'cd ', 'pwd', 'ls ', 'dir ', 'type ', 'cat ']):
                            logger.warning(f"[Security] Blocked unsafe command chain: {part[:30]}...")
                            return "Error: Unsafe command chain blocked"

                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=os.getcwd()
                )
            else:
                # [P0-1 FIX] Use subprocess without shell - safer
                process = await asyncio.create_subprocess_exec(
                    *args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=os.getcwd()
                )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"Error: Command timed out after {timeout} seconds"
            
            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace')
            
            result = []
            if output:
                result.append(f"STDOUT:\n{output}")
            if error:
                result.append(f"STDERR:\n{error}")
            result.append(f"Exit code: {process.returncode}")
            
            return '\n'.join(result)
            
        except Exception as e:
            logger.error(f"Shell execute failed: {e}")
            return f"Error executing command: {str(e)}"
    
    @registry.action(
        description="""Find files by name pattern (glob).

WHEN TO USE:
- Finding files by extension (*.py, *.tsx)
- Locating files by name pattern (test_*, config.*)
- Listing specific file types in a directory

WHEN NOT TO USE:
- Searching file content → use grep_search
- Semantic code search → use codebase_search
- Listing all directory contents → use list_directory

Parameters:
- pattern: Glob pattern (*, **, ?, [abc])
- root: Starting directory (default: current)

Returns: Matching file paths (max 100)""",
        category=ToolCategory.LOCAL
    )
    async def glob_search(pattern: str, root: str = ".") -> str:
        """Find files matching pattern"""
        try:
            if not _is_path_allowed(root):
                return f"Error: Access denied to path: {root}"
            
            # Use glob to find files
            search_path = os.path.join(root, pattern)
            matches = glob_module.glob(search_path, recursive=True)
            
            # Limit results
            max_results = 100
            if len(matches) > max_results:
                matches = matches[:max_results]
                truncated = True
            else:
                truncated = False
            
            if not matches:
                return f"No files found matching pattern: {pattern}"
            
            result = f"Found {len(matches)} files:\n"
            result += '\n'.join(matches)
            
            if truncated:
                result += f"\n... (showing first {max_results} results)"
            
            return result
            
        except Exception as e:
            logger.error(f"Glob search failed: {e}")
            return f"Error searching files: {str(e)}"
    
    @registry.action(
        description="""Search text/regex pattern in files (like grep/ripgrep).

WHEN TO USE:
- Finding exact text or regex matches in code
- Locating function/variable definitions
- Searching logs or data files for patterns

WHEN NOT TO USE:
- Finding files by name → use glob_search
- Semantic/meaning-based search → use codebase_search
- Reading known file → use read_file

Parameters:
- pattern: Text or regex pattern
- path: Search path (default: current directory)
- file_pattern: Filter by glob (default: *)

Returns: Matching lines as file:line:content (max 50)""",
        category=ToolCategory.LOCAL
    )
    async def grep_search(pattern: str, path: str = ".", file_pattern: str = "*") -> str:
        """Search for pattern in files"""
        try:
            if not _is_path_allowed(path):
                return f"Error: Access denied to path: {path}"
            
            results = []
            max_results = 50
            
            # Find files to search
            if os.path.isfile(path):
                files = [path]
            else:
                search_path = os.path.join(path, "**", file_pattern)
                files = glob_module.glob(search_path, recursive=True)
            
            regex = re.compile(pattern, re.IGNORECASE)
            
            for filepath in files:
                if not os.path.isfile(filepath):
                    continue
                    
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append(f"{filepath}:{line_num}: {line.strip()}")
                                if len(results) >= max_results:
                                    break
                except (IOError, OSError, UnicodeDecodeError, PermissionError):
                    continue
                
                if len(results) >= max_results:
                    break
            
            if not results:
                return f"No matches found for pattern: {pattern}"
            
            result = f"Found {len(results)} matches:\n"
            result += '\n'.join(results)
            
            if len(results) >= max_results:
                result += f"\n... (showing first {max_results} results)"
            
            return result
            
        except Exception as e:
            logger.error(f"Grep search failed: {e}")
            return f"Error searching: {str(e)}"
    
    @registry.action(
        description="""List directory contents.

WHEN TO USE:
- Exploring unfamiliar directories
- Checking what files exist before operations
- Getting overview of folder structure

WHEN NOT TO USE:
- Finding specific file types → use glob_search
- Reading file content → use read_file
- Searching inside files → use grep_search

Parameters:
- path: Directory path (default: current)

Returns: List with [DIR]/[FILE] markers and sizes
TIP: Use this first when unsure what files exist""",
        category=ToolCategory.LOCAL
    )
    async def list_directory(path: str = ".") -> str:
        """List directory contents"""
        try:
            if not _is_path_allowed(path):
                return f"Error: Access denied to path: {path}"
            
            if not os.path.exists(path):
                return f"Error: Path not found: {path}"
            
            if not os.path.isdir(path):
                return f"Error: Not a directory: {path}"
            
            entries = []
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    entries.append(f"[DIR]  {entry}/")
                else:
                    size = os.path.getsize(full_path)
                    entries.append(f"[FILE] {entry} ({size} bytes)")
            
            if not entries:
                return f"Directory is empty: {path}"
            
            return f"Contents of {path}:\n" + '\n'.join(sorted(entries))
            
        except Exception as e:
            logger.error(f"List directory failed: {e}")
            return f"Error listing directory: {str(e)}"
    
    @registry.action(
        description="""Create directory (with parent directories).

WHEN TO USE:
- Creating new folder structure
- Setting up project directories
- Preparing output locations

Note: Safe if directory already exists (no error).

Parameters:
- path: Directory path to create

Returns: Success message""",
        category=ToolCategory.LOCAL
    )
    async def create_directory(path: str) -> str:
        """Create directory"""
        try:
            if not _is_path_allowed(path):
                return f"Error: Access denied to path: {path}"
            
            os.makedirs(path, exist_ok=True)
            return f"Successfully created directory: {path}"
            
        except Exception as e:
            logger.error(f"Create directory failed: {e}")
            return f"Error creating directory: {str(e)}"
    
    @registry.action(
        description=GET_CWD,
        category=ToolCategory.LOCAL
    )
    async def get_cwd() -> str:
        """Get current working directory"""
        return os.getcwd()
    
    @registry.action(
        description="""Perform exact string replacement in files.

WHEN TO USE:
- Renaming variables/functions across files
- Fixing specific text patterns
- Precise code modifications
- Updating imports or references

WHEN NOT TO USE:
- Creating new files → use write_file
- Overwriting entire file → use write_file
- Complex regex transforms → use shell_execute with sed

Parameters:
- file_path: Target file
- old_string: Text to find (must be unique)
- new_string: Replacement text
- replace_all: Replace all occurrences (default: False)

Note: old_string must match exactly including whitespace.""",
        category=ToolCategory.LOCAL
    )
    async def search_replace(file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
        """Perform exact string replacement in file"""
        try:
            if not _is_path_allowed(file_path):
                return f"Error: Access denied to path: {file_path}"
            
            if not os.path.exists(file_path):
                return f"Error: File not found: {file_path}"
            
            if not os.path.isfile(file_path):
                return f"Error: Not a file: {file_path}"
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Check if old_string exists
            count = content.count(old_string)
            if count == 0:
                return f"Error: '{old_string[:50]}...' not found in {file_path}"
            
            # If not replace_all and multiple matches, warn
            if not replace_all and count > 1:
                return f"Error: Found {count} occurrences of '{old_string[:50]}...'. Use replace_all=True or provide more unique string."
            
            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
                replaced_count = count
            else:
                new_content = content.replace(old_string, new_string, 1)
                replaced_count = 1
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return f"Successfully replaced {replaced_count} occurrence(s) in {file_path}"
            
        except Exception as e:
            logger.error(f"Search replace failed: {e}")
            return f"Error performing replacement: {str(e)}"
    
    # ========================================
    # NEW: Essential file operations
    # ========================================
    
    @registry.action(
        description="""Move or rename file/directory.

WHEN TO USE:
- Renaming files or folders
- Moving files between directories
- Reorganizing project structure

WHEN NOT TO USE:
- Copying files → use copy_file
- Deleting files → use delete_file

Parameters:
- source: Path to move from
- destination: Target path

Note: Creates destination directory if needed.
PROTECTED: Won't move .git, code projects, system folders.""",
        category=ToolCategory.LOCAL
    )
    async def move_file(source: str, destination: str) -> str:
        """Move/rename file or directory"""
        import shutil
        try:
            # Safety check for source
            is_safe, error = _check_file_safety(source, "move")
            if not is_safe:
                return f"Error: {error}"
            
            # Safety check for destination
            is_safe, error = _check_file_safety(destination, "move")
            if not is_safe:
                return f"Error: {error}"
            
            if not os.path.exists(source):
                return f"Error: Source not found: {source}"
            
            # Create destination directory if needed
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(source, destination)
            return f"Successfully moved {source} to {destination}"
            
        except Exception as e:
            logger.error(f"Move file failed: {e}")
            return f"Error moving file: {str(e)}"
    
    @registry.action(
        description=COPY_FILE,
        category=ToolCategory.LOCAL
    )
    async def copy_file(source: str, destination: str) -> str:
        """Copy file or directory"""
        import shutil
        try:
            if not _is_path_allowed(source):
                return f"Error: Access denied to source path: {source}"
            if not _is_path_allowed(destination):
                return f"Error: Access denied to destination path: {destination}"
            
            if not os.path.exists(source):
                return f"Error: Source not found: {source}"
            
            # Create destination directory if needed
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(source, destination)
            
            return f"Successfully copied {source} to {destination}"
            
        except Exception as e:
            logger.error(f"Copy file failed: {e}")
            return f"Error copying file: {str(e)}"
    
    @registry.action(
        description="""Delete file or directory.

WHEN TO USE:
- Removing temporary files
- Cleaning up old directories
- Deleting generated outputs

WHEN NOT TO USE:
- Moving files → use move_file
- Archiving → use move_file to backup location

Parameters:
- path: File or directory to delete
- recursive: Delete non-empty directories (default: False)

PROTECTED: Won't delete .git, code projects, system files.""",
        category=ToolCategory.LOCAL
    )
    async def delete_file(path: str, recursive: bool = False) -> str:
        """Delete file or directory"""
        import shutil
        try:
            # Enhanced safety check
            is_safe, error = _check_file_safety(path, "delete")
            if not is_safe:
                return f"Error: {error}"
            
            if not os.path.exists(path):
                return f"Error: Path not found: {path}"
            
            # Additional safety check: don't delete important directories
            # Windows paths are case-insensitive, so normalize for comparison
            danger_paths = [
                os.path.expanduser("~"),
                "/",
                "/home",
                "/usr",
            ]
            # Windows-specific paths (case-insensitive)
            windows_danger_paths = [
                "c:\\",
                "c:\\windows",
                "c:\\program files",
                "c:\\program files (x86)",
                "c:\\users",
            ]
            abs_path = os.path.abspath(path)
            abs_path_lower = abs_path.lower()

            # Check exact matches for Unix paths
            if abs_path in danger_paths:
                return f"Error: Refusing to delete protected path: {path}"

            # Check case-insensitive matches for Windows paths
            if abs_path_lower in windows_danger_paths or abs_path_lower.rstrip("\\") in windows_danger_paths:
                return f"Error: Refusing to delete protected path: {path}"
            
            if os.path.isdir(path):
                if recursive:
                    shutil.rmtree(path)
                else:
                    os.rmdir(path)  # Only removes empty dirs
            else:
                os.remove(path)
            
            return f"Successfully deleted: {path}"
            
        except Exception as e:
            logger.error(f"Delete file failed: {e}")
            return f"Error deleting: {str(e)}"
    
    @registry.action(
        description=PATH_EXISTS,
        category=ToolCategory.LOCAL
    )
    async def path_exists(path: str) -> str:
        """Check if path exists"""
        try:
            if not _is_path_allowed(path):
                return f"Error: Access denied to path: {path}"
            
            exists = os.path.exists(path)
            is_file = os.path.isfile(path)
            is_dir = os.path.isdir(path)
            
            if exists:
                type_str = "file" if is_file else "directory" if is_dir else "unknown"
                size = os.path.getsize(path) if is_file else None
                return f"Exists: True, Type: {type_str}" + (f", Size: {size} bytes" if size else "")
            else:
                return f"Exists: False"
            
        except Exception as e:
            return f"Error checking path: {str(e)}"
    
    @registry.action(
        description="""Read linter errors for files.

WHEN TO USE:
- After editing code files
- Checking for syntax errors
- Validating code quality
- Before committing changes

WHEN NOT TO USE:
- Reading file content → use read_file
- Running tests → use shell_execute

Parameters:
- paths: File paths to lint (Python: pylint, JS: eslint)
- linter: Override linter (auto-detected by extension)

Returns: List of errors with line numbers and messages""",
        category=ToolCategory.LOCAL
    )
    async def read_lints(paths: List[str], linter: Optional[str] = None) -> str:
        """Read linter errors for specified files"""
        try:
            results = []
            
            for path in paths:
                if not _is_path_allowed(path):
                    results.append(f"Error: Access denied to {path}")
                    continue
                
                if not os.path.exists(path):
                    results.append(f"Error: File not found: {path}")
                    continue
                
                ext = os.path.splitext(path)[1].lower()
                
                # Auto-detect linter
                if linter:
                    lint_cmd = linter
                elif ext == '.py':
                    lint_cmd = 'pylint'
                elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                    lint_cmd = 'eslint'
                else:
                    results.append(f"No linter configured for {ext} files")
                    continue
                
                # Run linter
                try:
                    if lint_cmd == 'pylint':
                        cmd = f'python -m pylint --output-format=text --score=no "{path}"'
                    elif lint_cmd == 'eslint':
                        cmd = f'npx eslint --format=stylish "{path}"'
                    else:
                        cmd = f'{lint_cmd} "{path}"'
                    
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=os.getcwd()
                    )
                    
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=30
                    )
                    
                    output = stdout.decode('utf-8', errors='replace')
                    error = stderr.decode('utf-8', errors='replace')
                    
                    if output.strip():
                        results.append(f"=== {path} ===\n{output.strip()}")
                    elif process.returncode == 0:
                        results.append(f"=== {path} ===\nNo linter errors found.")
                    else:
                        results.append(f"=== {path} ===\n{error.strip() if error else 'Linter returned errors'}")
                        
                except asyncio.TimeoutError:
                    results.append(f"=== {path} ===\nLinter timed out")
                except Exception as e:
                    results.append(f"=== {path} ===\nLinter error: {str(e)}")
            
            if not results:
                return "No files to lint"
            
            return '\n\n'.join(results)
            
        except Exception as e:
            logger.error(f"Read lints failed: {e}")
            return f"Error reading lints: {str(e)}"
    
    logger.info(f"Registered {len(registry.get_by_category(ToolCategory.LOCAL))} local tools")
    return registry

