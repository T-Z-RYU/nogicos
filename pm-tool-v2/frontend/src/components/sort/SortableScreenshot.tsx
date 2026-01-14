'use client'

import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Check, Play, Flag } from 'lucide-react'
import { getThumbnailUrl } from '@/lib/api'
import type { SortableScreenshotProps } from '@/types/sort'

// 内联样式定义（替代 style jsx 解决 scoped CSS 问题）
const styles = {
  card: {
    position: 'relative' as const,
    aspectRatio: '9/16',
    overflow: 'hidden',
    background: 'var(--bg-secondary)',
    cursor: 'pointer',
    borderRadius: '6px',
    transition: 'border 150ms, box-shadow 150ms',
  },
  dragHandle: {
    position: 'absolute' as const,
    inset: 0,
  },
  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover' as const,
    pointerEvents: 'none' as const,
  },
  selectedOverlay: {
    position: 'absolute' as const,
    inset: 0,
    background: 'rgba(59, 130, 246, 0.35)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    pointerEvents: 'none' as const,
  },
  checkIcon: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
  },
  index: {
    position: 'absolute' as const,
    top: '4px',
    left: '4px',
    padding: '2px 6px',
    background: 'rgba(0, 0, 0, 0.7)',
    borderRadius: '4px',
    fontSize: '10px',
    color: 'var(--text-secondary)',
    fontFamily: 'var(--font-mono)',
  },
  badge: {
    position: 'absolute' as const,
    bottom: '4px',
    left: '4px',
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '9px',
    color: '#fff',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '2px',
  },
  onboardingDot: {
    position: 'absolute' as const,
    bottom: '4px',
    left: '4px',
    width: '6px',
    height: '6px',
    background: '#22c55e',
    borderRadius: '50%',
  },
  newBadge: {
    position: 'absolute' as const,
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    padding: '4px 8px',
    background: '#f59e0b',
    borderRadius: '4px',
    fontSize: '10px',
    color: '#fff',
    fontWeight: 700,
    textTransform: 'uppercase' as const,
  },
}

export function SortableScreenshot({
  screenshot,
  projectName,
  index,
  isSelected,
  isNewlyAdded = false,
  onCardClick,
  onboardingStart,
  onboardingEnd,
}: SortableScreenshotProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ 
    id: screenshot.filename,
    transition: {
      duration: 200,
      easing: 'cubic-bezier(0.25, 1, 0.5, 1)',
    },
  })

  const isInOnboarding =
    onboardingStart >= 0 &&
    onboardingEnd >= 0 &&
    index >= onboardingStart &&
    index <= onboardingEnd

  const isStart = index === onboardingStart
  const isEnd = index === onboardingEnd

  const wrapperStyle = {
    transform: CSS.Transform.toString(transform),
    transition: transition || 'transform 200ms cubic-bezier(0.25, 1, 0.5, 1)',
    opacity: isDragging ? 0.3 : 1,
    zIndex: isDragging ? 100 : 'auto' as const,
  }

  const getBorderStyle = () => {
    if (isDragging) return '2px dashed rgba(255,255,255,0.4)'
    if (isNewlyAdded) return '3px solid #f59e0b'
    if (isSelected) return '3px solid #3b82f6'
    if (isInOnboarding) return '2px solid #22c55e'
    return '2px solid rgba(255,255,255,0.15)'
  }

  const getBoxShadow = () => {
    if (isNewlyAdded) return '0 0 20px rgba(245, 158, 11, 0.5)'
    if (isSelected) return '0 0 0 2px rgba(59, 130, 246, 0.5)'
    if (isDragging) return '0 20px 40px rgba(0, 0, 0, 0.4)'
    return undefined
  }

  return (
    <div
      ref={setNodeRef}
      style={wrapperStyle}
      {...attributes}
    >
      <div
        onClick={onCardClick}
        style={{
          ...styles.card,
          border: getBorderStyle(),
          boxShadow: getBoxShadow(),
        }}
      >
        {/* Drag Handle */}
        <div
          {...listeners}
          style={{ ...styles.dragHandle, cursor: isDragging ? 'grabbing' : 'grab' }}
        />

        <img
          src={getThumbnailUrl(projectName, screenshot.filename, 'small')}
          alt={screenshot.filename}
          style={styles.image}
          loading="lazy"
        />

        {/* 选中遮罩和勾选图标 */}
        {isSelected && (
          <div style={styles.selectedOverlay}>
            <div style={styles.checkIcon}>
              <Check size={24} style={{ color: '#3b82f6' }} />
            </div>
          </div>
        )}

        {/* 索引 */}
        <div style={styles.index}>
          {String(index + 1).padStart(4, '0')}
        </div>

        {/* START/END 标记 */}
        {isStart && (
          <div style={{ ...styles.badge, background: '#22c55e' }}>
            <Play size={8} /> START
          </div>
        )}
        {isEnd && (
          <div style={{ ...styles.badge, background: '#f59e0b' }}>
            <Flag size={8} /> END
          </div>
        )}

        {/* Onboarding 范围内标记 */}
        {isInOnboarding && !isStart && !isEnd && (
          <div style={styles.onboardingDot} />
        )}

        {/* 新添加标记 */}
        {isNewlyAdded && (
          <div style={styles.newBadge}>NEW</div>
        )}
      </div>
    </div>
  )
}
