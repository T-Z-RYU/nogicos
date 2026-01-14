/**
 * Error State Display Component
 * Phase 7.7: Error State UI
 */

import { motion } from 'motion/react';
import { RefreshCw, XCircle, AlertTriangle, StopCircle, WifiOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { AgentErrorType, AgentError } from '@/types/agent';

// Error type configuration
interface ErrorConfig {
  icon: React.ReactNode;
  title: string;
  message: string;
  action?: {
    label: string;
    handler: string;
  };
  color: string;
}

const ERROR_TYPES: Record<AgentErrorType, ErrorConfig> = {
  api_timeout: {
    icon: <RefreshCw className="h-5 w-5 animate-spin" />,
    title: 'API Timeout',
    message: 'Auto-retrying...',
    action: undefined,
    color: 'yellow',
  },
  window_lost: {
    icon: <XCircle className="h-5 w-5" />,
    title: 'Target Window Lost',
    message: 'Please reopen the window',
    action: { label: 'Reconnect', handler: 'reconnect' },
    color: 'red',
  },
  tool_failed: {
    icon: <AlertTriangle className="h-5 w-5" />,
    title: 'Operation Failed',
    message: 'AI is trying alternative methods',
    action: undefined,
    color: 'orange',
  },
  emergency_stop: {
    icon: <StopCircle className="h-5 w-5" />,
    title: 'Emergency Stop',
    message: 'Task saved, can be resumed',
    action: { label: 'Resume Task', handler: 'resume' },
    color: 'red',
  },
  connection_error: {
    icon: <WifiOff className="h-5 w-5" />,
    title: 'Connection Lost',
    message: 'Attempting to reconnect...',
    action: { label: 'Manual Reconnect', handler: 'reconnect' },
    color: 'yellow',
  },
  unknown: {
    icon: <AlertTriangle className="h-5 w-5" />,
    title: 'Unknown Error',
    message: 'An unexpected error occurred',
    action: { label: 'Retry', handler: 'retry' },
    color: 'red',
  },
};

const colorClasses: Record<string, { bg: string; border: string; text: string }> = {
  yellow: {
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/30',
    text: 'text-yellow-400',
  },
  red: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    text: 'text-red-400',
  },
  orange: {
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/30',
    text: 'text-orange-400',
  },
};

interface ErrorDisplayProps {
  error: AgentError;
  onAction?: (handler: string) => void;
  className?: string;
  compact?: boolean;
}

export function ErrorDisplay({
  error,
  onAction,
  className,
  compact = false,
}: ErrorDisplayProps) {
  const config = ERROR_TYPES[error.type] || ERROR_TYPES.unknown;
  const colors = colorClasses[config.color];

  return (
    <motion.div
      className={cn(
        'rounded-lg border',
        colors.bg,
        colors.border,
        compact ? 'px-3 py-2' : 'p-4',
        className
      )}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
    >
      <div className={cn('flex items-start gap-3', compact && 'items-center')}>
        {/* Icon */}
        <div className={cn(colors.text, compact && 'scale-90')}>
          {config.icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h4 className={cn('font-medium text-white', compact && 'text-sm')}>
            {config.title}
          </h4>
          {!compact && (
            <p className="mt-0.5 text-sm text-white/60">{config.message}</p>
          )}
          {error.detail && !compact && (
            <p className="mt-1 text-xs text-white/40 font-mono truncate">
              {error.detail}
            </p>
          )}
        </div>

        {/* Action button */}
        {config.action && onAction && (
          <Button
            size={compact ? 'sm' : 'default'}
            variant="ghost"
            className={cn(
              'shrink-0',
              colors.text,
              'hover:bg-white/10 hover:text-white'
            )}
            onClick={() => onAction(config.action!.handler)}
          >
            {config.action.label}
          </Button>
        )}
      </div>
    </motion.div>
  );
}

// Compact error hint (for message list)
export function InlineError({
  message,
  recoverable = false,
  onRetry,
}: {
  message: string;
  recoverable?: boolean;
  onRetry?: () => void;
}) {
  return (
    <div className="flex items-center gap-2 rounded-md bg-red-500/10 px-3 py-2 text-xs text-red-400">
      <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
      <span className="flex-1">{message}</span>
      {recoverable && onRetry && (
        <button
          onClick={onRetry}
          className="rounded px-2 py-0.5 text-white/70 transition-colors hover:bg-white/10 hover:text-white"
        >
          Retry
        </button>
      )}
    </div>
  );
}
