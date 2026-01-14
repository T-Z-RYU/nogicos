'use client'

import { motion } from 'framer-motion'

interface ProgressBarProps {
  current: number
  total: number
  showLabel?: boolean
}

// VitaFlow 风格进度条
export function ProgressBar({ current, total, showLabel = false }: ProgressBarProps) {
  const progress = (current / total) * 100
  
  return (
    <div className="w-full px-6 py-3">
      {/* 进度条容器 - VitaFlow 细线样式 */}
      <div 
        className="relative h-[3px] rounded-full overflow-hidden"
        style={{ background: 'rgba(43, 39, 53, 0.1)' }}
      >
        {/* 进度填充 - VitaFlow 深色 */}
        <motion.div
          className="absolute left-0 top-0 h-full rounded-full"
          style={{ background: '#2B2735' }}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ 
            duration: 0.5,
            ease: [0.25, 0.46, 0.45, 0.94]
          }}
        />
      </div>
      
      {/* 标签 - 可选 */}
      {showLabel && (
        <div className="flex justify-between items-center mt-2">
          <motion.span 
            className="text-[11px] font-medium"
            style={{ color: '#999999', fontFamily: 'var(--font-outfit)' }}
            key={current}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            Step {current} of {total}
          </motion.span>
        </div>
      )}
    </div>
  )
}

// VitaFlow 分页点样式
export function ProgressDots({ current, total }: { current: number; total: number }) {
  // 只显示当前附近的点
  const visibleCount = Math.min(5, total)
  const startIndex = Math.max(0, Math.min(current - 3, total - visibleCount))
  
  return (
    <div className="flex items-center justify-center gap-[6px] py-4">
      {Array.from({ length: visibleCount }).map((_, i) => {
        const index = startIndex + i + 1
        const isActive = index === current
        const isPast = index < current
        
        return (
          <motion.div
            key={index}
            className="rounded-full transition-all duration-300"
            style={{
              width: isActive ? '20px' : '5px',
              height: '5px',
              background: isActive ? '#2B2735' : isPast ? 'rgba(43, 39, 53, 0.3)' : 'rgba(43, 39, 53, 0.15)'
            }}
            initial={false}
            animate={{
              scale: isActive ? 1 : 0.9,
              opacity: isActive ? 1 : isPast ? 0.7 : 0.4
            }}
          />
        )
      })}
    </div>
  )
}







