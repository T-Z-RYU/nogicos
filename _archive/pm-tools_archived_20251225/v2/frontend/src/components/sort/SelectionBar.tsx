'use client'

import { motion } from 'framer-motion'
import { CheckSquare, X, Trash2 } from 'lucide-react'
import type { SelectionBarProps } from '@/types/sort'

// 内联样式定义（替代 style jsx 解决 scoped CSS 问题）
const styles = {
  bar: {
    position: 'fixed' as const,
    bottom: '24px',
    left: '50%',
    transform: 'translateX(-50%)',
    background: 'rgba(30, 30, 30, 0.95)',
    backdropFilter: 'blur(12px)',
    borderRadius: '12px',
    padding: '12px 20px',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255,255,255,0.1)',
    zIndex: 1000,
  },
  info: {
    color: '#fff',
    fontSize: '14px',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  icon: {
    color: '#3b82f6',
  },
  divider: {
    width: '1px',
    height: '24px',
    background: 'rgba(255,255,255,0.2)',
  },
  btn: {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '13px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    transition: 'background 150ms, opacity 150ms',
  },
  btnSecondary: {
    background: 'rgba(255,255,255,0.1)',
    color: '#fff',
  },
  btnDanger: {
    background: '#ef4444',
    color: '#fff',
  },
}

export function SelectionBar({
  selectedCount,
  onDeselect,
  onDelete,
  disabled = false,
}: SelectionBarProps) {
  if (selectedCount === 0) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      transition={{ duration: 0.2, ease: [0.25, 1, 0.5, 1] }}
      style={styles.bar}
    >
      <span style={styles.info}>
        <CheckSquare size={18} style={styles.icon} />
        已选择 {selectedCount} 张截图
      </span>
      
      <div style={styles.divider} />
      
      <button
        onClick={onDeselect}
        style={{ ...styles.btn, ...styles.btnSecondary }}
      >
        <X size={14} />
        取消选择
      </button>
      
      <button
        onClick={onDelete}
        disabled={disabled}
        style={{ 
          ...styles.btn, 
          ...styles.btnDanger,
          opacity: disabled ? 0.6 : 1,
          cursor: disabled ? 'not-allowed' : 'pointer',
        }}
      >
        <Trash2 size={14} />
        删除选中
      </button>
    </motion.div>
  )
}
