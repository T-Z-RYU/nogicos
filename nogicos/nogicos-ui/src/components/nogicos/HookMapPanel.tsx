/**
 * HookMapPanel - Neural Link 的容器Component
 * 
 * 提供两种展示模式：
 * 1. 嵌入式面板 (在 Sidebar Medium)
 * 2. 全屏模式 (Demo用)
 * 
 * 快捷键: Cmd/Ctrl + M Open/Close
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Activity, X, Maximize2, Play, Square } from 'lucide-react';
import { HookMap } from './HookMap';
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
  progress?: number;
}

interface ThinkingLogEntry {
  id: string;
  type: 'read' | 'think' | 'act' | 'success';
  content: string;
  timestamp: number;
  appName?: string;
}

interface HookMapPanelProps {
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
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
};

// ============================================================================
// Demo Mode - forShowAnimationEffect
// ============================================================================

function useDemoMode(connectedApps: ConnectedApp[]) {
  const [isDemoRunning, setIsDemoRunning] = useState(false);
  const [demoState, setDemoState] = useState<{
    aiState: AIState;
    dataFlow?: DataFlowState;
    thinkingLog: ThinkingLogEntry[];
  }>({
    aiState: 'idle',
    dataFlow: undefined,
    thinkingLog: [],
  });

  const demoTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const runDemo = useCallback(() => {
    if (connectedApps.length === 0) return;

    setIsDemoRunning(true);
    const targetApp = connectedApps[0];
    let logId = 0;

    const addLog = (type: ThinkingLogEntry['type'], content: string, appName?: string) => {
      const entry: ThinkingLogEntry = {
        id: `demo-${logId++}`,
        type,
        content,
        timestamp: Date.now(),
        appName,
      };
      setDemoState(prev => ({
        ...prev,
        thinkingLog: [...prev.thinkingLog.slice(-2), entry],
      }));
    };

    // Demo sequence
    const sequence = [
      // Step 1: Reading
      () => {
        setDemoState(prev => ({
          ...prev,
          aiState: 'reading',
          dataFlow: {
            sourceHwnd: targetApp.hwnd,
            targetHwnd: null,
            direction: 'in',
          },
        }));
        addLog('read', `Reading page content...`, targetApp.app_display_name);
      },
      // Step 2: Thinking
      () => {
        setDemoState(prev => ({
          ...prev,
          aiState: 'thinking',
          dataFlow: undefined,
        }));
        addLog('think', 'Analyzing form fields...');
      },
      // Step 3: More thinking
      () => {
        addLog('think', 'Found 5 empty fields to fill');
      },
      // Step 4: Acting
      () => {
        setDemoState(prev => ({
          ...prev,
          aiState: 'acting',
          dataFlow: {
            sourceHwnd: targetApp.hwnd,
            targetHwnd: null,
            direction: 'out',
          },
        }));
        addLog('act', 'Filling form...', targetApp.app_display_name);
      },
      // Step 5: Success
      () => {
        setDemoState(prev => ({
          ...prev,
          aiState: 'success',
          dataFlow: undefined,
        }));
        addLog('success', 'Form filled successfully!');
      },
      // Step 6: Back to idle
      () => {
        setDemoState({
          aiState: 'idle',
          dataFlow: undefined,
          thinkingLog: [],
        });
        setIsDemoRunning(false);
      },
    ];

    let step = 0;
    const runStep = () => {
      if (step < sequence.length) {
        sequence[step]();
        step++;
        demoTimeoutRef.current = setTimeout(runStep, step === sequence.length ? 1500 : 1200);
      }
    };

    runStep();
  }, [connectedApps]);

  const stopDemo = useCallback(() => {
    if (demoTimeoutRef.current) {
      clearTimeout(demoTimeoutRef.current);
    }
    setDemoState({
      aiState: 'idle',
      dataFlow: undefined,
      thinkingLog: [],
    });
    setIsDemoRunning(false);
  }, []);

  useEffect(() => {
    return () => {
      if (demoTimeoutRef.current) {
        clearTimeout(demoTimeoutRef.current);
      }
    };
  }, []);

  return {
    isDemoRunning,
    demoState,
    runDemo,
    stopDemo,
  };
}

// ============================================================================
// Main Component
// ============================================================================

export function HookMapPanel({
  connectedApps,
  dataFlow: externalDataFlow,
  aiState: externalAiState,
  thinkingLog: externalThinkingLog,
  currentAction,
  onDisconnect,
  className,
}: HookMapPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  // Demo mode
  const { isDemoRunning, demoState, runDemo, stopDemo } = useDemoMode(connectedApps);

  // MergeOuterpartStateand demo State
  const aiState = isDemoRunning ? demoState.aiState : (externalAiState || 'idle');
  const dataFlow = isDemoRunning ? demoState.dataFlow : externalDataFlow;
  const thinkingLog = isDemoRunning ? demoState.thinkingLog : (externalThinkingLog || []);

  // Hotkey: Cmd/Ctrl + M
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'm') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // ExtendtoFullscreen
  const handleExpand = useCallback(() => {
    setIsExpanded(true);
    setIsOpen(false);
  }, []);

  const hasActiveApps = connectedApps.length > 0;
  const isActive = aiState !== 'idle';

  return (
    <>
      {/* Trigger按钮 */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-lg transition-colors",
          "border text-sm",
          isOpen
            ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
            : hasActiveApps
            ? "border-neutral-700 bg-neutral-900 text-neutral-300 hover:border-emerald-500/30 hover:text-emerald-400"
            : "border-neutral-800 bg-neutral-900/50 text-neutral-500",
          className
        )}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        transition={SPRING.snappy}
      >
        <Activity className={cn(
          "w-4 h-4",
          isActive && "animate-pulse text-emerald-400"
        )} />
        <span>Hook Map</span>
        {hasActiveApps && (
          <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded-full">
            {connectedApps.length}
          </span>
        )}
        <kbd className="ml-auto text-[10px] text-neutral-600 bg-neutral-900 px-1.5 py-0.5 rounded font-mono">
          ⌘M
        </kbd>
      </motion.button>

      {/* 弹出面板 */}
      <AnimatePresence>
        {isOpen && !isExpanded && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={SPRING.snappy}
            className={cn(
              "absolute bottom-full left-0 right-0 mb-2 z-50",
              "bg-neutral-950 rounded-xl border border-neutral-800",
              "shadow-2xl shadow-black/50"
            )}
            style={{ height: 380 }}
          >
            {/* title栏 */}
            <div className="absolute top-0 left-0 right-0 h-10 flex items-center justify-between px-3 border-b border-neutral-800 z-10 bg-neutral-950/90 backdrop-blur-sm rounded-t-xl">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-500" />
                <span className="text-xs font-medium text-white">Hook Map</span>
                <span className="text-[10px] text-neutral-500">
                  {connectedApps.length} connected
                </span>
              </div>
              <div className="flex items-center gap-1">
                {/* Demo 按钮 */}
                {hasActiveApps && (
                  <button
                    onClick={isDemoRunning ? stopDemo : runDemo}
                    className={cn(
                      "h-6 px-2 rounded flex items-center gap-1 text-[10px] transition-colors",
                      isDemoRunning
                        ? "bg-amber-500/20 text-amber-400 hover:bg-amber-500/30"
                        : "bg-neutral-800 text-neutral-400 hover:bg-neutral-700 hover:text-white"
                    )}
                    title={isDemoRunning ? "Stop demo" : "Run demo"}
                  >
                    {isDemoRunning ? (
                      <>
                        <Square className="w-3 h-3" />
                        <span>Stop</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-3 h-3" />
                        <span>Demo</span>
                      </>
                    )}
                  </button>
                )}
                <button
                  onClick={handleExpand}
                  className="w-6 h-6 rounded flex items-center justify-center text-neutral-500 hover:text-white hover:bg-neutral-800 transition-colors"
                  title="Fullscreen"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="w-6 h-6 rounded flex items-center justify-center text-neutral-500 hover:text-white hover:bg-neutral-800 transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Hook Map */}
            <div className="pt-10 h-full">
              <HookMap
                connectedApps={connectedApps}
                dataFlow={dataFlow}
                aiState={aiState}
                thinkingLog={thinkingLog}
                onDisconnect={onDisconnect}
                className="rounded-none rounded-b-xl"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 全屏模式 */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md"
            onClick={() => {
              setIsExpanded(false);
              stopDemo();
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={SPRING.snappy}
              className="w-[800px] h-[600px] rounded-2xl overflow-hidden shadow-2xl border border-neutral-800"
              onClick={(e) => e.stopPropagation()}
            >
              {/* 全屏title栏 */}
              <div className="h-12 flex items-center justify-between px-4 border-b border-neutral-800 bg-neutral-950">
                <div className="flex items-center gap-3">
                  <Activity className="w-5 h-5 text-emerald-500" />
                  <span className="text-sm font-medium text-white">Neural Link</span>
                  <span className="text-xs text-neutral-500">
                    {connectedApps.length} apps connected
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {/* Demo 按钮 */}
                  {hasActiveApps && (
                    <button
                      onClick={isDemoRunning ? stopDemo : runDemo}
                      className={cn(
                        "h-8 px-3 rounded-lg flex items-center gap-2 text-xs transition-colors",
                        isDemoRunning
                          ? "bg-amber-500/20 text-amber-400 hover:bg-amber-500/30"
                          : "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                      )}
                    >
                      {isDemoRunning ? (
                        <>
                          <Square className="w-3.5 h-3.5" />
                          <span>Stop Demo</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-3.5 h-3.5" />
                          <span>Run Demo</span>
                        </>
                      )}
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setIsExpanded(false);
                      stopDemo();
                    }}
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Hook Map */}
              <div className="h-[calc(100%-48px)]">
                <HookMap
                  connectedApps={connectedApps}
                  dataFlow={dataFlow}
                  aiState={aiState}
                  thinkingLog={thinkingLog}
                  onDisconnect={onDisconnect}
                  className="rounded-none h-full"
                />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export default HookMapPanel;
