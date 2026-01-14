/**
 * BubbleSidebar - Bubble Mode Left Sidebar
 * 
 * Includes:
 * 1. Session list
 * 2. Available apps (dock)
 * 3. Connected apps
 * 4. Drag connector
 */

import { useState, useCallback, useRef, useEffect, memo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Plus,
  Search,
  MessageSquare,
  Trash2,
  MoreHorizontal,
  Link2,
  Unlink,
  Globe,
  Code2,
  FileText,
  AppWindow,
  Music,
  Terminal,
  Crosshair,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

export interface Session {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
  isActive?: boolean;
}

interface WindowInfo {
  hwnd: number;
  title: string;
  app_name: string;
  app_display_name: string;
  icon_base64?: string;
  is_browser: boolean;
}

interface ConnectedApp extends WindowInfo {
  connected_at: string;
}

interface BubbleSidebarProps {
  // Session management
  sessions: Session[];
  activeSessionId?: string;
  onNewSession: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  
  // App connection
  availableWindows: WindowInfo[];
  connectedApps: ConnectedApp[];
  onConnect: (window: WindowInfo) => void;
  onDisconnect: (hwnd: number) => void;
  
  // Drag connector
  isDragging?: boolean;
  onDragStart?: (e: React.MouseEvent) => void;
  
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const APP_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  'Google Chrome': Globe,
  'Chrome': Globe,
  'Mozilla Firefox': Globe,
  'Microsoft Edge': Globe,
  'VS Code': Code2,
  'Cursor': Code2,
  'File Explorer': FileText,
  'Finder': FileText,
  'Figma': AppWindow,
  'Notion': FileText,
  'Spotify': Music,
  'Terminal': Terminal,
  'PowerShell': Terminal,
  'cmd': Terminal,
};

function getAppIcon(appName: string) {
  if (APP_ICONS[appName]) return APP_ICONS[appName];
  for (const [key, icon] of Object.entries(APP_ICONS)) {
    if (appName.toLowerCase().includes(key.toLowerCase())) return icon;
  }
  return AppWindow;
}

// ============================================================================
// AppItem Component
// ============================================================================

interface AppItemProps {
  window: WindowInfo;
  isConnected?: boolean;
  onClick: () => void;
  className?: string;
}

const AppItem = memo(function AppItem({ window, isConnected, onClick, className }: AppItemProps) {
  const Icon = getAppIcon(window.app_display_name || window.app_name);
  
  // Handle icon_base64: check if already has data: prefix
  const iconSrc = window.icon_base64 
    ? (window.icon_base64.startsWith('data:') ? window.icon_base64 : `data:image/png;base64,${window.icon_base64}`)
    : null;
  
  return (
    <motion.button
      onClick={onClick}
      className={cn(
        // 2026: Scroll-driven Animation (native CSS, zero JS)
        "sidebar-item-animate",
        "w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all",
        "hover:bg-white/5",
        isConnected && "bg-emerald-500/10 border border-emerald-500/30",
        className
      )}
      whileHover={{ x: 2 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Icon */}
      <div className={cn(
        "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
        "bg-white/5 border border-white/10",
        isConnected && "bg-emerald-500/20 border-emerald-500/30"
      )}>
        {iconSrc ? (
          <img 
            src={iconSrc} 
            alt="" 
            className="w-5 h-5 object-contain"
          />
        ) : (
          <Icon className={cn(
            "w-4 h-4",
            isConnected ? "text-emerald-400" : "text-white/50"
          )} />
        )}
      </div>
      
      {/* Info */}
      <div className="flex-1 min-w-0 text-left">
        <p className={cn(
          "text-xs font-medium truncate",
          isConnected ? "text-emerald-400" : "text-white/70"
        )}>
          {window.app_display_name || window.app_name}
        </p>
        <p className="text-[10px] text-white/30 truncate">
          {window.title.slice(0, 30)}
        </p>
      </div>
      
      {/* Status indicator */}
      {isConnected && (
        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
      )}
    </motion.button>
  );
});

// ============================================================================
// Section Header
// ============================================================================

interface SectionHeaderProps {
  title: string;
  count?: number;
  isExpanded: boolean;
  onToggle: () => void;
  action?: React.ReactNode;
}

const SectionHeader = memo(function SectionHeader({ 
  title, 
  count, 
  isExpanded, 
  onToggle,
  action 
}: SectionHeaderProps) {
  return (
    <div className="flex items-center justify-between px-3 py-2">
      <button 
        onClick={onToggle}
        className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-white/40 hover:text-white/60 transition-colors"
      >
        {isExpanded ? (
          <ChevronDown className="w-3 h-3" />
        ) : (
          <ChevronRight className="w-3 h-3" />
        )}
        {title}
        {count !== undefined && (
          <span className="text-white/20 ml-1">({count})</span>
        )}
      </button>
      {action}
    </div>
  );
});

// ============================================================================
// Main Component
// ============================================================================

export const BubbleSidebar = memo(function BubbleSidebar({
  sessions,
  activeSessionId,
  onNewSession,
  onSelectSession,
  onDeleteSession,
  availableWindows,
  connectedApps,
  onConnect,
  onDisconnect,
  isDragging,
  onDragStart,
  className,
}: BubbleSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sessionsExpanded, setSessionsExpanded] = useState(true);
  const [availableExpanded, setAvailableExpanded] = useState(true);
  const [connectedExpanded, setConnectedExpanded] = useState(true);

  // Filter unconnected apps (exclude windows without names)
  const unconnectedApps = availableWindows.filter(
    w => !connectedApps.some(c => c.hwnd === w.hwnd)
      && (w.app_display_name || w.app_name || w.title) // At least one name
  );

  // Filter sessions
  const filteredSessions = sessions.filter(
    (session) =>
      session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      session.preview.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <aside className={cn(
      "bubble-sidebar-container w-64 h-full flex flex-col",
      "bg-black/80 backdrop-blur-md border-r border-white/[0.06]",
      className
    )}>
      {/* Header */}
      <div className="p-3 space-y-3 border-b border-white/[0.06]">
        {/* New Chat Button */}
        <Button 
          onClick={onNewSession}
          className="w-full justify-start gap-2 h-9 bg-transparent hover:bg-white/5 border border-white/[0.08] text-white/60 hover:text-white"
          variant="ghost"
        >
          <Plus className="w-4 h-4" />
          <span className="text-sm">New Session</span>
          <kbd className="ml-auto text-[10px] text-white/30 bg-white/5 px-1.5 py-0.5 rounded font-mono">
            ⌘K
          </kbd>
        </Button>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/30" />
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-8 pl-9 pr-3 bg-white/[0.03] border border-white/[0.06] rounded-lg text-xs text-white/80 placeholder:text-white/30 focus:outline-none focus:border-white/20"
          />
        </div>
      </div>

      {/* Scrollable Content */}
      <ScrollArea className="flex-1">
        <div className="py-2">
          
          {/* ========== 1. Sessions - Most important, user focus first ========== */}
          <SectionHeader
            title="Sessions"
            count={filteredSessions.length}
            isExpanded={sessionsExpanded}
            onToggle={() => setSessionsExpanded(!sessionsExpanded)}
          />
          
          <AnimatePresence>
            {sessionsExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden px-2"
              >
                {filteredSessions.length === 0 ? (
                  <p className="text-[10px] text-white/30 text-center py-4 px-3">
                    {searchQuery ? 'No sessions found' : 'No sessions yet'}
                  </p>
                ) : (
                  <div className="space-y-1 pb-2">
                    {filteredSessions.map((session) => (
                      <div
                        key={session.id}
                        onClick={() => onSelectSession(session.id)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => e.key === 'Enter' && onSelectSession(session.id)}
                        className={cn(
                          "group grid grid-cols-[16px_1fr_24px] items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all",
                          activeSessionId === session.id
                            ? "text-white bg-white/10"
                            : "text-white/50 hover:text-white/70 hover:bg-white/5"
                        )}
                      >
                        <MessageSquare className="w-4 h-4" />
                        <div className="overflow-hidden">
                          <p className="text-xs truncate">{session.title}</p>
                          <p className="text-[10px] text-white/30">{formatTime(session.timestamp)}</p>
                        </div>
                        {/* Three dots menu */}
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <button
                              className="w-6 h-6 flex items-center justify-center rounded hover:bg-white/10 transition-all opacity-0 group-hover:opacity-100"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <MoreHorizontal className="w-3.5 h-3.5 text-white/40" />
                            </button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent 
                            align="end" 
                            className="w-32 bg-neutral-950 border-neutral-800"
                            onClick={(e) => e.stopPropagation()}
                            onPointerDown={(e) => e.stopPropagation()}
                          >
                            <DropdownMenuItem
                              onSelect={() => onDeleteSession(session.id)}
                              className="text-red-400 focus:text-red-400 focus:bg-neutral-900 cursor-pointer text-xs"
                            >
                              <Trash2 className="w-3.5 h-3.5 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* ========== 2. Connected Apps - Current work context ========== */}
          <div className="mt-2 border-t border-white/[0.06] pt-2">
            <SectionHeader
              title="Connected"
              count={connectedApps.length}
              isExpanded={connectedExpanded}
              onToggle={() => setConnectedExpanded(!connectedExpanded)}
            />
            
            <AnimatePresence>
              {connectedExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden px-2"
                >
                  {connectedApps.length === 0 ? (
                    <p className="text-[10px] text-white/30 text-center py-3 px-3">
                      Select an app below to connect
                    </p>
                  ) : (
                    <div className="space-y-1 pb-2">
                      {connectedApps.map((app) => (
                        <AppItem
                          key={app.hwnd}
                          window={app}
                          isConnected
                          onClick={() => onDisconnect(app.hwnd)}
                        />
                      ))}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* ========== 3. Available Apps - Expand on demand ========== */}
          <div className="mt-2 border-t border-white/[0.06] pt-2">
            <SectionHeader
              title="Available"
              count={unconnectedApps.length}
              isExpanded={availableExpanded}
              onToggle={() => setAvailableExpanded(!availableExpanded)}
            />
            
            <AnimatePresence>
              {availableExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden px-2"
                >
                  {unconnectedApps.length === 0 ? (
                    <p className="text-[10px] text-white/30 text-center py-3 px-3">
                      No apps available
                    </p>
                  ) : (
                    <div className="space-y-1 pb-1">
                      {unconnectedApps.map((window) => (
                        <AppItem
                          key={window.hwnd}
                          window={window}
                          onClick={() => onConnect(window)}
                        />
                      ))}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          
          {/* Drag Connector */}
          <div className="p-3 mt-2 border-t border-white/[0.06]">
            <motion.button
              onMouseDown={onDragStart}
              className={cn(
                "w-full flex items-center justify-center gap-2 h-10 rounded-lg transition-all",
                "cursor-grab active:cursor-grabbing",
                isDragging
                  ? "bg-emerald-500/20 border-2 border-emerald-500/50 text-emerald-400"
                  : "bg-white/[0.03] border border-white/[0.08] text-white/50 hover:text-white/70 hover:bg-white/5 hover:border-white/15"
              )}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Crosshair className="w-4 h-4" />
              <span className="text-xs font-medium">
                {isDragging ? 'Release on target window' : 'Drag to connect'}
              </span>
            </motion.button>
            
            {/* Drag hint */}
            <AnimatePresence>
              {isDragging && (
                <motion.p
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 5 }}
                  className="text-[10px] text-emerald-400/60 text-center mt-2"
                >
                  Move cursor to target window and release...
                </motion.p>
              )}
            </AnimatePresence>
          </div>
        </div>
      </ScrollArea>
    </aside>
  );
});

export default BubbleSidebar;
