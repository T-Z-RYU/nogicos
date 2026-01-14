/**
 * LivingCanvasChat - Integration useChat 的 Living Canvas
 * 
 * 这个Component将 LivingCanvas 的视觉体验与 useChat 的MessageHandle结合起来
 */

import { useState, useRef, useEffect, useCallback, useMemo, memo } from 'react';
import type { KeyboardEvent } from 'react';
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import { motion, AnimatePresence } from 'motion/react';
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
  ArrowDown,
  Square,
  Check,
  Loader2,
  AlertCircle,
  Terminal,
  Search,
  Folder,
  Code,
  Link,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
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

interface MessagePart {
  type: string;
  text?: string;
  [key: string]: unknown;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  parts?: MessagePart[];
  isHistory?: boolean;
}

// interactRecord（forRightsidePanel）
interface ActionRecord {
  id: string;
  timestamp: Date;
  type: 'read' | 'write' | 'navigate' | 'click' | 'type';
  status: 'pending' | 'active' | 'done' | 'error';
  label: string;
  detail?: string;
  appHwnd?: number;
}

// ToolCallInfo
interface ToolCallInfo {
  id: string;
  name: string;
  state: 'pending' | 'running' | 'success' | 'error';
  input?: Record<string, unknown>;
  output?: unknown;
}

interface LivingCanvasChatProps {
  apiUrl?: string;
  sessionId: string;
  // Hook relatedOff
  connectedApps: ConnectedApp[];
  dataFlow?: DataFlowState;
  onDisconnect?: (hwnd: number) => void;
  onFocusWindow?: (hwnd: number) => void;
  // FocusedState（forOuterpartcontrolRightsidePanel）
  focusedApp?: ConnectedApp | null;
  onFocusChange?: (app: ConnectedApp | null) => void;
  // initialMessage
  initialMessages?: ChatMessage[];
  // Callback
  onSessionUpdate?: (title: string, preview: string) => void;
  onMessagesChange?: (messages: ChatMessage[]) => void;
  onToolCall?: (tool: ToolCallInfo) => void;
  onAiStateChange?: (state: AIState, action?: string) => void;
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
  idle: { 
    color: COLORS.emerald, 
    icon: Zap, 
    label: 'Ready',
    animation: 'pulse-slow',      // 3s Cyclebreathing
    ringCount: 0,
    glowScale: [1, 1.1, 1],
    glowDuration: 4,
  },
  reading: { 
    color: COLORS.sky, 
    icon: Eye, 
    label: 'Reading',
    animation: 'pulse-in',        // towardheartreceiveshrink
    ringCount: 2,
    glowScale: [1, 1.15, 1],
    glowDuration: 2,
  },
  thinking: { 
    color: COLORS.violet, 
    icon: Brain, 
    label: 'Thinking',
    animation: 'pulse-ripple',    // ripple spread
    ringCount: 3,
    glowScale: [1, 1.2, 1],
    glowDuration: 1.5,
  },
  acting: { 
    color: COLORS.amber, 
    icon: Pencil, 
    label: 'Acting',
    animation: 'pulse-out',       // spread outward
    ringCount: 2,
    glowScale: [1, 1.25, 1],
    glowDuration: 1,
  },
  success: { 
    color: COLORS.emerald, 
    icon: Sparkles, 
    label: 'Done',
    animation: 'celebrate',       // celebration sparkle
    ringCount: 1,
    glowScale: [1, 1.3, 1],
    glowDuration: 0.8,
  },
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

// FormatterRelativeTime
function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

// ============================================================================
// Connection Success Guide
// ============================================================================

interface ConnectionSuccessGuideProps {
  app: ConnectedApp;
  onDismiss: () => void;
  onSuggestionClick: (suggestion: string) => void;
}

const ConnectionSuccessGuide = memo(function ConnectionSuccessGuide({ 
  app, 
  onDismiss,
  onSuggestionClick,
}: ConnectionSuccessGuideProps) {
  const Icon = getAppIcon(app.app_display_name);
  
  // RootdataApplyClasstypementionprovidedifferent's Suggestion
  const suggestions = app.is_browser
    ? ["What is this page about?", "Fill out this form", "Summarize page content"]
    : app.app_display_name.toLowerCase().includes('figma')
      ? ["Analyze this design", "Extract design specs", "Describe the layout"]
      : app.app_display_name.toLowerCase().includes('code') || app.app_display_name.toLowerCase().includes('cursor')
        ? ["Explain this code", "Optimize this file", "Find potential issues"]
        : ["Read这个应用的Inner容", "帮我整理Info", "提取Key数据"];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 10, scale: 0.95 }}
      transition={SPRING.snappy}
      className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 mb-4 relative"
    >
      {/* Close按钮 */}
      <button 
        onClick={onDismiss}
        className="absolute top-2 right-2 w-6 h-6 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/40 hover:text-white/60 transition-colors"
      >
        ×
      </button>

      {/* Head部 */}
      <div className="flex items-center gap-2.5 mb-3">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 500, damping: 25, delay: 0.1 }}
          className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center"
        >
          <Sparkles className="w-4 h-4 text-emerald-400" />
        </motion.div>
        <div>
          <p className="font-medium text-sm text-white flex items-center gap-1.5">
            Connected
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-white/10 text-xs">
              <Icon className="w-3 h-3" />
              {app.app_display_name}
            </span>
          </p>
        </div>
      </div>

      {/* Suggested commands */}
      <p className="text-xs text-white/50 mb-2.5">Try these commands:</p>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, i) => (
          <motion.button
            key={suggestion}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.05 }}
            className="text-xs px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 text-white/70 hover:text-white border border-white/5 hover:border-white/10 transition-all"
            onClick={() => onSuggestionClick(suggestion)}
          >
            {suggestion}
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
});

// ============================================================================
// Empty State Guide - EmptyStateguide
// ============================================================================

