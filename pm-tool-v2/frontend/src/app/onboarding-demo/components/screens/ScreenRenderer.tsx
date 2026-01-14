'use client'

import { AnimatePresence, motion } from 'framer-motion'
import { useOnboardingStore } from '../../store/onboarding-store'
import { useABTestStore } from '../../store/ab-test-store'
import { getScreenConfig } from '../../data/screens-config'
import { getScreenConfigV2 } from '../../data/screens-config-v2'

// 导入所有屏幕组件
import { LaunchScreen } from './LaunchScreen'
import { WelcomeScreen } from './WelcomeScreen'
import { QuestionSingleScreen } from './QuestionSingleScreen'
import { QuestionMultiScreen } from './QuestionMultiScreen'
import { NumberInputScreen } from './NumberInputScreen'
import { TextInputScreen } from './TextInputScreen'
import { TransitionScreen } from './TransitionScreen'
import { LoadingScreen } from './LoadingScreen'
import { ResultScreen } from './ResultScreen'
import { ValuePropScreen } from './ValuePropScreen'
import { ScanGameScreen } from './ScanGameScreen'
import { SpinGameScreen } from './SpinGameScreen'
import { PermissionScreen } from './PermissionScreen'
import { PaywallScreen } from './PaywallScreen'
import { CelebrationScreen } from './CelebrationScreen'
import { AccountScreen } from './AccountScreen'
import { SoftCommitScreen } from './SoftCommitScreen'

// 页面过渡动效
const pageVariants = {
  initial: (direction: number) => ({
    opacity: 0,
    x: direction > 0 ? 60 : -60,
    scale: 0.98
  }),
  animate: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.46, 0.45, 0.94]
    }
  },
  exit: (direction: number) => ({
    opacity: 0,
    x: direction > 0 ? -60 : 60,
    scale: 0.98,
    transition: {
      duration: 0.3,
      ease: [0.55, 0.085, 0.68, 0.53]
    }
  })
}

export function ScreenRenderer() {
  const { currentStep, direction } = useOnboardingStore()
  const { currentVersion } = useABTestStore()
  
  // 根据 A/B Test 版本选择配置
  const config = currentVersion === 'v2' 
    ? getScreenConfigV2(currentStep) 
    : getScreenConfig(currentStep)
  
  if (!config) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">Screen not found</p>
      </div>
    )
  }
  
  const renderScreen = () => {
    switch (config.type) {
      case 'launch':
        return <LaunchScreen config={config} />
      case 'welcome':
        return <WelcomeScreen config={config} />
      case 'question_single':
        return <QuestionSingleScreen config={config} />
      case 'question_multi':
        return <QuestionMultiScreen config={config} />
      case 'number_input':
        return <NumberInputScreen config={config} />
      case 'text_input':
        return <TextInputScreen config={config} />
      case 'transition':
        return <TransitionScreen config={config} />
      case 'loading':
        return <LoadingScreen config={config} />
      case 'result':
        return <ResultScreen config={config} />
      case 'value_prop':
        return <ValuePropScreen config={config} />
      case 'game_scan':
        return <ScanGameScreen config={config} />
      case 'game_spin':
        return <SpinGameScreen config={config} />
      case 'permission':
        return <PermissionScreen config={config} />
      case 'paywall':
        return <PaywallScreen config={config} />
      case 'celebration':
        return <CelebrationScreen config={config} />
      case 'account':
        return <AccountScreen config={config} />
      case 'soft_commit':
        return <SoftCommitScreen config={config as Parameters<typeof SoftCommitScreen>[0]['config']} />
      default:
        return <TransitionScreen config={config} />
    }
  }
  
  return (
    <AnimatePresence mode="wait" custom={direction}>
      <motion.div
        key={currentStep}
        custom={direction}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        className="h-full"
      >
        {renderScreen()}
      </motion.div>
    </AnimatePresence>
  )
}







