'use client'

import { Play, Flag } from 'lucide-react'

interface StatusBarProps {
  projectName: string
  total: number
  selected: number
  moved: number
  onboardingStart: number
  onboardingEnd: number
}

export function StatusBar({
  projectName,
  total,
  selected,
  moved,
  onboardingStart,
  onboardingEnd,
}: StatusBarProps) {
  const hasOnboarding = onboardingStart >= 0 && onboardingEnd >= 0
  const onboardingCount = hasOnboarding ? onboardingEnd - onboardingStart + 1 : 0

  return (
    <div
      style={{
        padding: '8px 20px',
        background: '#0a0a0a',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        display: 'flex',
        alignItems: 'center',
        gap: '24px',
        fontSize: '12px',
        color: '#6b7280',
      }}
    >
      {/* Project Name */}
      <span>
        <strong style={{ color: '#fff' }}>{projectName}</strong>
      </span>

      {/* Stats */}
      <div style={{ display: 'flex', gap: '16px' }}>
        <span>
          总数: <span style={{ color: '#fff' }}>{total}</span>
        </span>
        {selected > 0 && (
          <span>
            选中: <span style={{ color: '#fff' }}>{selected}</span>
          </span>
        )}
        {moved > 0 && (
          <span>
            已移动: <span style={{ color: '#9ca3af' }}>{moved}</span>
          </span>
        )}
      </div>

      {/* Onboarding Range */}
      {hasOnboarding && (
        <div
          style={{
            marginLeft: 'auto',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <span style={{ color: '#22c55e', fontWeight: 500 }}>Onboarding</span>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              background: 'rgba(34, 197, 94, 0.1)',
              padding: '4px 8px',
              borderRadius: '4px',
            }}
          >
            <Play size={10} style={{ color: '#22c55e' }} />
            <span style={{ color: '#22c55e' }}>#{onboardingStart + 1}</span>
            <span style={{ color: '#6b7280' }}>→</span>
            <Flag size={10} style={{ color: '#f59e0b' }} />
            <span style={{ color: '#f59e0b' }}>#{onboardingEnd + 1}</span>
            <span style={{ color: '#9ca3af', marginLeft: '4px' }}>
              ({onboardingCount}张)
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
