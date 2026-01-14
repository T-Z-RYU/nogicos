// VitaFlow Onboarding 37页配置
// 基于竞品分析和最佳实践设计
// 更新: 添加减重速度选择、Referral Code、ATT权限；精简付费后流程

export type ScreenType = 
  | 'launch'
  | 'welcome'
  | 'question_single'
  | 'question_multi'
  | 'number_input'
  | 'text_input'  // 文本输入（姓名等）
  | 'value_prop'
  | 'loading'
  | 'result'
  | 'game_scan'
  | 'game_spin'
  | 'permission'
  | 'paywall'
  | 'celebration'
  | 'account'
  | 'transition'

export interface ScreenOption {
  id: string
  icon: string // lucide icon name 或 emoji
  title: string
  subtitle?: string
}

export interface ScreenConfig {
  id: number
  type: ScreenType
  title: string
  subtitle?: string
  storeKey?: string // 存储到 userData 的 key
  options?: ScreenOption[]
  numberConfig?: {
    min: number
    max: number
    unit: string
    step: number
    defaultValue: number
  }
  textConfig?: {
    placeholder: string
    maxLength?: number
  }
  autoAdvance?: boolean // 选择后自动前进
  skipButton?: boolean // 是否显示跳过按钮
  phase: string // 所属阶段
  usePersonalization?: boolean // 是否使用个性化称呼（{{name}} 占位符）
}

