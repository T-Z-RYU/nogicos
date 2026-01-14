/**
 * Sensitive Action Confirmation Dialog
 * Phase 7.4: Sensitive action confirmation (redesigned)
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion } from 'motion/react';
import { AlertTriangle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';
import type { SensitiveAction } from '@/types/sensitive-action';
import { RISK_COLORS, RISK_LABELS } from '@/types/sensitive-action';

interface SensitiveActionDialogProps {
  action: SensitiveAction | null;
  onConfirm: (actionId: string) => void;
  onCancel: (actionId: string) => void;
  open?: boolean;
}

export function SensitiveActionDialog({
  action,
  onConfirm,
  onCancel,
  open = true,
}: SensitiveActionDialogProps) {
  const [countdown, setCountdown] = useState<number>(15);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const prevActionIdRef = useRef<string | undefined>(undefined);

  // Countdown logic - includes reset and decrement
  useEffect(() => {
    if (!action || !open) return;

    // Reset state when action changes
    if (action.id !== prevActionIdRef.current) {
      prevActionIdRef.current = action.id;
      /* eslint-disable react-hooks/set-state-in-effect -- intentional: reset state when action changes */
      setCountdown(action.timeout);
      setDetailsOpen(false);
      /* eslint-enable react-hooks/set-state-in-effect */
    }

    const timer = setInterval(() => {
      setCountdown((c) => {
        if (c <= 1) {
          onCancel(action.id);
          return 0;
        }
        return c - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [action, open, onCancel]);

  const handleConfirm = useCallback(() => {
    if (action) {
      onConfirm(action.id);
    }
  }, [action, onConfirm]);

  const handleCancel = useCallback(() => {
    if (action) {
      onCancel(action.id);
    }
  }, [action, onCancel]);

  if (!action) return null;

  const riskColor = RISK_COLORS[action.risk];
  const riskLabel = RISK_LABELS[action.risk];

  return (
    <Dialog open={open}>
      <DialogContent
        className="max-w-lg border-white/10 bg-zinc-900/95 backdrop-blur-xl"
        onEscapeKeyDown={handleCancel}
      >
        <DialogHeader className="pb-2">
          <div className="flex items-center gap-3">
            <motion.div
              className="rounded-full p-2"
              style={{ backgroundColor: `${riskColor}20` }}
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <AlertTriangle className="h-5 w-5" style={{ color: riskColor }} />
            </motion.div>
            <div>
              <DialogTitle className="text-white">Confirm Action</DialogTitle>
              <span
                className="text-xs font-medium"
                style={{ color: riskColor }}
              >
                {riskLabel}
              </span>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Screenshot preview + click position indicator */}
          {action.screenshot && (
            <div className="relative overflow-hidden rounded-lg border border-white/10">
              <img
                src={action.screenshot}
                alt="Action preview"
                className="w-full object-contain"
                style={{ maxHeight: '200px' }}
              />
              {action.coordinates && (
                <ClickIndicator
                  x={action.coordinates.x}
                  y={action.coordinates.y}
                />
              )}
            </div>
          )}

          {/* Human-readable description */}
          <div className="rounded-lg bg-white/5 p-4">
            <p className="text-sm text-white/90">
              AI will perform action in{' '}
              <strong className="text-emerald-400">
                {action.windowName || 'Unknown window'}
              </strong>
              <span className="ml-1">{action.humanReadable}</span>
            </p>

            {/* Action impact description */}
            {action.impact && (
              <div className="mt-3 flex items-start gap-2 rounded-md bg-yellow-500/10 p-2 text-xs text-yellow-400">
                <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>{action.impact}</span>
              </div>
            )}
          </div>

          {/* Technical details (collapsible) */}
          <Collapsible open={detailsOpen} onOpenChange={setDetailsOpen}>
            <CollapsibleTrigger className="flex w-full items-center justify-between rounded-md px-3 py-2 text-xs text-white/50 transition-colors hover:bg-white/5 hover:text-white/70">
              <span>View technical details</span>
              {detailsOpen ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="mt-2 rounded-md bg-zinc-800 p-3">
                <code className="block whitespace-pre-wrap break-all text-xs text-white/60">
                  {action.toolName}({JSON.stringify(action.params, null, 2)})
                </code>
              </div>
            </CollapsibleContent>
          </Collapsible>
        </div>

        <DialogFooter className="flex gap-2 sm:gap-2">
          <Button
            variant="outline"
            onClick={handleCancel}
            className="flex-1 border-white/10 bg-white/5 text-white/70 hover:bg-white/10 hover:text-white"
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            className="flex-1"
            style={{
              backgroundColor: riskColor,
              color: action.risk === 'low' ? '#000' : '#fff',
            }}
          >
            Confirm
            <CountdownBadge countdown={countdown} total={action.timeout} />
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Click position indicator
function ClickIndicator({ x, y }: { x: number; y: number }) {
  return (
    <motion.div
      className="pointer-events-none absolute"
      style={{
        left: `${x}%`,
        top: `${y}%`,
        transform: 'translate(-50%, -50%)',
      }}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
    >
      {/* Outer ripple */}
      <motion.div
        className="absolute h-10 w-10 rounded-full border-2 border-red-500"
        style={{ transform: 'translate(-50%, -50%)' }}
        animate={{
          scale: [1, 2],
          opacity: [0.8, 0],
        }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'easeOut',
        }}
      />
      {/* Inner circle */}
      <div
        className="absolute h-4 w-4 rounded-full bg-red-500"
        style={{ transform: 'translate(-50%, -50%)' }}
      />
    </motion.div>
  );
}

// Countdown badge
function CountdownBadge({
  countdown,
  total,
}: {
  countdown: number;
  total: number;
}) {
  const percent = (countdown / total) * 100;
  const isUrgent = countdown <= 5;

  return (
    <motion.span
      className={cn(
        'ml-2 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
        isUrgent ? 'bg-red-600/30 text-red-200' : 'bg-black/20 text-white/70'
      )}
      animate={isUrgent ? { scale: [1, 1.05, 1] } : {}}
      transition={{ duration: 0.5, repeat: Infinity }}
    >
      <svg className="h-3 w-3" viewBox="0 0 16 16">
        <circle
          cx="8"
          cy="8"
          r="6"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeDasharray={`${percent * 0.377} 100`}
          strokeLinecap="round"
          transform="rotate(-90 8 8)"
          opacity={0.6}
        />
      </svg>
      {countdown}s
    </motion.span>
  );
}
