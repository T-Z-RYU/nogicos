/**
 * WorkflowConfirmDialog - Confirmation dialog for preset workflows
 * 
 * Used by YC Application workflow to show answer preview and get user confirmation
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface WorkflowConfirmData {
  type: 'workflow_confirmation';
  workflow: string;
  title: string;
  question: string;
  answer: string;
  execution_count: number;
  skipped_steps?: string[];
  actions: string[];
}

interface WorkflowConfirmDialogProps {
  data: WorkflowConfirmData | null;
  onConfirm: () => void;
  onCancel: () => void;
}

export const WorkflowConfirmDialog: React.FC<WorkflowConfirmDialogProps> = ({
  data,
  onConfirm,
  onCancel,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (data) {
      setIsVisible(true);
    }
  }, [data]);

  const handleConfirm = () => {
    setIsVisible(false);
    setTimeout(onConfirm, 200);
  };

  const handleCancel = () => {
    setIsVisible(false);
    setTimeout(onCancel, 200);
  };

  if (!data) return null;

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            onClick={handleCancel}
          />
          
          {/* Dialog */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-lg"
          >
            <div className="bg-[#1a1a1a] border border-white/10 rounded-xl shadow-2xl overflow-hidden">
              {/* Header */}
              <div className="px-6 py-4 border-b border-white/10 bg-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                    <span className="text-xl">📝</span>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">{data.title}</h2>
                    <p className="text-xs text-white/50">
                      Execute #{data.execution_count}
                      {data.skipped_steps && data.skipped_steps.length > 0 && (
                        <span className="ml-2 text-green-400">
                          ⚡ Skip {data.skipped_steps.length} 步
                        </span>
                      )}
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Content */}
              <div className="px-6 py-5 space-y-4">
                {/* Question */}
                <div>
                  <label className="text-xs font-medium text-white/50 uppercase tracking-wider">
                    问题
                  </label>
                  <p className="mt-1 text-white/80 text-sm">
                    {data.question}
                  </p>
                </div>
                
                {/* Answer Preview */}
                <div>
                  <label className="text-xs font-medium text-white/50 uppercase tracking-wider">
                    将填Write的答案
                  </label>
                  <div className="mt-2 p-4 bg-black/40 border border-white/10 rounded-lg">
                    <p className="text-white text-sm leading-relaxed font-mono">
                      {data.answer}
                    </p>
                  </div>
                </div>
                
                {/* Notice */}
                <p className="text-xs text-white/40 flex items-center gap-2">
                  <span>ℹ️</span>
                  ConfirmAfter将Auto填Write到 YC ApplyTable单并Send WhatsApp Notify
                </p>
              </div>
              
              {/* Actions */}
              <div className="px-6 py-4 border-t border-white/10 bg-white/5 flex justify-end gap-3">
                <button
                  onClick={handleCancel}
                  className="px-4 py-2 text-sm text-white/70 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirm}
                  className="px-5 py-2 bg-white text-black text-sm font-medium rounded-lg hover:bg-white/90 transition-colors"
                >
                  Confirm填Write
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default WorkflowConfirmDialog;
