'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useOnboardingStore, calculateResults } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { personalizeText } from '../../utils/personalize'

interface LoadingScreenProps {
  config: ScreenConfig
}

export function LoadingScreen({ config }: LoadingScreenProps) {
  const { userData, setResults, nextStep, isManualNavigation, clearManualNavigation } = useOnboardingStore()
  
  // 个性化加载步骤
  const loadingSteps = [
    { text: personalizeText('Analyzing your profile, {{name}}...', userData.name), icon: '🔍' },
    { text: 'Calculating your metabolism...', icon: '⚡' },
    { text: 'Creating your nutrition plan...', icon: '🥗' },
    { text: personalizeText('Almost done, {{name}}!', userData.name), icon: '✨' }
  ]
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [progress, setProgress] = useState(0)
  
  useEffect(() => {
    // 如果是手动跳转到这个页面，清除标志但不自动跳转
    if (isManualNavigation) {
      clearManualNavigation()
      return
    }
    
    // 进度动画 - 平滑递增（5秒完成）
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          return 100
        }
        return prev + 1
      })
    }, 50)
    
    // 步骤切换 - 每个图标显示 1.25 秒，让动画完成且用户看清
    const stepInterval = setInterval(() => {
      setCurrentStepIndex(prev => {
        if (prev >= loadingSteps.length - 1) {
          clearInterval(stepInterval)
          return prev
        }
        return prev + 1
      })
    }, 1250)
    
    // 计算结果并前进 - 等待所有步骤显示完毕后再跳转
    const timer = setTimeout(() => {
      const results = calculateResults(userData)
      if (results) {
        setResults(results)
      }
      nextStep()
    }, 5200)
    
    return () => {
      clearInterval(progressInterval)
      clearInterval(stepInterval)
      clearTimeout(timer)
    }
  }, [userData, setResults, nextStep, isManualNavigation, clearManualNavigation])
  
  return (
    <div className="h-full flex flex-col items-center justify-center px-8" style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>
      {/* 背景动效 - VitaFlow 风格 */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-32 h-32 rounded-full"
            style={{
              background: `radial-gradient(circle, rgba(43, 39, 53, ${0.03 + i * 0.005}), transparent)`,
              left: `${(i * 20) % 100}%`,
              top: `${(i * 15) % 100}%`
            }}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.3, 0.6, 0.3],
              x: [0, 30, 0],
              y: [0, -20, 0]
            }}
            transition={{
              duration: 3 + i * 0.5,
              repeat: Infinity,
              delay: i * 0.3
            }}
          />
        ))}
      </div>
      
      {/* 主圆环进度 - VitaFlow 风格 */}
      <div className="relative z-10">
        <motion.div className="relative w-48 h-48">
          {/* 外环 - 背景 */}
          <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="rgba(43, 39, 53, 0.1)"
              strokeWidth="6"
            />
            {/* 外环 - 进度 - VitaFlow 深色 */}
            <circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke="#2B2735"
              strokeWidth="6"
              strokeLinecap="round"
              strokeDasharray={264}
              strokeDashoffset={264 - (264 * progress) / 100}
              style={{ transition: 'stroke-dashoffset 60ms linear' }}
            />
          </svg>
          
          {/* 中心内容 */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {/* 图标 - 恢复有质感的 spring 动画 */}
            <AnimatePresence mode="popLayout">
              <motion.span
                key={currentStepIndex}
                className="text-4xl mb-2"
                initial={{ scale: 0, opacity: 0, rotate: -180 }}
                animate={{ scale: 1, opacity: 1, rotate: 0 }}
                exit={{ scale: 0, opacity: 0, rotate: 180 }}
                transition={{ 
                  type: 'spring', 
                  stiffness: 200, 
                  damping: 15,
                  duration: 0.4
                }}
              >
                {loadingSteps[currentStepIndex]?.icon}
              </motion.span>
            </AnimatePresence>
            
            <motion.span 
              className="text-[24px] font-bold"
              style={{ color: '#2B2735' }}
            >
              {progress}%
            </motion.span>
          </div>
          
        </motion.div>
      </div>
      
      {/* 加载文本 - VitaFlow 样式 */}
      <AnimatePresence mode="wait">
        <motion.p
          key={currentStepIndex}
          className="mt-8 text-center font-medium text-[15px]"
          style={{ color: '#2B2735' }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
        >
          {loadingSteps[currentStepIndex]?.text}
        </motion.p>
      </AnimatePresence>
      
      {/* 底部提示 */}
      <motion.p
        className="absolute bottom-12 text-[13px]"
        style={{ color: '#999999' }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        This usually takes just a moment...
      </motion.p>
    </div>
  )
}







