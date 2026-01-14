/**
 * Hotkey Hints
 * Phase 7.9: Hotkey Support
 */

import { motion, AnimatePresence } from 'motion/react';
import { cn } from '@/lib/utils';

interface Hotkey {
  key: string;
  label: string;
  enabled?: boolean;
}

const DEFAULT_HOTKEYS: Hotkey[] = [
  { key: 'Esc', label: 'Emergency Stop' },
  { key: 'Space', label: 'Pause/Resume' },
  { key: 'Enter', label: 'Confirm Action' },
  { key: 'Tab', label: 'Switch Window' },
];

interface HotkeyHintsProps {
  visible: boolean;
  hotkeys?: Hotkey[];
  position?: 'bottom-left' | 'bottom-right' | 'bottom-center';
  className?: string;
}

export function HotkeyHints({
  visible,
  hotkeys = DEFAULT_HOTKEYS,
  position = 'bottom-right',
  className,
}: HotkeyHintsProps) {
  const positionClasses = {
    'bottom-left': 'left-4 bottom-4',
    'bottom-right': 'right-4 bottom-4',
    'bottom-center': 'left-1/2 bottom-4 -translate-x-1/2',
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className={cn(
            'fixed z-50 flex gap-2 rounded-lg border border-white/10 bg-zinc-900/90 px-3 py-2 backdrop-blur-sm',
            positionClasses[position],
            className
          )}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          {hotkeys.map((hotkey) => (
            <HotkeyItem
              key={hotkey.key}
              hotkey={hotkey}
            />
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Single hotkey item
function HotkeyItem({ hotkey }: { hotkey: Hotkey }) {
  const isDisabled = hotkey.enabled === false;

  return (
    <div
      className={cn(
        'flex items-center gap-1.5 text-xs',
        isDisabled && 'opacity-40'
      )}
    >
      <kbd
        className={cn(
          'inline-flex h-5 min-w-[20px] items-center justify-center rounded border px-1.5 font-mono text-[10px] font-medium',
          isDisabled
            ? 'border-white/5 bg-white/5 text-white/40'
            : 'border-white/20 bg-white/10 text-white/80'
        )}
      >
        {hotkey.key}
      </kbd>
      <span className={isDisabled ? 'text-white/30' : 'text-white/60'}>
        {hotkey.label}
      </span>
    </div>
  );
}

// Inline hotkey display (for dialogs etc)
export function InlineHotkey({ shortcut }: { shortcut: string }) {
  return (
    <kbd className="ml-1 inline-flex h-4 items-center rounded border border-white/10 bg-white/5 px-1 font-mono text-[10px] text-white/50">
      {shortcut}
    </kbd>
  );
}

// Hotkey help overlay
export function HotkeyHelp({ className }: { className?: string }) {
  const allHotkeys = [
    { key: 'Esc', label: 'Emergency stop all tasks', category: 'Control' },
    { key: 'Space', label: 'Pause/resume current task', category: 'Control' },
    { key: 'Enter', label: 'Confirm pending action', category: 'Confirm' },
    { key: 'Tab', label: 'Switch active window', category: 'Navigate' },
    { key: '⌘+K', label: 'Open command palette', category: 'Quick' },
    { key: '⌘+N', label: 'New session', category: 'Quick' },
  ];

  return (
    <div
      className={cn(
        'rounded-lg border border-white/10 bg-zinc-900/95 p-4',
        className
      )}
    >
      <h3 className="mb-3 text-sm font-medium text-white">Keyboard Shortcuts</h3>
      <div className="space-y-3">
        {['Control', 'Confirm', 'Navigate', 'Quick'].map((category) => {
          const items = allHotkeys.filter((h) => h.category === category);
          if (items.length === 0) return null;

          return (
            <div key={category}>
              <p className="mb-1.5 text-xs font-medium text-white/40">
                {category}
              </p>
              <div className="space-y-1">
                {items.map((hotkey) => (
                  <div
                    key={hotkey.key}
                    className="flex items-center justify-between text-xs"
                  >
                    <span className="text-white/60">{hotkey.label}</span>
                    <kbd className="rounded border border-white/10 bg-white/5 px-1.5 py-0.5 font-mono text-[10px] text-white/70">
                      {hotkey.key}
                    </kbd>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
