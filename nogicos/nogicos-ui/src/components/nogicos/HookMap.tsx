/**
 * HookMap - Neural Link 可视化
 * 
 * 设计理念：
 * - AI Yes"大脑"，应用Yes"感知器"，ConnectYes"神经"
 * - 思考时有波纹向Outer扩散
 * - Read/Write时有数据脉冲沿神经传输
 * - NodeRoot据Active度自然聚集
 * 
 * Joyful 元素：
 * - 有生命感的Animation
 * - 清晰的Info层次
 * - 微妙但精致的细节
 */

import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform, animate } from 'motion/react';
import { 
  Globe, 
  Code2, 
  FileText, 
  AppWindow,
  Zap,
  Brain,
  Sparkles,
  Eye,
  Pencil,
  Lightbulb,
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

/** AI State */
type AIState = 'idle' | 'reading' | 'thinking' | 'acting' | 'success';

interface DataFlowState {
  sourceHwnd: number | null;
  targetHwnd: number | null;
  direction: 'in' | 'out';
  action?: string;
  progress?: number;
}

/** 思考Log条目 */
interface ThinkingLogEntry {
  id: string;
  type: 'read' | 'think' | 'act' | 'success';
  content: string;
  timestamp: number;
  appName?: string;
}

interface HookMapProps {
  connectedApps: ConnectedApp[];
  dataFlow?: DataFlowState;
  aiState?: AIState;
  thinkingLog?: ThinkingLogEntry[];
  currentAction?: string;
  onDisconnect?: (hwnd: number) => void;
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const SPRING = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
  smooth: { type: 'spring' as const, stiffness: 200, damping: 20 },
  bouncy: { type: 'spring' as const, stiffness: 300, damping: 15 },
};

const COLORS = {
  emerald: {
    primary: '#10b981',
    light: '#34d399',
    dark: '#059669',
    glow: 'rgba(16, 185, 129, 0.4)',
    subtle: 'rgba(16, 185, 129, 0.1)',
  },
  amber: {
    primary: '#f59e0b',
    light: '#fbbf24',
    glow: 'rgba(245, 158, 11, 0.4)',
  },
  violet: {
    primary: '#8b5cf6',
    light: '#a78bfa',
    glow: 'rgba(139, 92, 246, 0.4)',
  },
  sky: {
    primary: '#0ea5e9',
    light: '#38bdf8',
    glow: 'rgba(14, 165, 233, 0.4)',
  },
};

const STATE_COLORS = {
  idle: COLORS.emerald,
  reading: COLORS.sky,
  thinking: COLORS.violet,
  acting: COLORS.amber,
  success: COLORS.emerald,
};

const STATE_ICONS = {
  idle: Zap,
  reading: Eye,
  thinking: Brain,
  acting: Pencil,
  success: Sparkles,
};

// ============================================================================
// App Icon Mapping
// ============================================================================

const APP_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  'Google Chrome': Globe,
  'Chrome': Globe,
  'Mozilla Firefox': Globe,
  'Microsoft Edge': Globe,
  'Brave': Globe,
  'Arc': Globe,
  'VS Code': Code2,
  'Cursor': Code2,
  'File Explorer': FileText,
  'Finder': FileText,
  'Figma': AppWindow,
};

function getAppIcon(appName: string) {
  // trypreciseMatch
  if (APP_ICONS[appName]) return APP_ICONS[appName];
  // tryPartialMatch
  for (const [key, icon] of Object.entries(APP_ICONS)) {
    if (appName.toLowerCase().includes(key.toLowerCase())) return icon;
  }
  return AppWindow;
}

// ============================================================================
// Sub-Components
// ============================================================================

/**
 * Medium心Node - AI 大脑
 * Root据StateDisplay不同的AnimationEffect
 */
