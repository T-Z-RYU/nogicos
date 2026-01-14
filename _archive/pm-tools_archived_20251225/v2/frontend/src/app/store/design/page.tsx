'use client'

import { useEffect, useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AppLayout } from '@/components/layout'
import {
  getAllStoreAnalysisV2,
  getStoreStatistics,
  getDesignPatterns,
  getVitaFlowRecommendations,
  getStoreScreenshotUrl,
  getStoreIconUrl,
  type StoreAnalysisV2Data,
  type StoreAnalysisV2Screenshot,
  type StoreStatistics,
  type DesignPatterns,
  type VitaFlowRecommendations,
} from '@/lib/api'
import {
  LayoutGrid,
  Table,
  BarChart3,
  Lightbulb,
  ChevronRight,
  X,
  Info,
  CheckCircle,
  AlertCircle,
  Palette,
  Type,
  Brain,
  Target,
  Sparkles,
  TrendingUp,
} from 'lucide-react'

// 页面类型颜色映射
const TYPE_COLORS: Record<string, string> = {
  VP: '#22c55e',
  AI_DEMO: '#a855f7',
  CORE_FUNC: '#3b82f6',
  RESULT_PREVIEW: '#06b6d4',
  PERSONALIZATION: '#ec4899',
  SOCIAL_PROOF: '#fbbf24',
  AUTHORITY: '#f97316',
  DATA_PROOF: '#10b981',
  USP: '#8b5cf6',
  HOW_IT_WORKS: '#6b7280',
  INTEGRATION: '#14b8a6',
  CONTENT_PREVIEW: '#f59e0b',
  FREE_TRIAL: '#ef4444',
  OTHER: '#9ca3af',
}

// 视图模式
type ViewMode = 'comparison' | 'patterns' | 'stats' | 'recommend'

