'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, useMotionValue, useTransform, animate } from 'framer-motion'

interface NumberPickerProps {
  value: number
  onChange: (value: number) => void
  min: number
  max: number
  step: number
  unit: string
}

export function NumberPicker({ value, onChange, min, max, step, unit }: NumberPickerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  
  // 生成数字列表
  const numbers = []
  for (let i = min; i <= max; i += step) {
    numbers.push(Math.round(i * 10) / 10)
  }
  
  const currentIndex = numbers.indexOf(value)
  const itemHeight = 60
  
  // 滚动位置
  const y = useMotionValue(0)
  
  // 设置初始位置
  useEffect(() => {
    const targetY = -currentIndex * itemHeight
    animate(y, targetY, { type: 'spring', stiffness: 300, damping: 30 })
  }, [currentIndex, itemHeight, y])
  
  const handleDragEnd = () => {
    setIsDragging(false)
    const currentY = y.get()
    const nearestIndex = Math.round(-currentY / itemHeight)
    const clampedIndex = Math.max(0, Math.min(nearestIndex, numbers.length - 1))
    const targetY = -clampedIndex * itemHeight
    
    animate(y, targetY, {
      type: 'spring',
      stiffness: 300,
      damping: 30,
      onComplete: () => {
        onChange(numbers[clampedIndex])
      }
    })
  }
  
  return (
    <div className="relative flex flex-col items-center">
      {/* 大数字显示 */}
      <motion.div 
        className="text-6xl font-bold text-center mb-2"
        style={{
          background: 'linear-gradient(135deg, #8B5CF6, #EC4899)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}
        key={value}
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      >
        {value}
      </motion.div>
      
      <span className="text-lg text-gray-400 font-medium mb-6">{unit}</span>
      
      {/* 滚轮选择器 */}
      <div 
        ref={containerRef}
        className="relative h-[180px] w-full overflow-hidden"
      >
        {/* 选中区域高亮 */}
        <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-[60px] bg-gradient-to-r from-purple-500/10 via-purple-500/15 to-purple-500/10 rounded-xl border border-purple-500/20 pointer-events-none z-10" />
        
        {/* 渐变遮罩 - 顶部 */}
        <div className="absolute top-0 inset-x-0 h-16 bg-gradient-to-b from-white via-white/90 to-transparent pointer-events-none z-20" />
        
        {/* 渐变遮罩 - 底部 */}
        <div className="absolute bottom-0 inset-x-0 h-16 bg-gradient-to-t from-white via-white/90 to-transparent pointer-events-none z-20" />
        
        {/* 数字列表 */}
        <motion.div
          className="absolute inset-x-0"
          style={{ 
            y,
            top: '50%',
            marginTop: '-30px'
          }}
          drag="y"
          dragConstraints={{
            top: -(numbers.length - 1) * itemHeight,
            bottom: 0
          }}
          dragElastic={0.1}
          onDragStart={() => setIsDragging(true)}
          onDragEnd={handleDragEnd}
        >
          {numbers.map((num, index) => {
            const distance = Math.abs(index - currentIndex)
            const scale = distance === 0 ? 1 : distance === 1 ? 0.85 : 0.7
            const opacity = distance === 0 ? 1 : distance === 1 ? 0.5 : 0.25
            
            return (
              <motion.div
                key={num}
                className="h-[60px] flex items-center justify-center cursor-grab active:cursor-grabbing"
                style={{
                  fontSize: distance === 0 ? '28px' : '20px',
                  fontWeight: distance === 0 ? 600 : 400,
                  color: distance === 0 ? '#1F2937' : '#9CA3AF'
                }}
                animate={{
                  scale,
                  opacity: isDragging ? 0.8 : opacity
                }}
                onClick={() => {
                  if (!isDragging) {
                    onChange(num)
                  }
                }}
              >
                {num}
              </motion.div>
            )
          })}
        </motion.div>
      </div>
      
      {/* 快速调整按钮 */}
      <div className="flex gap-4 mt-4">
        <motion.button
          className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 font-bold text-xl"
          whileHover={{ scale: 1.1, backgroundColor: '#F3E8FF' }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onChange(Math.max(min, value - step))}
        >
          −
        </motion.button>
        <motion.button
          className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 font-bold text-xl"
          whileHover={{ scale: 1.1, backgroundColor: '#F3E8FF' }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onChange(Math.min(max, value + step))}
        >
          +
        </motion.button>
      </div>
    </div>
  )
}

// VitaFlow 风格滑块版本
export function NumberSlider({ value, onChange, min, max, step, unit }: NumberPickerProps) {
  return (
    <div className="w-full px-4" style={{ fontFamily: 'var(--font-outfit)' }}>
      {/* 数值显示 - VitaFlow 样式 */}
      <motion.div 
        className="text-center mb-8"
        key={value}
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
      >
        <span 
          className="text-[64px] font-bold"
          style={{ color: '#2B2735' }}
        >
          {value}
        </span>
        <span className="text-[24px] ml-2" style={{ color: '#999999' }}>{unit}</span>
      </motion.div>
      
      {/* 滑块 - VitaFlow 风格 */}
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-[6px] rounded-full appearance-none cursor-pointer
            [&::-webkit-slider-thumb]:appearance-none
            [&::-webkit-slider-thumb]:w-6
            [&::-webkit-slider-thumb]:h-6
            [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-[#2B2735]
            [&::-webkit-slider-thumb]:shadow-[0px_2px_8px_rgba(43,39,53,0.3)]
            [&::-webkit-slider-thumb]:cursor-grab
            [&::-webkit-slider-thumb]:active:cursor-grabbing
            [&::-webkit-slider-thumb]:transition-transform
            [&::-webkit-slider-thumb]:hover:scale-110
          "
          style={{
            background: `linear-gradient(to right, #2B2735 0%, #2B2735 ${((value - min) / (max - min)) * 100}%, rgba(43,39,53,0.15) ${((value - min) / (max - min)) * 100}%, rgba(43,39,53,0.15) 100%)`
          }}
        />
        
        {/* 标签 */}
        <div className="flex justify-between mt-2 text-[13px]" style={{ color: '#999999' }}>
          <span>{min} {unit}</span>
          <span>{max} {unit}</span>
        </div>
      </div>
    </div>
  )
}







