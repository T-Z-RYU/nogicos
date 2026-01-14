'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useOnboardingStore, UserData } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { OptionCard } from '../ui/OptionCard'
import { Button, BackButton, SkipButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'

interface QuestionSingleScreenProps {
  config: ScreenConfig
}

export function QuestionSingleScreen({ config }: QuestionSingleScreenProps) {
  const { userData, setUserData, nextStep, prevStep, currentStep, totalSteps } = useOnboardingStore()
  
  const storeKey = config.storeKey as keyof UserData | undefined
  const currentValue = storeKey ? userData[storeKey] : null
  const [selected, setSelected] = useState<string | null>(currentValue as string | null)
  
  // 自动前进逻辑
  useEffect(() => {
    if (config.autoAdvance && selected && selected !== currentValue) {
      // 保存数据
      if (storeKey) {
        setUserData(storeKey, selected as never)
      }
      
      // 延迟前进，让用户看到选中动画
      const timer = setTimeout(() => {
        nextStep()
      }, 400)
      
      return () => clearTimeout(timer)
    }
  }, [selected, config.autoAdvance, currentValue, storeKey, setUserData, nextStep])
  
  const handleSelect = (optionId: string) => {
    setSelected(optionId)
    
    if (!config.autoAdvance && storeKey) {
      setUserData(storeKey, optionId as never)
    }
  }
  
  const handleContinue = () => {
    if (storeKey && selected) {
      setUserData(storeKey, selected as never)
    }
    nextStep()
  }
  
  return (
    <div className="h-full flex flex-col" style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部导航 */}
      <div className="flex items-center justify-between px-5 py-2">
        <BackButton onClick={prevStep} />
        {config.skipButton && <SkipButton onClick={nextStep} />}
      </div>
      
      {/* 标题区域 - VitaFlow 样式 */}
      <div className="px-5 pt-4 pb-6">
        <motion.h1
          className="text-[24px] font-semibold tracking-[-0.5px]"
          style={{ color: '#2B2735' }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {config.title}
        </motion.h1>
        
        {config.subtitle && (
          <motion.p
            className="mt-2 text-[14px]"
            style={{ color: '#999999' }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            {config.subtitle}
          </motion.p>
        )}
      </div>
      
      {/* 选项列表 */}
      <div className="flex-1 px-5 overflow-y-auto scrollbar-hide pb-4">
        <div className="space-y-3">
          {config.options?.map((option, index) => (
            <OptionCard
              key={option.id}
              icon={option.icon}
              title={option.title}
              subtitle={option.subtitle}
              selected={selected === option.id}
              onClick={() => handleSelect(option.id)}
              index={index}
            />
          ))}
        </div>
      </div>
      
      {/* 底部按钮 - VitaFlow 深色按钮 */}
      <motion.div
        className="px-5 py-6"
        style={{ background: '#F2F1F6' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Button 
          fullWidth 
          size="lg" 
          onClick={handleContinue}
          disabled={!selected}
        >
          Continue
        </Button>
      </motion.div>
    </div>
  )
}







