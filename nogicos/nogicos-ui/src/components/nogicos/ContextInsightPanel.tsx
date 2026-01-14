/**
 * ContextInsightPanel - Level 3 Intelligent Perception Micro-feedback Component
 * 
 * When user connects an app, shows AI's "I noticed..." analysis results
 * Supports single and multi-app combined analysis
 * - Specific file changes
 * - Form field states
 * - Cross-app differences
 * - Smart suggestions
 * - Workflow inference
 */

import { memo, useState, useEffect } from 'react';
import { motion, AnimatePresence, useDragControls } from 'motion/react';
import { 
  X, 
  Sparkles, 
  ChevronRight,
  Loader2,
  AlertCircle,
  Link2,
  Workflow
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface Observation {
  type: string;
  icon: string;
  title: string;
  detail: string;
  before?: string;
  after?: string;
  current_value?: string;
  time_ago?: string;
  highlight?: boolean;
}

interface Suggestion {
  id: string;
  label: string;
  description: string;
}

interface WorkflowInfo {
  name: string;
  steps: string[];
  confidence: number;
}

interface ContextInsight {
  success: boolean;
  app_name?: string;
  app_names?: string[];
  app_count?: number;
  hwnd?: number;
  observations: Observation[];
  suggestions: Suggestion[];
  workflow?: WorkflowInfo;
  error?: string;
}

interface AppInfo {
  hwnd: number;
  appName: string;
  appType: 'desktop' | 'browser' | 'ide';
}

interface ContextInsightPanelProps {
  // New multi-app interface
  apps: AppInfo[];
  onClose?: () => void;
  onSuggestionClick?: (suggestion: Suggestion) => void;
  className?: string;
}

// Export Suggestion type for external use
export type { Suggestion };

// ============================================================================
// Constants
// ============================================================================

const SPRING = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 400, damping: 25 },
};

// ============================================================================
// Sub-components
// ============================================================================

const ObservationItem = memo(function ObservationItem({ 
  observation,
  index 
}: { 
  observation: Observation;
  index: number;
}) {
  const hasDiff = observation.before && observation.after;
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ ...SPRING.gentle, delay: index * 0.1 }}
      className={cn(
        "p-3 rounded-lg",
        observation.highlight 
          ? "bg-emerald-500/10 border border-emerald-500/20" 
          : "bg-white/5 border border-white/5"
      )}
    >
      <div className="flex items-start gap-3">
        <span className="text-lg">{observation.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={cn(
              "text-sm font-medium",
              observation.highlight ? "text-emerald-400" : "text-white/90"
            )}>
              {observation.title}
            </span>
            {observation.time_ago && (
              <span className="text-xs text-white/40">
                {observation.time_ago}
              </span>
            )}
          </div>
          
          <p className="text-xs text-white/50 mt-0.5">
            {observation.detail}
          </p>
          
          {/* Diff display */}
          {hasDiff && (
            <div className="mt-2 space-y-1">
              <div className="flex items-center gap-2 text-xs">
                <span className="text-red-400/70 line-through">
                  "{observation.before}"
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-emerald-400">
                  "{observation.after}"
                </span>
              </div>
            </div>
          )}
          
          {/* Current value display */}
          {observation.current_value && !hasDiff && (
            <div className="mt-1.5 text-xs text-white/40 italic truncate">
              "{observation.current_value}"
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
});

const SuggestionButton = memo(function SuggestionButton({
  suggestion,
  onClick,
  index
}: {
  suggestion: Suggestion;
  onClick: () => void;
  index: number;
}) {
  const handleClick = () => {
        onClick();
  };
  
  return (
    <motion.button
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...SPRING.gentle, delay: 0.3 + index * 0.1 }}
      onClick={handleClick}
      className={cn(
        "w-full flex items-center gap-3 p-3 rounded-lg text-left",
        "bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10",
        "transition-all duration-200 group"
      )}
    >
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-white/90 group-hover:text-white">
          {suggestion.label}
        </div>
        <div className="text-xs text-white/40 mt-0.5">
          {suggestion.description}
        </div>
      </div>
      <ChevronRight className="w-4 h-4 text-white/30 group-hover:text-white/60 transition-colors" />
    </motion.button>
  );
});

