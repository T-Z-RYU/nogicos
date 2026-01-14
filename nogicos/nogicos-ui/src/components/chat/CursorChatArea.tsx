import { useState, useRef, useEffect, useCallback } from 'react';
import type { KeyboardEvent } from 'react';
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import { motion, AnimatePresence } from 'motion/react';
import { Send, Paperclip, Mic, StopCircle, Sparkles } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Message } from './Message';
import { ModeSelector, ModeIndicator, type AgentMode } from './ModeSelector';
import { PlanEditor, type EditablePlan } from './PlanEditor';
import { cn } from '@/lib/utils';
import './styles/cursor-theme.css';

interface CursorChatAreaProps {
  apiUrl?: string;
  sessionId?: string;
  className?: string;
}

/**
 * CursorChatArea - Cursor-style chat interface with Vercel AI SDK
 * 
 * Features:
 * - Streaming responses via useChat hook
 * - Thinking/reasoning display
 * - Tool call status
 * - Smooth animations
 * - Auto-scroll
 */
export function CursorChatArea({
  apiUrl = 'http://localhost:8080/api/chat',
  sessionId = 'default',
  className,
}: CursorChatAreaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [localInput, setLocalInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  // Mode state (Agent/Ask/Plan)
  const [mode, setMode] = useState<AgentMode>('agent');
  const [pendingPlan, setPendingPlan] = useState<EditablePlan | null>(null);
  const [isExecutingPlan, setIsExecutingPlan] = useState(false);

  // Vercel AI SDK useChat hook with DefaultChatTransport
  const {
    messages,
    sendMessage,
    stop,
  } = useChat({
    transport: new DefaultChatTransport({
      api: apiUrl,
      body: {
        session_id: sessionId,
        mode: mode,  // Include mode in request
      },
    }),
  });

  // Auto-scroll to bottom
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

  // Check if streaming (last message is from assistant and is being updated)
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      // If we just sent a message and waiting for response
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
      setPendingPlan(null);  // Clear any pending plan
      
      try {
        await sendMessage({ text: localInput.trim() });
        setLocalInput('');
        
        // TODO: Handle plan mode response - parse plan from response
        // For now, the backend sends plan_generated via WebSocket
        
      } catch (err) {
        console.error('[CursorChatArea] Error:', err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setIsLoading(false);
      }
    }
  }, [localInput, isLoading, sendMessage]);

  // Handle plan confirmation
  const handlePlanConfirm = useCallback(async () => {
    if (!pendingPlan) return;
    
    setIsExecutingPlan(true);
    try {
      // Send request with confirmed plan
      // This would need to be a separate API call or WebSocket message
      console.log('[CursorChatArea] Executing confirmed plan:', pendingPlan);
      
      // TODO: Implement actual plan execution via API
      // await fetch(`${apiUrl.replace('/chat', '/execute')}`, {
      //   method: 'POST',
      //   body: JSON.stringify({ mode: 'agent', confirmed_plan: pendingPlan }),
      // });
      
      setPendingPlan(null);
    } catch (err) {
      console.error('[CursorChatArea] Plan execution error:', err);
      setError(err instanceof Error ? err : new Error('Failed to execute plan'));
    } finally {
      setIsExecutingPlan(false);
    }
  }, [pendingPlan]);

  const handlePlanCancel = useCallback(() => {
    setPendingPlan(null);
  }, []);

  const handlePlanEdit = useCallback((editedPlan: EditablePlan) => {
    setPendingPlan(editedPlan);
  }, []);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e as unknown as React.FormEvent);
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <main className={cn(
      'flex-1 flex flex-col min-w-0 chat-container',
      'bg-gradient-to-b from-transparent to-black/20',
      className
    )}>
      {/* Messages Area */}
      <ScrollArea className="flex-1">
        <div className="max-w-3xl mx-auto px-6 py-8">
          <AnimatePresence mode="wait">
            {isEmpty ? (
              <WelcomeScreen 
                key="welcome" 
                onQuickAction={(action) => {
                  setLocalInput(action);
                }} 
              />
            ) : (
              <motion.div 
                key="messages"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {messages.map((message, index) => (
                  <Message
                    key={message.id}
                    id={message.id}
                    role={message.role as 'user' | 'assistant'}
                    content={(message as unknown as { content?: string }).content || ''}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- UIMessage parts to MessagePart compatibility
                    parts={message.parts as any}
                    isStreaming={isLoading && index === messages.length - 1 && message.role === 'assistant'}
                  />
                ))}

                {/* Loading indicator when waiting for response */}
                <AnimatePresence>
                  {isLoading && messages[messages.length - 1]?.role === 'user' && (
                    <motion.div 
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className="flex items-center gap-3 px-4 py-3"
                    >
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500/20 to-blue-500/20 border border-white/10 flex items-center justify-center">
                        <Sparkles className="w-4 h-4 text-violet-400" />
                      </div>
                      <div className="flex items-center gap-2">
                        <ThinkingDots />
                        <span className="text-sm text-[var(--chat-text-secondary)]">Thinking...</span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Error display */}
                {error && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
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

      {/* Plan Editor (when in Plan mode and have pending plan) */}
      <AnimatePresence>
        {pendingPlan && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="px-6 py-4 border-t border-white/[0.06]"
          >
            <PlanEditor
              plan={pendingPlan}
              onEdit={handlePlanEdit}
              onConfirm={handlePlanConfirm}
              onCancel={handlePlanCancel}
              isExecuting={isExecutingPlan}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input Area */}
      <div className="border-t border-[var(--chat-border-light)] bg-black/40 backdrop-blur-xl">
        <div className="max-w-3xl mx-auto p-4">
          <form onSubmit={onSubmit}>
            <motion.div 
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="relative rounded-2xl bg-white/[0.04] border border-[var(--chat-border-light)] p-3 shadow-lg shadow-black/20"
            >
              <div className="flex items-end gap-3">
                {/* Mode Selector */}
                <ModeSelector
                  mode={mode}
                  onModeChange={setMode}
                  disabled={isLoading}
                />
                
                {/* Attachment Button */}
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 shrink-0 text-[var(--chat-text-secondary)] hover:text-[var(--chat-text-primary)] hover:bg-white/5 rounded-xl"
                >
                  <Paperclip className="w-4 h-4" />
                </Button>

                {/* Text Input */}
                <div className="flex-1 relative">
                  <textarea
                    ref={textareaRef}
                    value={localInput}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder="What would you like me to do?"
                    rows={1}
                    disabled={isLoading}
                    className={cn(
                      'w-full resize-none bg-transparent',
                      'text-[15px] text-[var(--chat-text-primary)] leading-relaxed',
                      'placeholder:text-[var(--chat-text-muted)]',
                      'focus:outline-none',
                      'disabled:opacity-50',
                      'max-h-[200px]'
                    )}
                  />
                </div>

                {/* Voice Button */}
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 shrink-0 text-[var(--chat-text-secondary)] hover:text-[var(--chat-text-primary)] hover:bg-white/5 rounded-xl"
                >
                  <Mic className="w-4 h-4" />
                </Button>

                {/* Send/Stop Button */}
                {isLoading ? (
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      type="button"
                      onClick={stop}
                      size="icon"
                      className="h-9 w-9 shrink-0 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-xl"
                    >
                      <StopCircle className="w-4 h-4" />
                    </Button>
                  </motion.div>
                ) : (
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      type="submit"
                      disabled={!localInput.trim()}
                      size="icon"
                      className={cn(
                        'h-9 w-9 shrink-0 rounded-xl transition-all duration-200',
                        localInput.trim() 
                          ? 'bg-violet-500 hover:bg-violet-600 text-white shadow-lg shadow-violet-500/20' 
                          : 'bg-white/5 text-[var(--chat-text-muted)]'
                      )}
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </motion.div>
                )}
              </div>

              {/* Hints */}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-[var(--chat-border-light)]">
                <span className="text-[11px] text-[var(--chat-text-muted)] font-medium">
                  Press <kbd className="px-1.5 py-0.5 bg-white/5 rounded text-[10px] mx-0.5">Enter</kbd> to send, 
                  <kbd className="px-1.5 py-0.5 bg-white/5 rounded text-[10px] mx-0.5 ml-1">⌘.</kbd> switch mode
                </span>
                <span className="text-[11px] text-[var(--chat-text-muted)] font-medium flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/80 animate-pulse" />
                  <ModeIndicator mode={mode} />
                </span>
              </div>
            </motion.div>
          </form>
        </div>
      </div>
    </main>
  );
}

/**
 * ThinkingDots - Animated dots indicator
 */
function ThinkingDots() {
  return (
    <div className="flex gap-1">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-violet-400"
          animate={{ 
            opacity: [0.3, 1, 0.3],
            scale: [0.8, 1, 0.8],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: i * 0.15,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}

/**
 * WelcomeScreen - Quick actions
 */
function WelcomeScreen({ onQuickAction }: { onQuickAction?: (action: string) => void }) {
  const quickActions = [
    { icon: '🖥️', title: 'Organize Desktop', desc: 'Sort files by type', action: 'Organize my desktop' },
    { icon: '🌐', title: 'Web Research', desc: 'Extract & summarize', action: 'Search for latest AI news' },
    { icon: '📁', title: 'File Operations', desc: 'Create, move, delete', action: 'List all files on desktop' },
    { icon: '⚡', title: 'Shell Commands', desc: 'Run any command', action: 'Show system info' },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex flex-col items-center justify-center min-h-[60vh] text-center"
    >
      {/* Logo */}
      <motion.div 
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
        className="w-20 h-20 rounded-3xl bg-gradient-to-br from-violet-500/30 to-blue-500/20 border border-white/10 flex items-center justify-center mb-8 shadow-2xl shadow-violet-500/20"
      >
        <Sparkles className="w-10 h-10 text-violet-400" />
      </motion.div>
      
      <motion.h1 
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-3xl font-semibold text-white mb-3 tracking-tight"
      >
        Welcome to NogicOS
      </motion.h1>
      
      <motion.p 
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="text-[var(--chat-text-secondary)] text-[15px] max-w-md mb-10 leading-relaxed"
      >
        Your AI work partner that lives in your computer. Browse the web, organize files, 
        and automate tasks with natural language.
      </motion.p>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-2 gap-3 max-w-lg w-full">
        {quickActions.map((item, i) => (
          <motion.button
            key={i}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + i * 0.08 }}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onQuickAction?.(item.action)}
            className={cn(
              'flex flex-col items-start p-4 rounded-2xl text-left',
              'bg-white/[0.03] border border-[var(--chat-border-light)]',
              'hover:bg-white/[0.06] hover:border-[var(--chat-border-hover)]',
              'transition-all duration-200',
              'group cursor-pointer'
            )}
          >
            <span className="text-2xl mb-3 group-hover:scale-110 transition-transform">{item.icon}</span>
            <span className="text-[14px] font-medium text-white/90">{item.title}</span>
            <span className="text-[12px] text-[var(--chat-text-secondary)] mt-0.5">{item.desc}</span>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}

