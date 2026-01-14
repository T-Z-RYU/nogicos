import { motion } from 'motion/react';
import { Copy, Check, User, Sparkles } from 'lucide-react';
import { useState, memo } from 'react';
import { cn } from '@/lib/utils';
import { StreamingText } from './StreamingText';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
  isStreaming?: boolean;
}

interface MessageBubbleProps {
  message: Message;
  isLatest?: boolean;
}

/**
 * MessageBubble - Redesigned chat bubble with Cursor-like aesthetics
 * 
 * Features:
 * - Glassmorphism styling
 * - Copy button on hover
 * - Streaming text animation
 * - Staggered entry animation
 * - Better typography and spacing
 */
export const MessageBubble = memo(function MessageBubble({ message, isLatest = false }: MessageBubbleProps) {
    
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ 
        duration: 0.3, 
        ease: [0.22, 1, 0.36, 1] // Custom spring-like ease
      }}
      className={cn(
        'group flex gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.2 }}
        className={cn(
          'w-8 h-8 rounded-xl flex items-center justify-center shrink-0',
          'border transition-colors duration-200',
          isUser 
            ? 'bg-primary/20 border-primary/30 text-primary' 
            : 'bg-gradient-to-br from-violet-500/20 to-blue-500/20 border-white/10 text-white/80'
        )}
      >
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <Sparkles className="w-4 h-4" />
        )}
      </motion.div>

      {/* Content Container */}
      <div className={cn(
        'flex flex-col max-w-[85%] min-w-[100px]',
        isUser ? 'items-end' : 'items-start'
      )}>
        {/* Message Bubble */}
        <div
          className={cn(
            'relative px-4 py-3 rounded-2xl',
            'text-[14px] leading-[1.6]',
            'transition-all duration-200',
            isUser ? [
              // User bubble - solid primary color
              'bg-primary text-primary-foreground',
              'rounded-br-md',
            ] : [
              // Assistant bubble - glassmorphism
              'bg-white/[0.06] backdrop-blur-md',
              'border border-white/[0.08]',
              'text-white/90',
              'rounded-bl-md',
              'shadow-lg shadow-black/10',
            ]
          )}
        >
          {/* Copy Button (assistant only) */}
          {!isUser && (
            <motion.button
              initial={{ opacity: 0 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleCopy}
              className={cn(
                'absolute -top-2 -right-2 p-1.5 rounded-lg',
                'bg-white/10 border border-white/10',
                'opacity-0 group-hover:opacity-100',
                'transition-opacity duration-200',
                'hover:bg-white/15'
              )}
            >
              {copied ? (
                <Check className="w-3 h-3 text-emerald-400" />
              ) : (
                <Copy className="w-3 h-3 text-white/60" />
              )}
            </motion.button>
          )}

          {/* Content */}
          {isUser ? (
            <span className="whitespace-pre-wrap">{message.content}</span>
          ) : (
            <StreamingText 
              content={message.content}
              isStreaming={message.isStreaming && isLatest}
              speed={12}
            />
          )}
        </div>

        {/* Timestamp */}
        {message.timestamp && (
        <motion.span 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className={cn(
            'text-[11px] mt-1.5 px-1',
            'text-white/30',
            'font-medium tracking-wide'
          )}
        >
          {formatTime(message.timestamp)}
        </motion.span>
        )}
      </div>
    </motion.div>
  );
});

function formatTime(date?: Date): string {
  if (!date) return '';
  return date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });
}
