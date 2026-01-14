/**
 * BubbleCanvas - PS Vita Style Bubble Canvas
 * 
 * Design concept:
 * - All hookable apps shown as floating bubbles
 * - Bubbles are draggable, stackable, with physics
 * - Click bubble = connect/disconnect app
 * - Connected bubbles glow + line to AI center
 * - Click connected bubble again = enter LiveArea
 */

import { useState, useRef, useEffect, useCallback, memo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Globe,
  Code2,
  FileText,
  AppWindow,
  Music,
  MessageSquare,
  Terminal,
  Zap,
  Plus,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAnimationPerformance, AnimationPerformanceContext, useAnimationConfig } from '@/hooks/useAnimationPerformance';

// ============================================================================
// Types
// ============================================================================

interface WindowInfo {
  hwnd: number;
  title: string;
  app_name: string;
  app_display_name: string;
  icon_base64?: string;  // base64 icon data
  is_browser: boolean;
}

interface ConnectedApp extends WindowInfo {
  connected_at: string;
}

interface BubbleCanvasProps {
  availableWindows: WindowInfo[];
  connectedApps: ConnectedApp[];
  onConnect: (window: WindowInfo) => void;
  onDisconnect: (hwnd: number) => void;
  onOpenLiveArea: (app: ConnectedApp) => void;
  aiState?: 'idle' | 'thinking' | 'reading' | 'acting' | 'success';
  activeAppHwnd?: number;  // Currently active app
  // 2026: Semantic OutputType (for connection lines and node effects)
  outputType?: OutputType;
  targetHwnd?: number | null;  // Current operation target app
  sourceHwnd?: number | null;  // Data source app
  className?: string;
}

interface BubblePosition {
  x: number;
  y: number;
  scale: number;
}

// ============================================================================
// Constants
// ============================================================================

// ============================================================================
// 2026 Premium Spring Physics - Juicy Animation Core
// ============================================================================

const SPRING = {
  // Micro-interaction: 0ms delay feel, for buttons, switches, small elements
  micro: { type: 'spring' as const, stiffness: 500, damping: 30, mass: 0.5 },
  
  // Fast response: menus, tooltips, state changes
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25, mass: 0.8 },
  
  // Bouncy: cards, important elements (Juicy core - low damping creates overshoot)
  bouncy: { type: 'spring' as const, stiffness: 300, damping: 15, mass: 1 },
  
  // Gentle: backgrounds, large area elements
  gentle: { type: 'spring' as const, stiffness: 150, damping: 20, mass: 1.2 },
  
  // Inertia: physics effect after drag release
  inertia: {
    type: 'inertia' as const,
    power: 0.8,
    timeConstant: 700,
    bounceStiffness: 300,
    bounceDamping: 20,
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
  'Notion': FileText,
  'Slack': MessageSquare,
  'Spotify': Music,
  'Terminal': Terminal,
  'PowerShell': Terminal,
  'cmd': Terminal,
};

function getAppIcon(appName: string) {
  if (APP_ICONS[appName]) return APP_ICONS[appName];
  for (const [key, icon] of Object.entries(APP_ICONS)) {
    if (appName.toLowerCase().includes(key.toLowerCase())) return icon;
  }
  return AppWindow;
}

// ============================================================================
// 🎨 4-Color System - NogicOS Core Design Language
// ============================================================================
// Principle: Color = Action direction, intuition-driven, no learning required
//
// Cyan    (#06b6d4) = Inflow/Read    → Water flowing in, absorb, get info
// Emerald (#10b981) = Outflow/Output → Growth, send, success, brand color
// Violet  (#8b5cf6) = Think/Process  → Mystery, AI intelligence, analysis
// Red     (#ef4444) = Warning/Error  → Stop, danger (rarely used)

const COLORS = {
  // Main 4 colors - 🔥 Enhanced: higher saturation + stronger glow
  cyan: {
    primary: '#22d3ee',      // Brighter cyan
    glow: 'rgba(34, 211, 238, 0.7)',  // Glow intensity 0.4 → 0.7
    bg: 'rgba(34, 211, 238, 0.25)',   // More visible background
    border: 'rgba(34, 211, 238, 0.9)', // Brighter border
  },
  emerald: {
    primary: '#34d399',      // Brighter green
    glow: 'rgba(52, 211, 153, 0.7)',
    bg: 'rgba(52, 211, 153, 0.25)',
    border: 'rgba(52, 211, 153, 0.9)',
  },
  violet: {
    primary: '#a78bfa',      // Brighter purple
    glow: 'rgba(167, 139, 250, 0.7)',
    bg: 'rgba(167, 139, 250, 0.25)',
    border: 'rgba(167, 139, 250, 0.9)',
  },
  red: {
    primary: '#f87171',      // Brighter red
    glow: 'rgba(248, 113, 113, 0.7)',
    bg: 'rgba(248, 113, 113, 0.25)',
    border: 'rgba(248, 113, 113, 0.9)',
  },
} as const;

// AI state colors - mapped to 4-color system
const AI_STATE_CONFIG = {
  idle: { color: COLORS.emerald.primary, glow: COLORS.emerald.glow },
  thinking: { color: COLORS.violet.primary, glow: COLORS.violet.glow },
  reading: { color: COLORS.cyan.primary, glow: COLORS.cyan.glow },       // Reading = Cyan
  acting: { color: COLORS.emerald.primary, glow: COLORS.emerald.glow },  // Acting = Green
  success: { color: COLORS.emerald.primary, glow: 'rgba(16, 185, 129, 0.6)' },
};

// ============================================================================
// Helper: Generate bubble positions in a circular pattern
// ============================================================================

function generateBubblePositions(count: number, centerX: number, centerY: number, radius: number): BubblePosition[] {
  const positions: BubblePosition[] = [];
  const angleStep = (2 * Math.PI) / Math.max(count, 1);
  
  for (let i = 0; i < count; i++) {
    const angle = angleStep * i - Math.PI / 2; // Start from top
    const jitter = (Math.random() - 0.5) * 40; // Random offset
    const r = radius + jitter;
    positions.push({
      x: centerX + Math.cos(angle) * r,
      y: centerY + Math.sin(angle) * r,
      scale: 0.9 + Math.random() * 0.2, // Slight size variation
    });
  }
  
  return positions;
}

// ============================================================================
// AppDock Component - Top dock bar showing unconnected apps
// ============================================================================

interface AppDockProps {
  windows: WindowInfo[];
  onConnect: (window: WindowInfo) => void;
  className?: string;
}

