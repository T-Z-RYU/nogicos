'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Sparkles, 
  RotateCcw,
  Download,
  ChevronLeft,
  FileJson,
  FileText,
  Zap,
  Star,
  Crown,
  Gem,
  Layers,
  Shield,
  Target,
  Heart,
  Swords,
  ExternalLink,
  Image as ImageIcon,
  Eye,
  HelpCircle,
  Info,
  X,
  BookOpen
} from 'lucide-react'

// 类型定义
interface PageOption {
  id: string
  type: string
  name: string
  purpose: string
  psychology: string[]
  ui_pattern: string
  copy: {
    headline: string
    subheadline: string | null
    cta: string | null
  }
  competitor_refs: string[]
  confidence: string
  research: string
  recommended: boolean
  reason: string
}

interface HealthInfo {
  score: number
  level: string
  issues: string[]
  warnings: string[]
}

interface NextOptions {
  current_index: number
  current_phase: string
  phase_name: string
  options: PageOption[]
  health: HealthInfo
  can_finish: boolean
  recommendation: string
}

interface SelectedPage {
  index: number
  id: string
  type: string
  name: string
  purpose: string
  psychology: string[]
  ui_pattern: string
  copy: {
    headline: string
    subheadline: string | null
    cta: string | null
  }
  competitor_refs: string[]
  confidence: string
}

// 类型颜色映射
const TYPE_COLORS: Record<string, string> = {
  W: '#3b82f6',
  A: '#8b5cf6',
  S: '#ec4899',
  Q: '#f59e0b',
  V: '#10b981',
  C: '#6366f1',
  G: '#eab308',
  L: '#64748b',
  R: '#14b8a6',
  X: '#f97316',
  D: '#06b6d4',
  P: '#ef4444',
}

const TYPE_NAMES: Record<string, string> = {
  W: 'Welcome',
  A: 'Authority',
  S: 'Social',
  Q: 'Question',
  V: 'Value',
  C: 'Commit',
  G: 'Gamified',
  L: 'Loading',
  R: 'Result',
  X: 'Permission',
  D: 'Demo',
  P: 'Paywall',
}

