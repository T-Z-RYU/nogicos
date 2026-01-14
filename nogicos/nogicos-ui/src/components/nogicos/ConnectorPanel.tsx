/**
 * ConnectorPanel - 通用应用Connect器
 * 
 * 双PathConnect方案：
 * 1. Path A：WindowListSelect - Search并点击Connect
 * 2. Path B：拖拽Connect器 - 拖拽Graph标到TargetWindow
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Globe, 
  Plug,
  Unplug,
  ChevronDown,
  Search,
  GripVertical,
  Crosshair,
  CheckCircle2,
  Loader2,
  AppWindow,
  Code2,
  MessageSquare,
  Music,
  FileText,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface WindowInfo {
  hwnd: number;
  title: string;
  app_name: string;
  app_display_name: string;
  icon_path: string;
  is_browser: boolean;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface ConnectedApp {
  hwnd: number;
  title: string;
  app_name: string;
  app_display_name: string;
  is_browser: boolean;
  connected_at: string;
}

// ============================================================================
// App Icons & Display Names
// ============================================================================

// Processname -> DisplaynameMap
const PROCESS_DISPLAY_NAMES: Record<string, string> = {
  'chrome.exe': 'Google Chrome',
  'firefox.exe': 'Mozilla Firefox',
  'msedge.exe': 'Microsoft Edge',
  'brave.exe': 'Brave',
  'arc.exe': 'Arc',
  'code.exe': 'VS Code',
  'cursor.exe': 'Cursor',
  'slack.exe': 'Slack',
  'discord.exe': 'Discord',
  'spotify.exe': 'Spotify',
  'notion.exe': 'Notion',
  'obsidian.exe': 'Obsidian',
  'wechat.exe': 'WeChat',
  'weixin.exe': 'WeChat',
  'electron.exe': 'Electron',
  'explorer.exe': 'File Explorer',
};

// willProcessnameConvertforfriendlyDisplayname
function getDisplayName(processName: string): string {
  const lower = processName.toLowerCase();
  if (PROCESS_DISPLAY_NAMES[lower]) {
    return PROCESS_DISPLAY_NAMES[lower];
  }
  // Remove .exe Aftersuffixandfirst letter capitalize
  return processName.replace(/\.exe$/i, '').replace(/^./, c => c.toUpperCase());
}

const APP_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  'Google Chrome': Globe,
  'Mozilla Firefox': Globe,
  'Microsoft Edge': Globe,
  'Brave': Globe,
  'Arc': Globe,
  'VS Code': Code2,
  'Cursor': Code2,
  'Slack': MessageSquare,
  'Discord': MessageSquare,
  'Spotify': Music,
  'Notion': FileText,
  'Obsidian': FileText,
  'WeChat': MessageSquare,
};

function getAppIcon(appDisplayName: string): React.ComponentType<{ className?: string }> {
  return APP_ICONS[appDisplayName] || AppWindow;
}

// ============================================================================
// ConnectorPanel
// ============================================================================

interface ConnectorPanelProps {
  wsRef?: React.RefObject<WebSocket | null>;
  defaultExpanded?: boolean;
  className?: string;
  /** 当Connect的应用List变化时Callback */
  onConnectedAppsChange?: (apps: ConnectedApp[]) => void;
}

// ExportClasstypeprovideOuterpartUsage
export type { ConnectedApp };