export default function StoreDesignPage() {
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<ViewMode>('comparison')
  
  // 数据状态
  const [allApps, setAllApps] = useState<StoreAnalysisV2Data[]>([])
  const [statistics, setStatistics] = useState<StoreStatistics | null>(null)
  const [patterns, setPatterns] = useState<DesignPatterns | null>(null)
  const [recommendations, setRecommendations] = useState<VitaFlowRecommendations | null>(null)
  
  // 对比视图状态
  const [selectedPosition, setSelectedPosition] = useState('P1')
  const [selectedScreenshot, setSelectedScreenshot] = useState<{
    app: StoreAnalysisV2Data
    screenshot: StoreAnalysisV2Screenshot
  } | null>(null)
  
  // 加载数据
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const [appsRes, statsRes, patternsRes, recRes] = await Promise.all([
          getAllStoreAnalysisV2(),
          getStoreStatistics(),
          getDesignPatterns(),
          getVitaFlowRecommendations(),
        ])
        
        if (appsRes.success) setAllApps(appsRes.data)
        if (statsRes.success) setStatistics(statsRes.data)
        if (patternsRes.success) setPatterns(patternsRes.data)
        if (recRes.success) setRecommendations(recRes.data)
      } catch (err) {
        console.error('Failed to load data:', err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])
  
  // 获取指定位置的所有截图
  const screenshotsAtPosition = useMemo(() => {
    return allApps
      .map(app => {
        const screenshot = app.screenshots.find(s => s.position === selectedPosition)
        return screenshot ? { app, screenshot } : null
      })
      .filter(Boolean) as { app: StoreAnalysisV2Data; screenshot: StoreAnalysisV2Screenshot }[]
  }, [allApps, selectedPosition])
  
  // 计算该位置的统计摘要
  const positionStats = useMemo(() => {
    if (screenshotsAtPosition.length === 0) return null
    
    const types = screenshotsAtPosition.map(s => s.screenshot.L2_understanding.page_type.primary)
    const typeCount: Record<string, number> = {}
    types.forEach(t => { typeCount[t] = (typeCount[t] || 0) + 1 })
    
    const sortedTypes = Object.entries(typeCount).sort((a, b) => b[1] - a[1])
    const topType = sortedTypes[0]
    
    const hasDeviceMockup = screenshotsAtPosition.filter(
      s => s.screenshot.L1_extraction.visual_extraction.device_mockup.present
    ).length
    
    const hasGradient = screenshotsAtPosition.filter(
      s => s.screenshot.L1_extraction.visual_extraction.background_style === 'gradient'
    ).length
    
    return {
      total: screenshotsAtPosition.length,
      topType: topType ? { type: topType[0], count: topType[1], percentage: Math.round(topType[1] / screenshotsAtPosition.length * 100) } : null,
      deviceMockupRate: Math.round(hasDeviceMockup / screenshotsAtPosition.length * 100),
      gradientRate: Math.round(hasGradient / screenshotsAtPosition.length * 100),
    }
  }, [screenshotsAtPosition])

  return (
    <AppLayout>
      {/* 顶部导航 */}
      <div className="border-b border-white/10 bg-[#0a0a0a]/80 backdrop-blur-sm sticky top-0 z-30">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-white">Store Design Dashboard</h1>
              <p className="text-sm text-gray-400 mt-1">
                {statistics ? `${statistics.sample_size} Apps / ${statistics.total_screenshots} Screenshots` : 'Loading...'}
              </p>
            </div>
            
            {/* 视图切换 */}
            <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
              {[
                { mode: 'comparison' as ViewMode, icon: LayoutGrid, label: 'Compare' },
                { mode: 'patterns' as ViewMode, icon: Palette, label: 'Patterns' },
                { mode: 'stats' as ViewMode, icon: BarChart3, label: 'Statistics' },
                { mode: 'recommend' as ViewMode, icon: Lightbulb, label: 'VitaFlow' },
              ].map(({ mode, icon: Icon, label }) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    viewMode === mode
                      ? 'bg-white text-black'
                      : 'text-gray-400 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* 主内容区 */}
      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-400">Loading...</div>
          </div>
        ) : (
          <>
            {viewMode === 'comparison' && (
              <ComparisonView
                screenshotsAtPosition={screenshotsAtPosition}
                selectedPosition={selectedPosition}
                setSelectedPosition={setSelectedPosition}
                positionStats={positionStats}
                onSelectScreenshot={setSelectedScreenshot}
              />
            )}
            
            {viewMode === 'patterns' && patterns && (
              <PatternsView patterns={patterns} allApps={allApps} />
            )}
            
            {viewMode === 'stats' && statistics && (
              <StatisticsView statistics={statistics} />
            )}
            
            {viewMode === 'recommend' && recommendations && (
              <RecommendView recommendations={recommendations} statistics={statistics} />
            )}
          </>
        )}
      </div>
      
      {/* 截图详情面板 */}
      <AnimatePresence>
        {selectedScreenshot && (
          <ScreenshotDetailPanel
            data={selectedScreenshot}
            onClose={() => setSelectedScreenshot(null)}
          />
        )}
      </AnimatePresence>
    </AppLayout>
  )
}

// ============================================================================
// 对比视图组件
// ============================================================================

