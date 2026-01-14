# -*- coding: utf-8 -*-
"""
Context Store - UpDown文存储System

存储 Hook System捕获的UpDown文Info：
- 当BeforeState（Inner存）：实时的ConnectState和UpDown文
- 历史记录（SQLite）：持久化的Event历史
"""

import asyncio
import json
import logging
import sqlite3
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class HookType(Enum):
    """Hook Class型"""
    BROWSER = "browser"
    DESKTOP = "desktop"
    FILE = "file"
    APP = "app"  # generalApply Hook（Newincrease）


class AppType(Enum):
    """应用Class型（用于通用 App Hook）"""
    BROWSER = "browser"     # BrowserClassApply
    IDE = "ide"             # OnemitTool
    DESIGN = "design"       # DesignTool
    COMMUNICATION = "communication"  # communicationTool
    PRODUCTIVITY = "productivity"    # officeTool
    MEDIA = "media"         # mediaTool
    OTHER = "other"         # Other


class HookStatus(Enum):
    """Hook ConnectState"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class BrowserContext:
    """浏览器UpDown文"""
    app: str = ""                  # Chrome, Firefox, Edge, etc.
    url: str = ""                  # whenBefore URL
    title: str = ""                # pagetitle（fromWindowtitleParse）
    window_title: str = ""         # CompleteWindowtitle（for Overlay preciseMatch）
    hwnd: int = 0                  # Windowhandle（for Overlay）
    tab_count: int = 0             # tab Count
    tabs: List[Dict[str, str]] = field(default_factory=list)  # [{url, title}, ...]
    page_summary: str = ""         # pageInnercontentSummary
    screenshot_path: Optional[str] = None  # mostnearcaptureGraphPath
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DesktopContext:
    """桌面UpDown文"""
    hwnd: int = 0                  # Windowhandle
    active_app: str = ""           # whenBeforeActiveApply（Processnamelike chrome.exe）
    active_window: str = ""        # whenBeforeActiveWindowtitle
    window_list: List[Dict[str, str]] = field(default_factory=list)  # WindowList
    screenshot_path: Optional[str] = None
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class FileContext:
    """FileUpDown文"""
    watched_dirs: List[str] = field(default_factory=list)   # Listen's Directory
    recent_files: List[str] = field(default_factory=list)   # mostnearModify's File
    clipboard: str = ""            # clipboardInnercontent
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AppContext:
    """
    通用应用UpDown文（New版统一Interface）
    
    用于任意应用的Connect，Root据 app_type 提供不同级别的UpDown文Info
    """
    # basicallyInfo（allApplyallhave）
    hwnd: int = 0                  # Windowhandle
    title: str = ""                # Windowtitle
    app_name: str = ""             # Processname（like chrome.exe）
    app_display_name: str = ""     # Displayname（like Google Chrome）
    app_type: str = "other"        # ApplyClasstype（browser, ide, design, etc.）
    
    # WindowInfo
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    
    # Browserspecialhave（app_type == browser）
    url: str = ""                  # whenBefore URL
    tab_count: int = 0             # Tab Count
    
    # IDE specialhave（app_type == ide）
    file_path: str = ""            # whenBeforeFilePath
    project_path: str = ""         # projectPath
    
    # captureGraph/OCR（general）
    screenshot_path: Optional[str] = None
    ocr_text: Optional[str] = None
    
    # elementData
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HookState:
    """单个 Hook 的State"""
    type: HookType
    status: HookStatus = HookStatus.DISCONNECTED
    target: str = ""               # TargetApply/Directory
    context: Optional[Any] = None  # BrowserContext / DesktopContext / FileContext
    error: Optional[str] = None
    connected_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert为Dict"""
        return {
            "type": self.type.value,
            "status": self.status.value,
            "target": self.target,
            "context": asdict(self.context) if self.context else None,
            "error": self.error,
            "connected_at": self.connected_at,
        }


@dataclass
class ContextEvent:
    """UpDown文Event（用于历史记录）"""
    id: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    hook_type: str = ""
    event_type: str = ""           # connected, disconnected, updated, error
    data: Dict[str, Any] = field(default_factory=dict)


