import { useState } from 'react';
import { 
  MessageSquare, 
  Plus, 
  Search, 
  Trash2,
  MoreHorizontal,
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
import { ConnectorPanel, type ConnectedApp } from './ConnectorPanel';
import { HookMapPanel } from './HookMapPanel';

export interface Session {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
  isActive?: boolean;
}

interface SidebarProps {
  sessions: Session[];
  activeSessionId?: string;
  onNewSession: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  onOpenSettings?: () => void;
  /** 当Connect的应用List变化时Callback */
  onConnectedAppsChange?: (apps: ConnectedApp[]) => void;
}

// ExportClasstypeprovide App.tsx Usage
export type { ConnectedApp };

export function Sidebar({
  sessions,
  activeSessionId,
  onNewSession,
  onSelectSession,
  onDeleteSession,
  // onOpenSettings, // Available but not currently used
  onConnectedAppsChange,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [connectedApps, setConnectedApps] = useState<ConnectedApp[]>([]);

  // HandleConnectApplychange
  const handleConnectedAppsChange = (apps: ConnectedApp[]) => {
    setConnectedApps(apps);
    onConnectedAppsChange?.(apps);
  };

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
    <aside className="w-64 h-full flex flex-col bg-black border-r border-neutral-900">
      {/* Header */}
      <div className="p-3 space-y-3">
        {/* New Chat Button */}
        <Button 
          onClick={onNewSession}
          className="w-full justify-start gap-2 h-10 bg-transparent hover:bg-neutral-900 border border-neutral-800 text-neutral-300 hover:text-white"
          variant="ghost"
        >
          <Plus className="w-4 h-4" />
          <span>New Session</span>
          <kbd className="ml-auto text-[10px] text-neutral-600 bg-neutral-900 px-1.5 py-0.5 rounded font-mono">
            ⌘K
          </kbd>
        </Button>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600" />
          <input
            type="text"
            placeholder="Search sessions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-9 pl-9 pr-3 bg-neutral-950 border border-neutral-800 rounded-lg text-sm text-neutral-300 placeholder:text-neutral-600 focus:outline-none focus:border-neutral-700"
          />
        </div>
      </div>

      {/* Session List */}
      <ScrollArea className="flex-1 px-2">
        <div className="space-y-1 pb-2">
          {filteredSessions.length === 0 ? (
            <div className="text-center py-8 text-neutral-600 text-sm">
              {searchQuery ? 'No sessions found' : 'No sessions yet'}
            </div>
          ) : (
            filteredSessions.map((session) => (
              <div
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && onSelectSession(session.id)}
                className={cn(
                  'group grid grid-cols-[16px_1fr_28px] items-center gap-2 px-3 py-2 transition-all cursor-pointer border-l-2',
                  activeSessionId === session.id
                    ? 'text-white border-white bg-neutral-900/50'
                    : 'text-neutral-500 hover:text-neutral-300 border-transparent hover:border-neutral-700'
                )}
              >
                <MessageSquare className="w-4 h-4" />
                <div className="overflow-hidden">
                  <p className="text-sm truncate">{session.title}</p>
                  <p className="text-[11px] text-neutral-600">{formatTime(session.timestamp)}</p>
                </div>
                {/* Three dots menu */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button
                      className="w-7 h-7 flex items-center justify-center rounded hover:bg-neutral-700 transition-all opacity-0 group-hover:opacity-100"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <MoreHorizontal className="w-4 h-4 text-neutral-400" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent 
                    align="end" 
                    className="w-36 bg-neutral-950 border-neutral-800"
                    onClick={(e) => e.stopPropagation()}
                    onPointerDown={(e) => e.stopPropagation()}
                  >
                    <DropdownMenuItem
                      onSelect={() => onDeleteSession(session.id)}
                      className="text-red-400 focus:text-red-400 focus:bg-neutral-900 cursor-pointer"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Hook Map & Connector Panel */}
      <div className="border-t border-neutral-900 mt-auto">
        {/* Hook Map Panel - 可视化NodeConnect */}
        <div className="relative px-3 py-2">
          <HookMapPanel 
            connectedApps={connectedApps}
            className="w-full"
          />
        </div>

        {/* Connector Panel */}
        <ConnectorPanel 
          defaultExpanded={true} 
          onConnectedAppsChange={handleConnectedAppsChange}
        />
      </div>

    </aside>
  );
}

