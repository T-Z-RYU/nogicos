'use client'

import { motion } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button } from '../ui/Button'

interface WelcomeScreenProps {
  config: ScreenConfig
}

export function WelcomeScreen({ config }: WelcomeScreenProps) {
  const { nextStep } = useOnboardingStore()
  
  return (
    <div className="h-full flex flex-col" style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>
      {/* 顶部装饰 - VitaFlow 风格 */}
      <div className="absolute top-0 left-0 right-0 h-40 overflow-hidden">
        <motion.div
          className="absolute top-4 left-8 w-32 h-32 rounded-full blur-2xl"
          style={{ background: 'rgba(43, 39, 53, 0.03)' }}
          animate={{ y: [0, 10, 0], opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 4, repeat: Infinity }}
        />
        <motion.div
          className="absolute top-12 right-4 w-24 h-24 rounded-full blur-2xl"
          style={{ background: 'rgba(43, 39, 53, 0.02)' }}
          animate={{ y: [0, -10, 0], opacity: [0.4, 0.6, 0.4] }}
          transition={{ duration: 3, repeat: Infinity, delay: 0.5 }}
        />
      </div>
      
      {/* 主要内容区 */}
      <div className="flex-1 flex flex-col items-center justify-center px-8">
        {/* 手机模型展示 AI 扫描 - VitaFlow 配色 */}
        <motion.div
          className="relative w-48 h-64 mb-8"
          initial={{ y: 40, opacity: 0, rotateY: -10 }}
          animate={{ y: 0, opacity: 1, rotateY: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{ perspective: '1000px' }}
        >
          {/* 手机边框 */}
          <div className="absolute inset-0 rounded-3xl shadow-2xl overflow-hidden" style={{ background: '#2B2735' }}>
            {/* 屏幕内容 - 模拟扫描 */}
            <div className="absolute inset-2 rounded-2xl overflow-hidden" style={{ background: '#F2F1F6' }}>
              {/* 食物图片区域 */}
              <div className="absolute inset-4 top-8 bottom-12 rounded-xl flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.8)' }}>
                {/* 食物 emoji */}
                <motion.span 
                  className="text-6xl"
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  🍔
                </motion.span>
                
                {/* 扫描框 - VitaFlow 颜色 */}
                <motion.div
                  className="absolute inset-4 border-2 rounded-xl"
                  style={{ borderColor: '#2B2735' }}
                  animate={{
                    borderColor: ['#2B2735', '#999999', '#2B2735']
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  {/* 扫描线 */}
                  <motion.div
                    className="absolute left-0 right-0 h-0.5"
                    style={{ background: 'linear-gradient(90deg, transparent, #2B2735, transparent)' }}
                    animate={{ top: ['0%', '100%', '0%'] }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  />
                </motion.div>
              </div>
              
              {/* 底部信息 */}
              <div className="absolute bottom-4 left-4 right-4">
                <motion.div 
                  className="bg-white rounded-lg p-2 shadow-lg text-xs"
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.5 }}
                >
                  <div className="font-semibold" style={{ color: '#2B2735' }}>Burger</div>
                  <div className="font-bold" style={{ color: '#2B2735' }}>540 kcal</div>
                </motion.div>
              </div>
            </div>
          </div>
          
          {/* 浮动标签 - VitaFlow 风格 */}
          <motion.div
            className="absolute -right-4 top-1/3 px-3 py-1.5 bg-white rounded-full shadow-lg text-xs font-semibold"
            style={{ color: '#2B2735' }}
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            ✨ AI Powered
          </motion.div>
        </motion.div>
        
        {/* 标题 - VitaFlow 样式 */}
        <motion.h1
          className="text-[24px] font-semibold text-center tracking-[-0.5px]"
          style={{ color: '#2B2735' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {config.title}
        </motion.h1>
        
        {/* 副标题 */}
        <motion.p
          className="mt-3 text-center text-[14px] leading-relaxed"
          style={{ color: '#999999' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          {config.subtitle}
        </motion.p>
      </div>
      
      {/* 底部按钮 - VitaFlow 样式 */}
      <motion.div
        className="px-5 pb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Button fullWidth size="lg" onClick={nextStep}>
          Get Started
        </Button>
        
        {/* 条款提示 */}
        <p className="mt-4 text-xs text-center" style={{ color: '#999999' }}>
          By continuing, you agree to our{' '}
          <span style={{ color: '#2B2735' }}>Terms</span> and{' '}
          <span style={{ color: '#2B2735' }}>Privacy Policy</span>
        </p>
      </motion.div>
    </div>
  )
}