export const screensConfig: ScreenConfig[] = [
  // ============ Phase 1: 品牌建立 (P1-2) ============
  {
    id: 1,
    type: 'launch',
    title: 'VitaFlow',
    subtitle: 'Your AI Nutrition Companion',
    phase: 'brand',
    autoAdvance: true
  },
  {
    id: 2,
    type: 'welcome',
    title: 'Calorie tracking made easy',
    subtitle: 'Snap a photo. Get instant nutrition insights powered by AI.',
    phase: 'brand'
  },
  
  // ============ Phase 2: 姓名 + 目标设定 (P3-7) ============
  {
    id: 3,
    type: 'text_input',
    title: "What should we call you?",
    subtitle: "We'll use this to personalize your experience",
    storeKey: 'name',
    phase: 'goals',
    textConfig: {
      placeholder: 'Enter your name',
      maxLength: 30
    }
  },
  // Flo 风格的姓名欢迎过渡页
  {
    id: 4,
    type: 'transition',
    title: "Nice to meet you, {{name}}!",
    subtitle: "We're excited to be part of your health journey. Let's create a plan that works for you.",
    phase: 'goals',
    usePersonalization: true,
    autoAdvance: true
  },
  {
    id: 5,
    type: 'question_single',
    title: "What's your main goal?",
    storeKey: 'goal',
    phase: 'goals',
    options: [
      { id: 'lose_weight', icon: 'TrendingDown', title: 'Lose Weight', subtitle: 'Burn fat and feel lighter' },
      { id: 'build_muscle', icon: 'Dumbbell', title: 'Build Muscle', subtitle: 'Gain strength and mass' },
      { id: 'maintain_weight', icon: 'Scale', title: 'Maintain Weight', subtitle: 'Stay at your current level' }
    ],
    autoAdvance: true
  },
  {
    id: 6,
    type: 'question_single',
    title: "What's your biological sex?",
    subtitle: 'This helps us calculate your metabolism accurately',
    storeKey: 'gender',
    phase: 'goals',
    options: [
      { id: 'female', icon: 'Venus', title: 'Female' },
      { id: 'male', icon: 'Mars', title: 'Male' },
      { id: 'other', icon: 'CircleDot', title: 'Other / Prefer not to say' }
    ],
    autoAdvance: true
  },
  {
    id: 7,
    type: 'question_single',
    title: 'How active are you?',
    subtitle: 'Be honest for the best results',
    storeKey: 'activityLevel',
    phase: 'goals',
    options: [
      { id: 'sedentary', icon: 'Sofa', title: 'Sedentary', subtitle: 'Little to no exercise' },
      { id: 'light', icon: 'Footprints', title: 'Lightly Active', subtitle: '1-3 days/week' },
      { id: 'moderate', icon: 'Bike', title: 'Moderately Active', subtitle: '3-5 days/week' },
      { id: 'active', icon: 'Flame', title: 'Very Active', subtitle: '6-7 days/week' }
    ],
    autoAdvance: true
  },
  {
    id: 8,
    type: 'question_single',
    title: 'How often do you work out?',
    storeKey: 'workoutFrequency',
    phase: 'goals',
    options: [
      { id: 'rarely', icon: 'Moon', title: 'Rarely', subtitle: 'Workouts are not my thing yet' },
      { id: 'sometimes', icon: 'Sun', title: 'Sometimes', subtitle: 'A few times a month' },
      { id: 'often', icon: 'Zap', title: 'Regularly', subtitle: 'Multiple times a week' }
    ],
    autoAdvance: true
  },
  
  // ============ Phase 3: 过渡 + 身体数据 (P9-14) ============
  {
    id: 9,
    type: 'transition',
    title: "Great start, {{name}}! 🎯",
    subtitle: "Now let's personalize your plan with a few body measurements.",
    phase: 'biometrics',
    usePersonalization: true
  },
  {
    id: 10,
    type: 'number_input',
    title: 'How old are you?',
    storeKey: 'age',
    phase: 'biometrics',
    numberConfig: {
      min: 16,
      max: 100,
      unit: 'years',
      step: 1,
      defaultValue: 28
    }
  },
  {
    id: 11,
    type: 'number_input',
    title: "What's your current weight?",
    storeKey: 'currentWeight',
    phase: 'biometrics',
    numberConfig: {
      min: 40,
      max: 200,
      unit: 'kg',
      step: 0.5,
      defaultValue: 70
    }
  },
  {
    id: 12,
    type: 'number_input',
    title: "What's your goal weight?",
    storeKey: 'targetWeight',
    phase: 'biometrics',
    numberConfig: {
      min: 40,
      max: 200,
      unit: 'kg',
      step: 0.5,
      defaultValue: 65
    }
  },
  // 新增：减重速度选择
  {
    id: 13,
    type: 'question_single',
    title: 'How fast do you want to reach your goal?',
    subtitle: 'A slower pace is more sustainable long-term',
    storeKey: 'weeklyLossRate',
    phase: 'biometrics',
    options: [
      { id: '0.5', icon: 'Turtle', title: 'Slow & Steady', subtitle: '0.5 kg per week' },
      { id: '1', icon: 'Rabbit', title: 'Recommended', subtitle: '1 kg per week' },
      { id: '1.5', icon: 'Rocket', title: 'Aggressive', subtitle: '1.5 kg per week' }
    ],
    autoAdvance: true
  },
  {
    id: 14,
    type: 'transition',
    title: 'You can do it, {{name}}! 💪',
    subtitle: "Every journey begins with a single step. We'll help you get there.",
    phase: 'biometrics',
    usePersonalization: true
  },
  {
    id: 15,
    type: 'number_input',
    title: "What's your height?",
    storeKey: 'height',
    phase: 'biometrics',
    numberConfig: {
      min: 140,
      max: 220,
      unit: 'cm',
      step: 1,
      defaultValue: 170
    }
  },
  
  // ============ Phase 4: 伏笔问题 (P16-21) - 移到 Loading 之前 ============
  {
    id: 16,
    type: 'question_single',
    title: 'How did you hear about us?',
    storeKey: 'acquisitionChannel',
    phase: 'foreshadow',
    skipButton: true,
    options: [
      { id: 'social', icon: 'Instagram', title: 'Social Media' },
      { id: 'friend', icon: 'Users', title: 'Friend or Family' },
      { id: 'search', icon: 'Search', title: 'App Store Search' },
      { id: 'ad', icon: 'Megaphone', title: 'Advertisement' },
      { id: 'other', icon: 'MoreHorizontal', title: 'Other' }
    ],
    autoAdvance: true
  },
  {
    id: 17,
    type: 'question_single',
    title: 'Have you used a calorie tracking app before?',
    storeKey: 'previousAppExperience',
    phase: 'foreshadow',
    options: [
      { id: 'yes', icon: 'CheckCircle', title: 'Yes, I have' },
      { id: 'no', icon: 'Circle', title: "No, this is my first" }
    ],
    autoAdvance: true
  },
  {
    id: 18,
    type: 'question_multi',
    title: "What's stopped you from reaching your goals before?",
    storeKey: 'previousBarriers',
    phase: 'foreshadow',
    skipButton: true,
    options: [
      { id: 'time', icon: 'Clock', title: 'Not enough time' },
      { id: 'motivation', icon: 'Battery', title: 'Lost motivation' },
      { id: 'tracking', icon: 'ListTodo', title: 'Tracking was too tedious' },
      { id: 'knowledge', icon: 'BookOpen', title: "Didn't know what to eat" },
      { id: 'none', icon: 'Sparkles', title: 'Nothing — this is my first try!' }
    ]
  },
  {
    id: 19,
    type: 'question_multi',
    title: 'Any dietary preferences?',
    storeKey: 'dietaryPreferences',
    phase: 'foreshadow',
    skipButton: true,
    options: [
      { id: 'none', icon: 'Utensils', title: 'No restrictions' },
      { id: 'vegetarian', icon: 'Leaf', title: 'Vegetarian' },
      { id: 'vegan', icon: 'Vegan', title: 'Vegan' },
      { id: 'keto', icon: 'Beef', title: 'Keto / Low-carb' },
      { id: 'halal', icon: 'Moon', title: 'Halal' },
      { id: 'kosher', icon: 'Star', title: 'Kosher' }
    ]
  },
  {
    id: 20,
    type: 'question_multi',
    title: 'Any other goals you want to achieve?',
    storeKey: 'secondaryGoals',
    phase: 'foreshadow',
    skipButton: true,
    options: [
      { id: 'energy', icon: 'Zap', title: 'More energy' },
      { id: 'sleep', icon: 'Moon', title: 'Better sleep' },
      { id: 'skin', icon: 'Sparkles', title: 'Clearer skin' },
      { id: 'mood', icon: 'Smile', title: 'Improved mood' },
      { id: 'focus', icon: 'Brain', title: 'Better focus' }
    ]
  },
  {
    id: 21,
    type: 'text_input',
    title: 'Have a referral code?',
    subtitle: 'Enter it here to unlock special rewards',
    storeKey: 'referralCode',
    phase: 'foreshadow',
    skipButton: true,
    textConfig: {
      placeholder: 'Enter code (optional)',
      maxLength: 20
    }
  },
  
  // ============ Phase 5: Loading + 价值展示 (P22-27) ============
  {
    id: 22,
    type: 'loading',
    title: 'Analyzing your profile, {{name}}...',
    subtitle: 'Creating your personalized nutrition plan',
    phase: 'value',
    autoAdvance: true,
    usePersonalization: true
  },
  {
    id: 23,
    type: 'result',
    title: '{{name}}, your plan is ready!',
    subtitle: 'Based on your goals and body metrics',
    phase: 'value',
    usePersonalization: true
  },
  {
    id: 24,
    type: 'value_prop',
    title: 'Track meals in seconds',
    subtitle: 'Just snap a photo — our AI does the rest',
    phase: 'value'
  },
  {
    id: 25,
    type: 'value_prop',
    title: 'Stay on track effortlessly',
    subtitle: 'Smart reminders and progress insights keep you motivated',
    phase: 'value'
  },
  {
    id: 26,
    type: 'transition',
    title: "Let's try it, {{name}}! 📸",
    subtitle: 'Experience the magic of AI-powered food scanning',
    phase: 'value',
    usePersonalization: true
  },
  
  // ============ Phase 6: AI 扫描游戏 (P27) ============
  {
    id: 27,
    type: 'game_scan',
    title: 'Hold to Scan',
    subtitle: 'Press and hold to see AI nutrition analysis in action',
    phase: 'game'
  },
  
  // ============ Phase 7: 权限请求 (P28-31) ============
  {
    id: 28,
    type: 'permission',
    title: 'Connect Apple Health',
    subtitle: 'Sync your activity data for more accurate calorie calculations',
    storeKey: 'healthKitConnected',
    phase: 'permissions',
    skipButton: true
  },
  {
    id: 29,
    type: 'permission',
    title: 'Stay on track with reminders',
    subtitle: "We'll send gentle nudges to help you log your meals",
    storeKey: 'notificationsEnabled',
    phase: 'permissions',
    skipButton: true
  },
  // 新增：ATT 追踪权限请求
  {
    id: 30,
    type: 'permission',
    title: 'Help us improve VitaFlow',
    subtitle: 'Allow tracking to see personalized content and measure app improvements',
    storeKey: 'trackingAllowed',
    phase: 'permissions',
    skipButton: true
  },
  {
    id: 31,
    type: 'transition',
    title: "You're all set, {{name}}! 🎉",
    subtitle: 'Your personalized nutrition journey starts now',
    phase: 'permissions',
    usePersonalization: true
  },
  
  // ============ Phase 8: 付费墙 + 轮盘 (P32-34) - 精简版 ============
  {
    id: 32,
    type: 'paywall',
    title: '{{name}}, start your transformation',
    subtitle: 'Unlock all premium features',
    phase: 'conversion',
    usePersonalization: true
  },
  {
    id: 33,
    type: 'game_spin',
    title: "Wait, {{name}}! Here's a gift 🎁",
    subtitle: 'Spin the wheel for an exclusive discount',
    phase: 'conversion',
    usePersonalization: true
  },
  {
    id: 34,
    type: 'paywall',
    title: '🎉 50% OFF Unlocked!',
    subtitle: '{{name}}, claim your exclusive discount now',
    phase: 'conversion',
    usePersonalization: true
  },
  
  // ============ Phase 9: 成功 + 账号 (P35-37) - 精简版 ============
  {
    id: 35,
    type: 'celebration',
    title: 'Welcome to VitaFlow, {{name}}! 🎊',
    subtitle: 'Your transformation journey begins now',
    phase: 'success',
    usePersonalization: true
  },
  {
    id: 36,
    type: 'account',
    title: 'Create your account',
    subtitle: 'Sign in to sync your data across devices',
    phase: 'success'
  },
  {
    id: 37,
    type: 'celebration',
    title: "{{name}}, you're ready! 🚀",
    subtitle: 'Start tracking your first meal now',
    phase: 'success',
    usePersonalization: true
  }
]

// 获取当前屏幕配置
export function getScreenConfig(step: number): ScreenConfig | undefined {
  return screensConfig.find(s => s.id === step)
}

// 获取阶段进度
export function getPhaseProgress(currentStep: number): { phase: string; progress: number } {
  const current = getScreenConfig(currentStep)
  if (!current) return { phase: 'unknown', progress: 0 }
  
  const phaseScreens = screensConfig.filter(s => s.phase === current.phase)
  const indexInPhase = phaseScreens.findIndex(s => s.id === currentStep)
  
  return {
    phase: current.phase,
    progress: (indexInPhase + 1) / phaseScreens.length
  }
}







