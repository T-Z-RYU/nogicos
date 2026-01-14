'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button } from '../ui/Button'
import confetti from 'canvas-confetti'
import { personalizeText } from '../../utils/personalize'

interface CelebrationScreenProps {
  config: ScreenConfig
}

export function CelebrationScreen({ config }: CelebrationScreenProps) {
  const { nextStep, currentStep, totalSteps, userData } = useOnboardingStore()
  
  // 个性化文本
  const title = config.usePersonalization ? personalizeText(config.title, userData.name) : config.title
  const subtitle = config.usePersonalization ? personalizeText(config.subtitle, userData.name) : config.subtitle
  const confettiTriggered = useRef(false)
  
  // 触发撒花效果
  useEffect(() => {
    if (confettiTriggered.current) return
    confettiTriggered.current = true
    
    // 第一波
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#8B5CF6', '#EC4899', '#F59E0B', '#10B981']
    })
    
    // 第二波
    setTimeout(() => {
      confetti({
        particleCount: 50,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ['#8B5CF6', '#EC4899']
      })
    }, 250)
    
    // 第三波
    setTimeout(() => {
      confetti({
        particleCount: 50,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ['#F59E0B', '#10B981']
      })
    }, 400)
  }, [])
  
  const isLastScreen = currentStep === totalSteps
  
  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-purple-100 via-pink-50 to-white relative overflow-hidden">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* 浮动圆形 */}
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full"
            style={{
              width: 20 + Math.random() * 40,
              height: 20 + Math.random() * 40,
              background: i % 2 === 0 
                ? 'rgba(139, 92, 246, 0.1)' 
                : 'rgba(236, 72, 153, 0.1)',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`
            }}
            animate={{
              y: [0, -20, 0],
              x: [0, 10, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2
            }}
          />
        ))}
      </div>
      
      {/* 主要内容 */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 relative z-10">
        {/* 成功勾选动画 */}
        <motion.div
          className="w-32 h-32 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center shadow-2xl shadow-green-500/30 mb-8"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ 
            type: 'spring',
            stiffness: 200,
            damping: 15,
            delay: 0.2
          }}
        >
          <motion.svg
            width="60"
            height="60"
            viewBox="0 0 60 60"
            fill="none"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <motion.path
              d="M15 30L25 40L45 20"
              stroke="white"
              strokeWidth="6"
              strokeLinecap="round"
              strokeLinejoin="round"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.5, delay: 0.6 }}
            />
          </motion.svg>
        </motion.div>
        
        {/* 标题 */}
        <motion.h1
          className="text-3xl font-bold text-gray-900 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          {title.replace(/[🎊🚀]/g, '').trim()}
        </motion.h1>
        
        {/* 大 emoji */}
        <motion.div
          className="text-5xl my-4"
          initial={{ scale: 0 }}
          animate={{ scale: [0, 1.3, 1] }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          {title.includes('Welcome') ? '🎊' : '🚀'}
        </motion.div>
        
        {/* 副标题 */}
        <motion.p
          className="text-gray-500 text-center text-sm leading-relaxed"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          {subtitle}
        </motion.p>
        
        {/* 额外信息（如果是最后一页） */}
        {isLastScreen && (
          <motion.div
            className="mt-8 p-4 bg-white rounded-2xl shadow-lg w-full"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <span className="text-2xl">📸</span>
              </div>
              <div>
                <p className="font-semibold text-gray-900">Ready to scan?</p>
                <p className="text-xs text-gray-500">Your first meal is waiting!</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
      
      {/* 底部按钮 */}
      <motion.div
        className="px-6 py-8 relative z-10"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        <Button fullWidth size="lg" onClick={nextStep}>
          {isLastScreen ? "Let's Go! 🚀" : 'Continue'}
        </Button>
      </motion.div>
    </div>
  )
}







