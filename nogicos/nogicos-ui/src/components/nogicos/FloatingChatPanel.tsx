/**
 * FloatingChatPanel - 浮动对话框Component
 * 
 * 特点：
 * - 可拖拽Move
 * - 可收起/展On
 * - 毛玻璃Effect
 * - 不遮挡画布太多
 */

import { useState, useRef, memo, useCallback } from 'react';
import { motion, AnimatePresence, useDragControls } from 'motion/react';
import { MessageSquare, X, Minus, Maximize2, GripVertical, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { MessageBubble } from './MessageBubble';

// ============================================================================
// Types
// ============================================================================

interface ConnectedApp {
  hwnd: number;
  title: string;
  app_name: string;
  app_display_name: string;
  icon_base64?: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolInvocations?: ToolInvocation[];
}

interface ToolInvocation {
  toolCallId: string;
  toolName: string;
  args: Record<string, unknown>;
  state: 'partial-call' | 'call' | 'result';
  result?: unknown;
}

interface FloatingChatPanelProps {
  connectedApps: ConnectedApp[];
  messages: ChatMessage[];
  activeAppHwnd?: number;
  aiState?: 'idle' | 'thinking' | 'reading' | 'acting' | 'success';
  isLoading?: boolean;
  onClose?: () => void;
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const SPRING = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 300, damping: 25 },
};

// ============================================================================
// FloatingChatPanel Component
// ============================================================================