// 详细的页面类型说明 - 帮助用户理解每种类型的含义
const TYPE_DESCRIPTIONS: Record<string, {
  fullName: string
  shortDesc: string
  longDesc: string
  examples: string[]
  psychology: string
  whenToUse: string
  bestPractice: string
}> = {
  W: {
    fullName: '欢迎页 (Welcome)',
    shortDesc: '品牌第一印象',
    longDesc: '用户打开 App 后看到的第一批页面，用于建立品牌认知、传达核心价值主张、设定用户预期。通常包括启动页、价值介绍、流程说明等。',
    examples: ['品牌 Logo 启动页', '价值主张展示', '3步流程说明', '功能亮点轮播'],
    psychology: '首因效应 (Primacy Effect) - 第一印象会持续影响后续判断',
    whenToUse: 'Onboarding 开始时，用于快速传达"这是什么App"和"能给我带来什么价值"',
    bestPractice: '保持简洁，3秒内传达核心价值，避免过多文字'
  },
  A: {
    fullName: '权威背书 (Authority)',
    shortDesc: '建立专业信任',
    longDesc: '通过专家推荐、媒体报道、专业认证等方式建立信任。利用权威效应提升用户对产品的信任度。',
    examples: ['营养师/医生推荐', '媒体报道墙 (Forbes/TechCrunch)', '专业认证标识', '学术研究背书'],
    psychology: 'Cialdini 权威原则 - 人们倾向于相信专家和权威人士的建议',
    whenToUse: '在用户需要信任支撑时（如注册前、付费前），或产品涉及健康/金融等敏感领域',
    bestPractice: '使用真实可验证的背书，避免虚假宣传'
  },
  S: {
    fullName: '社会认同 (Social Proof)',
    shortDesc: '展示用户规模和评价',
    longDesc: '通过展示用户数量、评分、真实评价等方式，利用从众心理降低用户决策顾虑。',
    examples: ['500万+用户', '4.8★评分', '用户评价卡片', '成功案例展示', 'App Store排名'],
    psychology: '社会认同原理 + 从众效应 - 看到很多人在用会降低尝试门槛',
    whenToUse: '注册前或付费前，帮助用户克服"这个App靠谱吗"的顾虑',
    bestPractice: '使用真实数据，视频证言比文字效果更好(+34%转化)'
  },
  Q: {
    fullName: '问题收集 (Question)',
    shortDesc: '收集用户数据',
    longDesc: '通过问答方式收集用户信息，用于个性化推荐。这是 Onboarding 最核心的部分，直接影响个性化程度。',
    examples: ['目标选择(减重/增肌)', '性别/年龄/身高体重', '饮食偏好', '活动水平', '动机和挑战'],
    psychology: '承诺一致性原则 - 用户回答问题后会更倾向于完成注册',
    whenToUse: '建立信任后，开始收集个性化所需的数据',
    bestPractice: '每3-4个问题后插入价值页面(Q→Q→Q→V)，避免问卷疲劳'
  },
  V: {
    fullName: '价值展示 (Value)',
    shortDesc: '展示产品功能价值',
    longDesc: '在数据收集过程中穿插展示产品功能亮点，让用户了解"我的数据将如何被使用"以及"这个App能给我带来什么"。',
    examples: ['AI扫描功能演示', '个性化计划预览', '进度追踪功能', '食谱推荐', '社区功能'],
    psychology: '预期价值 - 让用户看到付出（填写问卷）的回报',
    whenToUse: '在连续问题后插入，缓解问卷疲劳，同时强化产品价值',
    bestPractice: '聚焦核心差异化功能，用动画/视觉增强吸引力'
  },
  C: {
    fullName: '承诺确认 (Commit)',
    shortDesc: '强化用户承诺',
    longDesc: '让用户明确确认自己的目标，利用承诺一致性原则提升后续完成率和留存率。',
    examples: ['目标确认页', '承诺宣言(长按确认)', '目标可视化', '里程碑预览'],
    psychology: '承诺一致性原则 - 公开承诺后人们更倾向于遵守',
    whenToUse: '数据收集完成后，正式"锁定"用户的目标',
    bestPractice: '使用交互式确认（如长按）增强承诺感'
  },
  G: {
    fullName: '游戏化 (Gamified)',
    shortDesc: '中途激励和成就',
    longDesc: '在较长的 Onboarding 流程中加入游戏化元素，维持用户动力，提供正向反馈。',
    examples: ['进度庆祝动画', '里程碑徽章', '完成奖励', '进度条/百分比'],
    psychology: '间歇强化 + 成就感 - 适时的正反馈维持动力',
    whenToUse: '长流程中期（如完成50%时），或关键节点后',
    bestPractice: '不要过度使用，避免显得幼稚或打断流程'
  },
  L: {
    fullName: '加载等待 (Loading)',
    shortDesc: '创造期待感',
    longDesc: '在生成个性化结果时展示加载动画，利用"Labor Illusion"让用户感受到系统正在为其专门处理。',
    examples: ['分析进度动画', '计划生成步骤', 'AI处理中', '数据计算动画'],
    psychology: 'Labor Illusion - 看到"工作过程"会让用户更珍惜结果',
    whenToUse: '在展示个性化结果前，即使实际计算很快也应展示',
    bestPractice: '展示具体步骤（如"计算热量目标→分析营养需求→生成计划"）'
  },
  R: {
    fullName: '结果展示 (Result)',
    shortDesc: '展示个性化结果',
    longDesc: '展示根据用户数据生成的个性化方案、目标、时间线等，这是数据收集的"回报"。',
    examples: ['专属计划概览', '每日热量目标', '营养配比', '预期时间线', '每周减重预测'],
    psychology: '即时满足 + 沉没成本 - 看到专属结果后不舍得放弃',
    whenToUse: '数据收集和加载后，作为价值的最终呈现',
    bestPractice: '强调"专为你定制"，使用具体数字而非模糊描述'
  },
  X: {
    fullName: '权限请求 (Permission)',
    shortDesc: '获取系统权限',
    longDesc: '请求推送通知、健康数据、位置等系统权限。正确的时机和说明方式对同意率影响巨大。',
    examples: ['推送通知权限', 'Apple Health连接', '位置权限', '相机权限'],
    psychology: '价值交换 - 说明权限能带来的好处，而非单纯请求',
    whenToUse: '在展示权限相关功能的价值后再请求',
    bestPractice: '使用预权限页说明价值后再触发系统弹窗(+34%同意率)'
  },
  D: {
    fullName: '功能演示 (Demo)',
    shortDesc: '展示产品界面和使用方法',
    longDesc: '让用户预览产品主界面、核心功能的使用方法，降低使用门槛，设定正确预期。',
    examples: ['主页预览', '扫描功能演示', '记录流程教学', '报告预览'],
    psychology: '渐进披露 + 预期设定 - 降低首次使用的认知负荷',
    whenToUse: '正式使用前，帮助用户建立"如何使用"的心智模型',
    bestPractice: '使用交互式演示而非纯展示，让用户动手尝试'
  },
  P: {
    fullName: '付费转化 (Paywall)',
    shortDesc: '订阅/付费转化',
    longDesc: '展示付费方案、价格、试用选项等，是 Onboarding 的最终转化环节。',
    examples: ['免费vs Pro对比', '定价方案卡片', '限时优惠', '试用说明'],
    psychology: '损失厌恶 + 锚定效应 + 稀缺性 - 多种心理策略的综合应用',
    whenToUse: '在用户充分了解价值后，通常在 Onboarding 末尾',
    bestPractice: '战略性放置可提升+234%转化，周订阅占市场55%'
  },
}

// 稀有度颜色（基于置信度）
const RARITY_STYLES: Record<string, { border: string; glow: string; badge: string; text: string }> = {
  '极高': { 
    border: 'border-yellow-500/80', 
    glow: 'shadow-yellow-500/30', 
    badge: 'bg-gradient-to-r from-yellow-600 to-amber-500',
    text: 'text-yellow-400'
  },
  '高': { 
    border: 'border-purple-500/80', 
    glow: 'shadow-purple-500/30', 
    badge: 'bg-gradient-to-r from-purple-600 to-violet-500',
    text: 'text-purple-400'
  },
  '中': { 
    border: 'border-blue-500/80', 
    glow: 'shadow-blue-500/30', 
    badge: 'bg-gradient-to-r from-blue-600 to-cyan-500',
    text: 'text-blue-400'
  },
}

// 稀有度图标
const RARITY_ICONS: Record<string, React.ReactNode> = {
  '极高': <Crown size={12} />,
  '高': <Gem size={12} />,
  '中': <Star size={12} />,
}

