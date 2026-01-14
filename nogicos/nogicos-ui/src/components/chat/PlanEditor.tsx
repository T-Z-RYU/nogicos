import { useState, useCallback } from 'react';
import { motion, AnimatePresence, Reorder } from 'motion/react';
import { 
  GripVertical, 
  Trash2, 
  Plus, 
  Check, 
  X, 
  AlertTriangle,
  Clock,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Pencil,
  Play,
  FileText,
  Code,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

// Types matching backend EditablePlan
export interface PlanStep {
  step: number;
  description: string;
  tool?: string;
  details?: string;
  file_paths?: string[];
  code_references?: string[];
  editable?: boolean;
}

export interface EditablePlan {
  summary: string;
  steps: PlanStep[];
  clarifying_questions?: string[];
  risks?: string[];
  estimated_time?: string;
  complexity?: 'simple' | 'moderate' | 'complex';
  confirmed?: boolean;
}

interface PlanEditorProps {
  plan: EditablePlan;
  onEdit: (plan: EditablePlan) => void;
  onConfirm: () => void;
  onCancel: () => void;
  isExecuting?: boolean;
  className?: string;
}

/**
 * PlanEditor - Cursor-style plan editor for Plan mode
 * 
 * Features:
 * - View and edit plan summary
 * - Reorder steps via drag & drop
 * - Edit/delete/add steps
 * - Answer clarifying questions
 * - View risks and estimated time
 * - Confirm to execute or cancel
 */
export function PlanEditor({
  plan,
  onEdit,
  onConfirm,
  onCancel,
  isExecuting = false,
  className,
}: PlanEditorProps) {
  const [expandedStep, setExpandedStep] = useState<number | null>(null);
  const [editingStep, setEditingStep] = useState<number | null>(null);
  const [showQuestions, setShowQuestions] = useState(true);
  const [showRisks, setShowRisks] = useState(false);

  // Handle step reorder
  const handleReorder = useCallback((newSteps: PlanStep[]) => {
    // Update step numbers
    const renumbered = newSteps.map((step, i) => ({
      ...step,
      step: i + 1,
    }));
    onEdit({ ...plan, steps: renumbered });
  }, [plan, onEdit]);

  // Handle step edit
  const handleStepEdit = useCallback((index: number, updates: Partial<PlanStep>) => {
    const newSteps = [...plan.steps];
    newSteps[index] = { ...newSteps[index], ...updates };
    onEdit({ ...plan, steps: newSteps });
  }, [plan, onEdit]);

  // Handle step delete
  const handleStepDelete = useCallback((index: number) => {
    const newSteps = plan.steps.filter((_, i) => i !== index);
    // Renumber
    const renumbered = newSteps.map((step, i) => ({ ...step, step: i + 1 }));
    onEdit({ ...plan, steps: renumbered });
  }, [plan, onEdit]);

  // Handle add step
  const handleAddStep = useCallback(() => {
    const newStep: PlanStep = {
      step: plan.steps.length + 1,
      description: 'New step',
      editable: true,
    };
    onEdit({ ...plan, steps: [...plan.steps, newStep] });
    setEditingStep(plan.steps.length);
  }, [plan, onEdit]);

  // Complexity badge color
  const complexityColor = {
    simple: 'bg-emerald-500/10 text-emerald-400',
    moderate: 'bg-amber-500/10 text-amber-400',
    complex: 'bg-red-500/10 text-red-400',
  }[plan.complexity || 'moderate'];

  return (
    <div className={cn('rounded-xl bg-[#111] border border-white/[0.08]', className)}>
      {/* Header */}
      <div className="px-5 py-4 border-b border-white/[0.06]">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-lg font-semibold text-white">Execution Plan</h3>
              {plan.complexity && (
                <span className={cn(
                  'px-2 py-0.5 rounded text-[11px] font-medium',
                  complexityColor,
                )}>
                  {plan.complexity}
                </span>
              )}
            </div>
            <p className="text-sm text-white/60 leading-relaxed">{plan.summary}</p>
          </div>
          {plan.estimated_time && (
            <div className="flex items-center gap-1.5 text-white/40 text-sm shrink-0">
              <Clock className="w-4 h-4" />
              <span>{plan.estimated_time}</span>
            </div>
          )}
        </div>
      </div>

      {/* Clarifying Questions */}
      {plan.clarifying_questions && plan.clarifying_questions.length > 0 && (
        <div className="px-5 py-3 border-b border-white/[0.06] bg-amber-500/[0.03]">
          <button
            onClick={() => setShowQuestions(!showQuestions)}
            className="flex items-center gap-2 w-full text-left"
          >
            <HelpCircle className="w-4 h-4 text-amber-400" />
            <span className="text-sm font-medium text-amber-400">
              {plan.clarifying_questions.length} clarifying question(s)
            </span>
            {showQuestions ? (
              <ChevronUp className="w-4 h-4 text-amber-400 ml-auto" />
            ) : (
              <ChevronDown className="w-4 h-4 text-amber-400 ml-auto" />
            )}
          </button>
          <AnimatePresence>
            {showQuestions && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <ul className="mt-3 space-y-2">
                  {plan.clarifying_questions.map((q, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                      <span className="text-amber-400 font-medium shrink-0">{i + 1}.</span>
                      <span>{q}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Steps */}
      <div className="px-5 py-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-white/60">
            Steps ({plan.steps.length})
          </h4>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleAddStep}
            className="h-7 px-2 text-[11px] text-white/50 hover:text-white"
          >
            <Plus className="w-3.5 h-3.5 mr-1" />
            Add Step
          </Button>
        </div>

        <Reorder.Group
          axis="y"
          values={plan.steps}
          onReorder={handleReorder}
          className="space-y-2"
        >
          {plan.steps.map((step, index) => (
            <Reorder.Item
              key={step.step}
              value={step}
              className="list-none"
            >
              <StepCard
                step={step}
                index={index}
                isExpanded={expandedStep === index}
                isEditing={editingStep === index}
                onToggleExpand={() => setExpandedStep(expandedStep === index ? null : index)}
                onStartEdit={() => setEditingStep(index)}
                onEndEdit={() => setEditingStep(null)}
                onEdit={(updates) => handleStepEdit(index, updates)}
                onDelete={() => handleStepDelete(index)}
              />
            </Reorder.Item>
          ))}
        </Reorder.Group>
      </div>

      {/* Risks */}
      {plan.risks && plan.risks.length > 0 && (
        <div className="px-5 py-3 border-t border-white/[0.06]">
          <button
            onClick={() => setShowRisks(!showRisks)}
            className="flex items-center gap-2 w-full text-left"
          >
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span className="text-sm font-medium text-red-400">
              {plan.risks.length} risk(s)
            </span>
            {showRisks ? (
              <ChevronUp className="w-4 h-4 text-red-400 ml-auto" />
            ) : (
              <ChevronDown className="w-4 h-4 text-red-400 ml-auto" />
            )}
          </button>
          <AnimatePresence>
            {showRisks && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <ul className="mt-3 space-y-2">
                  {plan.risks.map((risk, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                      <span className="text-red-400">•</span>
                      <span>{risk}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Actions */}
      <div className="px-5 py-4 border-t border-white/[0.06] bg-white/[0.02] flex items-center justify-end gap-3">
        <Button
          variant="ghost"
          onClick={onCancel}
          disabled={isExecuting}
          className="text-white/60 hover:text-white"
        >
          <X className="w-4 h-4 mr-2" />
          Cancel
        </Button>
        <Button
          onClick={onConfirm}
          disabled={isExecuting || plan.steps.length === 0}
          className={cn(
            'bg-emerald-500 hover:bg-emerald-600 text-white',
            'shadow-lg shadow-emerald-500/20',
          )}
        >
          {isExecuting ? (
            <>
              <motion.div
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full mr-2"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              />
              Executing...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Execute Plan
            </>
          )}
        </Button>
      </div>
    </div>
  );
}

/**
 * Individual step card component
 */
interface StepCardProps {
  step: PlanStep;
  index: number;
  isExpanded: boolean;
  isEditing: boolean;
  onToggleExpand: () => void;
  onStartEdit: () => void;
  onEndEdit: () => void;
  onEdit: (updates: Partial<PlanStep>) => void;
  onDelete: () => void;
}

function StepCard({
  step,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  index: _index,
  isExpanded,
  isEditing,
  onToggleExpand,
  onStartEdit,
  onEndEdit,
  onEdit,
  onDelete,
}: StepCardProps) {
  const [editedDescription, setEditedDescription] = useState(step.description);

  const handleSave = () => {
    onEdit({ description: editedDescription });
    onEndEdit();
  };

  const handleCancel = () => {
    setEditedDescription(step.description);
    onEndEdit();
  };

  return (
    <motion.div
      layout
      className={cn(
        'rounded-lg border transition-colors duration-150',
        isExpanded 
          ? 'bg-white/[0.04] border-white/[0.1]' 
          : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.1]',
      )}
    >
      {/* Main Row */}
      <div className="flex items-center gap-3 px-3 py-2.5">
        {/* Drag Handle */}
        <div className="cursor-grab active:cursor-grabbing text-white/20 hover:text-white/40">
          <GripVertical className="w-4 h-4" />
        </div>

        {/* Step Number */}
        <div className="w-6 h-6 rounded-full bg-white/[0.06] flex items-center justify-center text-[11px] font-medium text-white/50 shrink-0">
          {step.step}
        </div>

        {/* Description */}
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <input
              type="text"
              value={editedDescription}
              onChange={(e) => setEditedDescription(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSave();
                if (e.key === 'Escape') handleCancel();
              }}
              autoFocus
              className="w-full bg-transparent text-sm text-white outline-none border-b border-violet-500"
            />
          ) : (
            <p className="text-sm text-white/80 truncate">{step.description}</p>
          )}
        </div>

        {/* Tool Badge */}
        {step.tool && (
          <span className="px-2 py-0.5 rounded bg-violet-500/10 text-violet-400 text-[10px] font-mono shrink-0">
            {step.tool}
          </span>
        )}

        {/* Actions */}
        <div className="flex items-center gap-1 shrink-0">
          {isEditing ? (
            <>
              <button
                onClick={handleSave}
                className="p-1.5 rounded hover:bg-emerald-500/10 text-emerald-400"
              >
                <Check className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={handleCancel}
                className="p-1.5 rounded hover:bg-red-500/10 text-red-400"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </>
          ) : (
            <>
              {(step.details || step.file_paths?.length || step.code_references?.length) && (
                <button
                  onClick={onToggleExpand}
                  className="p-1.5 rounded hover:bg-white/[0.06] text-white/40"
                >
                  {isExpanded ? (
                    <ChevronUp className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5" />
                  )}
                </button>
              )}
              <button
                onClick={onStartEdit}
                className="p-1.5 rounded hover:bg-white/[0.06] text-white/40 hover:text-white/60"
              >
                <Pencil className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={onDelete}
                className="p-1.5 rounded hover:bg-red-500/10 text-white/40 hover:text-red-400"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Expanded Details */}
      <AnimatePresence>
        {isExpanded && !isEditing && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 pt-1 ml-[52px] space-y-2">
              {step.details && (
                <p className="text-[12px] text-white/50 leading-relaxed">
                  {step.details}
                </p>
              )}
              {step.file_paths && step.file_paths.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap">
                  <FileText className="w-3 h-3 text-white/30" />
                  {step.file_paths.map((path, i) => (
                    <code 
                      key={i} 
                      className="text-[10px] px-1.5 py-0.5 rounded bg-white/[0.04] text-white/60"
                    >
                      {path}
                    </code>
                  ))}
                </div>
              )}
              {step.code_references && step.code_references.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap">
                  <Code className="w-3 h-3 text-white/30" />
                  {step.code_references.map((ref, i) => (
                    <code 
                      key={i} 
                      className="text-[10px] px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-400"
                    >
                      {ref}
                    </code>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default PlanEditor;

