// VitaFlow Onboarding V2 - 40页优化流程配置
// 基于深度竞品分析 + 心理学最佳实践设计
// 核心改进：
// 1. 问题节奏优化：避免连续4+问题，穿插鼓励页
// 2. 权限分散：Health > Notification > ATT 间隔6-8页
// 3. Value展示后加"软承诺"按钮，激活IKEA效应
// 4. 0-input页面控制：连续0-input不超过2页

export type ScreenType = 
  | 'launch'
  | 'welcome'
  | 'question_single'
  | 'question_multi'
  | 'number_input'
  | 'text_input'
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
  | 'soft_commit'  // 新增：软承诺页面

export interface ScreenOption {
  id: string
  icon: string
  title: string
  subtitle?: string
}

export interface ScreenConfig {
  id: number
  type: ScreenType
  title: string
  subtitle?: string
  storeKey?: string
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
  autoAdvance?: boolean
  skipButton?: boolean
  phase: string
  usePersonalization?: boolean
  // V2 新增字段
  softCommitText?: string  // 软承诺按钮文案
  animationType?: 'fade' | 'slide' | 'scale' | 'spring'  // 动画类型
}

export const screensConfigV2: ScreenConfig[] = [
  // ============ Phase 1: 品牌建立 (P1-2) ============
  {
    id: 1,
    type: 'launch',
    title: 'VitaFlow',
    subtitle: 'Your AI Nutrition Companion',
    phase: 'brand',
    autoAdvance: true,
    animationType: 'scale'
  },
  {
    id: 2,
    type: 'welcome',
    title: 'Calorie tracking made easy',
    subtitle: 'Snap a photo. Get instant nutrition insights powered by AI.',
    phase: 'brand',
    animationType: 'fade'
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
  {
    id: 4,
    type: 'transition',
    title: "Nice to meet you, {{name}}! 👋",
    subtitle: "We're excited to be part of your health journey. Let's create a plan that works for you.",
    phase: 'goals',
    usePersonalization: true,
    autoAdvance: true,
    animationType: 'spring'
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
  // P7: 鼓励过渡 - 打断2问后
  {
    id: 7,
    type: 'transition',
    title: "Great choice, {{name}}! 🎯",
    subtitle: "Your goal is totally achievable. Let's learn more about you.",
    phase: 'goals',
    usePersonalization: true,
    animationType: 'spring'
  },
  
  // ============ Phase 3: 活动习惯 (P8-10) ============
  {
    id: 8,
    type: 'question_single',
    title: 'How active are you?',
    subtitle: 'Be honest for the best results',
    storeKey: 'activityLevel',
    phase: 'habits',
    options: [
      { id: 'sedentary', icon: 'Sofa', title: 'Sedentary', subtitle: 'Little to no exercise' },
      { id: 'light', icon: 'Footprints', title: 'Lightly Active', subtitle: '1-3 days/week' },
      { id: 'moderate', icon: 'Bike', title: 'Moderately Active', subtitle: '3-5 days/week' },
      { id: 'active', icon: 'Flame', title: 'Very Active', subtitle: '6-7 days/week' }
    ],
    autoAdvance: true
  },
  {
    id: 9,
    type: 'question_single',
    title: 'How often do you work out?',
    storeKey: 'workoutFrequency',
    phase: 'habits',
    options: [
      { id: 'rarely', icon: 'Moon', title: 'Rarely', subtitle: 'Workouts are not my thing yet' },
      { id: 'sometimes', icon: 'Sun', title: 'Sometimes', subtitle: 'A few times a month' },
      { id: 'often', icon: 'Zap', title: 'Regularly', subtitle: 'Multiple times a week' }
    ],
    autoAdvance: true
  },
  // P10: 鼓励过渡
  {
    id: 10,
    type: 'transition',
    title: "Perfect! 💪",
    subtitle: "Now let's personalize your plan with a few body measurements.",
    phase: 'habits',
    usePersonalization: true,
    animationType: 'spring'
  },
  
  // ============ Phase 4: 身体数据 (P11-16) ============
  {
    id: 11,
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
    id: 12,
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
  {
    id: 13,
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
  // P14: 鼓励过渡（3个数字输入后）
  {
    id: 14,
    type: 'transition',
    title: "Almost there! ⏳",
    subtitle: "Just a couple more questions to build your perfect plan.",
    phase: 'biometrics',
    usePersonalization: true,
    animationType: 'spring'
  },
  {
    id: 15,
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
  {
    id: 16,
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
  // P17: 目标确认 (Cal AI 风格)
  {
    id: 17,
    type: 'transition',
    title: "You can do it, {{name}}! 🔥",
    subtitle: "Based on your goal, you could reach {{targetWeight}} kg by March 2026. Every journey begins with a single step.",
    phase: 'biometrics',
    usePersonalization: true,
    animationType: 'spring'
  },
  
  // ============ Phase 5: 第一个权限 - Health (P18) ============
  {
    id: 18,
    type: 'permission',
    title: 'Connect Apple Health',
    subtitle: 'Sync your activity data for more accurate calorie calculations',
    storeKey: 'healthKitConnected',
    phase: 'permission_health',
    skipButton: true
  },
  
  // ============ Phase 6: 伏笔问题 (P19-23) ============
  {
    id: 19,
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
    id: 20,
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
    id: 21,
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
  // P22: 共情过渡 (MFP 风格)
  {
    id: 22,
    type: 'transition',
    title: "We understand, {{name}} 💙",
    subtitle: "That's exactly why we built VitaFlow — to make tracking effortless.",
    phase: 'foreshadow',
    usePersonalization: true,
    animationType: 'spring'
  },
  {
    id: 23,
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
  
  // ============ Phase 7: 第二个权限 - Notification (P24-25) ============
  // P24: Notification 价值铺垫
  {
    id: 24,
    type: 'value_prop',
    title: 'Stay consistent with gentle reminders',
    subtitle: '89% of successful users enable notifications to build healthy habits',
    phase: 'permission_notification'
  },
  {
    id: 25,
    type: 'permission',
    title: 'Enable Reminders',
    subtitle: "We'll send gentle nudges to help you log your meals",
    storeKey: 'notificationsEnabled',
    phase: 'permission_notification',
    skipButton: true
  },
  
  // ============ Phase 8: 最后问题 + Referral (P26-27) ============
  {
    id: 26,
    type: 'question_multi',
    title: 'Any other goals you want to achieve?',
    storeKey: 'secondaryGoals',
    phase: 'extra',
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
    id: 27,
    type: 'text_input',
    title: 'Have a referral code?',
    subtitle: 'Enter it here to unlock special rewards',
    storeKey: 'referralCode',
    phase: 'extra',
    skipButton: true,
    textConfig: {
      placeholder: 'Enter code (optional)',
      maxLength: 20
    }
  },
  
  // ============ Phase 9: Loading + Result (P28-29) ============
  {
    id: 28,
    type: 'loading',
    title: 'Analyzing your profile, {{name}}...',
    subtitle: 'Creating your personalized nutrition plan',
    phase: 'value',
    autoAdvance: true,
    usePersonalization: true,
    animationType: 'fade'
  },
  {
    id: 29,
    type: 'result',
    title: '{{name}}, your plan is ready!',
    subtitle: 'Based on your goals and body metrics',
    phase: 'value',
    usePersonalization: true
  },
  
  // ============ Phase 10: Value 展示 + 软承诺 (P30-32) ============
  {
    id: 30,
    type: 'value_prop',
    title: 'Track meals in seconds',
    subtitle: 'Just snap a photo — our AI does the rest',
    phase: 'value'
  },
  // P31: 软承诺页面 - 解决连续0-input问题
  {
    id: 31,
    type: 'soft_commit',
    title: "Ready to start your journey?",
    subtitle: "Tap below to see how our AI technology works",
    phase: 'value',
    softCommitText: "Yes, show me! 📸",
    animationType: 'spring'
  },
  
  // ============ Phase 11: AI 扫描游戏 (P32) ============
  {
    id: 32,
    type: 'game_scan',
    title: 'Hold to Scan',
    subtitle: 'Press and hold to see AI nutrition analysis in action',
    phase: 'game'
  },
  
  // ============ Phase 12: 第三个权限 - ATT (P33-34) ============
  // P33: ATT 价值铺垫
  {
    id: 33,
    type: 'value_prop',
    title: 'Get personalized recommendations',
    subtitle: 'Allow tracking to see content tailored to your health goals',
    phase: 'permission_att'
  },
  {
    id: 34,
    type: 'permission',
    title: 'Help us improve VitaFlow',
    subtitle: 'Allow tracking to see personalized content and measure app improvements',
    storeKey: 'trackingAllowed',
    phase: 'permission_att',
    skipButton: true
  },
  
  // ============ Phase 13: 成功过渡 (P35) ============
  {
    id: 35,
    type: 'transition',
    title: "You're all set, {{name}}! 🎉",
    subtitle: 'Your personalized nutrition journey starts now',
    phase: 'pre_conversion',
    usePersonalization: true,
    animationType: 'spring'
  },
  
  // ============ Phase 14: 付费墙 + 轮盘 (P36-38) ============
  {
    id: 36,
    type: 'paywall',
    title: '{{name}}, start your transformation',
    subtitle: 'Unlock all premium features',
    phase: 'conversion',
    usePersonalization: true
  },
  {
    id: 37,
    type: 'game_spin',
    title: "Wait, {{name}}! Here's a gift 🎁",
    subtitle: 'Spin the wheel for an exclusive discount',
    phase: 'conversion',
    usePersonalization: true
  },
  {
    id: 38,
    type: 'paywall',
    title: '🎉 50% OFF Unlocked!',
    subtitle: '{{name}}, claim your exclusive discount now',
    phase: 'conversion',
    usePersonalization: true
  },
  
  // ============ Phase 15: 成功 + 账号 (P39-40) ============
  {
    id: 39,
    type: 'celebration',
    title: 'Welcome to VitaFlow, {{name}}! 🎊',
    subtitle: 'Your transformation journey begins now',
    phase: 'success',
    usePersonalization: true,
    animationType: 'spring'
  },
  {
    id: 40,
    type: 'account',
    title: 'Create your account',
    subtitle: 'Sign in to sync your data across devices',
    phase: 'success'
  }
]

// 获取当前屏幕配置
export function getScreenConfigV2(step: number): ScreenConfig | undefined {
  return screensConfigV2.find(s => s.id === step)
}

// 获取阶段进度
export function getPhaseProgressV2(currentStep: number): { phase: string; progress: number } {
  const current = getScreenConfigV2(currentStep)
  if (!current) return { phase: 'unknown', progress: 0 }
  
  const phaseScreens = screensConfigV2.filter(s => s.phase === current.phase)
  const indexInPhase = phaseScreens.findIndex(s => s.id === currentStep)
  
  return {
    phase: current.phase,
    progress: (indexInPhase + 1) / phaseScreens.length
  }
}

// V2 版本的流程特点摘要
export const V2_FLOW_SUMMARY = {
  totalPages: 40,
  questionPages: 16,
  valuePages: 6,
  transitionPages: 8,
  permissionPages: 3,
  gamePages: 2,
  conversionPages: 5,
  
  // 关键改进
  improvements: [
    '问题节奏：最多连续3问后必有过渡',
    '权限分散：Health(P18) → Notification(P25) → ATT(P34)，间隔7-9页',
    '软承诺设计：P31 加入按钮，打断连续0-input',
    '价值铺垫：每个权限前都有价值说明页',
    '个性化：全程使用 {{name}} 称呼'
  ]
}