const AppDock = memo(function AppDock({ windows, onConnect, className }: AppDockProps) {
  if (windows.length === 0) return null;
  
  return (
    <motion.div
      className={cn(
        "absolute top-3 left-1/2 -translate-x-1/2 z-20",
        "flex items-center gap-1 px-3 py-2 rounded-full",
        "bg-black/40 backdrop-blur-md border border-white/10",
        className
      )}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
    >
      <span className="text-[10px] text-white/40 mr-2 whitespace-nowrap">Available:</span>
      {windows.slice(0, 8).map((window, index) => {
        const Icon = getAppIcon(window.app_display_name);
        
        return (
          <motion.button
            key={window.hwnd}
            className={cn(
              "relative w-9 h-9 rounded-lg flex items-center justify-center",
              "bg-white/5 hover:bg-white/15 border border-white/10 hover:border-white/30",
              "transition-colors cursor-pointer group"
            )}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05, type: 'spring', stiffness: 400 }}
            whileHover={{ scale: 1.1, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => onConnect(window)}
            title={window.app_display_name}
          >
            {window.icon_base64 ? (
              <img 
                src={window.icon_base64} 
                alt={window.app_display_name}
                className="w-5 h-5 rounded"
              />
            ) : (
              <Icon className="w-4 h-4 text-white/60 group-hover:text-white/90" />
            )}
            
            {/* Hover tooltip */}
            <motion.div
              className="absolute -bottom-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded bg-black/80 text-[10px] text-white whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"
            >
              {window.app_display_name}
            </motion.div>
          </motion.button>
        );
      })}
      
      {/* More indicator */}
      {windows.length > 8 && (
        <span className="text-[10px] text-white/40 ml-1">+{windows.length - 8}</span>
      )}
    </motion.div>
  );
});

// ============================================================================
// AppBubble Component
// ============================================================================

interface AppBubbleProps {
  window: WindowInfo;
  isConnected: boolean;
  isActive?: boolean;  // Being operated on
  isDimmed?: boolean;  // Other bubbles dimmed
  isSource?: boolean;  // Data source app (outer glow pulse)
  isTarget?: boolean;  // Operation target app (highlighted border + progress ring)
  position: BubblePosition;
  index: number;
  onClick: () => void;
  onDragStart?: () => void;  // Drag start callback
  onDrag?: (x: number, y: number) => void;  // Real-time update during drag
  onDragEnd: (x: number, y: number) => void;
  isSelfDragging?: boolean;  // Whether self is being dragged
}