function AIBrain({ 
  state = 'idle',
  connectedCount = 0,
}: { 
  state: AIState;
  connectedCount: number;
}) {
  const StateIcon = STATE_ICONS[state];
  const colors = STATE_COLORS[state];
  
  return (
    <div className="relative flex flex-col items-center">
      {/* 思考波纹 - 只在 thinking StateDisplay */}
      <AnimatePresence>
        {state === 'thinking' && (
          <>
            {[1, 2, 3].map((i) => (
              <motion.div
                key={i}
                className="absolute rounded-full border"
                style={{
                  borderColor: colors.primary,
                  width: 80,
                  height: 80,
                }}
                initial={{ scale: 1, opacity: 0.6 }}
                animate={{ 
                  scale: [1, 2.5], 
                  opacity: [0.6, 0],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: i * 0.6,
                  ease: 'easeOut',
                }}
              />
            ))}
          </>
        )}
      </AnimatePresence>

      {/* Outer圈光晕 */}
      <motion.div
        className="absolute rounded-full"
        style={{
          width: 100,
          height: 100,
          background: `radial-gradient(circle, ${colors.glow} 0%, transparent 70%)`,
        }}
        animate={{
          scale: state === 'idle' ? [1, 1.1, 1] : [1, 1.2, 1],
          opacity: state === 'idle' ? 0.3 : 0.6,
        }}
        transition={{
          duration: state === 'idle' ? 4 : 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      {/* 主圆 */}
      <motion.div
        className="relative w-20 h-20 rounded-full flex items-center justify-center overflow-hidden"
        style={{
          background: `linear-gradient(135deg, ${colors.dark || colors.primary} 0%, ${colors.primary} 50%, ${colors.light} 100%)`,
          boxShadow: `0 0 40px ${colors.glow}`,
          willChange: 'transform',
        }}
        animate={{
          scale: state === 'acting' ? [1, 1.05, 1] : 1,
        }}
        transition={{
          duration: 0.3,
          repeat: state === 'acting' ? Infinity : 0,
        }}
      >
        {/* 扫描线Effect */}
        <motion.div
          className="absolute inset-0"
          initial={{ rotate: 0 }}
          animate={{ rotate: 360 }}
          transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
        >
          <div 
            className="absolute top-0 left-1/2 w-1/2 h-full origin-left"
            style={{
              background: `linear-gradient(90deg, transparent 0%, ${colors.light}30 100%)`,
            }}
          />
        </motion.div>

        {/* StateGraph标 */}
        <motion.div
          key={state}
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={SPRING.bouncy}
        >
          <StateIcon className="w-8 h-8 text-white relative z-10" />
        </motion.div>
      </motion.div>

      {/* 标签 */}
      <motion.div 
        className="mt-3 text-center"
        layout
      >
        <div className="text-sm font-medium text-white">NogicOS</div>
        <motion.div 
          className="text-xs mt-0.5"
          style={{ color: colors.light }}
          key={state}
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {state === 'idle' && `${connectedCount} connected`}
          {state === 'reading' && 'Reading...'}
          {state === 'thinking' && 'Thinking...'}
          {state === 'acting' && 'Acting...'}
          {state === 'success' && 'Done!'}
        </motion.div>
      </motion.div>
    </div>
  );
}

/**
 * 应用Node - 感知器
 */
function SensorNode({ 
  app, 
  position, 
  isActive,
  flowDirection,
  onDisconnect,
  index,
  total,
}: { 
  app: ConnectedApp;
  position: { x: number; y: number; angle: number };
  isActive: boolean;
  flowDirection?: 'in' | 'out';
  onDisconnect?: () => void;
  index: number;
  total: number;
}) {
  const Icon = getAppIcon(app.app_display_name);
  const colors = isActive 
    ? (flowDirection === 'out' ? COLORS.amber : COLORS.sky)
    : COLORS.emerald;

  // calculate labelPosition(avoid overlap)
  const labelPosition = useMemo(() => {
    const angle = position.angle;
    // based on angleLabelPosition
    if (angle > -Math.PI / 4 && angle < Math.PI / 4) {
      return 'right';
    } else if (angle > Math.PI * 3 / 4 || angle < -Math.PI * 3 / 4) {
      return 'left';
    } else if (angle >= Math.PI / 4 && angle <= Math.PI * 3 / 4) {
      return 'bottom';
    } else {
      return 'top';
    }
  }, [position.angle]);

  return (
    <motion.div
      className="absolute"
      style={{ 
        left: position.x, 
        top: position.y,
        willChange: 'transform, opacity',
      }}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ 
        scale: 1, 
        opacity: 1,
        x: '-50%',
        y: '-50%',
      }}
      exit={{ scale: 0, opacity: 0 }}
      transition={{
        ...SPRING.bouncy,
        delay: index * 0.08,
      }}
    >
      {/* Active光晕 */}
      <AnimatePresence>
        {isActive && (
          <motion.div
            className="absolute rounded-full"
            style={{
              width: 56,
              height: 56,
              left: '50%',
              top: '50%',
              x: '-50%',
              y: '-50%',
              background: `radial-gradient(circle, ${colors.glow} 0%, transparent 70%)`,
            }}
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ 
              scale: [1, 1.5, 1],
              opacity: [0.8, 0.3, 0.8],
            }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
      </AnimatePresence>

      {/* 主圆 */}
      <motion.div
        className={cn(
          "relative w-14 h-14 rounded-full flex items-center justify-center cursor-pointer",
          "border-2 transition-colors duration-300",
        )}
        style={{
          borderColor: isActive ? colors.primary : 'rgba(255,255,255,0.1)',
          backgroundColor: isActive ? `${colors.primary}20` : 'rgba(10,10,10,0.8)',
          boxShadow: isActive ? `0 0 20px ${colors.glow}` : 'none',
        }}
        whileHover={{ 
          scale: 1.15,
          borderColor: colors.primary,
        }}
        whileTap={{ scale: 0.95 }}
        transition={SPRING.snappy}
        onClick={onDisconnect}
      >
        <Icon className={cn(
          "w-6 h-6 transition-colors duration-300",
          isActive ? "text-white" : "text-neutral-400"
        )} />

        {/* ConnectState点 */}
        <motion.div
          className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full"
          style={{ backgroundColor: COLORS.emerald.primary }}
          animate={{
            boxShadow: [
              `0 0 0 0 ${COLORS.emerald.glow}`,
              `0 0 0 4px transparent`,
            ],
          }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      </motion.div>

      {/* 标签 */}
      <motion.div 
        className={cn(
          "absolute whitespace-nowrap",
          labelPosition === 'bottom' && "top-full mt-2 left-1/2 -translate-x-1/2",
          labelPosition === 'top' && "bottom-full mb-2 left-1/2 -translate-x-1/2",
          labelPosition === 'left' && "right-full mr-3 top-1/2 -translate-y-1/2 text-right",
          labelPosition === 'right' && "left-full ml-3 top-1/2 -translate-y-1/2",
        )}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 + index * 0.08 }}
      >
        <div className={cn(
          "text-xs font-medium transition-colors",
          isActive ? "text-white" : "text-neutral-500"
        )}>
          {app.app_display_name}
        </div>
      </motion.div>
    </motion.div>
  );
}

