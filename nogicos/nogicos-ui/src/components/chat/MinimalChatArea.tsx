/**
 * NogicOS Minimal Chat Area
 * 
 * Architecture:
 * - App.tsx controls the source of truth for messages (stored per session)
 * - MinimalChatArea is a controlled component that displays messages and handles input
 * - useChat handles the streaming communication, but we sync its state with parent
 */

import { useState, useRef, useEffect, useCallback, useMemo, memo } from 'react';
import type { KeyboardEvent } from 'react';
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import { motion, AnimatePresence } from 'motion/react';
import { ArrowUp, ChevronRight, Square, Terminal, Check, Loader2, AlertCircle, Bot, Search, ListTodo, FileText, Folder, Code, Globe } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { cn } from '@/lib/utils';
import './styles/minimal-theme.css';

// === MODE TYPES ===
type AgentMode = 'agent' | 'ask' | 'plan';

const MODE_CONFIG = {
  agent: { label: 'Agent', icon: Bot, color: '#10b981', desc: 'Autonomous execution' },
  ask: { label: 'Ask', icon: Search, color: '#3b82f6', desc: 'Read-only query' },
  plan: { label: 'Plan', icon: ListTodo, color: '#f59e0b', desc: 'Generate plan' },
} as const;

// === SPRING CONFIGURATIONS ===
const springs = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 400, damping: 30 },
  smooth: { type: 'spring' as const, stiffness: 200, damping: 20 },
  micro: { type: 'spring' as const, stiffness: 500, damping: 35 },
} as const;

// Message part type
interface MessagePart {
  type: string;
  text?: string;
  [key: string]: unknown;
}

// Message type
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  parts?: MessagePart[];
  isHistory?: boolean;  // True for loaded messages (skip animations)
  timestamp?: number;   // For sorting messages from different sources
}

// File context for Cursor-style auto-injection
export interface FileContext {
  path?: string;           // Current file path
  content?: string;        // Full file content
  selected?: string;       // Selected code block
  cursorLine?: number;     // Line number where cursor is
  cursorColumn?: number;   // Column position
  visibleRange?: [number, number];  // [start_line, end_line] visible in editor
}

interface MinimalChatAreaProps {
  apiUrl?: string;
  sessionId: string;
  className?: string;
  style?: React.CSSProperties;
  // History loaded from backend
  initialMessages?: ChatMessage[];
  // Called when messages change (for saving)
  onMessagesChange?: (messages: ChatMessage[]) => void;
  // Called when session title/preview should update
  onSessionUpdate?: (title: string, preview: string) => void;
  // Current file context (Cursor-style auto-injection)
  fileContext?: FileContext;
}

