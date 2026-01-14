'use client'

import { motion } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button, BackButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'

interface AccountScreenProps {
  config: ScreenConfig
}

export function AccountScreen({ config }: AccountScreenProps) {
  const { nextStep, prevStep, currentStep, totalSteps } = useOnboardingStore()
  
  const handleAppleSignIn = () => {
    // 模拟 Apple 登录
    nextStep()
  }
  
  const handleGoogleSignIn = () => {
    // 模拟 Google 登录
    nextStep()
  }
  
  return (
    <div className="h-full flex flex-col bg-white">
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部导航 */}
      <div className="flex items-center justify-between px-6 py-2">
        <BackButton onClick={prevStep} />
        <div />
      </div>
      
      {/* 主要内容 */}
      <div className="flex-1 flex flex-col items-center justify-center px-8">
        {/* 图标 */}
        <motion.div
          className="w-20 h-20 rounded-3xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-xl shadow-purple-500/30 mb-8"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
        >
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
            <circle cx="20" cy="14" r="8" stroke="white" strokeWidth="2.5" fill="none" />
            <path
              d="M6 34C6 26.268 12.268 20 20 20C27.732 20 34 26.268 34 34"
              stroke="white"
              strokeWidth="2.5"
              strokeLinecap="round"
              fill="none"
            />
          </svg>
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
        
        {/* 登录按钮 */}
        <motion.div
          className="w-full mt-12 space-y-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          {/* Apple 登录 */}
          <motion.button
            onClick={handleAppleSignIn}
            className="w-full h-14 bg-black text-white rounded-2xl font-semibold flex items-center justify-center gap-3 shadow-lg"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <svg width="20" height="24" viewBox="0 0 20 24" fill="currentColor">
              <path d="M19.665 17.811c-.456 1.004-.673 1.453-1.258 2.347-.817 1.249-1.97 2.804-3.4 2.817-1.27.013-1.598-.826-3.323-.814-1.725.01-2.086.83-3.358.816-1.428-.014-2.52-1.418-3.34-2.667C2.63 16.638 2.417 12.15 4.29 9.774c1.322-1.677 3.32-2.66 5.176-2.66 1.623 0 2.64.83 3.98.83 1.302 0 2.097-.832 3.974-.832 1.65 0 3.417.883 4.735 2.41-4.16 2.282-3.488 8.223.51 10.289zM14.25 4.56c.635-.816 1.118-1.97.995-3.14-1.08.074-2.343.758-3.08 1.647-.67.807-1.223 1.974-1.007 3.12 1.18.038 2.4-.662 3.092-1.627z" />
            </svg>
            <span>Continue with Apple</span>
          </motion.button>
          
          {/* Google 登录 */}
          <motion.button
            onClick={handleGoogleSignIn}
            className="w-full h-14 bg-white text-gray-700 rounded-2xl font-semibold flex items-center justify-center gap-3 border-2 border-gray-200 hover:border-gray-300 transition-colors"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            <span>Continue with Google</span>
          </motion.button>
        </motion.div>
        
        {/* 分隔线 */}
        <motion.div
          className="w-full flex items-center gap-4 my-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-sm text-gray-400">or</span>
          <div className="flex-1 h-px bg-gray-200" />
        </motion.div>
        
        {/* 邮箱注册提示 */}
        <motion.button
          className="text-purple-600 font-medium text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          onClick={nextStep}
        >
          Sign up with email instead
        </motion.button>
      </div>
      
      {/* 底部条款 */}
      <motion.div
        className="px-8 pb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
      >
        <p className="text-xs text-center text-gray-400 leading-relaxed">
          By continuing, you agree to our{' '}
          <span className="text-purple-500">Terms of Service</span> and{' '}
          <span className="text-purple-500">Privacy Policy</span>
        </p>
      </motion.div>
    </div>
  )
}







