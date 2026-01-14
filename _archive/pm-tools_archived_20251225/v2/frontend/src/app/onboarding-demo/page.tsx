'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { useOnboardingStore } from './store/onboarding-store'
import { useABTestStore, VERSION_INFO, FlowVersion } from './store/ab-test-store'
import { getScreenConfig, screensConfig } from './data/screens-config'
import { getScreenConfigV2, screensConfigV2 } from './data/screens-config-v2'
import { PhoneFrame } from './components/ui/PhoneFrame'
import { ScreenRenderer } from './components/screens'
import { 
  ChevronLeft, 
  ChevronRight, 
  RotateCcw, 
  Download,
  GitBranch,
  Check
} from 'lucide-react'

export default function OnboardingDemoPage() {
  const { 
    currentStep, 
    totalSteps, 
    nextStep, 
    prevStep, 
    goToStep,
    resetDemo,
    setTotalSteps,
    userData,
    results
  } = useOnboardingStore()
  
  const { currentVersion, setVersion } = useABTestStore()
  
  // 根据版本获取配置
  const currentConfig = currentVersion === 'v2' 
    ? getScreenConfigV2(currentStep) 
    : getScreenConfig(currentStep)
  
  const currentScreensConfig = currentVersion === 'v2' ? screensConfigV2 : screensConfig
  const currentTotalSteps = currentVersion === 'v2' ? 40 : 37
  
  // 版本切换时更新 totalSteps
  useEffect(() => {
    setTotalSteps(currentTotalSteps)
  }, [currentVersion, currentTotalSteps, setTotalSteps])
  
  // 版本切换处理
  const handleVersionChange = (version: FlowVersion) => {
    if (version !== currentVersion) {
      setVersion(version)
      resetDemo()
    }
  }
  
  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault()
        nextStep()
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        prevStep()
      } else if (e.key === 'r' || e.key === 'R') {
        resetDemo()
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [nextStep, prevStep, resetDemo])
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl" />
      </div>
      
      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* 头部 */}
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">VitaFlow Onboarding Demo</h1>
            <p className="text-gray-400 text-sm mt-1">
              Interactive prototype • {currentTotalSteps} screens • 
              <span className={currentVersion === 'v2' ? 'text-green-400' : 'text-purple-400'}>
                {' '}{VERSION_INFO[currentVersion].name}
              </span>
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* A/B Test 版本切换 */}
            <div className="flex items-center gap-1 bg-gray-800 rounded-xl p-1">
              {(['v1', 'v2'] as FlowVersion[]).map((version) => (
                <motion.button
                  key={version}
                  onClick={() => handleVersionChange(version)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    currentVersion === version
                      ? version === 'v2' 
                        ? 'bg-green-600 text-white' 
                        : 'bg-purple-600 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                  whileHover={{ scale: currentVersion !== version ? 1.02 : 1 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {currentVersion === version && <Check className="w-3 h-3" />}
                  {version.toUpperCase()}
                  <span className="text-xs opacity-70">({VERSION_INFO[version].pages}p)</span>
                </motion.button>
              ))}
            </div>
            
            <motion.button
              onClick={resetDemo}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-gray-300 rounded-xl hover:bg-gray-700 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </motion.button>
            
            <motion.button
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-500 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Download className="w-4 h-4" />
              Export
            </motion.button>
          </div>
        </header>
        
        {/* 主要内容 */}
        <div className="flex gap-8 justify-center">
          {/* 手机预览 */}
          <div className="flex-shrink-0">
            <PhoneFrame>
              <ScreenRenderer />
            </PhoneFrame>
            
            {/* 导航控制 */}
            <div className="flex items-center justify-center gap-4 mt-6">
              <motion.button
                onClick={prevStep}
                disabled={currentStep === 1}
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
                  currentStep === 1 
                    ? 'bg-gray-800 text-gray-600 cursor-not-allowed' 
                    : 'bg-gray-700 text-white hover:bg-gray-600'
                }`}
                whileHover={currentStep !== 1 ? { scale: 1.1 } : {}}
                whileTap={currentStep !== 1 ? { scale: 0.95 } : {}}
              >
                <ChevronLeft className="w-6 h-6" />
              </motion.button>
              
              <div className="text-center min-w-[100px]">
                <span className="text-white font-semibold">
                  {currentStep} / {totalSteps}
                </span>
                <p className="text-gray-500 text-xs mt-1">
                  {currentConfig?.type}
                </p>
              </div>
              
              <motion.button
                onClick={nextStep}
                disabled={currentStep === totalSteps}
                className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
                  currentStep === totalSteps 
                    ? 'bg-gray-800 text-gray-600 cursor-not-allowed' 
                    : 'bg-purple-600 text-white hover:bg-purple-500'
                }`}
                whileHover={currentStep !== totalSteps ? { scale: 1.1 } : {}}
                whileTap={currentStep !== totalSteps ? { scale: 0.95 } : {}}
              >
                <ChevronRight className="w-6 h-6" />
              </motion.button>
            </div>
          </div>
          
          {/* 侧边栏信息 */}
          <div className="w-80 space-y-6">
            {/* 当前屏幕信息 */}
            <div className="bg-gray-800/50 rounded-2xl p-6 backdrop-blur-sm">
              <h3 className="text-white font-semibold mb-4">Current Screen</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-gray-400 text-xs uppercase tracking-wide">Type</p>
                  <p className="text-white font-medium capitalize">{currentConfig?.type.replace('_', ' ')}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs uppercase tracking-wide">Title</p>
                  <p className="text-white font-medium">{currentConfig?.title}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs uppercase tracking-wide">Phase</p>
                  <p className="text-purple-400 font-medium capitalize">{currentConfig?.phase}</p>
                </div>
              </div>
            </div>
            
            {/* 用户数据摘要 */}
            <div className="bg-gray-800/50 rounded-2xl p-6 backdrop-blur-sm">
              <h3 className="text-white font-semibold mb-4">Collected Data</h3>
              <div className="space-y-2 text-sm">
                {userData.goal && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Goal</span>
                    <span className="text-white capitalize">{userData.goal.replace('_', ' ')}</span>
                  </div>
                )}
                {userData.gender && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Gender</span>
                    <span className="text-white capitalize">{userData.gender}</span>
                  </div>
                )}
                {userData.age && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Age</span>
                    <span className="text-white">{userData.age} years</span>
                  </div>
                )}
                {userData.currentWeight && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Current Weight</span>
                    <span className="text-white">{userData.currentWeight} kg</span>
                  </div>
                )}
                {userData.targetWeight && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Target Weight</span>
                    <span className="text-white">{userData.targetWeight} kg</span>
                  </div>
                )}
                {results && (
                  <>
                    <div className="border-t border-gray-700 my-3" />
                    <div className="flex justify-between">
                      <span className="text-gray-400">Daily Calories</span>
                      <span className="text-purple-400 font-semibold">{results.dailyCalories} kcal</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">BMI</span>
                      <span className="text-white">{results.bmi}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
            
            {/* 流程缩略图 */}
            <div className="bg-gray-800/50 rounded-2xl p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-semibold">Flow Overview</h3>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  currentVersion === 'v2' ? 'bg-green-500/20 text-green-400' : 'bg-purple-500/20 text-purple-400'
                }`}>
                  {VERSION_INFO[currentVersion].name}
                </span>
              </div>
              <div className="grid grid-cols-8 gap-1">
                {currentScreensConfig.map((screen) => (
                  <motion.button
                    key={screen.id}
                    onClick={() => goToStep(screen.id)}
                    className={`
                      aspect-square rounded-sm text-[8px] font-bold
                      ${currentStep === screen.id 
                        ? currentVersion === 'v2' ? 'bg-green-500 text-white' : 'bg-purple-500 text-white'
                        : screen.id < currentStep
                          ? currentVersion === 'v2' ? 'bg-green-500/30 text-green-300' : 'bg-purple-500/30 text-purple-300'
                          : 'bg-gray-700 text-gray-500 hover:bg-gray-600'
                      }
                    `}
                    whileHover={{ scale: 1.2 }}
                    whileTap={{ scale: 0.9 }}
                    title={`${screen.id}. ${screen.title}`}
                  >
                    {screen.id}
                  </motion.button>
                ))}
              </div>
              
              {/* 图例 */}
              <div className="flex items-center gap-4 mt-4 text-xs">
                <div className="flex items-center gap-1">
                  <div className={`w-3 h-3 rounded-sm ${currentVersion === 'v2' ? 'bg-green-500/30' : 'bg-purple-500/30'}`} />
                  <span className="text-gray-400">Completed</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className={`w-3 h-3 rounded-sm ${currentVersion === 'v2' ? 'bg-green-500' : 'bg-purple-500'}`} />
                  <span className="text-gray-400">Current</span>
                </div>
              </div>
            </div>
            
            {/* V2 改进说明 */}
            {currentVersion === 'v2' && (
              <motion.div 
                className="bg-green-500/10 border border-green-500/20 rounded-xl p-4"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <GitBranch className="w-4 h-4 text-green-400" />
                  <h4 className="text-green-400 text-sm font-medium">V2 优化要点</h4>
                </div>
                <ul className="space-y-1.5 text-xs text-gray-400">
                  {VERSION_INFO.v2.highlights.map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-green-400 mt-0.5">•</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
            
            {/* 键盘快捷键 */}
            <div className="bg-gray-800/30 rounded-xl p-4">
              <p className="text-gray-500 text-xs">
                <span className="text-gray-400">Shortcuts:</span>{' '}
                ← → Navigate • R Reset • Space Next
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}







