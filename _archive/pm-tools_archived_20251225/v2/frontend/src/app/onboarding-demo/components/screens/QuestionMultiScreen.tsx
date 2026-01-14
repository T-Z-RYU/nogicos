'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useOnboardingStore, UserData } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { OptionCardMulti } from '../ui/OptionCard'
import { Button, BackButton, SkipButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'

interface QuestionMultiScreenProps {
  config: ScreenConfig
}

export function QuestionMultiScreen({ config }: QuestionMultiScreenProps) {
  const { userData, setUserData, nextStep, prevStep, currentStep, totalSteps } = useOnboardingStore()
  
  const storeKey = config.storeKey as keyof UserData | undefined
  const currentValue = (storeKey ? userData[storeKey] : null) as string[] | null
  const [selected, setSelected] = useState<string[]>(currentValue || [])
  
  const handleToggle = (optionId: string) => {
    setSelected(prev => {
      if (prev.includes(optionId)) {
        return prev.filter(id => id !== optionId)
      } else {
        return [...prev, optionId]
      }
    })
  }
  
  const handleContinue = () => {
    if (storeKey) {
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
      <div className="px-5 pt-4 pb-4">
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
        
        {/* 选中数量提示 - VitaFlow 样式 */}
        <motion.p
          className="mt-3 text-[12px] font-medium"
          style={{ color: '#2B2735' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Select all that apply ({selected.length} selected)
        </motion.p>
      </div>
      
      {/* 选项列表 */}
      <div className="flex-1 px-5 overflow-y-auto scrollbar-hide pb-4">
        <div className="space-y-2">
          {config.options?.map((option, index) => (
            <OptionCardMulti
              key={option.id}
              icon={option.icon}
              title={option.title}
              subtitle={option.subtitle}
              selected={selected.includes(option.id)}
              onClick={() => handleToggle(option.id)}
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
        >
          Continue
        </Button>
      </motion.div>
    </div>
  )
}







