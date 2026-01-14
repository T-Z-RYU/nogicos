import { useState, useRef, useEffect, useCallback } from 'react';
import type { KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Send, Paperclip, Mic, StopCircle, Sparkles } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { MessageBubble } from './MessageBubble';
import type { Message } from './MessageBubble';
import { ToolCard } from './ToolCard';
import type { ToolExecution } from './ToolCard';
import { ThinkingIndicator } from './ThinkingIndicator';
import type { ThinkingState } from './ThinkingIndicator';
import { cn } from '@/lib/utils';

// Phase 7: Agent ComponentImport
import {
  AgentStatusIndicator,
  TaskProgressBar,
  SensitiveActionDialog,
  ErrorDisplay,
  HotkeyHints,
  AgentToast,
} from '@/components/agent';
import { useAgentHotkeys } from '@/hooks/useAgentHotkeys';
import type { AgentStatus, AgentProgress, AgentError, AgentController } from '@/types/agent';
import type { SensitiveAction } from '@/types/sensitive-action';

// Phase 7: Toast Classtype
interface AgentToastItem {
  id: string;
  message: string;
  timestamp: number;
}

interface ChatAreaProps {
  messages: Message[];
  tools: ToolExecution[];
  isExecuting: boolean;
  thinkingState?: ThinkingState;
  onSendMessage: (content: string) => void;
  onStopExecution?: () => void;
  // Phase 7: Agent StateProperty
  agentStatus?: AgentStatus;
  agentProgress?: AgentProgress | null;
  agentError?: AgentError | null;
  pendingAction?: SensitiveAction | null;
  onConfirmAction?: (actionId: string, approved: boolean) => void;
  onRecoverFromError?: (handler: string) => void;
  agentController?: AgentController | null;
  // Phase 7: Toast Queue（forDisplayNone hwnd ActionTip）
  toastQueue?: AgentToastItem[];
  onDismissToast?: (id: string) => void;
}

