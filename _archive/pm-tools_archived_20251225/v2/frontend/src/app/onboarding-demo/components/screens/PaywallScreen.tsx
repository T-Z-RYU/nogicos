'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { ScreenConfig } from '../../data/screens-config'
import { Button, BackButton } from '../ui/Button'
import { ProgressBar } from '../ui/ProgressBar'
import { Check, Star, Zap, Shield } from 'lucide-react'
import { personalizeText } from '../../utils/personalize'

interface PaywallScreenProps {
  config: ScreenConfig
}

const plans = [
  {
    id: 'weekly',
    name: 'Weekly',
    price: 9.99,
    perWeek: 9.99,
    popular: false
  },
  {
    id: 'yearly',
    name: 'Yearly',
    price: 59.99,
    perWeek: 1.15,
    popular: true,
    savings: '88%'
  },
  {
    id: 'monthly',
    name: 'Monthly',
    price: 19.99,
    perWeek: 4.99,
    popular: false
  }
]

const features = [
  { icon: Zap, text: 'Unlimited AI food scans' },
  { icon: Star, text: 'Personalized meal plans' },
  { icon: Shield, text: 'Advanced progress analytics' }
]

export function PaywallScreen({ config }: PaywallScreenProps) {
  const { discountWon, completePayment, nextStep, prevStep, currentStep, totalSteps, userData } = useOnboardingStore()
  const [selectedPlan, setSelectedPlan] = useState<'weekly' | 'monthly' | 'yearly'>('yearly')
  
  const hasDiscount = discountWon && discountWon > 0
  const discountMultiplier = hasDiscount ? (100 - discountWon) / 100 : 1
  
  // 根据是否有折扣动态调整标题
  // 如果标题包含 "OFF" 或折扣相关词，但实际没有折扣，使用备用标题
  const rawTitle = config.usePersonalization ? personalizeText(config.title, userData.name) : config.title
  const rawSubtitle = config.usePersonalization ? personalizeText(config.subtitle, userData.name) : config.subtitle
  
  const isDiscountTitle = rawTitle?.includes('OFF') || rawTitle?.includes('%')
  const title = isDiscountTitle && !hasDiscount 
    ? personalizeText('{{name}}, start your transformation', userData.name)
    : rawTitle
  const subtitle = isDiscountTitle && !hasDiscount
    ? 'Unlock all premium features'
    : rawSubtitle
  
  const handleSubscribe = () => {
    completePayment(selectedPlan)
    // 跳过轮盘页面，直接到庆祝页
    // 根据当前步骤决定跳转
    nextStep()
  }
  
  const handleDecline = () => {
    // 如果还没有折扣，进入转盘页面
    if (!hasDiscount) {
      nextStep() // 去转盘
    } else {
      // 已有折扣，进入确认页面
      nextStep() // 去确认离开页
    }
  }
  
  return (
    <div className="h-full flex flex-col" style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>
      {/* 进度条 */}
      <ProgressBar current={currentStep} total={totalSteps} />
      
      {/* 头部 */}
      <div className="flex items-center justify-between px-5 py-2">
        <BackButton onClick={prevStep} />
        <div />
      </div>
      
      {/* 折扣标签 - VitaFlow 风格 */}
      {hasDiscount && (
        <motion.div
          className="mx-5 mb-4 p-3 rounded-[16px]"
          style={{ background: '#2B2735' }}
          initial={{ opacity: 0, y: -20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
        >
          <p className="text-white text-center font-bold text-[14px]">
            🎉 {discountWon}% OFF Applied!
          </p>
        </motion.div>
      )}
      
      {/* 标题 - VitaFlow 样式 */}
      <div className="px-5 pb-4">
        <motion.h1
          className="text-[24px] font-semibold text-center tracking-[-0.5px]"
          style={{ color: '#2B2735' }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {title}
        </motion.h1>
        <motion.p
          className="mt-2 text-center text-[14px]"
          style={{ color: '#999999' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          {subtitle}
        </motion.p>
      </div>
      
      {/* 功能列表 - VitaFlow 风格 */}
      <div className="px-5 mb-4">
        <div className="space-y-2">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="flex items-center gap-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
            >
              <div className="w-8 h-8 rounded-[10px] flex items-center justify-center" style={{ background: 'rgba(43, 39, 53, 0.08)' }}>
                <feature.icon className="w-4 h-4" style={{ color: '#2B2735' }} />
              </div>
              <span className="text-[14px]" style={{ color: '#2B2735' }}>{feature.text}</span>
            </motion.div>
          ))}
        </div>
      </div>
      
      {/* 价格选项 - VitaFlow 风格 */}
      <div className="flex-1 px-5 overflow-y-auto scrollbar-hide">
        <div className="space-y-3">
          {plans.map((plan, index) => {
            const finalPrice = (plan.price * discountMultiplier).toFixed(2)
            const finalPerWeek = (plan.perWeek * discountMultiplier).toFixed(2)
            
            return (
              <motion.button
                key={plan.id}
                onClick={() => setSelectedPlan(plan.id as 'weekly' | 'monthly' | 'yearly')}
                className="relative w-full p-4 rounded-[16px] text-left transition-all"
                style={{
                  background: '#FFFFFF',
                  boxShadow: selectedPlan === plan.id 
                    ? '0px 0px 0px 2px #2B2735, 0px 0px 8px rgba(43, 39, 53, 0.15)' 
                    : '0px 0px 2px 0px #E8E8E8'
                }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                whileTap={{ scale: 0.98 }}
              >
                {/* 推荐标签 - VitaFlow 风格 */}
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full" style={{ background: '#2B2735' }}>
                    <span className="text-[11px] font-bold text-white">BEST VALUE</span>
                  </div>
                )}
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-[15px]" style={{ color: '#2B2735' }}>{plan.name}</p>
                    <p className="text-[12px]" style={{ color: '#999999' }}>
                      ${finalPerWeek}/week
                    </p>
                  </div>
                  
                  <div className="text-right">
                    {hasDiscount && (
                      <p className="text-[12px] line-through" style={{ color: '#999999' }}>${plan.price}</p>
                    )}
                    <p className="text-[20px] font-bold" style={{ color: '#2B2735' }}>${finalPrice}</p>
                    {plan.savings && (
                      <p className="text-[11px] font-medium text-green-600">Save {plan.savings}</p>
                    )}
                  </div>
                  
                  {/* 选中指示器 - VitaFlow 风格 */}
                  <div 
                    className="ml-3 w-6 h-6 rounded-full border-2 flex items-center justify-center"
                    style={{
                      borderColor: selectedPlan === plan.id ? '#2B2735' : '#E8E8E8',
                      background: selectedPlan === plan.id ? '#2B2735' : 'transparent'
                    }}
                  >
                    {selectedPlan === plan.id && (
                      <Check className="w-4 h-4 text-white" />
                    )}
                  </div>
                </div>
              </motion.button>
            )
          })}
        </div>
      </div>
      
      {/* 底部按钮 - VitaFlow 风格 */}
      <motion.div
        className="px-5 py-4 space-y-3"
        style={{ background: '#F2F1F6' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Button fullWidth size="lg" onClick={handleSubscribe}>
          Start Free Trial
        </Button>
        
        <button
          onClick={handleDecline}
          className="w-full text-center text-[13px] py-2"
          style={{ color: '#999999' }}
        >
          {hasDiscount ? 'No thanks' : 'Not now'}
        </button>
        
        <p className="text-[11px] text-center" style={{ color: '#999999' }}>
          Cancel anytime. 7-day free trial, then {hasDiscount ? `$${(plans.find(p => p.id === selectedPlan)!.price * discountMultiplier).toFixed(2)}` : `$${plans.find(p => p.id === selectedPlan)?.price}`}/{selectedPlan}
        </p>
      </motion.div>
    </div>
  )
}







