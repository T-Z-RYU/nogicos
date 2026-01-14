'use client'

import { motion } from 'framer-motion'
import { getThumbnailUrl } from '@/lib/api'
import type { DragPreviewProps } from '@/types/sort'

// 内联样式定义
const styles = {
  container: {
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5), 0 0 0 2px rgba(255,255,255,0.8)',
    borderRadius: '8px',
    overflow: 'hidden',
    cursor: 'grabbing',
    position: 'relative' as const,
  },
  imageWrapper: {
    aspectRatio: '9/16',
    overflow: 'hidden',
    background: 'var(--bg-secondary)',
  },
  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover' as const,
    pointerEvents: 'none' as const,
  },
  label: {
    position: 'absolute' as const,
    bottom: '4px',
    left: '50%',
    transform: 'translateX(-50%)',
    padding: '2px 8px',
    background: 'rgba(0,0,0,0.8)',
    borderRadius: '4px',
    fontSize: '10px',
    color: '#fff',
    fontWeight: 500,
    whiteSpace: 'nowrap' as const,
  },
}

export function DragPreview({
  screenshot,
  projectName,
  zoom = 100,
}: DragPreviewProps) {
  const previewWidth = Math.round(120 * (zoom / 100))
  
  return (
    <motion.div
      initial={{ scale: 1, rotate: 0 }}
      animate={{ scale: 1.05, rotate: 2 }}
      transition={{ duration: 0.15, ease: 'easeOut' }}
      style={{ ...styles.container, width: `${previewWidth}px` }}
    >
      <div style={styles.imageWrapper}>
        <img
          src={getThumbnailUrl(projectName, screenshot.filename, 'small')}
          alt={screenshot.filename}
          style={styles.image}
        />
      </div>
      
      <div style={styles.label}>
        拖拽中...
      </div>
    </motion.div>
  )
}