const EmptyStateGuide = memo(function EmptyStateGuide() {
  return (
    <motion.div 
      className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* 脉冲Graph标 */}
      <motion.div
        className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
        style={{ 
          background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%)',
          boxShadow: '0 0 40px rgba(16, 185, 129, 0.15)',
        }}
        animate={{ 
          scale: [1, 1.05, 1],
          boxShadow: [
            '0 0 40px rgba(16, 185, 129, 0.15)',
            '0 0 60px rgba(16, 185, 129, 0.25)',
            '0 0 40px rgba(16, 185, 129, 0.15)',
          ],
        }}
        transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
      >
        <Link className="w-7 h-7 text-emerald-400" />
      </motion.div>
      
      {/* title */}
      <motion.h2 
        className="text-base font-medium text-white/80 mb-2"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        Connect your first app
      </motion.h2>
      
      {/* 描述 */}
      <motion.p 
        className="text-xs text-white/40 mb-5 max-w-[200px]"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        NogicOS 需要"看到"你的应用才能help你。
      </motion.p>
      
      {/* 指向侧边栏的箭Head提示 */}
      <motion.div
        className="flex items-center gap-2 text-xs text-emerald-400/60"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <motion.div
          animate={{ x: [-3, 3, -3] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          ←
        </motion.div>
        <span>从Left侧 App Connector Begin</span>
      </motion.div>
    </motion.div>
  );
});

// ============================================================================
// Context Bar Component - DisplaywhenBeforeUpDowntext
// ============================================================================

interface ContextBarProps {
  connectedApps: ConnectedApp[];
  aiState: AIState;
}

const ContextBar = memo(function ContextBar({ connectedApps, aiState }: ContextBarProps) {
  if (connectedApps.length === 0) return null;
  
  const config = STATE_CONFIG[aiState];
  
  return (
    <motion.div 
      className="flex items-center justify-center gap-2 py-2 text-xs"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={SPRING.gentle}
    >
      <span className="text-white/30 flex items-center gap-1.5">
        <motion.span
          className="w-1.5 h-1.5 rounded-full"
          style={{ backgroundColor: config.color.primary }}
          animate={{ 
            scale: aiState === 'idle' ? [1, 1.2, 1] : 1,
            opacity: aiState === 'idle' ? [0.5, 1, 0.5] : 1,
          }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        UpDown文:
      </span>
      <div className="flex items-center gap-1.5">
        {connectedApps.slice(0, 3).map(app => {
          const Icon = getAppIcon(app.app_display_name);
          return (
            <motion.span 
              key={app.hwnd}
              className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/5 text-white/50 hover:bg-white/10 hover:text-white/70 transition-colors cursor-default"
              whileHover={{ scale: 1.02 }}
            >
              <Icon className="w-3 h-3" />
              <span className="max-w-[80px] truncate">{app.app_display_name}</span>
            </motion.span>
          );
        })}
        {connectedApps.length > 3 && (
          <span className="text-white/30 px-1">+{connectedApps.length - 3}</span>
        )}
      </div>
    </motion.div>
  );
});

// ============================================================================
// App Hover Card Component
// ============================================================================

interface AppHoverCardProps {
  app: ConnectedApp;
  position: { x: number; y: number };
  onDisconnect?: (hwnd: number) => void;
}

const AppHoverCard = memo(function AppHoverCard({ app, position, onDisconnect }: AppHoverCardProps) {
  const Icon = getAppIcon(app.app_display_name);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 8, scale: 0.95 }}
      transition={SPRING.snappy}
      className="absolute z-50 bg-black/90 backdrop-blur-md border border-white/10 rounded-lg p-3 w-56 shadow-xl"
      style={{ 
        left: position.x, 
        top: position.y + 28,
        transform: 'translateX(-50%)',
      }}
    >
      {/* 小三角指示器 */}
      <div 
        className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-3 h-3 rotate-45 bg-black/90 border-l border-t border-white/10"
      />
      
      {/* 应用InfoHead部 */}
      <div className="flex items-center gap-2.5 mb-2.5">
        <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
          <Icon className="w-4 h-4 text-white/70" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm text-white truncate">
            {app.app_display_name}
          </p>
          <p className="text-[10px] text-white/40 truncate">
            {app.title}
          </p>
        </div>
      </div>
      
      {/* 详细Info */}
      <div className="text-xs text-white/50 space-y-1 mb-3 pl-0.5">
        <div className="flex items-center gap-2">
          <span className="w-14 text-white/30">Connected</span>
          <span>{formatRelativeTime(app.connected_at)}</span>
        </div>
        {app.is_browser && (
          <div className="flex items-center gap-2">
            <span className="w-14 text-white/30">Class型</span>
            <span className="flex items-center gap-1">
              <Globe className="w-3 h-3" /> 浏览器
            </span>
          </div>
        )}
        <div className="flex items-center gap-2">
          <span className="w-14 text-white/30">Process</span>
          <span className="font-mono text-[10px]">{app.app_name}</span>
        </div>
      </div>
      
      {/* 操作按钮 */}
      <div className="flex gap-2 pt-2 border-t border-white/5">
        <button 
          className="flex-1 text-xs px-2 py-1.5 rounded bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition-colors"
          onClick={() => {/* TODO: 聚焦Window */}}
        >
          聚焦Window
        </button>
        <button 
          className="text-xs px-2 py-1.5 rounded text-red-400/70 hover:text-red-400 hover:bg-red-500/10 transition-colors"
          onClick={() => onDisconnect?.(app.hwnd)}
        >
          Disconnect
        </button>
      </div>
    </motion.div>
  );
});

// ============================================================================
// Neural Background
// ============================================================================