// 竞品截图映射 - 真实分析数据中的截图路径
const COMPETITOR_SCREENSHOTS: Record<string, { app: string; page: number; description: string }[]> = {
  // Welcome 类型
  'w_splash': [
    { app: 'Flo', page: 1, description: 'Flo 的品牌启动页，紫色渐变背景' },
    { app: 'Noom', page: 1, description: 'Noom 简洁的品牌 Logo 展示' },
    { app: 'MyFitnessPal', page: 1, description: 'MyFitnessPal 绿色品牌色' },
  ],
  'w_value_prop': [
    { app: 'Cal_AI', page: 2, description: 'Cal.AI 的 AI 扫描价值主张' },
    { app: 'Yazio', page: 2, description: 'Yazio 的功能亮点展示' },
  ],
  'w_how_it_works': [
    { app: 'Noom', page: 3, description: 'Noom 的 3 步流程说明' },
    { app: 'WeightWatchers', page: 2, description: 'WW 的简单开始引导' },
  ],
  // Authority 类型
  'a_expert': [
    { app: 'Noom', page: 5, description: 'Noom 营养师背书页面' },
    { app: 'WeightWatchers', page: 4, description: 'WW 专家团队展示' },
  ],
  'a_media': [
    { app: 'Flo', page: 4, description: 'Flo 的媒体报道墙' },
    { app: 'Cal_AI', page: 3, description: 'Cal.AI 的 App Store 精选' },
  ],
  // Social 类型
  's_user_count': [
    { app: 'Cal_AI', page: 5, description: 'Cal.AI 用户数量展示' },
    { app: 'Flo', page: 3, description: 'Flo 300M+ 用户展示' },
    { app: 'Noom', page: 4, description: 'Noom 的成功案例数字' },
  ],
  's_testimonial': [
    { app: 'Flo', page: 6, description: 'Flo 用户评价卡片' },
    { app: 'MacroFactor', page: 4, description: 'MacroFactor 用户证言' },
  ],
  's_rating': [
    { app: 'Cal_AI', page: 4, description: 'Cal.AI 4.8 星评分展示' },
    { app: 'Yazio', page: 3, description: 'Yazio App Store 评分' },
  ],
  // Question 类型
  'q_goal': [
    { app: 'Noom', page: 8, description: 'Noom 目标选择 - 单选卡片' },
    { app: 'Flo', page: 7, description: 'Flo 健康目标选择' },
    { app: 'MyFitnessPal', page: 5, description: 'MFP 主要目标页' },
  ],
  'q_gender': [
    { app: 'Yazio', page: 8, description: 'Yazio 性别二选一' },
    { app: 'Cal_AI', page: 10, description: 'Cal.AI 性别选择页' },
  ],
  'q_birthday': [
    { app: 'Flo', page: 12, description: 'Flo 日期选择器' },
    { app: 'Noom', page: 15, description: 'Noom 出生日期输入' },
  ],
  'q_height': [
    { app: 'MyFitnessPal', page: 12, description: 'MFP 身高滚轮选择器' },
    { app: 'LoseIt', page: 10, description: 'LoseIt 身高输入' },
  ],
  'q_weight': [
    { app: 'Yazio', page: 15, description: 'Yazio 体重滚轮' },
    { app: 'Cal_AI', page: 18, description: 'Cal.AI 体重输入' },
  ],
  'q_target_weight': [
    { app: 'Noom', page: 20, description: 'Noom 目标体重滑块' },
    { app: 'WeightWatchers', page: 15, description: 'WW 目标设定' },
  ],
  'q_activity': [
    { app: 'MyFitnessPal', page: 18, description: 'MFP 活动水平列表选择' },
    { app: 'Yazio', page: 20, description: 'Yazio 日常活动评估' },
  ],
  'q_diet_type': [
    { app: 'Yazio', page: 22, description: 'Yazio 饮食偏好卡片' },
    { app: 'Noom', page: 25, description: 'Noom 饮食方式选择' },
  ],
  // Value 类型
  'v_ai_scan': [
    { app: 'Cal_AI', page: 12, description: 'Cal.AI AI 扫描功能展示' },
    { app: 'Yazio', page: 18, description: 'Yazio 食物识别介绍' },
  ],
  'v_personalized': [
    { app: 'Noom', page: 22, description: 'Noom 个性化计划说明' },
    { app: 'WeightWatchers', page: 18, description: 'WW 定制方案介绍' },
  ],
  'v_progress': [
    { app: 'MyFitnessPal', page: 25, description: 'MFP 进度图表预览' },
    { app: 'LoseIt', page: 20, description: 'LoseIt 数据可视化' },
  ],
  // Loading 类型
  'l_analyzing': [
    { app: 'Cal_AI', page: 30, description: 'Cal.AI 分析动画' },
    { app: 'Noom', page: 35, description: 'Noom 计算中进度条' },
  ],
  'l_generating': [
    { app: 'Flo', page: 28, description: 'Flo 计划生成步骤展示' },
    { app: 'WeightWatchers', page: 25, description: 'WW 方案生成动画' },
  ],
  // Result 类型
  'r_plan_overview': [
    { app: 'Noom', page: 38, description: 'Noom 计划概览卡片' },
    { app: 'Cal_AI', page: 35, description: 'Cal.AI 个性化结果' },
  ],
  'r_calorie_goal': [
    { app: 'MyFitnessPal', page: 30, description: 'MFP 热量目标大数字展示' },
    { app: 'LoseIt', page: 28, description: 'LoseIt 卡路里预算' },
  ],
  // Permission 类型
  'x_notification': [
    { app: 'Flo', page: 35, description: 'Flo 通知权限预请求' },
    { app: 'Noom', page: 42, description: 'Noom 推送权限说明' },
  ],
  'x_health': [
    { app: 'MyFitnessPal', page: 35, description: 'MFP Apple Health 连接' },
    { app: 'LoseIt', page: 32, description: 'LoseIt 健康数据同步' },
  ],
  // Paywall 类型
  'p_comparison': [
    { app: 'Yazio', page: 35, description: 'Yazio 免费 vs Pro 对比' },
    { app: 'Flo', page: 38, description: 'Flo 功能对比表' },
  ],
  'p_pricing': [
    { app: 'Cal_AI', page: 40, description: 'Cal.AI 定价卡片' },
    { app: 'Noom', page: 50, description: 'Noom 订阅方案' },
  ],
}

const API_BASE = 'http://localhost:8002/api'