function ComparisonView({
  screenshotsAtPosition,
  selectedPosition,
  setSelectedPosition,
  positionStats,
  onSelectScreenshot,
}: {
  screenshotsAtPosition: { app: StoreAnalysisV2Data; screenshot: StoreAnalysisV2Screenshot }[]
  selectedPosition: string
  setSelectedPosition: (pos: string) => void
  positionStats: { total: number; topType: { type: string; count: number; percentage: number } | null; deviceMockupRate: number; gradientRate: number } | null
  onSelectScreenshot: (data: { app: StoreAnalysisV2Data; screenshot: StoreAnalysisV2Screenshot }) => void
}) {
  return (
    <div className="p-6">
      {/* 位置选择器 */}
      <div className="flex items-center gap-4 mb-6">
        <span className="text-sm text-gray-400">Position:</span>
        <div className="flex gap-2">
          {['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10'].map(pos => (
            <button
              key={pos}
              onClick={() => setSelectedPosition(pos)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedPosition === pos
                  ? 'bg-white text-black'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              {pos}
            </button>
          ))}
        </div>
      </div>
      
      {/* 统计摘要 */}
      {positionStats && (
        <div className="bg-white/5 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-6 text-sm">
            <div>
              <span className="text-gray-400">Apps: </span>
              <span className="text-white font-medium">{positionStats.total}</span>
            </div>
            {positionStats.topType && (
              <div>
                <span className="text-gray-400">Top Type: </span>
                <span 
                  className="font-medium px-2 py-0.5 rounded"
                  style={{ 
                    backgroundColor: `${TYPE_COLORS[positionStats.topType.type]}20`,
                    color: TYPE_COLORS[positionStats.topType.type]
                  }}
                >
                  {positionStats.topType.type} ({positionStats.topType.percentage}%)
                </span>
              </div>
            )}
            <div>
              <span className="text-gray-400">Device Mockup: </span>
              <span className="text-white">{positionStats.deviceMockupRate}%</span>
            </div>
            <div>
              <span className="text-gray-400">Gradient BG: </span>
              <span className="text-white">{positionStats.gradientRate}%</span>
            </div>
          </div>
        </div>
      )}
      
      {/* 截图网格 */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
        {screenshotsAtPosition.map(({ app, screenshot }) => (
          <motion.div
            key={app.app_name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="group cursor-pointer"
            onClick={() => onSelectScreenshot({ app, screenshot })}
          >
            <div className="relative bg-white/5 rounded-xl overflow-hidden border border-white/10 hover:border-white/30 transition-all">
              {/* 截图 */}
              <div className="aspect-[9/19.5] relative">
                <img
                  src={getStoreScreenshotUrl(app.folder_name || app.app_name, screenshot.filename)}
                  alt={`${app.app_name} ${selectedPosition}`}
                  className="w-full h-full object-cover"
                />
                {/* 类型标签 */}
                <div 
                  className="absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium"
                  style={{
                    backgroundColor: `${TYPE_COLORS[screenshot.L2_understanding.page_type.primary]}`,
                    color: '#000'
                  }}
                >
                  {screenshot.L2_understanding.page_type.primary}
                </div>
              </div>
              
              {/* App 信息 */}
              <div className="p-3">
                <div className="flex items-center gap-2">
                  <img
                    src={getStoreIconUrl(app.folder_name || app.app_name)}
                    alt={app.app_name}
                    className="w-6 h-6 rounded-md"
                  />
                  <span className="text-sm text-white font-medium truncate">{app.app_name}</span>
                </div>
                {screenshot.L1_extraction.text_extraction.headline && (
                  <p className="text-xs text-gray-400 mt-2 line-clamp-2">
                    "{screenshot.L1_extraction.text_extraction.headline}"
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      {screenshotsAtPosition.length === 0 && (
        <div className="text-center text-gray-400 py-20">
          No screenshots found at position {selectedPosition}
        </div>
      )}
    </div>
  )
}

// ============================================================================
// 模式库组件
// ============================================================================

function PatternsView({ patterns, allApps }: { patterns: DesignPatterns; allApps: StoreAnalysisV2Data[] }) {
  const [activeTab, setActiveTab] = useState<'headlines' | 'layouts' | 'colors'>('headlines')
  
  return (
    <div className="p-6">
      {/* Tab 切换 */}
      <div className="flex gap-4 mb-6">
        {[
          { id: 'headlines' as const, label: 'Headline Patterns', icon: Type },
          { id: 'layouts' as const, label: 'Layout Patterns', icon: LayoutGrid },
          { id: 'colors' as const, label: 'Color Schemes', icon: Palette },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === id
                ? 'bg-white/10 text-white border border-white/20'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>
      
      {/* Headlines */}
      {activeTab === 'headlines' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white mb-4">High-Frequency Headlines</h3>
          <div className="grid gap-3">
            {patterns.headline_patterns.slice(0, 30).map((pattern, i) => (
              <div key={i} className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-white font-medium">"{pattern.text}"</p>
                    <div className="flex items-center gap-3 mt-2 text-sm text-gray-400">
                      <span>{pattern.app}</span>
                      <span>•</span>
                      <span>{pattern.position}</span>
                      <span>•</span>
                      <span 
                        className="px-2 py-0.5 rounded text-xs"
                        style={{ backgroundColor: `${TYPE_COLORS[pattern.type]}20`, color: TYPE_COLORS[pattern.type] }}
                      >
                        {pattern.type}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Layouts */}
      {activeTab === 'layouts' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white mb-4">Layout Distribution</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(patterns.layout_patterns).map(([layout, data]) => (
              <div key={layout} className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="text-white font-medium">{layout.replace(/_/g, ' ')}</div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-2xl font-bold text-white">{data.count}</span>
                  <span className="text-sm text-gray-400">{data.percentage}</span>
                </div>
                <div className="mt-2 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: data.percentage }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Colors */}
      {activeTab === 'colors' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white mb-4">Brand Color Schemes</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {patterns.color_schemes.map((scheme, i) => (
              <div key={i} className="bg-white/5 rounded-lg p-4 border border-white/10">
                <div className="flex items-center gap-2 mb-3">
                  <img
                    src={getStoreIconUrl(scheme.app)}
                    alt={scheme.app}
                    className="w-8 h-8 rounded-lg"
                  />
                  <span className="text-white font-medium">{scheme.app}</span>
                </div>
                <div className="flex gap-2">
                  {scheme.colors.map((color, j) => (
                    <div
                      key={j}
                      className="w-8 h-8 rounded-lg border border-white/20"
                      style={{ backgroundColor: color }}
                      title={color}
                    />
                  ))}
                </div>
                <div className="mt-2 text-xs text-gray-400 capitalize">{scheme.mood}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ============================================================================
// 统计仪表盘组件
// ============================================================================

function StatisticsView({ statistics }: { statistics: StoreStatistics }) {
  return (
    <div className="p-6 space-y-6">
      {/* 概览卡片 */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Apps" value={statistics.sample_size} />
        <StatCard label="Total Screenshots" value={statistics.total_screenshots} />
        <StatCard label="Avg Score" value={statistics.design_score_averages.visual_appeal?.toFixed(1) || 'N/A'} />
        <StatCard label="Page Types" value={Object.keys(statistics.type_distribution).length} />
      </div>
      
      {/* 类型分布 */}
      <div className="bg-white/5 rounded-xl p-6 border border-white/10">
        <h3 className="text-lg font-semibold text-white mb-4">Page Type Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {Object.entries(statistics.type_distribution)
            .sort((a, b) => b[1].count - a[1].count)
            .map(([type, data]) => (
              <div 
                key={type} 
                className="flex items-center justify-between p-3 rounded-lg"
                style={{ backgroundColor: `${TYPE_COLORS[type]}15` }}
              >
                <span 
                  className="font-medium"
                  style={{ color: TYPE_COLORS[type] }}
                >
                  {type}
                </span>
                <span className="text-white">{data.percentage}</span>
              </div>
            ))}
        </div>
      </div>
      
      {/* Position-Type 矩阵 */}
      <div className="bg-white/5 rounded-xl p-6 border border-white/10">
        <h3 className="text-lg font-semibold text-white mb-4">Position-Type Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-2 px-3 text-gray-400">Type</th>
                {['P1', 'P2', 'P3', 'P4', 'P5', 'P6'].map(pos => (
                  <th key={pos} className="text-center py-2 px-3 text-gray-400">{pos}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.keys(TYPE_COLORS).slice(0, 10).map(type => (
                <tr key={type} className="border-b border-white/5">
                  <td className="py-2 px-3" style={{ color: TYPE_COLORS[type] }}>{type}</td>
                  {['P1', 'P2', 'P3', 'P4', 'P5', 'P6'].map(pos => {
                    const cell = statistics.position_type_matrix[pos]?.[type]
                    const pct = cell ? parseInt(cell.percentage) : 0
                    return (
                      <td key={pos} className="text-center py-2 px-3">
                        {pct > 0 && (
                          <span 
                            className="inline-block px-2 py-1 rounded text-xs font-medium"
                            style={{ 
                              backgroundColor: `${TYPE_COLORS[type]}${Math.min(pct + 20, 100).toString(16).padStart(2, '0')}`,
                              color: pct > 50 ? '#000' : TYPE_COLORS[type]
                            }}
                          >
                            {cell?.percentage}
                          </span>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* 序列聚类 */}
      <div className="bg-white/5 rounded-xl p-6 border border-white/10">
        <h3 className="text-lg font-semibold text-white mb-4">Sequence Clusters</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(statistics.sequence_clusters).map(([cluster, data]) => (
            <div key={cluster} className="p-4 rounded-lg bg-white/5 border border-white/10">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium capitalize">{cluster.replace(/_/g, ' ')}</span>
                <span className="text-gray-400">{data.percentage}</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {data.apps.map(app => (
                  <span key={app} className="text-xs px-2 py-0.5 bg-white/10 rounded text-gray-300">
                    {app}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* 心理策略覆盖 */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5" /> Cialdini Principles
          </h3>
          <div className="space-y-2">
            {Object.entries(statistics.psychology_coverage.cialdini_principles)
              .sort((a, b) => b[1].count - a[1].count)
              .map(([principle, data]) => (
                <div key={principle} className="flex items-center justify-between">
                  <span className="text-gray-300 capitalize">{principle.replace(/_/g, ' ')}</span>
                  <span className="text-white">{data.percentage}</span>
                </div>
              ))}
          </div>
        </div>
        
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Target className="w-5 h-5" /> Cognitive Biases
          </h3>
          <div className="space-y-2">
            {Object.entries(statistics.psychology_coverage.cognitive_biases)
              .sort((a, b) => b[1].count - a[1].count)
              .slice(0, 8)
              .map(([bias, data]) => (
                <div key={bias} className="flex items-center justify-between">
                  <span className="text-gray-300 capitalize">{bias.replace(/_/g, ' ')}</span>
                  <span className="text-white">{data.percentage}</span>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white/5 rounded-xl p-4 border border-white/10">
      <div className="text-sm text-gray-400">{label}</div>
      <div className="text-2xl font-bold text-white mt-1">{value}</div>
    </div>
  )
}

// ============================================================================
// VitaFlow 推荐组件
// ============================================================================

function RecommendView({ 
  recommendations, 
  statistics 
}: { 
  recommendations: VitaFlowRecommendations
  statistics: StoreStatistics | null
}) {
  return (
    <div className="p-6 space-y-6">
      {/* 推荐序列 */}
      <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 rounded-xl p-6 border border-purple-500/20">
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          Recommended Sequence for VitaFlow
        </h3>
        <p className="text-gray-400 mb-4">
          Based on {statistics?.sample_size || 15} competitor apps analysis, the recommended cluster is: 
          <span className="text-purple-400 font-medium capitalize ml-1">
            {recommendations.recommended_sequence.cluster.replace(/_/g, ' ')}
          </span>
        </p>
        
        <div className="grid grid-cols-6 gap-3">
          {Object.entries(recommendations.recommended_sequence.positions).map(([pos, data]) => (
            <div key={pos} className="bg-black/30 rounded-lg p-3 text-center">
              <div className="text-gray-400 text-xs mb-1">{pos}</div>
              <div 
                className="text-lg font-bold"
                style={{ color: TYPE_COLORS[data.recommended_type] }}
              >
                {data.recommended_type}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {Math.round(data.confidence * 100)}% confidence
              </div>
              {data.alternatives.length > 0 && (
                <div className="text-xs text-gray-600 mt-1">
                  Alt: {data.alternatives.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* 设计指南 */}
      <div className="bg-white/5 rounded-xl p-6 border border-white/10">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-green-400" />
          Design Guidelines
        </h3>
        <div className="space-y-3">
          {Object.entries(recommendations.design_guidelines).map(([pos, guideline]) => (
            <div key={pos} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg">
              <span className="text-white font-medium w-8">{pos}</span>
              <span className="text-gray-300">{guideline}</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* 必备元素 */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            Must-Have Elements
          </h3>
          <div className="flex flex-wrap gap-2">
            {recommendations.must_have_elements.map(elem => (
              <span key={elem} className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                {elem}
              </span>
            ))}
          </div>
        </div>
        
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-blue-400" />
            Recommended Psychology
          </h3>
          <div className="flex flex-wrap gap-2">
            {recommendations.recommended_psychology.map(p => (
              <span key={p} className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm capitalize">
                {p.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// 截图详情面板
// ============================================================================

function ScreenshotDetailPanel({
  data,
  onClose,
}: {
  data: { app: StoreAnalysisV2Data; screenshot: StoreAnalysisV2Screenshot }
  onClose: () => void
}) {
  const { app, screenshot } = data
  const [activeLayer, setActiveLayer] = useState<1 | 2 | 3 | 4 | 5>(1)
  
  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed right-0 top-0 h-full w-[600px] bg-[#111] border-l border-white/10 z-50 overflow-hidden flex flex-col"
    >
      {/* 头部 */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img
            src={getStoreIconUrl(app.folder_name || app.app_name)}
            alt={app.app_name}
            className="w-10 h-10 rounded-xl"
          />
          <div>
            <div className="text-white font-medium">{app.app_name}</div>
            <div className="text-sm text-gray-400">{screenshot.position} - {screenshot.L2_understanding.page_type.primary}</div>
          </div>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg">
          <X className="w-5 h-5 text-gray-400" />
        </button>
      </div>
      
      {/* 截图预览 */}
      <div className="p-4 bg-black/30">
        <div className="aspect-[9/16] max-h-[300px] mx-auto">
          <img
            src={getStoreScreenshotUrl(app.folder_name || app.app_name, screenshot.filename)}
            alt={screenshot.filename}
            className="w-full h-full object-contain rounded-xl"
          />
        </div>
      </div>
      
      {/* Layer 选择器 */}
      <div className="p-4 border-b border-white/10">
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map(layer => (
            <button
              key={layer}
              onClick={() => setActiveLayer(layer as 1 | 2 | 3 | 4 | 5)}
              className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${
                activeLayer === layer
                  ? 'bg-white text-black'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              L{layer}
            </button>
          ))}
        </div>
      </div>
      
      {/* Layer 内容 */}
      <div className="flex-1 overflow-auto p-4">
        {activeLayer === 1 && <Layer1Content screenshot={screenshot} />}
        {activeLayer === 2 && <Layer2Content screenshot={screenshot} />}
        {activeLayer === 3 && <Layer3Content screenshot={screenshot} />}
        {activeLayer === 4 && <Layer4Content screenshot={screenshot} />}
        {activeLayer === 5 && <Layer5Content screenshot={screenshot} />}
      </div>
    </motion.div>
  )
}

// Layer 内容组件
function Layer1Content({ screenshot }: { screenshot: StoreAnalysisV2Screenshot }) {
  const { text_extraction, visual_extraction } = screenshot.L1_extraction
  
  return (
    <div className="space-y-4">
      <h4 className="text-white font-medium">Text Extraction</h4>
      <div className="space-y-2 text-sm">
        {text_extraction.headline && (
          <div className="p-3 bg-white/5 rounded-lg">
            <span className="text-gray-400">Headline: </span>
            <span className="text-white">"{text_extraction.headline}"</span>
          </div>
        )}
        {text_extraction.subheadline && (
          <div className="p-3 bg-white/5 rounded-lg">
            <span className="text-gray-400">Subheadline: </span>
            <span className="text-white">"{text_extraction.subheadline}"</span>
          </div>
        )}
      </div>
      
      <h4 className="text-white font-medium mt-6">Visual Elements</h4>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="p-2 bg-white/5 rounded">
          <span className="text-gray-400">Layout: </span>
          <span className="text-white">{visual_extraction.layout_type}</span>
        </div>
        <div className="p-2 bg-white/5 rounded">
          <span className="text-gray-400">Background: </span>
          <span className="text-white">{visual_extraction.background_style}</span>
        </div>
        <div className="p-2 bg-white/5 rounded">
          <span className="text-gray-400">Device: </span>
          <span className="text-white">{visual_extraction.device_mockup.present ? 'Yes' : 'No'}</span>
        </div>
        <div className="p-2 bg-white/5 rounded">
          <span className="text-gray-400">Mood: </span>
          <span className="text-white">{visual_extraction.color_mood}</span>
        </div>
      </div>
      
      {visual_extraction.dominant_colors.length > 0 && (
        <>
          <h4 className="text-white font-medium mt-4">Colors</h4>
          <div className="flex gap-2">
            {visual_extraction.dominant_colors.map((color, i) => (
              <div
                key={i}
                className="w-10 h-10 rounded-lg border border-white/20"
                style={{ backgroundColor: color }}
                title={color}
              />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function Layer2Content({ screenshot }: { screenshot: StoreAnalysisV2Screenshot }) {
  const { page_type, message_strategy, psychology_tactics } = screenshot.L2_understanding
  
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-white font-medium mb-2">Page Type</h4>
        <div 
          className="inline-block px-3 py-1.5 rounded-lg text-sm font-medium"
          style={{ backgroundColor: `${TYPE_COLORS[page_type.primary]}20`, color: TYPE_COLORS[page_type.primary] }}
        >
          {page_type.primary} - {page_type.primary_cn}
        </div>
      </div>
      
      <div>
        <h4 className="text-white font-medium mb-2">Message Strategy</h4>
        <div className="space-y-2 text-sm">
          <div className="p-3 bg-white/5 rounded-lg">
            <span className="text-gray-400">Primary Message: </span>
            <span className="text-white">{message_strategy.primary_message}</span>
          </div>
          <div className="p-3 bg-white/5 rounded-lg">
            <span className="text-gray-400">Emotional Appeal: </span>
            <span className="text-white capitalize">{message_strategy.emotional_appeal}</span>
          </div>
        </div>
      </div>
      
      <div>
        <h4 className="text-white font-medium mb-2">Psychology Tactics</h4>
        <div className="flex flex-wrap gap-2">
          {psychology_tactics.cialdini_principles.map(p => (
            <span key={p} className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs capitalize">
              {p}
            </span>
          ))}
          {psychology_tactics.cognitive_biases.map(b => (
            <span key={b} className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs capitalize">
              {b.replace(/_/g, ' ')}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

function Layer3Content({ screenshot }: { screenshot: StoreAnalysisV2Screenshot }) {
  const { visual_hierarchy, typography, color_strategy, layout_pattern, design_scores } = screenshot.L3_design
  
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-white font-medium mb-2">Design Scores</h4>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(design_scores).map(([key, value]) => (
            <div key={key} className="p-3 bg-white/5 rounded-lg">
              <div className="text-xs text-gray-400 capitalize">{key.replace(/_/g, ' ')}</div>
              <div className="text-lg font-bold text-white">{value}/5</div>
            </div>
          ))}
        </div>
      </div>
      
      <div>
        <h4 className="text-white font-medium mb-2">Visual Hierarchy</h4>
        <div className="text-sm space-y-1">
          <div><span className="text-gray-400">Eye Flow:</span> <span className="text-white">{visual_hierarchy.eye_flow}</span></div>
          <div><span className="text-gray-400">Focal Point:</span> <span className="text-white">{visual_hierarchy.focal_point}</span></div>
          <div><span className="text-gray-400">Info Density:</span> <span className="text-white">{visual_hierarchy.information_density}</span></div>
        </div>
      </div>
      
      <div>
        <h4 className="text-white font-medium mb-2">Layout</h4>
        <div className="text-sm space-y-1">
          <div><span className="text-gray-400">Template:</span> <span className="text-white">{layout_pattern.template_type}</span></div>
          <div><span className="text-gray-400">Whitespace:</span> <span className="text-white">{layout_pattern.whitespace_usage}</span></div>
          <div><span className="text-gray-400">Symmetry:</span> <span className="text-white">{layout_pattern.symmetry}</span></div>
        </div>
      </div>
    </div>
  )
}

function Layer4Content({ screenshot }: { screenshot: StoreAnalysisV2Screenshot }) {
  const { differentiation, competitive_positioning, target_audience_signals } = screenshot.L4_insights
  
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-white font-medium mb-2">Competitive Positioning</h4>
        <span className="px-3 py-1.5 bg-white/10 text-white rounded-lg text-sm capitalize">
          {competitive_positioning}
        </span>
      </div>
      
      {differentiation.unique_elements.length > 0 && (
        <div>
          <h4 className="text-white font-medium mb-2">Unique Elements</h4>
          <div className="flex flex-wrap gap-2">
            {differentiation.unique_elements.map((elem, i) => (
              <span key={i} className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">
                {elem}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {differentiation.category_conventions.length > 0 && (
        <div>
          <h4 className="text-white font-medium mb-2">Category Conventions</h4>
          <div className="flex flex-wrap gap-2">
            {differentiation.category_conventions.map((conv, i) => (
              <span key={i} className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded text-xs">
                {conv}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function Layer5Content({ screenshot }: { screenshot: StoreAnalysisV2Screenshot }) {
  const { vitaflow_applicability, reusable_elements, avoid_elements, adaptation_notes } = screenshot.L5_recommendations
  
  const applicabilityColor = {
    highly_relevant: 'text-green-400 bg-green-500/20',
    somewhat_relevant: 'text-yellow-400 bg-yellow-500/20',
    not_relevant: 'text-red-400 bg-red-500/20',
  }
  
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-white font-medium mb-2">VitaFlow Applicability</h4>
        <span className={`px-3 py-1.5 rounded-lg text-sm capitalize ${applicabilityColor[vitaflow_applicability as keyof typeof applicabilityColor] || ''}`}>
          {vitaflow_applicability.replace(/_/g, ' ')}
        </span>
      </div>
      
      {reusable_elements.length > 0 && (
        <div>
          <h4 className="text-white font-medium mb-2 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-400" />
            Reusable Elements
          </h4>
          <div className="flex flex-wrap gap-2">
            {reusable_elements.map((elem, i) => (
              <span key={i} className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">
                {elem}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {avoid_elements.length > 0 && (
        <div>
          <h4 className="text-white font-medium mb-2 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            Avoid Elements
          </h4>
          <div className="flex flex-wrap gap-2">
            {avoid_elements.map((elem, i) => (
              <span key={i} className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">
                {elem}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {adaptation_notes && (
        <div>
          <h4 className="text-white font-medium mb-2">Adaptation Notes</h4>
          <p className="text-sm text-gray-300 p-3 bg-white/5 rounded-lg">{adaptation_notes}</p>
        </div>
      )}
    </div>
  )
}