/**
 * 神经Connect线
 */
function NeuralConnection({
  startX,
  startY,
  endX,
  endY,
  isActive,
  flowDirection,
  index,
}: {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  isActive: boolean;
  flowDirection?: 'in' | 'out';
  index: number;
}) {
  const colors = isActive 
    ? (flowDirection === 'out' ? COLORS.amber : COLORS.sky)
    : COLORS.emerald;

  // calculate bezier curvecontrolPoint(make lines more curved)
  const midX = (startX + endX) / 2;
  const midY = (startY + endY) / 2;
  const dx = endX - startX;
  const dy = endY - startY;
  const dist = Math.sqrt(dx * dx + dy * dy);
  
  // controlPointOffset（letCurvemoreselfthen）
  const offset = dist * 0.15;
  const perpX = -dy / dist * offset;
  const perpY = dx / dist * offset;
  
  const ctrlX = midX + perpX;
  const ctrlY = midY + perpY;
  
  const pathD = `M ${startX} ${startY} Q ${ctrlX} ${ctrlY} ${endX} ${endY}`;

  return (
    <g>
      {/* 基础线 - 始终Display */}
      <motion.path
        d={pathD}
        fill="none"
        stroke={isActive ? colors.primary : 'rgba(255,255,255,0.08)'}
        strokeWidth={isActive ? 2 : 1}
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ 
          duration: 0.8, 
          delay: index * 0.1,
          ease: 'easeOut',
        }}
      />

      {/* Active时的发光Effect */}
      {isActive && (
        <motion.path
          d={pathD}
          fill="none"
          stroke={colors.light}
          strokeWidth={4}
          style={{ filter: `blur(4px)` }}
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}

      {/* 数据脉冲 */}
      {isActive && flowDirection && (
        <>
          {[0, 1, 2].map((i) => (
            <motion.circle
              key={i}
              r={4}
              fill={colors.light}
              style={{ filter: `drop-shadow(0 0 6px ${colors.primary})` }}
            >
              <motion.animate
                attributeName="cx"
                values={flowDirection === 'in' 
                  ? `${startX};${ctrlX};${endX}` 
                  : `${endX};${ctrlX};${startX}`
                }
                keyTimes="0;0.5;1"
                dur="1.2s"
                repeatCount="indefinite"
                begin={`${i * 0.4}s`}
              />
              <motion.animate
                attributeName="cy"
                values={flowDirection === 'in' 
                  ? `${startY};${ctrlY};${endY}` 
                  : `${endY};${ctrlY};${startY}`
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
}

/**
 * 思考Log面板
 */
function ThinkingLogPanel({ 
  entries = [],
  aiState,
}: { 
  entries: ThinkingLogEntry[];
  aiState: AIState;
}) {
  const colors = STATE_COLORS[aiState];
  
  // onlyDisplaymostnear's  3 item
  const recentEntries = entries.slice(-3);

  const getIcon = (type: ThinkingLogEntry['type']) => {
    switch (type) {
      case 'read': return Eye;
      case 'think': return Lightbulb;
      case 'act': return Pencil;
      case 'success': return Sparkles;
      default: return Zap;
    }
  };

  const getColor = (type: ThinkingLogEntry['type']) => {
    switch (type) {
      case 'read': return COLORS.sky;
      case 'think': return COLORS.violet;
      case 'act': return COLORS.amber;
      case 'success': return COLORS.emerald;
      default: return COLORS.emerald;
    }
  };

  if (recentEntries.length === 0 && aiState === 'idle') {
    return (
      <div className="h-full flex items-center justify-center">
        <span className="text-neutral-600 text-sm">Waiting for action...</span>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col justify-end gap-1.5 overflow-hidden">
      <AnimatePresence mode="popLayout">
        {recentEntries.map((entry, index) => {
          const Icon = getIcon(entry.type);
          const color = getColor(entry.type);
          
          return (
            <motion.div
              key={entry.id}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
              style={{ 
                backgroundColor: `${color.primary}10`,
                borderLeft: `2px solid ${color.primary}`,
              }}
              initial={{ opacity: 0, x: -20, height: 0 }}
              animate={{ opacity: 1, x: 0, height: 'auto' }}
              exit={{ opacity: 0, x: 20, height: 0 }}
              transition={SPRING.snappy}
            >
              <Icon 
                className="w-3.5 h-3.5 flex-shrink-0" 
                style={{ color: color.primary }}
              />
              <span className="text-xs text-neutral-300 truncate">
                {entry.content}
              </span>
              {entry.appName && (
                <span 
                  className="text-xs px-1.5 py-0.5 rounded flex-shrink-0"
                  style={{ 
                    backgroundColor: `${color.primary}20`,
                    color: color.light,
                  }}
                >
                  {entry.appName}
                </span>
              )}
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function HookMap({
  connectedApps,
  dataFlow,
  aiState = 'idle',
  thinkingLog = [],
  currentAction,
  onDisconnect,
  className,
}: HookMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 400, height: 300 });

  // UpdateSize
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

  // calculateNodePosition（OptimizationAfter's Layout）
  const nodePositions = useMemo(() => {
    const visualHeight = dimensions.height - 80; // subtractLogLocaleHeight
    const centerX = dimensions.width / 2;
    const centerY = visualHeight / 2;
    
    // RootdataNodeCountresize radius
    const baseRadius = Math.min(dimensions.width, visualHeight) * 0.35;
    const radius = connectedApps.length <= 3 
      ? baseRadius * 0.8 
      : baseRadius;
    
    return connectedApps.map((app, index) => {
      // from top, clockwise distribution
      const startAngle = -Math.PI / 2;
      const angle = startAngle + (2 * Math.PI * index) / Math.max(connectedApps.length, 1);
      
      return {
        app,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        angle,
      };
    });
  }, [connectedApps, dimensions]);

  const visualHeight = dimensions.height - 80;
  const centerX = dimensions.width / 2;
  const centerY = visualHeight / 2;

  return (
    <div 
      ref={containerRef}
      className={cn(
        "relative w-full h-full min-h-[350px] overflow-hidden",
        "bg-[#0a0a0a] rounded-xl",
        className
      )}
    >
      {/* Background - 微妙的径向渐变 */}
      <div 
        className="absolute inset-0"
        style={{
          background: `radial-gradient(circle at 50% 40%, rgba(16, 185, 129, 0.03) 0%, transparent 60%)`,
        }}
      />

      {/* 可视化区域 */}
      <div 
        className="relative"
        style={{ height: visualHeight }}
      >
        {/* SVG Connect线层 */}
        <svg 
          className="absolute inset-0" 
          width={dimensions.width} 
          height={visualHeight}
          style={{ overflow: 'visible' }}
        >
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {nodePositions.map(({ app, x, y }, index) => (
            <NeuralConnection
              key={app.hwnd}
              startX={x}
              startY={y}
              endX={centerX}
              endY={centerY}
              isActive={dataFlow?.sourceHwnd === app.hwnd}
              flowDirection={dataFlow?.sourceHwnd === app.hwnd ? dataFlow.direction : undefined}
              index={index}
            />
          ))}
        </svg>

        {/* Node层 */}
        <div className="absolute inset-0">
          {/* Medium心 AI 大脑 */}
          <div 
            className="absolute"
            style={{
              left: centerX,
              top: centerY,
              transform: 'translate(-50%, -50%)',
            }}
          >
            <AIBrain 
              state={aiState} 
              connectedCount={connectedApps.length}
            />
          </div>

          {/* 应用Node */}
          <AnimatePresence>
            {nodePositions.map(({ app, x, y, angle }, index) => (
              <SensorNode
                key={app.hwnd}
                app={app}
                position={{ x, y, angle }}
                isActive={dataFlow?.sourceHwnd === app.hwnd}
                flowDirection={dataFlow?.sourceHwnd === app.hwnd ? dataFlow.direction : undefined}
                onDisconnect={() => onDisconnect?.(app.hwnd)}
                index={index}
                total={connectedApps.length}
              />
            ))}
          </AnimatePresence>
        </div>

        {/* EmptyState */}
        {connectedApps.length === 0 && (
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <div className="text-center">
              <div className="text-neutral-600 text-sm">No apps connected</div>
              <div className="text-neutral-700 text-xs mt-1">
                Connect apps below to visualize
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Bottom思考Log面板 */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-20 border-t border-neutral-900 bg-neutral-950/90 backdrop-blur-sm"
      >
        <ThinkingLogPanel 
          entries={thinkingLog}
          aiState={aiState}
        />
      </div>
    </div>
  );
}

export default HookMap;