const WorkflowCard = memo(function WorkflowCard({
  workflow
}: {
  workflow: WorkflowInfo;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={SPRING.snappy}
      className="p-3 rounded-lg bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/20"
    >
      <div className="flex items-center gap-2 mb-2">
        <Workflow className="w-4 h-4 text-purple-400" />
        <span className="text-sm font-medium text-purple-300">
          Workflow Mode Detected
        </span>
        <span className="text-xs text-white/40 ml-auto">
          {Math.round(workflow.confidence * 100)}% match
        </span>
      </div>
      <div className="text-xs text-white/70 font-medium mb-2">
        {workflow.name}
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        {workflow.steps.map((step, i) => (
          <div key={i} className="flex items-center gap-1">
            <span className="text-xs text-white/50 bg-white/5 px-2 py-0.5 rounded">
              {step}
            </span>
            {i < workflow.steps.length - 1 && (
              <ChevronRight className="w-3 h-3 text-white/30" />
            )}
          </div>
        ))}
      </div>
    </motion.div>
  );
});

// ============================================================================
// Main Component
// ============================================================================

export const ContextInsightPanel = memo(function ContextInsightPanel({
  apps,
  onClose,
  onSuggestionClick,
  className,
}: ContextInsightPanelProps) {
  const [insight, setInsight] = useState<ContextInsight | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Drag controls
  const dragControls = useDragControls();
  
  // Multi-app mode check
  const isMultiApp = apps.length > 1;
  
  // Title display
  const titleText = isMultiApp 
    ? apps.map(a => a.appName).join(' + ')
    : apps[0]?.appName || 'Unknown';

  // Use stable key as dependency to avoid repeated requests from array reference changes
  const appsKey = apps.map(a => a.hwnd).join(',');

  // Fetch context analysis - use stable appsKey as dependency + delay to prevent race conditions
  useEffect(() => {
    if (apps.length === 0) return;
    
    const instanceId = `${Date.now()}-${Math.random().toString(36).slice(2,7)}`;
    const abortController = new AbortController();
    let isMounted = true;
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ContextInsightPanel.tsx:useEffect',message:'Effect started',data:{instanceId,appsKey,appsCount:apps.length},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
    // #endregion
    
    const fetchInsight = async () => {
      // Delay 300ms to wait for component to stabilize, avoiding race conditions during quick switches
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ContextInsightPanel.tsx:afterDelay',message:'After 300ms delay',data:{instanceId,isMounted,aborted:abortController.signal.aborted},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      
      // Check if request was cancelled or component unmounted
      if (abortController.signal.aborted || !isMounted) {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ContextInsightPanel.tsx:earlyExit',message:'Early exit - unmounted or aborted',data:{instanceId,isMounted,aborted:abortController.signal.aborted},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
        return;
      }
      
      setLoading(true);
      setError(null);
      
      try {
        let response: Response;
        const endpoint = apps.length > 1 ? 'analyze-multi' : 'analyze';
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ContextInsightPanel.tsx:beforeFetch',message:'Starting fetch',data:{instanceId,endpoint,appsCount:apps.length,appsKey},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'C'})}).catch(()=>{});
        // #endregion
        
        if (apps.length > 1) {
          // Multi-app: call combined analysis API
          response = await fetch('http://localhost:8080/api/context/analyze-multi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              apps: apps.map(app => ({
                hwnd: app.hwnd,
                app_name: app.appName,
                app_type: app.appType,
              })),
            }),
            signal: abortController.signal,
          });
        } else {
          // Single app: call individual analysis API
          const app = apps[0];
          response = await fetch('http://localhost:8080/api/context/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              hwnd: app.hwnd,
              app_name: app.appName,
              app_type: app.appType,
            }),
            signal: abortController.signal,
          });
        }
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ContextInsightPanel.tsx:afterFetch',message:'Fetch completed',data:{instanceId,status:response.status,ok:response.ok},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'D'})}).catch(()=>{});
        // #endregion
        
        if (!response.ok) {
          throw new Error('Failed to analyze context');
        }
        
        const data = await response.json();
        
        // Check again if component unmounted
        if (!isMounted) return;
        
        console.log('[ContextInsightPanel] Analysis result:', data);
        setInsight(data);
      } catch (err) {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ContextInsightPanel.tsx:catch',message:'Fetch error',data:{instanceId,errorName:err instanceof Error?err.name:'unknown',errorMsg:err instanceof Error?err.message:'unknown',isMounted},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B'})}).catch(()=>{});
        // #endregion
        
        // Ignore cancelled requests
        if (err instanceof Error && err.name === 'AbortError') {
          console.log('[ContextInsightPanel] Request aborted');
          return;
        }
        // Don't set error if component unmounted
        if (!isMounted) return;
        
        console.error('Context analysis failed:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        if (!abortController.signal.aborted && isMounted) {
          setLoading(false);
        }
      }
    };
    
    fetchInsight();
    
    // Cleanup: cancel previous request and mark component as unmounted
    return () => {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/bc94c9ea-7631-4e46-87b6-8d3adb9e38dd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ContextInsightPanel.tsx:cleanup',message:'Cleanup called',data:{instanceId,appsKey},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      isMounted = false;
      abortController.abort();
    };
  }, [appsKey]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: 20 }}
      transition={SPRING.snappy}
      drag
      dragControls={dragControls}
      dragListener={false}
      dragMomentum={false}
      dragElastic={0.1}
      className={cn(
        "w-[420px] rounded-xl overflow-hidden",
        "bg-black/80 backdrop-blur-xl border border-white/10",
        "shadow-2xl shadow-black/50",
        className
      )}
      style={{ willChange: 'transform, opacity' }}
    >
      {/* Header - draggable area */}
      <div 
        className="flex items-center justify-between p-4 border-b border-white/10 cursor-grab active:cursor-grabbing"
        onPointerDown={(e) => dragControls.start(e)}
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <motion.div
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="text-emerald-400 flex-shrink-0"
          >
            {isMultiApp ? (
              <Link2 className="w-4 h-4" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
          </motion.div>
          <div className="min-w-0">
            <span className="text-sm font-medium text-white/90">
              I noticed...
            </span>
            <div className="text-xs text-white/40 truncate">
              {isMultiApp ? `${apps.length} apps` : titleText}
            </div>
          </div>
        </div>
        
        {/* Multi-app tags */}
        {isMultiApp && (
          <div className="flex items-center gap-1 mr-2">
            {apps.slice(0, 3).map((app, i) => (
              <motion.div
                key={app.hwnd}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center text-xs"
                title={app.appName}
              >
                {app.appName.charAt(0)}
              </motion.div>
            ))}
            {apps.length > 3 && (
              <span className="text-xs text-white/40">+{apps.length - 3}</span>
            )}
          </div>
        )}
        
        {onClose && (
          <button
            onClick={(e) => { e.stopPropagation(); onClose(); }}
            className="p-1 rounded-md text-white/40 hover:text-white/70 hover:bg-white/10 transition-colors flex-shrink-0"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
      
      {/* Content */}
      <div className="p-4 max-h-[450px] overflow-y-auto">
        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 text-emerald-400 animate-spin" />
            <span className="ml-2 text-sm text-white/50">
              {isMultiApp ? 'Analyzing multi-app context...' : `Analyzing ${titleText}...`}
            </span>
          </div>
        )}
        
        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span className="text-sm text-red-400">{error}</span>
          </div>
        )}
        
        {!loading && !error && insight && (
          <>
            {/* Workflow Detection - shown in multi-app mode */}
            {insight.workflow && (
              <div className="mb-4">
                <WorkflowCard workflow={insight.workflow} />
              </div>
            )}
            
            {/* Observations */}
            <div className="space-y-2">
              {insight.observations.map((obs, i) => (
                <ObservationItem key={`${obs.type}-${i}`} observation={obs} index={i} />
              ))}
            </div>
            
            {/* Divider */}
            {insight.suggestions.length > 0 && (
              <div className="my-4 border-t border-white/10" />
            )}
            
            {/* Suggestions */}
            {insight.suggestions.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs text-white/40 mb-2">
                  💡 {isMultiApp ? 'Recommended workflow:' : 'You might want:'}
                </div>
                {insight.suggestions.map((sug, i) => (
                  <SuggestionButton
                    key={sug.id}
                    suggestion={sug}
                    onClick={() => onSuggestionClick?.(sug)}
                    index={i}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
      
      {/* Footer hint */}
      <div className="px-4 py-2 border-t border-white/5 bg-white/[0.02]">
        <div className="text-[10px] text-white/30 text-center">
          {isMultiApp 
            ? 'Click suggestion to run cross-app workflow · ESC to close'
            : 'Click suggestion to execute · ESC to close'
          }
        </div>
      </div>
    </motion.div>
  );
});

export default ContextInsightPanel;
