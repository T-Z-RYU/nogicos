'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AppLayout } from '@/components/layout'
import {
  getStoreComparison,
  getStoreInfo,
  getStoreScreenshotUrl,
  getStoreIconUrl,
  getStoreAnalysis,
  getAllStoreAnalysis,
  type StoreApp,
  type StoreAnalysisData,
  type StoreScreenshotAnalysis,
  type StoreAnalysisAllItem,
} from '@/lib/api'
import {
  Store,
  Star,
  Download,
  DollarSign,
  TrendingUp,
  X,
  Table,
  LayoutGrid,
  ChevronDown,
  ChevronUp,
  Info,
} from 'lucide-react'

// 格式化数字
function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

// 格式化金额
function formatCurrency(num: number): string {
  if (num >= 1000000) {
    return '$' + (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return '$' + (num / 1000).toFixed(0) + 'K'
  }
  return '$' + num.toString()
}

// 类型标签颜色映射
const typeColors: Record<string, string> = {
  'VP': '#22c55e',
  'AI_DEMO': '#a855f7',
  'RESULT_PREVIEW': '#3b82f6',
  'PERSONALIZATION': '#ec4899',
  'SOCIAL_PROOF': '#fbbf24',
  'FREE_TRIAL': '#ef4444',
  'CORE_FUNC': '#06b6d4',
  'AUTHORITY': '#f97316',
  'DATA_PROOF': '#10b981',
  'USP': '#8b5cf6',
  'HOW_IT_WORKS': '#6b7280',
  'INTEGRATION': '#14b8a6',
  'CONTENT_PREVIEW': '#f59e0b',
}

// 类型中文名称映射
const typeCnNames: Record<string, string> = {
  'VP': '价值主张',
  'AI_DEMO': 'AI演示',
  'RESULT_PREVIEW': '效果预览',
  'PERSONALIZATION': '个性化',
  'SOCIAL_PROOF': '社会证明',
  'FREE_TRIAL': '免费试用',
  'CORE_FUNC': '核心功能',
  'AUTHORITY': '权威背书',
  'DATA_PROOF': '数据证明',
  'USP': '独特卖点',
  'HOW_IT_WORKS': '使用说明',
  'INTEGRATION': '集成功能',
  'CONTENT_PREVIEW': '内容预览',
}

// 类型标签组件
function TypeBadge({ type, size = 'normal' }: { type: string; size?: 'small' | 'normal' }) {
  const isSmall = size === 'small'
  return (
    <span
      style={{
        display: 'inline-block',
        padding: isSmall ? '2px 6px' : '4px 10px',
        borderRadius: '4px',
        fontSize: isSmall ? '10px' : '11px',
        fontWeight: 600,
        letterSpacing: '0.3px',
        background: typeColors[type] || '#6366f1',
        color: type === 'SOCIAL_PROOF' ? '#000' : '#fff',
        whiteSpace: 'nowrap',
      }}
    >
      {type}
    </span>
  )
}

export default function StorePage() {
  const [apps, setApps] = useState<StoreApp[]>([])
  const [allAnalysis, setAllAnalysis] = useState<StoreAnalysisAllItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'table' | 'gallery'>('gallery')
  const [selectedApp, setSelectedApp] = useState<StoreApp | null>(null)
  const [analysisData, setAnalysisData] = useState<StoreAnalysisData | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [expandedApp, setExpandedApp] = useState<string | null>(null)
  const [selectedScreenshot, setSelectedScreenshot] = useState<{
    app: string
    screenshot: StoreScreenshotAnalysis
    url: string
  } | null>(null)

  // 加载数据
  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [compData, analysisData] = await Promise.all([
        getStoreComparison(),
        getAllStoreAnalysis()
      ])
      setApps(compData.apps || [])
      setAllAnalysis(analysisData.data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败')
    }
    setLoading(false)
  }

  // 获取 App 的业务数据
  const getAppBusinessData = (appName: string) => {
    return apps.find(a => a.folder_name === appName || a.name === appName)
  }

  // 点击截图查看详情
  const handleScreenshotClick = (appName: string, screenshot: StoreScreenshotAnalysis) => {
    setSelectedScreenshot({
      app: appName,
      screenshot,
      url: getStoreScreenshotUrl(appName, screenshot.filename)
    })
  }

  // 表格视图
  const TableView = () => (
    <div style={{ overflowX: 'auto' }}>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '13px',
        }}
      >
        <thead>
          <tr style={{ background: 'var(--bg-secondary)' }}>
            <th style={{ ...thStyle, width: '180px', position: 'sticky', left: 0, background: 'var(--bg-secondary)', zIndex: 2 }}>App</th>
            <th style={{ ...thStyle, width: '80px' }}>收入</th>
            <th style={thStyle}>P1</th>
            <th style={thStyle}>P2</th>
            <th style={thStyle}>P3</th>
            <th style={thStyle}>P4</th>
            <th style={thStyle}>P5</th>
            <th style={thStyle}>P6</th>
            <th style={thStyle}>P7+</th>
          </tr>
        </thead>
        <tbody>
          {allAnalysis.filter(a => a.has_analysis).map((app, idx) => {
            const businessData = getAppBusinessData(app.app_name)
            const screenshots = app.screenshots || []
            
            return (
              <tr
                key={app.app_name}
                style={{
                  background: idx % 2 === 0 ? 'transparent' : 'var(--bg-secondary)',
                  borderBottom: '1px solid var(--border-subtle)',
                }}
              >
                {/* App 名称 */}
                <td style={{ ...tdStyle, position: 'sticky', left: 0, background: idx % 2 === 0 ? 'var(--bg-primary)' : 'var(--bg-secondary)', zIndex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <img
                      src={getStoreIconUrl(app.app_name)}
                      alt=""
                      style={{ width: '28px', height: '28px', borderRadius: '6px' }}
                      onError={(e) => { e.currentTarget.style.display = 'none' }}
                    />
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '13px' }}>{app.track_name || app.app_name}</div>
                      {app.rating && (
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '2px' }}>
                          <Star size={10} fill="#f59e0b" color="#f59e0b" />
                          {app.rating.toFixed(1)}
                        </div>
                      )}
                    </div>
                  </div>
                </td>
                
                {/* 收入 */}
                <td style={tdStyle}>
                  {businessData?.revenue ? (
                    <span style={{ color: 'var(--success)', fontWeight: 500 }}>
                      {formatCurrency(businessData.revenue)}
                    </span>
                  ) : '-'}
                </td>
                
                {/* P1-P6 */}
                {[0, 1, 2, 3, 4, 5].map(i => (
                  <td key={i} style={tdStyle}>
                    {screenshots[i] ? (
                      <div
                        style={{ cursor: 'pointer' }}
                        onClick={() => handleScreenshotClick(app.app_name, screenshots[i])}
                      >
                        <TypeBadge type={screenshots[i].type} size="small" />
                      </div>
                    ) : (
                      <span style={{ color: 'var(--text-muted)' }}>-</span>
                    )}
                  </td>
                ))}
                
                {/* P7+ */}
                <td style={tdStyle}>
                  {screenshots.length > 6 ? (
                    <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                      {screenshots.slice(6).map((s, i) => (
                        <div
                          key={i}
                          style={{ cursor: 'pointer' }}
                          onClick={() => handleScreenshotClick(app.app_name, s)}
                        >
                          <TypeBadge type={s.type} size="small" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <span style={{ color: 'var(--text-muted)' }}>-</span>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      
      {/* 图例 */}
      <div style={{ marginTop: '24px', padding: '16px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
        <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '12px' }}>截图类型图例</h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {Object.entries(typeColors).map(([type, color]) => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <TypeBadge type={type} size="small" />
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{typeCnNames[type]}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  // 画廊视图
  const GalleryView = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {allAnalysis.filter(a => a.has_analysis).map((app) => {
        const businessData = getAppBusinessData(app.app_name)
        const isExpanded = expandedApp === app.app_name
        const screenshots = app.screenshots || []
        
        return (
          <div
            key={app.app_name}
            style={{
              background: 'var(--bg-card)',
              borderRadius: '12px',
              border: '1px solid var(--border-default)',
              overflow: 'hidden',
            }}
          >
            {/* App 头部 */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                borderBottom: '1px solid var(--border-subtle)',
                cursor: 'pointer',
              }}
              onClick={() => setExpandedApp(isExpanded ? null : app.app_name)}
            >
              <img
                src={getStoreIconUrl(app.app_name)}
                alt=""
                style={{ width: '40px', height: '40px', borderRadius: '10px' }}
                onError={(e) => { e.currentTarget.style.display = 'none' }}
              />
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: 600, fontSize: '15px' }}>{app.track_name || app.app_name}</span>
                  {app.rating && (
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '2px' }}>
                      <Star size={12} fill="#f59e0b" color="#f59e0b" />
                      {app.rating.toFixed(1)}
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {screenshots.length} 张截图 · 
                  序列: {app.sequence_pattern?.split(' → ').slice(0, 4).join(' → ')}...
                </div>
              </div>
              
              {/* 业务数据 */}
              <div style={{ display: 'flex', gap: '16px', marginRight: '16px' }}>
                {businessData?.revenue ? (
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>收入</div>
                    <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--success)' }}>
                      {formatCurrency(businessData.revenue)}
                    </div>
                  </div>
                ) : null}
                {businessData?.downloads ? (
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>下载</div>
                    <div style={{ fontSize: '14px', fontWeight: 500 }}>
                      {formatNumber(businessData.downloads)}
                    </div>
                  </div>
                ) : null}
                {businessData?.growth_rate !== undefined && businessData.growth_rate !== 0 ? (
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>增长</div>
                    <div style={{ 
                      fontSize: '14px', 
                      fontWeight: 500, 
                      color: businessData.growth_rate > 0 ? 'var(--success)' : 'var(--danger)' 
                    }}>
                      {businessData.growth_rate > 0 ? '+' : ''}{businessData.growth_rate.toFixed(1)}%
                    </div>
                  </div>
                ) : null}
              </div>
              
              {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </div>
            
            {/* 截图横向滚动区 */}
            <div
              style={{
                display: 'flex',
                gap: '12px',
                padding: '16px',
                overflowX: 'auto',
                background: 'var(--bg-secondary)',
              }}
            >
              {screenshots.map((screenshot, idx) => (
                <div
                  key={screenshot.filename}
                  style={{
                    flexShrink: 0,
                    width: '130px',
                    cursor: 'pointer',
                    transition: 'transform 0.15s',
                  }}
                  onClick={() => handleScreenshotClick(app.app_name, screenshot)}
                  onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.02)' }}
                  onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)' }}
                >
                  {/* 截图 */}
                  <div
                    style={{
                      position: 'relative',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      border: '1px solid var(--border-default)',
                    }}
                  >
                    {/* 位置标签 */}
                    <div
                      style={{
                        position: 'absolute',
                        top: '6px',
                        left: '6px',
                        background: 'rgba(0,0,0,0.75)',
                        color: '#fff',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 600,
                        zIndex: 2,
                      }}
                    >
                      P{idx + 1}
                    </div>
                    
                    {/* 图片 */}
                    <img
                      src={getStoreScreenshotUrl(app.app_name, screenshot.filename)}
                      alt={screenshot.filename}
                      style={{
                        width: '100%',
                        aspectRatio: '9/19.5',
                        objectFit: 'cover',
                        display: 'block',
                      }}
                    />
                    
                    {/* 类型标签 */}
                    <div
                      style={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        padding: '24px 6px 8px',
                        background: 'linear-gradient(to top, rgba(0,0,0,0.9) 60%, transparent)',
                      }}
                    >
                      <TypeBadge type={screenshot.type} size="small" />
                      <div style={{ fontSize: '9px', color: '#9ca3af', marginTop: '2px' }}>
                        {screenshot.type_cn || typeCnNames[screenshot.type]}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* 展开详情 */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  style={{ overflow: 'hidden' }}
                >
                  <div style={{ padding: '16px', borderTop: '1px solid var(--border-subtle)' }}>
                    {/* 完整序列 */}
                    <div style={{ marginBottom: '16px' }}>
                      <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                        完整截图序列
                      </h4>
                      <div style={{ fontSize: '13px', fontFamily: 'monospace', wordBreak: 'break-all', lineHeight: 1.6 }}>
                        {app.sequence_pattern}
                      </div>
                    </div>
                    
                    {/* 优势与不足 */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      {app.strengths && app.strengths.length > 0 && (
                        <div>
                          <h4 style={{ fontSize: '12px', color: 'var(--success)', marginBottom: '6px' }}>✓ 优势</h4>
                          <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                            {app.strengths.map((s, i) => <li key={i} style={{ marginBottom: '4px' }}>{s}</li>)}
                          </ul>
                        </div>
                      )}
                      {app.weaknesses && app.weaknesses.length > 0 && (
                        <div>
                          <h4 style={{ fontSize: '12px', color: 'var(--warning)', marginBottom: '6px' }}>△ 待改进</h4>
                          <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                            {app.weaknesses.map((w, i) => <li key={i} style={{ marginBottom: '4px' }}>{w}</li>)}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )
      })}
    </div>
  )

  // 表格样式
  const thStyle: React.CSSProperties = {
    padding: '12px 8px',
    textAlign: 'left',
    fontWeight: 600,
    fontSize: '12px',
    color: 'var(--text-muted)',
    borderBottom: '1px solid var(--border-default)',
    whiteSpace: 'nowrap',
  }
  
  const tdStyle: React.CSSProperties = {
    padding: '10px 8px',
    verticalAlign: 'middle',
  }

  return (
    <AppLayout>
      {/* 顶栏 */}
      <div className="topbar">
        <h1 className="topbar-title">商店截图分析</h1>
        <div style={{ flex: 1 }} />
        
        {/* 视图切换 */}
        <div style={{ display: 'flex', gap: '4px', background: 'var(--bg-secondary)', borderRadius: '6px', padding: '4px' }}>
          <button
            onClick={() => setViewMode('table')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              border: 'none',
              borderRadius: '4px',
              fontSize: '13px',
              cursor: 'pointer',
              background: viewMode === 'table' ? 'var(--bg-card)' : 'transparent',
              color: viewMode === 'table' ? 'var(--text-primary)' : 'var(--text-muted)',
              fontWeight: viewMode === 'table' ? 500 : 400,
            }}
          >
            <Table size={14} />
            表格
          </button>
          <button
            onClick={() => setViewMode('gallery')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              border: 'none',
              borderRadius: '4px',
              fontSize: '13px',
              cursor: 'pointer',
              background: viewMode === 'gallery' ? 'var(--bg-card)' : 'transparent',
              color: viewMode === 'gallery' ? 'var(--text-primary)' : 'var(--text-muted)',
              fontWeight: viewMode === 'gallery' ? 500 : 400,
            }}
          >
            <LayoutGrid size={14} />
            画廊
          </button>
        </div>
        
        <span style={{ fontSize: '13px', color: 'var(--text-muted)', marginLeft: '12px' }}>
          {allAnalysis.filter(a => a.has_analysis).length} 个已分析
        </span>
      </div>

      {/* 内容区 */}
      <div className="content-area">
        {/* 加载中 */}
        {loading && (
          <div style={{ display: 'flex', height: '256px', alignItems: 'center', justifyContent: 'center' }}>
            <div className="spinner" />
          </div>
        )}

        {/* 错误提示 */}
        {error && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '256px', gap: '16px' }}>
            <p style={{ color: 'var(--danger)' }}>{error}</p>
            <button className="btn-ghost" onClick={loadData}>重试</button>
          </div>
        )}

        {/* 主内容 */}
        {!loading && !error && (
          viewMode === 'table' ? <TableView /> : <GalleryView />
        )}

        {/* 空状态 */}
        {!loading && !error && allAnalysis.filter(a => a.has_analysis).length === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '400px', color: 'var(--text-muted)', gap: '16px' }}>
            <Store size={48} />
            <p>暂无分析数据</p>
          </div>
        )}
      </div>

      {/* 截图详情弹窗 */}
      <AnimatePresence>
        {selectedScreenshot && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.9)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '40px',
            }}
            onClick={() => setSelectedScreenshot(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              style={{
                display: 'flex',
                gap: '24px',
                maxWidth: '1000px',
                width: '100%',
                maxHeight: '90vh',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* 截图 */}
              <div style={{ flexShrink: 0 }}>
                <img
                  src={selectedScreenshot.url}
                  alt=""
                  style={{
                    height: '80vh',
                    maxHeight: '700px',
                    width: 'auto',
                    borderRadius: '16px',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
                  }}
                />
              </div>
              
              {/* 分析详情 */}
              <div
                style={{
                  flex: 1,
                  background: 'var(--bg-card)',
                  borderRadius: '16px',
                  padding: '24px',
                  overflow: 'auto',
                  maxHeight: '80vh',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>{selectedScreenshot.app}</span>
                      <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>·</span>
                      <span style={{ fontSize: '14px', fontWeight: 600 }}>{selectedScreenshot.screenshot.position}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <TypeBadge type={selectedScreenshot.screenshot.type} />
                      <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                        {selectedScreenshot.screenshot.type_cn || typeCnNames[selectedScreenshot.screenshot.type]}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedScreenshot(null)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '8px' }}
                  >
                    <X size={20} />
                  </button>
                </div>
                
                {/* 文案 */}
                {selectedScreenshot.screenshot.copywriting && (
                  <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>📝 文案</h4>
                    <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '8px' }}>
                      {selectedScreenshot.screenshot.copywriting.headline && (
                        <p style={{ fontSize: '15px', fontWeight: 600, marginBottom: '4px' }}>
                          {selectedScreenshot.screenshot.copywriting.headline}
                        </p>
                      )}
                      {selectedScreenshot.screenshot.copywriting.subheadline && (
                        <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                          {selectedScreenshot.screenshot.copywriting.subheadline}
                        </p>
                      )}
                    </div>
                  </div>
                )}
                
                {/* 设计元素 */}
                {selectedScreenshot.screenshot.elements && selectedScreenshot.screenshot.elements.length > 0 && (
                  <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>🎨 设计元素</h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {selectedScreenshot.screenshot.elements.map((el, i) => (
                        <span
                          key={i}
                          style={{
                            padding: '4px 10px',
                            background: 'var(--bg-secondary)',
                            borderRadius: '4px',
                            fontSize: '12px',
                          }}
                        >
                          {el}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* 心理学原理 */}
                {selectedScreenshot.screenshot.psychology && (
                  <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>🧠 心理学原理</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {selectedScreenshot.screenshot.psychology.cialdini && selectedScreenshot.screenshot.psychology.cialdini.length > 0 && (
                        <div>
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Cialdini:</span>
                          <div style={{ display: 'flex', gap: '6px', marginTop: '4px', flexWrap: 'wrap' }}>
                            {selectedScreenshot.screenshot.psychology.cialdini.map((p, i) => (
                              <span key={i} style={{ padding: '3px 8px', background: '#f97316', color: '#fff', borderRadius: '4px', fontSize: '11px' }}>
                                {p}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedScreenshot.screenshot.psychology.cognitive_biases && selectedScreenshot.screenshot.psychology.cognitive_biases.length > 0 && (
                        <div>
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>认知偏见:</span>
                          <div style={{ display: 'flex', gap: '6px', marginTop: '4px', flexWrap: 'wrap' }}>
                            {selectedScreenshot.screenshot.psychology.cognitive_biases.map((b, i) => (
                              <span key={i} style={{ padding: '3px 8px', background: '#8b5cf6', color: '#fff', borderRadius: '4px', fontSize: '11px' }}>
                                {b}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {/* 设计评分 */}
                {selectedScreenshot.screenshot.design_scores && (
                  <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>📊 设计评分</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
                      {selectedScreenshot.screenshot.design_scores.visual_hierarchy !== undefined && (
                        <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                          <div style={{ fontSize: '18px', fontWeight: 600 }}>{selectedScreenshot.screenshot.design_scores.visual_hierarchy}</div>
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>视觉层次</div>
                        </div>
                      )}
                      {selectedScreenshot.screenshot.design_scores.brand_consistency !== undefined && (
                        <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                          <div style={{ fontSize: '18px', fontWeight: 600 }}>{selectedScreenshot.screenshot.design_scores.brand_consistency}</div>
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>品牌一致</div>
                        </div>
                      )}
                      {selectedScreenshot.screenshot.design_scores.readability !== undefined && (
                        <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                          <div style={{ fontSize: '18px', fontWeight: 600 }}>{selectedScreenshot.screenshot.design_scores.readability}</div>
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>可读性</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {/* AI 分析 */}
                {selectedScreenshot.screenshot.analysis && (
                  <div>
                    <h4 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>💡 AI 分析</h4>
                    <p style={{ fontSize: '13px', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
                      {selectedScreenshot.screenshot.analysis}
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AppLayout>
  )
}
