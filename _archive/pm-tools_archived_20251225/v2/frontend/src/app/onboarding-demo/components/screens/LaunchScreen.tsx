'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'

interface LaunchScreenProps {
  config: ScreenConfig
}

export function LaunchScreen({ config }: LaunchScreenProps) {
  const { nextStep, isManualNavigation, clearManualNavigation } = useOnboardingStore()
  
  // 自动前进（仅在非手动导航时）
  useEffect(() => {
    // 如果是手动跳转到这个页面，清除标志但不自动跳转
    if (isManualNavigation) {
      clearManualNavigation()
      return
    }
    
    const timer = setTimeout(() => {
      nextStep()
    }, 2500)
    
    return () => clearTimeout(timer)
  }, [nextStep, isManualNavigation, clearManualNavigation])
  
  return (
    <div className="h-full flex flex-col items-center justify-center" style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>
      {/* 背景动效 - VitaFlow 风格 */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-1/2 -left-1/2 w-full h-full rounded-full blur-3xl"
          style={{ background: 'rgba(43, 39, 53, 0.03)' }}
          animate={{
            x: [0, 100, 0],
            y: [0, 50, 0],
            scale: [1, 1.2, 1]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        />
        <motion.div
          className="absolute -bottom-1/2 -right-1/2 w-full h-full rounded-full blur-3xl"
          style={{ background: 'rgba(43, 39, 53, 0.02)' }}
          animate={{
            x: [0, -80, 0],
            y: [0, -60, 0],
            scale: [1.2, 1, 1.2]
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        />
      </div>
      
      {/* Logo - VitaFlow 风格 */}
      <motion.div
        className="relative z-10"
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{
          type: 'spring',
          stiffness: 200,
          damping: 20,
          delay: 0.2
        }}
      >
        {/* Logo 容器 - VitaFlow 深色 */}
        <motion.div 
          className="w-24 h-24 rounded-3xl flex items-center justify-center shadow-2xl"
          style={{ background: '#2B2735', boxShadow: '0px 8px 32px rgba(43, 39, 53, 0.25)' }}
          animate={{
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        >
          {/* 简化的 V 字母 Logo */}
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <path
              d="M12 14L24 34L36 14"
              stroke="white"
              strokeWidth="4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <motion.circle
              cx="24"
              cy="24"
              r="4"
              fill="white"
              initial={{ scale: 0 }}
              animate={{ scale: [0, 1.2, 1] }}
              transition={{ delay: 0.5, duration: 0.5 }}
            />
          </svg>
        </motion.div>
        
        {/* 光环效果 */}
        <motion.div
          className="absolute inset-0 rounded-3xl"
          style={{
            background: 'linear-gradient(45deg, transparent, rgba(255,255,255,0.2), transparent)',
          }}
          animate={{
            opacity: [0, 1, 0],
            rotate: [0, 180, 360]
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'linear'
          }}
        />
      </motion.div>
      
      {/* 品牌名 - VitaFlow 样式 */}
      <motion.h1
        className="mt-6 text-[28px] font-medium tracking-[-0.28px]"
        style={{ color: '#2B2735' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        {config.title}
      </motion.h1>
      
      {/* 副标题 */}
      <motion.p
        className="mt-2 text-[14px]"
        style={{ color: '#999999' }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.6 }}
      >
        {config.subtitle}
      </motion.p>
      
      {/* 加载指示器 - VitaFlow 风格 */}
      <motion.div
        className="mt-12 flex gap-1.5"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-2 h-2 rounded-full"
            style={{ background: '#2B2735' }}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.3, 1, 0.3]
            }}
            transition={{
              duration: 0.8,
              repeat: Infinity,
              delay: i * 0.2
            }}
          />
        ))}
      </motion.div>
    </div>
  )
}







