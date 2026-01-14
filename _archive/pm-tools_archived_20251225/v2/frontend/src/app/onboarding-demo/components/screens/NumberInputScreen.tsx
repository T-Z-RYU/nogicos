'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useOnboardingStore, UserData } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { NumberSlider } from '../ui/NumberPicker'
import { Button, BackButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'

interface NumberInputScreenProps {
  config: ScreenConfig
}

export function NumberInputScreen({ config }: NumberInputScreenProps) {
  const { userData, setUserData, nextStep, prevStep, currentStep, totalSteps } = useOnboardingStore()
  
  const storeKey = config.storeKey as keyof UserData | undefined
  const currentValue = storeKey ? (userData[storeKey] as number | null) : null
  const defaultVal = config.numberConfig?.defaultValue || 0
  
  const [value, setValue] = useState<number>(currentValue || defaultVal)
  
  const handleContinue = () => {
    if (storeKey) {
      setUserData(storeKey, value as never)
    }
    nextStep()
  }
  
  if (!config.numberConfig) {
    return <div>Missing number config</div>
  }
  
  const { min, max, step, unit } = config.numberConfig
  
  return (
    <div className="h-full flex flex-col" style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部导航 */}
      <div className="flex items-center justify-between px-5 py-2">
        <BackButton onClick={prevStep} />
        <div /> {/* Spacer */}
      </div>
      
      {/* 标题区域 - VitaFlow 样式 */}
      <div className="px-5 pt-4 pb-8">
        <motion.h1
          className="text-[24px] font-semibold text-center tracking-[-0.5px]"
          style={{ color: '#2B2735' }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {config.title}
        </motion.h1>
        
        {config.subtitle && (
          <motion.p
            className="mt-2 text-[14px] text-center"
            style={{ color: '#999999' }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            {config.subtitle}
          </motion.p>
        )}
      </div>
      
      {/* 数字选择器 */}
      <motion.div
        className="flex-1 flex items-center justify-center px-5"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <NumberSlider
          value={value}
          onChange={setValue}
          min={min}
          max={max}
          step={step}
          unit={unit}
        />
      </motion.div>
      
      {/* 底部按钮 - VitaFlow 样式 */}
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







