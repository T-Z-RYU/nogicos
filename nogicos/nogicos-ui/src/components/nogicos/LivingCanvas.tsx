/**
 * LivingCanvas - 活的画布
 * 
 * 设计理念：
 * - Hook Map 不Yes功能，Yes体验的一部分
 * - 三层架构：Background层（神经Network）+ Inner容层（对话）+ 控制层（Input）
 * - Sexy & Joyful：呼吸感、数据流动、StateConvertAnimation
 * 
 * 参考：Linear 的动效、Arc 的Empty间感、Figma 的协作光标
 */

import { useState, useEffect, useRef, useMemo, useCallback, memo } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, animate } from 'motion/react';
import { 
  Globe, 
  Code2, 
  FileText, 
  AppWindow,
  Zap,
  Brain,
  Eye,
  Pencil,
  Sparkles,
  ArrowUp,
  Square,
  ChevronRight,
  Bot,
  Search,
  ListTodo,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface ConnectedApp {
  hwnd: number;
  title: string;
  app_name: string;
  app_display_name: string;
  is_browser: boolean;
  connected_at: string;
}

type AIState = 'idle' | 'reading' | 'thinking' | 'acting' | 'success';

interface DataFlowState {
  sourceHwnd: number | null;
  targetHwnd: number | null;
  direction: 'in' | 'out';
  action?: string;
}

interface ThinkingLogEntry {
  id: string;
  type: 'read' | 'think' | 'act' | 'success';
  content: string;
  timestamp: number;
  appName?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isHistory?: boolean;
}

interface LivingCanvasProps {
  // Hook relatedOff
  connectedApps: ConnectedApp[];
  dataFlow?: DataFlowState;
  aiState?: AIState;
  thinkingLog?: ThinkingLogEntry[];
  // DialogrelatedOff
  messages: ChatMessage[];
  isLoading?: boolean;
  onSendMessage: (content: string) => void;
  onStopExecution?: () => void;
  // Style
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const SPRING = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
  smooth: { type: 'spring' as const, stiffness: 200, damping: 20 },
  micro: { type: 'spring' as const, stiffness: 500, damping: 35 },
};

const COLORS = {
  emerald: {
    primary: '#10b981',
    light: '#34d399',
    dark: '#059669',
    glow: 'rgba(16, 185, 129, 0.3)',
    subtle: 'rgba(16, 185, 129, 0.08)',
  },
  sky: {
    primary: '#0ea5e9',
    light: '#38bdf8',
    glow: 'rgba(14, 165, 233, 0.3)',
  },
  violet: {
    primary: '#8b5cf6',
    light: '#a78bfa',
    glow: 'rgba(139, 92, 246, 0.3)',
  },
  amber: {
    primary: '#f59e0b',
    light: '#fbbf24',
    glow: 'rgba(245, 158, 11, 0.3)',
  },
};

const STATE_CONFIG = {
  idle: { color: COLORS.emerald, icon: Zap, label: 'Ready' },
  reading: { color: COLORS.sky, icon: Eye, label: 'Reading' },
  thinking: { color: COLORS.violet, icon: Brain, label: 'Thinking' },
  acting: { color: COLORS.amber, icon: Pencil, label: 'Acting' },
  success: { color: COLORS.emerald, icon: Sparkles, label: 'Done' },
};

// App icon mapping
const APP_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  'Google Chrome': Globe,
  'Chrome': Globe,
  'Mozilla Firefox': Globe,
  'Microsoft Edge': Globe,
  'VS Code': Code2,
  'Cursor': Code2,
  'File Explorer': FileText,
  'Finder': FileText,
  'Figma': AppWindow,
};

function getAppIcon(appName: string) {
  if (APP_ICONS[appName]) return APP_ICONS[appName];
  for (const [key, icon] of Object.entries(APP_ICONS)) {
    if (appName.toLowerCase().includes(key.toLowerCase())) return icon;
  }
  return AppWindow;
}

// ============================================================================
// Background Layer - Neural Network
// ============================================================================

