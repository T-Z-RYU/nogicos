'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AppLayout } from '@/components/layout'
import {
  getStoreComparison,
  getStoreInfo,
  getStoreScreenshotUrl,
  getStoreIconUrl,
  type StoreApp,
} from '@/lib/api'
import {
  Store,
  Star,
  Download,
  DollarSign,
  TrendingUp,
  Users,
  ChevronRight,
  X,
  ExternalLink,
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

export default function StorePage() {
  const [apps, setApps] = useState<StoreApp[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedApp, setSelectedApp] = useState<StoreApp | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  // 加载商店数据
  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getStoreComparison()
      setApps(data.apps || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败')
    }
    setLoading(false)
  }

  // 加载应用详情
  const loadAppDetail = async (app: StoreApp) => {
    setDetailLoading(true)
    try {
      const detail = await getStoreInfo(app.folder_name)
      setSelectedApp({ ...app, ...detail })
    } catch (err) {
      setSelectedApp(app)
    }
    setDetailLoading(false)
  }

  return (
    <AppLayout>
      {/* 顶栏 */}
      <div className="topbar">
        <h1 className="topbar-title">App Store 对比</h1>
        <div style={{ flex: 1 }} />
        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          共 {apps.length} 个应用
        </span>
      </div>

      {/* 内容区 */}
      <div className="content-area">
        {/* 加载中 */}
        {loading && (
          <div
            style={{
              display: 'flex',
              height: '256px',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <div className="spinner" />
          </div>
        )}

        {/* 错误提示 */}
        {error && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '256px',
              gap: '16px',
            }}
          >
            <p style={{ color: 'var(--danger)' }}>{error}</p>
            <button className="btn-ghost" onClick={loadData}>
              重试
            </button>
          </div>
        )}

        {/* 应用列表 */}
        {!loading && !error && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
              gap: '16px',
            }}
          >
            {apps.map((app, index) => (
              <motion.div
                key={app.folder_name}
                className="screenshot-card"
                style={{
                  cursor: 'pointer',
                  padding: '16px',
                }}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.02 }}
                whileHover={{ scale: 1.01 }}
                onClick={() => loadAppDetail(app)}
              >
                <div style={{ display: 'flex', gap: '12px' }}>
                  {/* 应用图标 */}
                  <div
                    style={{
                      width: '60px',
                      height: '60px',
                      borderRadius: '12px',
                      background: 'var(--bg-secondary)',
                      overflow: 'hidden',
                      flexShrink: 0,
                    }}
                  >
                    <img
                      src={getStoreIconUrl(app.folder_name)}
                      alt={app.name}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                      }}
                      onError={(e) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                  </div>

                  {/* 应用信息 */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3
                      style={{
                        fontSize: '15px',
                        fontWeight: 600,
                        marginBottom: '4px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {app.track_name || app.name}
                    </h3>
                    <p
                      style={{
                        fontSize: '12px',
                        color: 'var(--text-muted)',
                        marginBottom: '8px',
                      }}
                    >
                      {app.folder_name}
                    </p>

                    {/* 评分 */}
                    {app.rating && (
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '12px',
                        }}
                      >
                        <Star size={12} color="#f59e0b" fill="#f59e0b" />
                        <span>{app.rating.toFixed(1)}</span>
                        {app.rating_count && (
                          <span style={{ color: 'var(--text-muted)' }}>
                            ({formatNumber(app.rating_count)})
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <ChevronRight size={18} style={{ opacity: 0.3 }} />
                </div>

                {/* 数据指标 */}
                {(app.revenue || app.downloads) && (
                  <div
                    style={{
                      display: 'flex',
                      gap: '16px',
                      marginTop: '12px',
                      paddingTop: '12px',
                      borderTop: '1px solid var(--border-subtle)',
                    }}
                  >
                    {app.revenue !== undefined && app.revenue > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <DollarSign size={14} style={{ color: 'var(--success)' }} />
                        <span style={{ fontSize: '13px', fontWeight: 500 }}>
                          {formatCurrency(app.revenue)}
                        </span>
                      </div>
                    )}
                    {app.downloads !== undefined && app.downloads > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Download size={14} style={{ color: 'var(--text-muted)' }} />
                        <span style={{ fontSize: '13px' }}>
                          {formatNumber(app.downloads)}
                        </span>
                      </div>
                    )}
                    {app.growth_rate !== undefined && app.growth_rate !== 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <TrendingUp
                          size={14}
                          style={{
                            color: app.growth_rate > 0 ? 'var(--success)' : 'var(--danger)',
                          }}
                        />
                        <span
                          style={{
                            fontSize: '13px',
                            color: app.growth_rate > 0 ? 'var(--success)' : 'var(--danger)',
                          }}
                        >
                          {app.growth_rate > 0 ? '+' : ''}
                          {app.growth_rate.toFixed(1)}%
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}

        {/* 空状态 */}
        {!loading && !error && apps.length === 0 && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '400px',
              color: 'var(--text-muted)',
              gap: '16px',
            }}
          >
            <Store size={48} />
            <p>暂无商店数据</p>
          </div>
        )}
      </div>

      {/* 详情面板 */}
      <AnimatePresence>
        {selectedApp && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.8)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '40px',
            }}
            onClick={() => setSelectedApp(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              style={{
                background: 'var(--bg-card)',
                borderRadius: '16px',
                maxWidth: '800px',
                width: '100%',
                maxHeight: '90vh',
                overflow: 'auto',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* 头部 */}
              <div
                style={{
                  padding: '20px',
                  borderBottom: '1px solid var(--border-default)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '16px',
                }}
              >
                <div
                  style={{
                    width: '80px',
                    height: '80px',
                    borderRadius: '16px',
                    background: 'var(--bg-secondary)',
                    overflow: 'hidden',
                    flexShrink: 0,
                  }}
                >
                  <img
                    src={getStoreIconUrl(selectedApp.folder_name)}
                    alt={selectedApp.name}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                    }}
                    onError={(e) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                </div>

                <div style={{ flex: 1 }}>
                  <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '4px' }}>
                    {selectedApp.track_name || selectedApp.name}
                  </h2>
                  <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                    {selectedApp.folder_name}
                  </p>

                  {selectedApp.rating && (
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        marginTop: '8px',
                      }}
                    >
                      <Star size={16} color="#f59e0b" fill="#f59e0b" />
                      <span style={{ fontSize: '14px', fontWeight: 500 }}>
                        {selectedApp.rating.toFixed(1)}
                      </span>
                      {selectedApp.rating_count && (
                        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                          ({formatNumber(selectedApp.rating_count)} 评分)
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => setSelectedApp(null)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    padding: '8px',
                  }}
                >
                  <X size={20} />
                </button>
              </div>

              {/* 数据指标 */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(4, 1fr)',
                  gap: '16px',
                  padding: '20px',
                  borderBottom: '1px solid var(--border-default)',
                }}
              >
                <div>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    月收入
                  </p>
                  <p style={{ fontSize: '18px', fontWeight: 600, color: 'var(--success)' }}>
                    {selectedApp.revenue ? formatCurrency(selectedApp.revenue) : '-'}
                  </p>
                </div>
                <div>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    下载量
                  </p>
                  <p style={{ fontSize: '18px', fontWeight: 600 }}>
                    {selectedApp.downloads ? formatNumber(selectedApp.downloads) : '-'}
                  </p>
                </div>
                <div>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    ARPU
                  </p>
                  <p style={{ fontSize: '18px', fontWeight: 600 }}>
                    {selectedApp.arpu ? `$${selectedApp.arpu.toFixed(2)}` : '-'}
                  </p>
                </div>
                <div>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    增长率
                  </p>
                  <p
                    style={{
                      fontSize: '18px',
                      fontWeight: 600,
                      color:
                        selectedApp.growth_rate && selectedApp.growth_rate > 0
                          ? 'var(--success)'
                          : selectedApp.growth_rate && selectedApp.growth_rate < 0
                            ? 'var(--danger)'
                            : 'inherit',
                    }}
                  >
                    {selectedApp.growth_rate
                      ? `${selectedApp.growth_rate > 0 ? '+' : ''}${selectedApp.growth_rate.toFixed(1)}%`
                      : '-'}
                  </p>
                </div>
              </div>

              {/* 描述 */}
              {selectedApp.description && (
                <div style={{ padding: '20px', borderBottom: '1px solid var(--border-default)' }}>
                  <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                    描述
                  </h3>
                  <p
                    style={{
                      fontSize: '13px',
                      color: 'var(--text-secondary)',
                      lineHeight: 1.6,
                    }}
                  >
                    {selectedApp.description}
                  </p>
                </div>
              )}

              {/* 商店截图 */}
              {selectedApp.store_screenshots && selectedApp.store_screenshots.length > 0 && (
                <div style={{ padding: '20px' }}>
                  <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px' }}>
                    商店截图
                  </h3>
                  <div
                    style={{
                      display: 'flex',
                      gap: '12px',
                      overflowX: 'auto',
                      paddingBottom: '8px',
                    }}
                  >
                    {selectedApp.store_screenshots.map((screenshot) => (
                      <div
                        key={screenshot}
                        style={{
                          width: '120px',
                          aspectRatio: '9/16',
                          borderRadius: '8px',
                          overflow: 'hidden',
                          background: 'var(--bg-secondary)',
                          flexShrink: 0,
                        }}
                      >
                        <img
                          src={getStoreScreenshotUrl(selectedApp.folder_name, screenshot)}
                          alt={screenshot}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                          }}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {detailLoading && (
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'center',
                    padding: '20px',
                  }}
                >
                  <div className="spinner" />
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AppLayout>
  )
}
