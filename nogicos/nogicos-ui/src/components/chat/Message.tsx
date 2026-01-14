import { motion } from 'motion/react';
import { User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';
import { StreamingText } from './StreamingText';
import { ThinkingBlock } from './ThinkingBlock';
import './styles/cursor-theme.css';

// Vercel AI SDK message part types
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

interface MessageProps {
  id: string;
  role: 'user' | 'assistant';
  content?: string;
  parts?: MessagePart[];
  isStreaming?: boolean;
  className?: string;
}

/**
 * Message - Cursor-style message bubble
 * 
 * Supports Vercel AI SDK message format with parts:
 * - text: Regular text content
 * - reasoning: Thinking/reasoning content (collapsible)
 * - tool-invocation: Tool call status
 */
export function Message({
  id,
  role,
  content,
  parts,
  isStreaming = false,
  className,
}: MessageProps) {
  const isUser = role === 'user';

  // Extract content from parts if available
  const textContent = parts
    ?.filter((p): p is TextPart => p.type === 'text')
    .map(p => p.text)
    .join('') || content || '';

  const reasoningParts = parts?.filter((p): p is ReasoningPart => p.type === 'reasoning') || [];
  const toolParts = parts?.filter((p): p is ToolInvocationPart => p.type === 'tool-invocation') || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
      style={{ willChange: 'transform, opacity' }}
      className={cn('flex gap-3', className)}
    >
      {/* Avatar */}
      <div className={cn(
        'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
        isUser 
          ? 'bg-[var(--chat-bg-user-message)]' 
          : 'bg-gradient-to-br from-violet-500/20 to-blue-500/20 border border-white/10'
      )}>
        {isUser ? (
          <User className="w-4 h-4 text-[var(--chat-text-secondary)]" />
        ) : (
          <Bot className="w-4 h-4 text-violet-400" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Role label */}
        <div className="text-xs text-[var(--chat-text-secondary)] mb-1 font-medium">
          {isUser ? 'You' : 'NogicOS'}
        </div>

        {isUser ? (
          // User message - simple text
          <div className="chat-message-user">
            <p className="text-[var(--chat-text-primary)]">{textContent}</p>
          </div>
        ) : (
          // Assistant message - with thinking, tools, and streaming
          <div className="space-y-3">
            {/* Thinking blocks */}
            {reasoningParts.map((part, i) => (
              <ThinkingBlock
                key={`${id}-reasoning-${i}`}
                content={part.text}
                isStreaming={isStreaming && i === reasoningParts.length - 1}
                defaultExpanded={true}
              />
            ))}

            {/* Tool invocations */}
            {toolParts.map((part, i) => (
              <div 
                key={`${id}-tool-${i}`}
                className="chat-tool-status flex items-center gap-2"
              >
                {part.state === 'pending' ? (
                  <>
                    <span className="animate-spin">⚙️</span>
                    <span>Running {part.toolName}...</span>
                  </>
                ) : (
                  <>
                    <span>✓</span>
                    <span className="text-[var(--chat-accent-green)]">
                      {part.toolName} completed
                    </span>
                  </>
                )}
              </div>
            ))}

            {/* Text content */}
            {textContent && (
              <StreamingText
                content={textContent}
                isStreaming={isStreaming}
              />
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}