export function MinimalChatArea({
  apiUrl = 'http://localhost:8080/api/chat',
  sessionId,
  className,
  style,
  initialMessages = [],
  onMessagesChange,
  onSessionUpdate,
  fileContext,
}: MinimalChatAreaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const [localInput, setLocalInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [userScrolledUp, setUserScrolledUp] = useState(false);
  const [justSentMessage, setJustSentMessage] = useState(false);
  const lastUserMessageRef = useRef<HTMLDivElement>(null);
  
  // === MODE STATE ===
  const [currentMode, setCurrentMode] = useState<AgentMode>('agent');
  const [modeMenuOpen, setModeMenuOpen] = useState(false);
  const modeMenuRef = useRef<HTMLDivElement>(null);
  
  // Close mode menu on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (modeMenuRef.current && !modeMenuRef.current.contains(e.target as Node)) {
        setModeMenuOpen(false);
      }
    };
    if (modeMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [modeMenuOpen]);
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: globalThis.KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === '.') {
        e.preventDefault();
        setModeMenuOpen(o => !o);
      }
      if ((e.metaKey || e.ctrlKey) && ['1', '2', '3'].includes(e.key)) {
        e.preventDefault();
        const modes: AgentMode[] = ['agent', 'ask', 'plan'];
        setCurrentMode(modes[parseInt(e.key) - 1]);
        setModeMenuOpen(false);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Create transport with current fileContext
  // useMemo ensures transport is recreated when fileContext changes
  const chatTransport = useMemo(() => new DefaultChatTransport({
    api: apiUrl,
    body: { 
      session_id: sessionId,
      // File context for Cursor-style auto-injection
      // This is sent with every message when available
      ...(fileContext && { fileContext }),
    },
  }), [apiUrl, sessionId, fileContext]);
  
  // useChat - using session ID as key
  const {
    messages: chatMessages,
    sendMessage,
    stop,
    status,
    setMessages,
  } = useChat({
    id: `chat-${sessionId}`,  // Unique per session
    transport: chatTransport,
    onError: (err) => {
      // #region debug log A,D,E
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'MinimalChatArea.tsx:158',message:'useChat onError',data:{error:err.message,stack:err.stack,name:err.name},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,D,E'})}).catch(()=>{});
      // #endregion
      console.error('[MinimalChatArea] Chat Error:', err);
      console.error('[MinimalChatArea] Error details:', {
        message: err.message,
        stack: err.stack,
        name: err.name,
      });
      // Show user-friendly error
      if (err.message) {
        alert(`Chat error: ${err.message}`);
      }
    },
    onFinish: (message) => {
      // #region debug log E
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'MinimalChatArea.tsx:171',message:'useChat onFinish',data:{messageId:message.id,finishReason:message.finishReason},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      console.log('[MinimalChatArea] Message finished:', message);
    },
  });
  
  // Derive loading state
  const isLoading = status === 'submitted' || status === 'streaming';
  const isActuallyStreaming = status === 'streaming';

  // Refs for tracking
  const prevMessageCountRef = useRef(0);
  
  // Track session changes and load messages
  const prevSessionIdRef = useRef(sessionId);
  useEffect(() => {
    // When session changes, load the new session's messages
    if (prevSessionIdRef.current !== sessionId) {
      prevSessionIdRef.current = sessionId;
      prevMessageCountRef.current = 0;  // Reset save counter
      
      // Load initial messages for new session
      if (initialMessages.length > 0) {
        const formatted = initialMessages.map(m => ({
          id: m.id,
          role: m.role,
          content: m.content,
          parts: m.parts,
        }));
         
        setMessages(formatted as Parameters<typeof setMessages>[0]);
      } else {
        setMessages([]);
      }
    }
  }, [sessionId, initialMessages, setMessages]);
  
  // Also load on initial mount if we have messages
  const hasLoadedInitial = useRef(false);
  useEffect(() => {
    if (!hasLoadedInitial.current && initialMessages.length > 0) {
      hasLoadedInitial.current = true;
      const formatted = initialMessages.map(m => ({
        id: m.id,
        role: m.role,
        content: m.content,
        parts: m.parts,
      }));
       
      setMessages(formatted as Parameters<typeof setMessages>[0]);
    }
  }, [initialMessages, setMessages]);

  // Combine messages: prefer chatMessages if they exist, otherwise use initialMessages
  const messages = useMemo(() => {
    // If we have chat messages from useChat, use them
    if (chatMessages.length > 0) {
      return chatMessages.map(m => ({
        ...m,
        isHistory: m.id.startsWith('loaded-'),
      }));
    }
    // Otherwise use initial messages
    return initialMessages.map(m => ({
      ...m,
      isHistory: true,
    }));
  }, [chatMessages, initialMessages]);

  // Save messages when they change (debounced) - use ref to avoid dependency issues
  // [Repair #27]Add saveTimeoutRef Cleanup
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onMessagesChangeRef = useRef(onMessagesChange);
  const chatMessagesRef = useRef(chatMessages);
  useEffect(() => { onMessagesChangeRef.current = onMessagesChange; }, [onMessagesChange]);
  useEffect(() => { chatMessagesRef.current = chatMessages; }, [chatMessages]);

  // [Repair #27]component unmounttimeCleanup saveTimeoutRef
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);
  
  // Helper to prepare messages for saving
  const prepareMessagesForSave = useCallback((msgs: typeof chatMessages) => {
    return msgs.map(m => {
      // Extract content from parts if needed
      const msgAny = m as unknown as { content?: string };
      let content = msgAny.content || '';
      if (!content && m.parts) {
        content = (m.parts as MessagePart[])
          .filter((p) => p.type === 'text')
          .map((p) => p.text || '')
          .join('');
      }
      return {
        id: m.id,
        role: m.role as 'user' | 'assistant',
        content,
        parts: m.parts,
      };
    });
  }, []);

  // Save immediately before session switch
  useEffect(() => {
    const prevId = prevSessionIdRef.current;
    if (prevId && prevId !== sessionId && chatMessagesRef.current.length > 0) {
      // Session is changing - save current messages immediately
      if (onMessagesChangeRef.current) {
        const toSave = prepareMessagesForSave(chatMessagesRef.current);
        if (toSave.length > 0) {
          onMessagesChangeRef.current(toSave);
        }
      }
    }
    prevSessionIdRef.current = sessionId;
  }, [sessionId, prepareMessagesForSave]);
  
  useEffect(() => {
    // Save when message count changes - don't wait for status to be 'ready'
    // This ensures sidebar updates immediately when user sends a message
    if (chatMessages.length > 0 && chatMessages.length !== prevMessageCountRef.current) {
      prevMessageCountRef.current = chatMessages.length;
      
      // Clear previous timeout
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
      // Debounce save
      saveTimeoutRef.current = setTimeout(() => {
        if (onMessagesChangeRef.current) {
          const toSave = prepareMessagesForSave(chatMessages)
            // Filter out empty assistant messages (streaming not complete) for regular saves
            .filter(m => m.role === 'user' || (m.content && m.content.trim().length > 0));
          
          // Only save if we have valid messages
          if (toSave.length > 0) {
            onMessagesChangeRef.current(toSave);
          }
        }
      }, 500);
    }
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [chatMessages, status, prepareMessagesForSave]);

  // Update session title when first message is sent
  useEffect(() => {
    if (onSessionUpdate && chatMessages.length > 0) {
      const firstUserMsg = chatMessages.find(m => m.role === 'user');
      if (firstUserMsg) {
        // Extract content from message (handle UIMessage parts format)
        const msgContent = (firstUserMsg as unknown as { content?: string }).content || 
          (firstUserMsg.parts as MessagePart[] | undefined)?.filter((p) => p.type === 'text').map((p) => p.text || '').join('') || '';
        const title = msgContent.slice(0, 30) || 'New Session';
        const preview = msgContent.slice(0, 100) || '';
        onSessionUpdate(title, preview);
      }
    }
  }, [chatMessages, onSessionUpdate]);

  // Scroll handling
  const handleScroll = useCallback(() => {
    const container = chatContainerRef.current;
    if (!container) return;
    
    const { scrollTop, scrollHeight, clientHeight } = container;
    const distFromBottom = scrollHeight - scrollTop - clientHeight;
    
    setUserScrolledUp(prev => {
      if (prev) return distFromBottom < 20 ? false : true;
      return distFromBottom > 100;
    });
  }, []);

  // Reset scroll lock when streaming ends
  const wasStreamingRef = useRef(isActuallyStreaming);
  useEffect(() => {
    if (wasStreamingRef.current && !isActuallyStreaming) {
      // Streaming just ended, reset scroll state
      // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional: syncing state with streaming end
      setUserScrolledUp(false);
    }
    wasStreamingRef.current = isActuallyStreaming;
  }, [isActuallyStreaming]);

  // Auto scroll - only for new messages, not when loading history
  useEffect(() => {
    if (userScrolledUp) return;
    
    // Don't auto-scroll if all messages are history (loaded from backend)
    const hasNewMessages = messages.some(m => !m.isHistory && !m.id.startsWith('loaded-'));
    if (!hasNewMessages && messages.length > 0) return;
    
    if (justSentMessage) {
      setTimeout(() => {
        lastUserMessageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        setJustSentMessage(false);
      }, 100);
    } else if (hasNewMessages) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, userScrolledUp, justSentMessage]);

  // Streaming scroll
  // [Repair #28]Add scrollInterval Cleanup
  const scrollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  useEffect(() => {
    if (isActuallyStreaming && !userScrolledUp) {
      scrollIntervalRef.current = setInterval(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 300);
      return () => {
        if (scrollIntervalRef.current) {
          clearInterval(scrollIntervalRef.current);
          scrollIntervalRef.current = null;
        }
      };
    }
  }, [isActuallyStreaming, userScrolledUp]);

  // Auto resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [localInput]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setLocalInput(e.target.value);
  }, []);

  const onSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (localInput.trim() && !isLoading) {
      const messageText = localInput.trim();
      
      // #region debug log A
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'MinimalChatArea.tsx:409',message:'onSubmit called',data:{messageText,isLoading,apiUrl},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      
      setUserScrolledUp(false);
      setJustSentMessage(true);
      setLocalInput('');
      
      try {
        // #region debug log A
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'MinimalChatArea.tsx:419',message:'sendMessage called',data:{messageText},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
        
        await sendMessage({ text: messageText });
        
        // #region debug log A
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'MinimalChatArea.tsx:422',message:'sendMessage completed',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
      } catch (err) {
        // #region debug log A
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'MinimalChatArea.tsx:425',message:'sendMessage error',data:{error:err instanceof Error?err.message:String(err)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
        console.error('[MinimalChatArea] Error:', err);
      }
    }
  }, [localInput, isLoading, sendMessage, apiUrl]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e as unknown as React.FormEvent);
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className={cn('minimal-main', className)} style={style}>
      <div className="minimal-grain-overlay" aria-hidden="true" />
      
      <div 
        className="minimal-chat"
        ref={chatContainerRef}
        onScroll={handleScroll}
      >
        <div className="minimal-chat-inner">
          <AnimatePresence mode="wait">
            {isEmpty ? (
              <WelcomeScreen key="welcome" onExample={setLocalInput} />
            ) : (
              <motion.div
                key="messages"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2 }}
              >
                {messages.map((message, index) => {
                  const isLastUserMessage = message.role === 'user' && 
                    messages.slice(index + 1).every(m => m.role !== 'user');
                  
                  // Skip animation for historical messages
                  const skipAnimation = message.isHistory || message.id.startsWith('loaded-');
                  
                  // Use stable key: index for streaming messages, id for historical
                  const stableKey = skipAnimation ? message.id : `msg-${index}`;
                  
                  return (
                    <motion.div
                      key={stableKey}
                      ref={isLastUserMessage ? lastUserMessageRef : undefined}
                      initial={skipAnimation ? false : { opacity: 0, y: 15, filter: 'blur(4px)' }}
                      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                      transition={skipAnimation ? { duration: 0 } : { duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
                      style={{ willChange: skipAnimation ? undefined : 'transform, opacity, filter' }}
                    >
                      <MinimalMessage
                        role={message.role === 'system' ? 'assistant' : message.role}
                        content={(message as unknown as { content?: string }).content || ''}
                        parts={message.parts}
                        isStreaming={isLoading && index === messages.length - 1 && message.role === 'assistant'}
                        skipAnimation={skipAnimation}
                      />
                    </motion.div>
                  );
                })}
                
                <div ref={messagesEndRef} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <motion.div 
        className="minimal-input-area"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ...springs.smooth, delay: 0.1 }}
      >
        <div className="minimal-input-container">
          <form onSubmit={onSubmit}>
            <motion.div 
              className="minimal-input-box"
              animate={{
                boxShadow: isFocused 
                  ? '0 0 0 1px rgba(255,255,255,0.15), 0 4px 20px rgba(0,0,0,0.3)' 
                  : '0 0 0 1px rgba(255,255,255,0.06), 0 2px 8px rgba(0,0,0,0.2)',
              }}
              transition={{ duration: 0.2 }}
              style={{ willChange: 'box-shadow' }}
            >
              {/* Mode Selector */}
              <div className="minimal-mode-selector" ref={modeMenuRef}>
                <motion.button
                  type="button"
                  className="minimal-mode-btn"
                  onClick={() => setModeMenuOpen(o => !o)}
                  whileHover={{ backgroundColor: 'rgba(255,255,255,0.08)' }}
                  whileTap={{ scale: 0.98 }}
                  style={{ color: MODE_CONFIG[currentMode].color }}
                >
                  {(() => {
                    const Icon = MODE_CONFIG[currentMode].icon;
                    return <Icon className="w-4 h-4" />;
                  })()}
                  <span className="minimal-mode-label">{MODE_CONFIG[currentMode].label}</span>
                  <ChevronRight className={cn("w-3 h-3 transition-transform", modeMenuOpen && "rotate-90")} />
                </motion.button>
                
                <AnimatePresence>
                  {modeMenuOpen && (
                    <motion.div
                      className="minimal-mode-menu"
                      initial={{ opacity: 0, y: 8, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.95 }}
                      transition={{ duration: 0.15 }}
                    >
                      {(Object.keys(MODE_CONFIG) as AgentMode[]).map((mode, i) => {
                        const config = MODE_CONFIG[mode];
                        const Icon = config.icon;
                        return (
                          <motion.button
                            key={mode}
                            type="button"
                            className={cn("minimal-mode-option", currentMode === mode && "active")}
                            onClick={() => { setCurrentMode(mode); setModeMenuOpen(false); }}
                            whileHover={{ backgroundColor: 'rgba(255,255,255,0.08)' }}
                          >
                            <Icon className="w-4 h-4" style={{ color: config.color }} />
                            <div className="minimal-mode-option-text">
                              <span className="minimal-mode-option-label">{config.label}</span>
                              <span className="minimal-mode-option-desc">{config.desc}</span>
                            </div>
                            <kbd className="minimal-mode-kbd">⌘{i + 1}</kbd>
                          </motion.button>
                        );
                      })}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
              
              <textarea
                ref={textareaRef}
                value={localInput}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder="Message NogicOS..."
                rows={1}
                disabled={isLoading}
                className="minimal-textarea"
              />
              <AnimatePresence mode="wait">
                {isLoading ? (
                  <StopButton key="stop" onClick={stop} />
                ) : (
                  <SendButton key="send" disabled={!localInput.trim()} />
                )}
              </AnimatePresence>
            </motion.div>
          </form>
          <motion.div 
            className="minimal-input-meta"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.3 }}
          >
            <span className="minimal-input-hint">
              <kbd>Enter</kbd> to send · <kbd>⌘.</kbd> switch mode
            </span>
            <span className="minimal-model-badge" style={{ color: MODE_CONFIG[currentMode].color }}>
              <motion.span 
                className="minimal-status-dot"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                style={{ backgroundColor: MODE_CONFIG[currentMode].color }}
              />
              {MODE_CONFIG[currentMode].label}
            </span>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}