const NeuralBackground = memo(function NeuralBackground({
  connectedApps,
  dataFlow,
  aiState = 'idle',
  dimensions,
}: {
  connectedApps: ConnectedApp[];
  dataFlow?: DataFlowState;
  aiState: AIState;
  dimensions: { width: number; height: number };
}) {
  const config = STATE_CONFIG[aiState];
  
  // Calculate positions
  const centerX = dimensions.width / 2;
  const centerY = dimensions.height * 0.35; // UpsideOffset，give dialog empty space
  const radius = Math.min(dimensions.width * 0.3, 180);

  const nodePositions = useMemo(() => {
    return connectedApps.map((app, index) => {
      const startAngle = -Math.PI / 2;
      const angle = startAngle + (2 * Math.PI * index) / Math.max(connectedApps.length, 1);
      return {
        app,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        angle,
      };
    });
  }, [connectedApps, centerX, centerY, radius]);

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {/* 微妙的网格Background */}
      <div 
        className="absolute inset-0 opacity-[0.015]"
        style={{
          backgroundImage: `
            radial-gradient(circle at 50% 35%, ${config.color.glow} 0%, transparent 50%),
            linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 60px 60px, 60px 60px',
        }}
      />

      {/* SVG Connect线 */}
      <svg 
        className="absolute inset-0" 
        width={dimensions.width} 
        height={dimensions.height}
        style={{ overflow: 'visible' }}
      >
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={config.color.primary} stopOpacity="0.1" />
            <stop offset="50%" stopColor={config.color.primary} stopOpacity="0.3" />
            <stop offset="100%" stopColor={config.color.primary} stopOpacity="0.1" />
          </linearGradient>
        </defs>

        {nodePositions.map(({ app, x, y }, index) => {
          const isActive = dataFlow?.sourceHwnd === app.hwnd;
          const flowColor = dataFlow?.direction === 'out' ? COLORS.amber : COLORS.sky;
          
          // bezierCurve
          const midX = (x + centerX) / 2;
          const midY = (y + centerY) / 2;
          const dx = centerX - x;
          const dy = centerY - y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const offset = dist * 0.12;
          const perpX = -dy / dist * offset;
          const perpY = dx / dist * offset;
          const ctrlX = midX + perpX;
          const ctrlY = midY + perpY;
          const pathD = `M ${x} ${y} Q ${ctrlX} ${ctrlY} ${centerX} ${centerY}`;

          return (
            <g key={app.hwnd}>
              {/* 基础线 - 始终Display */}
              <motion.path
                d={pathD}
                fill="none"
                stroke={isActive ? flowColor.primary : 'rgba(255,255,255,0.06)'}
                strokeWidth={isActive ? 1.5 : 0.5}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
              />

              {/* Active时的发光 */}
              {isActive && (
                <motion.path
                  d={pathD}
                  fill="none"
                  stroke={flowColor.light}
                  strokeWidth={3}
                  style={{ filter: 'blur(3px)' }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: [0.2, 0.4, 0.2] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
              )}

              {/* 数据脉冲 */}
              {isActive && dataFlow?.direction && (
                <>
                  {[0, 1, 2].map((i) => (
                    <motion.circle
                      key={i}
                      r={3}
                      fill={flowColor.light}
                      style={{ filter: `drop-shadow(0 0 4px ${flowColor.primary})` }}
                    >
                      <motion.animate
                        attributeName="cx"
                        values={dataFlow.direction === 'in' 
                          ? `${x};${ctrlX};${centerX}` 
                          : `${centerX};${ctrlX};${x}`
                        }
                        keyTimes="0;0.5;1"
                        dur="1.2s"
                        repeatCount="indefinite"
                        begin={`${i * 0.4}s`}
                      />
                      <motion.animate
                        attributeName="cy"
                        values={dataFlow.direction === 'in' 
                          ? `${y};${ctrlY};${centerY}` 
                          : `${centerY};${ctrlY};${y}`
                        }
                        keyTimes="0;0.5;1"
                        dur="1.2s"
                        repeatCount="indefinite"
                        begin={`${i * 0.4}s`}
                      />
                      <motion.animate
                        attributeName="opacity"
                        values="0;1;1;0"
                        keyTimes="0;0.1;0.9;1"
                        dur="1.2s"
                        repeatCount="indefinite"
                        begin={`${i * 0.4}s`}
                      />
                    </motion.circle>
                  ))}
                </>
              )}
            </g>
          );
        })}
      </svg>

      {/* 应用Node */}
      <AnimatePresence>
        {nodePositions.map(({ app, x, y }, index) => {
          const Icon = getAppIcon(app.app_display_name);
          const isActive = dataFlow?.sourceHwnd === app.hwnd;
          const flowColor = dataFlow?.direction === 'out' ? COLORS.amber : COLORS.sky;
          
          return (
            <motion.div
              key={app.hwnd}
              className="absolute pointer-events-auto"
              style={{ left: x, top: y, transform: 'translate(-50%, -50%)' }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ ...SPRING.snappy, delay: index * 0.08 }}
            >
              {/* Active光晕 */}
              {isActive && (
                <motion.div
                  className="absolute rounded-full"
                  style={{
                    width: 48, height: 48,
                    left: '50%', top: '50%',
                    x: '-50%', y: '-50%',
                    background: `radial-gradient(circle, ${flowColor.glow} 0%, transparent 70%)`,
                  }}
                  animate={{ scale: [1, 1.5, 1], opacity: [0.6, 0.2, 0.6] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
              )}
              
              {/* Node */}
              <div
                className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center",
                  "border transition-all duration-300 cursor-pointer",
                  isActive 
                    ? "border-white/30 bg-white/10" 
                    : "border-white/10 bg-black/40 hover:border-white/20"
                )}
              >
                <Icon className={cn(
                  "w-4 h-4 transition-colors",
                  isActive ? "text-white" : "text-white/40"
                )} />
              </div>
              
              {/* 标签 */}
              <div className="absolute top-full mt-1 left-1/2 -translate-x-1/2 whitespace-nowrap">
                <span className={cn(
                  "text-[10px] transition-colors",
                  isActive ? "text-white/80" : "text-white/30"
                )}>
                  {app.app_display_name}
                </span>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* Medium心 AI Node */}
      <motion.div
        className="absolute"
        style={{ left: centerX, top: centerY, transform: 'translate(-50%, -50%)' }}
        animate={{ scale: aiState === 'thinking' ? [1, 1.02, 1] : 1 }}
        transition={{ duration: 2, repeat: aiState === 'thinking' ? Infinity : 0 }}
      >
        {/* 思考波纹 */}
        <AnimatePresence>
          {aiState === 'thinking' && (
            <>
              {[1, 2, 3].map((i) => (
                <motion.div
                  key={i}
                  className="absolute rounded-full border"
                  style={{
                    width: 56, height: 56,
                    left: '50%', top: '50%',
                    x: '-50%', y: '-50%',
                    borderColor: config.color.primary,
                  }}
                  initial={{ scale: 1, opacity: 0.4 }}
                  animate={{ scale: 2.5, opacity: 0 }}
                  transition={{ duration: 2, repeat: Infinity, delay: i * 0.6 }}
                />
              ))}
            </>
          )}
        </AnimatePresence>

        {/* Outer圈光晕 */}
        <motion.div
          className="absolute rounded-full"
          style={{
            width: 72, height: 72,
            left: '50%', top: '50%',
            x: '-50%', y: '-50%',
            background: `radial-gradient(circle, ${config.color.glow} 0%, transparent 70%)`,
          }}
          animate={{
            scale: aiState === 'idle' ? [1, 1.1, 1] : [1, 1.15, 1],
            opacity: aiState === 'idle' ? 0.3 : 0.5,
          }}
          transition={{ duration: aiState === 'idle' ? 4 : 2, repeat: Infinity }}
        />

        {/* 主Node */}
        <motion.div
          className="relative w-14 h-14 rounded-full flex items-center justify-center overflow-hidden"
          style={{
            background: `linear-gradient(135deg, ${config.color.dark || config.color.primary} 0%, ${config.color.primary} 50%, ${config.color.light} 100%)`,
            boxShadow: `0 0 30px ${config.color.glow}`,
          }}
        >
          {/* 扫描线 */}
          <motion.div
            className="absolute inset-0"
            animate={{ rotate: 360 }}
            transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          >
            <div 
              className="absolute top-0 left-1/2 w-1/2 h-full origin-left"
              style={{ background: `linear-gradient(90deg, transparent 0%, ${config.color.light}20 100%)` }}
            />
          </motion.div>

          {/* StateGraph标 */}
          <motion.div
            key={aiState}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={SPRING.snappy}
          >
            {(() => {
              const StateIcon = config.icon;
              return <StateIcon className="w-6 h-6 text-white relative z-10" />;
            })()}
          </motion.div>
        </motion.div>

        {/* State标签 */}
        <motion.div 
          className="absolute top-full mt-2 left-1/2 -translate-x-1/2 text-center"
          key={aiState}
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="text-xs font-medium text-white/80">NogicOS</div>
          <div className="text-[10px]" style={{ color: config.color.light }}>
            {connectedApps.length > 0 ? `${connectedApps.length} connected` : config.label}
          </div>
        </motion.div>
      </motion.div>

      {/* EmptyState提示 */}
      {connectedApps.length === 0 && (
        <motion.div
          className="absolute left-1/2 -translate-x-1/2"
          style={{ top: centerY + 80 }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-white/20 text-xs text-center">
            Connect apps to see the magic
          </p>
        </motion.div>
      )}
    </div>
  );
});

// ============================================================================
// Status Bar
// ============================================================================

const StatusBar = memo(function StatusBar({
  aiState,
  thinkingLog,
}: {
  aiState: AIState;
  thinkingLog: ThinkingLogEntry[];
}) {
  const config = STATE_CONFIG[aiState];
  const latestEntry = thinkingLog[thinkingLog.length - 1];

  if (aiState === 'idle' && thinkingLog.length === 0) {
    return null;
  }

  const getIcon = (type: ThinkingLogEntry['type']) => {
    switch (type) {
      case 'read': return Eye;
      case 'think': return Brain;
      case 'act': return Pencil;
      case 'success': return Sparkles;
      default: return Zap;
    }
  };

  return (
    <motion.div
      className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06]"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={SPRING.snappy}
    >
      {/* State指示 */}
      <motion.div
        className="w-1.5 h-1.5 rounded-full"
        style={{ backgroundColor: config.color.primary }}
        animate={{ scale: aiState !== 'idle' ? [1, 1.3, 1] : 1 }}
        transition={{ duration: 1, repeat: aiState !== 'idle' ? Infinity : 0 }}
      />

      {/* Inner容 */}
      <AnimatePresence mode="wait">
        {latestEntry ? (
          <motion.div
            key={latestEntry.id}
            className="flex items-center gap-2"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
            transition={{ duration: 0.2 }}
          >
            {(() => {
              const Icon = getIcon(latestEntry.type);
              return <Icon className="w-3 h-3" style={{ color: config.color.light }} />;
            })()}
            <span className="text-[11px] text-white/60 truncate max-w-[200px]">
              {latestEntry.content}
            </span>
            {latestEntry.appName && (
              <span 
                className="text-[10px] px-1.5 py-0.5 rounded"
                style={{ 
                  backgroundColor: `${config.color.primary}15`,
                  color: config.color.light,
                }}
              >
                {latestEntry.appName}
              </span>
            )}
          </motion.div>
        ) : (
          <motion.span
            key="ready"
            className="text-[11px] text-white/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            Ready
          </motion.span>
        )}
      </AnimatePresence>
    </motion.div>
  );
});

// ============================================================================
// Message Bubble - semi-transparent version
// ============================================================================

const TransparentBubble = memo(function TransparentBubble({
  message,
  isStreaming,
}: {
  message: ChatMessage;
  isStreaming?: boolean;
}) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      className={cn(
        "max-w-[85%] rounded-2xl px-4 py-3",
        "backdrop-blur-md",
        isUser 
          ? "ml-auto bg-emerald-500/20 border border-emerald-500/20" 
          : "mr-auto bg-white/[0.04] border border-white/[0.06]"
      )}
      initial={message.isHistory ? false : { opacity: 0, y: 15, filter: 'blur(4px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={message.isHistory ? { duration: 0 } : { duration: 0.35 }}
    >
      {/* Role */}
      <div className={cn(
        "text-[10px] font-medium mb-1",
        isUser ? "text-emerald-400/80" : "text-white/40"
      )}>
        {isUser ? 'You' : 'NogicOS'}
      </div>

      {/* Content */}
      <div className={cn(
        "text-sm leading-relaxed whitespace-pre-wrap",
        isUser ? "text-white" : "text-white/90"
      )}>
        {message.content}
        {isStreaming && (
          <motion.span
            className="inline-block w-2 h-4 ml-0.5 bg-white/60 rounded-sm"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 0.8, repeat: Infinity }}
          />
        )}
      </div>
    </motion.div>
  );
});

// ============================================================================
// Input Area
// ============================================================================

const InputArea = memo(function InputArea({
  onSend,
  onStop,
  isLoading,
}: {
  onSend: (content: string) => void;
  onStop?: () => void;
  isLoading: boolean;
}) {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto resize
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
    }
  }, [input, isLoading, onSend]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <motion.div
        className={cn(
          "flex items-end gap-2 p-2 rounded-xl",
          "bg-white/[0.03] border transition-all duration-200",
          isFocused ? "border-white/20" : "border-white/[0.08]"
        )}
        animate={{
          boxShadow: isFocused 
            ? '0 0 0 1px rgba(255,255,255,0.1), 0 4px 20px rgba(0,0,0,0.3)' 
            : '0 2px 8px rgba(0,0,0,0.2)',
        }}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Message NogicOS..."
          rows={1}
          disabled={isLoading}
          className={cn(
            "flex-1 bg-transparent border-0 outline-none resize-none",
            "text-sm text-white placeholder:text-white/30",
            "py-2 px-2 max-h-[150px]"
          )}
        />

        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.button
              key="stop"
              type="button"
              onClick={onStop}
              className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/15 flex items-center justify-center transition-colors"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Square className="w-3.5 h-3.5 text-white" fill="currentColor" />
            </motion.button>
          ) : (
            <motion.button
              key="send"
              type="submit"
              disabled={!input.trim()}
              className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center transition-all",
                input.trim() 
                  ? "bg-emerald-500 hover:bg-emerald-400 text-white" 
                  : "bg-white/5 text-white/30"
              )}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              whileHover={input.trim() ? { scale: 1.05 } : undefined}
              whileTap={input.trim() ? { scale: 0.95 } : undefined}
            >
              <ArrowUp className="w-4 h-4" />
            </motion.button>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Hints */}
      <div className="flex items-center justify-between mt-2 px-1">
        <span className="text-[10px] text-white/20">
          <kbd className="px-1 py-0.5 rounded bg-white/5">Enter</kbd> to send
        </span>
        <motion.span 
          className="text-[10px] flex items-center gap-1"
          style={{ color: COLORS.emerald.light }}
        >
          <motion.span 
            className="w-1.5 h-1.5 rounded-full"
            style={{ backgroundColor: COLORS.emerald.primary }}
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          Ready
        </motion.span>
      </div>
    </form>
  );
});

// ============================================================================
// Main Component
// ============================================================================

export function LivingCanvas({
  connectedApps,
  dataFlow,
  aiState = 'idle',
  thinkingLog = [],
  messages,
  isLoading = false,
  onSendMessage,
  onStopExecution,
  className,
}: LivingCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Update dimensions
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };

    updateDimensions();
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    return () => resizeObserver.disconnect();
  }, []);

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const isEmpty = messages.length === 0;

  return (
    <div 
      ref={containerRef}
      className={cn(
        "relative w-full h-full flex flex-col overflow-hidden",
        "bg-[#0a0a0a]",
        className
      )}
    >
      {/* Background层 - 神经Network */}
      <NeuralBackground
        connectedApps={connectedApps}
        dataFlow={dataFlow}
        aiState={aiState}
        dimensions={dimensions}
      />

      {/* Inner容层 - 对话 */}
      <div className="relative flex-1 flex flex-col z-10">
        {/* Message区域 */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-2xl mx-auto">
            <AnimatePresence mode="popLayout">
              {isEmpty ? (
                <motion.div
                  key="welcome"
                  className="flex flex-col items-center justify-center h-full pt-[30vh]"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <motion.h1 
                    className="text-3xl font-semibold text-white mb-2"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    NogicOS
                  </motion.h1>
                  <motion.p 
                    className="text-white/40 text-sm"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    AI that works where you work
                  </motion.p>
                </motion.div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <TransparentBubble
                      key={message.id || index}
                      message={message}
                      isStreaming={isLoading && index === messages.length - 1 && message.role === 'assistant'}
                    />
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* 控制层 - State条 + Input框 */}
        <div className="px-4 pb-4">
          <div className="max-w-2xl mx-auto space-y-3">
            {/* State条 */}
            <div className="flex justify-center">
              <StatusBar aiState={aiState} thinkingLog={thinkingLog} />
            </div>

            {/* Input框 */}
            <InputArea 
              onSend={onSendMessage}
              onStop={onStopExecution}
              isLoading={isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default LivingCanvas;