class ContextStore:
    """
    UpDown文存储
    
    - 当BeforeState：Inner存Medium的实时State
    - 历史记录：SQLite 持久化
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Context Store
        
        Args:
            db_path: SQLite 数据LibraryPath，None 则UsageDefaultPath
        """
        self._lock = threading.Lock()
        
        # whenBeforeState（Innerstore）
        self._hooks: Dict[str, HookState] = {}
        
        # EventListener
        self._listeners: List[Callable[[str, HookState], None]] = []
        
        # DataLibraryPath
        if db_path is None:
            db_dir = Path(__file__).parent.parent.parent / "data"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "context_history.db")
        
        self._db_path = db_path
        self._init_db()
        
        logger.info(f"[ContextStore] Initialized, db: {db_path}")
    
    def _init_db(self):
        """Initialize数据LibraryTable"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    hook_type TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    data TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON context_events(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_hook_type 
                ON context_events(hook_type)
            """)
            conn.commit()
    
    # ============== Statemanage ==============
    
    def get_hook_state(self, hook_id: str) -> Optional[HookState]:
        """Get Hook State"""
        with self._lock:
            return self._hooks.get(hook_id)
    
    def get_all_hooks(self) -> Dict[str, HookState]:
        """Get所有 Hook State"""
        with self._lock:
            return dict(self._hooks)
    
    def get_connected_hooks(self) -> Dict[str, HookState]:
        """Get所有已Connect的 Hook"""
        with self._lock:
            return {
                k: v for k, v in self._hooks.items() 
                if v.status == HookStatus.CONNECTED
            }
    
    def set_hook_state(self, hook_id: str, state: HookState):
        """Set Hook State"""
        with self._lock:
            old_state = self._hooks.get(hook_id)
            self._hooks[hook_id] = state
        
        # NotifyListener
        self._notify_listeners(hook_id, state)
        
        # RecordEvent
        if old_state is None or old_state.status != state.status:
            self.record_event(ContextEvent(
                hook_type=state.type.value,
                event_type=state.status.value,
                data=state.to_dict(),
            ))
    
    def update_context(self, hook_id: str, context: Any):
        """Update Hook 的UpDown文"""
        state = None
        with self._lock:
            # [Repair #17]LockInnertwotimeCheck，ensureStateonecauseproperty
            if hook_id in self._hooks:
                self._hooks[hook_id].context = context
                state = self._hooks[hook_id]

        if state is not None:
            self._notify_listeners(hook_id, state)
    
    def remove_hook(self, hook_id: str):
        """移除 Hook"""
        with self._lock:
            if hook_id in self._hooks:
                state = self._hooks.pop(hook_id)
                self.record_event(ContextEvent(
                    hook_type=state.type.value,
                    event_type="removed",
                    data={"hook_id": hook_id},
                ))
    
    # ============== EventListen ==============
    
    def add_listener(self, callback: Callable[[str, HookState], None]):
        """AddState变更Listen器"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable[[str, HookState], None]):
        """移除Listen器"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, hook_id: str, state: HookState):
        """Notify所有Listen器"""
        for listener in self._listeners:
            try:
                listener(hook_id, state)
            except Exception as e:
                logger.error(f"[ContextStore] Listener error: {e}")
    
    # ============== History ==============
    
    def record_event(self, event: ContextEvent):
        """记录Event到历史"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT INTO context_events (timestamp, hook_type, event_type, data) VALUES (?, ?, ?, ?)",
                    (event.timestamp, event.hook_type, event.event_type, json.dumps(event.data))
                )
                conn.commit()
        except Exception as e:
            logger.error(f"[ContextStore] Failed to record event: {e}")
    
    def get_recent_events(self, minutes: int = 30, hook_type: Optional[str] = None) -> List[ContextEvent]:
        """Get最近 N Minute的历史Event"""
        try:
            from datetime import timedelta
            cutoff = (datetime.now() - timedelta(minutes=minutes)).isoformat()
            
            with sqlite3.connect(self._db_path) as conn:
                if hook_type:
                    cursor = conn.execute(
                        "SELECT id, timestamp, hook_type, event_type, data FROM context_events "
                        "WHERE timestamp > ? AND hook_type = ? ORDER BY timestamp DESC",
                        (cutoff, hook_type)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT id, timestamp, hook_type, event_type, data FROM context_events "
                        "WHERE timestamp > ? ORDER BY timestamp DESC",
                        (cutoff,)
                    )
                
                events = []
                for row in cursor.fetchall():
                    events.append(ContextEvent(
                        id=row[0],
                        timestamp=row[1],
                        hook_type=row[2],
                        event_type=row[3],
                        data=json.loads(row[4]),
                    ))
                return events
        except Exception as e:
            logger.error(f"[ContextStore] Failed to get recent events: {e}")
            return []
    
    # ============== Agent Interface ==============
    
    def get_context_for_agent(self) -> Dict[str, Any]:
        """
        Get当BeforeUpDown文（供 Agent Usage）
        
        Returns:
            Package含所有已Connect Hook UpDown文的Dict
        """
        connected = self.get_connected_hooks()
        
        context = {
            "connected_hooks": list(connected.keys()),
            "browser": None,
            "desktop": None,
            "files": None,
            # Newincrease：SupportmultipleWindow
            "connected_windows": [],  # List[AppContext]
        }
        
        for hook_id, state in connected.items():
            if state.type == HookType.BROWSER and state.context:
                context["browser"] = asdict(state.context)
            elif state.type == HookType.DESKTOP and state.context:
                context["desktop"] = asdict(state.context)
            elif state.type == HookType.FILE and state.context:
                context["files"] = asdict(state.context)
            
            # receivesetallwith hwnd 's UpDowntext
            if state.context and hasattr(state.context, 'hwnd') and state.context.hwnd:
                ctx_dict = asdict(state.context) if hasattr(state.context, '__dataclass_fields__') else {}
                if ctx_dict:
                    ctx_dict['hook_id'] = hook_id
                    context["connected_windows"].append(ctx_dict)
        
        return context
    
    def format_context_prompt(self) -> str:
        """
        格式化UpDown文为 prompt Character串
        
        Returns:
            可直接注入到 system prompt 的UpDown文描述
        """
        ctx = self.get_context_for_agent()
        
        if not ctx["connected_hooks"]:
            return ""
        
        lines = ["[CONNECTED TARGETS - You MUST use these windows, do NOT enumerate windows yourself:]"]
        
        # Newincrease：DisplayallConnect's Window
        connected_windows = ctx.get("connected_windows", [])
        if connected_windows:
            lines.append(f"\n## Connected Windows ({len(connected_windows)} total)")
            for i, win in enumerate(connected_windows, 1):
                hwnd = win.get('hwnd', 0)
                title = win.get('title', '') or win.get('active_window', '')
                app = win.get('app_name', '') or win.get('app_display_name', '') or win.get('active_app', '')
                app_type = win.get('app_type', 'unknown')
                
                lines.append(f"\n### Window {i}: {app}")
                lines.append(f"- **HWND: {hwnd}** ← Target window handle")
                lines.append(f"- Title: {title}")
                lines.append(f"- Type: {app_type}")
                
                # BrowserspecialhaveInfo
                if win.get('url'):
                    lines.append(f"- URL: {win['url']}")
                if win.get('tab_count'):
                    lines.append(f"- Tabs: {win['tab_count']}")
            
            lines.append(f"\n⚠️ IMPORTANT: User has connected to {len(connected_windows)} specific window(s).")
            lines.append(f"   Do NOT call list_windows or find_window to find other windows.")
            lines.append(f"   Always use the HWND values above for window_screenshot, window_click, etc.")
        
        # CompatOldFormat
        elif ctx["browser"]:
            b = ctx["browser"]
            hwnd = b.get('hwnd', 0)
            lines.append(f"\n## Browser Target ({b['app']})")
            lines.append(f"- **HWND: {hwnd}** ← Use this for all browser operations")
            lines.append(f"- Active URL: {b['url']}")
            lines.append(f"- Page Title: {b['title']}")
            if b.get('tabs'):
                lines.append(f"- Open Tabs ({len(b['tabs'])}):")
                for i, tab in enumerate(b['tabs'][:5]):  # mostDisplay 5 a
                    lines.append(f"  {i+1}. {tab.get('title', 'Unknown')} - {tab.get('url', '')}")
                if len(b['tabs']) > 5:
                    lines.append(f"  ... and {len(b['tabs']) - 5} more tabs")
        
        elif ctx["desktop"]:
            d = ctx["desktop"]
            hwnd = d.get('hwnd', 0)
            lines.append(f"\n## Desktop Target")
            lines.append(f"- **HWND: {hwnd}** ← Use this for all desktop operations (click, type, screenshot)")
            lines.append(f"- App: {d['active_app']}")
            lines.append(f"- Window Title: {d['active_window']}")
            lines.append(f"\n⚠️ IMPORTANT: User has connected to this specific window.")
            lines.append(f"   Do NOT call list_windows or find_window to find another window.")
            lines.append(f"   Always use hwnd={hwnd} for window_screenshot, window_click, etc.")
        
        if ctx["files"]:
            f = ctx["files"]
            lines.append(f"\n## Files")
            if f.get('recent_files'):
                lines.append("- Recent Files:")
                for path in f['recent_files'][:5]:
                    lines.append(f"  - {path}")
            if f.get('clipboard'):
                clip = f['clipboard'][:200] + "..." if len(f['clipboard']) > 200 else f['clipboard']
                lines.append(f"- Clipboard: {clip}")
        
        return "\n".join(lines)


# GlobalSingleton
_context_store: Optional[ContextStore] = None
_store_lock = threading.Lock()


def get_context_store() -> ContextStore:
    """Get Context Store Singleton"""
    global _context_store
    with _store_lock:
        if _context_store is None:
            _context_store = ContextStore()
        return _context_store