// === ANIMATED COMPONENTS ===

function LoadingDots() {
  return (
    <div className="minimal-loading">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="minimal-loading-dot"
          animate={{ y: [0, -6, 0], opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
          style={{ willChange: 'transform, opacity' }}
        />
      ))}
    </div>
  );
}

function SendButton({ disabled }: { disabled: boolean }) {
  return (
    <motion.button
      type="submit"
      disabled={disabled}
      className="minimal-send-btn"
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.8, opacity: 0 }}
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.92 }}
      transition={springs.micro}
      style={{ willChange: 'transform' }}
    >
      <motion.div animate={{ y: disabled ? 0 : [0, -1, 0] }} transition={{ duration: 0.3 }}>
        <ArrowUp className="w-4 h-4" />
      </motion.div>
    </motion.button>
  );
}

function StopButton({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      type="button"
      onClick={onClick}
      className="minimal-send-btn minimal-send-btn--stop"
      initial={{ scale: 0.8, opacity: 0, rotate: -90 }}
      animate={{ scale: 1, opacity: 1, rotate: 0 }}
      exit={{ scale: 0.8, opacity: 0, rotate: 90 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.92 }}
      transition={springs.micro}
      style={{ background: 'var(--m-gray-700)', willChange: 'transform' }}
    >
      <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ duration: 1.5, repeat: Infinity }}>
        <Square className="w-3 h-3" fill="currentColor" />
      </motion.div>
    </motion.button>
  );
}

