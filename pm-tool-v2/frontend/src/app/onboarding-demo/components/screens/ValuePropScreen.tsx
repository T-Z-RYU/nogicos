'use client'

import { motion } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button, BackButton, SkipButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'
import { Camera, Bell, Shield, Lock, Sparkles, ChartLine } from 'lucide-react'

interface ValuePropScreenProps {
  config: ScreenConfig
}

// 根据标题选择图标和颜色
function getValuePropConfig(title: string) {
  if (title.includes('Track meals') || title.includes('seconds')) {
    return {
      icon: Camera,
      color: 'from-purple-500 to-pink-500',
      bgColor: 'bg-purple-50',
      illustration: (
        <motion.div className="relative w-32 h-32">
          {/* 相机图标 */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-xl shadow-purple-500/30">
              <Camera className="w-12 h-12 text-white" />
            </div>
          </motion.div>
          
          {/* 扫描线 */}
          <motion.div
            className="absolute left-1/2 -translate-x-1/2 w-20 h-0.5 bg-gradient-to-r from-transparent via-white to-transparent"
            animate={{ top: ['20%', '80%', '20%'] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          
          {/* 浮动标签 */}
          <motion.div
            className="absolute -right-8 top-1/4 px-2 py-1 bg-white rounded-lg shadow-lg text-xs font-semibold text-purple-600"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            540 kcal
          </motion.div>
        </motion.div>
      )
    }
  }
  
  if (title.includes('Stay on track') || title.includes('reminders')) {
    return {
      icon: Bell,
      color: 'from-orange-500 to-yellow-500',
      bgColor: 'bg-orange-50',
      illustration: (
        <motion.div className="relative w-32 h-32">
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            animate={{ rotate: [0, -10, 10, 0] }}
            transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
          >
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-orange-500 to-yellow-500 flex items-center justify-center shadow-xl shadow-orange-500/30">
              <Bell className="w-12 h-12 text-white" />
            </div>
          </motion.div>
          
          {/* 通知气泡 */}
          <motion.div
            className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: 'spring' }}
          >
            3
          </motion.div>
        </motion.div>
      )
    }
  }
  
  if (title.includes('data is safe') || title.includes('safe')) {
    return {
      icon: Shield,
      color: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-50',
      illustration: (
        <motion.div className="relative w-32 h-32">
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
          >
            <motion.div 
              className="w-24 h-24 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-xl shadow-green-500/30"
              animate={{ scale: [1, 1.02, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <Shield className="w-12 h-12 text-white" />
            </motion.div>
          </motion.div>
          
          {/* 锁图标 */}
          <motion.div
            className="absolute -bottom-2 -right-2 w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-lg"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.4, type: 'spring' }}
          >
            <Lock className="w-5 h-5 text-green-600" />
          </motion.div>
        </motion.div>
      )
    }
  }
  
  if (title.includes('Track') && title.includes('Transform')) {
    return {
      icon: ChartLine,
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-50',
      illustration: (
        <motion.div className="relative w-32 h-32">
          <motion.div className="absolute inset-0 flex items-center justify-center">
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-xl shadow-blue-500/30">
              <ChartLine className="w-12 h-12 text-white" />
            </div>
          </motion.div>
          
          {/* 上升趋势线 */}
          <motion.svg
            className="absolute -right-4 top-0 w-16 h-16"
            viewBox="0 0 40 40"
          >
            <motion.path
              d="M5 30 Q 15 25, 20 15 T 35 5"
              fill="none"
              stroke="#10B981"
              strokeWidth="3"
              strokeLinecap="round"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1, delay: 0.3 }}
            />
          </motion.svg>
        </motion.div>
      )
    }
  }
  
  // 默认
  return {
    icon: Sparkles,
    color: 'from-purple-500 to-pink-500',
    bgColor: 'bg-purple-50',
    illustration: (
      <motion.div
        className="w-24 h-24 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-xl"
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <Sparkles className="w-12 h-12 text-white" />
      </motion.div>
    )
  }
}

export function ValuePropScreen({ config }: ValuePropScreenProps) {
  const { nextStep, prevStep, currentStep, totalSteps } = useOnboardingStore()
  
  const { illustration, bgColor } = getValuePropConfig(config.title)
  
  return (
    <div className={`h-full flex flex-col ${bgColor}`}>
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部导航 */}
      <div className="flex items-center justify-between px-6 py-2">
        <BackButton onClick={prevStep} />
        <SkipButton onClick={nextStep} />
      </div>
      
      {/* 主要内容 */}
      <div className="flex-1 flex flex-col items-center justify-center px-8">
        {/* 插图 */}
        <motion.div
          className="mb-12"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {illustration}
        </motion.div>
        
        {/* 标题 */}
        <motion.h1
          className="text-2xl font-bold text-gray-900 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {config.title}
        </motion.h1>
        
        {/* 副标题 */}
        <motion.p
          className="mt-4 text-gray-500 text-center text-sm leading-relaxed"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {config.subtitle}
        </motion.p>
      </div>
      
      {/* 底部按钮 */}
      <motion.div
        className="px-6 py-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Button fullWidth size="lg" onClick={nextStep}>
          Continue
        </Button>
      </motion.div>
    </div>
  )
}







