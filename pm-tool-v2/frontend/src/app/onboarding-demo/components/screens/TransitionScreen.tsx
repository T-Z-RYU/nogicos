'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button, BackButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'
import { personalizeText } from '../../utils/personalize'

interface TransitionScreenProps {
  config: ScreenConfig
}

// 根据标题选择合适的动画图标
function getAnimatedIcon(title: string) {
  // Nice to meet you - 挥手欢迎
  if (title.includes('Nice to meet') || title.includes('meet you')) {
    return (
      <motion.div
        className="text-6xl"
        animate={{ 
          rotate: [0, 20, -10, 20, 0],
        }}
        transition={{ duration: 1.2, repeat: Infinity }}
      >
        👋
      </motion.div>
    )
  }
  if (title.includes('Great') || title.includes('🎯')) {
    return (
      <motion.div
        className="text-6xl"
        animate={{ 
          scale: [1, 1.2, 1],
          rotate: [0, 10, -10, 0]
        }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        🎯
      </motion.div>
    )
  }
  if (title.includes('You can') || title.includes('💪')) {
    return (
      <motion.div
        className="text-6xl"
        animate={{ 
          rotate: [0, 15, -15, 0],
          scale: [1, 1.1, 1]
        }}
        transition={{ duration: 0.8, repeat: Infinity }}
      >
        💪
      </motion.div>
    )
  }
  if (title.includes('try it') || title.includes('📸')) {
    return (
      <motion.div className="relative">
        <motion.div
          className="text-6xl"
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
        >
          📸
        </motion.div>
        <motion.div
          className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-400 rounded-full"
          animate={{ 
            scale: [0, 1.5, 0],
            opacity: [1, 0.5, 0]
          }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      </motion.div>
    )
  }
  if (title.includes('all set') || title.includes('🎉')) {
    return (
      <motion.div
        className="text-6xl"
        animate={{ 
          y: [0, -10, 0],
          rotate: [0, 10, -10, 0]
        }}
        transition={{ duration: 1, repeat: Infinity }}
      >
        🎉
      </motion.div>
    )
  }
  if (title.includes('Almost') || title.includes('⏳')) {
    return (
      <motion.div
        className="text-6xl"
        animate={{ rotate: [0, 180] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
      >
        ⏳
      </motion.div>
    )
  }
  if (title.includes('Pro tips') || title.includes('💡')) {
    return (
      <motion.div
        className="text-6xl"
        animate={{ 
          opacity: [0.5, 1, 0.5],
          scale: [0.95, 1.05, 0.95]
        }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        💡
      </motion.div>
    )
  }
  if (title.includes('sure') || title.includes('Are you')) {
    return (
      <motion.div
        className="text-6xl"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 0.8, repeat: Infinity }}
      >
        🤔
      </motion.div>
    )
  }
  
  // 默认动画
  return (
    <motion.div
      className="text-6xl"
      animate={{ scale: [1, 1.1, 1] }}
      transition={{ duration: 1.5, repeat: Infinity }}
    >
      ✨
    </motion.div>
  )
}

export function TransitionScreen({ config }: TransitionScreenProps) {
  const { nextStep, prevStep, currentStep, totalSteps, goToStep, isManualNavigation, clearManualNavigation, userData } = useOnboardingStore()
  
  // 个性化文本
  const title = config.usePersonalization ? personalizeText(config.title, userData.name) : (config.title || '')
  const subtitle = config.usePersonalization ? personalizeText(config.subtitle, userData.name) : (config.subtitle || '')
  
  // 自动前进（如果配置了，且非手动导航）
  useEffect(() => {
    // 如果是手动跳转到这个页面，清除标志但不自动跳转
    if (isManualNavigation) {
      clearManualNavigation()
      return
    }
    
    if (config.autoAdvance) {
      const timer = setTimeout(() => {
        nextStep()
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [config.autoAdvance, nextStep, isManualNavigation, clearManualNavigation])
  
  // 特殊处理：P31 "Are you sure?" 页面
  const isConfirmationPage = config.id === 31
  
  const handleConfirmLeave = () => {
    // 回到欢迎页
    goToStep(1)
  }
  
  const handleStay = () => {
    // 返回到折扣付费墙
    prevStep()
  }
  
  return (
    <div className="h-full flex flex-col" style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>
      {/* 进度条 */}
      {!config.autoAdvance && (
        <ProgressBar current={currentStep} total={totalSteps} />
      )}
      
      {/* 头部导航（非确认页面时显示） */}
      {!config.autoAdvance && !isConfirmationPage && (
        <div className="flex items-center justify-between px-5 py-2">
          <BackButton onClick={prevStep} />
          <div />
        </div>
      )}
      
      {/* 背景装饰 - VitaFlow 风格 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/4 left-0 w-64 h-64 rounded-full blur-3xl"
          style={{ background: 'rgba(43, 39, 53, 0.03)' }}
          animate={{ x: [-20, 20, -20], y: [-10, 10, -10] }}
          transition={{ duration: 6, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-1/4 right-0 w-64 h-64 rounded-full blur-3xl"
          style={{ background: 'rgba(43, 39, 53, 0.02)' }}
          animate={{ x: [20, -20, 20], y: [10, -10, 10] }}
          transition={{ duration: 8, repeat: Infinity }}
        />
      </div>
      
      {/* 主要内容 */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 relative z-10">
        {/* 动画图标 */}
        <motion.div
          className="mb-8"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        >
          {getAnimatedIcon(title)}
        </motion.div>
        
        {/* 标题 - VitaFlow 样式 */}
        <motion.h1
          className="text-[24px] font-semibold text-center tracking-[-0.5px]"
          style={{ color: '#2B2735' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {title.replace(/[🎯💪📸🎉⏳💡]/g, '').trim()}
        </motion.h1>
        
        {/* 副标题 */}
        <motion.p
          className="mt-4 text-center text-[14px] leading-relaxed"
          style={{ color: '#999999' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {subtitle}
        </motion.p>
      </div>
      
      {/* 底部按钮 - VitaFlow 样式 */}
      {!config.autoAdvance && (
        <motion.div
          className="px-5 py-6 space-y-3"
          style={{ background: '#F2F1F6' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          {isConfirmationPage ? (
            <>
              <Button fullWidth size="lg" onClick={handleStay}>
                Claim My 50% Discount
              </Button>
              <Button fullWidth size="lg" variant="ghost" onClick={handleConfirmLeave}>
                No thanks, I'll pay full price later
              </Button>
            </>
          ) : (
            <Button fullWidth size="lg" onClick={nextStep}>
              Continue
            </Button>
          )}
        </motion.div>
      )}
    </div>
  )
}







