'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, X, Maximize2 } from 'lucide-react'
import { getScreenshotUrl } from '@/lib/api'
import type { Screenshot } from '@/types'

interface PreviewPanelProps {
  screenshot: Screenshot | null
  projectName: string
  currentIndex: number
  total: number
  onClose: () => void
  onPrev: () => void
  onNext: () => void
  onboardingStart: number
  onboardingEnd: number
}

export function PreviewPanel({
  screenshot,
  projectName,
  currentIndex,
  total,
  onClose,
  onPrev,
  onNext,
  onboardingStart,
  onboardingEnd,
}: PreviewPanelProps) {
  const isInOnboarding =
    onboardingStart >= 0 &&
    onboardingEnd >= 0 &&
    currentIndex >= onboardingStart &&
    currentIndex <= onboardingEnd

  const isStart = currentIndex === onboardingStart
  const isEnd = currentIndex === onboardingEnd

  return (
    <div
      style={{
        width: '320px',
        background: '#0a0a0a',
        borderLeft: '1px solid rgba(255,255,255,0.06)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '12px 16px',
          background: '#111111',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>
          预览
        </span>
        {screenshot && (
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#6b7280',
              cursor: 'pointer',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Image */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '8px',
          overflow: 'hidden',
          minHeight: 0, // 关键：允许 flex 子元素收缩
        }}
      >
        <AnimatePresence mode="wait">
          {screenshot ? (
            <motion.div
              key={screenshot.filename}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              style={{
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <img
                src={getScreenshotUrl(projectName, screenshot.filename)}
                alt={screenshot.filename}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain',
                  borderRadius: '12px',
                  boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
                }}
              />
            </motion.div>
          ) : (
            <span style={{ color: '#6b7280', fontSize: '13px' }}>
              点击卡片查看大图
            </span>
          )}
        </AnimatePresence>
      </div>

      {/* Info */}
      {screenshot && (
        <div
          style={{
            padding: '12px 16px',
            background: '#111111',
            borderTop: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          {/* Filename */}
          <div
            style={{
              fontSize: '12px',
              color: '#fff',
              fontWeight: 500,
              marginBottom: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span style={{ fontFamily: 'var(--font-mono)' }}>
              #{currentIndex + 1}
            </span>
            <span style={{ color: '#6b7280' }}>{screenshot.filename}</span>
          </div>

          {/* Onboarding Status */}
          {isInOnboarding && (
            <div
              style={{
                display: 'flex',
                gap: '6px',
                marginBottom: '8px',
              }}
            >
              {isStart && (
                <span
                  style={{
                    padding: '2px 8px',
                    background: '#22c55e',
                    color: '#fff',
                    borderRadius: '4px',
                    fontSize: '10px',
                    fontWeight: 600,
                  }}
                >
                  START
                </span>
              )}
              {isEnd && (
                <span
                  style={{
                    padding: '2px 8px',
                    background: '#f59e0b',
                    color: '#fff',
                    borderRadius: '4px',
                    fontSize: '10px',
                    fontWeight: 600,
                  }}
                >
                  END
                </span>
              )}
              {!isStart && !isEnd && (
                <span
                  style={{
                    padding: '2px 8px',
                    background: 'rgba(34, 197, 94, 0.2)',
                    color: '#22c55e',
                    borderRadius: '4px',
                    fontSize: '10px',
                    fontWeight: 500,
                  }}
                >
                  Onboarding
                </span>
              )}
            </div>
          )}

          {/* Navigation */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginTop: '8px',
            }}
          >
            <button
              onClick={onPrev}
              disabled={currentIndex === 0}
              style={{
                background: 'rgba(255,255,255,0.06)',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 12px',
                color: currentIndex === 0 ? '#4b5563' : '#fff',
                cursor: currentIndex === 0 ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '12px',
              }}
            >
              <ChevronLeft size={14} />
              上一张
            </button>

            <span style={{ color: '#6b7280', fontSize: '12px' }}>
              {currentIndex + 1} / {total}
            </span>

            <button
              onClick={onNext}
              disabled={currentIndex === total - 1}
              style={{
                background: 'rgba(255,255,255,0.06)',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 12px',
                color: currentIndex === total - 1 ? '#4b5563' : '#fff',
                cursor: currentIndex === total - 1 ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '12px',
              }}
            >
              下一张
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