function WelcomeScreen({ onExample }: { onExample: (text: string) => void }) {
  const examples = [
    { text: 'Organize desktop', full: 'Organize my desktop files' },
    { text: 'Find recent files', full: 'Search recently modified files' },
    { text: 'Open Hacker News', full: 'Open Hacker News' },
    { text: 'Run git status', full: 'Run git status' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ duration: 0.4 }}
      className="minimal-welcome-v2"
    >
      <div className="minimal-hero">
        <motion.h1 
          className="minimal-hero-title"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          NogicOS
        </motion.h1>
        <motion.p 
          className="minimal-hero-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          AI that lives in your computer
        </motion.p>
      </div>

      <motion.div 
        className="minimal-quick-actions"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.35 }}
      >
        <span className="minimal-quick-label">Try</span>
        <div className="minimal-pills">
          {examples.map((example, i) => (
            <motion.button
              key={example.text}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.4 + i * 0.05 }}
              whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.08)' }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onExample(example.full)}
              className="minimal-pill"
            >
              {example.text}
            </motion.button>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}

// === MESSAGE COMPONENTS ===

interface MinimalMessageProps {
  role: 'user' | 'assistant';
  content?: string;
  parts?: MessagePart[];
  isStreaming?: boolean;
  skipAnimation?: boolean;
}