const NeuralBackground = memo(function NeuralBackground({
  connectedApps,
  dataFlow,
  aiState = 'idle',
  dimensions,
  onDisconnect,
  focusedApp,
  onFocusChange,
  currentAction,
}: {
  connectedApps: ConnectedApp[];
  dataFlow?: DataFlowState;
  aiState: AIState;
  dimensions: { width: number; height: number };
  onDisconnect?: (hwnd: number) => void;
  focusedApp?: ConnectedApp | null;
  onFocusChange?: (app: ConnectedApp | null) => void;
  currentAction?: string;
}) {
  const config = STATE_CONFIG[aiState];
  const [hoveredApp, setHoveredApp] = useState<{ app: ConnectedApp; x: number; y: number } | null>(null);
  
  const centerX = dimensions.width / 2;
  const centerY = dimensions.height * 0.45; // resize to center, offset down
  const radius = Math.min(dimensions.width * 0.20, 100); // shrink radius to fit screen height

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
            radial-gradient(circle at 50% 30%, ${config.color.glow} 0%, transparent 50%),
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
        onClick={(e) => {
          // click empty area to unfocus
          if (e.target === e.currentTarget) {
            onFocusChange?.(null);
          }
        }}
      >
        {nodePositions.map(({ app, x, y }, index) => {
          const isActive = dataFlow?.sourceHwnd === app.hwnd;
          const isFocused = focusedApp?.hwnd === app.hwnd;
          const hasFocusedApp = focusedApp != null;
          const isDimmed = hasFocusedApp && !isFocused;
          const flowColor = dataFlow?.direction === 'out' ? COLORS.amber : COLORS.sky;
          
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
            <g key={app.hwnd} style={{ opacity: isDimmed ? 0.3 : 1 }}>
              {/* Layer 1: 基础Connect线 */}
              <motion.path
                d={pathD}
                fill="none"
                stroke={isFocused ? COLORS.emerald.primary : (isActive ? flowColor.primary : 'rgba(16, 185, 129, 0.3)')}
                strokeWidth={isFocused ? 2.5 : (isActive ? 2 : 1)}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
              />

              {/* Layer 2: 发光线（Active时） */}
              {isActive && (
                <motion.path
                  d={pathD}
                  fill="none"
                  stroke={flowColor.light}
                  strokeWidth={4}
                  style={{ filter: 'blur(4px)' }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: [0.2, 0.5, 0.2] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
              )}

              {/* Layer 3: Empty闲心跳光点（非Active时也有生命感） */}
              {!isActive && (
                <circle
                  r={2}
                  fill={COLORS.emerald.light}
                  opacity={0.4}
                >
                  <animateMotion
                    path={pathD}
                    dur="4s"
                    repeatCount="indefinite"
                    begin={`${index * 1.2}s`}
                  />
                  <animate
                    attributeName="opacity"
                    values="0;0.4;0.4;0"
                    keyTimes="0;0.1;0.9;1"
                    dur="4s"
                    repeatCount="indefinite"
                    begin={`${index * 1.2}s`}
                  />
                </circle>
              )}

              {/* Layer 4: Active数据流动光点（5个，更优雅） */}
              {isActive && dataFlow?.direction && (
                <>
                  {[0, 1, 2, 3, 4].map((i) => (
                    <circle
                      key={i}
                      r={4}
                      fill={flowColor.light}
                      style={{ filter: `drop-shadow(0 0 6px ${flowColor.primary})` }}
                    >
                      <animate
                        attributeName="cx"
                        values={dataFlow.direction === 'in' 
                          ? `${x};${ctrlX};${centerX}` 
                          : `${centerX};${ctrlX};${x}`
                        }
                        keyTimes="0;0.5;1"
                        dur="2s"
                        repeatCount="indefinite"
                        begin={`${i * 0.4}s`}
                      />
                      <animate
                        attributeName="cy"
                        values={dataFlow.direction === 'in' 
                          ? `${y};${ctrlY};${centerY}` 
                          : `${centerY};${ctrlY};${y}`
                        }
                        keyTimes="0;0.5;1"
                        dur="2s"
                        repeatCount="indefinite"
                        begin={`${i * 0.4}s`}
                      />
                      <animate
                        attributeName="opacity"
                        values="0;1;1;0"
                        keyTimes="0;0.1;0.9;1"
                        dur="2s"
                        repeatCount="indefinite"
                        begin={`${i * 0.4}s`}
                      />
                      <animate
                        attributeName="r"
                        values="3;4;3"
                        dur="2s"
                        repeatCount="indefinite"
                        begin={`${i * 0.4}s`}
                      />
                    </circle>
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
          const isHovered = hoveredApp?.app.hwnd === app.hwnd;
          const isFocused = focusedApp?.hwnd === app.hwnd;
          const hasFocusedApp = focusedApp != null;
          const isDimmed = hasFocusedApp && !isFocused;
          
          return (
            <motion.div
              key={app.hwnd}
              className="absolute pointer-events-auto cursor-pointer"
              style={{ 
                left: x, 
                top: y, 
                transform: 'translate(-50%, -50%)',
                zIndex: isFocused ? 10 : 1,
              }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ 
                scale: 1, 
                opacity: isDimmed ? 0.4 : 1,
              }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ ...SPRING.snappy, delay: index * 0.08 }}
              onMouseEnter={() => setHoveredApp({ app, x, y })}
              onMouseLeave={() => setHoveredApp(null)}
              onClick={() => {
                // ClickSwitchFocusedState
                if (isFocused) {
                  onFocusChange?.(null);
                } else {
                  onFocusChange?.(app);
                }
              }}
            >
              {/* 聚焦态Outer发光环 */}
              {isFocused && (
                <>
                  {[1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="absolute rounded-full border"
                      style={{
                        width: 36, height: 36,
                        left: '50%', top: '50%',
                        x: '-50%', y: '-50%',
                        borderColor: COLORS.emerald.primary,
                        willChange: 'transform, opacity',
                      }}
                      initial={{ scale: 1, opacity: 0.6 }}
                      animate={{ scale: 2.2, opacity: 0 }}
                      transition={{ 
                        duration: 2, 
                        repeat: Infinity, 
                        delay: i * 0.8,
                        ease: 'easeOut',
                      }}
                    />
                  ))}
                </>
              )}

              <motion.div
                className={cn(
                  "w-9 h-9 rounded-full flex items-center justify-center",
                  "border transition-all duration-300",
                  isFocused
                    ? "border-emerald-400/60 bg-emerald-500/20"
                    : isActive 
                      ? "border-white/30 bg-white/10" 
                      : isHovered
                        ? "border-white/30 bg-white/5"
                        : "border-white/10 bg-black/40"
                )}
                animate={{ 
                  scale: isFocused ? 1.25 : (isHovered ? 1.15 : 1),
                  boxShadow: isFocused 
                    ? `0 0 20px ${COLORS.emerald.glow}, 0 0 40px ${COLORS.emerald.glow}` 
                    : '0 0 0 transparent',
                }}
                transition={SPRING.micro}
                style={{ willChange: 'transform' }}
              >
                <Icon className={cn(
                  "w-4 h-4 transition-colors",
                  isFocused ? "text-emerald-300" :
                  isActive || isHovered ? "text-white" : "text-white/40"
                )} />
              </motion.div>
              
              <div className="absolute top-full mt-1 left-1/2 -translate-x-1/2 whitespace-nowrap">
                <span className={cn(
                  "text-[10px] transition-colors",
                  isFocused ? "text-emerald-300 font-medium" :
                  isActive || isHovered ? "text-white/80" : "text-white/30"
                )}>
                  {app.app_display_name}
                </span>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* Hover 预览卡片 */}
      <AnimatePresence>
        {hoveredApp && (
          <AppHoverCard 
            app={hoveredApp.app} 
            position={{ x: hoveredApp.x, y: hoveredApp.y }}
            onDisconnect={onDisconnect}
          />
        )}
      </AnimatePresence>

      {/* Medium心 AI Node - 增强Animation */}
      <motion.div
        className="absolute"
        style={{ left: centerX, top: centerY, transform: 'translate(-50%, -50%)' }}
        animate={{ 
          scale: aiState === 'success' ? [1, 1.1, 1] : (aiState === 'thinking' ? [1, 1.02, 1] : 1)
        }}
        transition={{ 
          duration: aiState === 'success' ? 0.5 : 2, 
          repeat: aiState === 'thinking' ? Infinity : (aiState === 'success' ? 2 : 0)
        }}
      >
        {/* State波纹环 - Root据StateDisplay不同Count */}
        {config.ringCount > 0 && (
          <>
            {Array.from({ length: config.ringCount }).map((_, i) => (
              <motion.div
                key={i}
                className="absolute rounded-full border"
                style={{
                  width: 48, height: 48,
                  left: '50%', top: '50%',
                  x: '-50%', y: '-50%',
                  borderColor: config.color.primary,
                  willChange: 'transform, opacity',
                }}
                initial={{ scale: 1, opacity: 0.5 }}
                animate={{ 
                  scale: aiState === 'reading' ? [2.5, 1] : [1, 2.5],  // reading towardheart，OthertowardOuter
                  opacity: [0.5, 0] 
                }}
                transition={{ 
                  duration: config.glowDuration, 
                  repeat: Infinity, 
                  delay: i * (config.glowDuration / config.ringCount),
                  ease: aiState === 'reading' ? 'easeIn' : 'easeOut',
                }}
              />
            ))}
          </>
        )}

        {/* Outer发光层 - UsageNewConfig */}
        <motion.div
          className="absolute rounded-full"
          style={{
            width: 64, height: 64,
            left: '50%', top: '50%',
            x: '-50%', y: '-50%',
            background: `radial-gradient(circle, ${config.color.glow} 0%, transparent 70%)`,
            willChange: 'transform, opacity',
          }}
          animate={{
            scale: config.glowScale,
            opacity: aiState === 'idle' ? 0.3 : (aiState === 'success' ? [0.5, 0.8, 0.5] : 0.5),
          }}
          transition={{ 
            duration: config.glowDuration, 
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {/* 主Node */}
        <motion.div
          className="relative w-12 h-12 rounded-full flex items-center justify-center overflow-hidden"
          style={{
            background: `linear-gradient(135deg, ${'dark' in config.color ? config.color.dark : config.color.primary} 0%, ${config.color.primary} 50%, ${config.color.light} 100%)`,
            boxShadow: `0 0 25px ${config.color.glow}`,
            willChange: 'transform',
          }}
          animate={aiState === 'success' ? { rotate: [0, 10, -10, 0] } : {}}
          transition={{ duration: 0.4, repeat: aiState === 'success' ? 2 : 0 }}
        >
          {/* 旋转High光 */}
          <motion.div
            className="absolute inset-0"
            animate={{ rotate: 360 }}
            transition={{ duration: aiState === 'acting' ? 4 : 8, repeat: Infinity, ease: 'linear' }}
          >
            <div 
              className="absolute top-0 left-1/2 w-1/2 h-full origin-left"
              style={{ background: `linear-gradient(90deg, transparent 0%, ${config.color.light}20 100%)` }}
            />
          </motion.div>

          <motion.div
            key={aiState}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={SPRING.snappy}
          >
            {(() => {
              const StateIcon = config.icon;
              return <StateIcon className="w-5 h-5 text-white relative z-10" />;
            })()}
          </motion.div>
        </motion.div>

        <motion.div 
          className="absolute top-full mt-2 left-1/2 -translate-x-1/2 text-center"
          key={aiState}
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="text-xs font-medium text-white/80 whitespace-nowrap">NogicOS</div>
          <div className="text-[10px] whitespace-nowrap" style={{ color: config.color.light }}>
            {connectedApps.length > 0 
              ? `${connectedApps.length} connected` 
              : 'Ready'}
          </div>
          {/* 当Before动作 - AI 工作时Display */}
          <AnimatePresence mode="wait">
            {currentAction && aiState !== 'idle' && (
              <motion.div
                key={currentAction}
                initial={{ opacity: 0, y: -4, height: 0 }}
                animate={{ opacity: 1, y: 0, height: 'auto' }}
                exit={{ opacity: 0, y: 4, height: 0 }}
                transition={{ duration: 0.2 }}
                className="mt-2 px-3 py-1.5 rounded-lg bg-black/60 backdrop-blur-sm border border-white/10 max-w-[200px]"
              >
                <div className="flex items-center gap-1.5">
                  <motion.div
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: config.color.primary }}
                    animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                  />
                  <span className="text-[10px] text-white/70 truncate">
                    {currentAction}
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </motion.div>

      {/* EmptyState引导 - 当没有Connect应用时Display */}
      <AnimatePresence>
        {connectedApps.length === 0 && <EmptyStateGuide />}
      </AnimatePresence>
    </div>
  );
});

// ============================================================================
// Status Bar
// ============================================================================

const StatusBar = memo(function StatusBar({
  aiState,
  currentAction,
}: {
  aiState: AIState;
  currentAction?: string;
}) {
  const config = STATE_CONFIG[aiState];

  if (aiState === 'idle' && !currentAction) {
    return null;
  }

  return (
    <motion.div
      className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06]"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={SPRING.snappy}
    >
      <motion.div
        className="w-1.5 h-1.5 rounded-full"
        style={{ backgroundColor: config.color.primary }}
        animate={{ scale: aiState !== 'idle' ? [1, 1.3, 1] : 1 }}
        transition={{ duration: 1, repeat: aiState !== 'idle' ? Infinity : 0 }}
      />

      <span className="text-[11px] text-white/60">
        {currentAction || config.label}
      </span>
    </motion.div>
  );
});

// ============================================================================
// Action Trace - Executeprocesscanvisualization
// ============================================================================

interface TraceStep {
  id: string;
  type: 'read' | 'analyze' | 'write' | 'confirm' | 'tool';
  status: 'pending' | 'active' | 'done' | 'error';
  label: string;
  detail?: string;
  toolName?: string;
}

// StepIndicatorComponent
const StepIndicator = memo(function StepIndicator({ 
  status, 
  type 
}: { 
  status: TraceStep['status']; 
  type: TraceStep['type'];
}) {
  const getIcon = () => {
    if (status === 'error') return <AlertCircle className="w-3 h-3 text-red-400" />;
    if (status === 'active') return <Loader2 className="w-3 h-3 animate-spin text-white" />;
    if (status === 'done') return <Check className="w-3 h-3 text-emerald-400" />;
    
    // pending StateRootdataClasstypeDisplay
    switch (type) {
      case 'read': return <Eye className="w-3 h-3 text-white/30" />;
      case 'analyze': return <Brain className="w-3 h-3 text-white/30" />;
      case 'write': return <Pencil className="w-3 h-3 text-white/30" />;
      case 'confirm': return <Square className="w-3 h-3 text-white/30" />;
      default: return <Terminal className="w-3 h-3 text-white/30" />;
    }
  };

  return (
    <div className={cn(
      "w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0",
      status === 'done' && "bg-emerald-500/10",
      status === 'active' && "bg-white/10",
      status === 'error' && "bg-red-500/10",
      status === 'pending' && "bg-white/5",
    )}>
      {getIcon()}
    </div>
  );
});

// ActionTrace Component - DisplayExecuteStep
const ActionTrace = memo(function ActionTrace({ 
  steps,
  isExpanded = true,
}: { 
  steps: TraceStep[];
  isExpanded?: boolean;
}) {
  if (steps.length === 0) return null;

  const completedCount = steps.filter(s => s.status === 'done').length;
  const hasError = steps.some(s => s.status === 'error');
  const isAllDone = completedCount === steps.length;

  return (
    <motion.div
      className="my-3"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* 折叠Head部 */}
      <div className="flex items-center gap-2 mb-2 text-[11px]">
        <div className={cn(
          "w-1.5 h-1.5 rounded-full",
          hasError ? "bg-red-400" : isAllDone ? "bg-emerald-400" : "bg-white/40"
        )} />
        <span className="text-white/40">
          {hasError ? 'Error' : isAllDone ? `Done ${completedCount} steps` : `Executing ${completedCount}/${steps.length}`}
        </span>
      </div>

      {/* 步骤List */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-l-2 border-white/10 pl-3 ml-1 space-y-2"
          >
            {steps.map((step, i) => (
              <motion.div
                key={step.id}
                className="flex items-start gap-2"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <StepIndicator status={step.status} type={step.type} />
                <div className="flex-1 min-w-0 pt-0.5">
                  <p className={cn(
                    "text-xs",
                    step.status === 'done' ? "text-white/70" : 
                    step.status === 'active' ? "text-white" :
                    step.status === 'error' ? "text-red-400" :
                    "text-white/40"
                  )}>
                    {step.label}
                  </p>
                  {step.detail && (
                    <p className="text-[10px] text-white/30 truncate">
                      {step.detail}
                    </p>
                  )}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});

// Toolnameto TraceStep Classtype's Map
function mapToolToTraceType(toolName: string): TraceStep['type'] {
  const name = toolName.toLowerCase();
  if (name.includes('read') || name.includes('get') || name.includes('list') || name.includes('search') || name.includes('snapshot')) {
    return 'read';
  }
  if (name.includes('write') || name.includes('create') || name.includes('update') || name.includes('click') || name.includes('type')) {
    return 'write';
  }
  if (name.includes('analyze') || name.includes('think')) {
    return 'analyze';
  }
  if (name.includes('confirm') || name.includes('ask')) {
    return 'confirm';
  }
  return 'tool';
}

// ============================================================================
// Tool Display Helpers
// ============================================================================

interface ToolInfo {
  type: string;
  toolCallId: string;
  toolName?: string;
  state: string;
  input?: Record<string, unknown>;
  output?: unknown;
}

function getFileName(path: string): string {
  if (!path) return '';
  return path.split(/[/\\]/).pop() || path;
}

function formatToolDisplay(toolName: string, input: Record<string, unknown> | undefined) {
  const name = toolName.toLowerCase().replace(/^tool-/, '');
  const str = (v: unknown) => typeof v === 'string' ? v : '';
  
  switch (name) {
    case 'read_file':
      return { icon: <FileText className="w-3 h-3" />, label: `Read ${getFileName(str(input?.target_file))}` };
    case 'list_dir':
      return { icon: <Folder className="w-3 h-3" />, label: `Listed ${getFileName(str(input?.target_directory))}` };
    case 'codebase_search':
      return { icon: <Search className="w-3 h-3" />, label: `Searched "${str(input?.query).slice(0, 25)}..."` };
    case 'grep':
      return { icon: <Code className="w-3 h-3" />, label: `Grep ${str(input?.pattern)}` };
    case 'browser_navigate':
    case 'browser_click':
    case 'browser_type':
      return { icon: <Globe className="w-3 h-3" />, label: name.replace('browser_', '') };
    case 'run_terminal_cmd':
      return { icon: <Terminal className="w-3 h-3" />, label: `Run ${str(input?.command).slice(0, 30)}...` };
    default:
      return { icon: <Terminal className="w-3 h-3" />, label: name.replace(/_/g, ' ') };
  }
}

const ToolItem = memo(function ToolItem({ tool }: { tool: ToolInfo }) {
  const toolName = tool.toolName || tool.type?.replace(/^tool-/, '') || 'unknown';
  const display = formatToolDisplay(toolName, tool.input);
  const isError = tool.state === 'error';
  const isRunning = tool.state === 'input-streaming' || tool.state === 'input-available';
  
  return (
    <motion.div 
      className="flex items-center gap-2 text-[11px]"
      initial={{ opacity: 0, x: -5 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <span className="text-white/40">
        {isError ? <AlertCircle className="w-3 h-3 text-red-400" />
         : isRunning ? <Loader2 className="w-3 h-3 animate-spin" />
         : <Check className="w-3 h-3 text-emerald-400" />}
      </span>
      <span className="text-white/30">{display.icon}</span>
      <span className="text-white/50">{display.label}</span>
    </motion.div>
  );
});

// ============================================================================
// Message Bubble
// ============================================================================

const MessageBubble = memo(function MessageBubble({
  message,
  isStreaming,
  toolInvocations,
}: {
  message: { role: 'user' | 'assistant'; content: string; isHistory?: boolean };
  isStreaming?: boolean;
  toolInvocations?: ToolInfo[];
}) {
  const isUser = message.role === 'user';
  const hasTools = toolInvocations && toolInvocations.length > 0;

  // ConvertToolCallfor ActionTrace Step
  const traceSteps: TraceStep[] = useMemo(() => {
    if (!toolInvocations) return [];
    return toolInvocations.map((tool) => {
      const toolName = tool.toolName || tool.type?.replace(/^tool-/, '') || 'unknown';
      const display = formatToolDisplay(toolName, tool.input);
      
      let status: TraceStep['status'] = 'pending';
      if (tool.state === 'error') status = 'error';
      else if (tool.state === 'output-available') status = 'done';
      else if (tool.state === 'input-streaming' || tool.state === 'input-available') status = 'active';
      
      return {
        id: tool.toolCallId || `tool-${Math.random()}`,
        type: mapToolToTraceType(toolName),
        status,
        label: display.label,
        toolName,
      };
    });
  }, [toolInvocations]);

  return (
    <motion.div
      className={cn(
        "max-w-[85%] rounded-2xl px-4 py-3",
        "backdrop-blur-md",
        isUser 
          ? "ml-auto bg-emerald-500/15 border border-emerald-500/20" 
          : "mr-auto bg-white/[0.03] border border-white/[0.06]"
      )}
      initial={message.isHistory ? false : { opacity: 0, y: 15, filter: 'blur(4px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={message.isHistory ? { duration: 0 } : { duration: 0.35 }}
    >
      <div className={cn(
        "text-[10px] font-medium mb-1",
        isUser ? "text-emerald-400/80" : "text-white/40"
      )}>
        {isUser ? 'You' : 'NogicOS'}
      </div>

      {/* Usage ActionTrace 替代简单的 ToolItem List */}
      {hasTools && traceSteps.length > 0 && (
        <div className="mb-2 pb-2 border-b border-white/5">
          <ActionTrace steps={traceSteps} isExpanded={true} />
        </div>
      )}

      <div className={cn(
        "text-sm leading-relaxed",
        isUser ? "text-white" : "text-white/90"
      )}>
        {!isUser ? (
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
              code: ({ className, children }) => {
                const match = /language-(\w+)/.exec(className || '');
                return match ? (
                  <SyntaxHighlighter
                    style={oneDark as Record<string, React.CSSProperties>}
                    language={match[1]}
                    PreTag="div"
                    customStyle={{ margin: 0, padding: '0.75rem', borderRadius: '0.5rem', fontSize: '0.8rem' }}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className="bg-neutral-800 px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
                );
              },
              a: ({ href, children }) => {
                const isSafe = href && (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('#'));
                if (!isSafe) return <span className="text-neutral-400">{children}</span>;
                return <a href={href} className="text-white underline hover:text-neutral-300" target="_blank" rel="noopener noreferrer">{children}</a>;
              },
            }}
          >
            {message.content}
          </ReactMarkdown>
        ) : (
          <span className="whitespace-pre-wrap">{message.content}</span>
        )}
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
// Main Component
// ============================================================================

export function LivingCanvasChat({
  apiUrl = 'http://localhost:8080/api/chat',
  sessionId,
  connectedApps,
  dataFlow,
  onDisconnect,
  onFocusWindow,
  focusedApp: externalFocusedApp,
  onFocusChange: externalOnFocusChange,
  initialMessages = [],
  onSessionUpdate,
  onMessagesChange,
  onToolCall,
  onAiStateChange,
  className,
}: LivingCanvasChatProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [localInput, setLocalInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  
  // FocusedApplyState（SupportOuterpartcontrolorInnerpartmanage）
  const [internalFocusedApp, setInternalFocusedApp] = useState<ConnectedApp | null>(null);
  const focusedApp = externalFocusedApp !== undefined ? externalFocusedApp : internalFocusedApp;
  const handleFocusChange = useCallback((app: ConnectedApp | null) => {
    if (externalOnFocusChange) {
      externalOnFocusChange(app);
    } else {
      setInternalFocusedApp(app);
    }
  }, [externalOnFocusChange]);
  
  // interactRecord（forRightsidePanel）
  const [actionRecords, setActionRecords] = useState<ActionRecord[]>([]);
  
  // NewConnectApplyguide
  const [newlyConnectedApp, setNewlyConnectedApp] = useState<ConnectedApp | null>(null);
  const prevConnectedAppsRef = useRef<ConnectedApp[]>([]);

  // Chat transport
  const chatTransport = useMemo(() => new DefaultChatTransport({
    api: apiUrl,
    body: { session_id: sessionId },
  }), [apiUrl, sessionId]);

  // useChat
  const {
    messages: chatMessages,
    sendMessage,
    stop,
    status,
    setMessages,
  } = useChat({
    id: `living-${sessionId}`,
    transport: chatTransport,
    onError: (err) => {
      console.error('[LivingCanvasChat] Error:', err);
    },
  });

  const isLoading = status === 'submitted' || status === 'streaming';

  // Derive AI state from status and messages
  const aiState: AIState = useMemo(() => {
    if (status === 'submitted') return 'thinking';
    if (status === 'streaming') {
      const lastMsg = chatMessages[chatMessages.length - 1];
      if (lastMsg && lastMsg.parts) {
        const hasTool = lastMsg.parts.some((p: MessagePart) => 
          p.type?.startsWith('tool-') || p.type === 'dynamic-tool'
        );
        if (hasTool) return 'acting';
      }
      return 'thinking';
    }
    return 'idle';
  }, [status, chatMessages]);

  // Current action for status bar
  const currentAction = useMemo(() => {
    if (!isLoading) return undefined;
    const lastMsg = chatMessages[chatMessages.length - 1];
    if (lastMsg?.parts) {
      const toolPart = lastMsg.parts.find((p: MessagePart) => 
        p.type?.startsWith('tool-') && (p as { state?: string }).state !== 'output-available'
      );
      if (toolPart) {
        const toolName = (toolPart as { toolName?: string }).toolName || '';
        return `Running ${toolName.replace(/_/g, ' ')}...`;
      }
    }
    return status === 'submitted' ? 'Processing...' : 'Generating...';
  }, [isLoading, chatMessages, status]);
  
  // NotifyParentComponent AI Statechange（Usage ref avoidNonelimitLoop）
  const prevAiStateRef = useRef<{ state: AIState; action?: string }>({ state: 'idle' });
  useEffect(() => {
    if (prevAiStateRef.current.state !== aiState || prevAiStateRef.current.action !== currentAction) {
      prevAiStateRef.current = { state: aiState, action: currentAction };
      onAiStateChange?.(aiState, currentAction);
    }
  }, [aiState, currentAction, onAiStateChange]);
  
  // trackToolCallandNotifyParentComponent
  const processedToolIds = useRef<Set<string>>(new Set());
  useEffect(() => {
    const lastMsg = chatMessages[chatMessages.length - 1];
    if (!lastMsg?.parts) return;
    
    for (const part of lastMsg.parts) {
      if (!part.type?.startsWith('tool-')) continue;
      
      const toolPart = part as MessagePart & { 
        toolCallId?: string; 
        toolName?: string; 
        state?: string;
        input?: Record<string, unknown>;
        output?: unknown;
      };
      
      const toolId = toolPart.toolCallId;
      if (!toolId) continue;
      
      // DetectionNewToolCallorStatechange
      const stateKey = `${toolId}-${toolPart.state}`;
      if (processedToolIds.current.has(stateKey)) continue;
      processedToolIds.current.add(stateKey);
      
      // NotifyParentComponent
      let toolState: ToolCallInfo['state'] = 'running';
      if (toolPart.state === 'output-available') {
        toolState = 'success';
      } else if (toolPart.state === 'error') {
        toolState = 'error';
      }
      
      // from toolName or type ExtractionToolname
      const extractedName = toolPart.toolName || toolPart.type?.replace(/^tool-/, '') || 'unknown';
      onToolCall?.({
        id: toolId,
        name: extractedName,
        state: toolState,
        input: toolPart.input,
        output: toolPart.output,
      });
    }
  }, [chatMessages, onToolCall]);

  // Load initial messages
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
    if (containerRef.current) resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  // Auto resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [localInput]);

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Save messages callback
  const onMessagesChangeRef = useRef(onMessagesChange);
  useEffect(() => { onMessagesChangeRef.current = onMessagesChange; }, [onMessagesChange]);
  
  useEffect(() => {
    if (chatMessages.length > 0 && onMessagesChangeRef.current) {
      const toSave = chatMessages.map(m => ({
        id: m.id,
        role: m.role as 'user' | 'assistant',
        content: (m as unknown as { content?: string }).content || '',
        parts: m.parts,
      }));
      onMessagesChangeRef.current(toSave);
    }
  }, [chatMessages]);

  // Update session title
  useEffect(() => {
    if (onSessionUpdate && chatMessages.length > 0) {
      const firstUserMsg = chatMessages.find(m => m.role === 'user');
      if (firstUserMsg) {
        const content = (firstUserMsg as unknown as { content?: string }).content || '';
        onSessionUpdate(content.slice(0, 30), content.slice(0, 100));
      }
    }
  }, [chatMessages, onSessionUpdate]);

  // DetectionNewConnect's Apply
  useEffect(() => {
    const prevHwnds = new Set(prevConnectedAppsRef.current.map(a => a.hwnd));
    const newApp = connectedApps.find(app => !prevHwnds.has(app.hwnd));
    
    if (newApp && prevConnectedAppsRef.current.length > 0) {
      // haveNewApplyConnect（excludeinitialLoad）
      setNewlyConnectedApp(newApp);
      // 5SecondAfterAutoClose
      const timer = setTimeout(() => setNewlyConnectedApp(null), 8000);
      return () => clearTimeout(timer);
    }
    
    prevConnectedAppsRef.current = connectedApps;
  }, [connectedApps]);

  // Submit handler
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (localInput.trim() && !isLoading) {
      const text = localInput.trim();
      setLocalInput('');
      await sendMessage({ text });
    }
  }, [localInput, isLoading, sendMessage]);

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  }, [handleSubmit]);

  // Format messages for display
  const displayMessages = useMemo(() => {
    return chatMessages.map(m => {
      const msgAny = m as unknown as { content?: string; parts?: MessagePart[] };
      
      // from parts MediumExtraction text Innercontent
      let textContent = msgAny.content || '';
      if (!textContent && m.parts) {
        const textParts = m.parts.filter((p: MessagePart) => p.type === 'text');
        textContent = textParts.map((p: MessagePart) => p.text || '').join('');
      }
      
      const toolInvocations: ToolInfo[] = (m.parts || [])
        .filter((p: MessagePart) => p.type?.startsWith('tool-'))
        .map((p: MessagePart) => {
          const part = p as MessagePart & { toolCallId?: string; toolName?: string; state?: string; input?: Record<string, unknown>; output?: unknown };
          return {
            type: part.type,
            toolCallId: part.toolCallId || '',
            toolName: part.toolName,
            state: part.state || 'pending',
            input: part.input,
            output: part.output,
          };
        });
      
      return {
        id: m.id,
        role: m.role as 'user' | 'assistant',
        content: textContent,
        isHistory: m.id.startsWith('loaded-'),
        toolInvocations,
      };
    });
  }, [chatMessages]);

  const isEmpty = displayMessages.length === 0;

  // calculate Canvas Height（totalHeight - BottomInputLocale）
  const inputAreaHeight = 120; // InputboxLocaleLargeaboutHeight
  const canvasHeight = Math.max(dimensions.height - inputAreaHeight, 300);

  return (
    <div 
      ref={containerRef}
      className={cn(
        "relative w-full h-full flex flex-col overflow-hidden",
        "bg-[#0a0a0a]",
        className
      )}
    >
      {/* Canvas 区域 - 占Full除Input框Outer的所有Empty间 */}
      <div className="relative flex-1 min-h-0 flex flex-col">
        {/* 神经NetworkBackground - 固定在Top */}
        <div className="relative h-[200px] flex-shrink-0">
          <NeuralBackground
            connectedApps={connectedApps}
            dataFlow={dataFlow}
            aiState={aiState}
            dimensions={{ width: dimensions.width, height: 200 }}
            onDisconnect={onDisconnect}
            focusedApp={focusedApp}
            onFocusChange={handleFocusChange}
            currentAction={currentAction}
          />
        </div>

        {/* 对话区域 - 可滚动 */}
        <div className="flex-1 overflow-y-auto px-4 py-3 min-h-0">
          <div className="max-w-2xl mx-auto">
            {/* ConnectSuccess引导 */}
            <AnimatePresence>
              {newlyConnectedApp && (
                <ConnectionSuccessGuide
                  app={newlyConnectedApp}
                  onDismiss={() => setNewlyConnectedApp(null)}
                  onSuggestionClick={(suggestion) => {
                    setLocalInput(suggestion);
                    setNewlyConnectedApp(null);
                    textareaRef.current?.focus();
                  }}
                />
              )}
            </AnimatePresence>

            {/* MessageList */}
            <AnimatePresence mode="popLayout">
              {isEmpty && !newlyConnectedApp ? (
                <motion.div
                  key="welcome"
                  className="flex flex-col items-center justify-center py-8"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <motion.p 
                    className="text-white/40 text-sm"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    Begin对话...
                  </motion.p>
                </motion.div>
              ) : (
                <div className="space-y-4">
                  {displayMessages
                    // FilterEmptywhiteMessage：MusthaveInnercontentorToolCall
                    .filter(msg => msg.content.trim() || (msg.toolInvocations && msg.toolInvocations.length > 0))
                    .map((message, index, filtered) => (
                    <MessageBubble
                      key={message.id || index}
                      message={message}
                      isStreaming={isLoading && index === filtered.length - 1 && message.role === 'assistant'}
                      toolInvocations={message.toolInvocations}
                    />
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* BottomInput区域 - 固定Height */}
      <div className="flex-shrink-0 px-4 pb-4 pt-2 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a] to-transparent">
        <div className="max-w-2xl mx-auto space-y-2">
          {/* UpDown文条 */}
          <ContextBar connectedApps={connectedApps} aiState={aiState} />
          
          {/* State条 */}
          <div className="flex justify-center">
            <StatusBar aiState={aiState} currentAction={currentAction} />
          </div>

          {/* Input框 */}
          <form onSubmit={handleSubmit}>
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
                value={localInput}
                onChange={(e) => setLocalInput(e.target.value)}
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
                      onClick={stop}
                      className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/15 flex items-center justify-center"
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
                      disabled={!localInput.trim()}
                      className={cn(
                        "w-8 h-8 rounded-lg flex items-center justify-center transition-all",
                        localInput.trim() 
                          ? "bg-emerald-500 hover:bg-emerald-400 text-white" 
                          : "bg-white/5 text-white/30"
                      )}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      exit={{ scale: 0.8, opacity: 0 }}
                      whileHover={localInput.trim() ? { scale: 1.05 } : undefined}
                      whileTap={localInput.trim() ? { scale: 0.95 } : undefined}
                    >
                      <ArrowUp className="w-4 h-4" />
                    </motion.button>
                  )}
                </AnimatePresence>
              </motion.div>
            </form>

          {/* Hints */}
          <div className="flex items-center justify-between px-1">
            <span className="text-[10px] text-white/20">
              <kbd className="px-1 py-0.5 rounded bg-white/5">Enter</kbd> to send
            </span>
            <motion.span 
              className="text-[10px] flex items-center gap-1"
              style={{ color: STATE_CONFIG[aiState].color.light }}
            >
              <motion.span 
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: STATE_CONFIG[aiState].color.primary }}
                animate={{ scale: aiState !== 'idle' ? [1, 1.3, 1] : [1, 1.2, 1] }}
                transition={{ duration: aiState !== 'idle' ? 1 : 2, repeat: Infinity }}
              />
              {STATE_CONFIG[aiState].label}
            </motion.span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LivingCanvasChat;
