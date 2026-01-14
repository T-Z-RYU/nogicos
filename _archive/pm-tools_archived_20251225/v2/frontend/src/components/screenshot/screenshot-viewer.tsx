'use client'

import { useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useScreenshotStore } from '@/store/screenshot-store'
import { getScreenshotUrl } from '@/lib/api'
import { ChevronLeft, ChevronRight, X } from 'lucide-react'

interface ScreenshotViewerProps {
  projectName: string
}

export function ScreenshotViewer({ projectName }: ScreenshotViewerProps) {
  const {
    screenshots,
    selectedIndex,
    setSelectedIndex,
    nextScreenshot,
    prevScreenshot,
  } = useScreenshotStore()

  const isOpen = selectedIndex !== null
  const screenshot = selectedIndex !== null ? screenshots[selectedIndex] : null

  // 键盘导航
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isOpen) return
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        nextScreenshot()
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        prevScreenshot()
      } else if (e.key === 'Escape') {
        setSelectedIndex(null)
      }
    },
    [isOpen, nextScreenshot, prevScreenshot, setSelectedIndex]
  )

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  if (!screenshot) return null

  const imageUrl = getScreenshotUrl(projectName, screenshot.filename)
  const classification = screenshot.classification

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          data-testid="screenshot-viewer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.9)',
            zIndex: 1000,
            display: 'flex',
            flexDirection: 'column',
          }}
          onClick={() => setSelectedIndex(null)}
        >
          {/* Header - 复刻老版模态框头部 */}
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.2 }}
            style={{
              background: 'var(--bg-secondary)',
              borderBottom: '1px solid var(--border-default)',
              padding: 'var(--spacing-lg) 20px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ 
                fontSize: '14px', 
                fontWeight: 500,
                fontFamily: 'var(--font-mono)',
              }}>
                #{screenshot.index} / {screenshots.length}
              </span>
              {classification && (
                <div style={{ display: 'flex', gap: '6px' }}>
                  {classification.stage && (
                    <span className="badge" style={{
                      background: 'rgba(255, 255, 255, 0.1)',
                      color: '#fff',
                    }}>
                      {classification.stage}
                    </span>
                  )}
                  {classification.module && (
                    <span className="badge" style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      color: 'var(--text-secondary)',
                    }}>
                      {classification.module}
                    </span>
                  )}
                </div>
              )}
            </div>
            <button
              onClick={() => setSelectedIndex(null)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '8px',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                transition: 'var(--transition-fast)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#fff'
                e.currentTarget.style.background = 'var(--bg-hover)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'var(--text-muted)'
                e.currentTarget.style.background = 'none'
              }}
            >
              <X size={20} />
            </button>
          </motion.div>

          {/* Image */}
          <div 
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 'var(--spacing-xl)',
              position: 'relative',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <AnimatePresence mode="wait">
              <motion.img
                key={screenshot.filename}
                src={imageUrl}
                alt={screenshot.filename}
                style={{
                  maxHeight: '100%',
                  maxWidth: '100%',
                  objectFit: 'contain',
                  borderRadius: 'var(--radius-lg)',
                }}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
              />
            </AnimatePresence>

            {/* Navigation - 左右按钮 */}
            <motion.button
              style={{
                position: 'absolute',
                left: '20px',
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.1)',
                border: 'none',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: selectedIndex === 0 ? 0.3 : 1,
              }}
              whileHover={{ background: 'rgba(255, 255, 255, 0.2)' }}
              whileTap={{ scale: 0.95 }}
              disabled={selectedIndex === 0}
              onClick={(e) => {
                e.stopPropagation()
                prevScreenshot()
              }}
            >
              <ChevronLeft size={24} />
            </motion.button>
            
            <motion.button
              style={{
                position: 'absolute',
                right: '20px',
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.1)',
                border: 'none',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: selectedIndex === screenshots.length - 1 ? 0.3 : 1,
              }}
              whileHover={{ background: 'rgba(255, 255, 255, 0.2)' }}
              whileTap={{ scale: 0.95 }}
              disabled={selectedIndex === screenshots.length - 1}
              onClick={(e) => {
                e.stopPropagation()
                nextScreenshot()
              }}
            >
              <ChevronRight size={24} />
            </motion.button>
          </div>

          {/* Footer */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.2 }}
            style={{
              background: 'var(--bg-secondary)',
              borderTop: '1px solid var(--border-default)',
              padding: 'var(--spacing-md) 20px',
              fontSize: '12px',
              color: 'var(--text-muted)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <span style={{ fontFamily: 'var(--font-mono)' }}>
              {screenshot.filename}
            </span>
            {screenshot.description && (
              <span style={{ marginLeft: '12px', color: 'var(--text-secondary)' }}>
                {screenshot.description}
              </span>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}


