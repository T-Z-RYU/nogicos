'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { getThumbnailUrl } from '@/lib/api'
import { ImageOff } from 'lucide-react'
import type { Screenshot } from '@/types'

interface ScreenshotCardProps {
  screenshot: Screenshot
  projectName: string
  onClick: () => void
}

export function ScreenshotCard({ screenshot, projectName, onClick }: ScreenshotCardProps) {
  const thumbUrl = getThumbnailUrl(projectName, screenshot.filename, 'medium')
  const classification = screenshot.classification
  const [imageError, setImageError] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)

  return (
    <motion.div
      className="screenshot-card group"
      style={{ cursor: 'pointer' }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      onClick={onClick}
    >
      {/* 缩略图 */}
      <div style={{ 
        position: 'relative',
        aspectRatio: '9/16',
        overflow: 'hidden',
        background: 'var(--bg-secondary)',
      }}>
        {/* 加载占位 */}
        {!imageLoaded && !imageError && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--bg-secondary)',
          }}>
            <div className="spinner" style={{ width: '24px', height: '24px' }} />
          </div>
        )}
        
        {/* 加载失败 */}
        {imageError && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--bg-secondary)',
            color: 'var(--text-muted)',
            gap: '8px',
          }}>
            <ImageOff size={24} />
            <span style={{ fontSize: '11px' }}>加载失败</span>
          </div>
        )}
        
        {/* 图片 */}
        {!imageError && (
          <motion.img
            src={thumbUrl}
            alt={screenshot.filename}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: imageLoaded ? 1 : 0,
              transition: 'opacity 0.2s ease',
            }}
            loading="lazy"
            initial={{ scale: 1 }}
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageError(true)}
          />
        )}

        {/* 索引标签 - 左上角 */}
        <div style={{
          position: 'absolute',
          top: '8px',
          left: '8px',
          padding: '2px 6px',
          background: 'rgba(0, 0, 0, 0.6)',
          borderRadius: '4px',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-secondary)',
        }}>
          #{screenshot.index}
        </div>

        {/* 悬停遮罩 */}
        <motion.div 
          style={{
            position: 'absolute',
            inset: 0,
            background: 'rgba(0, 0, 0, 0)',
            pointerEvents: 'none',
          }}
          whileHover={{ background: 'rgba(0, 0, 0, 0.15)' }}
          transition={{ duration: 0.2 }}
        />
      </div>

      {/* 信息区 */}
      <div style={{ 
        padding: 'var(--spacing-sm)',
        borderTop: '1px solid var(--border-subtle)',
      }}>
        {/* 分类标签 */}
        {classification && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {classification.stage && (
              <span className="badge" style={{
                background: 'rgba(255, 255, 255, 0.08)',
                color: 'var(--text-secondary)',
                fontSize: '10px',
              }}>
                {classification.stage}
              </span>
            )}
            {classification.module && (
              <span className="badge" style={{
                background: 'rgba(255, 255, 255, 0.04)',
                color: 'var(--text-muted)',
                fontSize: '10px',
              }}>
                {classification.module}
              </span>
            )}
          </div>
        )}
        {!classification && (
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            未分类
          </span>
        )}
      </div>
    </motion.div>
  )
}


