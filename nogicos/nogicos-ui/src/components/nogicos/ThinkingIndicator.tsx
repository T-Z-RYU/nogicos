import { motion, AnimatePresence } from 'motion/react';
import { Brain, ChevronDown } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

export interface ThinkingState {
  isThinking: boolean;
  content: string;
  durationMs?: number;
}

interface ThinkingIndicatorProps {
  state: ThinkingState;
  className?: string;
}

/**
 * ThinkingIndicator - Shows AI thinking process in real-time
 * 
 * Features:
 * - Pulsing animation while thinking
 * - Collapsible thinking content
 * - Streaming text display
 * - Duration display when complete
 */
export function ThinkingIndicator({ state, className }: ThinkingIndicatorProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when new content arrives
  useEffect(() => {
    if (contentRef.current && isExpanded) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [state.content, isExpanded]);

  // Auto-expand when thinking starts
  useEffect(() => {
    if (state.isThinking && state.content.length > 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional: expand on thinking start
      setIsExpanded(true);
    }
  }, [state.isThinking, state.content]);

  if (!state.isThinking && !state.content) {
    return null;
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.95 }}
        transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
        className={cn(
          'rounded-xl overflow-hidden',
          'bg-gradient-to-r from-violet-500/10 via-purple-500/10 to-blue-500/10',
          'border border-white/[0.08]',
          'backdrop-blur-md',
          className
        )}
      >
        {/* Header */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={cn(
            'w-full flex items-center gap-3 px-4 py-3',
            'hover:bg-white/[0.03] transition-colors',
            'text-left'
          )}
        >
          {/* Brain icon with pulse animation */}
          <div className="relative">
            <Brain className={cn(
              'w-5 h-5 text-violet-400',
              state.isThinking && 'animate-pulse'
            )} />
            {state.isThinking && (
              <motion.div
                className="absolute inset-0 rounded-full bg-violet-400/30"
                animate={{
                  scale: [1, 1.5, 1],
                  opacity: [0.5, 0, 0.5],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />
            )}
          </div>

          {/* Label */}
          <div className="flex-1">
            <span className={cn(
              'text-sm font-medium',
              state.isThinking ? 'text-violet-300' : 'text-white/60'
            )}>
              {state.isThinking ? (
                <span className="flex items-center gap-2">
                  Thinking
                  <motion.span
                    animate={{ opacity: [1, 0.3, 1] }}
                    transition={{ duration: 1.2, repeat: Infinity }}
                  >
                    ...
                  </motion.span>
                </span>
              ) : (
                `Thought for ${state.durationMs ? `${(state.durationMs / 1000).toFixed(1)}s` : 'a moment'}`
              )}
            </span>
          </div>

          {/* Expand/collapse button */}
          {state.content && (
            <motion.div
              animate={{ rotate: isExpanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronDown className="w-4 h-4 text-white/40" />
            </motion.div>
          )}
        </button>

        {/* Expandable content */}
        <AnimatePresence>
          {isExpanded && state.content && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            >
              <div
                ref={contentRef}
                className={cn(
                  'px-4 pb-4 max-h-[200px] overflow-y-auto',
                  'scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent'
                )}
              >
                <div className={cn(
                  'text-xs leading-relaxed',
                  'text-white/50 font-mono',
                  'whitespace-pre-wrap break-words'
                )}>
                  {state.content}
                  {state.isThinking && (
                    <motion.span
                      className="inline-block w-2 h-3 ml-0.5 bg-violet-400/60"
                      animate={{ opacity: [1, 0, 1] }}
                      transition={{ duration: 0.8, repeat: Infinity }}
                    />
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </AnimatePresence>
  );
}

