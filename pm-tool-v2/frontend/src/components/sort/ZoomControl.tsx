'use client'

import { useState } from 'react'
import { ZoomIn, ZoomOut } from 'lucide-react'
import { ZOOM_CONFIG } from '@/types/sort'
import type { ZoomControlProps } from '@/types/sort'

// 内联样式定义
const styles = {
  container: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    padding: '4px 8px',
    background: 'var(--bg-secondary)',
    borderRadius: '8px',
  },
  btn: {
    padding: '4px',
    background: 'transparent',
    border: 'none',
    borderRadius: '4px',
    color: 'var(--text-secondary)',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'color 150ms, background 150ms',
  },
  btnDisabled: {
    color: 'var(--text-muted)',
    cursor: 'not-allowed',
  },
  btnHover: {
    background: 'rgba(255,255,255,0.1)',
    color: 'var(--text-primary)',
  },
  value: {
    padding: '2px 8px',
    background: 'transparent',
    border: 'none',
    borderRadius: '4px',
    color: 'var(--text-primary)',
    cursor: 'pointer',
    fontSize: '12px',
    fontFamily: 'var(--font-mono)',
    fontWeight: 500,
    minWidth: '48px',
    transition: 'background 150ms',
  },
  valueChanged: {
    background: 'rgba(59, 130, 246, 0.2)',
  },
}

export function ZoomControl({
  zoom,
  onZoomIn,
  onZoomOut,
  onReset,
  min = ZOOM_CONFIG.min,
  max = ZOOM_CONFIG.max,
}: ZoomControlProps) {
  const isAtMin = zoom <= min
  const isAtMax = zoom >= max
  const isDefault = zoom === ZOOM_CONFIG.default
  const [hoveredBtn, setHoveredBtn] = useState<string | null>(null)

  return (
    <div style={styles.container}>
      <button
        onClick={onZoomOut}
        disabled={isAtMin}
        style={{
          ...styles.btn,
          ...(isAtMin ? styles.btnDisabled : {}),
          ...(hoveredBtn === 'out' && !isAtMin ? styles.btnHover : {}),
        }}
        onMouseEnter={() => setHoveredBtn('out')}
        onMouseLeave={() => setHoveredBtn(null)}
        title="缩小 (Ctrl+-)"
      >
        <ZoomOut size={16} />
      </button>
      
      <button
        onClick={onReset}
        style={{
          ...styles.value,
          ...(!isDefault ? styles.valueChanged : {}),
          ...(hoveredBtn === 'reset' ? { background: 'rgba(255,255,255,0.1)' } : {}),
        }}
        onMouseEnter={() => setHoveredBtn('reset')}
        onMouseLeave={() => setHoveredBtn(null)}
        title="重置缩放 (Ctrl+0)"
      >
        {zoom}%
      </button>
      
      <button
        onClick={onZoomIn}
        disabled={isAtMax}
        style={{
          ...styles.btn,
          ...(isAtMax ? styles.btnDisabled : {}),
          ...(hoveredBtn === 'in' && !isAtMax ? styles.btnHover : {}),
        }}
        onMouseEnter={() => setHoveredBtn('in')}
        onMouseLeave={() => setHoveredBtn(null)}
        title="放大 (Ctrl++)"
      >
        <ZoomIn size={16} />
      </button>
    </div>
  )
}
