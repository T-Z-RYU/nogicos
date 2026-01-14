/**
 * PremiumMessage - Refined message component
 * 
 * Features:
 * - Warm amber/cyan accent theme
 * - Spring-based animations
 * - Collapsible thinking block
 * - Beautiful code blocks
 */

import { motion, AnimatePresence } from 'motion/react';
import { User, Sparkles, ChevronDown, Loader2, Check } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';
import './styles/premium-theme.css';

// Types
interface TextPart {
  type: 'text';
  text: string;
}

interface ReasoningPart {
  type: 'reasoning';
  text: string;
}

interface ToolInvocationPart {
  type: 'tool-invocation';
  toolName: string;
  toolCallId: string;
  state: 'pending' | 'result';
  result?: string;
}

type MessagePart = TextPart | ReasoningPart | ToolInvocationPart;

interface PremiumMessageProps {
  id: string;
  role: 'user' | 'assistant';
  content?: string;
  parts?: MessagePart[];
  isStreaming?: boolean;
  className?: string;
}

export function PremiumMessage({
  id,
  role,
  content,
  parts,
  isStreaming = false,
  className,
}: PremiumMessageProps) {
  const isUser = role === 'user';

  // Extract content
  const textContent = parts
    ?.filter((p): p is TextPart => p.type === 'text')
    .map(p => p.text)
    .join('') || content || '';

  const reasoningParts = parts?.filter((p): p is ReasoningPart => p.type === 'reasoning') || [];
  const toolParts = parts?.filter((p): p is ToolInvocationPart => p.type === 'tool-invocation') || [];

  return (
    <div className={cn('premium-message', className)}>
      {/* Avatar */}
      <div className={cn(
        'premium-avatar',
        isUser ? 'premium-avatar-user' : 'premium-avatar-ai',
        isStreaming && !isUser && 'is-streaming'
      )}>
        {isUser ? (
          <User className="w-5 h-5 text-zinc-400" />
        ) : (
          <Sparkles className="w-5 h-5 text-amber-400" />
        )}
      </div>

      {/* Content */}
      <div className="premium-content">
        <div className={cn('premium-role', !isUser && 'premium-role-ai')}>
          {isUser ? 'You' : 'NogicOS'}
        </div>

        {isUser ? (
          <div className="premium-user-text">{textContent}</div>
        ) : (
          <div className="space-y-4">
            {/* Thinking blocks */}
            {reasoningParts.map((part, i) => (
              <PremiumThinking
                key={`${id}-reasoning-${i}`}
                content={part.text}
                isStreaming={isStreaming && i === reasoningParts.length - 1}
              />
            ))}

            {/* Tool invocations */}
            {toolParts.map((part, i) => (
              <PremiumTool
                key={`${id}-tool-${i}`}
                name={part.toolName}
                state={part.state}
              />
            ))}

            {/* Text content */}
            {textContent && (
              <div className="premium-ai-response">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    pre: ({ children }) => (
                      <div className="premium-code-block">
                        <pre className="premium-code-content">{children}</pre>
                      </div>
                    ),
                    code: ({ className, children, ...props }) => {
                      const isInline = !className;
                      if (isInline) {
                        return <code className="premium-code-inline" {...props}>{children}</code>;
                      }
                      const lang = className?.replace('language-', '') || '';
                      return (
                        <>
                          {lang && (
                            <div className="premium-code-header">
                              <span className="premium-code-filename">{lang}</span>
                            </div>
                          )}
                          <code className="block text-sm" {...props}>{children}</code>
                        </>
                      );
                    },
                    table: ({ children }) => (
                      <div className="overflow-x-auto rounded-lg border border-zinc-800 my-4">
                        <table className="w-full">{children}</table>
                      </div>
                    ),
                    thead: ({ children }) => <thead className="bg-zinc-900">{children}</thead>,
                    th: ({ children }) => (
                      <th className="text-left p-3 text-sm font-semibold text-zinc-300 border-b border-zinc-800">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="p-3 text-sm border-b border-zinc-800/50">{children}</td>
                    ),
                    ul: ({ children }) => <ul className="list-disc ml-6 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal ml-6 space-y-1">{children}</ol>,
                    li: ({ children }) => <li>{children}</li>,
                    strong: ({ children }) => <strong className="font-semibold text-zinc-100">{children}</strong>,
                    a: ({ href, children }) => (
                      <a href={href} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-amber-400 underline underline-offset-2 transition-colors">
                        {children}
                      </a>
                    ),
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-2 border-amber-500 pl-4 my-4 text-zinc-400 italic">
                        {children}
                      </blockquote>
                    ),
                  }}
                >
                  {textContent}
                </ReactMarkdown>
                {isStreaming && <span className="premium-cursor" />}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * PremiumThinking - Collapsible thinking display
 */
function PremiumThinking({
  content,
  isStreaming = false,
}: {
  content: string;
  isStreaming?: boolean;
}) {
  const [isExpanded, setIsExpanded] = useState(true);
  const contentRef = useRef<HTMLDivElement>(null);

  // Auto-scroll when streaming
  useEffect(() => {
    if (contentRef.current && isExpanded && isStreaming) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [content, isExpanded, isStreaming]);

  if (!content && !isStreaming) return null;

  return (
    <div className="premium-thinking">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="premium-thinking-header"
      >
        <svg
          className={cn('premium-thinking-icon', isStreaming && 'is-streaming')}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V12h3a3 3 0 0 1 3 3v1h-2v-1a1 1 0 0 0-1-1h-3v3h-4v-3H7a1 1 0 0 0-1 1v1H4v-1a3 3 0 0 1 3-3h3V9.5c-1.2-.7-2-2-2-3.5a4 4 0 0 1 4-4z" />
          <circle cx="12" cy="6" r="2" />
          <path d="M9 22v-4M15 22v-4M12 22v-4" />
        </svg>

        <span className="premium-thinking-label">
          {isStreaming ? (
            <span className="flex items-center gap-2">
              Thinking
              <motion.span
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                ...
              </motion.span>
            </span>
          ) : (
            'Thought process'
          )}
        </span>

        <ChevronDown className={cn('premium-thinking-chevron', isExpanded && 'is-expanded')} />
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            style={{ willChange: 'height, opacity' }}
          >
            <div ref={contentRef} className="premium-thinking-content premium-scrollbar">
              {content}
              {isStreaming && (
                <motion.span
                  className="inline-block w-1.5 h-3 ml-1 bg-cyan-400 rounded-sm"
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity }}
                />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * PremiumTool - Tool execution status
 */
function PremiumTool({
  name,
  state,
}: {
  name: string;
  state: 'pending' | 'result';
}) {
  return (
    <div className="premium-tool">
      {state === 'pending' ? (
        <Loader2 className="premium-tool-icon is-spinning" />
      ) : (
        <Check className="premium-tool-icon text-emerald-400" />
      )}
      <span>
        {state === 'pending' ? `Running ${name}...` : `${name} completed`}
      </span>
    </div>
  );
}

export default PremiumMessage;


