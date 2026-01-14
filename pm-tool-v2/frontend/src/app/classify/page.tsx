'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AppLayout } from '@/components/layout'
import { useProjectStore } from '@/store/project-store'
import { useClassifyStore } from '@/store/classify-store'
import { getThumbnailUrl } from '@/lib/api'
import {
  Tags,
  Check,
  X,
  ChevronDown,
  ChevronRight,
  Square,
  CheckSquare,
} from 'lucide-react'

// 阶段配色
const stageColors: Record<string, string> = {
  Onboarding: '#22c55e',
  Registration: '#3b82f6',
  Home: '#8b5cf6',
  Browse: '#f59e0b',
  Search: '#06b6d4',
  Detail: '#ec4899',
  Profile: '#6366f1',
  Settings: '#64748b',
  Paywall: '#ef4444',
  Checkout: '#14b8a6',
  Other: '#71717a',
}

export default function ClassifyPage() {
  const { projects, fetchProjects, loading: projectsLoading } = useProjectStore()
  const {
    unclassified,
    classified,
    taxonomy,
    loading,
    saving,
    error,
    selectedFiles,
    fetchData,
    toggleSelect,
    selectAll,
    deselectAll,
    assignToStage,
    removeFromStage,
    reset,
  } = useClassifyStore()

  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set())

  // 加载项目列表
  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  // 切换项目时加载数据
  useEffect(() => {
    if (selectedProject) {
      fetchData(selectedProject)
      // 默认展开所有阶段
      if (taxonomy) {
        setExpandedStages(new Set(taxonomy.stages))
      }
    } else {
      reset()
    }
  }, [selectedProject, fetchData, reset])

  // 切换阶段展开状态
  const toggleStage = (stage: string) => {
    const newExpanded = new Set(expandedStages)
    if (newExpanded.has(stage)) {
      newExpanded.delete(stage)
    } else {
      newExpanded.add(stage)
    }
    setExpandedStages(newExpanded)
  }

  // 分配选中截图到阶段
  const handleAssignSelected = (stage: string) => {
    if (selectedProject && selectedFiles.size > 0) {
      assignToStage(selectedProject, Array.from(selectedFiles), stage)
    }
  }

  return (
    <AppLayout>
      {/* 顶栏 */}
      <div className="topbar">
        <h1 className="topbar-title">手动分类</h1>
        <div style={{ flex: 1 }} />

        {/* 项目选择器 */}
        <select
          value={selectedProject || ''}
          onChange={(e) => setSelectedProject(e.target.value || null)}
          style={{
            padding: '8px 12px',
            borderRadius: '6px',
            background: 'var(--bg-secondary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-default)',
            fontSize: '14px',
            minWidth: '200px',
            cursor: 'pointer',
          }}
        >
          <option value="">选择项目...</option>
          {projects.map((project) => (
            <option key={project.name} value={project.name}>
              {project.display_name} ({project.screen_count})
            </option>
          ))}
        </select>

        {/* 选择操作 */}
        {selectedProject && unclassified.length > 0 && (
          <div style={{ display: 'flex', gap: '8px', marginLeft: '16px' }}>
            <button
              className="btn-ghost"
              onClick={() => (selectedFiles.size > 0 ? deselectAll() : selectAll())}
            >
              {selectedFiles.size > 0 ? (
                <>
                  <X size={16} />
                  取消 ({selectedFiles.size})
                </>
              ) : (
                <>
                  <CheckSquare size={16} />
                  全选
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* 内容区 - 两栏布局 */}
      <div className="content-area" style={{ display: 'flex', gap: '20px', overflow: 'hidden' }}>
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
              width: '100%',
            }}
          >
            <Tags size={48} />
            <p>请选择一个项目来分类截图</p>
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
              width: '100%',
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
              width: '100%',
            }}
          >
            {error}
          </div>
        )}

        {/* 左侧：未分类截图 */}
        {selectedProject && !loading && (
          <div
            style={{
              width: '280px',
              flexShrink: 0,
              background: 'var(--bg-card)',
              borderRadius: '8px',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                padding: '12px 16px',
                borderBottom: '1px solid var(--border-default)',
                fontWeight: 500,
              }}
            >
              未分类 ({unclassified.length})
            </div>
            <div
              style={{
                flex: 1,
                overflow: 'auto',
                padding: '12px',
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '8px',
                alignContent: 'start',
              }}
            >
              {unclassified.map((screenshot) => (
                <motion.div
                  key={screenshot.filename}
                  className="screenshot-card"
                  style={{
                    cursor: 'pointer',
                    outline: selectedFiles.has(screenshot.filename)
                      ? '2px solid var(--success)'
                      : 'none',
                    outlineOffset: '-2px',
                  }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => toggleSelect(screenshot.filename)}
                >
                  <div
                    style={{
                      aspectRatio: '9/16',
                      overflow: 'hidden',
                      background: 'var(--bg-secondary)',
                      position: 'relative',
                    }}
                  >
                    <img
                      src={getThumbnailUrl(selectedProject, screenshot.filename, 'small')}
                      alt={screenshot.filename}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                      }}
                      loading="lazy"
                    />
                    <div
                      style={{
                        position: 'absolute',
                        bottom: '2px',
                        right: '2px',
                        padding: '1px 4px',
                        background: 'rgba(0, 0, 0, 0.7)',
                        borderRadius: '3px',
                        fontSize: '9px',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      #{screenshot.index}
                    </div>
                  </div>
                </motion.div>
              ))}
              {unclassified.length === 0 && (
                <div
                  style={{
                    gridColumn: '1 / -1',
                    textAlign: 'center',
                    color: 'var(--text-muted)',
                    padding: '20px',
                  }}
                >
                  全部已分类 ✓
                </div>
              )}
            </div>
          </div>
        )}

        {/* 右侧：阶段分组 */}
        {selectedProject && !loading && taxonomy && (
          <div style={{ flex: 1, overflow: 'auto' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {taxonomy.stages.map((stage) => {
                const stageScreenshots = classified[stage] || []
                const isExpanded = expandedStages.has(stage)
                const color = stageColors[stage] || '#71717a'

                return (
                  <div
                    key={stage}
                    style={{
                      background: 'var(--bg-card)',
                      borderRadius: '8px',
                      overflow: 'hidden',
                    }}
                  >
                    {/* 阶段头部 */}
                    <div
                      style={{
                        padding: '12px 16px',
                        background: 'var(--bg-secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        cursor: 'pointer',
                      }}
                      onClick={() => toggleStage(stage)}
                    >
                      {isExpanded ? (
                        <ChevronDown size={18} />
                      ) : (
                        <ChevronRight size={18} />
                      )}
                      <div
                        style={{
                          width: '12px',
                          height: '12px',
                          borderRadius: '50%',
                          background: color,
                        }}
                      />
                      <span style={{ fontWeight: 500, flex: 1 }}>{stage}</span>
                      <span
                        style={{
                          padding: '2px 8px',
                          background: `${color}33`,
                          color: color,
                          borderRadius: '10px',
                          fontSize: '12px',
                        }}
                      >
                        {stageScreenshots.length}
                      </span>
                      {/* 快速分配按钮 */}
                      {selectedFiles.size > 0 && (
                        <button
                          className="btn-ghost"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleAssignSelected(stage)
                          }}
                          disabled={saving}
                          style={{
                            padding: '4px 8px',
                            fontSize: '12px',
                            background: color,
                            color: '#fff',
                          }}
                        >
                          <Check size={12} />
                          分配到此
                        </button>
                      )}
                    </div>

                    {/* 阶段内容 */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: 'auto' }}
                          exit={{ height: 0 }}
                          style={{ overflow: 'hidden' }}
                        >
                          <div
                            style={{
                              padding: '12px',
                              minHeight: '60px',
                              display: 'flex',
                              flexWrap: 'wrap',
                              gap: '8px',
                              alignContent: 'start',
                            }}
                          >
                            {stageScreenshots.map((screenshot) => (
                              <div
                                key={screenshot.filename}
                                style={{
                                  width: '50px',
                                  position: 'relative',
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
                                {/* 移除按钮 */}
                                <button
                                  onClick={() =>
                                    selectedProject &&
                                    removeFromStage(selectedProject, screenshot.filename)
                                  }
                                  style={{
                                    position: 'absolute',
                                    top: '-4px',
                                    right: '-4px',
                                    width: '16px',
                                    height: '16px',
                                    borderRadius: '50%',
                                    background: 'var(--danger)',
                                    border: 'none',
                                    color: '#fff',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '10px',
                                    opacity: 0,
                                    transition: 'opacity 0.2s',
                                  }}
                                  className="remove-btn"
                                >
                                  <X size={10} />
                                </button>
                              </div>
                            ))}
                            {stageScreenshots.length === 0 && (
                              <div
                                style={{
                                  color: 'var(--text-muted)',
                                  fontSize: '13px',
                                  width: '100%',
                                  textAlign: 'center',
                                  padding: '10px',
                                }}
                              >
                                拖拽或选择截图分配到此阶段
                              </div>
                            )}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .remove-btn:hover,
        div:hover > .remove-btn {
          opacity: 1 !important;
        }
      `}</style>
    </AppLayout>
  )
}
