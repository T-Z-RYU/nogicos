/**
 * BubbleChatPanel - Right-side chat panel for Bubble mode
 * 
 * Features:
 * - Display chat messages
 * - Real-time tool call visualization
 * - Highlight currently active app tag
 */

import { memo, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Globe,
  Code2,
  FileText,
  AppWindow,
  Zap,
  Eye,
  Pencil,
  Check,
  Loader2,
  AlertCircle,
  User,
  Bot,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface ConnectedApp {
  hwnd: number;
  title: string;
  app_name: string;
  app_display_name: string;
  icon_base64?: string;
  is_browser: boolean;
  connected_at: string;
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

interface BubbleChatPanelProps {
  connectedApps: ConnectedApp[];
  messages: ChatMessage[];
  activeAppHwnd?: number;
  aiState: 'idle' | 'thinking' | 'reading' | 'acting' | 'success';
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const SPRING = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
};

// App icon mapping
const APP_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  'Google Chrome': Globe,
  'Chrome': Globe,
  'VS Code': Code2,
  'Cursor': Code2,
  'Figma': AppWindow,
  'Notion': FileText,
};

function getAppIcon(appName: string) {
  if (APP_ICONS[appName]) return APP_ICONS[appName];
  for (const [key, icon] of Object.entries(APP_ICONS)) {
    if (appName.toLowerCase().includes(key.toLowerCase())) return icon;
  }
  return AppWindow;
}

// ============================================================================
// AppTag Component
// ============================================================================

interface AppTagProps {
  app: ConnectedApp;
  isActive: boolean;
}

const AppTag = memo(function AppTag({ app, isActive }: AppTagProps) {
  const Icon = getAppIcon(app.app_display_name);
  
  return (
    <motion.div
      className={cn(
        "flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs",
        "transition-all duration-200",
        isActive
          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
          : "bg-white/5 text-white/50 border border-transparent"
      )}
      animate={isActive ? { scale: [1, 1.02, 1] } : undefined}
      transition={{ duration: 0.3 }}
    >
      {app.icon_base64 ? (
        <img src={app.icon_base64} alt="" className="w-3.5 h-3.5 rounded" />
      ) : (
        <Icon className="w-3.5 h-3.5" />
      )}
      <span className="max-w-[80px] truncate">{app.app_display_name}</span>
      {isActive && (
        <motion.span
          className="w-1.5 h-1.5 rounded-full bg-emerald-400"
          animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      )}
    </motion.div>
  );
});

// ============================================================================
// ToolCallCard Component
// ============================================================================

interface ToolCallCardProps {
  invocation: ToolInvocation;
}

const ToolCallCard = memo(function ToolCallCard({ invocation }: ToolCallCardProps) {
  const getStatusIcon = () => {
    switch (invocation.state) {
      case 'result': return <Check className="w-3.5 h-3.5 text-emerald-400" />;
      case 'call': return <Loader2 className="w-3.5 h-3.5 text-white animate-spin" />;
      default: return <Loader2 className="w-3.5 h-3.5 text-white/30 animate-spin" />;
    }
  };

  const getTypeIcon = () => {
    const name = invocation.toolName.toLowerCase();
    if (name.includes('read') || name.includes('get') || name.includes('snapshot')) {
      return <Eye className="w-3.5 h-3.5" />;
    }
    if (name.includes('click') || name.includes('type') || name.includes('fill')) {
      return <Pencil className="w-3.5 h-3.5" />;
    }
    return <Zap className="w-3.5 h-3.5" />;
  };

  return (
    <motion.div
      className={cn(
        "flex items-center gap-2 p-2 rounded-lg text-xs",
        invocation.state === 'result' ? "bg-emerald-500/10" : "bg-white/5"
      )}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={SPRING.snappy}
    >
      <div className={cn(
        "w-6 h-6 rounded-full flex items-center justify-center",
        invocation.state === 'result' ? "bg-emerald-500/20" : "bg-white/10"
      )}>
        {getStatusIcon()}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 text-white/70">
          {getTypeIcon()}
          <span className="font-medium truncate">{invocation.toolName}</span>
        </div>
      </div>
    </motion.div>
  );
});

// ============================================================================
// MessageBubble Component
// ============================================================================

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble = memo(function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  
  return (
    <motion.div
      className={cn(
        "flex gap-3",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={SPRING.gentle}
    >
      {/* Avatar */}
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
        isUser ? "bg-white/10" : "bg-emerald-500/20"
      )}>
        {isUser ? (
          <User className="w-4 h-4 text-white/60" />
        ) : (
          <Bot className="w-4 h-4 text-emerald-400" />
        )}
      </div>
      
      {/* Content */}
      <div className={cn(
        "flex-1 min-w-0 space-y-2",
        isUser ? "text-right" : "text-left"
      )}>
        {/* Text content */}
        {message.content && (
          <div className={cn(
            "inline-block max-w-[85%] p-3 rounded-2xl text-sm",
            isUser 
              ? "bg-white/10 text-white ml-auto rounded-br-md"
              : "bg-white/[0.03] text-white/90 mr-auto rounded-bl-md border border-white/[0.06]"
          )}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
                code: ({ children }) => (
                  <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs font-mono">
                    {children}
                  </code>
                ),
                ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        
        {/* Tool invocations */}
        {message.toolInvocations && message.toolInvocations.length > 0 && (
          <div className={cn(
            "space-y-1.5 max-w-[85%]",
            isUser ? "ml-auto" : "mr-auto"
          )}>
            {message.toolInvocations.map((inv) => (
              <ToolCallCard key={inv.toolCallId} invocation={inv} />
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
});

// ============================================================================
// Main BubbleChatPanel Component
// ============================================================================

export const BubbleChatPanel = memo(function BubbleChatPanel({
  connectedApps,
  messages,
  activeAppHwnd,
  aiState,
  className,
}: BubbleChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);
  
  return (
    <motion.div
      className={cn(
        "flex flex-col h-full",
        "bg-black/40 backdrop-blur-sm",
        "border-l border-white/[0.06]",
        className
      )}
      initial={{ x: '100%', opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: '100%', opacity: 0 }}
      transition={SPRING.gentle}
    >
      {/* Header: Connected Apps */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2 flex-wrap">
          {connectedApps.map(app => (
            <AppTag 
              key={app.hwnd} 
              app={app} 
              isActive={activeAppHwnd === app.hwnd}
            />
          ))}
        </div>
        
        {/* AI State indicator */}
        <div className="ml-auto flex items-center gap-1.5 text-[10px]">
          <motion.span 
            className="w-1.5 h-1.5 rounded-full"
            style={{ 
              backgroundColor: aiState === 'idle' ? '#10b981' : 
                              aiState === 'thinking' ? '#8b5cf6' :
                              aiState === 'reading' ? '#3b82f6' : 
                              aiState === 'acting' ? '#f59e0b' : '#10b981'
            }}
            animate={{ scale: aiState !== 'idle' ? [1, 1.3, 1] : 1 }}
            transition={{ duration: 0.8, repeat: aiState !== 'idle' ? Infinity : 0 }}
          />
          <span className="text-white/40">
            {aiState === 'idle' ? 'Ready' : 
             aiState === 'thinking' ? 'Thinking...' :
             aiState === 'reading' ? 'Reading...' :
             aiState === 'acting' ? 'Acting...' : 'Done'}
          </span>
        </div>
      </div>
      
      {/* Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-4 space-y-4"
      >
        <AnimatePresence mode="popLayout">
          {messages.length > 0 ? (
            messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))
          ) : (
            <motion.div 
              className="flex flex-col items-center justify-center h-full text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-3">
                <Bot className="w-6 h-6 text-white/20" />
              </div>
              <p className="text-white/30 text-sm">Send a message to start</p>
              <p className="text-white/20 text-xs mt-1">
                NogicOS will operate connected apps
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
});

export default BubbleChatPanel;
