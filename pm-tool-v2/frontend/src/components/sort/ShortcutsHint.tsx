'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Keyboard, ChevronUp, ChevronDown } from 'lucide-react'

const shortcuts = [
  { key: 'Ctrl+A', action: '全选' },
  { key: 'Delete', action: '删除选中' },
  { key: 'Ctrl+Z', action: '撤销' },
  { key: '← →', action: '导航' },
  { key: 'Esc', action: '取消选择' },
  { key: '拖拽', action: '排序/插入' },
]

export function ShortcutsHint() {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '20px',
        left: '260px', // 避开侧边栏
        zIndex: 100,
      }}
    >
      <motion.div
        initial={false}
        animate={{
          height: expanded ? 'auto' : '36px',
        }}
        style={{
          background: '#111111',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '8px',
          overflow: 'hidden',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        }}
      >
        {/* Toggle Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          style={{
            width: '100%',
            padding: '8px 12px',
            background: 'none',
            border: 'none',
            color: '#9ca3af',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '12px',
          }}
        >
          <Keyboard size={14} />
          <span>快捷键</span>
          {expanded ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
        </button>

        {/* Shortcuts List */}
        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{
                padding: '0 12px 12px',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px',
              }}
            >
              {shortcuts.map(({ key, action }) => (
                <div
                  key={key}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontSize: '11px',
                  }}
                >
                  <kbd
                    style={{
                      background: 'rgba(255,255,255,0.06)',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      color: '#fff',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '10px',
                      minWidth: '50px',
                      textAlign: 'center',
                    }}
                  >
                    {key}
                  </kbd>
                  <span style={{ color: '#6b7280' }}>{action}</span>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  )
}
