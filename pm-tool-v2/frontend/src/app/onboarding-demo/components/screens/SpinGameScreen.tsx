'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { SpinWheel } from '../ui/SpinWheel'
import { Button, BackButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'
import { personalizeText } from '../../utils/personalize'

interface SpinGameScreenProps {
  config: ScreenConfig
}

export function SpinGameScreen({ config }: SpinGameScreenProps) {
  const { spinAttempts, spinWheel, discountWon, nextStep, prevStep, currentStep, totalSteps, userData } = useOnboardingStore()
  
  // 个性化文本
  const title = config.usePersonalization ? personalizeText(config.title, userData.name) : config.title
  const subtitle = config.usePersonalization ? personalizeText(config.subtitle, userData.name) : config.subtitle
  const [lastPrize, setLastPrize] = useState<number | null>(null)
  const [isSpinning, setIsSpinning] = useState(false)
  const [showCelebration, setShowCelebration] = useState(false)
  
  // 确定是第几次转
  const isFirstSpin = spinAttempts === 0
  const isSecondSpin = spinAttempts === 1
  
  // 强制结果
  const forcePrize = isSecondSpin ? 3 : undefined // 3 是 50% 的索引
  
  const handleSpinComplete = (prize: number) => {
    setLastPrize(prize)
    setIsSpinning(false)
    
    if (prize === 50) {
      setShowCelebration(true)
      setTimeout(() => {
        nextStep()
      }, 2000)
    }
  }
  
  const handleContinue = () => {
    if (lastPrize === 0 || (lastPrize && lastPrize < 50)) {
      // 如果没中大奖，进入第二次转盘页面
      nextStep()
    } else if (lastPrize === 50) {
      // 中了 50%，进入折扣付费墙
      nextStep()
    }
  }
  
  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-yellow-50 via-white to-purple-50 relative overflow-hidden">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-20 -left-20 w-40 h-40 bg-yellow-300/20 rounded-full blur-3xl"
          animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 4, repeat: Infinity }}
        />
        <motion.div
          className="absolute -bottom-20 -right-20 w-60 h-60 bg-purple-300/20 rounded-full blur-3xl"
          animate={{ scale: [1.2, 1, 1.2], opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 5, repeat: Infinity }}
        />
      </div>
      
      {/* 庆祝效果 */}
      <AnimatePresence>
        {showCelebration && (
          <>
            {[...Array(30)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-3 h-3 rounded-full"
                style={{
                  background: ['#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#3B82F6'][i % 5],
                  left: `${Math.random() * 100}%`,
                  top: -20
                }}
                initial={{ y: -20, opacity: 1 }}
                animate={{
                  y: 900,
                  x: (Math.random() - 0.5) * 200,
                  rotate: Math.random() * 720,
                  opacity: [1, 1, 0]
                }}
                transition={{
                  duration: 2 + Math.random(),
                  ease: 'easeIn',
                  delay: Math.random() * 0.5
                }}
              />
            ))}
          </>
        )}
      </AnimatePresence>
      
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部导航 */}
      <div className="flex items-center justify-between px-6 py-2 relative z-10">
        <BackButton onClick={prevStep} />
        <div />
      </div>
      
      {/* 标题 */}
      <div className="px-6 pt-2 pb-4 text-center relative z-10">
        <motion.h1
          className="text-2xl font-bold text-gray-900"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {title}
        </motion.h1>
        <motion.p
          className="mt-2 text-gray-500 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          {subtitle}
        </motion.p>
      </div>
      
      {/* 轮盘区域 */}
      <div className="flex-1 flex items-center justify-center relative z-10">
        <SpinWheel
          onSpinComplete={handleSpinComplete}
          forcePrize={forcePrize}
          disabled={isSpinning || showCelebration}
        />
      </div>
      
      {/* 结果提示 */}
      <AnimatePresence>
        {lastPrize !== null && !showCelebration && (
          <motion.div
            className="absolute bottom-32 left-0 right-0 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            {lastPrize === 0 ? (
              <p className="text-gray-600 font-medium">So close! Try again 🍀</p>
            ) : lastPrize < 50 ? (
              <p className="text-orange-600 font-medium">You got {lastPrize}% off! But wait...</p>
            ) : (
              <p className="text-purple-600 font-bold text-xl">🎉 Amazing! 50% OFF!</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* 底部按钮 */}
      {lastPrize !== null && lastPrize !== 50 && !isSpinning && (
        <motion.div
          className="px-6 py-6 relative z-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Button fullWidth size="lg" onClick={handleContinue}>
            {lastPrize === 0 ? 'Try One More Time!' : 'See Your Discount'}
          </Button>
        </motion.div>
      )}
    </div>
  )
}







