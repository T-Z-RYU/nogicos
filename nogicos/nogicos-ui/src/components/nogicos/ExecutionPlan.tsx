/**
 * ExecutionPlan - Streaming Plan Display for YC Demo
 *
 * Shows the AI's execution plan with real-time progress:
 * - Steps appear with streaming animation
 * - Current step highlighted
 * - Completed steps show checkmark
 * - Key demo moment: Shows AI's planning capabilities
 */

import { motion, AnimatePresence } from 'motion/react';
import { Check, Loader2, Circle, Brain, Zap, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';

export interface PlanStep {
  text: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
}

export interface ExecutionPlanData {
  steps: string[];
  currentStep: number;
  isGenerating: boolean;
  usedCache?: boolean;
  cacheSimilarity?: number;
  estimatedTime?: number;
}

interface ExecutionPlanProps {
  data: ExecutionPlanData | null;
  visible: boolean;
  className?: string;
}

// Spring configuration for smooth animations
const springs = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 400, damping: 30 },
} as const;

export function ExecutionPlan({
  data,
  visible,
  className
}: ExecutionPlanProps) {
  const [displayedSteps, setDisplayedSteps] = useState<number>(0);

  // Animate steps appearing one by one
  useEffect(() => {
    if (!data || !visible) {
      setDisplayedSteps(0);
      return;
    }

    if (displayedSteps < data.steps.length) {
      const timer = setTimeout(() => {
        setDisplayedSteps(prev => prev + 1);
      }, 150); // 150ms delay between each step
      return () => clearTimeout(timer);
    }
  }, [data, visible, displayedSteps]);

  // Reset when data changes
  useEffect(() => {
    setDisplayedSteps(0);
  }, [data?.steps.length]);

  if (!visible || !data) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.98 }}
        transition={springs.gentle}
        className={cn(
          "bg-[#0d0d12]/95 backdrop-blur-xl",
          "rounded-xl border border-white/[0.08]",
          "shadow-xl shadow-black/30",
          "p-4 mb-4",
          className
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1, ...springs.snappy }}
              className="w-7 h-7 rounded-lg bg-indigo-500/20 flex items-center justify-center"
            >
              <Brain className="w-4 h-4 text-indigo-400" />
            </motion.div>
            <div>
              <h4 className="text-sm font-medium text-white/90">Execution Plan</h4>
              {data.isGenerating && (
                <p className="text-[10px] text-white/40">Generating...</p>
              )}
            </div>
          </div>

          {/* Cache indicator - key demo moment! */}
          {data.usedCache && (
            <motion.div
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20"
            >
              <Zap className="w-3 h-3 text-emerald-400" />
              <span className="text-[10px] text-emerald-400 font-medium">
                Pattern matched! {data.cacheSimilarity ? `${Math.round(data.cacheSimilarity * 100)}%` : ''}
              </span>
            </motion.div>
          )}

          {/* Estimated time */}
          {data.estimatedTime && !data.usedCache && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="flex items-center gap-1 text-[10px] text-white/40"
            >
              <Clock className="w-3 h-3" />
              <span>~{data.estimatedTime}s</span>
            </motion.div>
          )}
        </div>

        {/* Steps */}
        <div className="space-y-2">
          {data.steps.slice(0, displayedSteps).map((step, index) => {
            const isCurrent = index === data.currentStep;
            const isCompleted = index < data.currentStep;
            // isPending calculated inline where needed

            return (
              <motion.div
                key={`step-${index}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={cn(
                  "flex items-center gap-3 py-1.5 px-2 rounded-lg transition-colors",
                  isCurrent && "bg-indigo-500/10",
                  isCompleted && "opacity-60"
                )}
              >
                {/* Status icon */}
                <div className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
                  {isCompleted ? (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={springs.snappy}
                    >
                      <Check className="w-4 h-4 text-emerald-400" />
                    </motion.div>
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                  ) : (
                    <Circle className="w-3 h-3 text-white/20" />
                  )}
                </div>

                {/* Step number */}
                <span className={cn(
                  "text-[10px] font-mono w-4",
                  isCurrent ? "text-indigo-400" : "text-white/30"
                )}>
                  {index + 1}
                </span>

                {/* Step text */}
                <span className={cn(
                  "text-sm flex-1",
                  isCurrent ? "text-white/90" : isCompleted ? "text-white/50 line-through" : "text-white/40"
                )}>
                  {step}
                </span>
              </motion.div>
            );
          })}

          {/* Loading placeholder for remaining steps */}
          {displayedSteps < data.steps.length && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-3 py-1.5 px-2"
            >
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <motion.span
                    key={i}
                    className="w-1 h-1 rounded-full bg-white/20"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15 }}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </div>

        {/* Progress bar */}
        {data.steps.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-3 pt-3 border-t border-white/[0.06]"
          >
            <div className="flex items-center justify-between text-[10px] text-white/40 mb-1.5">
              <span>Progress</span>
              <span>{Math.round((data.currentStep / data.steps.length) * 100)}%</span>
            </div>
            <div className="h-1 bg-white/[0.06] rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-indigo-500 to-indigo-400 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${(data.currentStep / data.steps.length) * 100}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

export default ExecutionPlan;
