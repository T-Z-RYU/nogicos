import { motion, AnimatePresence } from 'motion/react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import './styles/cursor-theme.css';

interface ThinkingBlockProps {
  content: string;
  isStreaming?: boolean;
  durationMs?: number;
  className?: string;
  defaultExpanded?: boolean;
}

/**
 * ThinkingBlock - Cursor-style collapsible thinking display
 * 
 * Features:
 * - Collapsible with smooth animation
 * - Streaming content with blinking cursor
 * - "Thinking ∧/∨" toggle
 * - Gray text styling like Cursor
 */
export function ThinkingBlock({ 
  content, 
  isStreaming = false,
  durationMs,
  className,
  defaultExpanded = false
}: ThinkingBlockProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const contentRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll when streaming
  useEffect(() => {
    if (contentRef.current && isExpanded && isStreaming) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [content, isExpanded, isStreaming]);

  // Auto-expand when streaming starts
  useEffect(() => {
    if (isStreaming && content.length > 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional: expand on streaming start
      setIsExpanded(true);
    }
  }, [isStreaming, content]);

  if (!content && !isStreaming) {
    return null;
  }

  const formatDuration = (ms: number) => {
    const seconds = ms / 1000;
    if (seconds < 1) return `${Math.round(ms)}ms`;
    return `${seconds.toFixed(1)}s`;
  };

  return (
    <div className={cn('chat-thinking', className)}>
      {/* Header - Click to toggle */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="chat-thinking-header w-full text-left hover:text-[var(--chat-text-primary)] transition-colors"
      >
        <span className="text-[var(--chat-text-secondary)]">
          {isStreaming ? (
            <span className="flex items-center gap-1">
              Thinking
              <motion.span
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ duration: 1.2, repeat: Infinity }}
              >
                ...
              </motion.span>
            </span>
          ) : (
            `Thought for ${durationMs ? formatDuration(durationMs) : 'a moment'}`
          )}
        </span>
        <span className="ml-1 text-[10px]">
          {isExpanded ? <ChevronUp className="w-3 h-3 inline" /> : <ChevronDown className="w-3 h-3 inline" />}
        </span>
      </button>

      {/* Expandable Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            style={{ willChange: 'opacity' }}
          >
            <div
              ref={contentRef}
              className="chat-thinking-content max-h-[200px] overflow-y-auto chat-scrollbar"
            >
              {content}
              {isStreaming && (
                <motion.span
                  className="inline-block w-1.5 h-3 ml-0.5 bg-[var(--chat-text-secondary)]"
                  style={{ willChange: 'opacity' }}
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

