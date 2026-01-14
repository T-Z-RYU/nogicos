/**
 * PremiumChatArea - Linear/Raycast-grade chat interface
 * 
 * Design Philosophy:
 * - Refined futuristic aesthetic
 * - Warm dark theme with amber/cyan accents
 * - Spring-based animations
 * - Glassmorphism input
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import type { KeyboardEvent } from 'react';
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Send, 
  Paperclip, 
  Square, 
  Sparkles,
  Zap,
  Globe,
  FolderOpen,
  Terminal,
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { PremiumMessage } from './PremiumMessage';
import './styles/premium-theme.css';

interface PremiumChatAreaProps {
  apiUrl?: string;
  sessionId?: string;
  className?: string;
}

// Animation variants (using as const for proper type inference)
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
} as const;

const itemVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: 'spring' as const,
      stiffness: 300,
      damping: 30,
    },
  },
};

export function PremiumChatArea({
  apiUrl = 'http://localhost:8080/api/chat',
  sessionId = 'default',
  className,
}: PremiumChatAreaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [localInput, setLocalInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const {
    messages,
    sendMessage,
    stop,
  } = useChat({
    transport: new DefaultChatTransport({
      api: apiUrl,
      body: { session_id: sessionId },
    }),
  });

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [localInput]);

  // Track loading state
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      setIsLoading(lastMessage.role === 'user');
    } else {
      setIsLoading(false);
    }
  }, [messages]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setLocalInput(e.target.value);
  }, []);

  const onSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (localInput.trim() && !isLoading) {
      setIsLoading(true);
      setError(null);
      try {
        await sendMessage({ text: localInput.trim() });
        setLocalInput('');
      } catch (err) {
        console.error('[PremiumChat] Error:', err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setIsLoading(false);
      }
    }
  }, [localInput, isLoading, sendMessage]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e as unknown as React.FormEvent);
    }
  };

  const handleQuickAction = useCallback((action: string) => {
    setLocalInput(action);
    textareaRef.current?.focus();
  }, []);

  const isEmpty = messages.length === 0;

  return (
    <main className={cn('premium-chat premium-chat-container flex-1 flex flex-col min-w-0', className)}>
      {/* Messages Area */}
      <ScrollArea className="flex-1 premium-scrollbar">
        <div className="premium-messages">
          <AnimatePresence mode="wait">
            {isEmpty ? (
              <WelcomeScreen key="welcome" onQuickAction={handleQuickAction} />
            ) : (
              <motion.div
                key="messages"
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className="space-y-1"
              >
                {messages.map((message, index) => (
                  <motion.div key={message.id} variants={itemVariants}>
                    <PremiumMessage
                      id={message.id}
                      role={message.role as 'user' | 'assistant'}
                      content={(message as unknown as { content?: string }).content || ''}
                      // eslint-disable-next-line @typescript-eslint/no-explicit-any -- UIMessage parts to MessagePart compatibility
                      parts={message.parts as any}
                      isStreaming={isLoading && index === messages.length - 1 && message.role === 'assistant'}
                    />
                  </motion.div>
                ))}

                {/* Loading indicator */}
                <AnimatePresence>
                  {isLoading && messages[messages.length - 1]?.role === 'user' && (
                    <motion.div
                      initial={{ opacity: 0, y: 16, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -8, scale: 0.95 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                      className="premium-message"
                    >
                      <div className="premium-avatar premium-avatar-ai is-streaming">
                        <Sparkles className="w-5 h-5 text-amber-400" />
                      </div>
                      <div className="premium-content">
                        <div className="premium-role premium-role-ai">NogicOS</div>
                        <div className="flex items-center gap-3">
                          <ThinkingAnimation />
                          <span className="text-sm text-zinc-500">Thinking...</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Error */}
                {error && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                  >
                    Error: {error.message}
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="premium-input-area">
        <div className="premium-input-container">
          <form onSubmit={onSubmit}>
            <motion.div
              initial={{ y: 24, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="premium-input-box"
            >
              <div className="premium-input-row">
                {/* Attachment */}
                <button
                  type="button"
                  className="premium-btn premium-btn-ghost"
                  aria-label="Attach file"
                >
                  <Paperclip className="w-4 h-4" />
                </button>

                {/* Textarea */}
                <textarea
                  ref={textareaRef}
                  value={localInput}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder="What would you like me to do?"
                  rows={1}
                  disabled={isLoading}
                  className="premium-textarea"
                />

                {/* Send/Stop */}
                {isLoading ? (
                  <motion.button
                    type="button"
                    onClick={stop}
                    className="premium-btn premium-btn-stop"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    aria-label="Stop generation"
                  >
                    <Square className="w-4 h-4" />
                  </motion.button>
                ) : (
                  <motion.button
                    type="submit"
                    disabled={!localInput.trim()}
                    className="premium-btn premium-btn-primary"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    aria-label="Send message"
                  >
                    <Send className="w-4 h-4" />
                  </motion.button>
                )}
              </div>

              {/* Hints */}
              <div className="premium-hints">
                <span className="premium-hint-text">
                  <kbd className="premium-hint-kbd">Enter</kbd> send
                  <kbd className="premium-hint-kbd">Shift+Enter</kbd> new line
                </span>
                <div className="premium-status">
                  <span className="premium-status-dot" />
                  <span>NogicOS Agent</span>
                </div>
              </div>
            </motion.div>
          </form>
        </div>
      </div>
    </main>
  );
}

/**
 * ThinkingAnimation - Smooth wave animation
 */
function ThinkingAnimation() {
  return (
    <div className="flex gap-1">
      {[0, 1, 2, 3].map((i) => (
        <motion.span
          key={i}
          className="w-2 h-2 rounded-full"
          style={{
            background: i % 2 === 0 ? 'var(--accent-primary)' : 'var(--accent-secondary)',
          }}
          animate={{
            y: [0, -6, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: i * 0.1,
            ease: [0.22, 1, 0.36, 1],
          }}
        />
      ))}
    </div>
  );
}

/**
 * WelcomeScreen - Refined landing experience
 */
function WelcomeScreen({ onQuickAction }: { onQuickAction?: (action: string) => void }) {
  const quickActions = [
    { 
      icon: <Globe className="w-4 h-4 text-cyan-400" />, 
      title: 'Web Research', 
      desc: 'Extract & summarize content', 
      action: 'Search for latest AI news and summarize' 
    },
    { 
      icon: <FolderOpen className="w-4 h-4 text-amber-400" />, 
      title: 'Organize Files', 
      desc: 'Sort by type or date', 
      action: 'Organize my desktop files' 
    },
    { 
      icon: <Terminal className="w-4 h-4 text-emerald-400" />, 
      title: 'Run Commands', 
      desc: 'Execute shell scripts', 
      action: 'Show system info' 
    },
    { 
      icon: <Zap className="w-4 h-4 text-purple-400" />, 
      title: 'Automate', 
      desc: 'Create workflows', 
      action: 'Help me automate a daily task' 
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="premium-welcome"
    >
      {/* Logo */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 20, delay: 0.1 }}
        className="premium-logo"
      >
        <Sparkles className="w-10 h-10 text-amber-400" />
      </motion.div>

      {/* Title */}
      <motion.h1
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        className="premium-title"
      >
        Welcome to <span className="gradient-text">NogicOS</span>
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.5 }}
        className="premium-subtitle"
      >
        Your AI work partner that lives in your computer. Browse, organize, and automate with natural language.
      </motion.p>

      {/* Quick Actions */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="premium-actions"
      >
        {quickActions.map((item, i) => (
          <motion.button
            key={i}
            variants={itemVariants}
            whileHover={{ scale: 1.02, y: -3 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onQuickAction?.(item.action)}
            className="premium-action"
          >
            <div className="premium-action-icon">{item.icon}</div>
            <span className="premium-action-title">{item.title}</span>
            <span className="premium-action-desc">{item.desc}</span>
          </motion.button>
        ))}
      </motion.div>
    </motion.div>
  );
}

export default PremiumChatArea;


