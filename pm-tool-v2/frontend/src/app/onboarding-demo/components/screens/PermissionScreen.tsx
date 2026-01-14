'use client'

import { motion } from 'framer-motion'
import { useOnboardingStore, UserData } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button, BackButton, SkipButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'
import { Heart, Bell, Activity } from 'lucide-react'

interface PermissionScreenProps {
  config: ScreenConfig
}

// 获取权限页面的配置
function getPermissionConfig(title: string) {
  if (title.includes('Apple Health') || title.includes('Health')) {
    return {
      icon: Heart,
      color: 'from-red-500 to-pink-500',
      benefits: [
        { icon: '🏃', text: 'Sync your steps and workouts' },
        { icon: '❤️', text: 'Track heart rate data' },
        { icon: '📊', text: 'More accurate calorie calculations' }
      ]
    }
  }
  
  if (title.includes('reminders') || title.includes('notifications')) {
    return {
      icon: Bell,
      color: 'from-orange-500 to-yellow-500',
      benefits: [
        { icon: '⏰', text: 'Meal logging reminders' },
        { icon: '🎯', text: 'Goal progress updates' },
        { icon: '💡', text: 'Personalized tips and insights' }
      ]
    }
  }
  
  return {
    icon: Activity,
    color: 'from-purple-500 to-pink-500',
    benefits: []
  }
}

export function PermissionScreen({ config }: PermissionScreenProps) {
  const { setUserData, nextStep, prevStep, currentStep, totalSteps } = useOnboardingStore()
  
  const { icon: Icon, color, benefits } = getPermissionConfig(config.title)
  const storeKey = config.storeKey as keyof UserData | undefined
  
  const handleAllow = () => {
    if (storeKey) {
      setUserData(storeKey, true as never)
    }
    nextStep()
  }
  
  const handleSkip = () => {
    if (storeKey) {
      setUserData(storeKey, false as never)
    }
    nextStep()
  }
  
  return (
    <div className="h-full flex flex-col bg-white">
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部导航 */}
      <div className="flex items-center justify-between px-6 py-2">
        <BackButton onClick={prevStep} />
        {config.skipButton && <SkipButton onClick={handleSkip} />}
      </div>
      
      {/* 主要内容 */}
      <div className="flex-1 flex flex-col items-center justify-center px-8">
        {/* 图标 */}
        <motion.div
          className={`w-24 h-24 rounded-3xl bg-gradient-to-br ${color} flex items-center justify-center shadow-xl mb-8`}
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
        >
          <Icon className="w-12 h-12 text-white" />
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
          className="mt-3 text-gray-500 text-center text-sm"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {config.subtitle}
        </motion.p>
        
        {/* 好处列表 */}
        {benefits.length > 0 && (
          <motion.div
            className="mt-8 w-full space-y-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {benefits.map((benefit, index) => (
              <motion.div
                key={index}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
              >
                <span className="text-xl">{benefit.icon}</span>
                <span className="text-sm text-gray-700">{benefit.text}</span>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
      
      {/* 底部按钮 */}
      <motion.div
        className="px-6 py-6 space-y-3"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Button fullWidth size="lg" onClick={handleAllow}>
          Allow Access
        </Button>
        <Button fullWidth size="lg" variant="ghost" onClick={handleSkip}>
          Maybe Later
        </Button>
      </motion.div>
    </div>
  )
}







