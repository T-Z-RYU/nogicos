/**
 * ExecutionStats - Task Execution Statistics Panel
 *
 * Displays completion statistics after task execution:
 * - Total execution time
 * - Number of actions/tools used
 * - Apps/windows involved
 * - Patterns learned/cached
 * - Estimated future speedup
 *
 * Key Demo moment: Shows NogicOS's learning capabilities
 */

import { motion, AnimatePresence } from 'motion/react';
import { Check, Clock, Zap, Brain, Sparkles, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface ExecutionStatsData {
  /** Task completed successfully */
  success: boolean;
  /** Total execution time in seconds */
  totalTime: number;
  /** Time to first response in milliseconds */
  ttft?: number;
  /** Number of iterations/tool calls */
  iterations: number;
  /** Number of tools used */
  toolsUsed: number;
  /** Apps/windows involved */
  apps?: string[];
  /** Was a cached plan used? */
  usedCachedPlan?: boolean;
  /** Similarity score if cached plan was used */
  cacheSimilarity?: number;
  /** New patterns learned and cached */
  patternsLearned?: number;
  /** Estimated speedup for similar future tasks */
  estimatedSpeedup?: number;
}

interface ExecutionStatsProps {
  data: ExecutionStatsData;
  visible: boolean;
  onDismiss?: () => void;
  className?: string;
}

// Spring configuration for smooth animations
const springs = {
  gentle: { type: 'spring' as const, stiffness: 120, damping: 14 },
  snappy: { type: 'spring' as const, stiffness: 400, damping: 30 },
} as const;

export function ExecutionStats({
  data,
  visible,
  onDismiss,
  className
}: ExecutionStatsProps) {
  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs.toFixed(0)}s`;
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={springs.gentle}
          className={cn(
            "fixed bottom-6 right-6 z-50",
            "bg-[#1a1a2e]/95 backdrop-blur-xl",
            "rounded-2xl border border-white/10",
            "shadow-2xl shadow-black/40",
            "p-6 w-[340px]",
            className
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, ...springs.snappy }}
                className={cn(
                  "w-10 h-10 rounded-xl flex items-center justify-center",
                  data.success
                    ? "bg-emerald-500/20 text-emerald-400"
                    : "bg-red-500/20 text-red-400"
                )}
              >
                {data.success ? <Check className="w-5 h-5" /> : <X className="w-5 h-5" />}
              </motion.div>
              <div>
                <h3 className="text-white font-semibold">
                  {data.success ? 'Task Completed' : 'Task Failed'}
                </h3>
                <p className="text-white/50 text-xs">Execution Summary</p>
              </div>
            </div>

            {onDismiss && (
              <button
                onClick={onDismiss}
                className="text-white/40 hover:text-white/80 transition-colors p-1"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Performance Stats */}
          <div className="space-y-3">
            <StatRow
              icon={<Clock className="w-4 h-4" />}
              label="Total time"
              value={formatTime(data.totalTime)}
              delay={0.1}
            />

            <StatRow
              icon={<Zap className="w-4 h-4 text-yellow-400" />}
              label="Actions"
              value={`${data.toolsUsed} tools, ${data.iterations} iterations`}
              delay={0.15}
            />

            {data.apps && data.apps.length > 0 && (
              <StatRow
                icon={<Sparkles className="w-4 h-4 text-purple-400" />}
                label="Apps"
                value={data.apps.join(', ')}
                delay={0.2}
              />
            )}
          </div>

          {/* Learning Section - Key Demo Moment! */}
          {(data.patternsLearned ?? 0) > 0 || data.usedCachedPlan && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ delay: 0.3 }}
              className="mt-4 pt-4 border-t border-white/10"
            >
              <div className="flex items-center gap-2 mb-3">
                <Brain className="w-4 h-4 text-cyan-400" />
                <span className="text-white/80 text-sm font-medium">Learning</span>
              </div>

              {data.usedCachedPlan && (
                <motion.div
                  initial={{ x: -10, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.35 }}
                  className="flex items-center gap-2 text-sm mb-2"
                >
                  <span className="text-emerald-400">Pattern recognized</span>
                  <span className="text-white/40">
                    ({((data.cacheSimilarity ?? 0) * 100).toFixed(0)}% match)
                  </span>
                </motion.div>
              )}

              {(data.patternsLearned ?? 0) > 0 && (
                <motion.div
                  initial={{ x: -10, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  className="flex items-center gap-2 text-sm mb-2"
                >
                  <span className="text-cyan-400">
                    {data.patternsLearned} new pattern{(data.patternsLearned ?? 0) > 1 ? 's' : ''} learned
                  </span>
                </motion.div>
              )}

              {data.estimatedSpeedup && data.estimatedSpeedup > 1 && (
                <motion.div
                  initial={{ x: -10, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.45 }}
                  className="flex items-center gap-2 text-sm"
                >
                  <span className="text-white/60">Future speedup:</span>
                  <span className="text-yellow-400 font-semibold">
                    ~{data.estimatedSpeedup.toFixed(1)}x faster
                  </span>
                </motion.div>
              )}
            </motion.div>
          )}

          {/* AI Quote - for emotional impact */}
          {data.success && (data.patternsLearned ?? 0) > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="mt-4 pt-3 border-t border-white/5"
            >
              <p className="text-white/40 text-xs italic">
                "I learned {data.patternsLearned} new pattern{(data.patternsLearned ?? 0) > 1 ? 's' : ''} that
                will help me do similar tasks faster next time."
              </p>
            </motion.div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Individual stat row component
function StatRow({
  icon,
  label,
  value,
  delay = 0
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ x: -10, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ delay }}
      className="flex items-center justify-between text-sm"
    >
      <div className="flex items-center gap-2 text-white/60">
        {icon}
        <span>{label}</span>
      </div>
      <span className="text-white font-medium">{value}</span>
    </motion.div>
  );
}

export default ExecutionStats;
