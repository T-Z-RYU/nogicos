'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { ScreenshotCard } from './screenshot-card'
import { useScreenshotStore } from '@/store/screenshot-store'

interface ScreenshotGridProps {
  projectName: string
}

export function ScreenshotGrid({ projectName }: ScreenshotGridProps) {
  const {
    screenshots,
    loading,
    error,
    fetchScreenshots,
    stageFilter,
    moduleFilter,
    setSelectedIndex,
  } = useScreenshotStore()

  // 加载截图
  useEffect(() => {
    fetchScreenshots(projectName)
  }, [fetchScreenshots, projectName, stageFilter, moduleFilter])

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        height: '256px', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        <div className="spinner" />
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        height: '256px', 
        alignItems: 'center', 
        justifyContent: 'center',
        textAlign: 'center',
      }}>
        <p style={{ color: 'var(--danger)' }}>{error}</p>
        <button
          onClick={() => fetchScreenshots(projectName)}
          className="btn-ghost"
          style={{ marginTop: '16px' }}
        >
          重试
        </button>
      </div>
    )
  }

  if (screenshots.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        height: '256px', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: 'var(--text-muted)',
        gap: 'var(--spacing-md)',
      }}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <path d="M21 15l-5-5L5 21" />
        </svg>
        <p style={{ fontSize: '14px' }}>没有找到截图</p>
        {(stageFilter || moduleFilter) && (
          <button
            onClick={() => {
              useScreenshotStore.getState().setStageFilter(null)
              useScreenshotStore.getState().setModuleFilter(null)
            }}
            className="btn-ghost"
            style={{ fontSize: '13px' }}
          >
            清除筛选条件
          </button>
        )}
      </div>
    )
  }

  return (
    <motion.div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
        gap: 'var(--spacing-md)',
      }}
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: 0.02,
          },
        },
      }}
    >
      {screenshots.map((screenshot, index) => (
        <motion.div
          key={screenshot.filename}
          variants={{
            hidden: { opacity: 0, y: 15, scale: 0.98 },
            visible: { opacity: 1, y: 0, scale: 1 },
          }}
          transition={{ 
            duration: 0.25, 
            ease: [0.4, 0, 0.2, 1],
          }}
        >
          <ScreenshotCard
            screenshot={screenshot}
            projectName={projectName}
            onClick={() => setSelectedIndex(index)}
          />
        </motion.div>
      ))}
    </motion.div>
  )
}


