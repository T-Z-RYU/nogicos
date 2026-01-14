/**
 * NogicOS Confirmation Dialog
 * 
 * Used for YC Workflow to show the answer and get user confirmation
 * before filling the form.
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Check, X, FileText, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ConfirmDialogData {
  title: string;
  question: string;
  answer: string;
  execution_count: number;
  source_file?: string;
}

interface ConfirmDialogProps {
  isOpen: boolean;
  data: ConfirmDialogData | null;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({ isOpen, data, onConfirm, onCancel }: ConfirmDialogProps) {
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    if (isOpen) {
      // Slight delay for animation
      setTimeout(() => setIsVisible(true), 50);
    } else {
      setIsVisible(false);
    }
  }, [isOpen]);

  const handleConfirm = useCallback(() => {
    setIsVisible(false);
    setTimeout(onConfirm, 200);
  }, [onConfirm]);

  const handleCancel = useCallback(() => {
    setIsVisible(false);
    setTimeout(onCancel, 200);
  }, [onCancel]);

  // Handle keyboard shortcuts
  useEffect(() => {
    if (!isOpen) return;
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        handleConfirm();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        handleCancel();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, handleConfirm, handleCancel]);

  if (!data) return null;

  const isFirstRun = data.execution_count === 1;
  const versionLabel = isFirstRun ? '1st Draft' : `Revision ${data.execution_count}`;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="confirm-dialog-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: isVisible ? 1 : 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={handleCancel}
          />
          
          {/* Dialog */}
          <motion.div
            className="confirm-dialog"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ 
              opacity: isVisible ? 1 : 0, 
              scale: isVisible ? 1 : 0.95,
              y: isVisible ? 0 : 20
            }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ 
              duration: 0.25, 
              ease: [0.32, 0.72, 0, 1]
            }}
          >
            {/* Header */}
            <div className="confirm-dialog-header">
              <div className="confirm-dialog-title">
                <FileText className="w-5 h-5 text-emerald-400" />
                <span>{data.title}</span>
              </div>
              <span className={cn(
                "confirm-dialog-badge",
                isFirstRun ? "badge-draft" : "badge-revision"
              )}>
                {versionLabel}
              </span>
            </div>
            
            {/* Content */}
            <div className="confirm-dialog-content">
              {/* Source indication */}
              {data.source_file && (
                <div className="confirm-dialog-source">
                  <span className="text-neutral-500">Source:</span>
                  <span className="text-neutral-300">{data.source_file}</span>
                </div>
              )}
              
              {/* Question */}
              <div className="confirm-dialog-question">
                <span className="text-neutral-400 text-sm">YC Question:</span>
                <p className="text-white font-medium">{data.question}</p>
              </div>
              
              {/* Answer Preview */}
              <div className="confirm-dialog-answer">
                <span className="text-neutral-400 text-sm">Answer to fill:</span>
                <div className="confirm-dialog-answer-box">
                  <p>{data.answer}</p>
                </div>
              </div>
              
              {/* Warning */}
              <div className="confirm-dialog-warning">
                <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                <span>This will type the answer into the active Chrome form field.</span>
              </div>
            </div>
            
            {/* Actions */}
            <div className="confirm-dialog-actions">
              <motion.button
                className="confirm-dialog-btn btn-cancel"
                onClick={handleCancel}
                whileHover={{ backgroundColor: 'rgba(255,255,255,0.08)' }}
                whileTap={{ scale: 0.98 }}
              >
                <X className="w-4 h-4" />
                <span>Cancel</span>
                <kbd>Esc</kbd>
              </motion.button>
              
              <motion.button
                className="confirm-dialog-btn btn-confirm"
                onClick={handleConfirm}
                whileHover={{ backgroundColor: 'rgba(16, 185, 129, 0.2)' }}
                whileTap={{ scale: 0.98 }}
              >
                <Check className="w-4 h-4" />
                <span>Confirm & Fill</span>
                <kbd>⌘↵</kbd>
              </motion.button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// Hook for managing confirm dialog state
export function useConfirmDialog() {
  const [isOpen, setIsOpen] = useState(false);
  const [data, setData] = useState<ConfirmDialogData | null>(null);
  const [resolveRef, setResolveRef] = useState<((value: boolean) => void) | null>(null);

  const showConfirm = useCallback((dialogData: ConfirmDialogData): Promise<boolean> => {
    return new Promise((resolve) => {
      setData(dialogData);
      setResolveRef(() => resolve);
      setIsOpen(true);
    });
  }, []);

  const handleConfirm = useCallback(() => {
    setIsOpen(false);
    resolveRef?.(true);
    setResolveRef(null);
  }, [resolveRef]);

  const handleCancel = useCallback(() => {
    setIsOpen(false);
    resolveRef?.(false);
    setResolveRef(null);
  }, [resolveRef]);

  return {
    isOpen,
    data,
    showConfirm,
    handleConfirm,
    handleCancel,
  };
}

export default ConfirmDialog;
