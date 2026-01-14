'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useOnboardingStore, calculateResults } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button, BackButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'
import { personalizeText } from '../../utils/personalize'

interface ResultScreenProps {
  config: ScreenConfig
}

// 动画计数组件
function AnimatedNumber({ value, suffix = '' }: { value: number; suffix?: string }) {
  const [displayValue, setDisplayValue] = useState(0)
  
  useEffect(() => {
    const duration = 1500
    const startTime = Date.now()
    
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // 缓动函数
      const easeOut = 1 - Math.pow(1 - progress, 3)
      setDisplayValue(Math.round(value * easeOut))
      
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    
    requestAnimationFrame(animate)
  }, [value])
  
  return <>{displayValue}{suffix}</>
}

export function ResultScreen({ config }: ResultScreenProps) {
  const { results, userData, nextStep, prevStep, currentStep, totalSteps, setResults } = useOnboardingStore()
  
  // 如果没有 results，自动计算（处理手动跳转的情况）
  useEffect(() => {
    if (!results) {
      const calculatedResults = calculateResults(userData)
      if (calculatedResults) {
        setResults(calculatedResults)
      }
    }
  }, [results, userData, setResults])
  
  // 个性化文本
  const title = config.usePersonalization ? personalizeText(config.title, userData.name) : config.title
  const subtitle = config.usePersonalization ? personalizeText(config.subtitle, userData.name) : config.subtitle
  
  // 使用计算的结果或临时默认值
  const displayResults = results || calculateResults(userData)
  
  if (!displayResults) {
    return (
      <div className="h-full flex items-center justify-center" style={{ background: '#F2F1F6' }}>
        <div className="text-center px-8">
          <p className="text-[16px] font-medium" style={{ color: '#2B2735' }}>Missing profile data</p>
          <p className="text-[14px] mt-2" style={{ color: '#999999' }}>Please complete your profile first</p>
        </div>
      </div>
    )
  }
  
  const weightDiff = (userData.targetWeight || 0) - (userData.currentWeight || 0)
  const isLosing = weightDiff < 0
  const isGaining = weightDiff > 0
  
  return (
    <div className="h-full flex flex-col" style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部导航 */}
      <div className="flex items-center justify-between px-5 py-2">
        <BackButton onClick={prevStep} />
        <div />
      </div>
      
      {/* 标题 - VitaFlow 样式 */}
      <div className="px-5 pt-4 pb-4">
        <motion.h1
          className="text-[24px] font-semibold tracking-[-0.5px]"
          style={{ color: '#2B2735' }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {title}
        </motion.h1>
        <motion.p
          className="mt-1 text-[14px]"
          style={{ color: '#999999' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          {subtitle}
        </motion.p>
      </div>
      
      {/* 结果卡片区域 - VitaFlow 样式 */}
      <div className="flex-1 px-5 pb-4 overflow-y-auto scrollbar-hide">
        {/* 主要目标卡片 - VitaFlow 深色 */}
        <motion.div
          className="relative overflow-hidden rounded-[20px] p-6 mb-4"
          style={{ background: '#2B2735' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {/* 背景装饰 */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/3 rounded-full translate-y-1/2 -translate-x-1/2" />
          
          <div className="relative z-10">
            <p className="text-white/70 text-[13px] font-medium">Your Daily Target</p>
            <div className="flex items-baseline mt-2">
              <span className="text-[48px] font-bold text-white">
                <AnimatedNumber value={displayResults.dailyCalories} />
              </span>
              <span className="text-white/70 ml-2 text-[18px]">kcal</span>
            </div>
            
            <div className="mt-4 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-400" />
              <p className="text-white/80 text-[13px]">
                {isLosing && `Lose ${Math.abs(weightDiff)}kg by ${displayResults.targetDate}`}
                {isGaining && `Gain ${Math.abs(weightDiff)}kg by ${displayResults.targetDate}`}
                {!isLosing && !isGaining && 'Maintain your current weight'}
              </p>
            </div>
          </div>
        </motion.div>
        
        {/* 详细数据网格 - VitaFlow 白色卡片 */}
        <div className="grid grid-cols-2 gap-3">
          {/* BMI */}
          <motion.div
            className="bg-white rounded-[16px] p-4"
            style={{ boxShadow: '0px 0px 2px 0px #E8E8E8' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <p className="text-[12px] font-medium" style={{ color: '#999999' }}>Your BMI</p>
            <p className="text-[24px] font-bold mt-1" style={{ color: '#2B2735' }}>
              <AnimatedNumber value={displayResults.bmi} />
            </p>
            <p className="text-[11px] mt-1" style={{ color: '#2B2735' }}>
              {displayResults.bmi < 18.5 ? 'Underweight' : 
               displayResults.bmi < 25 ? 'Normal' : 
               displayResults.bmi < 30 ? 'Overweight' : 'Obese'}
            </p>
          </motion.div>
          
          {/* TDEE */}
          <motion.div
            className="bg-white rounded-[16px] p-4"
            style={{ boxShadow: '0px 0px 2px 0px #E8E8E8' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
          >
            <p className="text-[12px] font-medium" style={{ color: '#999999' }}>Your TDEE</p>
            <p className="text-[24px] font-bold mt-1" style={{ color: '#2B2735' }}>
              <AnimatedNumber value={displayResults.tdee} />
            </p>
            <p className="text-[11px] mt-1" style={{ color: '#999999' }}>kcal/day</p>
          </motion.div>
          
          {/* 每周变化 */}
          <motion.div
            className="bg-white rounded-[16px] p-4"
            style={{ boxShadow: '0px 0px 2px 0px #E8E8E8' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <p className="text-[12px] font-medium" style={{ color: '#999999' }}>Weekly Change</p>
            <p className="text-[24px] font-bold mt-1" style={{ color: '#2B2735' }}>
              {isLosing ? '-' : isGaining ? '+' : ''}{displayResults.weeklyLoss}kg
            </p>
            <p className="text-[11px] mt-1 text-green-500">Healthy pace</p>
          </motion.div>
          
          {/* 目标日期 */}
          <motion.div
            className="bg-white rounded-[16px] p-4"
            style={{ boxShadow: '0px 0px 2px 0px #E8E8E8' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
          >
            <p className="text-[12px] font-medium" style={{ color: '#999999' }}>Goal Date</p>
            <p className="text-[18px] font-bold mt-1" style={{ color: '#2B2735' }}>
              {displayResults.targetDate}
            </p>
            <p className="text-[11px] mt-1" style={{ color: '#2B2735' }}>You got this! 💪</p>
          </motion.div>
        </div>
        
        {/* 激励文案 - VitaFlow 风格 */}
        <motion.div
          className="mt-6 p-4 bg-white rounded-[16px]"
          style={{ boxShadow: '0px 0px 2px 0px #E8E8E8' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-[13px] leading-relaxed" style={{ color: '#2B2735' }}>
            🌟 Based on your profile, this plan is designed for sustainable results. 
            Most users see visible changes within 2-4 weeks!
          </p>
        </motion.div>
      </div>
      
      {/* 底部按钮 - VitaFlow 样式 */}
      <motion.div
        className="px-5 py-6"
        style={{ background: '#F2F1F6' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Button fullWidth size="lg" onClick={nextStep}>
          Continue
        </Button>
      </motion.div>
    </div>
  )
}







