'use client'

import { motion } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button, BackButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'
import { personalizeText } from '../../utils/personalize'
import { ArrowRight, Sparkles } from 'lucide-react'

interface SoftCommitScreenProps {
  config: ScreenConfig & { softCommitText?: string }
}

export function SoftCommitScreen({ config }: SoftCommitScreenProps) {
  const { nextStep, prevStep, currentStep, totalSteps, userData } = useOnboardingStore()
  
  const title = config.usePersonalization ? personalizeText(config.title, userData.name) : config.title
  const subtitle = config.usePersonalization ? personalizeText(config.subtitle, userData.name) : config.subtitle
  
  return (
    <div className="h-full flex flex-col" style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部导航 */}
      <div className="flex items-center justify-between px-5 py-2">
        <BackButton onClick={prevStep} />
        <div />
      </div>
      
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/3 left-1/2 -translate-x-1/2 w-80 h-80 rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(43, 39, 53, 0.05) 0%, transparent 70%)' }}
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
          transition={{ duration: 4, repeat: Infinity }}
        />
      </div>
      
      {/* 主要内容 */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 relative z-10">
        {/* 动画图标 */}
        <motion.div
          className="mb-8 relative"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        >
          <motion.div
            className="w-24 h-24 rounded-[28px] flex items-center justify-center"
            style={{ background: 'rgba(43, 39, 53, 0.08)' }}
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <Sparkles className="w-12 h-12" style={{ color: '#2B2735' }} />
          </motion.div>
          
          {/* 闪烁点 */}
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-3 h-3 rounded-full"
              style={{ 
                background: '#2B2735',
                top: `${20 + i * 20}%`,
                right: `${-10 + i * 5}%`
              }}
              animate={{ 
                scale: [0, 1, 0],
                opacity: [0, 1, 0]
              }}
              transition={{ 
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.3
              }}
            />
          ))}
        </motion.div>
        
        {/* 标题 */}
        <motion.h1
          className="text-[24px] font-semibold text-center tracking-[-0.5px]"
          style={{ color: '#2B2735' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {title}
        </motion.h1>
        
        {/* 副标题 */}
        <motion.p
          className="mt-4 text-center text-[14px] leading-relaxed max-w-[280px]"
          style={{ color: '#999999' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {subtitle}
        </motion.p>
      </div>
      
      {/* 底部按钮 - 带图标的 CTA */}
      <motion.div
        className="px-5 py-6 space-y-3"
        style={{ background: '#F2F1F6' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Button 
          fullWidth 
          size="lg" 
          onClick={nextStep}
          icon={<ArrowRight className="w-5 h-5" />}
          iconPosition="right"
        >
          {config.softCommitText || "Let's go!"}
        </Button>
        
        {/* 可选的次要选项 */}
        <motion.p 
          className="text-center text-[12px]"
          style={{ color: '#999999' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          Takes less than 5 seconds
        </motion.p>
      </motion.div>
    </div>
  )
}

