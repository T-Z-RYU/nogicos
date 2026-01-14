/**
 * AppDetailPanel - Right侧应用详情面板
 * 
 * 当User在 Canvas Up聚焦一个 App 时，Display该 App 的详细Info和交互记录
 */

import { memo, useMemo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Globe,
  Code2,
  FileText,
  AppWindow,
  X,
  ExternalLink,
  Unplug,
  Eye,
  Pencil,
  Check,
  Loader2,
  AlertCircle,
  Clock,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface ConnectedApp {
  hwnd: number;
  title: string;
  app_name: string;
  app_display_name: string;
  is_browser: boolean;
  connected_at: string;
}

interface ActionRecord {
  id: string;
  timestamp: Date;
  type: 'read' | 'write' | 'navigate' | 'click' | 'type';
  status: 'pending' | 'active' | 'done' | 'error';
  label: string;
  detail?: string;
}

interface AppDetailPanelProps {
  focusedApp: ConnectedApp | null;
  actionRecords?: ActionRecord[];
  onClose: () => void;
  onDisconnect?: (hwnd: number) => void;
  onFocusWindow?: (hwnd: number) => void;
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const SPRING = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
};

// App icon mapping
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
};

function getAppIcon(appName: string) {
  if (APP_ICONS[appName]) return APP_ICONS[appName];
  for (const [key, icon] of Object.entries(APP_ICONS)) {
    if (appName.toLowerCase().includes(key.toLowerCase())) return icon;
  }
  return AppWindow;
}

// Format relative time
function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

// Format timestamp
function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

// ============================================================================
// Action Record Item
// ============================================================================

const ActionRecordItem = memo(function ActionRecordItem({ record }: { record: ActionRecord }) {
  const getStatusIcon = () => {
    switch (record.status) {
      case 'done': return <Check className="w-3 h-3 text-emerald-400" />;
      case 'active': return <Loader2 className="w-3 h-3 text-white animate-spin" />;
      case 'error': return <AlertCircle className="w-3 h-3 text-red-400" />;
      default: return <Clock className="w-3 h-3 text-white/30" />;
    }
  };

  const getTypeIcon = () => {
    switch (record.type) {
      case 'read': return <Eye className="w-3 h-3" />;
      case 'write': return <Pencil className="w-3 h-3" />;
      case 'navigate': return <Globe className="w-3 h-3" />;
      case 'click': return <Zap className="w-3 h-3" />;
      case 'type': return <Code2 className="w-3 h-3" />;
      default: return <Zap className="w-3 h-3" />;
    }
  };

  return (
    <motion.div
      className={cn(
        "flex items-start gap-2.5 p-2.5 rounded-lg transition-colors",
        record.status === 'active' && "bg-white/5",
        record.status === 'error' && "bg-red-500/5",
      )}
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={SPRING.snappy}
    >
      {/* Timestamp */}
      <span className="text-[10px] text-white/30 font-mono w-16 flex-shrink-0 pt-0.5">
        {formatTime(record.timestamp)}
      </span>

      {/* Status icon */}
      <div className={cn(
        "w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0",
        record.status === 'done' && "bg-emerald-500/10",
        record.status === 'active' && "bg-white/10",
        record.status === 'error' && "bg-red-500/10",
        record.status === 'pending' && "bg-white/5",
      )}>
        {getStatusIcon()}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className="text-white/40">{getTypeIcon()}</span>
          <span className={cn(
            "text-xs",
            record.status === 'done' ? "text-white/70" :
            record.status === 'active' ? "text-white" :
            record.status === 'error' ? "text-red-400" :
            "text-white/40"
          )}>
            {record.label}
          </span>
        </div>
        {record.detail && (
          <p className="text-[10px] text-white/30 mt-0.5 truncate">
            {record.detail}
          </p>
        )}
      </div>
    </motion.div>
  );
});

// ============================================================================
// Empty State
// ============================================================================