export const FloatingChatPanel = memo(function FloatingChatPanel({
  connectedApps,
  messages,
  activeAppHwnd,
  aiState = 'idle',
  isLoading = false,
  onClose,
  className,
}: FloatingChatPanelProps) {
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const constraintsRef = useRef<HTMLDivElement>(null);
  const dragControls = useDragControls();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // AutoScrolltoBottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // MessagechangetimeScroll
  useState(() => {
    scrollToBottom();
  });

  // Minizetime's SmallBubble
  if (isMinimized) {
    return (
      <motion.button
        className="fixed bottom-24 right-6 z-50"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0, opacity: 0 }}
        transition={SPRING.snappy}
        onClick={() => setIsMinimized(false)}
      >
        <motion.div
          className={cn(
            "w-14 h-14 rounded-full flex items-center justify-center",
            "bg-emerald-500/90 backdrop-blur-md shadow-lg shadow-emerald-500/30",
            "border border-emerald-400/50"
          )}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          animate={{
            boxShadow: aiState !== 'idle' 
              ? ['0 0 20px rgba(16, 185, 129, 0.5)', '0 0 40px rgba(16, 185, 129, 0.8)', '0 0 20px rgba(16, 185, 129, 0.5)']
              : '0 10px 40px rgba(16, 185, 129, 0.3)',
          }}
          transition={aiState !== 'idle' ? { duration: 1, repeat: Infinity } : {}}
        >
          <MessageSquare className="w-6 h-6 text-white" />
          {messages.length > 0 && (
            <motion.span
              className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-white text-emerald-600 text-[10px] font-bold flex items-center justify-center"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
            >
              {messages.length}
            </motion.span>
          )}
        </motion.div>
      </motion.button>
    );
  }

  return (
    <div ref={constraintsRef} className="fixed inset-0 pointer-events-none z-40">
      <motion.div
        className={cn(
          "pointer-events-auto absolute",
          isMaximized ? "inset-4" : "bottom-24 right-6",
          className
        )}
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ 
          scale: 1, 
          opacity: 1, 
          y: 0,
          width: isMaximized ? 'auto' : 380,
          height: isMaximized ? 'auto' : 480,
        }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        transition={SPRING.gentle}
        drag={!isMaximized}
        dragControls={dragControls}
        dragMomentum={false}
        dragConstraints={constraintsRef}
        style={!isMaximized ? { x: position.x, y: position.y } : undefined}
        onDragEnd={(_, info) => {
          setPosition(prev => ({
            x: prev.x + info.offset.x,
            y: prev.y + info.offset.y,
          }));
        }}
      >
        <div
          className={cn(
            "flex flex-col h-full rounded-2xl overflow-hidden",
            "bg-black/70 backdrop-blur-xl",
            "border border-white/10",
            "shadow-2xl shadow-black/50"
          )}
        >
          {/* Header - 可拖拽区域 */}
          <div
            className="flex items-center justify-between px-4 py-3 border-b border-white/10 cursor-grab active:cursor-grabbing"
            onPointerDown={(e) => {
              if (!isMaximized) {
                dragControls.start(e);
              }
            }}
          >
            <div className="flex items-center gap-2">
              <GripVertical className="w-4 h-4 text-white/30" />
              <div className="flex items-center gap-2">
                <motion.div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: aiState === 'idle' ? '#10b981' : '#8b5cf6' }}
                  animate={{ scale: aiState !== 'idle' ? [1, 1.3, 1] : 1 }}
                  transition={{ duration: 0.8, repeat: aiState !== 'idle' ? Infinity : 0 }}
                />
                <span className="text-xs font-medium text-white/70">
                  {aiState === 'idle' ? 'NogicOS' : 
                   aiState === 'thinking' ? 'Thinking...' :
                   aiState === 'reading' ? 'Reading...' :
                   aiState === 'acting' ? 'Executing...' : 'Done!'}
                </span>
              </div>
            </div>
            
            <div className="flex items-center gap-1">
              {/* Min化 */}
              <button
                onClick={() => setIsMinimized(true)}
                className="w-7 h-7 rounded-lg hover:bg-white/10 flex items-center justify-center text-white/40 hover:text-white/70 transition-colors"
              >
                <Minus className="w-3.5 h-3.5" />
              </button>
              
              {/* Max化 */}
              <button
                onClick={() => setIsMaximized(!isMaximized)}
                className="w-7 h-7 rounded-lg hover:bg-white/10 flex items-center justify-center text-white/40 hover:text-white/70 transition-colors"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </button>
              
              {/* Close */}
              {onClose && (
                <button
                  onClick={onClose}
                  className="w-7 h-7 rounded-lg hover:bg-red-500/20 flex items-center justify-center text-white/40 hover:text-red-400 transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Connected Apps Tags */}
          {connectedApps.length > 0 && (
            <div className="flex flex-wrap gap-1.5 px-3 py-2 border-b border-white/5">
              {connectedApps.map(app => (
                <motion.div
                  key={app.hwnd}
                  className={cn(
                    "flex items-center gap-1.5 px-2 py-1 rounded-full text-[10px]",
                    activeAppHwnd === app.hwnd
                      ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                      : "bg-white/5 text-white/50"
                  )}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  layout
                >
                  {app.icon_base64 ? (
                    <img src={app.icon_base64} alt="" className="w-3 h-3 rounded" />
                  ) : (
                    <Zap className="w-3 h-3" />
                  )}
                  <span className="max-w-[80px] truncate">{app.app_display_name}</span>
                  {activeAppHwnd === app.hwnd && (
                    <motion.span
                      className="w-1.5 h-1.5 rounded-full bg-emerald-400"
                      animate={{ scale: [1, 1.3, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    />
                  )}
                </motion.div>
              ))}
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {/* #region agent log */}
            {(() => { fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'FloatingChatPanel.tsx:render',message:'H3: Rendering messages',data:{messagesCount:messages?.length,messagesValid:messages?.every(m=>m&&typeof m.id==='string')},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{}); return null; })()}
            {/* #endregion */}
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-white/30">
                <MessageSquare className="w-10 h-10 mb-3 opacity-50" />
                <p className="text-sm">Send a message to start</p>
                <p className="text-xs mt-1">NogicOS will operate connected apps</p>
              </div>
            ) : (
              <>
                <AnimatePresence initial={false}>
                  {messages.map((msg) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.2 }}
                    >
                      <MessageBubble 
                        message={msg} 
                        variant={msg.role === 'user' ? 'user' : 'assistant'}
                      />
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                {/* Loading indicator */}
                {isLoading && (
                  <motion.div
                    className="flex items-center gap-2 text-white/50 text-sm"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <motion.div
                      className="flex gap-1"
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                    </motion.div>
                    <span>AI processing...</span>
                  </motion.div>
                )}
                
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
});

export default FloatingChatPanel;