function StreamingText({ text, isStreaming, onComplete }: { text: string; isStreaming: boolean; onComplete?: () => void }) {
  const containerRef = useRef<HTMLSpanElement>(null);
  const displayedRef = useRef(0);
  const textRef = useRef(text);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const completedRef = useRef(false);
  const isStreamingRef = useRef(isStreaming);
  const onCompleteRef = useRef(onComplete);

  // Update refs in effect to avoid render-phase mutation
  useEffect(() => {
    textRef.current = text;
    isStreamingRef.current = isStreaming;
    onCompleteRef.current = onComplete;
  });

  const updateDisplay = (length: number) => {
    if (!containerRef.current) return;
    containerRef.current.textContent = textRef.current.slice(0, length);
  };

  useEffect(() => {
    const tick = () => {
      const target = textRef.current;
      const current = displayedRef.current;
      
      if (current >= target.length) {
        if (!isStreamingRef.current && !completedRef.current) {
          completedRef.current = true;
          onCompleteRef.current?.();
        } else {
          timeoutRef.current = setTimeout(tick, 50);
        }
        return;
      }

      displayedRef.current = current + 1;
      updateDisplay(current + 1);

      const char = target[current];
      const isCJK = /[\u4e00-\u9fff\u3400-\u4dbf\uac00-\ud7af\u3040-\u309f\u30a0-\u30ff]/.test(char);
      const delay = isCJK ? 35 : 12;

      timeoutRef.current = setTimeout(tick, delay);
    };

    tick();

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  return <span ref={containerRef} className="whitespace-pre-wrap" />;
}

// === TOOL DISPLAY HELPERS ===

interface ToolInfo {
  type: string;
  toolCallId: string;
  toolName?: string;
  state: string;
  input?: Record<string, unknown>;
  output?: unknown;
  errorText?: string;
}

// === SCREENSHOT OUTPUT ===

interface ScreenshotData {
  type: 'browser_screenshot';
  image_base64: string;
  page_content?: string;
  url?: string;
  title?: string;
}

function _parseToolOutput(output: unknown): unknown {
  if (!output) return null;
  // If it's a string, try to parse as JSON
  if (typeof output === 'string') {
    try {
      return JSON.parse(output);
    } catch {
      return output;
    }
  }
  return output;
}
void _parseToolOutput; // Suppress unused warning

function getScreenshotData(output: unknown): ScreenshotData | null {
  if (!output) return null;
  
  // Try to parse if string
  let data: unknown = output;
  if (typeof data === 'string') {
    try {
      data = JSON.parse(data);
    } catch {
      return null;
    }
  }
  
  // Check if it's a screenshot object
  if (data && typeof data === 'object') {
    const obj = data as Record<string, unknown>;
    // Direct match
    if (obj.type === 'browser_screenshot' && obj.image_base64) {
      return data as ScreenshotData;
    }
    // Check if it has image_base64 (maybe type is slightly different)
    if (obj.image_base64 && typeof obj.image_base64 === 'string' && obj.image_base64.length > 100) {
      // [P0-7 FIX] Enhanced security: Validate base64 is a valid PNG/JPEG image
      try {
        // Decode enough bytes to check file magic bytes (400 base64 chars = ~300 bytes)
        const decoded = atob(obj.image_base64.slice(0, 400));

        // [P0-7 FIX] Validate PNG magic bytes: 0x89 'P' 'N' 'G' 0x0D 0x0A 0x1A 0x0A
        const isPNG = decoded.charCodeAt(0) === 0x89 &&
                      decoded.slice(1, 4) === 'PNG';

        // [P0-7 FIX] Validate JPEG magic bytes: 0xFF 0xD8 0xFF
        const isJPEG = decoded.charCodeAt(0) === 0xFF &&
                       decoded.charCodeAt(1) === 0xD8 &&
                       decoded.charCodeAt(2) === 0xFF;

        // Only allow PNG and JPEG images
        if (!isPNG && !isJPEG) {
          console.warn('[Security] Blocked non-image base64 content (not PNG/JPEG)');
          return null;
        }

        // [P0-7 FIX] Additional check: Block any SVG/XML/HTML markers anywhere in first 300 bytes
        const lowerDecoded = decoded.toLowerCase();
        const blockedPatterns = ['<svg', '<?xml', '<!doctype', '<html', '<script', 'javascript:'];
        for (const pattern of blockedPatterns) {
          if (lowerDecoded.includes(pattern)) {
            console.warn(`[Security] Blocked potential injection (${pattern}) in image_base64`);
            return null;
          }
        }
      } catch {
        // Invalid base64
        console.warn('[Security] Invalid base64 in image_base64');
        return null;
      }

      return {
        type: 'browser_screenshot',
        image_base64: obj.image_base64,
        page_content: obj.page_content as string | undefined,
        url: obj.url as string | undefined,
        title: obj.title as string | undefined,
      };
    }
  }
  
  return null;
}

// isScreenshotOutput removed - was used by ToolWidget which was removed

const ScreenshotOutput = memo(function ScreenshotOutput({ data }: { data: ScreenshotData }) {
  const [imageExpanded, setImageExpanded] = useState(false);
  
  return (
    <div className="screenshot-output">
      {/* URL & Title */}
      {(data.url || data.title) && (
        <div className="screenshot-header">
          {data.title && <span className="screenshot-title">{data.title}</span>}
          {data.url && (
            <a 
              href={data.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="screenshot-url"
            >
              {data.url}
            </a>
          )}
        </div>
      )}
      
      {/* Screenshot Image */}
      <motion.div 
        className={cn("screenshot-image-container", imageExpanded && "expanded")}
        onClick={() => setImageExpanded(e => !e)}
        whileHover={{ scale: 1.01 }}
        transition={{ duration: 0.15 }}
      >
        <img 
          src={`data:image/png;base64,${data.image_base64}`}
          alt={data.title || 'Browser Screenshot'}
          className="screenshot-image"
        />
        <div className="screenshot-overlay">
          <span>{imageExpanded ? 'Click to collapse' : 'Click to expand'}</span>
        </div>
      </motion.div>
      
      {/* Page Content Preview */}
      {data.page_content && (
        <details className="screenshot-content">
          <summary>Page Content</summary>
          <pre>{data.page_content}</pre>
        </details>
      )}
    </div>
  );
});

// Get filename from path
function getFileName(path: string): string {
  if (!path) return '';
  return path.split(/[/\\]/).pop() || path;
}

// Format tool display based on type
function formatToolDisplay(toolName: string, input: Record<string, unknown> | undefined) {
  const name = toolName.toLowerCase().replace(/^tool-/, '');
  const str = (v: unknown) => typeof v === 'string' ? v : '';
  const num = (v: unknown) => typeof v === 'number' ? v : 0;
  
  switch (name) {
    case 'read_file': {
      const fileName = getFileName(str(input?.target_file));
      const offset = num(input?.offset);
      const limit = num(input?.limit);
      const lines = offset && limit ? `L${offset}-${offset + limit}` : '';
      return {
        icon: <FileText className="w-3.5 h-3.5" />,
        label: `Read ${fileName}${lines ? ' ' + lines : ''}`,
        category: 'explore'
      };
    }
    
    case 'list_dir':
      return {
        icon: <Folder className="w-3.5 h-3.5" />,
        label: `Listed ${getFileName(str(input?.target_directory))}`,
        category: 'explore'
      };
    
    case 'codebase_search': {
      const query = str(input?.query);
      return {
        icon: <Search className="w-3.5 h-3.5" />,
        label: `Searched "${query.length > 30 ? query.slice(0, 30) + '...' : query}"`,
        category: 'search'
      };
    }
    
    case 'grep':
      return {
        icon: <Code className="w-3.5 h-3.5" />,
        label: `Grep ${str(input?.pattern)}`,
        category: 'search'
      };
    
    case 'glob_file_search':
    case 'file_search':
      return {
        icon: <Search className="w-3.5 h-3.5" />,
        label: `Search files ${str(input?.glob_pattern) || str(input?.pattern)}`,
        category: 'search'
      };

    case 'browser_navigate':
    case 'browser_click':
    case 'browser_type':
    case 'browser_snapshot':
      return {
        icon: <Globe className="w-3.5 h-3.5" />,
        label: name.replace('browser_', '').replace(/_/g, ' '),
        category: 'browser'
      };
    
    case 'run_terminal_cmd': {
      const cmd = str(input?.command);
      return {
        icon: <Terminal className="w-3.5 h-3.5" />,
        label: `Run ${cmd.length > 40 ? cmd.slice(0, 40) + '...' : cmd}`,
        category: 'terminal'
      };
    }
    
    default:
      return {
        icon: <Terminal className="w-3.5 h-3.5" />,
        label: name.replace(/_/g, ' '),
        category: 'other'
      };
  }
}

// Group tools by category - removed, using ToolItemCursor individually

// Cursor-style: Single tool item with inline result display
const ToolItemCursor = memo(function ToolItemCursor({ tool }: { tool: ToolInfo }) {
  const [expanded, setExpanded] = useState(false);
  
  const toolName = tool.toolName || tool.type?.replace(/^tool-/, '') || 'unknown';
  const display = formatToolDisplay(toolName, tool.input);
  const _isComplete = tool.state === 'output-available'; // Reserved for future use
  const isError = tool.state === 'error' || !!tool.errorText;
  const isRunning = tool.state === 'input-streaming' || tool.state === 'input-available';
  const hasOutput = !!tool.output;
  void _isComplete;
  
  // Parse output and check for screenshot
  const screenshotData = useMemo(() => getScreenshotData(tool.output), [tool.output]);
  const isScreenshot = toolName.includes('screenshot') || screenshotData !== null;
  
  return (
    <motion.div 
      className="tool-item-cursor"
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      {/* Tool header line */}
      <div 
        className={cn("tool-item-header", hasOutput && !isScreenshot && "clickable")}
        onClick={() => hasOutput && !isScreenshot && setExpanded(e => !e)}
      >
        <span className="tool-item-status">
          {isError ? <AlertCircle className="w-3.5 h-3.5 text-red-400" />
           : isRunning ? <Loader2 className="w-3.5 h-3.5 text-neutral-400 animate-spin" />
           : <Check className="w-3.5 h-3.5 text-emerald-400" />}
        </span>
        <span className="tool-item-label">{display.label}</span>
        {hasOutput && !isScreenshot && (
          <ChevronRight className={cn("w-3.5 h-3.5 tool-item-chevron", expanded && "expanded")} />
        )}
      </div>
      
      {/* Screenshot results - always visible */}
      {screenshotData && (
        <motion.div
          className="tool-item-screenshot"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <ScreenshotOutput data={screenshotData} />
        </motion.div>
      )}
      
      {/* Other results - expandable */}
      <AnimatePresence>
        {expanded && hasOutput && !isScreenshot && (
          <motion.div
            className="tool-item-output"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <pre>{typeof tool.output === 'string' ? tool.output.slice(0, 500) : JSON.stringify(tool.output, null, 2).slice(0, 500)}</pre>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});

// Cursor-style operations list - each tool on its own line
const OperationGroup = memo(function OperationGroup({ tools }: { tools: ToolInfo[] }) {
  if (tools.length === 0) return null;
  
  return (
    <div className="operations-list-cursor">
      {tools.map((tool, index) => (
        <ToolItemCursor key={tool.toolCallId || index} tool={tool} />
      ))}
    </div>
  );
});

// Legacy ToolWidget removed - using ToolItemCursor instead

const MinimalMessage = memo(function MinimalMessage({ role, content, parts, isStreaming, skipAnimation }: MinimalMessageProps) {
  const [thinkingOpen, setThinkingOpen] = useState(true);
  const [thinkingComplete, setThinkingComplete] = useState(skipAnimation ? true : false);
  const [thinkingAnimationDone, setThinkingAnimationDone] = useState(skipAnimation ? true : false);
  const [thinkingDuration, setThinkingDuration] = useState<number | null>(null);
  const [planningMinTimeElapsed, setPlanningMinTimeElapsed] = useState(skipAnimation ? true : false);
  const thinkingStartTime = useRef<number | null>(null);
  const planningStartTime = useRef<number | null>(null);
  const hasAutoCollapsed = useRef(false); // Track if we've auto-collapsed once
  const isUser = role === 'user';

  // [P1 FIX] Type-safe parts processing with runtime validation
  const textContent = useMemo(() => {
    if (!Array.isArray(parts)) return content || '';
    return parts
      .filter((p): p is { type: string; text: string } =>
        p && typeof p === 'object' && p.type === 'text' && typeof p.text === 'string'
      )
      .map(p => p.text)
      .join('') || content || '';
  }, [parts, content]);

  const reasoningText = useMemo(() => {
    if (!Array.isArray(parts)) return '';
    return parts
      .filter((p): p is { type: string; text: string } =>
        p && typeof p === 'object' && p.type === 'reasoning' && typeof p.text === 'string'
      )
      .map(p => p.text)
      .join('');
  }, [parts]);

  const toolInvocations = useMemo((): ToolInfo[] => {
    if (!Array.isArray(parts)) return [];
    return parts
      .filter((p) =>
        p && typeof p === 'object' && typeof p.type === 'string' &&
        (p.type.startsWith('tool-') || p.type === 'dynamic-tool')
      )
      .map((p) => {
        const part = p as MessagePart & { toolCallId?: string; toolName?: string; state?: string; input?: Record<string, unknown>; output?: unknown; errorText?: string };
        return {
          type: part.type,
          toolCallId: part.toolCallId || '',
          toolName: part.toolName,
          state: part.state || 'pending',
          input: part.input,
          output: part.output,
          errorText: part.errorText,
        };
      });
  }, [parts]);

  const hasReasoning = reasoningText.length > 0;
  const hasTools = toolInvocations.length > 0;
  
  // Track when planning starts and ensure minimum display time
  const shouldShowPlanning = isStreaming && !hasReasoning && !textContent;
  
  // Timer for minimum planning display time
  useEffect(() => {
    if (shouldShowPlanning) {
      if (planningStartTime.current === null) {
        planningStartTime.current = Date.now();
        // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional: reset timer on planning start
        setPlanningMinTimeElapsed(false);
      }
      // Ensure planning shows for at least 400ms to prevent flashing
      const timer = setTimeout(() => setPlanningMinTimeElapsed(true), 400);
      return () => clearTimeout(timer);
    }
  }, [shouldShowPlanning]);
  
  // Show planning if we should AND either: still in planning state OR minimum time hasn't elapsed
  const showPlanning = isStreaming && (shouldShowPlanning || (!planningMinTimeElapsed && !textContent));
  
  
  useEffect(() => {
    if (hasReasoning && thinkingStartTime.current === null) {
      thinkingStartTime.current = Date.now();
    }
    // Calculate duration when thinking completes
    if (thinkingComplete && thinkingStartTime.current && thinkingDuration === null) {
      setThinkingDuration(Math.round((Date.now() - thinkingStartTime.current) / 1000));
    }
  }, [hasReasoning, thinkingComplete, thinkingDuration]);
  
  // Auto-collapse thinking ONCE when response text appears (Cursor-style)
  useEffect(() => {
    if (textContent && thinkingComplete && !hasAutoCollapsed.current && !skipAnimation) {
      hasAutoCollapsed.current = true;
      const timer = setTimeout(() => setThinkingOpen(false), 300);
      return () => clearTimeout(timer);
    }
  }, [textContent, thinkingComplete, skipAnimation]);
  
  const showText = !hasReasoning || thinkingComplete;

  return (
    <div className="minimal-message">
      <div className="minimal-message-role">
        {isUser ? 'You' : 'NogicOS'}
      </div>
      
      <div className={`minimal-message-content ${isStreaming ? 'streaming' : ''}`}>
        <AnimatePresence mode="wait">
          {showPlanning ? (
            <motion.div
              key="planning"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
              className="minimal-planning"
            >
              <LoadingDots />
              <span className="minimal-planning-text">Planning next moves</span>
            </motion.div>
          ) : hasReasoning ? (
            <motion.div
              key="thinking"
              className={cn("minimal-thinking", isStreaming && !textContent && "thinking-active")}
              initial={skipAnimation ? false : { opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={skipAnimation ? { duration: 0 } : { duration: 0.35, delay: 0.35, ease: [0.4, 0, 0.2, 1] }}
            >
              <div className="minimal-thinking-header" onClick={() => setThinkingOpen(o => !o)}>
                <span className={`minimal-thinking-chevron ${thinkingOpen ? 'open' : ''}`}>
                  <ChevronRight className="w-3 h-3" />
                </span>
                <span className="minimal-thinking-status">
                  {isStreaming && !textContent 
                    ? 'Thinking...' 
                    : thinkingDuration !== null 
                      ? `Thought for ${thinkingDuration}s` 
                      : 'Thought process'}
                </span>
              </div>
              <AnimatePresence>
                {thinkingOpen && (
                  <motion.div 
                    className="minimal-thinking-content"
                    initial={{ opacity: 0, scaleY: 0.8, height: 0 }}
                    animate={{ opacity: 1, scaleY: 1, height: 'auto' }}
                    exit={{ opacity: 0, scaleY: 0.95, height: 0 }}
                    transition={{ 
                      duration: 0.35, 
                      ease: [0.32, 0.72, 0, 1],
                      opacity: { duration: 0.2 }
                    }}
                    style={{ transformOrigin: 'top', willChange: 'transform, opacity' }}
                  >
                    {thinkingAnimationDone || skipAnimation ? (
                      <span className="whitespace-pre-wrap">{reasoningText}</span>
                    ) : (
                      <StreamingText 
                        text={reasoningText} 
                        isStreaming={!!(isStreaming && !textContent)}
                        onComplete={() => {
                          setThinkingAnimationDone(true);
                          const startTime = thinkingStartTime.current || Date.now();
                          const elapsed = Date.now() - startTime;
                          const minDisplayTime = 1500;
                          const remainingTime = Math.max(0, minDisplayTime - elapsed);
                          setTimeout(() => setThinkingComplete(true), remainingTime + 300);
                        }}
                      />
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ) : null}
        </AnimatePresence>

        {/* Operations/Tools - Cursor style grouped display */}
        <AnimatePresence>
          {hasTools && (
            <motion.div
              className="minimal-tools"
              initial={skipAnimation ? false : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={skipAnimation ? { duration: 0 } : { duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            >
              <OperationGroup tools={toolInvocations} />
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {textContent && showText && (
            <motion.div 
              className="minimal-prose"
              initial={skipAnimation ? false : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={skipAnimation ? { duration: 0 } : { duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
            >
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => <h1 className="text-xl font-semibold text-white mt-4 mb-2">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-lg font-semibold text-white mt-3 mb-2">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-base font-medium text-white mt-2 mb-1">{children}</h3>,
                  p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                  li: ({ children }) => <li className="text-neutral-300">{children}</li>,
                  strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
                  em: ({ children }) => <em className="italic text-neutral-200">{children}</em>,
                  code: ({ className, children }) => {
                    const match = /language-(\w+)/.exec(className || '');
                    const isBlock = Boolean(match);
                    return isBlock ? (
                      <SyntaxHighlighter
                         
                        style={oneDark as Record<string, React.CSSProperties>}
                        language={match?.[1] || 'text'}
                        PreTag="div"
                        customStyle={{
                          margin: 0,
                          padding: '1rem',
                          borderRadius: '0.5rem',
                          fontSize: '0.875rem',
                          lineHeight: '1.5',
                        }}
                        showLineNumbers={String(children).split('\n').length > 5}
                        lineNumberStyle={{
                          minWidth: '2.5em',
                          paddingRight: '1em',
                          color: '#666',
                          userSelect: 'none',
                        }}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className="bg-neutral-800 px-1.5 py-0.5 rounded text-sm font-mono text-neutral-200">{children}</code>
                    );
                  },
                  pre: ({ children }) => <div className="my-3 overflow-x-auto">{children}</div>,
                  a: ({ href, children }) => {
                    // [P0 FIX Round 1] XSS prevention: validate URL protocol
                    const isSafeUrl = href && (
                      href.startsWith('http://') ||
                      href.startsWith('https://') ||
                      href.startsWith('mailto:') ||
                      href.startsWith('#')
                    );
                    if (!isSafeUrl) {
                      // Block javascript:, data:, vbscript:, and other dangerous protocols
                      return <span className="text-neutral-400">{children}</span>;
                    }
                    return (
                      <a href={href} className="text-white underline underline-offset-2 hover:text-neutral-300" target="_blank" rel="noopener noreferrer">
                        {children}
                      </a>
                    );
                  },
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-2 border-neutral-700 pl-4 my-3 text-neutral-400 italic">{children}</blockquote>
                  ),
                  hr: () => <hr className="border-neutral-800 my-4" />,
                  table: ({ children }) => (
                    <div className="my-3 overflow-x-auto">
                      <table className="w-full text-sm border-collapse">{children}</table>
                    </div>
                  ),
                  thead: ({ children }) => <thead className="border-b border-neutral-700">{children}</thead>,
                  tbody: ({ children }) => <tbody>{children}</tbody>,
                  tr: ({ children }) => <tr className="border-b border-neutral-800 last:border-0">{children}</tr>,
                  th: ({ children }) => <th className="text-left py-2 px-3 font-medium text-neutral-300">{children}</th>,
                  td: ({ children }) => <td className="py-2 px-3 text-neutral-400">{children}</td>,
                }}
              >
                {textContent}
              </ReactMarkdown>
              {isStreaming && <span className="minimal-cursor" />}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
});