const AppBubble = memo(function AppBubble({
  window,
  isConnected,
  isActive = false,
  isDimmed = false,
  isSource = false,
  isTarget = false,
  position,
  index,
  onClick,
  onDragStart,
  onDrag,
  onDragEnd,
  isSelfDragging = false,
}: AppBubbleProps) {
  const Icon = getAppIcon(window.app_display_name);
  const constraintsRef = useRef({ startX: 0, startY: 0 });

  // Use key to force remount and reset drag transform
  const [dragKey, setDragKey] = useState(0);
  
  return (
    <motion.div
      key={`bubble-${window.hwnd}-${dragKey}`}
      className="absolute cursor-pointer select-none"
      style={{ 
        left: 0, 
        top: 0,
        x: position.x,
        y: position.y,
        willChange: 'transform, opacity',
      }}
      initial={{ scale: position.scale, opacity: 1 }}
      animate={{ 
        scale: position.scale,
        opacity: isDimmed ? 0.4 : 1,
        filter: isDimmed ? 'brightness(0.6)' : 'brightness(1)',
      }}
      exit={{ scale: 0, opacity: 0 }}
      transition={{ 
        opacity: { duration: 0.2 },
        filter: { duration: 0.2 },
        scale: { duration: 0.2 },
      }}
      // Drag config - disable momentum to prevent flying off
      drag
      dragElastic={0.05}
      dragMomentum={false}
      onDragStart={() => {
        constraintsRef.current = { startX: position.x, startY: position.y };
        onDragStart?.();
      }}
      onDrag={(_, info) => {
        onDrag?.(info.offset.x, info.offset.y);
      }}
      onDragEnd={(_, info) => {
        const newX = constraintsRef.current.startX + info.offset.x;
        const newY = constraintsRef.current.startY + info.offset.y;
        onDragEnd(newX, newY);
        setDragKey(k => k + 1); // Force reset drag transform
      }}
      onClick={onClick}
      // 2026 Premium interaction feedback - Juicy core
      whileHover={{ 
        scale: position.scale * 1.08,
        transition: SPRING.bouncy,
      }}
      whileTap={{ 
        scale: position.scale * 0.95,
        transition: { duration: 0.1 },
      }}
      whileDrag={{
        scale: position.scale * 1.1,
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
        cursor: 'grabbing',
      }}
    >
      {/* Outer层呼吸光晕 - 已Connect时Display (4 色System) - 🔥 增强版 */}
      {isConnected && (
        <>
          {/* 基础发光层 - 更大Range + 更强亮度 */}
          <motion.div
            className="absolute inset-[-20px] rounded-full"
            style={{
              // isTarget (outflow) = green, isSource (inflow) = cyan, isActive = purple, default = light green
              background: isTarget 
                ? `radial-gradient(circle, ${COLORS.emerald.glow} 0%, ${COLORS.emerald.bg} 40%, transparent 70%)`
                : isSource
                  ? `radial-gradient(circle, ${COLORS.cyan.glow} 0%, ${COLORS.cyan.bg} 40%, transparent 70%)`
                  : isActive 
                    ? `radial-gradient(circle, ${COLORS.violet.glow} 0%, ${COLORS.violet.bg} 40%, transparent 70%)`
                    : `radial-gradient(circle, ${COLORS.emerald.bg} 0%, transparent 70%)`,
              filter: 'blur(12px)',
              willChange: 'opacity, transform',
            }}
            animate={{
              opacity: isSource || isTarget ? [0.7, 1, 0.7] : [0.4, 0.7, 0.4],
              scale: isSource || isTarget ? [1, 1.1, 1] : [1, 1.05, 1],
            }}
            transition={{
              duration: isSource || isTarget ? 0.8 : isActive ? 1.2 : 3,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          
          {/* 额OuterHigh亮环 - 仅在 source/target 时Display */}
          {(isSource || isTarget) && (
            <motion.div
              className="absolute inset-[-8px] rounded-full"
              style={{
                border: `3px solid ${isSource ? COLORS.cyan.primary : COLORS.emerald.primary}`,
                boxShadow: `0 0 20px ${isSource ? COLORS.cyan.glow : COLORS.emerald.glow}, inset 0 0 10px ${isSource ? COLORS.cyan.bg : COLORS.emerald.bg}`,
              }}
              animate={{
                opacity: [0.8, 1, 0.8],
              }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          )}
        </>
      )}
      
      {/* Source State：Outer发光脉冲 (数据流入 = 青色) - 🔥 更明显 */}
      {isSource && (
        <>
          {[0, 1, 2].map((i) => (
            <motion.div
              key={`source-pulse-${i}`}
              className="absolute inset-[-6px] rounded-full"
              style={{ 
                border: `3px solid ${COLORS.cyan.primary}`,
                boxShadow: `0 0 10px ${COLORS.cyan.glow}`,
              }}
              initial={{ scale: 1, opacity: 0.8 }}
              animate={{ scale: 2.5, opacity: 0 }}
              transition={{
                duration: 1.2,
                repeat: Infinity,
                delay: i * 0.4,
                ease: [0.22, 1, 0.36, 1],
              }}
            />
          ))}
        </>
      )}
      
      {/* Target State：High亮Border + 进度环 (数据流出 = 绿色) - 🔥 更明显 */}
      {isTarget && (
        <>
          {/* High亮Border - 更粗更亮 */}
          <motion.div
            className="absolute inset-[-5px] rounded-full"
            style={{
              border: `4px solid ${COLORS.emerald.primary}`,
              boxShadow: `0 0 25px ${COLORS.emerald.glow}, 0 0 50px ${COLORS.emerald.bg}`,
            }}
            animate={{
              boxShadow: [
                `0 0 25px ${COLORS.emerald.glow}, 0 0 50px ${COLORS.emerald.bg}`,
                `0 0 40px ${COLORS.emerald.glow}, 0 0 80px ${COLORS.emerald.bg}`,
                `0 0 25px ${COLORS.emerald.glow}, 0 0 50px ${COLORS.emerald.bg}`,
              ],
            }}
            transition={{ duration: 1, repeat: Infinity, ease: 'easeInOut' }}
          />
          {/* SVG 进度环 */}
          <svg
            className="absolute inset-[-6px] w-[calc(100%+12px)] h-[calc(100%+12px)]"
            style={{ transform: 'rotate(-90deg)' }}
          >
            <motion.circle
              cx="50%"
              cy="50%"
              r="48%"
              fill="none"
              stroke={`${COLORS.emerald.primary}cc`}
              strokeWidth="2"
              strokeLinecap="round"
              strokeDasharray="100"
              initial={{ strokeDashoffset: 100 }}
              animate={{ strokeDashoffset: 0 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            />
          </svg>
        </>
      )}
      
      {/* Active indicator ring - 旋转环 (AI 操作Medium = 紫色) */}
      {isActive && (
        <motion.div
          className="absolute inset-[-4px] rounded-full"
          style={{
            border: `1.5px solid ${COLORS.violet.border}`,
            willChange: 'transform',
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
        />
      )}
      
      {/* Bubble body - 🔥 增强版：Root据State变色 */}
      <motion.div
        className={cn(
          "relative w-16 h-16 rounded-full flex flex-col items-center justify-center overflow-hidden",
          !isConnected && "bg-gradient-to-br from-white/10 to-white/5 border border-white/20 hover:border-white/40"
        )}
        style={{
          // Dynamically set color based on state
          background: !isConnected 
            ? undefined
            : isSource 
              ? `linear-gradient(135deg, ${COLORS.cyan.bg} 0%, rgba(34, 211, 238, 0.1) 100%)`
              : isTarget 
                ? `linear-gradient(135deg, ${COLORS.emerald.bg} 0%, rgba(52, 211, 153, 0.1) 100%)`
                : isActive
                  ? `linear-gradient(135deg, ${COLORS.violet.bg} 0%, rgba(167, 139, 250, 0.1) 100%)`
                  : 'linear-gradient(135deg, rgba(52, 211, 153, 0.2) 0%, rgba(52, 211, 153, 0.08) 100%)',
          border: !isConnected 
            ? undefined 
            : isSource 
              ? `3px solid ${COLORS.cyan.primary}`
              : isTarget 
                ? `3px solid ${COLORS.emerald.primary}`
                : isActive
                  ? `3px solid ${COLORS.violet.primary}`
                  : '2px solid rgba(52, 211, 153, 0.5)',
          boxShadow: !isConnected
            ? '0 4px 15px rgba(0, 0, 0, 0.3)'
            : isSource
              ? `0 0 30px ${COLORS.cyan.glow}, inset 0 0 15px ${COLORS.cyan.bg}`
              : isTarget
                ? `0 0 30px ${COLORS.emerald.glow}, inset 0 0 15px ${COLORS.emerald.bg}`
                : isActive
                  ? `0 0 25px ${COLORS.violet.glow}, inset 0 0 12px ${COLORS.violet.bg}`
                  : '0 0 20px rgba(52, 211, 153, 0.2), inset 0 0 10px rgba(52, 211, 153, 0.1)',
          willChange: 'transform',
        }}
      >
        {/* DisplayTrue实Graph标（如果有）或DefaultGraph标 */}
        {window.icon_base64 ? (
          <img 
            src={window.icon_base64} 
            alt={window.app_display_name}
            className={cn(
              "w-8 h-8 rounded object-contain",
              !isConnected && "opacity-70"
            )}
            style={{
              // Icon color also changes based on state
              filter: isSource 
                ? 'drop-shadow(0 0 8px rgba(34, 211, 238, 0.8))'
                : isTarget 
                  ? 'drop-shadow(0 0 8px rgba(52, 211, 153, 0.8))'
                  : isActive
                    ? 'drop-shadow(0 0 6px rgba(167, 139, 250, 0.6))'
                    : undefined,
            }}
            draggable={false}
          />
        ) : (
          <Icon 
            className={cn(
              "w-6 h-6",
              isConnected ? "text-emerald-300" : "text-white/60"
            )}
            style={{
              color: isSource ? COLORS.cyan.primary : isTarget ? COLORS.emerald.primary : isActive ? COLORS.violet.primary : undefined,
            }}
          />
        )}
        
        {/* Connection indicator - Root据State变色 */}
        {isConnected && (
          <motion.div
            className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center"
            style={{
              backgroundColor: isSource ? COLORS.cyan.primary : isTarget ? COLORS.emerald.primary : isActive ? COLORS.violet.primary : '#34d399',
              boxShadow: `0 0 8px ${isSource ? COLORS.cyan.glow : isTarget ? COLORS.emerald.glow : isActive ? COLORS.violet.glow : 'rgba(52, 211, 153, 0.5)'}`,
            }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 300 }}
          >
            <Zap className="w-2.5 h-2.5 text-black" />
          </motion.div>
        )}
      </motion.div>
      
      {/* App name label */}
      <motion.div
        className={cn(
          "absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap",
          "text-[10px] font-medium px-2 py-0.5 rounded-full",
          isConnected
            ? "bg-emerald-500/20 text-emerald-300 shadow-lg shadow-emerald-500/20"
            : "bg-black/50 text-white/50"
        )}
        initial={{ opacity: 0, y: -5 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.05 + 0.2 }}
      >
        {window.app_display_name}
      </motion.div>
    </motion.div>
  );
});

// ============================================================================
// OutputType semantic type definition
// ============================================================================

type OutputType = 
  | 'idle'        // Idle
  | 'observing'   // Observing (reading app state)
  | 'analyzing'   // Analyzing (comparing/analyzing)
  | 'planning'    // Planning
  | 'writing'     // Writing
  | 'sending'     // Sending
  | 'waiting'     // Waiting for confirmation
  | 'completed'   // Completed
  | 'error';      // Error

// OutputType → 4-color system mapping
// Intuition-based design by action direction
const OUTPUT_TYPE_COLORS: Record<OutputType, { primary: string; glow: string }> = {
  idle: { primary: COLORS.emerald.primary, glow: COLORS.emerald.glow },
  observing: { primary: COLORS.cyan.primary, glow: COLORS.cyan.glow },     // Read = Cyan (inflow)
  analyzing: { primary: COLORS.violet.primary, glow: COLORS.violet.glow }, // Analyze = Purple (AI thinking)
  planning: { primary: COLORS.violet.primary, glow: COLORS.violet.glow },  // Plan = Purple (AI thinking)
  writing: { primary: COLORS.violet.primary, glow: COLORS.violet.glow },   // Write = Purple (AI operating)
  sending: { primary: COLORS.emerald.primary, glow: COLORS.emerald.glow }, // Send = Green (outflow/complete)
  waiting: { primary: COLORS.violet.primary, glow: 'rgba(139, 92, 246, 0.25)' }, // Wait = Dim purple
  completed: { primary: COLORS.emerald.primary, glow: 'rgba(16, 185, 129, 0.6)' }, // Complete = Bright green
  error: { primary: COLORS.red.primary, glow: COLORS.red.glow },           // Error = Red
};

// ============================================================================
// ConnectionLine Component - 2026 Premium: SMIL flowing particles + semantic animation
// ============================================================================

interface ConnectionLineProps {
  startX: number;  // Bubble top-left X
  startY: number;  // Bubble top-left Y
  endX: number;    // AI center X
  endY: number;    // AI center Y
  isActive: boolean;
  isConnecting?: boolean;
  isDragging?: boolean;  // Simplify rendering during drag
  outputType?: OutputType;
  flowDirection?: 'in' | 'out' | 'bidirectional' | 'none';
  // Performance degradation config
  enableParticles?: boolean;
  maxParticles?: number;
}

const ConnectionLine = memo(function ConnectionLine({
  startX,
  startY,
  endX,
  endY,
  isActive,
  isConnecting = false,
  isDragging = false,
  enableParticles = true,
  maxParticles = 5,
  outputType = 'idle',
  flowDirection = 'none',
}: ConnectionLineProps) {
  const colors = OUTPUT_TYPE_COLORS[outputType];
  
  // Bubble center (bubble 64x64)
  const sx = startX + 32;
  const sy = startY + 32;
  const ex = endX;
  const ey = endY;
  
  // Calculate elegant Bezier curve control points
  const dx = ex - sx;
  const dy = ey - sy;
  const dist = Math.sqrt(dx * dx + dy * dy);
  
  // Prevent division by zero
  if (dist < 1) return null;
  
  // Curve bend amount
  const curveFactor = Math.min(dist * 0.2, 80);
  const perpX = -dy / dist * curveFactor;
  const perpY = dx / dist * curveFactor;
  
  const cx = (sx + ex) / 2 + perpX;
  const cy = (sy + ey) / 2 + perpY;
  
  // Unique ID for SMIL reference
  const pathId = `conn-path-${Math.round(sx)}-${Math.round(sy)}`;
  const reversePathId = `${pathId}-rev`;
  
  // Quadratic Bezier curve
  const curvePath = `M${sx},${sy} Q${cx},${cy} ${ex},${ey}`;
  const reversePath = `M${ex},${ey} Q${cx},${cy} ${sx},${sy}`;
  
  // Determine actual flow direction
  const actualFlowDirection = flowDirection !== 'none' ? flowDirection
    : outputType === 'observing' ? 'in'
    : outputType === 'writing' || outputType === 'sending' ? 'out'
    : outputType === 'analyzing' ? 'bidirectional'
    : 'none';
  
  // Calculate animation params based on outputType
  const animDuration = outputType === 'writing' || outputType === 'sending' ? 1.2 
    : outputType === 'observing' ? 2 
    : outputType === 'analyzing' ? 1.5
    : 2.5;
  
  // Particle count (limited by performance config)
  const baseParticleCount = outputType === 'analyzing' ? 4 
    : outputType === 'sending' ? 3 
    : outputType === 'writing' ? 3
    : 2;
  const particleCount = enableParticles ? Math.min(baseParticleCount, maxParticles) : 0;
  
  // Particle size (adapts to distance)
  const particleSize = Math.max(3, Math.min(5, dist / 80));
  
  return (
    <svg
      className="absolute inset-0 pointer-events-none"
      style={{ overflow: 'visible', zIndex: 0 }}
    >
      <defs>
        {/* 定义Path供 SMIL animateMotion Usage */}
        <path id={pathId} d={curvePath} fill="none" />
        <path id={reversePathId} d={reversePath} fill="none" />
        
        {/* 粒Child发光渐变 */}
        <radialGradient id={`particle-glow-${pathId}`}>
          <stop offset="0%" stopColor={colors.primary} stopOpacity="1" />
          <stop offset="50%" stopColor={colors.primary} stopOpacity="0.6" />
          <stop offset="100%" stopColor={colors.primary} stopOpacity="0" />
        </radialGradient>
      </defs>
      
      {/* 层1: 发光底层 - 丝滑Transition */}
      <motion.path
        d={curvePath}
        fill="none"
        stroke={colors.primary}
        strokeLinecap="round"
        animate={{
          strokeWidth: isDragging ? 6 : 12,
          opacity: isDragging ? 0.08 : 0.12,
        }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
      />
      <motion.path
        d={curvePath}
        fill="none"
        stroke={colors.primary}
        strokeLinecap="round"
        animate={{
          strokeWidth: isDragging ? 3 : 6,
          opacity: isDragging ? 0.12 : 0.2,
        }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
      />
      
      {/* 层2: Core线条 - 丝滑Transition */}
      <motion.path
        d={curvePath}
        fill="none"
        stroke={colors.primary}
        strokeLinecap="round"
        animate={{
          strokeWidth: isDragging ? 1.5 : 2,
          opacity: isDragging ? 0.5 : (isActive ? 0.8 : 0.5),
        }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
      />
      
      {/* 层3: High亮Medium心 - 丝滑Transition */}
      <motion.path
        d={curvePath}
        fill="none"
        stroke="rgba(255,255,255,0.95)"
        strokeLinecap="round"
        animate={{
          strokeWidth: isDragging ? 0.5 : 1,
          opacity: isDragging ? 0.3 : (isActive ? 0.7 : 0.4),
        }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
      />
      
      {/* 层4: SMIL 流动粒Child - App → AI (in) - 丝滑淡入淡出 */}
      {particleCount > 0 && (actualFlowDirection === 'in' || actualFlowDirection === 'bidirectional' || actualFlowDirection === 'none') && (
        <motion.g
          animate={{ opacity: isDragging ? 0 : 1 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
        >
          {Array.from({ length: particleCount }).map((_, i) => (
            <g key={`particle-in-${i}`}>
              {/* 粒Child光晕 */}
              <circle
                r={particleSize * 2}
                fill={`url(#particle-glow-${pathId})`}
                opacity={0.6}
              >
                <animateMotion
                  dur={`${animDuration}s`}
                  repeatCount="indefinite"
                  begin={`${i * (animDuration / particleCount)}s`}
                  calcMode="spline"
                  keySplines="0.4 0 0.2 1"
                  keyTimes="0;1"
                >
                  <mpath href={`#${pathId}`} />
                </animateMotion>
              </circle>
              {/* 粒ChildCore */}
              <circle
                r={particleSize}
                fill={colors.primary}
                opacity={1}
              >
                <animateMotion
                  dur={`${animDuration}s`}
                  repeatCount="indefinite"
                  begin={`${i * (animDuration / particleCount)}s`}
                  calcMode="spline"
                  keySplines="0.4 0 0.2 1"
                  keyTimes="0;1"
                >
                  <mpath href={`#${pathId}`} />
                </animateMotion>
              </circle>
              {/* 粒Child亮点 */}
              <circle
                r={particleSize * 0.4}
                fill="white"
                opacity={0.9}
              >
                <animateMotion
                  dur={`${animDuration}s`}
                  repeatCount="indefinite"
                  begin={`${i * (animDuration / particleCount)}s`}
                  calcMode="spline"
                  keySplines="0.4 0 0.2 1"
                  keyTimes="0;1"
                >
                  <mpath href={`#${pathId}`} />
                </animateMotion>
              </circle>
            </g>
          ))}
        </motion.g>
      )}
      
      {/* 层4: SMIL 流动粒Child - AI → App (out) - 丝滑淡入淡出 */}
      {particleCount > 0 && (actualFlowDirection === 'out' || actualFlowDirection === 'bidirectional') && (
        <motion.g
          animate={{ opacity: isDragging ? 0 : 1 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
        >
          {Array.from({ length: particleCount }).map((_, i) => (
            <g key={`particle-out-${i}`}>
              {/* 粒Child光晕 */}
              <circle
                r={particleSize * 2}
                fill={`url(#particle-glow-${pathId})`}
                opacity={0.6}
              >
                <animateMotion
                  dur={`${animDuration}s`}
                  repeatCount="indefinite"
                  begin={`${i * (animDuration / particleCount) + (actualFlowDirection === 'bidirectional' ? animDuration / 2 : 0)}s`}
                  calcMode="spline"
                  keySplines="0.4 0 0.2 1"
                  keyTimes="0;1"
                >
                  <mpath href={`#${reversePathId}`} />
                </animateMotion>
              </circle>
              {/* 粒ChildCore */}
              <circle
                r={particleSize}
                fill={colors.primary}
                opacity={1}
              >
                <animateMotion
                  dur={`${animDuration}s`}
                  repeatCount="indefinite"
                  begin={`${i * (animDuration / particleCount) + (actualFlowDirection === 'bidirectional' ? animDuration / 2 : 0)}s`}
                  calcMode="spline"
                  keySplines="0.4 0 0.2 1"
                  keyTimes="0;1"
                >
                  <mpath href={`#${reversePathId}`} />
                </animateMotion>
              </circle>
              {/* 粒Child亮点 */}
              <circle
                r={particleSize * 0.4}
                fill="white"
                opacity={0.9}
              >
                <animateMotion
                  dur={`${animDuration}s`}
                  repeatCount="indefinite"
                  begin={`${i * (animDuration / particleCount) + (actualFlowDirection === 'bidirectional' ? animDuration / 2 : 0)}s`}
                  calcMode="spline"
                  keySplines="0.4 0 0.2 1"
                  keyTimes="0;1"
                >
                  <mpath href={`#${reversePathId}`} />
                </animateMotion>
              </circle>
            </g>
          ))}
        </motion.g>
      )}
      
      {/* waiting State：脉冲呼吸 */}
      {outputType === 'waiting' && !isDragging && (
        <path
          d={curvePath}
          fill="none"
          stroke={colors.primary}
          strokeWidth={3}
          strokeLinecap="round"
          className="connection-pulse"
        />
      )}
      
      {/* completed State：扫光Effect */}
      {outputType === 'completed' && !isDragging && (
        <>
          {/* 扫光线 */}
          <motion.path
            d={curvePath}
            fill="none"
            stroke="white"
            strokeWidth={4}
            strokeLinecap="round"
            initial={{ pathLength: 0, opacity: 1 }}
            animate={{ pathLength: 1, opacity: 0 }}
            transition={{ 
              pathLength: { duration: 0.8, ease: [0.22, 1, 0.36, 1] },
              opacity: { duration: 0.8, delay: 0.2 }
            }}
          />
          {/* Success光晕 */}
          <motion.path
            d={curvePath}
            fill="none"
            stroke={colors.primary}
            strokeWidth={8}
            strokeLinecap="round"
            initial={{ opacity: 0.8 }}
            animate={{ opacity: 0 }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </>
      )}
      
      {/* Connect时的脉冲Effect */}
      {isConnecting && (
        <motion.circle
          cx={sx}
          cy={sy}
          r={16}
          fill="none"
          stroke={colors.primary}
          strokeWidth={2}
          initial={{ scale: 0.5, opacity: 1 }}
          animate={{ scale: 2.5, opacity: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        />
      )}
    </svg>
  );
});

// ============================================================================
// ConnectionRipple Component - Connection success ripple effect (enhanced)
// ============================================================================

interface ConnectionRippleProps {
  x: number;
  y: number;
  onComplete?: () => void;
}

const ConnectionRipple = memo(function ConnectionRipple({ x, y, onComplete }: ConnectionRippleProps) {
  const cx = x + 32;
  const cy = y + 32;
  
  // Connection success ripple - use green (success semantic)
  return (
    <svg
      className="absolute inset-0 pointer-events-none"
      style={{ overflow: 'visible', zIndex: 100 }}
    >
      {/* 3 层涟漪 - 绿色渐变 */}
      {[1, 2, 3].map((i) => (
        <motion.circle
          key={i}
          cx={cx}
          cy={cy}
          r={24}
          fill="none"
          stroke={COLORS.emerald.primary}
          strokeWidth={2}
          initial={{ scale: 0.8, opacity: 0.6 - i * 0.12 }}
          animate={{ scale: 2 + i * 0.3, opacity: 0 }}
          transition={{ 
            duration: 0.8, 
            delay: i * 0.1,
            ease: 'easeOut',
          }}
          onAnimationComplete={i === 3 ? onComplete : undefined}
        />
      ))}
    </svg>
  );
});


// ============================================================================
// CenterAINode Component - 2026 Premium: stagger pulse ring + dual rotating halo
// ============================================================================

interface CenterAINodeProps {
  x: number;
  y: number;
  state: 'idle' | 'thinking' | 'reading' | 'acting' | 'success';
  outputType?: OutputType;
}

const CenterAINode = memo(function CenterAINode({ x, y, state, outputType = 'idle' }: CenterAINodeProps) {
  const config = AI_STATE_CONFIG[state];
  const outputColors = OUTPUT_TYPE_COLORS[outputType];
  
  // Dynamically adjust animation params based on state - converged version
  const stateAnimations = {
    idle: { 
      scale: [1, 1.01, 1],  // Minimal breathing
      duration: 4,
      pulseCount: 0,  // No pulse rings
    },
    thinking: { 
      scale: [1, 1.03, 1], 
      duration: 1.5,
      pulseCount: 1,  // Single pulse
    },
    reading: { 
      scale: [1, 1.02, 1], 
      duration: 2,
      pulseCount: 1,
    },
    acting: { 
      scale: [1, 1.03, 1], 
      duration: 1,
      pulseCount: 1,
    },
    success: { 
      scale: [1, 1.05, 1], 
      duration: 0.6,
      pulseCount: 1,
    },
  };
  
  const anim = stateAnimations[state];
  const nodeSize = 80;
  const activeColor = state !== 'idle' ? outputColors.primary : config.color;
  const activeGlow = state !== 'idle' ? outputColors.glow : config.glow;
  
  return (
    <motion.div
      className="absolute"
      style={{ 
        left: x - nodeSize / 2,
        top: y - nodeSize / 2,
        width: nodeSize,
        height: nodeSize,
        willChange: 'transform',
      }}
    >
      {/* 柔和发光Background - 收敛版 */}
      <motion.div
        className="absolute rounded-full"
        style={{
          inset: -15,
          background: `radial-gradient(circle, ${activeGlow} 0%, transparent 70%)`,
          willChange: 'opacity',
        }}
        animate={{ opacity: [0.2, 0.35, 0.2] }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      
      {/* 脉冲环 - 收敛版：仅工作StateDisplay */}
      {anim.pulseCount > 0 && Array.from({ length: anim.pulseCount }).map((_, i) => (
        <motion.div
          key={`pulse-${i}`}
          className="absolute rounded-full"
          style={{
            inset: 0,
            border: `1.5px solid ${activeColor}`,
            willChange: 'transform, opacity',
          }}
          initial={{ scale: 1, opacity: 0.5 }}
          animate={{
            scale: [1, 1.8],
            opacity: [0.5, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: i * (2 / anim.pulseCount),
            ease: [0.22, 1, 0.36, 1],
          }}
        />
      ))}
      
      {/* 主Node - 收敛版呼吸Effect */}
      <motion.div
        className="absolute inset-0 rounded-full flex items-center justify-center"
        style={{
          background: `linear-gradient(135deg, ${activeColor}40 0%, ${activeColor}12 100%)`,
          border: `2px solid ${activeColor}70`,
          willChange: 'transform, box-shadow',
        }}
        animate={{ 
          scale: anim.scale,
          boxShadow: [
            `0 0 15px ${activeGlow}`,
            `0 0 25px ${activeGlow}`,
            `0 0 15px ${activeGlow}`,
          ],
        }}
        transition={{
          scale: {
            duration: anim.duration,
            repeat: Infinity,
            ease: 'easeInOut',
          },
          boxShadow: {
            duration: anim.duration,
            repeat: Infinity,
            ease: 'easeInOut',
          },
        }}
      >
        {/* 闪电Graph标 - Root据State有微动效 */}
        <motion.div
          animate={
            state === 'thinking' 
              ? { rotate: [0, 5, -5, 0] }
              : state === 'acting'
                ? { scale: [1, 1.1, 1] }
                : {}
          }
          transition={{
            duration: 0.5,
            repeat: state === 'thinking' || state === 'acting' ? Infinity : 0,
            ease: 'easeInOut',
          }}
        >
          <Zap 
            className="w-9 h-9" 
            style={{ 
              color: activeColor,
              filter: `drop-shadow(0 0 8px ${activeColor})`,
            }}
            fill={activeColor}
          />
        </motion.div>
      </motion.div>
      
      {/* State标签 */}
      <motion.div
        className="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap flex flex-col items-center gap-1"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <motion.span 
          className="text-sm font-bold"
          style={{ 
            color: activeColor,
            textShadow: `0 0 12px ${activeGlow}`,
          }}
        >
          NogicOS
        </motion.span>
        {state !== 'idle' && (
          <motion.span 
            className="text-[11px] px-3 py-1 rounded-full font-medium"
            style={{ 
              backgroundColor: `${activeColor}30`,
              color: activeColor,
              boxShadow: `0 0 15px ${activeGlow}`,
            }}
            initial={{ opacity: 0, y: -5, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={SPRING.bouncy}
          >
            {state === 'thinking' ? 'Thinking...' :
             state === 'reading' ? 'Reading...' :
             state === 'acting' ? 'Executing...' : 'Done!'}
          </motion.span>
        )}
      </motion.div>
    </motion.div>
  );
});

// ============================================================================
// Main BubbleCanvas Component
// ============================================================================

export const BubbleCanvas = memo(function BubbleCanvas({
  availableWindows,
  connectedApps,
  onConnect,
  onDisconnect,
  onOpenLiveArea,
  aiState = 'idle',
  activeAppHwnd,
  outputType = 'idle',
  targetHwnd,
  sourceHwnd,
  className,
}: BubbleCanvasProps) {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleCanvas.tsx:props',message:'H4: Canvas props received',data:{aiState,outputType,targetHwnd,sourceHwnd,connectedAppsCount:connectedApps?.length},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H4'})}).catch(()=>{});
  // #endregion
  
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [bubblePositions, setBubblePositions] = useState<Map<number, BubblePosition>>(new Map());
  
  // Connection animation state
  const [connectingHwnd, setConnectingHwnd] = useState<number | null>(null);
  const [ripples, setRipples] = useState<Array<{ id: number; x: number; y: number }>>([]);
  
  // Drag state - for simplified line rendering to improve smoothness
  const [isDraggingAny, setIsDraggingAny] = useState(false);
  const [draggingHwnd, setDraggingHwnd] = useState<number | null>(null);
  
  // Performance monitoring and auto-degradation
  const { metrics, config: perfConfig } = useAnimationPerformance({
    fpsThreshold: 30,
    autoDegrade: true,
  });
  
  // Calculate center position
  const centerX = dimensions.width / 2;
  const centerY = dimensions.height / 2;
  
  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        if (rect.width > 100 && rect.height > 100) {
          setDimensions({ width: rect.width, height: rect.height });
        }
      }
    };
    
    // Update on first render and resize
    updateDimensions();
    
    // Use ResizeObserver to listen for container size changes
    const resizeObserver = new ResizeObserver(() => {
      updateDimensions();
    });
    
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    
    window.addEventListener('resize', updateDimensions);
    
    // Delayed update to ensure container is rendered
    const timeout = setTimeout(updateDimensions, 100);
    
    return () => {
      window.removeEventListener('resize', updateDimensions);
      resizeObserver.disconnect();
      clearTimeout(timeout);
    };
  }, []);
  
  // Record previous center point for proportional scaling
  const prevCenterRef = useRef({ x: 400, y: 300 });
  const isInitializedRef = useRef(false);
  
  // Generate positions only for connected apps (canvas only shows connected apps)
  useEffect(() => {
    // Wait for container to have actual size
    if (dimensions.width <= 100 || dimensions.height <= 100) return;
    
    // Only calculate positions for connected apps
    if (connectedApps.length === 0) return;
    
    const radius = Math.min(dimensions.width, dimensions.height) * 0.28;
    const prevCenter = prevCenterRef.current;
    
    setBubblePositions(prev => {
      const newPositions = new Map<number, BubblePosition>();
      
      // Preserve existing positions (for scaling)
      const scale = Math.min(dimensions.width, dimensions.height) / 
                    Math.min(prevCenter.x * 2 || dimensions.width, prevCenter.y * 2 || dimensions.height);
      
      // Calculate/update position for each connected app
      connectedApps.forEach((app, index) => {
        const existingPos = prev.get(app.hwnd);
        
        if (existingPos) {
          // Existing position, scale proportionally
          const relX = existingPos.x + 32 - prevCenter.x;
          const relY = existingPos.y + 32 - prevCenter.y;
          
          let newX = centerX + relX * scale - 32;
          let newY = centerY + relY * scale - 32;
          
          // Boundary check
          newX = Math.max(0, Math.min(dimensions.width - 64, newX));
          newY = Math.max(0, Math.min(dimensions.height - 64, newY));
          
          newPositions.set(app.hwnd, { x: newX, y: newY, scale: existingPos.scale });
        } else {
          // Newly connected app, calculate initial position (distributed around center)
          const angle = (2 * Math.PI * index) / Math.max(connectedApps.length, 1) - Math.PI / 2;
          const jitter = (Math.random() - 0.5) * 15;
          
          newPositions.set(app.hwnd, {
            x: centerX + Math.cos(angle) * (radius + jitter) - 32,
            y: centerY + Math.sin(angle) * (radius + jitter) - 32,
            scale: 0.95 + Math.random() * 0.1,
          });
        }
      });
      
      return newPositions;
    });
    
    // Update previous center point
    prevCenterRef.current = { x: centerX, y: centerY };
  }, [connectedApps, dimensions, centerX, centerY]);
  
  // Handle bubble click with animation
  const handleBubbleClick = useCallback((window: WindowInfo) => {
    const isConnected = connectedApps.some(app => app.hwnd === window.hwnd);
    
    if (isConnected) {
      // Already connected - just focus it
      const connectedApp = connectedApps.find(app => app.hwnd === window.hwnd);
      if (connectedApp) {
        onOpenLiveArea(connectedApp);
      }
    } else {
      // Not connected - play connect animation then connect
      const position = bubblePositions.get(window.hwnd);
      
      // 1. Start connecting animation
      setConnectingHwnd(window.hwnd);
      
      // 2. After line animation, show ripple and connect
      setTimeout(() => {
        // Add ripple effect
        if (position) {
          const rippleId = Date.now();
          setRipples(prev => [...prev, { id: rippleId, x: position.x, y: position.y }]);
          
          // Remove ripple after animation
          setTimeout(() => {
            setRipples(prev => prev.filter(r => r.id !== rippleId));
          }, 1000);
        }
        
        // Actually connect
        onConnect(window);
        setConnectingHwnd(null);
      }, 600); // Match the line animation duration
    }
  }, [connectedApps, onConnect, onOpenLiveArea, bubblePositions]);
  
  // Drag offset - for real-time line following
  const [dragOffset, setDragOffset] = useState<{ hwnd: number; x: number; y: number } | null>(null);
  
  // Handle bubble drag - only update offset, don't trigger position state update
  const handleDrag = useCallback((hwnd: number, offsetX: number, offsetY: number) => {
    setDragOffset({ hwnd, x: offsetX, y: offsetY });
  }, []);
  
  // Handle bubble drag end - drag finished
  const handleDragEnd = useCallback((hwnd: number, newX: number, newY: number) => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleCanvas:handleDragEnd',message:'handleDragEnd called',data:{hwnd,newX,newY,dimensionsWidth:dimensions.width,dimensionsHeight:dimensions.height},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H1'})}).catch(()=>{});
    // #endregion
    
    // Clear drag state
    setIsDraggingAny(false);
    setDraggingHwnd(null);
    setDragOffset(null);
    
    setBubblePositions(prev => {
      const newPositions = new Map(prev);
      const existing = newPositions.get(hwnd);
      if (existing) {
        // Boundary check - ensure bubble is within visible range
        const clampedX = Math.max(0, Math.min(dimensions.width - 64, newX));
        const clampedY = Math.max(0, Math.min(dimensions.height - 64, newY));
        
        newPositions.set(hwnd, { 
          ...existing, 
          x: clampedX, 
          y: clampedY,
        });
      }
      return newPositions;
    });
  }, [dimensions.width, dimensions.height]);
  
  // Separate connected and unconnected windows
  const connectedHwnds = new Set(connectedApps.map(app => app.hwnd));
  const unconnectedWindows = availableWindows.filter(w => !connectedHwnds.has(w.hwnd));
  
  // Only show connected apps on canvas
  const canvasWindows = connectedApps;
  
  return (
    <div
      ref={containerRef}
      className={cn(
        "relative w-full h-full overflow-hidden",
        "bg-gradient-to-b from-[#0a0a0a] to-[#111]",
        className
      )}
    >
      {/* Background grid */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }}
      />
      
      {/* Connection lines - 已Connect的应用 */}
      <AnimatePresence>
        {connectedApps.map(app => {
          const position = bubblePositions.get(app.hwnd);
          if (!position) return null;
          
          // Determine outputType and flow direction for this connection line
          const isTargetApp = targetHwnd === app.hwnd;
          const isSourceApp = sourceHwnd === app.hwnd;
          const lineOutputType = isTargetApp || isSourceApp ? outputType : 'idle';
          const flowDir = isSourceApp ? 'in' as const : isTargetApp ? 'out' as const : 'none' as const;
          
          // If dragging this bubble, use offset
          const isDraggingThis = dragOffset?.hwnd === app.hwnd;
          const lineStartX = isDraggingThis ? position.x + dragOffset.x : position.x;
          const lineStartY = isDraggingThis ? position.y + dragOffset.y : position.y;
          
          return (
            <ConnectionLine
              key={`line-${app.hwnd}`}
              startX={lineStartX}
              startY={lineStartY}
              endX={centerX}
              endY={centerY}
              isActive={aiState !== 'idle'}
              isConnecting={false}
              isDragging={isDraggingAny}
              outputType={lineOutputType}
              flowDirection={flowDir}
              enableParticles={perfConfig.enableParticles}
              maxParticles={perfConfig.particleCount}
            />
          );
        })}
      </AnimatePresence>
      
      {/* Connection line - 正在Connect的应用 */}
      <AnimatePresence>
        {connectingHwnd && !connectedApps.some(a => a.hwnd === connectingHwnd) && (
          (() => {
            const position = bubblePositions.get(connectingHwnd);
            if (!position) return null;
            
            return (
              <ConnectionLine
                key={`connecting-${connectingHwnd}`}
                startX={position.x}
                startY={position.y}
                endX={centerX}
                endY={centerY}
                isActive={false}
                isConnecting={true}
                isDragging={isDraggingAny}
                enableParticles={perfConfig.enableParticles}
                maxParticles={perfConfig.particleCount}
              />
            );
          })()
        )}
      </AnimatePresence>
      
      {/* Connection ripples */}
      <AnimatePresence>
        {ripples.map(ripple => (
          <ConnectionRipple
            key={ripple.id}
            x={ripple.x}
            y={ripple.y}
          />
        ))}
      </AnimatePresence>
      
      {/* AppDock removed - 未Connect应用已移到侧边栏 */}
      
      {/* Center AI Node - 2026 顶级版本 */}
      <CenterAINode x={centerX} y={centerY} state={aiState} outputType={outputType} />
      
      {/* App Bubbles - 只Display已Connect的应用 */}
      <AnimatePresence>
        {canvasWindows.map((window, index) => {
          const position = bubblePositions.get(window.hwnd);
          if (!position) return null;
          
          const isActive = activeAppHwnd === window.hwnd && aiState !== 'idle';
          // When there's an active app, dim other apps
          const isDimmed = activeAppHwnd !== undefined && activeAppHwnd !== window.hwnd && aiState !== 'idle';
          // 2026 Premium: Source/Target state
          const isSourceApp = sourceHwnd === window.hwnd && outputType !== 'idle';
          const isTargetApp = targetHwnd === window.hwnd && outputType !== 'idle';
          
          // #region agent log
          if (index === 0) {
            fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'BubbleCanvas.tsx:AppBubble:render',message:'H5: Bubble state check',data:{windowHwnd:window.hwnd,sourceHwnd,targetHwnd,outputType,isSourceApp,isTargetApp,aiState},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H5'})}).catch(()=>{});
          }
          // #endregion
          
          return (
            <AppBubble
              key={window.hwnd}
              window={window}
              isConnected={true}
              isActive={isActive}
              isDimmed={isDimmed}
              isSource={isSourceApp}
              isTarget={isTargetApp}
              position={position}
              index={index}
              onClick={() => handleBubbleClick(window)}
              onDragStart={() => {
                setIsDraggingAny(true);
                setDraggingHwnd(window.hwnd);
              }}
              onDrag={(x, y) => handleDrag(window.hwnd, x, y)}
              onDragEnd={(x, y) => handleDragEnd(window.hwnd, x, y)}
              isSelfDragging={draggingHwnd === window.hwnd}
            />
          );
        })}
      </AnimatePresence>
      
      {/* Empty state hint - 简化版，避免重复 */}
      
      {/* Instructions overlay */}
      {canvasWindows.length > 0 && (
        <motion.div
          className="absolute bottom-4 left-1/2 -translate-x-1/2"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <div className="flex items-center gap-4 text-[11px] text-white/30">
            <span>Drag to reposition</span>
            <span>•</span>
            <span>Click for details</span>
          </div>
        </motion.div>
      )}
      
    </div>
  );
});

export default BubbleCanvas;