export function ChatArea({
  messages,
  tools,
  isExecuting,
  thinkingState,
  onSendMessage,
  onStopExecution,
  // Phase 7: Agent State
  agentStatus = 'idle',
  agentProgress = null,
  agentError = null,
  pendingAction = null,
  onConfirmAction,
  onRecoverFromError,
  agentController = null,
  // Phase 7: Toast
  toastQueue = [],
  onDismissToast,
}: ChatAreaProps) {
  const [input, setInput] = useState('');
  const [showHotkeyHints, setShowHotkeyHints] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Phase 7: sensitiveActionConfirmHandle
  const handleConfirmAction = useCallback((actionId: string) => {
    onConfirmAction?.(actionId, true);
  }, [onConfirmAction]);

  const handleCancelAction = useCallback((actionId: string) => {
    onConfirmAction?.(actionId, false);
  }, [onConfirmAction]);

  // Phase 7: ErrorResumeHandle
  const handleErrorAction = useCallback((handler: string) => {
    onRecoverFromError?.(handler);
  }, [onRecoverFromError]);

  // Phase 7: HotkeySupport
  useAgentHotkeys(agentController, {
    enabled: agentStatus !== 'idle' && agentStatus !== 'completed',
    onEmergencyStop: () => onStopExecution?.(),
    onConfirmAction: pendingAction ? () => handleConfirmAction(pendingAction.id) : undefined,
  });

  // DisplayHotkeyTip（Agent Executetime）
  useEffect(() => {
    const isAgentActive = agentStatus !== 'idle' && agentStatus !== 'completed' && agentStatus !== 'failed';
    // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional: sync with agent status
    setShowHotkeyHints(isAgentActive);
  }, [agentStatus]);

  // Smooth scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, tools]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    if (input.trim() && !isExecuting) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const isEmpty = messages.length === 0;

  // JudgeYesNoDisplay Agent StateLocale
  const showAgentStatus = agentStatus !== 'idle' || agentProgress || agentError;

  return (
    <main className="flex-1 flex flex-col min-w-0 bg-gradient-to-b from-transparent to-black/20">
      {/* Phase 7: Agent State区域 */}
      <AnimatePresence>
        {showAgentStatus && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-b border-white/[0.06] bg-black/20 overflow-hidden"
          >
            <div className="max-w-3xl mx-auto px-6 py-3 space-y-3">
              {/* State指示器 */}
              <div className="flex items-center justify-between">
                <AgentStatusIndicator 
                  status={agentStatus} 
                  detail={agentProgress?.currentWindow}
                />
                {agentStatus !== 'idle' && agentStatus !== 'completed' && agentStatus !== 'failed' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onStopExecution}
                    className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                  >
                    <StopCircle className="w-4 h-4 mr-1.5" />
                    Stop
                  </Button>
                )}
              </div>

              {/* 进度条 */}
              {agentProgress && (
                <TaskProgressBar 
                  progress={agentProgress} 
                  showDetails={true}
                />
              )}

              {/* ErrorDisplay */}
              {agentError && (
                <ErrorDisplay
                  error={agentError}
                  onAction={handleErrorAction}
                />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages Area */}
      <ScrollArea className="flex-1" ref={scrollRef}>
        <div className="max-w-3xl mx-auto px-6 py-8">
          <AnimatePresence mode="wait">
            {isEmpty ? (
              <WelcomeScreen key="welcome" onQuickAction={onSendMessage} />
            ) : (
              <motion.div 
                key="messages"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {messages.map((message, index) => (
                  <div key={message.id}>
                    <MessageBubble 
                      message={message} 
                      isLatest={index === messages.length - 1}
                    />
                    
                    {/* Tool executions after assistant messages */}
                    {message.role === 'assistant' && (
                      <AnimatePresence>
                        <div className="mt-3 ml-11 space-y-2">
                          {tools
                            .filter((t) => t.messageId === message.id)
                            .map((tool, toolIndex) => (
                              <motion.div
                                key={tool.id}
                                initial={{ opacity: 0, x: -8 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: toolIndex * 0.1 }}
                              >
                                <ToolCard tool={tool} />
                              </motion.div>
                            ))}
                        </div>
                      </AnimatePresence>
                    )}
                  </div>
                ))}

                {/* Thinking indicator - Shows AI reasoning process */}
                <AnimatePresence>
                  {thinkingState && (thinkingState.isThinking || thinkingState.content) && (
                    <ThinkingIndicator 
                      state={thinkingState} 
                      className="ml-11"
                    />
                  )}
                </AnimatePresence>

                {/* Simple loading indicator (fallback when no thinking state) */}
                <AnimatePresence>
                  {isExecuting && (!thinkingState || (!thinkingState.isThinking && !thinkingState.content)) && (
                    <motion.div 
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className="flex items-center gap-3 px-4 py-3"
                    >
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500/20 to-blue-500/20 border border-white/10 flex items-center justify-center">
                        <Sparkles className="w-4 h-4 text-white/80" />
                      </div>
                      <div className="flex items-center gap-2">
                        <ThinkingDots />
                        <span className="text-sm text-white/50">Processing...</span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                <div ref={messagesEndRef} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t border-white/[0.06] bg-black/40 backdrop-blur-xl">
        <div className="max-w-3xl mx-auto p-4">
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="relative rounded-2xl bg-white/[0.04] border border-white/[0.08] p-3 shadow-lg shadow-black/20"
          >
            <div className="flex items-end gap-3">
              {/* Attachment Button */}
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9 shrink-0 text-white/40 hover:text-white/70 hover:bg-white/5 rounded-xl"
              >
                <Paperclip className="w-4 h-4" />
              </Button>

              {/* Text Input */}
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="What would you like me to do?"
                  rows={1}
                  disabled={isExecuting}
                  className={cn(
                    'w-full resize-none bg-transparent',
                    'text-[15px] text-white/90 leading-relaxed',
                    'placeholder:text-white/30',
                    'focus:outline-none',
                    'disabled:opacity-50',
                    'max-h-[200px]'
                  )}
                />
              </div>

              {/* Voice Button */}
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9 shrink-0 text-white/40 hover:text-white/70 hover:bg-white/5 rounded-xl"
              >
                <Mic className="w-4 h-4" />
              </Button>

              {/* Send/Stop Button */}
              {isExecuting ? (
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    onClick={onStopExecution}
                    size="icon"
                    className="h-9 w-9 shrink-0 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-xl"
                  >
                    <StopCircle className="w-4 h-4" />
                  </Button>
                </motion.div>
              ) : (
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    onClick={handleSubmit}
                    disabled={!input.trim()}
                    size="icon"
                    className={cn(
                      'h-9 w-9 shrink-0 rounded-xl transition-all duration-200',
                      input.trim() 
                        ? 'bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/20' 
                        : 'bg-white/5 text-white/20'
                    )}
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </motion.div>
              )}
            </div>

            {/* Hints */}
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/[0.04]">
              <span className="text-[11px] text-white/25 font-medium">
                Press <kbd className="px-1.5 py-0.5 bg-white/5 rounded text-[10px] mx-0.5">Enter</kbd> to send, 
                <kbd className="px-1.5 py-0.5 bg-white/5 rounded text-[10px] mx-0.5 ml-1">Shift+Enter</kbd> for new line
              </span>
              <span className="text-[11px] text-white/25 font-medium flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/80 animate-pulse" />
                Claude Opus 4.5
              </span>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Phase 7: 敏感操作Confirm对话框 */}
      <SensitiveActionDialog
        action={pendingAction}
        onConfirm={handleConfirmAction}
        onCancel={handleCancelAction}
        open={!!pendingAction}
      />

      {/* Phase 7: 快捷键提示 */}
      <HotkeyHints visible={showHotkeyHints} position="bottom-right" />

      {/* Phase 7: Agent Toast 提示（无 hwnd 操作Notify） */}
      {toastQueue.length > 0 && (
        <AgentToast 
          toasts={toastQueue} 
          onDismiss={onDismissToast}
          position="bottom-center"
        />
      )}
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
          className="w-1.5 h-1.5 rounded-full bg-primary"
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
 * WelcomeScreen - Redesigned welcome with quick actions
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
        className="w-20 h-20 rounded-3xl bg-gradient-to-br from-primary/30 to-violet-500/20 border border-white/10 flex items-center justify-center mb-8 shadow-2xl shadow-primary/20"
      >
        <Sparkles className="w-10 h-10 text-primary" />
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
        className="text-white/50 text-[15px] max-w-md mb-10 leading-relaxed"
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
              'bg-white/[0.03] border border-white/[0.06]',
              'hover:bg-white/[0.06] hover:border-white/[0.1]',
              'transition-all duration-200',
              'group cursor-pointer'
            )}
          >
            <span className="text-2xl mb-3 group-hover:scale-110 transition-transform">{item.icon}</span>
            <span className="text-[14px] font-medium text-white/90">{item.title}</span>
            <span className="text-[12px] text-white/40 mt-0.5">{item.desc}</span>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}
