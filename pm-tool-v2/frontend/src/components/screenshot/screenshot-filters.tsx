'use client'

import { useScreenshotStore } from '@/store/screenshot-store'
import { X } from 'lucide-react'

export function ScreenshotFilters() {
  const {
    stages,
    modules,
    stageFilter,
    moduleFilter,
    setStageFilter,
    setModuleFilter,
    total,
    screenshots,
  } = useScreenshotStore()

  const hasFilters = stageFilter || moduleFilter
  const stageEntries = Object.entries(stages).sort((a, b) => b[1] - a[1])
  const moduleEntries = Object.entries(modules).sort((a, b) => b[1] - a[1])

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
      {/* 统计 */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px',
        fontSize: '13px',
        color: 'var(--text-muted)',
      }}>
        <span>
          <strong style={{ color: 'var(--text-primary)' }}>{screenshots.length}</strong>
          {' / '}{total} 张
        </span>
        {hasFilters && (
          <button
            className="btn-ghost"
            style={{ padding: '4px 8px', fontSize: '12px' }}
            onClick={() => {
              setStageFilter(null)
              setModuleFilter(null)
            }}
          >
            <X size={12} />
            清除
          </button>
        )}
      </div>

      {/* Stage 筛选 */}
      {stageEntries.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginRight: '4px' }}>
            Stage:
          </span>
          {stageEntries.slice(0, 5).map(([stage, count]) => (
            <button
              key={stage}
              className={`btn-ghost ${stageFilter === stage ? 'active' : ''}`}
              style={{ padding: '4px 10px', fontSize: '12px' }}
              onClick={() => setStageFilter(stageFilter === stage ? null : stage)}
            >
              {stage}
              <span style={{ opacity: 0.5, marginLeft: '4px' }}>({count})</span>
            </button>
          ))}
        </div>
      )}

      {/* Module 筛选 - 显示选中的 */}
      {moduleFilter && (
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '4px',
          padding: '4px 10px',
          background: 'var(--bg-active)',
          borderRadius: 'var(--radius-md)',
          fontSize: '12px',
        }}>
          <span style={{ color: 'var(--text-muted)' }}>Module:</span>
          <span style={{ color: 'var(--text-primary)' }}>{moduleFilter}</span>
          <button
            onClick={() => setModuleFilter(null)}
            style={{ 
              background: 'none', 
              border: 'none', 
              cursor: 'pointer',
              color: 'var(--text-muted)',
              padding: '2px',
              display: 'flex',
            }}
          >
            <X size={12} />
          </button>
        </div>
      )}
    </div>
  )
}


