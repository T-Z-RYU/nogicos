# -*- coding: utf-8 -*-
"""
Tool Descriptions - Cursor-style detailed tool descriptions for NogicOS Agent

This module provides structured, detailed descriptions for all tools,
following the pattern observed in Cursor's tool definitions:
- Summary: Brief description of what the tool does
- When to Use: Specific scenarios where this tool is appropriate
- When NOT to Use: Common mistakes and better alternatives
- Parameters: Detailed parameter documentation
- Examples: Usage examples
- Returns: What the tool returns

Reference: Cursor's tool descriptions use "When to Use / When NOT to Use" pattern
to help the LLM make better tool selection decisions.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ToolDescription:
    """
    Structured tool description following Cursor's pattern.
    
    The description is formatted as markdown-like text that LLMs can easily parse.
    """
    summary: str
    when_to_use: List[str] = field(default_factory=list)
    when_not_to_use: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    returns: str = ""
    notes: List[str] = field(default_factory=list)
    
    def to_string(self) -> str:
        """Convert to formatted string for tool definition."""
        lines = [self.summary, ""]
        
        if self.when_to_use:
            lines.append("WHEN TO USE:")
            for item in self.when_to_use:
                lines.append(f"- {item}")
            lines.append("")
        
        if self.when_not_to_use:
            lines.append("WHEN NOT TO USE:")
            for item in self.when_not_to_use:
                lines.append(f"- {item}")
            lines.append("")
        
        if self.parameters:
            lines.append("Parameters:")
            for param in self.parameters:
                lines.append(f"- {param}")
            lines.append("")
        
        if self.examples:
            lines.append("Examples:")
            for ex in self.examples:
                lines.append(f"- {ex}")
            lines.append("")
        
        if self.returns:
            lines.append(f"Returns: {self.returns}")
        
        if self.notes:
            lines.append("")
            for note in self.notes:
                lines.append(f"Note: {note}")
        
        return "\n".join(lines).strip()
    
    def __str__(self) -> str:
        return self.to_string()


# =============================================================================
# LOCAL TOOLS DESCRIPTIONS
# =============================================================================

READ_FILE = ToolDescription(
    summary="Read file content from local filesystem.",
    when_to_use=[
        "Reading known file paths",
        "Viewing configuration, source code, or data files",
        "Checking file content before modification",
        "Understanding existing code structure",
    ],
    when_not_to_use=[
        "Finding files by pattern → use glob_search",
        "Searching content across files → use grep_search",
        "Listing directory contents → use list_directory",
        "Semantic code search → use codebase_search",
    ],
    parameters=[
        "path: File path (relative/absolute, supports ~)",
        "limit: Max lines to read (0 = unlimited, default: 0)",
    ],
    returns="File content (truncated if >50KB)",
)

WRITE_FILE = ToolDescription(
    summary="Write content to file (creates or overwrites).",
    when_to_use=[
        "Creating new files",
        "Overwriting entire file content",
        "Saving generated code, config, or data",
        "Creating files from scratch",
    ],
    when_not_to_use=[
        "Partial text replacement → use search_replace",
        "Appending to file → use append_file",
        "Small edits to existing code → prefer search_replace",
    ],
    parameters=[
        "path: Target file path",
        "content: Content to write",
    ],
    returns="Success message with byte count",
    notes=[
        "Creates parent directories automatically",
        "Overwrites existing files without warning",
    ],
)

APPEND_FILE = ToolDescription(
    summary="Append content to the end of a file.",
    when_to_use=[
        "Adding to log files",
        "Appending new entries to data files",
        "Adding content without reading entire file",
        "Building files incrementally",
    ],
    when_not_to_use=[
        "Creating new file → use write_file",
        "Inserting in middle → use search_replace",
        "Overwriting content → use write_file",
    ],
    parameters=[
        "path: Target file path",
        "content: Content to append",
    ],
    returns="Success message with byte count",
    notes=["Creates the file if it doesn't exist"],
)

LIST_DIRECTORY = ToolDescription(
    summary="List directory contents with file types and sizes.",
    when_to_use=[
        "Exploring unfamiliar directories",
        "Checking what files exist before operations",
        "Getting overview of folder structure",
        "Verifying file/folder existence",
    ],
    when_not_to_use=[
        "Finding specific file types → use glob_search",
        "Reading file content → use read_file",
        "Searching inside files → use grep_search",
        "Deep recursive listing → use glob_search with **/*",
    ],
    parameters=[
        "path: Directory path (default: current directory)",
    ],
    returns="List with [DIR]/[FILE] markers and sizes",
    notes=["Use this first when unsure what files exist in a location"],
)

GLOB_SEARCH = ToolDescription(
    summary="Find files by name pattern using glob syntax.",
    when_to_use=[
        "Finding files by extension (*.py, *.tsx)",
        "Locating files by name pattern (test_*, config.*)",
        "Listing specific file types in a directory tree",
        "Finding all files matching a pattern recursively",
    ],
    when_not_to_use=[
        "Searching file content → use grep_search",
        "Semantic code search → use codebase_search",
        "Listing all directory contents → use list_directory",
        "Finding by exact path → use path_exists",
    ],
    parameters=[
        "pattern: Glob pattern (supports *, **, ?, [abc])",
        "root: Starting directory (default: current)",
    ],
    examples=[
        'glob_search("**/*.py") → All Python files',
        'glob_search("test_*.py", "tests/") → Test files in tests/',
        'glob_search("*.{js,ts}") → JS and TS files',
    ],
    returns="Matching file paths (max 100)",
)

GREP_SEARCH = ToolDescription(
    summary="Search text or regex pattern in files (like grep/ripgrep).",
    when_to_use=[
        "Finding exact text or regex matches in code",
        "Locating function/variable definitions",
        "Searching logs or data files for patterns",
        "Finding all usages of a string",
    ],
    when_not_to_use=[
        "Finding files by name → use glob_search",
        "Semantic/meaning-based search → use codebase_search",
        "Reading known file → use read_file",
        "Simple file listing → use list_directory",
    ],
    parameters=[
        "pattern: Text or regex pattern to search",
        "path: Search path (default: current directory)",
        "file_pattern: Filter by glob (default: *)",
    ],
    examples=[
        'grep_search("def main", ".", "*.py") → Find main function in Python files',
        'grep_search("TODO", ".") → Find all TODOs',
        'grep_search("import.*React", "src/", "*.tsx") → Find React imports',
    ],
    returns="Matching lines as file:line:content (max 50)",
)

SHELL_EXECUTE = ToolDescription(
    summary="Execute shell command and return output.",
    when_to_use=[
        "Installing packages (npm, pip, etc.)",
        "Running scripts or build commands",
        "Git operations",
        "System commands without dedicated tools",
        "Running tests",
    ],
    when_not_to_use=[
        "Listing directories → use list_directory (more reliable)",
        "Reading files → use read_file (handles encoding)",
        "Searching files → use glob_search or grep_search",
        "File operations → use dedicated file tools",
    ],
    parameters=[
        "command: Shell command to execute",
        "timeout: Max seconds (default: 30)",
    ],
    returns="STDOUT, STDERR, and exit code",
    notes=[
        "Security: Blocks rm -rf /, sudo, format, shutdown",
        "Windows: Use ; instead of && for command chaining",
    ],
)

SEARCH_REPLACE = ToolDescription(
    summary="Perform exact string replacement in files.",
    when_to_use=[
        "Renaming variables/functions across a file",
        "Fixing specific text patterns",
        "Precise code modifications",
        "Updating imports or references",
        "Small, targeted edits",
    ],
    when_not_to_use=[
        "Creating new files → use write_file",
        "Overwriting entire file → use write_file",
        "Complex regex transforms → use shell_execute with sed",
        "Multi-file refactoring → call multiple times",
    ],
    parameters=[
        "file_path: Target file",
        "old_string: Text to find (must be unique in file)",
        "new_string: Replacement text",
        "replace_all: Replace all occurrences (default: False)",
    ],
    returns="Success message with replacement count",
    notes=[
        "old_string must match exactly including whitespace",
        "If multiple matches and replace_all=False, will error - provide more context to make unique",
    ],
)

MOVE_FILE = ToolDescription(
    summary="Move or rename file/directory.",
    when_to_use=[
        "Renaming files or folders",
        "Moving files between directories",
        "Reorganizing project structure",
        "Batch file organization",
    ],
    when_not_to_use=[
        "Copying files (keep original) → use copy_file",
        "Deleting files → use delete_file",
        "Moving to trash → use delete_file",
    ],
    parameters=[
        "source: Path to move from",
        "destination: Target path (can be new name or directory)",
    ],
    returns="Success message",
    notes=[
        "Creates destination directory if needed",
        "PROTECTED: Won't move .git, code projects, system folders",
    ],
)

COPY_FILE = ToolDescription(
    summary="Copy a file or directory.",
    when_to_use=[
        "Creating backups",
        "Duplicating files/folders",
        "Copying templates",
        "Creating file copies for modification",
    ],
    when_not_to_use=[
        "Moving files (remove original) → use move_file",
        "Creating new file from scratch → use write_file",
    ],
    parameters=[
        "source: Path to copy from",
        "destination: Path to copy to",
    ],
    examples=[
        'copy_file("doc.txt", "doc_backup.txt")',
        'copy_file("folder", "folder_copy")',
        'copy_file("config.json", "backup/config.json")',
    ],
    returns="Success message",
    notes=["Preserves file metadata, creates destination dir if needed"],
)

DELETE_FILE = ToolDescription(
    summary="Delete file or directory.",
    when_to_use=[
        "Removing temporary files",
        "Cleaning up old directories",
        "Deleting generated outputs",
        "Removing unwanted files",
    ],
    when_not_to_use=[
        "Moving files elsewhere → use move_file",
        "Archiving → use move_file to backup location",
        "Renaming → use move_file",
    ],
    parameters=[
        "path: File or directory to delete",
        "recursive: Delete non-empty directories (default: False)",
    ],
    returns="Success message",
    notes=[
        "PROTECTED: Won't delete .git, code projects, system files",
        "Use recursive=True only when sure - cannot be undone",
    ],
)

CREATE_DIRECTORY = ToolDescription(
    summary="Create directory with parent directories.",
    when_to_use=[
        "Creating new folder structure",
        "Setting up project directories",
        "Preparing output locations",
        "Organizing files into new folders",
    ],
    when_not_to_use=[
        "Directory already exists (but safe - no error)",
    ],
    parameters=[
        "path: Directory path to create",
    ],
    returns="Success message",
    notes=["Safe if directory already exists (no error)"],
)

GET_CWD = ToolDescription(
    summary="Get the current working directory.",
    when_to_use=[
        "Checking current location",
        "Building relative paths",
        "Debugging path issues",
    ],
    when_not_to_use=[
        "Listing directory contents → use list_directory",
    ],
    parameters=[],
    returns="Absolute path of current working directory",
)

PATH_EXISTS = ToolDescription(
    summary="Check if a file or directory exists.",
    when_to_use=[
        "Verifying path before operations",
        "Checking if file needs to be created",
        "Validating user-provided paths",
        "Conditional logic based on existence",
    ],
    when_not_to_use=[
        "Listing directory contents → use list_directory",
        "Finding files by pattern → use glob_search",
    ],
    parameters=[
        "path: Path to check",
    ],
    returns="Exists (True/False), Type (file/directory), Size if file",
)

READ_LINTS = ToolDescription(
    summary="Read linter errors for code files.",
    when_to_use=[
        "After editing code files",
        "Checking for syntax errors",
        "Validating code quality",
        "Before committing changes",
    ],
    when_not_to_use=[
        "Reading file content → use read_file",
        "Running tests → use shell_execute",
        "Type checking → use shell_execute with tsc/mypy",
    ],
    parameters=[
        "paths: List of file paths to lint",
        "linter: Override linter (auto-detected by extension: .py→pylint, .js/.ts→eslint)",
    ],
    returns="List of errors with line numbers and messages",
)


# =============================================================================
# BROWSER TOOLS DESCRIPTIONS
# =============================================================================

BROWSER_NAVIGATE = ToolDescription(
    summary="Navigate to a URL in the browser.",
    when_to_use=[
        "Opening a webpage",
        "Loading a new URL",
        "Navigating to a different page",
        "Starting a web interaction session",
    ],
    when_not_to_use=[
        "Clicking links on current page → use browser_click",
        "Refreshing current page → use browser_navigate with same URL",
        "Going back → use browser_navigate_back (if available)",
    ],
    parameters=[
        "url: Full URL to navigate to (must include http:// or https://)",
    ],
    examples=[
        'browser_navigate("https://google.com")',
        'browser_navigate("https://github.com/user/repo")',
    ],
    returns="Page title after navigation",
)

BROWSER_CLICK = ToolDescription(
    summary="Click on an element in the browser.",
    when_to_use=[
        "Clicking buttons",
        "Following links",
        "Selecting options",
        "Interacting with UI elements",
    ],
    when_not_to_use=[
        "Typing into input fields → use browser_type",
        "Navigating to known URL → use browser_navigate",
        "Selecting from dropdown → may need browser_type for some dropdowns",
    ],
    parameters=[
        "selector: CSS selector or text content to identify element",
    ],
    examples=[
        'browser_click("#submit-button")',
        'browser_click(".nav-link")',
        'browser_click("button:contains(Submit)")',
    ],
    returns="Confirmation of click action",
    notes=["Element must be visible and clickable"],
)

BROWSER_TYPE = ToolDescription(
    summary="Type text into an input field in the browser.",
    when_to_use=[
        "Filling form fields",
        "Typing in search boxes",
        "Entering text into text areas",
        "Providing input to web applications",
    ],
    when_not_to_use=[
        "Clicking buttons → use browser_click",
        "Selecting from dropdown → may need browser_click first",
        "Submitting forms → use browser_click on submit button after typing",
    ],
    parameters=[
        "selector: CSS selector to identify the input element",
        "text: Text to type into the element",
    ],
    examples=[
        'browser_type("#search-input", "search query")',
        'browser_type("input[name=email]", "user@example.com")',
    ],
    returns="Confirmation of typing action",
    notes=["Clears existing content before typing"],
)

BROWSER_SCREENSHOT = ToolDescription(
    summary="Take a screenshot of the current browser page.",
    when_to_use=[
        "Capturing current page state",
        "Debugging visual issues",
        "Documenting web content",
        "Verifying page loaded correctly",
    ],
    when_not_to_use=[
        "Getting page text content → use browser_get_content (if available)",
        "Extracting specific data → use browser_extract (if available)",
    ],
    parameters=[],
    returns="Screenshot as base64-encoded image",
    notes=["Captures visible viewport only"],
)

BROWSER_GET_CONTENT = ToolDescription(
    summary="Get the text content of the current page.",
    when_to_use=[
        "Extracting readable text from page",
        "Getting article or document content",
        "Reading page without visual rendering",
        "Processing page text programmatically",
    ],
    when_not_to_use=[
        "Need visual layout → use browser_screenshot",
        "Need specific element → use browser_extract with selector",
        "Need raw HTML → use browser_get_html (if available)",
    ],
    parameters=[],
    returns="Plain text content of the page",
)

BROWSER_SCROLL = ToolDescription(
    summary="Scroll the browser page.",
    when_to_use=[
        "Loading lazy-loaded content",
        "Viewing content below the fold",
        "Navigating long pages",
        "Triggering infinite scroll",
    ],
    when_not_to_use=[
        "Clicking elements → use browser_click (handles scroll automatically)",
        "Going to specific element → use browser_click on that element",
    ],
    parameters=[
        "direction: 'up' or 'down'",
        "amount: Pixels to scroll (default: viewport height)",
    ],
    returns="Confirmation of scroll action",
)

BROWSER_EXTRACT = ToolDescription(
    summary="Extract data from specific elements on the page.",
    when_to_use=[
        "Getting specific element text",
        "Extracting structured data",
        "Scraping specific page sections",
        "Reading element attributes",
    ],
    when_not_to_use=[
        "Getting full page text → use browser_get_content",
        "Visual inspection → use browser_screenshot",
    ],
    parameters=[
        "selector: CSS selector for target element(s) (empty = full page)",
    ],
    returns="Extracted content from matching elements (max 5000 chars)",
)

BROWSER_GET_URL = ToolDescription(
    summary="Get the current page URL.",
    when_to_use=[
        "Checking current location",
        "Verifying navigation success",
        "Building relative URLs",
        "Logging current state",
    ],
    when_not_to_use=[
        "Getting page content → use browser_get_content",
        "Checking page title → use browser_get_title",
    ],
    parameters=[],
    returns="Current page URL",
)

BROWSER_GET_TITLE = ToolDescription(
    summary="Get the current page title.",
    when_to_use=[
        "Verifying correct page loaded",
        "Getting page identification",
        "Checking navigation result",
    ],
    when_not_to_use=[
        "Getting page content → use browser_get_content",
        "Getting URL → use browser_get_url",
    ],
    parameters=[],
    returns="Page title or '(No title)' if empty",
)

BROWSER_BACK = ToolDescription(
    summary="Go back to the previous page in browser history.",
    when_to_use=[
        "Returning to previous page",
        "Undoing accidental navigation",
        "Multi-step navigation workflows",
    ],
    when_not_to_use=[
        "Navigating to specific URL → use browser_navigate",
        "Refreshing current page → navigate to same URL",
    ],
    parameters=[],
    returns="Confirmation of back navigation",
)

BROWSER_WAIT = ToolDescription(
    summary="Wait for a specified number of seconds.",
    when_to_use=[
        "Waiting for page to load",
        "Allowing animations to complete",
        "Rate limiting requests",
        "Waiting for dynamic content",
    ],
    when_not_to_use=[
        "Checking if element exists → use browser_extract",
        "Long waits (>10s) → consider if action is correct",
    ],
    parameters=[
        "seconds: Number of seconds to wait (default: 1)",
    ],
    returns="Confirmation with wait duration",
)

BROWSER_SEND_KEYS = ToolDescription(
    summary="Send keyboard keys to the browser.",
    when_to_use=[
        "Pressing Enter to submit forms",
        "Using Tab to navigate fields",
        "Pressing Escape to close dialogs",
        "Arrow keys for navigation",
        "Keyboard shortcuts",
    ],
    when_not_to_use=[
        "Typing text into input → use browser_type",
        "Clicking elements → use browser_click",
    ],
    parameters=[
        "keys: Key name ('Enter', 'Tab', 'Escape', 'ArrowDown', etc.)",
    ],
    examples=[
        'browser_send_keys("Enter") → Submit form',
        'browser_send_keys("Tab") → Next field',
        'browser_send_keys("Escape") → Close dialog',
    ],
    returns="Confirmation of keys sent",
)


# =============================================================================
# DESCRIPTION REGISTRY
# =============================================================================

LOCAL_DESCRIPTIONS = {
    "read_file": READ_FILE,
    "write_file": WRITE_FILE,
    "append_file": APPEND_FILE,
    "list_directory": LIST_DIRECTORY,
    "glob_search": GLOB_SEARCH,
    "grep_search": GREP_SEARCH,
    "shell_execute": SHELL_EXECUTE,
    "search_replace": SEARCH_REPLACE,
    "move_file": MOVE_FILE,
    "copy_file": COPY_FILE,
    "delete_file": DELETE_FILE,
    "create_directory": CREATE_DIRECTORY,
    "get_cwd": GET_CWD,
    "path_exists": PATH_EXISTS,
    "read_lints": READ_LINTS,
}

BROWSER_DESCRIPTIONS = {
    "browser_navigate": BROWSER_NAVIGATE,
    "browser_click": BROWSER_CLICK,
    "browser_type": BROWSER_TYPE,
    "browser_screenshot": BROWSER_SCREENSHOT,
    "browser_get_content": BROWSER_GET_CONTENT,
    "browser_scroll": BROWSER_SCROLL,
    "browser_extract": BROWSER_EXTRACT,
    "browser_get_url": BROWSER_GET_URL,
    "browser_get_title": BROWSER_GET_TITLE,
    "browser_back": BROWSER_BACK,
    "browser_wait": BROWSER_WAIT,
    "browser_send_keys": BROWSER_SEND_KEYS,
}

ALL_DESCRIPTIONS = {**LOCAL_DESCRIPTIONS, **BROWSER_DESCRIPTIONS}


def get_description(tool_name: str) -> Optional[ToolDescription]:
    """Get description for a tool by name."""
    return ALL_DESCRIPTIONS.get(tool_name)


def get_description_string(tool_name: str) -> str:
    """Get formatted description string for a tool."""
    desc = get_description(tool_name)
    if desc:
        return desc.to_string()
    return f"Tool: {tool_name}"

