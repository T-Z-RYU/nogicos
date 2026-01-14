/**
 * ExecutionFlowPanel - Execute流面板
 * 
 * 实时Display AI 的工作过程：思考、Tool调用、ExecuteResult
 */

import { memo, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Brain,
  Eye,
  Pencil,
  Check,
  X,
  Loader2,
  Terminal,
  Search,
  FileText,
  Globe,
  Code2,
  MousePointer,
  Keyboard,
  Sparkles,
  ChevronRight,
  Clock,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

export type ExecutionStepStatus = 'pending' | 'running' | 'success' | 'error';
export type ExecutionStepType = 'thinking' | 'tool_call' | 'tool_result' | 'message';

export interface ExecutionStep {
  id: string;
  type: ExecutionStepType;
  status: ExecutionStepStatus;
  timestamp: Date;
  // ToolCallrelatedOff
  toolName?: string;
  toolInput?: Record<string, unknown>;
  toolOutput?: unknown;
  // MessagerelatedOff
  content?: string;
  // Offconnect's Apply
  targetApp?: string;
  targetHwnd?: number;
}

interface ExecutionFlowPanelProps {
  steps: ExecutionStep[];
  isVisible: boolean;
  onClose?: () => void;
  className?: string;
}

// ============================================================================
// Constants
// ============================================================================

const SPRING = {
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
};

// ToolnametoGraphmark's Map
const TOOL_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  // BrowserTool
  browser_navigate: Globe,
  browser_click: MousePointer,
  browser_type: Keyboard,
  browser_scroll: MousePointer,
  browser_snapshot: Eye,
  playwright_find_elements: Search,
  playwright_click: MousePointer,
  playwright_type: Keyboard,
  // FileTool
  read_file: FileText,
  write_file: Pencil,
  list_directory: FileText,
  glob_search: Search,
  // SearchTool
  search_web: Globe,
  // Other
  execute_command: Terminal,
  run_code: Code2,
};

// Toolname's friendlyDisplay
const TOOL_LABELS: Record<string, string> = {
  browser_navigate: '导航到页面',
  browser_click: '点击元素',
  browser_type: 'Input文字',
  browser_scroll: '滚动页面',
  browser_snapshot: '截取页面',
  playwright_find_elements: 'Find元素',
  playwright_click: '点击',
  playwright_type: 'Input',
  read_file: 'ReadFile',
  write_file: 'WriteFile',
  list_directory: 'Column出Directory',
  glob_search: 'SearchFile',
  search_web: 'webpageSearch',
  execute_command: 'ExecuteCommand',
  run_code: 'Running代码',
};

const STATUS_CONFIG = {
  pending: {
    color: 'text-white/40',
    bgColor: 'bg-white/5',
    borderColor: 'border-white/10',
    icon: Clock,
  },
  running: {
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30',
    icon: Loader2,
  },
  success: {
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30',
    icon: Check,
  },
  error: {
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
    icon: X,
  },
};

// ============================================================================
// Step Item Component
// ============================================================================

