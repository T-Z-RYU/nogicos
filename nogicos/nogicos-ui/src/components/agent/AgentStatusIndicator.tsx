/**
 * Agent Status Indicator
 * Phase 7.3: Rich status indicator
 */

import { motion, type TargetAndTransition } from 'motion/react';
import { cn } from '@/lib/utils';
import type { AgentStatus, StatusDisplay, AnimationType } from '@/types/agent';

// Status config mapping
const STATUS_CONFIG: Record<AgentStatus, StatusDisplay> = {
  idle: { icon: '○', label: 'Ready', color: 'gray', animation: null },
  queued: { icon: '◷', label: 'Queued...', color: 'yellow', animation: 'pulse' },
  thinking: { icon: '◐', label: 'AI Thinking...', color: 'blue', animation: 'spin' },
  planning: { icon: '📋', label: 'Planning...', color: 'blue', animation: 'pulse' },
  executing: { icon: '▶', label: 'Executing...', color: 'green', animation: 'pulse' },
  verifying: { icon: '🔍', label: 'Verifying...', color: 'cyan', animation: 'scan' },
  waiting: { icon: '◷', label: 'Waiting for response...', color: 'yellow', animation: 'blink' },
  confirm: { icon: '⚠️', label: 'Confirmation Required', color: 'orange', animation: 'bounce' },
  paused: { icon: '⏸', label: 'Paused', color: 'gray', animation: null },
  recovering: { icon: '🔄', label: 'Recovering...', color: 'yellow', animation: 'spin' },
  completed: { icon: '✓', label: 'Completed', color: 'green', animation: 'check' },
  failed: { icon: '✕', label: 'Failed', color: 'red', animation: 'shake' },
};

// Animation variants
const animations: Record<AnimationType, TargetAndTransition> = {
  pulse: {
    scale: [1, 1.1, 1],
    opacity: [1, 0.8, 1],
    transition: { duration: 1.5, repeat: Infinity, ease: 'easeInOut' },
  },
  spin: {
    rotate: 360,
    transition: { duration: 1, repeat: Infinity, ease: 'linear' },
  },
  bounce: {
    y: [0, -4, 0],
    transition: { duration: 0.6, repeat: Infinity, ease: 'easeInOut' },
  },
  blink: {
    opacity: [1, 0.4, 1],
    transition: { duration: 0.8, repeat: Infinity, ease: 'easeInOut' },
  },
  scan: {
    scaleX: [1, 1.2, 1],
    transition: { duration: 0.5, repeat: Infinity, ease: 'easeInOut' },
  },
  shake: {
    x: [-2, 2, -2, 2, 0],
    transition: { duration: 0.4, repeat: Infinity, repeatDelay: 1 },
  },
  check: {
    scale: [0.8, 1.2, 1],
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

// Color to Tailwind class mapping
const colorClasses: Record<string, string> = {
  gray: 'text-gray-400',
  yellow: 'text-yellow-400',
  blue: 'text-blue-400',
  green: 'text-emerald-400',
  cyan: 'text-cyan-400',
  orange: 'text-orange-400',
  red: 'text-red-400',
};

const bgColorClasses: Record<string, string> = {
  gray: 'bg-gray-400/10',
  yellow: 'bg-yellow-400/10',
  blue: 'bg-blue-400/10',
  green: 'bg-emerald-400/10',
  cyan: 'bg-cyan-400/10',
  orange: 'bg-orange-400/10',
  red: 'bg-red-400/10',
};

interface AgentStatusIndicatorProps {
  status: AgentStatus;
  detail?: string;
  compact?: boolean;
  className?: string;
}

export function AgentStatusIndicator({
  status,
  detail,
  compact = false,
  className,
}: AgentStatusIndicatorProps) {
  const config = STATUS_CONFIG[status];

  return (
    <motion.div
      className={cn(
        'flex items-center gap-2 rounded-lg px-3 py-2',
        bgColorClasses[config.color],
        colorClasses[config.color],
        compact && 'px-2 py-1 text-sm',
        className
      )}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      {/* Status icon */}
      <motion.span
        className="text-lg"
        animate={config.animation ? animations[config.animation] : undefined}
      >
        {config.icon}
      </motion.span>

      {/* Status label */}
      <span className="font-medium">{config.label}</span>

      {/* Detail info */}
      {detail && !compact && (
        <span className="ml-2 text-xs opacity-70">{detail}</span>
      )}
    </motion.div>
  );
}

// ExportConfigprovideOtherComponentUsage
// eslint-disable-next-line react-refresh/only-export-components -- these constants are used by other components
export { STATUS_CONFIG, animations };
