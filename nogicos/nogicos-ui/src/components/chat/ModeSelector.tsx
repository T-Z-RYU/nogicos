import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Bot, Search, ListTodo, ChevronDown, Check, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

export type AgentMode = 'agent' | 'ask' | 'plan';

interface ModeSelectorProps {
  mode: AgentMode;
  onModeChange: (mode: AgentMode) => void;
  disabled?: boolean;
  className?: string;
}

interface ModeConfig {
  id: AgentMode;
  name: string;
  description: string;
  icon: typeof Bot;
  shortcut: string;
  color: string;
  bgColor: string;
}

const MODES: ModeConfig[] = [
  {
    id: 'agent',
    name: 'Agent',
    description: 'Execute tasks autonomously',
    icon: Bot,
    shortcut: '1',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10',
  },
  {
    id: 'ask',
    name: 'Ask',
    description: 'Read-only exploration',
    icon: Search,
    shortcut: '2',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
  },
  {
    id: 'plan',
    name: 'Plan',
    description: 'Create editable plan',
    icon: ListTodo,
    shortcut: '3',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10',
  },
];

/**
 * ModeSelector - Cursor-style mode switcher
 * 
 * Three modes:
 * - Agent: Autonomous execution (default)
 * - Ask: Read-only exploration
 * - Plan: Generate editable plan
 * 
 * Shortcuts:
 * - Ctrl/Cmd + . : Toggle dropdown
 * - Ctrl/Cmd + 1/2/3 : Switch to specific mode
 */
export function ModeSelector({
  mode,
  onModeChange,
  disabled = false,
  className,
}: ModeSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const currentMode = MODES.find(m => m.id === mode) || MODES[0];

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + . : Toggle dropdown
      if ((e.ctrlKey || e.metaKey) && e.key === '.') {
        e.preventDefault();
        setIsOpen(prev => !prev);
        return;
      }

      // Ctrl/Cmd + 1/2/3 : Switch mode
      if ((e.ctrlKey || e.metaKey) && ['1', '2', '3'].includes(e.key)) {
        e.preventDefault();
        const modeIndex = parseInt(e.key) - 1;
        if (MODES[modeIndex] && !disabled) {
          onModeChange(MODES[modeIndex].id);
          setIsOpen(false);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onModeChange, disabled]);

  // Close on outside click
  useEffect(() => {
    if (!isOpen) return;
    
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('[data-mode-selector]')) {
        setIsOpen(false);
      }
    };

    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [isOpen]);

  const handleModeSelect = useCallback((modeId: AgentMode) => {
    if (disabled) return;
    onModeChange(modeId);
    setIsOpen(false);
  }, [onModeChange, disabled]);

  const Icon = currentMode.icon;

  return (
    <div 
      className={cn('relative', className)}
      data-mode-selector
    >
      {/* Trigger Button */}
      <motion.button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-lg',
          'bg-white/[0.04] border border-white/[0.08]',
          'hover:bg-white/[0.08] hover:border-white/[0.15]',
          'transition-all duration-200',
          'text-sm font-medium',
          disabled && 'opacity-50 cursor-not-allowed',
          currentMode.color,
        )}
      >
        <Icon className="w-4 h-4" />
        <span>{currentMode.name}</span>
        <ChevronDown 
          className={cn(
            'w-3.5 h-3.5 text-white/40 transition-transform duration-200',
            isOpen && 'rotate-180'
          )} 
        />
      </motion.button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className={cn(
              'absolute top-full left-0 mt-2 z-50',
              'w-64 p-1.5',
              'bg-[#1a1a1a] border border-white/[0.1]',
              'rounded-xl shadow-xl shadow-black/40',
              'backdrop-blur-xl',
            )}
          >
            {/* Header */}
            <div className="px-3 py-2 mb-1">
              <p className="text-[11px] text-white/40 font-medium uppercase tracking-wide">
                Mode
              </p>
            </div>

            {/* Options */}
            {MODES.map((modeOption) => {
              const OptionIcon = modeOption.icon;
              const isSelected = mode === modeOption.id;
              
              return (
                <motion.button
                  key={modeOption.id}
                  onClick={() => handleModeSelect(modeOption.id)}
                  whileHover={{ x: 2 }}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg',
                    'text-left transition-all duration-150',
                    isSelected 
                      ? 'bg-white/[0.08]' 
                      : 'hover:bg-white/[0.04]',
                  )}
                >
                  {/* Icon */}
                  <div className={cn(
                    'w-8 h-8 rounded-lg flex items-center justify-center',
                    modeOption.bgColor,
                  )}>
                    <OptionIcon className={cn('w-4 h-4', modeOption.color)} />
                  </div>

                  {/* Text */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        'text-sm font-medium',
                        isSelected ? 'text-white' : 'text-white/80',
                      )}>
                        {modeOption.name}
                      </span>
                      <kbd className="px-1.5 py-0.5 text-[10px] font-mono text-white/30 bg-white/[0.04] rounded">
                        ⌘{modeOption.shortcut}
                      </kbd>
                    </div>
                    <p className="text-[11px] text-white/40 mt-0.5 truncate">
                      {modeOption.description}
                    </p>
                  </div>

                  {/* Check */}
                  {isSelected && (
                    <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  )}
                </motion.button>
              );
            })}

            {/* Footer hint */}
            <div className="px-3 py-2 mt-1 border-t border-white/[0.06]">
              <p className="text-[10px] text-white/30 flex items-center gap-1.5">
                <Zap className="w-3 h-3" />
                Press <kbd className="px-1 py-0.5 bg-white/[0.04] rounded text-[9px]">⌘ .</kbd> to toggle
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * Compact mode indicator (for chat header)
 */
export function ModeIndicator({ mode }: { mode: AgentMode }) {
  const currentMode = MODES.find(m => m.id === mode) || MODES[0];
  const Icon = currentMode.icon;

  return (
    <div className={cn(
      'flex items-center gap-1.5 px-2 py-1 rounded-md',
      'text-[11px] font-medium',
      currentMode.bgColor,
      currentMode.color,
    )}>
      <Icon className="w-3 h-3" />
      <span>{currentMode.name}</span>
    </div>
  );
}

export default ModeSelector;

