'use client'

import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { User } from 'lucide-react'
import { useOnboardingStore, UserData } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button, BackButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'

interface TextInputScreenProps {
  config: ScreenConfig
}

export function TextInputScreen({ config }: TextInputScreenProps) {
  const { userData, setUserData, nextStep, prevStep, currentStep, totalSteps } = useOnboardingStore()
  
  const storeKey = config.storeKey as keyof UserData | undefined
  const currentValue = storeKey ? (userData[storeKey] as string | null) : null
  
  const [value, setValue] = useState<string>(currentValue || '')
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  
  // 自动聚焦输入框
  useEffect(() => {
    const timer = setTimeout(() => {
      inputRef.current?.focus()
    }, 500)
    return () => clearTimeout(timer)
  }, [])
  
  const handleContinue = () => {
    if (value.trim() && storeKey) {
      setUserData(storeKey, value.trim() as never)
    }
    nextStep()
  }
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && value.trim()) {
      handleContinue()
    }
  }
  
  const isValid = value.trim().length > 0
  
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
      
      {/* 输入区域 */}
      <motion.div
        className="flex-1 flex flex-col items-center justify-center px-5"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        {/* 头像图标 - VitaFlow 风格 */}
        <motion.div
          className="w-20 h-20 rounded-full flex items-center justify-center mb-8"
          style={{ background: 'rgba(43, 39, 53, 0.08)' }}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ 
            type: "spring",
            stiffness: 200,
            damping: 15,
            delay: 0.3 
          }}
        >
          <User className="w-10 h-10" style={{ color: '#2B2735' }} />
        </motion.div>
        
        {/* 输入框 - VitaFlow 样式 */}
        <div className="w-full max-w-xs">
          <motion.div
            className="relative rounded-[16px] transition-all duration-300"
            style={{
              background: '#FFFFFF',
              boxShadow: isFocused 
                ? '0px 0px 0px 2px #2B2735, 0px 0px 8px rgba(43, 39, 53, 0.15)' 
                : '0px 0px 2px 0px #E8E8E8'
            }}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <input
              ref={inputRef}
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              onKeyDown={handleKeyDown}
              placeholder={config.textConfig?.placeholder || 'Enter your name'}
              maxLength={config.textConfig?.maxLength || 30}
              className="w-full px-4 py-4 text-[18px] text-center font-medium rounded-[16px] outline-none bg-transparent"
              style={{ color: '#2B2735' }}
              autoComplete="off"
              autoCorrect="off"
              spellCheck={false}
            />
          </motion.div>
          
          {/* 字数提示 */}
          <motion.p
            className="mt-2 text-[11px] text-center"
            style={{ color: '#999999' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {value.length} / {config.textConfig?.maxLength || 30}
          </motion.p>
        </div>
        
      </motion.div>
      
      {/* 底部按钮 - VitaFlow 样式 */}
      <motion.div
        className="px-5 py-6"
        style={{ background: '#F2F1F6' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Button 
          fullWidth 
          size="lg" 
          onClick={handleContinue}
          disabled={!isValid}
        >
          Continue
        </Button>
      </motion.div>
    </div>
  )
}

