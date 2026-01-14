'use client'

import { useState, useRef } from 'react'
import { motion, useAnimation } from 'framer-motion'

interface SpinWheelProps {
  onSpinComplete: (prize: number) => void
  forcePrize?: number // 强制中奖的奖品索引
  disabled?: boolean
}

const segments = [
  { label: '10%', color: '#F3E8FF', textColor: '#7C3AED', value: 10 },
  { label: '20%', color: '#FDE68A', textColor: '#92400E', value: 20 },
  { label: '15%', color: '#F3E8FF', textColor: '#7C3AED', value: 15 },
  { label: '50%', color: '#8B5CF6', textColor: '#FFFFFF', value: 50 },
  { label: '🔄', color: '#E5E7EB', textColor: '#374151', value: 0 },
  { label: '25%', color: '#FDE68A', textColor: '#92400E', value: 25 },
]

export function SpinWheel({ onSpinComplete, forcePrize, disabled }: SpinWheelProps) {
  const [isSpinning, setIsSpinning] = useState(false)
  const [rotation, setRotation] = useState(0)
  const controls = useAnimation()
  
  const handleSpin = async () => {
    if (isSpinning || disabled) return
    setIsSpinning(true)
    
    // 确定目标奖品
    const targetIndex = forcePrize !== undefined 
      ? forcePrize 
      : Math.floor(Math.random() * segments.length)
    
    // 计算旋转角度（每个扇形60度）
    const segmentAngle = 360 / segments.length
    const targetAngle = targetIndex * segmentAngle
    
    // 旋转多圈后停在目标位置（指针在顶部，需要补偿）
    const spins = 5 + Math.random() * 2 // 5-7圈
    const finalRotation = rotation + (spins * 360) + (360 - targetAngle - segmentAngle / 2)
    
    await controls.start({
      rotate: finalRotation,
      transition: {
        duration: 4 + Math.random(),
        ease: [0.15, 0.85, 0.25, 1], // 自定义缓动：快速开始，缓慢结束
      }
    })
    
    setRotation(finalRotation)
    setIsSpinning(false)
    onSpinComplete(segments[targetIndex].value)
  }
  
  const segmentAngle = 360 / segments.length
  
  return (
    <div className="relative flex flex-col items-center">
      {/* 指针 */}
      <div className="absolute -top-2 z-10 w-0 h-0 border-l-[15px] border-l-transparent border-r-[15px] border-r-transparent border-t-[25px] border-t-purple-600 drop-shadow-lg" />
      
      {/* 轮盘外框光效 */}
      <motion.div 
        className="absolute inset-0 -m-4 rounded-full"
        style={{
          background: 'conic-gradient(from 0deg, rgba(139, 92, 246, 0.3), rgba(236, 72, 153, 0.3), rgba(139, 92, 246, 0.3))'
        }}
        animate={{
          rotate: [0, 360]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'linear'
        }}
      />
      
      {/* 轮盘 */}
      <motion.div
        className="relative w-[280px] h-[280px] rounded-full shadow-2xl"
        animate={controls}
        style={{
          rotate: rotation,
          background: '#F9FAFB'
        }}
      >
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {segments.map((segment, index) => {
            const startAngle = index * segmentAngle - 90
            const endAngle = startAngle + segmentAngle
            
            const startRad = (startAngle * Math.PI) / 180
            const endRad = (endAngle * Math.PI) / 180
            
            const x1 = 50 + 45 * Math.cos(startRad)
            const y1 = 50 + 45 * Math.sin(startRad)
            const x2 = 50 + 45 * Math.cos(endRad)
            const y2 = 50 + 45 * Math.sin(endRad)
            
            const largeArc = segmentAngle > 180 ? 1 : 0
            
            const textAngle = startAngle + segmentAngle / 2
            const textRad = (textAngle * Math.PI) / 180
            const textX = 50 + 30 * Math.cos(textRad)
            const textY = 50 + 30 * Math.sin(textRad)
            
            return (
              <g key={index}>
                <path
                  d={`M 50 50 L ${x1} ${y1} A 45 45 0 ${largeArc} 1 ${x2} ${y2} Z`}
                  fill={segment.color}
                  stroke="#fff"
                  strokeWidth="0.5"
                />
                <text
                  x={textX}
                  y={textY}
                  fill={segment.textColor}
                  fontSize="7"
                  fontWeight="bold"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  transform={`rotate(${textAngle + 90}, ${textX}, ${textY})`}
                >
                  {segment.label}
                </text>
              </g>
            )
          })}
          
          {/* 中心圆 */}
          <circle cx="50" cy="50" r="12" fill="white" stroke="#8B5CF6" strokeWidth="2" />
          <text
            x="50"
            y="50"
            fill="#8B5CF6"
            fontSize="5"
            fontWeight="bold"
            textAnchor="middle"
            dominantBaseline="middle"
          >
            SPIN
          </text>
        </svg>
      </motion.div>
      
      {/* 旋转按钮 */}
      <motion.button
        onClick={handleSpin}
        disabled={isSpinning || disabled}
        className={`
          mt-8 px-8 py-4 rounded-full font-bold text-white text-lg
          ${isSpinning || disabled 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-gradient-to-r from-purple-500 to-pink-500 shadow-lg shadow-purple-500/30'
          }
        `}
        whileHover={!isSpinning && !disabled ? { scale: 1.05 } : {}}
        whileTap={!isSpinning && !disabled ? { scale: 0.95 } : {}}
      >
        {isSpinning ? 'Spinning...' : '🎰 Spin Now!'}
      </motion.button>
    </div>
  )
}