export function ConnectorPanel({ 
  wsRef: _wsRef, 
  defaultExpanded = true,
  className,
  onConnectedAppsChange,
}: ConnectorPanelProps) {
  void _wsRef; // Reserved for future WebSocket integration
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [windows, setWindows] = useState<WindowInfo[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [connectedApps, setConnectedApps] = useState<ConnectedApp[]>([]);
  const [loadingHwnd, setLoadingHwnd] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoadingWindows, setIsLoadingWindows] = useState(false);
  
  const dragRef = useRef<HTMLDivElement>(null);
  
  // Save callback ref avoidclosePackageIssue
  const onConnectedAppsChangeRef = useRef(onConnectedAppsChange);
  useEffect(() => { onConnectedAppsChangeRef.current = onConnectedAppsChange; }, [onConnectedAppsChange]);

  // GetallWindow
  // [P1 FIX] Enhanced fetch error handling
  const fetchWindows = useCallback(async () => {
    setIsLoadingWindows(true);
    try {
      const response = await fetch('http://localhost:8080/api/windows');
      if (!response.ok) {
        console.warn(`[ConnectorPanel] fetchWindows failed: ${response.status}`);
        return;
      }
      const data = await response.json();
      if (data.success && Array.isArray(data.windows)) {
        setWindows(data.windows);
      }
    } catch (error) {
      // [P1 FIX] Differentiate network errors from other errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.debug('[ConnectorPanel] Server not reachable for windows');
      } else {
        console.error('[ConnectorPanel] Failed to fetch windows:', error);
      }
    } finally {
      setIsLoadingWindows(false);
    }
  }, []);

  // GetalreadyConnect's Apply
  // [P1 FIX] Enhanced fetch error handling with type guards
  const fetchConnectedApps = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8080/api/hooks/status');
      if (!response.ok) {
        console.warn(`[ConnectorPanel] fetchConnectedApps failed: ${response.status}`);
        return;
      }
      const data = await response.json();
      const apps: ConnectedApp[] = [];

      // [P1 FIX] Type guard for hooks data
      if (!data.hooks || typeof data.hooks !== 'object') {
        return;
      }

      for (const [hookId, state] of Object.entries(data.hooks)) {
        // [P1 FIX] Runtime type validation
        if (!state || typeof state !== 'object') continue;

        const hookState = state as {
          status?: string;
          context?: {
            hwnd?: number;
            active_app?: string;
            active_window?: string;
            app?: string;
            title?: string;
          };
          connected_at?: string;
        };

        if (hookState.status === 'connected' && hookState.context) {
          const appName = hookState.context.active_app || hookState.context.app || '';
          const windowTitle = hookState.context.active_window || hookState.context.title || '';

          apps.push({
            hwnd: typeof hookState.context.hwnd === 'number' ? hookState.context.hwnd : 0,
            title: typeof windowTitle === 'string' ? windowTitle : '',
            app_name: typeof appName === 'string' ? appName : '',
            app_display_name: getDisplayName(typeof appName === 'string' ? appName : ''),
            is_browser: hookId.startsWith('browser'),
            connected_at: hookState.connected_at || new Date().toISOString(),
          });
        }
      }

      setConnectedApps(apps);
      // NotifyParentComponent
      onConnectedAppsChangeRef.current?.(apps);
    } catch (error) {
      // [P1 FIX] Differentiate network errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.debug('[ConnectorPanel] Server not reachable for hooks status');
      } else {
        console.error('[ConnectorPanel] Failed to fetch connected apps:', error);
      }
    }
  }, []);

  // Initialize
  useEffect(() => {
    fetchWindows();
    fetchConnectedApps();
    
    const interval = setInterval(() => {
      fetchWindows();
      fetchConnectedApps();
    }, 3000);
    
    return () => clearInterval(interval);
  }, [fetchWindows, fetchConnectedApps]);

  // ConnecttoWindow
  const connectToWindow = useCallback(async (window: WindowInfo) => {
    setLoadingHwnd(window.hwnd);
    
    try {
      const response = await fetch('http://localhost:8080/api/windows/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hwnd: window.hwnd,
          window_title: window.title,
        }),
      });
      
      if (response.ok) {
        await fetchConnectedApps();
        
        const electronAPI = (globalThis as { electronAPI?: {
          createMultiOverlay?: (hwnd: number, hookType: string, targetTitle: string) => Promise<{ success: boolean }>;
        } }).electronAPI;
        
        if (electronAPI?.createMultiOverlay) {
          const hookType = window.is_browser ? 'browser' : 'desktop';
          await electronAPI.createMultiOverlay(window.hwnd, hookType, window.app_display_name || window.app_name);
        }
      } else {
        console.error('Failed to connect:', await response.text());
      }
    } catch (error) {
      console.error('Failed to connect to window:', error);
    } finally {
      setLoadingHwnd(null);
    }
  }, [fetchConnectedApps]);

  // DisconnectConnect
  const disconnectApp = async (app: ConnectedApp) => {
    setLoadingHwnd(app.hwnd);
    
    try {
      const hookType = app.is_browser ? 'browser' : 'desktop';
      const hookId = `${hookType}_${app.hwnd}`;
      
      const response = await fetch(`http://localhost:8080/api/hooks/disconnect/${hookId}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        await fetchConnectedApps();
        
        const electronAPI = (globalThis as { electronAPI?: {
          destroyMultiOverlay?: (hwnd: number) => Promise<{ success: boolean }>;
        } }).electronAPI;
        
        if (electronAPI?.destroyMultiOverlay) {
          await electronAPI.destroyMultiOverlay(app.hwnd);
        }
      }
    } catch (error) {
      console.error('Failed to disconnect:', error);
    } finally {
      setLoadingHwnd(null);
    }
  };

  // FilterWindow
  const filteredWindows = windows.filter(w => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      w.title.toLowerCase().includes(query) ||
      w.app_display_name.toLowerCase().includes(query)
    );
  });

  // DragBegin（Usage mousedown andnon HTML5 drag API）
  const handleDragStart = useCallback(async (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    
    const electronAPI = (window as { electronAPI?: {
      startDragConnector?: () => Promise<{ success: boolean }>;
    } }).electronAPI;
    
    if (electronAPI?.startDragConnector) {
      try {
        const result = await electronAPI.startDragConnector();
        console.log('[ConnectorPanel] Drag connector started:', result);
        if (!result?.success) {
          console.error('[ConnectorPanel] Failed to start drag connector:', result);
          setIsDragging(false);
        }
      } catch (error) {
        console.error('[ConnectorPanel] Error starting drag connector:', error);
        setIsDragging(false);
      }
    } else {
      console.warn('[ConnectorPanel] electronAPI.startDragConnector not available');
      setIsDragging(false);
    }
  }, []);

  // [Repair #30]Usage ref SavemostNew's  windows State，avoidclosePackageIssue
  const windowsRef = useRef(windows);
  useEffect(() => { windowsRef.current = windows; }, [windows]);

  // DragEnd（UsageGlobal mouseup Listen）
  const handleDragEnd = useCallback(async () => {
    if (!isDragging) return;

    setIsDragging(false);

    const electronAPI = (window as { electronAPI?: {
      endDragConnector?: () => Promise<{ success: boolean; target: { hwnd: number; title: string } | null }>;
    } }).electronAPI;

    if (electronAPI?.endDragConnector) {
      try {
        const result = await electronAPI.endDragConnector();
        console.log('[ConnectorPanel] Drag ended, result:', result);

        if (result?.target) {
        // firstRefreshWindowList
        await fetchWindows();

        // [Repair #30]Usage ref GetmostNew's WindowList
        const currentWindows = windowsRef.current;
        const targetWindow = currentWindows.find(w => w.hwnd === result.target!.hwnd);
        if (targetWindow) {
          console.log('[ConnectorPanel] Connecting to:', targetWindow);
          await connectToWindow(targetWindow);
        } else {
          // IfWindowListinsideno，directlyuseReturn's InfoCreateConnect
          console.log('[ConnectorPanel] Window not in list, creating connection with:', result.target);
          const fakeWindow: WindowInfo = {
            hwnd: result.target.hwnd,
            title: result.target.title,
            app_name: '',
            app_display_name: result.target.title.split(' - ').pop() || result.target.title,
            icon_path: '',
            is_browser: false,
            x: 0, y: 0, width: 0, height: 0,
          };
          await connectToWindow(fakeWindow);
        }
      } else {
        console.log('[ConnectorPanel] Drag ended but no target window');
      }
      } catch (error) {
        console.error('[ConnectorPanel] Error ending drag connector:', error);
      }
    } else {
      console.warn('[ConnectorPanel] electronAPI.endDragConnector not available');
    }
  }, [isDragging, fetchWindows, connectToWindow]);

  // ListenDragAutoCompleteEvent（frommainProcessDetectiontoMouseRelease）
  // [Repair #31]Optimization Effect Dependency，Usage ref avoidovermultipleheavyNewSubscribe
  useEffect(() => {
    const electronAPI = (window as { electronAPI?: {
      onDragConnectorComplete?: (callback: (target: { hwnd: number; title: string }) => void) => () => void;
    } }).electronAPI;

    if (!electronAPI?.onDragConnectorComplete) {
      console.warn('[ConnectorPanel] electronAPI.onDragConnectorComplete not available');
      return;
    }
    
    console.log('[ConnectorPanel] Setting up drag connector complete listener');

    const cleanup = electronAPI.onDragConnectorComplete(async (target) => {
      console.log('[ConnectorPanel] Drag complete from main process:', target);
      setIsDragging(false);

      if (target) {
        // firstRefreshWindowList
        await fetchWindows();

        // [Repair #31]Usage ref GetmostNew's WindowList
        const currentWindows = windowsRef.current;
        const targetWindow = currentWindows.find(w => w.hwnd === target.hwnd);
        if (targetWindow) {
          console.log('[ConnectorPanel] Found window in list, connecting:', targetWindow);
          await connectToWindow(targetWindow);
        } else {
          // IfWindowListinsideno，directlyuseReturn's InfoCreateConnect
          console.log('[ConnectorPanel] Window not in list, creating connection with:', target);
          const fakeWindow: WindowInfo = {
            hwnd: target.hwnd,
            title: target.title,
            app_name: '',
            app_display_name: target.title.split(' - ').pop() || target.title,
            icon_path: '',
            is_browser: false,
            x: 0, y: 0, width: 0, height: 0,
          };
          await connectToWindow(fakeWindow);
        }
      }
    });

    return cleanup;
  }, [fetchWindows, connectToWindow]);

  // backup：Global mouseup Listen（asfor fallback）
  // [Repair #32]Usage ref avoid isDragging closePackageIssue，andensureDedupe
  const isDraggingRef = useRef(isDragging);
  useEffect(() => { isDraggingRef.current = isDragging; }, [isDragging]);
  const mouseUpHandledRef = useRef(false);

  useEffect(() => {
    if (!isDragging) {
      mouseUpHandledRef.current = false;
      return;
    }

    const handleGlobalMouseUp = () => {
      // [Repair #32]Dedupe：ensureonlyExecuteonce
      if (mouseUpHandledRef.current) return;
      mouseUpHandledRef.current = true;

      // DelayedonePointExecute，let main process have chancefirstHandle
      setTimeout(() => {
        if (isDraggingRef.current) {
          console.log('[ConnectorPanel] Fallback mouseup triggered');
          handleDragEnd();
        }
      }, 100);
    };

    document.addEventListener('mouseup', handleGlobalMouseUp);

    return () => {
      document.removeEventListener('mouseup', handleGlobalMouseUp);
    };
  }, [isDragging, handleDragEnd]);

  return (
    <Collapsible 
      open={isExpanded} 
      onOpenChange={setIsExpanded}
      className={cn('', className)}
    >
      {/* Header */}
      <CollapsibleTrigger asChild>
        <button className="w-full flex items-center gap-2 px-3 py-2 text-neutral-400 hover:text-neutral-200 transition-colors">
          <Plug className="w-4 h-4" />
          <span className="text-xs font-medium uppercase tracking-wider flex-1 text-left">
            App Connector
          </span>
          {connectedApps.length > 0 && (
            <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded-full">
              {connectedApps.length}
            </span>
          )}
          <motion.div
            animate={{ rotate: isExpanded ? 0 : -90 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-4 h-4" />
          </motion.div>
        </button>
      </CollapsibleTrigger>

      <CollapsibleContent>
        <div className="px-2 pb-3 space-y-3">
          
          {/* 已Connect的应用 - Premium 视觉Sync */}
          {connectedApps.length > 0 && (
            <div className="space-y-2">
              <p className="text-[10px] text-neutral-500 uppercase tracking-wider px-1">
                Connected
              </p>
              {connectedApps.map((app, index) => {
                const Icon = getAppIcon(app.app_display_name);
                return (
                  <motion.div
                    key={app.hwnd}
                    initial={{ opacity: 0, scale: 0.9, y: -8 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ 
                      type: 'spring', 
                      stiffness: 400, 
                      damping: 25,
                      delay: index * 0.05 
                    }}
                    className="relative group"
                  >
                    {/* 扫描线Effect（入场时） */}
                    <motion.div
                      initial={{ scaleX: 0, opacity: 1 }}
                      animate={{ scaleX: 1, opacity: 0 }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent rounded-lg origin-left"
                    />
                    
                    {/* 四角 L 标记 */}
                    <div className="absolute top-0 left-0 w-2 h-2 border-l-2 border-t-2 border-emerald-500/60 rounded-tl" />
                    <div className="absolute top-0 right-0 w-2 h-2 border-r-2 border-t-2 border-emerald-500/60 rounded-tr" />
                    <div className="absolute bottom-0 left-0 w-2 h-2 border-l-2 border-b-2 border-emerald-500/60 rounded-bl" />
                    <div className="absolute bottom-0 right-0 w-2 h-2 border-r-2 border-b-2 border-emerald-500/60 rounded-br" />
                    
                    {/* 主卡片 */}
                    <div className="relative flex items-center gap-2.5 px-3 py-2 rounded-lg border border-emerald-500/20 bg-emerald-500/5 backdrop-blur-sm overflow-hidden">
                      {/* Background光效 */}
                      <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 via-transparent to-emerald-500/5 opacity-50" />
                      
                      {/* State指示器（带脉冲） */}
                      <div className="relative flex-shrink-0">
                        <motion.div
                          animate={{ 
                            boxShadow: [
                              '0 0 0 0 rgba(16, 185, 129, 0.4)',
                              '0 0 0 4px rgba(16, 185, 129, 0)',
                            ]
                          }}
                          transition={{ 
                            duration: 2, 
                            repeat: Infinity,
                            ease: 'easeOut'
                          }}
                          className="absolute inset-0 rounded-lg"
                        />
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                          <Icon className="w-4 h-4 text-white" />
                        </div>
                      </div>
                      
                      {/* 应用Info */}
                      <div className="flex-1 min-w-0 relative z-10">
                        <div className="flex items-center gap-1.5">
                          <motion.div
                            animate={{ opacity: [1, 0.6, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                            className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50"
                          />
                          <p className="text-xs font-medium text-emerald-300 truncate">
                            {app.app_display_name}
                          </p>
                        </div>
                        <p className="text-[10px] text-neutral-500 truncate mt-0.5">
                          {app.title}
                        </p>
                      </div>
                      
                      {/* Disconnect按钮 */}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => disconnectApp(app)}
                        disabled={loadingHwnd === app.hwnd}
                        className="relative z-10 h-7 w-7 p-0 text-neutral-500 hover:text-red-400 hover:bg-red-500/10 rounded-md transition-colors"
                      >
                        {loadingHwnd === app.hwnd ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Unplug className="w-3.5 h-3.5" />
                        )}
                      </Button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}

          {/* 分隔线 */}
          <div className="flex items-center gap-2 text-neutral-600">
            <div className="flex-1 h-px bg-neutral-800" />
            <span className="text-[10px]">Connect to App</span>
            <div className="flex-1 h-px bg-neutral-800" />
          </div>

          {/* Path B: 拖拽Connect器 */}
          <div className="relative">
            <motion.div
              ref={dragRef}
              onMouseDown={handleDragStart}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.95 }}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg border cursor-grab active:cursor-grabbing transition-colors select-none",
                isDragging
                  ? "border-emerald-500/50 bg-emerald-500/10"
                  : "border-neutral-800 bg-neutral-900/50 hover:border-neutral-700"
              )}
            >
              <div className={cn(
                "flex items-center justify-center w-8 h-8 rounded-lg border transition-colors",
                isDragging 
                  ? "bg-gradient-to-br from-emerald-500/30 to-emerald-600/20 border-emerald-500/50"
                  : "bg-gradient-to-br from-blue-500/20 to-purple-500/20 border-blue-500/30"
              )}>
                <Crosshair className={cn(
                  "w-4 h-4 transition-colors",
                  isDragging ? "text-emerald-400" : "text-blue-400"
                )} />
              </div>
              <div className="flex-1">
                <p className="text-xs text-neutral-300">
                  {isDragging ? "Release on target window" : "Drag to connect"}
                </p>
                <p className="text-[10px] text-neutral-500">
                  {isDragging ? "Move cursor to the window you want" : "Hold and drag to any window"}
                </p>
              </div>
              <GripVertical className={cn(
                "w-4 h-4 transition-colors",
                isDragging ? "text-emerald-500" : "text-neutral-600"
              )} />
            </motion.div>
            
            {isDragging && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="absolute -inset-1 rounded-xl border-2 border-dashed border-emerald-500/40 bg-emerald-500/5 pointer-events-none"
              />
            )}
          </div>

          {/* Path A: WindowListSelect */}
          <div className="space-y-2">
            {/* Search框 */}
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-500" />
              <Input
                type="text"
                placeholder="Search windows..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={fetchWindows}
                className="h-8 pl-8 text-xs bg-neutral-900 border-neutral-800 focus:border-neutral-700"
              />
              {isLoadingWindows && (
                <Loader2 className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-500 animate-spin" />
              )}
            </div>

            {/* WindowList */}
            <ScrollArea className="h-[280px]">
              <div className="space-y-1 pr-4">
                <AnimatePresence mode="popLayout">
                  {filteredWindows.length === 0 ? (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-xs text-neutral-500 text-center py-4"
                    >
                      {searchQuery ? 'No windows found' : 'Click to load windows'}
                    </motion.p>
                  ) : (
                    filteredWindows.map((window) => {
                      const Icon = getAppIcon(window.app_display_name);
                      const isConnected = connectedApps.some(a => a.hwnd === window.hwnd);
                      const isLoading = loadingHwnd === window.hwnd;

                      return (
                        <motion.div
                          key={window.hwnd}
                          layout
                          initial={{ opacity: 0, y: -4 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -4 }}
                          className={cn(
                            "flex items-center gap-2 px-2 py-1.5 rounded-lg border transition-colors cursor-pointer",
                            isConnected
                              ? "border-emerald-500/30 bg-emerald-500/5"
                              : "border-transparent hover:border-neutral-800 hover:bg-neutral-900/50"
                          )}
                          onClick={() => !isConnected && !isLoading && connectToWindow(window)}
                        >
                          <Icon className={cn(
                            "w-4 h-4 flex-shrink-0",
                            isConnected ? "text-emerald-400" : "text-neutral-500"
                          )} />
                          
                          <div className="flex-1 min-w-0">
                            <p className={cn(
                              "text-xs truncate",
                              isConnected ? "text-emerald-300" : "text-neutral-300"
                            )}>
                              {window.app_display_name}
                            </p>
                            <p className="text-[10px] text-neutral-500 truncate">
                              {window.title}
                            </p>
                          </div>

                          {isConnected ? (
                            <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                          ) : isLoading ? (
                            <Loader2 className="w-4 h-4 animate-spin text-neutral-500 flex-shrink-0" />
                          ) : (
                            <Plug className="w-4 h-4 text-neutral-600 flex-shrink-0" />
                          )}
                        </motion.div>
                      );
                    })
                  )}
                </AnimatePresence>
              </div>
            </ScrollArea>
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}

export default ConnectorPanel;
