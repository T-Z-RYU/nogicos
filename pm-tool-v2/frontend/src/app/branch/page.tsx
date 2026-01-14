'use client'

import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AppLayout } from '@/components/layout'
import { useProjectStore } from '@/store/project-store'
import { useBranchStore, BRANCH_COLORS } from '@/store/branch-store'
import { getThumbnailUrl } from '@/lib/api'
import {
  GitFork,
  GitMerge,
  GitBranch,
  Plus,
  Trash2,
  X,
  Check,
  ChevronDown,
  Palette,
  Eye,
  EyeOff,
  LayoutGrid,
  Network,
  ArrowRight,
  ArrowUp,
} from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

// Logo URL helper
function getLogoUrl(projectName: string): string {
  const appName = projectName.includes('/') 
    ? projectName.split('/').pop() 
    : projectName
  return `${API_BASE}/api/logo/${appName}`
}

export default function BranchPage() {
  const { projects, fetchProjects, loading: projectsLoading } = useProjectStore()
  const {
    branchData,
    screenshots,
    onboardingRange,
    editMode,
    selectedBranch,
    pendingBranchScreens,
    loading,
    saving,
    error,
    fetchData,
    setEditMode,
    toggleForkPoint,
    toggleMergePoint,
    toggleScreenInPending,
    clearPendingScreens,
    createBranch,
    removeBranch,
    selectBranch,
    clearAll,
    reset,
  } = useBranchStore()

  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [showBranchDialog, setShowBranchDialog] = useState(false)
  const [newBranchName, setNewBranchName] = useState('')
  const [newBranchColor, setNewBranchColor] = useState(BRANCH_COLORS[0].value)
  const [newBranchForkFrom, setNewBranchForkFrom] = useState<number>(-1)
  const [newBranchMergeTo, setNewBranchMergeTo] = useState<number | null>(null)
  const [showAllScreens, setShowAllScreens] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'flow'>('grid')

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

  // 判断截图类型
  const getScreenType = useCallback((index: number) => {
    const isForkPoint = branchData.fork_points.some(fp => fp.index === index)
    const isMergePoint = branchData.merge_points.includes(index)
    const inBranch = branchData.branches.find(b => b.screens.includes(index))
    const isPending = pendingBranchScreens.includes(index)
    
    return { isForkPoint, isMergePoint, inBranch, isPending }
  }, [branchData, pendingBranchScreens])

  // 获取截图边框颜色
  const getScreenBorderColor = useCallback((index: number) => {
    const { isForkPoint, isMergePoint, inBranch, isPending } = getScreenType(index)
    
    if (isPending) return '#f59e0b' // 待添加到分支
    if (isForkPoint) return '#ef4444' // 分支点 - 红色
    if (isMergePoint) return '#8b5cf6' // 汇合点 - 紫色
    if (inBranch) return inBranch.color // 分支颜色
    if (selectedBranch) {
      const branch = branchData.branches.find(b => b.id === selectedBranch)
      if (branch && !branch.screens.includes(index)) {
        return 'rgba(255,255,255,0.1)' // 未选中分支的截图变暗
      }
    }
    return 'rgba(255,255,255,0.15)' // 默认
  }, [getScreenType, selectedBranch, branchData.branches])

  // 处理截图点击
  const handleScreenClick = useCallback((index: number) => {
    if (!selectedProject) return

    switch (editMode) {
      case 'fork':
        toggleForkPoint(selectedProject, index)
        break
      case 'merge':
        toggleMergePoint(selectedProject, index)
        break
      case 'branch':
        toggleScreenInPending(index)
        break
    }
  }, [editMode, selectedProject, toggleForkPoint, toggleMergePoint, toggleScreenInPending])

  // 打开创建分支对话框
  const openBranchDialog = useCallback(() => {
    if (branchData.fork_points.length === 0) {
      alert('请先标记至少一个分支点')
      return
    }
    setNewBranchForkFrom(branchData.fork_points[0].index)
    setNewBranchMergeTo(branchData.merge_points[0] ?? null)
    setShowBranchDialog(true)
  }, [branchData])

  // 创建分支
  const handleCreateBranch = useCallback(async () => {
    if (!selectedProject || !newBranchName.trim()) return
    
    await createBranch(
      selectedProject,
      newBranchName.trim(),
      newBranchColor,
      newBranchForkFrom,
      newBranchMergeTo
    )
    
    setShowBranchDialog(false)
    setNewBranchName('')
    setNewBranchColor(BRANCH_COLORS[0].value)
  }, [selectedProject, newBranchName, newBranchColor, newBranchForkFrom, newBranchMergeTo, createBranch])

  // 过滤显示的截图
  const displayScreenshots = showAllScreens 
    ? screenshots 
    : screenshots.filter((_, index) => {
        const { inBranch, isForkPoint, isMergePoint } = getScreenType(index)
        return inBranch || isForkPoint || isMergePoint
      })

  return (
    <AppLayout>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* 主内容区 */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* 顶部工具栏 */}
          <div
            className="toolbar"
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--border-default)',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <h2 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>
              分支流程 <span style={{ color: 'var(--text-secondary)', fontWeight: 400 }}>Branch Flow</span>
            </h2>

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

            <div style={{ flex: 1 }} />

            {/* 编辑模式按钮 */}
            {selectedProject && (
              <>
                <button
                  className={`btn-ghost ${editMode === 'fork' ? 'active' : ''}`}
                  onClick={() => setEditMode(editMode === 'fork' ? 'none' : 'fork')}
                  style={{
                    background: editMode === 'fork' ? 'rgba(239, 68, 68, 0.2)' : undefined,
                    borderColor: editMode === 'fork' ? '#ef4444' : undefined,
                  }}
                >
                  <GitFork size={16} />
                  分支点
                </button>

                <button
                  className={`btn-ghost ${editMode === 'merge' ? 'active' : ''}`}
                  onClick={() => setEditMode(editMode === 'merge' ? 'none' : 'merge')}
                  style={{
                    background: editMode === 'merge' ? 'rgba(139, 92, 246, 0.2)' : undefined,
                    borderColor: editMode === 'merge' ? '#8b5cf6' : undefined,
                  }}
                >
                  <GitMerge size={16} />
                  汇合点
                </button>

                <button
                  className={`btn-ghost ${editMode === 'branch' ? 'active' : ''}`}
                  onClick={() => {
                    if (editMode === 'branch') {
                      setEditMode('none')
                      clearPendingScreens()
                    } else {
                      setEditMode('branch')
                    }
                  }}
                  style={{
                    background: editMode === 'branch' ? 'rgba(245, 158, 11, 0.2)' : undefined,
                    borderColor: editMode === 'branch' ? '#f59e0b' : undefined,
                  }}
                >
                  <GitBranch size={16} />
                  选择分支
                </button>

                {editMode === 'branch' && pendingBranchScreens.length > 0 && (
                  <button
                    className="btn-primary"
                    onClick={openBranchDialog}
                  >
                    <Plus size={16} />
                    创建分支 ({pendingBranchScreens.length})
                  </button>
                )}

                <button
                  className="btn-ghost"
                  onClick={() => setShowAllScreens(!showAllScreens)}
                  title={showAllScreens ? '只显示标记的截图' : '显示所有截图'}
                >
                  {showAllScreens ? <Eye size={16} /> : <EyeOff size={16} />}
                </button>

                {/* 视图切换 */}
                <div style={{ 
                  display: 'flex', 
                  gap: '2px', 
                  background: 'var(--bg-secondary)', 
                  borderRadius: '6px', 
                  padding: '2px',
                  marginLeft: '8px',
                }}>
                  <button
                    className="btn-ghost"
                    onClick={() => setViewMode('grid')}
                    title="网格视图"
                    style={{
                      background: viewMode === 'grid' ? 'var(--bg-tertiary)' : 'transparent',
                      padding: '6px 10px',
                    }}
                  >
                    <LayoutGrid size={16} />
                  </button>
                  <button
                    className="btn-ghost"
                    onClick={() => setViewMode('flow')}
                    title="流程图视图"
                    style={{
                      background: viewMode === 'flow' ? 'var(--bg-tertiary)' : 'transparent',
                      padding: '6px 10px',
                    }}
                  >
                    <Network size={16} />
                  </button>
                </div>
              </>
            )}
          </div>

          {/* 内容区 */}
          <div className="content-area" style={{ flex: 1, overflow: 'auto', padding: '16px' }}>
            {/* 未选择项目 */}
            {!selectedProject && (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '100%',
                color: 'var(--text-secondary)',
              }}>
                请选择一个项目开始标记分支流程
              </div>
            )}

            {/* 加载中 */}
            {selectedProject && loading && (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '100%',
                color: 'var(--text-secondary)',
              }}>
                加载中...
              </div>
            )}

            {/* 流程图视图 - 泳道式布局 */}
            {selectedProject && !loading && viewMode === 'flow' && branchData.branches.length > 0 && (
              <div style={{ padding: '20px' }}>
                {/* 主流程 - 显示所有截图 */}
                <div style={{ 
                  marginBottom: '24px',
                  background: 'var(--bg-secondary)',
                  borderRadius: '12px',
                  padding: '16px',
                }}>
                  <h3 style={{ 
                    fontSize: '13px', 
                    color: 'var(--text-secondary)', 
                    marginBottom: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}>
                    <span style={{ fontSize: '16px' }}>📍</span> 主流程 (Onboarding)
                    {onboardingRange.start >= 0 && onboardingRange.end >= 0 && (
                      <span style={{ fontSize: '11px', opacity: 0.6, marginLeft: '4px' }}>
                        #{onboardingRange.start + 1} - #{onboardingRange.end + 1}
                      </span>
                    )}
                  </h3>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'flex-start', 
                    gap: '4px',
                    flexWrap: 'wrap',
                  }}>
                    {(() => {
                      // 计算 Onboarding 范围内的截图
                      const startIdx = onboardingRange.start >= 0 ? onboardingRange.start : 0
                      const endIdx = onboardingRange.end >= 0 ? onboardingRange.end + 1 : screenshots.length
                      const onboardingScreenshots = screenshots.slice(startIdx, endIdx)
                      
                      return onboardingScreenshots.map((screenshot, displayIndex) => {
                        // 真实索引（用于分支点判断等）
                        const realIndex = startIdx + displayIndex
                        const { isForkPoint, isMergePoint, inBranch } = getScreenType(realIndex)
                        const branchesFromHere = branchData.branches.filter(b => b.fork_from === realIndex)
                      
                        return (
                        <div key={screenshot.filename} style={{ 
                          display: 'flex', 
                          flexDirection: 'column',
                          alignItems: 'center', 
                          gap: '2px',
                        }}>
                          {/* 截图容器 */}
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <div style={{ position: 'relative' }}>
                              <img
                                src={getThumbnailUrl(selectedProject, screenshot.filename, 'small')}
                                alt={screenshot.filename}
                                style={{
                                  width: '45px',
                                  height: '80px',
                                  objectFit: 'cover',
                                  borderRadius: '4px',
                                  border: isForkPoint 
                                    ? '2px solid #ef4444' 
                                    : isMergePoint 
                                      ? '2px solid #8b5cf6' 
                                      : inBranch 
                                        ? `2px solid ${inBranch.color}` 
                                        : '1px solid var(--border-default)',
                                  opacity: inBranch ? 0.5 : 1,
                                }}
                              />
                              {/* 序号标签 */}
                              <div style={{
                                position: 'absolute',
                                top: '2px',
                                left: '2px',
                                fontSize: '9px',
                                background: inBranch ? inBranch.color : 'rgba(0,0,0,0.7)',
                                color: '#fff',
                                padding: '1px 3px',
                                borderRadius: '2px',
                              }}>
                                {realIndex + 1}
                              </div>
                              {/* 分支点标记 */}
                              {isForkPoint && (
                                <div style={{
                                  position: 'absolute',
                                  bottom: '2px',
                                  right: '2px',
                                  background: '#ef4444',
                                  borderRadius: '50%',
                                  width: '14px',
                                  height: '14px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                }}>
                                  <GitFork size={8} color="#fff" />
                                </div>
                              )}
                              {/* 汇合点标记 */}
                              {isMergePoint && (
                                <div style={{
                                  position: 'absolute',
                                  bottom: '2px',
                                  left: '2px',
                                  background: '#8b5cf6',
                                  borderRadius: '50%',
                                  width: '14px',
                                  height: '14px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                }}>
                                  <GitMerge size={8} color="#fff" />
                                </div>
                              )}
                            </div>
                            {/* 箭头 */}
                            {displayIndex < onboardingScreenshots.length - 1 && (
                              <ArrowRight size={12} color="var(--text-secondary)" style={{ opacity: 0.3 }} />
                            )}
                          </div>
                          {/* 分叉指示器 - 向上箭头指向分支起点 */}
                          {isForkPoint && branchesFromHere.length > 0 && (
                            <div style={{ 
                              display: 'flex', 
                              flexDirection: 'column', 
                              alignItems: 'center',
                              marginTop: '4px',
                            }}>
                              <ArrowUp size={12} color="#ef4444" />
                              <div style={{ 
                                fontSize: '8px', 
                                color: '#ef4444',
                                whiteSpace: 'nowrap',
                                marginTop: '2px',
                              }}>
                                {branchesFromHere.map(b => b.name).join(', ')}
                              </div>
                            </div>
                          )}
                        </div>
                        )
                      })
                    })()}
                  </div>
                </div>

                {/* 分支流程 - 泳道 */}
                {branchData.branches.map((branch) => (
                  <div key={branch.id} style={{ 
                    marginBottom: '16px',
                    background: 'var(--bg-secondary)',
                    borderRadius: '12px',
                    padding: '16px',
                    borderLeft: `4px solid ${branch.color}`,
                  }}>
                    <h3 style={{ 
                      fontSize: '13px', 
                      color: branch.color, 
                      marginBottom: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}>
                      <div style={{ 
                        width: '10px', 
                        height: '10px', 
                        borderRadius: '2px', 
                        background: branch.color 
                      }} />
                      {branch.name}
                      <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 400 }}>
                        (从 #{branch.fork_from + 1} 分叉 → {branch.screens.length} 张截图
                        {branch.merge_to !== null && ` → 汇合到 #${branch.merge_to + 1}`})
                      </span>
                    </h3>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '4px',
                      flexWrap: 'wrap',
                    }}>
                      {/* 分叉起点 */}
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        gap: '4px',
                        padding: '4px 8px',
                        background: 'rgba(239, 68, 68, 0.1)',
                        borderRadius: '4px',
                        border: '1px dashed #ef4444',
                      }}>
                        <GitFork size={12} color="#ef4444" />
                        <span style={{ fontSize: '10px', color: '#ef4444' }}>#{branch.fork_from + 1}</span>
                      </div>
                      <ArrowRight size={12} color={branch.color} />
                      
                      {/* 分支截图 */}
                      {branch.screens.map((screenIndex, i) => {
                        const screenshot = screenshots[screenIndex]
                        if (!screenshot) return null
                        
                        return (
                          <div key={screenIndex} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <div style={{ position: 'relative' }}>
                              <img
                                src={getThumbnailUrl(selectedProject, screenshot.filename, 'small')}
                                alt={screenshot.filename}
                                style={{
                                  width: '45px',
                                  height: '80px',
                                  objectFit: 'cover',
                                  borderRadius: '4px',
                                  border: `2px solid ${branch.color}`,
                                }}
                              />
                              <div style={{
                                position: 'absolute',
                                top: '2px',
                                left: '2px',
                                fontSize: '9px',
                                background: branch.color,
                                color: '#fff',
                                padding: '1px 3px',
                                borderRadius: '2px',
                              }}>
                                {screenIndex + 1}
                              </div>
                            </div>
                            {i < branch.screens.length - 1 && (
                              <ArrowRight size={12} color={branch.color} />
                            )}
                          </div>
                        )
                      })}
                      
                      {/* 汇合点 */}
                      {branch.merge_to !== null && (
                        <>
                          <ArrowRight size={12} color={branch.color} />
                          <div style={{ 
                            display: 'flex', 
                            alignItems: 'center',
                            gap: '4px',
                            padding: '4px 8px',
                            background: 'rgba(139, 92, 246, 0.1)',
                            borderRadius: '4px',
                            border: '1px dashed #8b5cf6',
                          }}>
                            <GitMerge size={12} color="#8b5cf6" />
                            <span style={{ fontSize: '10px', color: '#8b5cf6' }}>#{branch.merge_to + 1}</span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                ))}

                {/* 图例说明 */}
                <div style={{ 
                  marginTop: '24px', 
                  padding: '12px 16px',
                  background: 'rgba(255,255,255,0.03)',
                  borderRadius: '8px',
                  display: 'flex',
                  gap: '24px',
                  fontSize: '11px',
                  color: 'var(--text-secondary)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <GitFork size={12} color="#ef4444" /> 分支点
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <GitMerge size={12} color="#8b5cf6" /> 汇合点
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <div style={{ width: '12px', height: '12px', background: '#22c55e', borderRadius: '2px' }} /> 分支路径
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <div style={{ width: '12px', height: '12px', opacity: 0.5, border: '1px solid var(--text-secondary)', borderRadius: '2px' }} /> 属于分支的截图（主流程中半透明）
                  </div>
                </div>
              </div>
            )}

            {/* 流程图视图 - 无分支提示 */}
            {selectedProject && !loading && viewMode === 'flow' && branchData.branches.length === 0 && (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '100%',
                color: 'var(--text-secondary)',
                gap: '12px',
              }}>
                <Network size={48} style={{ opacity: 0.3 }} />
                <div>暂无分支数据</div>
                <div style={{ fontSize: '13px' }}>
                  请先在网格视图中标记分支点并创建分支
                </div>
                <button 
                  className="btn-ghost"
                  onClick={() => setViewMode('grid')}
                  style={{ marginTop: '8px' }}
                >
                  <LayoutGrid size={16} />
                  切换到网格视图
                </button>
              </div>
            )}

            {/* 截图网格视图 */}
            {selectedProject && !loading && viewMode === 'grid' && (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
                  gap: '10px',
                }}
              >
                {displayScreenshots.map((screenshot, displayIndex) => {
                  const realIndex = screenshots.findIndex(s => s.filename === screenshot.filename)
                  const { isForkPoint, isMergePoint, inBranch, isPending } = getScreenType(realIndex)
                  const borderColor = getScreenBorderColor(realIndex)
                  
                  return (
                    <motion.div
                      key={screenshot.filename}
                      whileHover={{ scale: 1.02 }}
                      style={{
                        position: 'relative',
                        cursor: editMode !== 'none' ? 'pointer' : 'default',
                      }}
                      onClick={() => handleScreenClick(realIndex)}
                    >
                      {/* 截图卡片 */}
                      <div
                        style={{
                          aspectRatio: '9/16',
                          borderRadius: '6px',
                          overflow: 'hidden',
                          border: `2px solid ${borderColor}`,
                          background: 'var(--bg-secondary)',
                          transition: 'all 0.2s ease',
                        }}
                      >
                        <img
                          src={getThumbnailUrl(selectedProject, screenshot.filename, 'small')}
                          alt={screenshot.filename}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            opacity: selectedBranch && !inBranch && !isForkPoint && !isMergePoint ? 0.3 : 1,
                          }}
                        />
                      </div>

                      {/* 索引标签 */}
                      <div
                        style={{
                          position: 'absolute',
                          top: '4px',
                          left: '4px',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          background: 'rgba(0,0,0,0.7)',
                          fontSize: '10px',
                          color: '#fff',
                        }}
                      >
                        {String(realIndex + 1).padStart(4, '0')}
                      </div>

                      {/* 分支点标记 */}
                      {isForkPoint && (
                        <div
                          style={{
                            position: 'absolute',
                            top: '4px',
                            right: '4px',
                            padding: '2px 4px',
                            borderRadius: '4px',
                            background: '#ef4444',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '2px',
                          }}
                        >
                          <GitFork size={10} color="#fff" />
                        </div>
                      )}

                      {/* 汇合点标记 */}
                      {isMergePoint && (
                        <div
                          style={{
                            position: 'absolute',
                            top: '4px',
                            right: isForkPoint ? '28px' : '4px',
                            padding: '2px 4px',
                            borderRadius: '4px',
                            background: '#8b5cf6',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '2px',
                          }}
                        >
                          <GitMerge size={10} color="#fff" />
                        </div>
                      )}

                      {/* 分支颜色条 */}
                      {inBranch && (
                        <div
                          style={{
                            position: 'absolute',
                            bottom: 0,
                            left: 0,
                            right: 0,
                            height: '3px',
                            background: inBranch.color,
                          }}
                        />
                      )}

                      {/* 待添加标记 */}
                      {isPending && (
                        <div
                          style={{
                            position: 'absolute',
                            inset: 0,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: 'rgba(245, 158, 11, 0.3)',
                            borderRadius: '6px',
                          }}
                        >
                          <Check size={24} color="#f59e0b" />
                        </div>
                      )}
                    </motion.div>
                  )
                })}
              </div>
            )}
          </div>

          {/* 底部状态栏 */}
          {selectedProject && (
            <div
              style={{
                padding: '8px 16px',
                borderTop: '1px solid var(--border-default)',
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                fontSize: '12px',
                color: 'var(--text-secondary)',
              }}
            >
              <span>截图: {screenshots.length}</span>
              <span>分支点: {branchData.fork_points.length}</span>
              <span>汇合点: {branchData.merge_points.length}</span>
              <span>分支: {branchData.branches.length}</span>
              
              {editMode !== 'none' && (
                <span style={{ color: '#f59e0b' }}>
                  {editMode === 'fork' && '点击截图标记/取消分支点'}
                  {editMode === 'merge' && '点击截图标记/取消汇合点'}
                  {editMode === 'branch' && `选择分支包含的截图 (已选 ${pendingBranchScreens.length})`}
                </span>
              )}
              
              <div style={{ flex: 1 }} />
              
              {saving && <span>保存中...</span>}
              {error && <span style={{ color: '#ef4444' }}>{error}</span>}
            </div>
          )}
        </div>

        {/* 右侧分支列表面板 */}
        {selectedProject && (
          <div
            style={{
              width: '280px',
              borderLeft: '1px solid var(--border-default)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            <div style={{ padding: '12px', borderBottom: '1px solid var(--border-default)' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, margin: 0 }}>
                分支列表
              </h3>
            </div>

            <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
              {/* 分支点列表 */}
              {branchData.fork_points.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    分支点 ({branchData.fork_points.length})
                  </h4>
                  {branchData.fork_points.map((fp) => (
                    <div
                      key={fp.index}
                      style={{
                        padding: '8px',
                        borderRadius: '6px',
                        background: 'var(--bg-secondary)',
                        marginBottom: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <GitFork size={14} color="#ef4444" />
                      <span style={{ fontSize: '12px' }}>#{fp.index + 1}</span>
                      <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {fp.name || '未命名'}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* 分支列表 */}
              {branchData.branches.length > 0 && (
                <div>
                  <h4 style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    分支路径 ({branchData.branches.length})
                  </h4>
                  {branchData.branches.map((branch) => (
                    <div
                      key={branch.id}
                      onClick={() => selectBranch(selectedBranch === branch.id ? null : branch.id)}
                      style={{
                        padding: '10px',
                        borderRadius: '6px',
                        background: selectedBranch === branch.id ? 'rgba(255,255,255,0.1)' : 'var(--bg-secondary)',
                        marginBottom: '4px',
                        cursor: 'pointer',
                        border: `2px solid ${selectedBranch === branch.id ? branch.color : 'transparent'}`,
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <div
                          style={{
                            width: '12px',
                            height: '12px',
                            borderRadius: '3px',
                            background: branch.color,
                          }}
                        />
                        <span style={{ fontSize: '13px', fontWeight: 500 }}>{branch.name}</span>
                        <div style={{ flex: 1 }} />
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            if (confirm(`确定删除分支 "${branch.name}" 吗？`)) {
                              removeBranch(selectedProject, branch.id)
                            }
                          }}
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: '2px',
                            opacity: 0.5,
                          }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                        从 #{branch.fork_from + 1} 分叉 · {branch.screens.length} 张截图
                        {branch.merge_to !== null && ` · 汇合到 #${branch.merge_to + 1}`}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {branchData.branches.length === 0 && branchData.fork_points.length === 0 && (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '24px', 
                  color: 'var(--text-secondary)',
                  fontSize: '13px',
                }}>
                  <GitBranch size={32} style={{ opacity: 0.3, marginBottom: '8px' }} />
                  <div>暂无分支数据</div>
                  <div style={{ fontSize: '12px', marginTop: '4px' }}>
                    点击"分支点"按钮开始标记
                  </div>
                </div>
              )}
            </div>

            {/* 清空按钮 */}
            {(branchData.branches.length > 0 || branchData.fork_points.length > 0) && (
              <div style={{ padding: '8px', borderTop: '1px solid var(--border-default)' }}>
                <button
                  className="btn-ghost"
                  onClick={() => {
                    if (confirm('确定清空所有分支数据吗？此操作不可恢复。')) {
                      clearAll(selectedProject)
                    }
                  }}
                  style={{ width: '100%', justifyContent: 'center', color: '#ef4444' }}
                >
                  <Trash2 size={14} />
                  清空所有
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 创建分支对话框 */}
      <AnimatePresence>
        {showBranchDialog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0,0,0,0.7)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 100,
            }}
            onClick={() => setShowBranchDialog(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                background: '#1a1a1a',
                borderRadius: '12px',
                padding: '24px',
                width: '400px',
                border: '1px solid var(--border-default)',
              }}
            >
              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '20px' }}>
                创建分支
              </h3>

              {/* 分支名称 */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                  分支名称
                </label>
                <input
                  type="text"
                  value={newBranchName}
                  onChange={(e) => setNewBranchName(e.target.value)}
                  placeholder="如：减重路径"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '6px',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-default)',
                    color: '#fff',
                    fontSize: '14px',
                  }}
                />
              </div>

              {/* 颜色选择 */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                  分支颜色
                </label>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {BRANCH_COLORS.map((color) => (
                    <button
                      key={color.value}
                      onClick={() => setNewBranchColor(color.value)}
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '6px',
                        background: color.value,
                        border: newBranchColor === color.value ? '2px solid #fff' : '2px solid transparent',
                        cursor: 'pointer',
                      }}
                      title={color.name}
                    />
                  ))}
                </div>
              </div>

              {/* 分叉点选择 */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                  从哪个分支点分叉
                </label>
                <select
                  value={newBranchForkFrom}
                  onChange={(e) => setNewBranchForkFrom(Number(e.target.value))}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '6px',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-default)',
                    color: '#fff',
                    fontSize: '14px',
                  }}
                >
                  {branchData.fork_points.map((fp) => (
                    <option key={fp.index} value={fp.index}>
                      #{fp.index + 1} - {fp.name || '未命名'}
                    </option>
                  ))}
                </select>
              </div>

              {/* 汇合点选择 */}
              <div style={{ marginBottom: '24px' }}>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                  汇合到哪个点（可选）
                </label>
                <select
                  value={newBranchMergeTo ?? ''}
                  onChange={(e) => setNewBranchMergeTo(e.target.value ? Number(e.target.value) : null)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '6px',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-default)',
                    color: '#fff',
                    fontSize: '14px',
                  }}
                >
                  <option value="">不汇合</option>
                  {branchData.merge_points.map((mp) => (
                    <option key={mp} value={mp}>
                      #{mp + 1}
                    </option>
                  ))}
                </select>
              </div>

              {/* 已选截图 */}
              <div style={{ marginBottom: '24px', padding: '12px', background: 'var(--bg-secondary)', borderRadius: '6px' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                  已选择 {pendingBranchScreens.length} 张截图
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                  {pendingBranchScreens.slice(0, 10).map(i => `#${i + 1}`).join(', ')}
                  {pendingBranchScreens.length > 10 && '...'}
                </div>
              </div>

              {/* 按钮 */}
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  className="btn-ghost"
                  onClick={() => setShowBranchDialog(false)}
                >
                  取消
                </button>
                <button
                  className="btn-primary"
                  onClick={handleCreateBranch}
                  disabled={!newBranchName.trim() || pendingBranchScreens.length === 0}
                >
                  创建分支
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AppLayout>
  )
}
