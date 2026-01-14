'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AppLayout } from '@/components/layout'
import { useProjectStore } from '@/store/project-store'
import { useOnboardingStore } from '@/store/onboarding-store'
import { getThumbnailUrl, getScreenshotUrl } from '@/lib/api'
import {
  Play,
  Flag,
  Save,
  Trash2,
  ChevronLeft,
  ChevronRight,
  X,
  Check,
  Folder,
  CheckCircle,
} from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

// Logo URL helper
function getLogoUrl(projectName: string): string {
  const appName = projectName.includes('/') 
    ? projectName.split('/').pop() 
    : projectName
  return `${API_BASE}/api/logo/${appName}`
}

export default function OnboardingPage() {
  const { projects, fetchProjects, loading: projectsLoading } = useProjectStore()
  const {
    screenshots,
    onboardingRange,
    previewStart,
    previewEnd,
    selectionMode,
    loading,
    saving,
    error,
    fetchData,
    setSelectionMode,
    selectScreenshot,
    saveRange,
    clearRange,
    reset,
  } = useOnboardingStore()

  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [viewerIndex, setViewerIndex] = useState<number | null>(null)

  // 加载项目列表
  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  // 切换项目时加载数据
  useEffect(() => {
    if (selectedProject) {
      fetchData(selectedProject)
    } else {
      reset()
    }
  }, [selectedProject, fetchData, reset])

  // 保存并刷新项目列表
  const handleSaveRange = async () => {
    if (!selectedProject) return
    await saveRange(selectedProject)
    // 保存成功后刷新项目列表，使已标记的项目移动到正确位置
    await fetchProjects()
  }

  // 清除并刷新项目列表
  const handleClearRange = async () => {
    if (!selectedProject) return
    await clearRange(selectedProject)
    // 清除成功后刷新项目列表
    await fetchProjects()
  }

  // 全局键盘监听
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape 取消选择模式或关闭查看器
      if (e.key === 'Escape') {
        if (viewerIndex !== null) {
          setViewerIndex(null)
        } else if (selectionMode) {
          setSelectionMode(null)
        }
      }
      // 左右箭头导航
      if (viewerIndex !== null) {
        if (e.key === 'ArrowLeft' && viewerIndex > 0) {
          setViewerIndex(viewerIndex - 1)
        }
        if (e.key === 'ArrowRight' && viewerIndex < screenshots.length - 1) {
          setViewerIndex(viewerIndex + 1)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [viewerIndex, selectionMode, screenshots.length, setSelectionMode])

  // 计算 Onboarding 截图数量
  const onboardingCount =
    previewStart >= 0 && previewEnd >= 0 ? previewEnd - previewStart + 1 : 0

  // 是否有未保存的更改
  const hasChanges =
    previewStart !== onboardingRange.start || previewEnd !== onboardingRange.end

  // 离开页面提示（如果有未保存的更改）
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasChanges) {
        e.preventDefault()
        e.returnValue = '你有未保存的更改，确定要离开吗？'
        return e.returnValue
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [hasChanges])

  // 判断截图是否在 Onboarding 范围内
  const isInRange = (index: number) => {
    if (previewStart < 0 || previewEnd < 0) return false
    return index >= previewStart && index <= previewEnd
  }

  // 判断是否为起点/终点
  const isStart = (index: number) => index === previewStart
  const isEnd = (index: number) => index === previewEnd

  // 筛选有 Onboarding 的项目 (onboarding_start >= 0 且 end >= 0 表示已标记，-1 表示未标记)
  const projectsWithOnboarding = projects.filter(
    (p) => p.onboarding_start >= 0 && p.onboarding_end >= 0
  )
  const projectsWithoutOnboarding = projects.filter(
    (p) => p.onboarding_start < 0 || p.onboarding_end < 0
  )

  return (
    <AppLayout>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* 左侧项目列表 */}
        <div
          style={{
            width: '260px',
            background: '#0a0a0a',
            borderRight: '1px solid rgba(255,255,255,0.06)',
            display: 'flex',
            flexDirection: 'column',
            flexShrink: 0,
            overflow: 'hidden',
          }}
        >
          {/* 标题 */}
          <div
            style={{
              padding: '16px',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <h3
              style={{
                fontSize: '12px',
                color: '#6b7280',
                letterSpacing: '0.02em',
                fontWeight: 500,
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              项目列表 <span style={{ opacity: 0.5 }}>Projects</span>
            </h3>
          </div>

          {/* 项目列表 */}
          <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
            {/* 已标记的项目 */}
            {projectsWithOnboarding.length > 0 && (
              <div style={{ marginBottom: '16px' }}>
                <div
                  style={{
                    fontSize: '10px',
                    color: '#22c55e',
                    padding: '4px 8px',
                    marginBottom: '4px',
                    fontWeight: 500,
                  }}
                >
                  已标记 ({projectsWithOnboarding.length})
                </div>
                {projectsWithOnboarding.map((project) => (
                  <button
                    key={project.name}
                    onClick={() => setSelectedProject(project.name)}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      background:
                        selectedProject === project.name
                          ? 'rgba(255,255,255,0.08)'
                          : 'transparent',
                      border: 'none',
                      borderRadius: '6px',
                      color:
                        selectedProject === project.name ? '#fff' : '#9ca3af',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      fontSize: '13px',
                      textAlign: 'left',
                      marginBottom: '2px',
                      borderLeft:
                        selectedProject === project.name
                          ? '2px solid #22c55e'
                          : '2px solid transparent',
                    }}
                  >
                    {/* App Logo */}
                    <div style={{ position: 'relative', flexShrink: 0 }}>
                      <img
                        src={getLogoUrl(project.name)}
                        alt={project.display_name}
                        style={{
                          width: '28px',
                          height: '28px',
                          borderRadius: '6px',
                          objectFit: 'cover',
                        }}
                        onError={(e) => {
                          const target = e.target as HTMLImageElement
                          target.style.display = 'none'
                        }}
                      />
                      <CheckCircle
                        size={12}
                        style={{
                          position: 'absolute',
                          bottom: '-2px',
                          right: '-2px',
                          color: '#22c55e',
                          background: '#0a0a0a',
                          borderRadius: '50%',
                        }}
                      />
                    </div>
                    <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {project.display_name}
                    </span>
                    <span
                      style={{
                        fontSize: '11px',
                        color: '#6b7280',
                        flexShrink: 0,
                      }}
                    >
                      {project.onboarding_end !== undefined && project.onboarding_start !== undefined
                        ? project.onboarding_end - project.onboarding_start + 1
                        : 0}
                    </span>
                  </button>
                ))}
              </div>
            )}

            {/* 未标记的项目 */}
            {projectsWithoutOnboarding.length > 0 && (
              <div>
                <div
                  style={{
                    fontSize: '10px',
                    color: '#6b7280',
                    padding: '4px 8px',
                    marginBottom: '4px',
                    fontWeight: 500,
                  }}
                >
                  未标记 ({projectsWithoutOnboarding.length})
                </div>
                {projectsWithoutOnboarding.map((project) => (
                  <button
                    key={project.name}
                    onClick={() => setSelectedProject(project.name)}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      background:
                        selectedProject === project.name
                          ? 'rgba(255,255,255,0.08)'
                          : 'transparent',
                      border: 'none',
                      borderRadius: '6px',
                      color:
                        selectedProject === project.name ? '#fff' : '#6b7280',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      fontSize: '13px',
                      textAlign: 'left',
                      marginBottom: '2px',
                      borderLeft:
                        selectedProject === project.name
                          ? '2px solid #fff'
                          : '2px solid transparent',
                    }}
                  >
                    {/* App Logo */}
                    <img
                      src={getLogoUrl(project.name)}
                      alt={project.display_name}
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '6px',
                        objectFit: 'cover',
                        opacity: 0.7,
                        flexShrink: 0,
                      }}
                      onError={(e) => {
                        const target = e.target as HTMLImageElement
                        target.style.display = 'none'
                      }}
                    />
                    <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {project.display_name}
                    </span>
                    <span
                      style={{
                        fontSize: '11px',
                        color: '#4b5563',
                        flexShrink: 0,
                      }}
                    >
                      {project.screen_count}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* 统计信息 */}
          <div
            style={{
              padding: '12px 16px',
              borderTop: '1px solid rgba(255,255,255,0.06)',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px',
              fontSize: '11px',
              color: '#6b7280',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>项目 Projects</span>
              <span style={{ color: '#fff' }}>{projects.length}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>已标记 Marked</span>
              <span style={{ color: '#22c55e' }}>
                {projectsWithOnboarding.length}
              </span>
            </div>
          </div>
        </div>

        {/* 右侧主内容区 */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* 顶栏 */}
          <div className="topbar">
            <h1 className="topbar-title">
              {selectedProject ? (
                <>
                  <strong>
                    {selectedProject
                      .replace('downloads_2024/', '')
                      .replace('[SD] ', '')
                      .replace('[Mobbin] ', '')}
                  </strong>
                  <span style={{ marginLeft: '8px', fontSize: '12px', color: '#6b7280' }}>
                    {screenshots.length} 张截图
                  </span>
                </>
              ) : (
                'Onboarding 分析'
              )}
            </h1>
            <div style={{ flex: 1 }} />

            {/* 操作按钮 */}
            {selectedProject && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  className={`btn-ghost ${selectionMode === 'start' ? 'active' : ''}`}
                  onClick={() =>
                    setSelectionMode(selectionMode === 'start' ? null : 'start')
                  }
                  title="设置起点"
                >
                  <Play size={16} />
                  起点
                </button>
                <button
                  className={`btn-ghost ${selectionMode === 'end' ? 'active' : ''}`}
                  onClick={() =>
                    setSelectionMode(selectionMode === 'end' ? null : 'end')
                  }
                  title="设置终点"
                >
                  <Flag size={16} />
                  终点
                </button>

                {onboardingCount > 0 && (
                  <>
                    <div
                      style={{
                        padding: '8px 12px',
                        background: 'rgba(34, 197, 94, 0.2)',
                        color: '#22c55e',
                        borderRadius: '6px',
                        fontSize: '13px',
                        fontWeight: 500,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      <Play size={12} />#{previewStart + 1}
                      <span style={{ color: '#6b7280' }}>→</span>
                      <Flag size={12} style={{ color: '#f59e0b' }} />#{previewEnd + 1}
                      <span style={{ color: '#9ca3af', marginLeft: '4px' }}>
                        ({onboardingCount}张)
                      </span>
                    </div>

                    <button
                      className="btn-ghost"
                      onClick={handleSaveRange}
                      disabled={saving || !hasChanges}
                      style={{
                        background: hasChanges ? 'var(--success)' : undefined,
                        color: hasChanges ? '#fff' : undefined,
                      }}
                    >
                      <Save size={16} />
                      {saving ? '保存中...' : '保存'}
                    </button>

                    <button
                      className="btn-ghost"
                      onClick={handleClearRange}
                      disabled={saving}
                      style={{ color: 'var(--danger)' }}
                    >
                      <Trash2 size={16} />
                      清除
                    </button>
                  </>
                )}
              </div>
            )}
          </div>

          {/* 内容区 */}
          <div className="content-area" style={{ flex: 1, overflow: 'auto' }}>
            {/* 未选择项目 */}
            {!selectedProject && (
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
                <Play size={48} />
                <p>从左侧选择一个项目来标记 Onboarding 范围</p>
              </div>
            )}

            {/* 加载中 */}
            {selectedProject && loading && (
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
                  padding: '12px 16px',
                  background: 'rgba(239, 68, 68, 0.2)',
                  color: 'var(--danger)',
                  borderRadius: '8px',
                  marginBottom: '16px',
                }}
              >
                {error}
              </div>
            )}

            {/* 选择模式提示 */}
            {selectionMode && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                style={{
                  padding: '12px 16px',
                  background:
                    selectionMode === 'start'
                      ? 'rgba(34, 197, 94, 0.2)'
                      : 'rgba(245, 158, 11, 0.2)',
                  color: selectionMode === 'start' ? '#22c55e' : '#f59e0b',
                  borderRadius: '8px',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                {selectionMode === 'start' ? (
                  <Play size={18} />
                ) : (
                  <Flag size={18} />
                )}
                点击截图设置{selectionMode === 'start' ? '起点' : '终点'}
                <button
                  onClick={() => setSelectionMode(null)}
                  style={{
                    marginLeft: 'auto',
                    background: 'none',
                    border: 'none',
                    color: 'inherit',
                    cursor: 'pointer',
                    padding: '4px',
                  }}
                >
                  <X size={16} />
                </button>
              </motion.div>
            )}

            {/* 截图网格 */}
            {selectedProject && !loading && screenshots.length > 0 && (
              <motion.div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
                  gap: '10px',
                }}
                initial="hidden"
                animate="visible"
                variants={{
                  visible: { transition: { staggerChildren: 0.01 } },
                }}
              >
                {screenshots.map((screenshot, index) => (
                  <motion.div
                    key={screenshot.filename}
                    variants={{
                      hidden: { opacity: 0, y: 10 },
                      visible: { opacity: 1, y: 0 },
                    }}
                    style={{
                      position: 'relative',
                      cursor: selectionMode ? 'pointer' : 'default',
                    }}
                    onClick={async () => {
                      if (selectionMode && selectedProject) {
                        selectScreenshot(index, selectedProject)
                        // 自动保存后刷新项目列表
                        await fetchProjects()
                      } else {
                        setViewerIndex(index)
                      }
                    }}
                  >
                    <div
                      className="screenshot-card"
                      style={{
                        border: isInRange(index)
                          ? '2px solid #22c55e'
                          : selectionMode
                            ? '2px solid rgba(255,255,255,0.1)'
                            : '2px solid transparent',
                        borderRadius: '6px',
                        opacity: isInRange(index) || selectionMode ? 1 : 0.6,
                        transition: 'all 0.2s ease',
                        cursor: 'pointer',
                      }}
                    >
                      <div
                        style={{
                          aspectRatio: '9/16',
                          overflow: 'hidden',
                          background: 'var(--bg-secondary)',
                          borderRadius: '4px',
                        }}
                      >
                        <img
                          src={getThumbnailUrl(
                            selectedProject,
                            screenshot.filename,
                            'small'
                          )}
                          alt={screenshot.filename}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                          }}
                          loading="lazy"
                        />
                      </div>

                      {/* 索引 */}
                      <div
                        style={{
                          position: 'absolute',
                          top: '4px',
                          left: '4px',
                          padding: '2px 6px',
                          background: 'rgba(0, 0, 0, 0.7)',
                          borderRadius: '4px',
                          fontSize: '10px',
                          color: 'var(--text-secondary)',
                          fontFamily: 'var(--font-mono)',
                        }}
                      >
                        {String(index + 1).padStart(4, '0')}
                      </div>

                      {/* 起点/终点标记 */}
                      {isStart(index) && (
                        <div
                          style={{
                            position: 'absolute',
                            bottom: '4px',
                            left: '4px',
                            padding: '2px 6px',
                            background: '#22c55e',
                            borderRadius: '4px',
                            fontSize: '9px',
                            color: '#fff',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '2px',
                          }}
                        >
                          <Play size={8} /> START
                        </div>
                      )}
                      {isEnd(index) && (
                        <div
                          style={{
                            position: 'absolute',
                            bottom: '4px',
                            left: '4px',
                            padding: '2px 6px',
                            background: '#f59e0b',
                            borderRadius: '4px',
                            fontSize: '9px',
                            color: '#fff',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '2px',
                          }}
                        >
                          <Flag size={8} /> END
                        </div>
                      )}

                      {/* Onboarding 范围内标记 */}
                      {isInRange(index) && !isStart(index) && !isEnd(index) && (
                        <div
                          style={{
                            position: 'absolute',
                            top: '4px',
                            right: '4px',
                            width: '8px',
                            height: '8px',
                            background: '#22c55e',
                            borderRadius: '50%',
                          }}
                        />
                      )}
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}

            {/* 空状态 */}
            {selectedProject && !loading && screenshots.length === 0 && (
              <div
                style={{
                  display: 'flex',
                  height: '256px',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--text-muted)',
                }}
              >
                该项目没有截图
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 全屏查看器 */}
      <AnimatePresence>
        {viewerIndex !== null && selectedProject && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.95)',
              zIndex: 1000,
              display: 'flex',
              flexDirection: 'column',
            }}
            onClick={() => setViewerIndex(null)}
          >
            {/* Header */}
            <div
              style={{
                padding: '16px 20px',
                background: 'var(--bg-secondary)',
                borderBottom: '1px solid var(--border-default)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontFamily: 'var(--font-mono)' }}>
                  #{viewerIndex + 1} / {screenshots.length}
                </span>
                {isInRange(viewerIndex) && (
                  <span
                    style={{
                      padding: '4px 8px',
                      background: 'rgba(34, 197, 94, 0.2)',
                      color: '#22c55e',
                      borderRadius: '4px',
                      fontSize: '11px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <Check size={12} /> Onboarding
                  </span>
                )}
                {isStart(viewerIndex) && (
                  <span
                    style={{
                      padding: '4px 8px',
                      background: '#22c55e',
                      color: '#fff',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 600,
                    }}
                  >
                    START
                  </span>
                )}
                {isEnd(viewerIndex) && (
                  <span
                    style={{
                      padding: '4px 8px',
                      background: '#f59e0b',
                      color: '#fff',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 600,
                    }}
                  >
                    END
                  </span>
                )}
              </div>
              <button
                onClick={() => setViewerIndex(null)}
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

            {/* Image */}
            <div
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '60px 80px',
                position: 'relative',
                minHeight: 0,
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <motion.img
                key={viewerIndex}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.15 }}
                src={getScreenshotUrl(
                  selectedProject,
                  screenshots[viewerIndex].filename
                )}
                alt={screenshots[viewerIndex].filename}
                style={{
                  height: '100%',
                  width: 'auto',
                  maxWidth: '100%',
                  objectFit: 'contain',
                  borderRadius: '16px',
                  boxShadow: '0 20px 60px rgba(0,0,0,0.6)',
                }}
              />

              {/* Navigation */}
              <button
                style={{
                  position: 'absolute',
                  left: '20px',
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: 'none',
                  color: '#fff',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: viewerIndex === 0 ? 0.3 : 1,
                }}
                disabled={viewerIndex === 0}
                onClick={(e) => {
                  e.stopPropagation()
                  setViewerIndex(viewerIndex - 1)
                }}
              >
                <ChevronLeft size={24} />
              </button>

              <button
                style={{
                  position: 'absolute',
                  right: '20px',
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: 'none',
                  color: '#fff',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: viewerIndex === screenshots.length - 1 ? 0.3 : 1,
                }}
                disabled={viewerIndex === screenshots.length - 1}
                onClick={(e) => {
                  e.stopPropagation()
                  setViewerIndex(viewerIndex + 1)
                }}
              >
                <ChevronRight size={24} />
              </button>
            </div>

            {/* Footer hint */}
            <div
              style={{
                padding: '12px',
                textAlign: 'center',
                color: '#6b7280',
                fontSize: '12px',
              }}
            >
              使用 ← → 键导航，Esc 关闭
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </AppLayout>
  )
}