export default function BuilderPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [nextOptions, setNextOptions] = useState<NextOptions | null>(null)
  const [selectedPages, setSelectedPages] = useState<SelectedPage[]>([])
  const [showExport, setShowExport] = useState(false)
  // 关键修复：使用索引而不是 option.id 作为 hover 状态标识
  const [hoveredCardIndex, setHoveredCardIndex] = useState<number | null>(null)
  const [selectingCard, setSelectingCard] = useState<string | null>(null)
  const [showDeck, setShowDeck] = useState(false)
  // 新增：详情面板状态
  const [detailOption, setDetailOption] = useState<PageOption | null>(null)
  // 新增：类型说明面板
  const [showTypeGuide, setShowTypeGuide] = useState(false)
  // 新增：竞品截图预览（支持大图展示）
  const [screenshotPreview, setScreenshotPreview] = useState<{ app: string; page: number; description?: string } | null>(null)

  const startBuilder = useCallback(async () => {
    setIsLoading(true)
    setHoveredCardIndex(null) // 重置 hover 状态
    try {
      const res = await fetch(`${API_BASE}/builder/start`)
      const data = await res.json()
      setNextOptions(data.next)
      setSelectedPages([])
    } catch (err) {
      console.error('Failed to start builder:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const selectOption = async (optionId: string) => {
    setSelectingCard(optionId)
    setHoveredCardIndex(null) // 选择时清除 hover
    
    // 选择动画
    await new Promise(resolve => setTimeout(resolve, 300))
    
    try {
      const res = await fetch(`${API_BASE}/builder/select/${optionId}`, {
        method: 'POST',
      })
      const data = await res.json()
      
      if (data.success) {
        setSelectedPages(prev => [...prev, data.selected])
        setNextOptions(data.next)
      }
    } catch (err) {
      console.error('Failed to select option:', err)
    } finally {
      setSelectingCard(null)
    }
  }

  const undoSelection = async () => {
    try {
      const res = await fetch(`${API_BASE}/builder/undo`, {
        method: 'POST',
      })
      const data = await res.json()
      
      if (data.success) {
        setSelectedPages(prev => prev.slice(0, -1))
        setNextOptions(data.next)
      }
    } catch (err) {
      console.error('Failed to undo:', err)
    }
  }

  const exportPlan = async (format: 'json' | 'markdown') => {
    try {
      const res = await fetch(`${API_BASE}/builder/export`)
      const data = await res.json()
      
      let content: string
      let filename: string
      let mimeType: string
      
      if (format === 'json') {
        content = JSON.stringify(data, null, 2)
        filename = 'vitaflow-onboarding-plan.json'
        mimeType = 'application/json'
      } else {
        content = generateMarkdown(data)
        filename = 'vitaflow-onboarding-plan.md'
        mimeType = 'text/markdown'
      }
      
      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
      setShowExport(false)
    } catch (err) {
      console.error('Failed to export:', err)
    }
  }

  const generateMarkdown = (data: any): string => {
    let md = `# ${data.title}\n\n`
    md += `> ${data.source}\n\n`
    md += `**总页数**: ${data.total_pages}\n`
    md += `**健康度**: ${data.health_score?.score || 0}%\n\n`
    md += `---\n\n## 页面序列\n\n`
    
    for (const page of data.pages) {
      md += `### ${page.index}. [${page.type}] ${page.name}\n\n`
      md += `- **目的**: ${page.purpose}\n`
      md += `- **心理策略**: ${page.psychology?.join(', ') || ''}\n`
      md += `- **UI 模式**: ${page.ui_pattern}\n`
      md += `- **竞品参考**: ${page.competitor_refs?.join(', ') || ''}\n\n`
    }
    
    return md
  }

  // 获取竞品截图信息
  const getCompetitorScreenshots = (optionId: string) => {
    return COMPETITOR_SCREENSHOTS[optionId] || []
  }

  useEffect(() => {
    startBuilder()
  }, [startBuilder])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black flex items-center justify-center">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <Sparkles className="w-16 h-16 text-purple-500 mx-auto mb-4" />
          </motion.div>
          <p className="text-gray-400 text-lg">正在洗牌...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-900 to-black text-white overflow-hidden">
      {/* 背景装饰 */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
      </div>

      {/* 顶部 HUD */}
      <div className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* 左侧：标题 + 进度 */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Swords size={24} />
              </div>
              <div>
                <h1 className="text-xl font-bold">Onboarding 构建器</h1>
                <p className="text-gray-500 text-sm">选择你的卡牌，构建完美流程</p>
              </div>
            </div>
            
            {/* 当前阶段 */}
            {nextOptions && (
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-800/50 rounded-full border border-gray-700">
                <Target size={16} className="text-purple-400" />
                <span className="text-sm">
                  <span className="text-gray-400">第 {nextOptions.current_index} 回合</span>
                  <span className="mx-2 text-gray-600">·</span>
                  <span className="text-purple-400">{nextOptions.phase_name}</span>
                </span>
              </div>
            )}
          </div>

          {/* 右侧：操作按钮 */}
          <div className="flex items-center gap-3">
            {/* 类型说明按钮 */}
            <button
              onClick={() => setShowTypeGuide(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800/50 hover:bg-gray-700/50 rounded-full border border-gray-700 transition-colors"
              title="查看页面类型详细说明"
            >
              <BookOpen size={16} className="text-cyan-400" />
              <span className="text-sm">类型说明</span>
            </button>

            {/* 健康度 */}
            {nextOptions?.health && (
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-800/50 rounded-full border border-gray-700">
                <Heart size={16} className={
                  nextOptions.health.score >= 80 ? 'text-green-400' :
                  nextOptions.health.score >= 60 ? 'text-yellow-400' : 'text-red-400'
                } />
                <span className="text-sm font-medium">{nextOptions.health.score}%</span>
              </div>
            )}

            <button
              onClick={startBuilder}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800/50 hover:bg-gray-700/50 rounded-full border border-gray-700 transition-colors"
            >
              <RotateCcw size={16} />
              <span className="text-sm">重开</span>
            </button>
            
            <div className="relative">
              <button
                onClick={() => setShowExport(!showExport)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-full transition-all"
              >
                <Download size={16} />
                <span className="text-sm font-medium">导出</span>
              </button>
              
              <AnimatePresence>
                {showExport && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    className="absolute right-0 mt-2 bg-gray-800 rounded-xl shadow-xl overflow-hidden z-20 border border-gray-700"
                  >
                    <button
                      onClick={() => exportPlan('json')}
                      className="flex items-center gap-2 px-4 py-3 hover:bg-gray-700 w-full text-left"
                    >
                      <FileJson size={16} className="text-blue-400" />
                      <span className="text-sm">JSON</span>
                    </button>
                    <button
                      onClick={() => exportPlan('markdown')}
                      className="flex items-center gap-2 px-4 py-3 hover:bg-gray-700 w-full text-left"
                    >
                      <FileText size={16} className="text-green-400" />
                      <span className="text-sm">Markdown</span>
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>

      {/* 主体区域 */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-8">
        {/* 推荐提示 */}
        {nextOptions?.recommendation && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 flex items-center gap-2 px-4 py-2 bg-yellow-500/10 border border-yellow-500/30 rounded-full"
          >
            <Zap size={16} className="text-yellow-400" />
            <span className="text-sm text-yellow-300">{nextOptions.recommendation}</span>
          </motion.div>
        )}

        {/* 卡牌选择区 */}
        {nextOptions && (
          <div className="flex items-start justify-center gap-6">
            {nextOptions.options.map((option, idx) => {
              const rarity = RARITY_STYLES[option.confidence] || RARITY_STYLES['中']
              // 关键修复：使用索引判断 hover 状态
              const isHovered = hoveredCardIndex === idx
              const isSelecting = selectingCard === option.id
              const screenshots = getCompetitorScreenshots(option.id)
              
              return (
                <motion.div
                  key={`card-${idx}`}
                  initial={{ opacity: 0, y: 50, rotateY: -180 }}
                  animate={{ 
                    opacity: isSelecting ? 0 : 1, 
                    y: isSelecting ? -100 : 0,
                    rotateY: 0,
                    scale: isHovered ? 1.05 : 1,
                    zIndex: isHovered ? 10 : 1,
                  }}
                  transition={{ 
                    delay: idx * 0.1,
                    type: "spring",
                    stiffness: 200,
                    damping: 20
                  }}
                  // 关键修复：使用 onMouseEnter/Leave 替代 onHoverStart/End
                  onMouseEnter={() => setHoveredCardIndex(idx)}
                  onMouseLeave={() => setHoveredCardIndex(null)}
                  className={`
                    relative w-72 cursor-pointer
                    ${isHovered ? 'shadow-2xl ' + rarity.glow : ''}
                  `}
                  style={{ perspective: '1000px' }}
                >
                  {/* 卡牌主体 */}
                  <div className={`
                    relative bg-gradient-to-b from-gray-800 to-gray-900 
                    rounded-2xl border-2 ${rarity.border}
                    overflow-hidden transition-all duration-300
                    ${isHovered ? 'shadow-lg' : ''}
                  `}>
                    {/* 推荐标识 */}
                    {option.recommended && (
                      <div className="absolute -top-1 -right-1 z-10">
                        <div className="bg-gradient-to-r from-yellow-500 to-amber-500 text-black text-xs font-bold px-3 py-1 rounded-bl-xl rounded-tr-xl flex items-center gap-1">
                          <Crown size={12} />
                          推荐
                        </div>
                      </div>
                    )}

                    {/* 卡牌顶部：类型标识 */}
                    <div 
                      className="h-24 flex items-center justify-center relative"
                      style={{ 
                        background: `linear-gradient(135deg, ${TYPE_COLORS[option.type]}40 0%, ${TYPE_COLORS[option.type]}10 100%)`
                      }}
                    >
                      {/* 类型图标大背景 */}
                      <div 
                        className="absolute inset-0 flex items-center justify-center opacity-20"
                        style={{ color: TYPE_COLORS[option.type] }}
                      >
                        <span className="text-7xl font-black">{option.type}</span>
                      </div>
                      
                      {/* 类型徽章 */}
                      <div 
                        className="relative z-10 w-14 h-14 rounded-xl flex flex-col items-center justify-center text-white shadow-lg"
                        style={{ backgroundColor: TYPE_COLORS[option.type] }}
                      >
                        <span className="text-xl font-black">{option.type}</span>
                        <span className="text-[9px] opacity-80">{TYPE_NAMES[option.type]}</span>
                      </div>
                    </div>

                    {/* 卡牌内容 */}
                    <div className="p-4">
                      {/* 稀有度 */}
                      <div className="flex items-center justify-between mb-2">
                        <div className={`flex items-center gap-1 text-xs ${rarity.text}`}>
                          {RARITY_ICONS[option.confidence]}
                          <span>{option.confidence}</span>
                        </div>
                        {screenshots.length > 0 && (
                          <div className="flex items-center gap-1 text-xs text-gray-500">
                            <ImageIcon size={10} />
                            <span>{screenshots.length} 参考</span>
                          </div>
                        )}
                      </div>

                      {/* 名称 */}
                      <h3 className="text-lg font-bold mb-1">{option.name}</h3>
                      
                      {/* 描述 */}
                      <p className="text-gray-400 text-sm mb-3 line-clamp-2">{option.purpose}</p>

                      {/* 心理策略标签 */}
                      <div className="flex flex-wrap gap-1 mb-3">
                        {option.psychology.slice(0, 2).map((p, i) => (
                          <span 
                            key={i} 
                            className="text-xs px-2 py-0.5 bg-gray-700/50 rounded text-gray-300"
                          >
                            {p}
                          </span>
                        ))}
                      </div>

                      {/* 展开详情 - 悬浮时显示 */}
                      <AnimatePresence>
                        {isHovered && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.2 }}
                            className="border-t border-gray-700 pt-3 mt-3"
                          >
                            <div className="text-xs space-y-3">
                              {/* UI 模式 */}
                              <div>
                                <span className="text-gray-500 block mb-1">UI 模式</span>
                                <p className="text-gray-300 bg-gray-800/50 px-2 py-1 rounded">
                                  {option.ui_pattern}
                                </p>
                              </div>

                              {/* 文案建议 */}
                              {option.copy.headline && (
                                <div>
                                  <span className="text-gray-500 block mb-1">文案参考</span>
                                  <div className="bg-gray-800/50 px-2 py-1.5 rounded space-y-1">
                                    <p className="text-white font-medium">{option.copy.headline}</p>
                                    {option.copy.subheadline && (
                                      <p className="text-gray-400 text-[11px]">{option.copy.subheadline}</p>
                                    )}
                                    {option.copy.cta && (
                                      <p className="text-purple-400 text-[11px]">CTA: {option.copy.cta}</p>
                                    )}
                                  </div>
                                </div>
                              )}

                              {/* 竞品截图参考 - 直接展示缩略图 */}
                              {screenshots.length > 0 && (
                                <div>
                                  <span className="text-gray-500 block mb-1">竞品 UI（点击查看大图）</span>
                                  <div className="flex gap-2 overflow-x-auto pb-1">
                                    {screenshots.slice(0, 3).map((shot, i) => (
                                      <div 
                                        key={i}
                                        className="flex-shrink-0 cursor-pointer group"
                                        onClick={(e) => {
                                          e.stopPropagation()
                                          setScreenshotPreview({ app: shot.app, page: shot.page, description: shot.description })
                                        }}
                                      >
                                        <div className="relative w-14 h-24 rounded-lg overflow-hidden border border-gray-600 group-hover:border-purple-500 transition-colors">
                                          <img 
                                            src={`http://localhost:8002/api/thumbnails/downloads_2024%2F${shot.app}/${String(shot.page).padStart(4, '0')}.png?size=small`}
                                            alt={`${shot.app} #${shot.page}`}
                                            className="w-full h-full object-cover"
                                            onError={(e) => {
                                              const target = e.target as HTMLImageElement
                                              target.style.display = 'none'
                                              target.parentElement!.innerHTML = `<div class="w-full h-full flex items-center justify-center bg-gray-700 text-[10px] text-gray-500">${shot.app[0]}</div>`
                                            }}
                                          />
                                          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                            <Eye size={14} className="text-white" />
                                          </div>
                                        </div>
                                        <p className="text-[9px] text-gray-500 mt-1 text-center truncate w-14">{shot.app}</p>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* 研究依据 */}
                              {option.research && (
                                <div className="bg-green-500/10 text-green-400 px-2 py-1.5 rounded text-[11px]">
                                  📊 {option.research}
                                </div>
                              )}

                              {/* 查看更多详情按钮 */}
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setDetailOption(option)
                                }}
                                className="w-full flex items-center justify-center gap-1 text-purple-400 hover:text-purple-300 py-1"
                              >
                                <Eye size={12} />
                                <span>查看完整详情</span>
                              </button>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>

                    {/* 底部按钮区 */}
                    <div className="px-4 pb-4">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={(e) => {
                          e.stopPropagation()
                          selectOption(option.id)
                        }}
                        className={`
                          w-full py-2.5 rounded-xl font-medium text-sm transition-all
                          ${option.recommended 
                            ? 'bg-gradient-to-r from-yellow-500 to-amber-500 text-black' 
                            : 'bg-gray-700 hover:bg-gray-600 text-white'
                          }
                        `}
                      >
                        选择此卡
                      </motion.button>
                    </div>
                  </div>

                  {/* 卡牌光晕效果 */}
                  {isHovered && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="absolute -inset-2 rounded-3xl pointer-events-none"
                      style={{
                        background: `radial-gradient(circle, ${TYPE_COLORS[option.type]}20 0%, transparent 70%)`,
                        filter: 'blur(20px)',
                        zIndex: -1,
                      }}
                    />
                  )}
                </motion.div>
              )
            })}
          </div>
        )}

        {/* 完成提示 */}
        {nextOptions?.can_finish && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 text-center"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-500/30 rounded-full text-green-400 text-sm">
              <Shield size={16} />
              已达成最低要求，可以导出或继续构建
            </div>
          </motion.div>
        )}
      </div>

      {/* 底部：已选卡组 */}
      <div className="relative z-10 p-6 border-t border-gray-800/50 bg-gray-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <button 
              onClick={() => setShowDeck(!showDeck)}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <Layers size={18} />
              <span className="font-medium">已选卡组</span>
              <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded-full text-sm">
                {selectedPages.length}
              </span>
            </button>
            
            {selectedPages.length > 0 && (
              <button
                onClick={undoSelection}
                className="flex items-center gap-2 text-sm text-gray-500 hover:text-white transition-colors"
              >
                <ChevronLeft size={16} />
                撤销上一张
              </button>
            )}
          </div>

          {/* 卡组展示 */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {selectedPages.length === 0 ? (
              <div className="text-gray-600 text-sm py-4">
                还没有选择任何卡牌，从上方选择开始构建你的 Onboarding 流程
              </div>
            ) : (
              selectedPages.map((page, idx) => (
                <motion.div
                  key={`deck-${idx}`}
                  initial={{ opacity: 0, scale: 0.8, x: -20 }}
                  animate={{ opacity: 1, scale: 1, x: 0 }}
                  transition={{ delay: idx * 0.02 }}
                  className="flex-shrink-0 group relative"
                >
                  <div 
                    className={`
                      w-14 h-20 rounded-lg border-2 flex flex-col items-center justify-center
                      bg-gradient-to-b from-gray-800 to-gray-900
                      transition-all group-hover:scale-110 group-hover:-translate-y-1
                      ${RARITY_STYLES[page.confidence]?.border || 'border-gray-600'}
                    `}
                  >
                    <div 
                      className="w-8 h-8 rounded flex items-center justify-center text-white text-xs font-bold mb-1"
                      style={{ backgroundColor: TYPE_COLORS[page.type] }}
                    >
                      {page.type}
                    </div>
                    <span className="text-[10px] text-gray-500">#{idx + 1}</span>
                  </div>
                  
                  {/* 悬浮提示 */}
                  <div className="opacity-0 group-hover:opacity-100 absolute -top-10 left-1/2 -translate-x-1/2 pointer-events-none transition-opacity z-20">
                    <div className="bg-gray-800 px-2 py-1 rounded text-xs whitespace-nowrap border border-gray-700">
                      {page.name}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* 详情弹窗 */}
      <AnimatePresence>
        {detailOption && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-8"
            onClick={() => setDetailOption(null)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-gray-900 rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-auto border border-gray-700"
              onClick={(e) => e.stopPropagation()}
            >
              {/* 头部 */}
              <div 
                className="p-6 border-b border-gray-700"
                style={{ 
                  background: `linear-gradient(135deg, ${TYPE_COLORS[detailOption.type]}20 0%, transparent 100%)`
                }}
              >
                <div className="flex items-center gap-4">
                  <div 
                    className="w-16 h-16 rounded-xl flex flex-col items-center justify-center text-white shadow-lg"
                    style={{ backgroundColor: TYPE_COLORS[detailOption.type] }}
                  >
                    <span className="text-2xl font-black">{detailOption.type}</span>
                    <span className="text-[10px] opacity-80">{TYPE_NAMES[detailOption.type]}</span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">{detailOption.name}</h2>
                    <p className="text-gray-400">{detailOption.purpose}</p>
                  </div>
                </div>
              </div>

              {/* 内容 */}
              <div className="p-6 space-y-6">
                {/* 心理策略 */}
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2">心理策略</h3>
                  <div className="flex flex-wrap gap-2">
                    {detailOption.psychology.map((p, i) => (
                      <span key={i} className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>

                {/* UI 模式 */}
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2">UI 模式</h3>
                  <p className="text-white bg-gray-800 px-4 py-3 rounded-xl">{detailOption.ui_pattern}</p>
                </div>

                {/* 文案建议 */}
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2">文案建议</h3>
                  <div className="bg-gray-800 px-4 py-3 rounded-xl space-y-2">
                    <p className="text-xl font-bold text-white">{detailOption.copy.headline}</p>
                    {detailOption.copy.subheadline && (
                      <p className="text-gray-400">{detailOption.copy.subheadline}</p>
                    )}
                    {detailOption.copy.cta && (
                      <div className="pt-2">
                        <span className="inline-block px-4 py-2 bg-purple-500 text-white rounded-lg text-sm">
                          {detailOption.copy.cta}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* 竞品 UI 参考 - 直接展示截图 */}
                {getCompetitorScreenshots(detailOption.id).length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-400 mb-3">竞品 UI 参考（点击查看大图）</h3>
                    <div className="grid grid-cols-3 gap-3">
                      {getCompetitorScreenshots(detailOption.id).map((shot, i) => (
                        <div
                          key={i}
                          className="cursor-pointer group"
                          onClick={() => {
                            setDetailOption(null)
                            setScreenshotPreview({ app: shot.app, page: shot.page, description: shot.description })
                          }}
                        >
                          <div className="relative aspect-[9/16] rounded-xl overflow-hidden border-2 border-gray-700 group-hover:border-purple-500 transition-all">
                            <img 
                              src={`http://localhost:8002/api/thumbnails/downloads_2024%2F${shot.app}/${String(shot.page).padStart(4, '0')}.png?size=medium`}
                              alt={`${shot.app} #${shot.page}`}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                const target = e.target as HTMLImageElement
                                target.parentElement!.innerHTML = `<div class="w-full h-full flex items-center justify-center bg-gray-800 text-gray-500 text-xs">加载失败</div>`
                              }}
                            />
                            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                              <Eye size={20} className="text-white" />
                            </div>
                          </div>
                          <p className="text-gray-400 text-xs mt-2 font-medium">{shot.app}</p>
                          <p className="text-gray-500 text-[10px] line-clamp-1">{shot.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 研究依据 */}
                {detailOption.research && (
                  <div className="bg-green-500/10 border border-green-500/30 p-4 rounded-xl">
                    <h3 className="text-sm font-medium text-green-400 mb-1">📊 研究依据</h3>
                    <p className="text-green-300">{detailOption.research}</p>
                  </div>
                )}

                {/* 竞品原始参考 */}
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2">竞品来源</h3>
                  <div className="flex flex-wrap gap-2">
                    {detailOption.competitor_refs.map((ref, i) => (
                      <span key={i} className="px-3 py-1 bg-gray-800 text-gray-300 rounded-full text-sm">
                        {ref}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* 底部 */}
              <div className="p-6 border-t border-gray-700 flex gap-3">
                <button
                  onClick={() => setDetailOption(null)}
                  className="flex-1 py-3 bg-gray-800 hover:bg-gray-700 rounded-xl transition-colors"
                >
                  关闭
                </button>
                <button
                  onClick={() => {
                    selectOption(detailOption.id)
                    setDetailOption(null)
                  }}
                  className="flex-1 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 rounded-xl font-medium transition-colors"
                >
                  选择此卡
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 类型说明弹窗 */}
      <AnimatePresence>
        {showTypeGuide && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowTypeGuide(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-gray-900 rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden border border-gray-700"
              onClick={(e) => e.stopPropagation()}
            >
              {/* 头部 */}
              <div className="p-6 border-b border-gray-700 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                    <BookOpen size={20} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">页面类型说明</h2>
                    <p className="text-gray-400 text-sm">12 种 Onboarding 页面类型的详细解释</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowTypeGuide(false)}
                  className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              {/* 内容 */}
              <div className="p-6 overflow-auto max-h-[calc(90vh-100px)]">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(TYPE_DESCRIPTIONS).map(([type, desc]) => (
                    <div
                      key={type}
                      className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden hover:border-gray-600 transition-colors"
                    >
                      {/* 类型头部 */}
                      <div 
                        className="p-4 flex items-center gap-3"
                        style={{ 
                          background: `linear-gradient(135deg, ${TYPE_COLORS[type]}30 0%, transparent 100%)`
                        }}
                      >
                        <div 
                          className="w-12 h-12 rounded-xl flex flex-col items-center justify-center text-white shadow-lg font-bold"
                          style={{ backgroundColor: TYPE_COLORS[type] }}
                        >
                          <span className="text-lg">{type}</span>
                          <span className="text-[8px] opacity-80">{TYPE_NAMES[type]}</span>
                        </div>
                        <div>
                          <h3 className="font-bold text-white">{desc.fullName}</h3>
                          <p className="text-sm text-gray-400">{desc.shortDesc}</p>
                        </div>
                      </div>

                      {/* 详情内容 */}
                      <div className="p-4 space-y-3 text-sm">
                        <div>
                          <p className="text-gray-300 leading-relaxed">{desc.longDesc}</p>
                        </div>
                        
                        <div>
                          <span className="text-gray-500 text-xs">常见示例：</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {desc.examples.map((ex, i) => (
                              <span key={i} className="px-2 py-0.5 bg-gray-700/50 rounded text-gray-300 text-xs">
                                {ex}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="bg-purple-500/10 border border-purple-500/30 p-2 rounded-lg">
                          <span className="text-purple-400 text-xs font-medium">🧠 心理学原理：</span>
                          <p className="text-purple-300 text-xs mt-0.5">{desc.psychology}</p>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div className="bg-gray-700/30 p-2 rounded">
                            <span className="text-gray-500">何时使用：</span>
                            <p className="text-gray-300 mt-0.5">{desc.whenToUse}</p>
                          </div>
                          <div className="bg-green-500/10 p-2 rounded">
                            <span className="text-green-500">最佳实践：</span>
                            <p className="text-green-300 mt-0.5">{desc.bestPractice}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 竞品截图预览弹窗 - 大图模式，方便设计参考 */}
      <AnimatePresence>
        {screenshotPreview && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/95 z-50 flex"
            onClick={() => setScreenshotPreview(null)}
          >
            {/* 左侧：大图展示区 */}
            <div className="flex-1 flex items-center justify-center p-8">
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="relative"
                onClick={(e) => e.stopPropagation()}
              >
                <img 
                  src={`http://localhost:8002/api/screenshots/downloads_2024%2F${screenshotPreview.app}/${String(screenshotPreview.page).padStart(4, '0')}.png`}
                  alt={`${screenshotPreview.app} 第 ${screenshotPreview.page} 页`}
                  className="max-h-[85vh] w-auto rounded-2xl shadow-2xl border border-gray-700"
                  onError={(e) => {
                    // 原图失败时尝试缩略图
                    (e.target as HTMLImageElement).src = `http://localhost:8002/api/thumbnails/downloads_2024%2F${screenshotPreview.app}/${String(screenshotPreview.page).padStart(4, '0')}.png?size=large`
                  }}
                />
              </motion.div>
            </div>

            {/* 右侧：信息面板 */}
            <motion.div
              initial={{ x: 100, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 100, opacity: 0 }}
              className="w-72 bg-gray-900/95 border-l border-gray-700 p-5 flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              {/* 关闭按钮 */}
              <button
                onClick={() => setScreenshotPreview(null)}
                className="absolute top-4 right-4 p-2 bg-gray-800 rounded-full hover:bg-gray-700 transition-colors"
              >
                <X size={18} />
              </button>

              {/* 标题 */}
              <div className="mb-4">
                <h2 className="text-lg font-bold text-white">{screenshotPreview.app}</h2>
                <p className="text-gray-400 text-sm">第 {screenshotPreview.page} 页</p>
              </div>

              {/* 描述 */}
              {screenshotPreview.description && (
                <div className="mb-4 p-3 bg-gray-800/50 rounded-xl">
                  <p className="text-gray-300 text-sm">{screenshotPreview.description}</p>
                </div>
              )}

              {/* 设计提示 */}
              <div className="mb-4 p-3 bg-purple-500/10 border border-purple-500/30 rounded-xl">
                <p className="text-purple-300 text-xs">
                  💡 可直接复制图片链接或下载原图，作为设计参考
                </p>
              </div>

              {/* 操作按钮 */}
              <div className="space-y-2 mt-auto">
                <button
                  onClick={() => {
                    const imgUrl = `http://localhost:8002/api/screenshots/downloads_2024%2F${screenshotPreview.app}/${String(screenshotPreview.page).padStart(4, '0')}.png`
                    navigator.clipboard.writeText(imgUrl)
                    alert('图片链接已复制！')
                  }}
                  className="w-full py-2.5 bg-gray-800 hover:bg-gray-700 rounded-xl text-sm transition-colors flex items-center justify-center gap-2"
                >
                  <ImageIcon size={14} />
                  复制图片链接
                </button>
                
                <a
                  href={`http://localhost:8002/api/screenshots/downloads_2024%2F${screenshotPreview.app}/${String(screenshotPreview.page).padStart(4, '0')}.png`}
                  download={`${screenshotPreview.app}_page${screenshotPreview.page}.png`}
                  className="w-full py-2.5 bg-gray-800 hover:bg-gray-700 rounded-xl text-sm transition-colors flex items-center justify-center gap-2"
                >
                  <Download size={14} />
                  下载原图
                </a>

                <a
                  href={`http://localhost:3001/analysis/swimlane/${screenshotPreview.app}?page=${screenshotPreview.page}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-2.5 bg-purple-500 hover:bg-purple-400 rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <ExternalLink size={14} />
                  查看完整流程
                </a>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

