import { Minus, Square, X, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TitleBarProps {
  title?: string;
  onMinimize?: () => void;
  onMaximize?: () => void;
  onClose?: () => void;
  onReconnect?: () => void;
}

export function TitleBar({ 
  title = 'NogicOS', 
  onMinimize, 
  onMaximize, 
  onClose,
  onReconnect,
}: TitleBarProps) {
  // Determine connection status from title
  const isConnected = title === 'NogicOS';
  const isConnecting = title.includes('Connecting');
  const isReconnecting = title.includes('Reconnecting');
  const isDisconnected = title.includes('Disconnected');

  // Call Electron IPC via preload script
  const handleMinimize = () => {
    if (onMinimize) onMinimize();
    else window.electronAPI?.minimize?.();
  };

  const handleMaximize = () => {
    if (onMaximize) onMaximize();
    else window.electronAPI?.maximize?.();
  };

  const handleClose = () => {
    if (onClose) onClose();
    else window.electronAPI?.close?.();
  };

  // Get status indicator (reserved for future use)
  const _getStatusIndicator = () => {
    if (isConnected) {
      return (
        <>
          <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
          <span className="text-xs text-neutral-500">Ready</span>
        </>
      );
    }
    if (isConnecting || isReconnecting) {
      return (
        <>
          <RefreshCw className="w-3 h-3 text-neutral-400 animate-spin" />
          <span className="text-xs text-neutral-400">
            {isReconnecting ? 'Reconnecting' : 'Connecting'}
          </span>
        </>
      );
    }
    if (isDisconnected) {
      return (
        <>
          <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
          <span className="text-xs text-red-400">Offline</span>
          {onReconnect && (
            <button
              onClick={onReconnect}
              className="ml-1 px-2 py-0.5 text-[10px] bg-neutral-800 hover:bg-neutral-700 rounded text-neutral-400 hover:text-white transition-colors"
            >
              Retry
            </button>
          )}
        </>
      );
    }
    return null;
  };
  void _getStatusIndicator; // Suppress unused warning - reserved for future use

  return (
    <header className="electron-titlebar h-11 flex items-center justify-between px-4 bg-black border-b border-neutral-900">
      {/* Logo & Title */}
      <div className="flex items-center gap-2.5">
        <div className={cn(
          "w-5 h-5 rounded-md flex items-center justify-center transition-colors",
          isConnected 
            ? "bg-white" 
            : "bg-neutral-800"
        )}>
          <span className={cn(
            "text-[10px] font-bold",
            isConnected ? "text-black" : "text-neutral-500"
          )}>N</span>
        </div>
        <span className="text-sm font-medium text-neutral-400">
          NogicOS
        </span>
      </div>

      {/* Window Controls */}
      <div className="flex items-center gap-0.5">
        <button
          onClick={handleMinimize}
          className="w-8 h-8 flex items-center justify-center rounded-md text-neutral-500 hover:bg-neutral-900 hover:text-neutral-300 transition-colors"
        >
          <Minus className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={handleMaximize}
          className="w-8 h-8 flex items-center justify-center rounded-md text-neutral-500 hover:bg-neutral-900 hover:text-neutral-300 transition-colors"
        >
          <Square className="w-3 h-3" />
        </button>
        <button
          onClick={handleClose}
          className="w-8 h-8 flex items-center justify-center rounded-md text-neutral-500 hover:bg-red-500/90 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}

// Type declaration for Electron preload API
declare global {
  interface Window {
    electronAPI?: {
      minimize: () => void;
      maximize: () => void;
      close: () => void;
      platform: string;
      isElectron: boolean;
      onNewSession: (callback: () => void) => () => void;
      onToggleCommandPalette: (callback: () => void) => () => void;
      toggleCommandPalette: () => void;
    };
  }
}