const EmptyState = memo(function EmptyState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center px-6 py-12">
      <motion.div
        className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mb-4"
        animate={{ 
          scale: [1, 1.02, 1],
          opacity: [0.5, 0.7, 0.5],
        }}
        transition={{ duration: 3, repeat: Infinity }}
      >
        <AppWindow className="w-6 h-6 text-white/30" />
      </motion.div>
      <h3 className="text-sm font-medium text-white/60 mb-1">
        Select an app
      </h3>
      <p className="text-xs text-white/30 max-w-[180px]">
        Click an app node on the Canvas to view details
      </p>
    </div>
  );
});

// ============================================================================
// Main Component
// ============================================================================

export const AppDetailPanel = memo(function AppDetailPanel({
  focusedApp,
  actionRecords = [],
  onClose,
  onDisconnect,
  onFocusWindow,
  className,
}: AppDetailPanelProps) {
  const Icon = focusedApp ? getAppIcon(focusedApp.app_display_name) : AppWindow;

  // Filter records for current app (in practice, should receive pre-filtered records)
  const filteredRecords = useMemo(() => {
    return actionRecords.slice(-20); // Show last 20 records
  }, [actionRecords]);

  return (
    <motion.div
      className={cn(
        "w-[280px] h-full flex flex-col",
        "bg-[#0a0a0a] border-l border-white/[0.06]",
        className
      )}
      initial={{ x: 20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 20, opacity: 0 }}
      transition={SPRING.gentle}
    >
      <AnimatePresence mode="wait">
        {focusedApp ? (
          <motion.div
            key={focusedApp.hwnd}
            className="flex flex-col h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Header */}
            <div className="flex items-center gap-3 px-4 py-4 border-b border-white/[0.06]">
              <motion.div
                className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center"
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={SPRING.snappy}
              >
                <Icon className="w-5 h-5 text-white/70" />
              </motion.div>
              <div className="flex-1 min-w-0">
                <h2 className="text-sm font-medium text-white truncate">
                  {focusedApp.app_display_name}
                </h2>
                <p className="text-[10px] text-white/40 truncate">
                  {focusedApp.title}
                </p>
              </div>
              <button
                onClick={onClose}
                className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/40 hover:text-white/70 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Info Section */}
            <div className="px-4 py-3 border-b border-white/[0.06]">
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-white/40">Status</span>
                  <span className="flex items-center gap-1.5 text-emerald-400">
                    <motion.span
                      className="w-1.5 h-1.5 rounded-full bg-emerald-400"
                      animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                    Connected
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-white/40">Connected at</span>
                  <span className="text-white/60">
                    {formatRelativeTime(focusedApp.connected_at)}
                  </span>
                </div>
                {focusedApp.is_browser && (
                  <div className="flex items-center justify-between">
                    <span className="text-white/40">Class型</span>
                    <span className="flex items-center gap-1 text-white/60">
                      <Globe className="w-3 h-3" /> 浏览器
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Action Records */}
            <div className="flex-1 flex flex-col min-h-0">
              <div className="px-4 py-2.5 border-b border-white/[0.06]">
                <h3 className="text-xs font-medium text-white/60">交互记录</h3>
              </div>
              <div className="flex-1 overflow-y-auto px-2 py-2">
                {filteredRecords.length > 0 ? (
                  <div className="space-y-1">
                    {filteredRecords.map(record => (
                      <ActionRecordItem key={record.id} record={record} />
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full text-xs text-white/30">
                    暂无交互记录
                  </div>
                )}
              </div>
            </div>

            {/* Footer Actions */}
            <div className="px-4 py-3 border-t border-white/[0.06]">
              <div className="flex gap-2">
                <button
                  onClick={() => onFocusWindow?.(focusedApp.hwnd)}
                  className="flex-1 flex items-center justify-center gap-1.5 text-xs px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition-colors"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  聚焦Window
                </button>
                <button
                  onClick={() => onDisconnect?.(focusedApp.hwnd)}
                  className="flex items-center justify-center gap-1.5 text-xs px-3 py-2 rounded-lg text-red-400/70 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                >
                  <Unplug className="w-3.5 h-3.5" />
                  Disconnect
                </button>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="empty"
            className="flex-1 flex flex-col"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <EmptyState />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});

export default AppDetailPanel;
