'use client'

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

// 用户在 Onboarding 中收集的所有数据
export interface UserData {
  // 姓名（用于个性化称呼）
  name: string | null
  
  // 基础目标
  goal: 'lose_weight' | 'build_muscle' | 'maintain_weight' | null
  
  // 个人信息
  gender: 'female' | 'male' | 'other' | null
  age: number | null
  
  // 身体数据
  currentWeight: number | null
  targetWeight: number | null
  height: number | null
  weeklyLossRate: 0.5 | 1 | 1.5 | null  // 每周减重速度 (kg)
  
  // 运动习惯
  activityLevel: 'sedentary' | 'light' | 'moderate' | 'active' | null
  workoutFrequency: 'rarely' | 'sometimes' | 'often' | null
  
  // 伏笔问题
  acquisitionChannel: string | null
  previousAppExperience: 'yes' | 'no' | null
  previousBarriers: string[] | null
  dietaryPreferences: string[] | null
  secondaryGoals: string[] | null
  
  // 权限
  healthKitConnected: boolean
  notificationsEnabled: boolean
  trackingAllowed: boolean
  
  // 其他
  referralCode: string | null
}

// 计算结果（基于用户数据）
export interface CalculatedResults {
  dailyCalories: number
  targetDate: string
  weeklyLoss: number
  bmi: number
  tdee: number
}

interface OnboardingState {
  // 当前步骤
  currentStep: number
  totalSteps: number
  
  // 用户数据
  userData: UserData
  
  // 计算结果
  results: CalculatedResults | null
  
  // 游戏状态
  scanGameCompleted: boolean
  spinAttempts: number
  discountWon: number | null
  
  // 付款状态
  paymentCompleted: boolean
  selectedPlan: 'weekly' | 'monthly' | 'yearly' | null
  
  // 动画控制
  direction: 1 | -1 // 1: forward, -1: backward
  
  // 手动导航标志（用于禁用自动跳转）
  isManualNavigation: boolean
  
  // Actions
  nextStep: () => void
  prevStep: () => void
  goToStep: (step: number) => void
  clearManualNavigation: () => void
  setUserData: <K extends keyof UserData>(key: K, value: UserData[K]) => void
  setResults: (results: CalculatedResults) => void
  completeScanGame: () => void
  spinWheel: () => number // 返回获得的折扣
  completePayment: (plan: 'weekly' | 'monthly' | 'yearly') => void
  resetDemo: () => void
  setTotalSteps: (total: number) => void  // A/B Test 用
}

const initialUserData: UserData = {
  name: null,
  goal: null,
  gender: null,
  age: null,
  currentWeight: null,
  targetWeight: null,
  height: null,
  weeklyLossRate: null,
  activityLevel: null,
  workoutFrequency: null,
  acquisitionChannel: null,
  previousAppExperience: null,
  previousBarriers: null,
  dietaryPreferences: null,
  secondaryGoals: null,
  healthKitConnected: false,
  notificationsEnabled: false,
  trackingAllowed: false,
  referralCode: null,
}

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set, get) => ({
      currentStep: 1,
      totalSteps: 37,
      userData: initialUserData,
      results: null,
      scanGameCompleted: false,
      spinAttempts: 0,
      discountWon: null,
      paymentCompleted: false,
      selectedPlan: null,
      direction: 1,
      isManualNavigation: false,
      
      nextStep: () => set((state) => ({
        currentStep: Math.min(state.currentStep + 1, state.totalSteps),
        direction: 1,
        isManualNavigation: false
      })),
      
      prevStep: () => set((state) => ({
        currentStep: Math.max(state.currentStep - 1, 1),
        direction: -1,
        isManualNavigation: false
      })),
      
      goToStep: (step) => set((state) => ({
        currentStep: Math.max(1, Math.min(step, state.totalSteps)),
        direction: step > state.currentStep ? 1 : -1,
        isManualNavigation: true // 标记为手动导航
      })),
      
      clearManualNavigation: () => set({ isManualNavigation: false }),
      
      setUserData: (key, value) => set((state) => ({
        userData: { ...state.userData, [key]: value }
      })),
      
      setResults: (results) => set({ results }),
      
      completeScanGame: () => set({ scanGameCompleted: true }),
      
      spinWheel: () => {
        const { spinAttempts } = get()
        let discount: number
        
        if (spinAttempts === 0) {
          // 第一次：故意不中大奖，给个小奖或"再试一次"
          const smallPrizes = [10, 15, 20, 0] // 0 表示"再试一次"
          discount = smallPrizes[Math.floor(Math.random() * smallPrizes.length)]
        } else {
          // 第二次：必中 50%
          discount = 50
        }
        
        set((state) => ({
          spinAttempts: state.spinAttempts + 1,
          discountWon: discount > 0 ? discount : state.discountWon
        }))
        
        return discount
      },
      
      completePayment: (plan) => set({
        paymentCompleted: true,
        selectedPlan: plan
      }),
      
      resetDemo: () => set({
        currentStep: 1,
        userData: initialUserData,
        results: null,
        scanGameCompleted: false,
        spinAttempts: 0,
        discountWon: null,
        paymentCompleted: false,
        selectedPlan: null,
        direction: 1,
        isManualNavigation: false
      }),
      
      setTotalSteps: (total) => set({ totalSteps: total })
    }),
    {
      name: 'vitaflow-onboarding-demo',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        currentStep: state.currentStep,
        userData: state.userData,
        results: state.results,
        scanGameCompleted: state.scanGameCompleted,
        spinAttempts: state.spinAttempts,
        discountWon: state.discountWon,
        paymentCompleted: state.paymentCompleted,
        selectedPlan: state.selectedPlan,
      })
    }
  )
)

// 计算用户的个性化结果
export function calculateResults(userData: UserData): CalculatedResults | null {
  const { currentWeight, targetWeight, height, age, gender, activityLevel } = userData
  
  if (!currentWeight || !height || !age || !gender || !activityLevel) {
    return null
  }
  
  // BMR 计算 (Mifflin-St Jeor 公式)
  let bmr: number
  if (gender === 'male') {
    bmr = 10 * currentWeight + 6.25 * height - 5 * age + 5
  } else {
    bmr = 10 * currentWeight + 6.25 * height - 5 * age - 161
  }
  
  // 活动系数
  const activityMultipliers = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    active: 1.725
  }
  
  const tdee = Math.round(bmr * activityMultipliers[activityLevel])
  
  // 计算每日目标卡路里
  let dailyCalories = tdee
  const weightDiff = (targetWeight || currentWeight) - currentWeight
  
  if (weightDiff < 0) {
    // 减重：每周减 0.5kg，需要每天赤字 550 卡
    dailyCalories = tdee - 550
  } else if (weightDiff > 0) {
    // 增重：每天增加 300-500 卡
    dailyCalories = tdee + 400
  }
  
  // 计算达到目标的预计日期
  const weeksNeeded = Math.abs(weightDiff) / 0.5
  const targetDate = new Date()
  targetDate.setDate(targetDate.getDate() + weeksNeeded * 7)
  
  // BMI
  const heightInM = height / 100
  const bmi = Math.round((currentWeight / (heightInM * heightInM)) * 10) / 10
  
  return {
    dailyCalories: Math.max(1200, Math.round(dailyCalories)),
    targetDate: targetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
    weeklyLoss: weightDiff < 0 ? 0.5 : (weightDiff > 0 ? 0.3 : 0),
    bmi,
    tdee
  }
}