const ExecutionStepItem = memo(function ExecutionStepItem({
  step,
  index,
}: {
  step: ExecutionStep;
  index: number;
}) {
  const statusConfig = STATUS_CONFIG[step.status];
  const StatusIcon = statusConfig.icon;
  
  // RootdataStepClasstypeSelectGraphmark
  const getStepIcon = () => {
    if (step.type === 'thinking') return Brain;
    if (step.type === 'message') return Sparkles;
    if (step.toolName) {
      return TOOL_ICONS[step.toolName] || Terminal;
    }
    return Terminal;
  };
  
  const StepIcon = getStepIcon();
  
  // GetStepLabel
  const getStepLabel = () => {
    if (step.type === 'thinking') return 'Thinking...';
    if (step.type === 'message') return step.content?.slice(0, 50) || 'Generating reply';
    if (step.toolName) {
      return TOOL_LABELS[step.toolName] || step.toolName.replace(/_/g, ' ');
    }
    return 'Executing';
  };
  
  // FormatterTime
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };
  
  // GetToolInputSummary
  const getInputSummary = () => {
    if (!step.toolInput) return null;
    const input = step.toolInput;
    
    // RootdataToolClasstypeDisplayKeyInfo
    if (input.url) return input.url as string;
    if (input.selector) return `Select器: ${input.selector}`;
    if (input.text) return `"${(input.text as string).slice(0, 30)}..."`;
    if (input.path) return input.path as string;
    if (input.query) return `"${input.query}"`;
    
    return null;
  };
  
  const inputSummary = getInputSummary();

  return (
    <motion.div
      initial={{ opacity: 0, x: -10, height: 0 }}
      animate={{ opacity: 1, x: 0, height: 'auto' }}
      exit={{ opacity: 0, x: 10, height: 0 }}
      transition={{ ...SPRING.snappy, delay: index * 0.05 }}
      className={cn(
        "relative pl-6 pb-4",
        index === 0 && "pt-0"
      )}
    >
      {/* Time线 */}
      <div className="absolute left-[9px] top-0 bottom-0 w-px bg-white/10" />
      
      {/* State指示器 */}
      <motion.div
        className={cn(
          "absolute left-0 top-0.5 w-[18px] h-[18px] rounded-full flex items-center justify-center",
          "border",
          statusConfig.bgColor,
          statusConfig.borderColor
        )}
        animate={step.status === 'running' ? { scale: [1, 1.1, 1] } : {}}
        transition={{ duration: 1, repeat: step.status === 'running' ? Infinity : 0 }}
      >
        <StatusIcon 
          className={cn(
            "w-2.5 h-2.5",
            statusConfig.color,
            step.status === 'running' && "animate-spin"
          )} 
        />
      </motion.div>
      
      {/* Inner容 */}
      <div className="space-y-1">
        {/* titleRow */}
        <div className="flex items-center gap-2">
          <StepIcon className={cn("w-3.5 h-3.5", statusConfig.color)} />
          <span className="text-xs font-medium text-white/80">
            {getStepLabel()}
          </span>
          <span className="text-[10px] text-white/30 ml-auto">
            {formatTime(step.timestamp)}
          </span>
        </div>
        
        {/* Input摘要 */}
        {inputSummary && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-[10px] text-white/40 pl-5.5 truncate max-w-full"
          >
            <ChevronRight className="w-2.5 h-2.5 inline mr-1 opacity-50" />
            {inputSummary}
          </motion.div>
        )}
        
        {/* Target应用 */}
        {step.targetApp && (
          <div className="text-[10px] text-white/30 pl-5.5 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/50" />
            {step.targetApp}
          </div>
        )}
        
        {/* ToolOutput（Success时） */}
        {step.status === 'success' && step.toolOutput && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-1.5 p-2 rounded bg-emerald-500/5 border border-emerald-500/10"
          >
            <div className="text-[10px] text-emerald-400/70 font-mono truncate">
              {typeof step.toolOutput === 'string' 
                ? step.toolOutput.slice(0, 100) 
                : JSON.stringify(step.toolOutput).slice(0, 100)}
              {(typeof step.toolOutput === 'string' ? step.toolOutput.length : JSON.stringify(step.toolOutput).length) > 100 && '...'}
            </div>
          </motion.div>
        )}
        
        {/* ErrorInfo */}
        {step.status === 'error' && step.toolOutput && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-1.5 p-2 rounded bg-red-500/5 border border-red-500/10"
          >
            <div className="text-[10px] text-red-400/70">
              {String(step.toolOutput).slice(0, 100)}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
});

// ============================================================================
// Main Component
// ============================================================================

export const ExecutionFlowPanel = memo(function ExecutionFlowPanel({
  steps,
  isVisible,
  onClose,
  className,
}: ExecutionFlowPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // AutoScrolltoBottom
  useEffect(() => {
    if (scrollRef.current && steps.length > 0) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [steps]);
  
  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={SPRING.snappy}
      className={cn(
        "w-72 h-full bg-[#0d0d0d] border-l border-white/[0.06]",
        "flex flex-col",
        className
      )}
    >
      {/* Head部 */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <motion.div
            animate={{ rotate: steps.some(s => s.status === 'running') ? 360 : 0 }}
            transition={{ duration: 2, repeat: steps.some(s => s.status === 'running') ? Infinity : 0, ease: 'linear' }}
          >
            <Brain className="w-4 h-4 text-emerald-400" />
          </motion.div>
          <h3 className="text-sm font-medium text-white/80">Execute流程</h3>
          {steps.length > 0 && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-white/40">
              {steps.length}
            </span>
          )}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="w-6 h-6 rounded flex items-center justify-center text-white/40 hover:text-white/60 hover:bg-white/5 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
      
      {/* 步骤List */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-3"
      >
        {steps.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <motion.div
              className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-3"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Sparkles className="w-5 h-5 text-white/30" />
            </motion.div>
            <p className="text-xs text-white/40 mb-1">WaitExecute</p>
            <p className="text-[10px] text-white/25">
              Send a message to start
            </p>
          </div>
        ) : (
          <AnimatePresence mode="popLayout">
            {steps.map((step, index) => (
              <ExecutionStepItem
                key={step.id}
                step={step}
                index={index}
              />
            ))}
          </AnimatePresence>
        )}
      </div>
      
      {/* Bottom stats */}
      {steps.length > 0 && (
        <div className="px-4 py-2 border-t border-white/[0.06] flex items-center justify-between text-[10px] text-white/30">
          <span>
            {steps.filter(s => s.status === 'success').length} done
          </span>
          <span>
            {steps.filter(s => s.status === 'running').length > 0 && (
              <motion.span
                className="text-amber-400"
                animate={{ opacity: [1, 0.5, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              >
                Executing...
              </motion.span>
            )}
          </span>
        </div>
      )}
    </motion.div>
  );
});

export default ExecutionFlowPanel;
