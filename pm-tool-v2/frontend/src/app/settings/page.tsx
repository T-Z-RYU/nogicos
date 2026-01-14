'use client'

import { useEffect, useState } from 'react'
import { AppLayout } from '@/components/layout'
import { FadeIn } from '@/components/motion'
import { Settings, Clock, Trash2 } from 'lucide-react'
import { getHistory, clearHistory, type HistoryItem } from '@/lib/api'

export default function SettingsPage() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [historyLoading, setHistoryLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const data = await getHistory(20)
      setHistory(data.items)
    } catch (error) {
      console.error('加载历史失败:', error)
    }
    setHistoryLoading(false)
  }

  const handleClearHistory = async () => {
    if (confirm('确定要清空历史记录吗？')) {
      await clearHistory()
      setHistory([])
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <AppLayout>
      {/* 顶栏 */}
      <div className="topbar">
        <h1 className="topbar-title">设置</h1>
      </div>

      {/* 内容区 */}
      <div className="content-area">
        <FadeIn delay={0.1}>
          <div style={{ maxWidth: '640px' }}>
            {/* 关于 */}
            <section style={{ marginBottom: 'var(--spacing-2xl)' }}>
              <h2 style={{ 
                fontSize: '14px', 
                fontWeight: 600, 
                color: 'var(--text-muted)',
                marginBottom: 'var(--spacing-lg)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}>
                关于
              </h2>
              
              <div className="screenshot-card" style={{ padding: 'var(--spacing-xl)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
                  <div style={{ 
                    width: '48px', 
                    height: '48px', 
                    borderRadius: 'var(--radius-lg)',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <Settings size={24} color="#fff" />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      PM Lab v2.0
                    </h3>
                    <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                      产品经理竞品分析截图工具
                    </p>
                  </div>
                </div>
                
                <p style={{ 
                  fontSize: '14px', 
                  color: 'var(--text-secondary)', 
                  lineHeight: 1.6,
                  marginBottom: 'var(--spacing-lg)',
                }}>
                  PM Lab 帮助产品经理高效管理和浏览竞品截图，支持按项目分类、阶段筛选、模块查看等功能。
                  采用 Linear 风格设计，带来流畅的使用体验。
                </p>

                <div style={{ 
                  display: 'flex', 
                  gap: 'var(--spacing-md)',
                  flexWrap: 'wrap',
                }}>
                  <span className="badge" style={{ 
                    background: 'rgba(102, 126, 234, 0.2)', 
                    color: '#667eea' 
                  }}>
                    Next.js 16
                  </span>
                  <span className="badge" style={{ 
                    background: 'rgba(34, 197, 94, 0.2)', 
                    color: '#22c55e' 
                  }}>
                    FastAPI
                  </span>
                  <span className="badge" style={{ 
                    background: 'rgba(245, 158, 11, 0.2)', 
                    color: '#f59e0b' 
                  }}>
                    Framer Motion
                  </span>
                  <span className="badge" style={{ 
                    background: 'rgba(156, 163, 175, 0.2)', 
                    color: '#9ca3af' 
                  }}>
                    Zustand
                  </span>
                </div>
              </div>
            </section>

            {/* 功能特性 */}
            <section style={{ marginBottom: 'var(--spacing-2xl)' }}>
              <h2 style={{ 
                fontSize: '14px', 
                fontWeight: 600, 
                color: 'var(--text-muted)',
                marginBottom: 'var(--spacing-lg)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}>
                功能特性
              </h2>
              
              <div style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                {[
                  { title: '项目管理', desc: '按项目分类管理截图，支持多数据源' },
                  { title: '智能分类', desc: '按阶段（Stage）和模块（Module）筛选截图' },
                  { title: '流畅浏览', desc: '全屏查看器，支持键盘导航' },
                  { title: '快速搜索', desc: '实时搜索，快速定位目标项目' },
                ].map((feature) => (
                  <div 
                    key={feature.title}
                    className="screenshot-card" 
                    style={{ 
                      padding: 'var(--spacing-lg)',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 'var(--spacing-md)',
                    }}
                  >
                    <div style={{ 
                      width: '8px', 
                      height: '8px', 
                      borderRadius: '50%',
                      background: 'var(--success)',
                      marginTop: '6px',
                      flexShrink: 0,
                    }} />
                    <div>
                      <h4 style={{ 
                        fontSize: '14px', 
                        fontWeight: 500, 
                        color: 'var(--text-primary)',
                        marginBottom: '4px',
                      }}>
                        {feature.title}
                      </h4>
                      <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                        {feature.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* 快捷键 */}
            <section style={{ marginBottom: 'var(--spacing-2xl)' }}>
              <h2 style={{ 
                fontSize: '14px', 
                fontWeight: 600, 
                color: 'var(--text-muted)',
                marginBottom: 'var(--spacing-lg)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}>
                快捷键
              </h2>
              
              <div className="screenshot-card" style={{ padding: 'var(--spacing-lg)' }}>
                <div style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                  {[
                    { key: '← →', action: '上一张 / 下一张截图' },
                    { key: '↑ ↓', action: '上一张 / 下一张截图' },
                    { key: 'Esc', action: '关闭查看器' },
                    { key: '1-0', action: '快速分类：选择阶段' },
                    { key: '空格', action: '快速分类：跳过' },
                  ].map((shortcut) => (
                    <div 
                      key={shortcut.key}
                      style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                        {shortcut.action}
                      </span>
                      <kbd style={{
                        padding: '4px 8px',
                        background: 'var(--bg-primary)',
                        border: '1px solid var(--border-default)',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '12px',
                        fontFamily: 'var(--font-mono)',
                        color: 'var(--text-muted)',
                      }}>
                        {shortcut.key}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* 操作历史 */}
            <section>
              <div style={{ 
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 'var(--spacing-lg)',
              }}>
                <h2 style={{ 
                  fontSize: '14px', 
                  fontWeight: 600, 
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}>
                  操作历史
                </h2>
                {history.length > 0 && (
                  <button
                    onClick={handleClearHistory}
                    className="btn-ghost"
                    style={{ padding: '4px 8px', fontSize: '12px' }}
                  >
                    <Trash2 size={12} />
                    清空
                  </button>
                )}
              </div>
              
              <div className="screenshot-card" style={{ padding: 'var(--spacing-lg)' }}>
                {historyLoading ? (
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'center', 
                    padding: '20px' 
                  }}>
                    <div className="spinner" style={{ width: '24px', height: '24px' }} />
                  </div>
                ) : history.length === 0 ? (
                  <div style={{ 
                    textAlign: 'center', 
                    color: 'var(--text-muted)',
                    padding: '20px',
                  }}>
                    暂无操作历史
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {history.map((item, index) => (
                      <div
                        key={index}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '12px',
                          padding: '8px 0',
                          borderBottom: index < history.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                        }}
                      >
                        <Clock size={14} style={{ 
                          color: 'var(--text-muted)', 
                          marginTop: '2px',
                          flexShrink: 0,
                        }} />
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <p style={{ 
                            fontSize: '13px', 
                            color: 'var(--text-primary)',
                            marginBottom: '2px',
                          }}>
                            {item.description}
                          </p>
                          <p style={{ 
                            fontSize: '11px', 
                            color: 'var(--text-muted)',
                          }}>
                            {formatTime(item.timestamp)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>
          </div>
        </FadeIn>
      </div>
    </AppLayout>
  )
}
