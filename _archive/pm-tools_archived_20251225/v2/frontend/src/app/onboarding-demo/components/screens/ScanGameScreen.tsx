'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { useLongPress } from '../../hooks/useLongPress'
import { Button, BackButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'

interface ScanGameScreenProps {
  config: ScreenConfig
}

export function ScanGameScreen({ config }: ScanGameScreenProps) {
  const { completeScanGame, scanGameCompleted, nextStep, prevStep, currentStep, totalSteps } = useOnboardingStore()
  const [showResult, setShowResult] = useState(false)
  const [showParticles, setShowParticles] = useState(false)
  
  const { isPressed, progress, handlers } = useLongPress({
    threshold: 2500,
    onStart: () => {
      // 可以添加震动反馈
    },
    onComplete: () => {
      setShowParticles(true)
      setTimeout(() => {
        setShowResult(true)
        completeScanGame()
      }, 500)
    }
  })
  
  // 完成后自动继续
  useEffect(() => {
    if (scanGameCompleted && showResult) {
      const timer = setTimeout(() => {
        nextStep()
      }, 2500)
      return () => clearTimeout(timer)
    }
  }, [scanGameCompleted, showResult, nextStep])
  
  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-purple-50 via-white to-pink-50">
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部导航 */}
      <div className="flex items-center justify-between px-6 py-2">
        <BackButton onClick={prevStep} />
        <div />
      </div>
      
      {/* 标题 */}
      <div className="px-6 pt-4 pb-4 text-center">
        <motion.h1
          className="text-2xl font-bold text-gray-900"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {showResult ? '🎉 Amazing!' : config.title}
        </motion.h1>
        <motion.p
          className="mt-2 text-gray-500 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          {showResult ? 'Your food has been analyzed in seconds!' : config.subtitle}
        </motion.p>
      </div>
      
      {/* 扫描区域 */}
      <div className="flex-1 flex items-center justify-center px-8">
        <div className="relative">
          {/* 扫描框 */}
          <motion.div
            className="relative w-64 h-64 rounded-3xl overflow-hidden bg-gradient-to-br from-orange-100 to-yellow-50 shadow-2xl"
            animate={{
              boxShadow: isPressed 
                ? '0 25px 50px -12px rgba(139, 92, 246, 0.5)' 
                : '0 25px 50px -12px rgba(0, 0, 0, 0.15)'
            }}
          >
            {/* 食物图片 */}
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.span 
                className="text-8xl"
                animate={{ 
                  scale: isPressed ? [1, 1.1, 1] : 1,
                }}
                transition={{ duration: 0.5, repeat: isPressed ? Infinity : 0 }}
              >
                🍕
              </motion.span>
            </div>
            
            {/* 扫描框边框 */}
            <motion.div
              className="absolute inset-4 border-2 rounded-2xl"
              style={{
                borderColor: isPressed ? '#8B5CF6' : '#E5E7EB'
              }}
              animate={{
                borderColor: isPressed 
                  ? ['#8B5CF6', '#EC4899', '#8B5CF6'] 
                  : '#E5E7EB'
              }}
              transition={{ duration: 1, repeat: isPressed ? Infinity : 0 }}
            >
              {/* 扫描线 */}
              {isPressed && (
                <motion.div
                  className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent rounded-full"
                  animate={{ top: ['0%', '100%', '0%'] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                />
              )}
            </motion.div>
            
            {/* 进度覆盖层 */}
            {isPressed && progress < 1 && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-t from-purple-500/30 to-transparent"
                style={{ 
                  height: `${progress * 100}%`,
                  bottom: 0,
                  top: 'auto'
                }}
              />
            )}
          </motion.div>
          
          {/* 粒子效果 */}
          <AnimatePresence>
            {showParticles && (
              <>
                {[...Array(12)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-3 h-3 rounded-full"
                    style={{
                      background: i % 2 === 0 ? '#8B5CF6' : '#EC4899',
                      left: '50%',
                      top: '50%'
                    }}
                    initial={{ scale: 0, x: 0, y: 0 }}
                    animate={{
                      scale: [0, 1, 0],
                      x: Math.cos((i / 12) * Math.PI * 2) * 120,
                      y: Math.sin((i / 12) * Math.PI * 2) * 120
                    }}
                    transition={{ duration: 0.6, ease: 'easeOut' }}
                  />
                ))}
              </>
            )}
          </AnimatePresence>
          
          {/* 结果卡片 */}
          <AnimatePresence>
            {showResult && (
              <motion.div
                className="absolute inset-x-0 -bottom-24 mx-auto w-56 bg-white rounded-2xl p-4 shadow-xl"
                initial={{ opacity: 0, y: 20, scale: 0.9 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">Pizza Slice</p>
                    <p className="text-sm text-gray-500">285 kcal</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">Protein</p>
                    <p className="font-semibold text-purple-600">12g</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
      
      {/* 长按按钮 */}
      {!showResult && (
        <div className="px-8 pb-8">
          <div className="text-center mb-4">
            <p className="text-sm text-gray-500">
              {isPressed ? `Scanning... ${Math.round(progress * 100)}%` : 'Press and hold to scan'}
            </p>
          </div>
          
          <motion.button
            className={`
              w-full h-16 rounded-2xl font-semibold text-lg
              flex items-center justify-center gap-3
              transition-all duration-200
              ${isPressed 
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' 
                : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
              }
            `}
            style={{
              boxShadow: isPressed 
                ? '0 10px 40px -10px rgba(139, 92, 246, 0.5)' 
                : '0 10px 30px -10px rgba(139, 92, 246, 0.4)'
            }}
            animate={{
              scale: isPressed ? 0.98 : 1
            }}
            {...handlers}
          >
            {/* 进度条背景 */}
            <motion.div
              className="absolute left-0 top-0 bottom-0 rounded-2xl bg-white/20"
              style={{ width: `${progress * 100}%` }}
            />
            
            <span className="relative z-10">
              {isPressed ? '🔍 Scanning...' : '📸 Hold to Scan'}
            </span>
          </motion.button>
        </div>
      )}
      
      {/* 完成后的继续按钮 */}
      {showResult && (
        <motion.div
          className="px-6 py-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Button fullWidth size="lg" onClick={nextStep}>
            Continue
          </Button>
        </motion.div>
      )}
    </div>
  )
}







