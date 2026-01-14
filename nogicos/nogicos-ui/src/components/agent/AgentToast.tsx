/**
 * AgentToast Component
 * Phase 7: Toast notifications for operations without hwnd
 */

import { motion, AnimatePresence } from 'motion/react';
import { Zap, X } from 'lucide-react';

interface Toast {
  id: string;
  message: string;
  timestamp: number;
}

interface AgentToastProps {
  toasts: Toast[];
  onDismiss?: (id: string) => void;
  position?: 'top-right' | 'bottom-right' | 'bottom-center';
}

export function AgentToast({ 
  toasts, 
  onDismiss,
  position = 'bottom-right' 
}: AgentToastProps) {
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'bottom-right': 'bottom-20 right-4',
    'bottom-center': 'bottom-20 left-1/2 -translate-x-1/2',
  };

  return (
    <div className={`fixed ${positionClasses[position]} z-50 flex flex-col gap-2 pointer-events-none`}>
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ 
              type: 'spring', 
              stiffness: 500, 
              damping: 30 
            }}
            className="pointer-events-auto"
          >
            <div className="flex items-center gap-3 px-4 py-3 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl shadow-black/50 max-w-sm">
              {/* Icon */}
              <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                <Zap className="w-4 h-4 text-emerald-400" />
              </div>
              
              {/* Message */}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white/90 truncate">
                  {toast.message}
                </p>
                <p className="text-xs text-white/40 mt-0.5">
                  AI processing...
                </p>
              </div>
              
              {/* Dismiss button */}
              {onDismiss && (
                <button
                  onClick={() => onDismiss(toast.id)}
                  className="flex-shrink-0 p-1 text-white/40 hover:text-white/70 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              
              {/* Progress bar (auto-dismiss indicator) */}
              <motion.div
                className="absolute bottom-0 left-0 h-0.5 bg-emerald-500/50 rounded-full"
                initial={{ width: '100%' }}
                animate={{ width: '0%' }}
                transition={{ duration: 3, ease: 'linear' }}
              />
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

/**
 * Single Toast component (for finer-grained control)
 */
export function SingleAgentToast({ 
  message, 
  visible,
  onDismiss,
}: { 
  message: string; 
  visible: boolean;
  onDismiss?: () => void;
}) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="fixed bottom-20 right-4 z-50"
        >
          <div className="flex items-center gap-3 px-4 py-3 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl">
            <Zap className="w-4 h-4 text-emerald-400" />
            <span className="text-sm text-white/90">{message}</span>
            {onDismiss && (
              <button onClick={onDismiss} className="text-white/40 hover:text-white/70">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
