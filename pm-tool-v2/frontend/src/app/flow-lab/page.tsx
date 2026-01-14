'use client'

import { useEffect, useCallback, useRef, useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  type DropAnimation,
  defaultDropAnimationSideEffects,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
} from '@dnd-kit/sortable'
import { AppLayout } from '@/components/layout'
import {
  PreviewPanel,
  PendingPanel,
  StatusBar,
  ShortcutsHint,
  ProjectSelector,
  SortableScreenshot,
  DragPreview,
  ZoomControl,
  SelectionBar,
} from '@/components/sort'
import { useProjectStore } from '@/store/project-store'
import { useSortStore } from '@/store/sort'
import { useBranchStore } from '@/store/branch-store'
import { importScreenshot, uploadScreenshot } from '@/lib/api'
import type { Screenshot } from '@/types'
import {
  ArrowUpDown,
  Save,
  Check,
  Trash2,
  RotateCcw,
  CheckSquare,
  X,
  LayoutGrid,
  GitBranch,
  GitFork,
  GitMerge,
  FlaskConical,
} from 'lucide-react'
import { toast } from 'sonner'

// ==================== 配置 ====================

const dropAnimation: DropAnimation = {
  sideEffects: defaultDropAnimationSideEffects({
    styles: { active: { opacity: '0.5' } },
  }),
  duration: 250,
  easing: 'cubic-bezier(0.25, 1, 0.5, 1)',
}

function getCardMinWidth(zoom: number): number {
  return Math.round(100 * (zoom / 100))
}

// ==================== 主页面 ====================

export default function FlowLabPage() {
  // Store - 排序
  const { projects, fetchProjects } = useProjectStore()
  const {
    sortedScreenshots,
    deletedBatches,
    selectedFiles,
    onboardingRange,
    previewIndex,
    loading,
    saving,
    error,
    hasChanges,
    zoom,
    fetchData,
    reorder,
    toggleSelect,
    selectAll,
    deselectAll,
    setSelectedFiles,
    deleteSelected,
    restoreBatch,
    saveSortOrder,
    applySortOrder,
    setPreviewIndex,
    prevPreview,
    nextPreview,
    reset,
    zoomIn,
    zoomOut,
    resetZoom,
    setLastClickedIndex,
    lastClickedIndex,
  } = useSortStore()

  // Store - 分支
  const {
    branchData,
    editMode,
    pendingBranchScreens,
    fetchData: fetchBranchData,
    setEditMode,
    toggleForkPoint,
    toggleMergePoint,
    toggleScreenInPending,
    clearPendingScreens,
    createBranch,
    removeBranch,
    clearAll: clearBranchData,
  } = useBranchStore()

  // Local State
  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [showDeleted, setShowDeleted] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)
  const [dropTargetIndex, setDropTargetIndex] = useState<number | null>(null)
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [newlyAdded, setNewlyAdded] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'flow'>('flow')
  
  // Refs
  const contentRef = useRef<HTMLDivElement>(null)
  const gridRef = useRef<HTMLDivElement>(null)

  // DnD Sensors
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  )

  // ==================== Effects ====================

  // 加载项目列表
  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  // 离开页面提示
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasChanges) {
        e.preventDefault()
        e.returnValue = '你有未保存的排序更改，确定要离开吗？'
      }
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [hasChanges])

  // 切换项目时加载数据
  useEffect(() => {
    if (selectedProject) {
      fetchData(selectedProject)
      fetchBranchData(selectedProject)
    } else {
      reset()
    }
  }, [selectedProject, fetchData, fetchBranchData, reset])

  // 滚轮缩放
  useEffect(() => {
    if (!selectedProject) return
    
    const handleWheel = (e: WheelEvent) => {
      if (e.ctrlKey) {
        e.preventDefault()
        e.deltaY < 0 ? zoomIn() : zoomOut()
      }
    }
    
    const contentArea = contentRef.current
    if (contentArea) {
      contentArea.addEventListener('wheel', handleWheel, { passive: false })
      return () => contentArea.removeEventListener('wheel', handleWheel)
    }
  }, [selectedProject, zoomIn, zoomOut])

  // 全局快捷键
  useEffect(() => {
    if (!selectedProject) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'a') { e.preventDefault(); selectAll() }
      if (e.ctrlKey && (e.key === '=' || e.key === '+')) { e.preventDefault(); zoomIn() }
      if (e.ctrlKey && e.key === '-') { e.preventDefault(); zoomOut() }
      if (e.ctrlKey && e.key === '0') { e.preventDefault(); resetZoom() }
      if (e.key === 'Delete' && selectedFiles.size > 0) {
        const count = selectedFiles.size
        if (count <= 10 || window.confirm(`确定要删除 ${count} 张截图吗？`)) {
          deleteSelected(selectedProject)
        }
      }
      if (e.key === 'Escape') { 
        deselectAll()
        setPreviewIndex(null)
        setEditMode('none')
        clearPendingScreens()
      }
      if (e.key === 'ArrowLeft' && previewIndex !== null) { prevPreview() }
      if (e.key === 'ArrowRight' && previewIndex !== null) { nextPreview() }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedProject, selectedFiles, previewIndex, selectAll, deselectAll, 
      deleteSelected, setPreviewIndex, prevPreview, nextPreview, zoomIn, zoomOut, resetZoom,
      setEditMode, clearPendingScreens])

  // ==================== Handlers ====================

  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id as string)
  }, [])

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event
    setActiveId(null)

    if (over && active.id !== over.id) {
      const oldIndex = sortedScreenshots.findIndex(s => s.filename === active.id)
      const newIndex = sortedScreenshots.findIndex(s => s.filename === over.id)
      
      if (previewIndex !== null) {
        if (previewIndex === oldIndex) {
          setPreviewIndex(newIndex)
        } else if (oldIndex < previewIndex && newIndex >= previewIndex) {
          setPreviewIndex(previewIndex - 1)
        } else if (oldIndex > previewIndex && newIndex <= previewIndex) {
          setPreviewIndex(previewIndex + 1)
        }
      }
      
      reorder(oldIndex, newIndex)
    }
  }, [sortedScreenshots, reorder, previewIndex, setPreviewIndex])

  const handleCardClick = useCallback((e: React.MouseEvent, index: number, filename: string) => {
    // 如果在分支编辑模式，处理分支相关点击
    if (editMode === 'fork' && selectedProject) {
      toggleForkPoint(selectedProject, index)
      return
    }
    if (editMode === 'merge' && selectedProject) {
      toggleMergePoint(selectedProject, index)
      return
    }
    if (editMode === 'branch') {
      toggleScreenInPending(index)
      return
    }
    
    // 普通模式
    setPreviewIndex(index)
    
    if (e.shiftKey && lastClickedIndex !== null) {
      const start = Math.min(lastClickedIndex, index)
      const end = Math.max(lastClickedIndex, index)
      setSelectedFiles(new Set(sortedScreenshots.slice(start, end + 1).map(s => s.filename)))
    } else if (e.ctrlKey || e.metaKey) {
      toggleSelect(filename)
    } else {
      setSelectedFiles(new Set([filename]))
    }
    
    setLastClickedIndex(index)
  }, [editMode, selectedProject, lastClickedIndex, sortedScreenshots, 
      setPreviewIndex, setSelectedFiles, toggleSelect, setLastClickedIndex,
      toggleForkPoint, toggleMergePoint, toggleScreenInPending])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!selectedProject || viewMode !== 'grid') return
    
    const hasFiles = e.dataTransfer.types.includes('Files')
    const hasPending = e.dataTransfer.types.includes('application/x-pending-screenshot')
    
    if (hasFiles || hasPending) {
      setIsDragOver(true)
      e.dataTransfer.dropEffect = 'copy'
      
      if (gridRef.current) {
        const cards = gridRef.current.querySelectorAll('[data-screenshot-card]')
        let targetIndex = sortedScreenshots.length
        
        for (let i = 0; i < cards.length; i++) {
          const card = cards[i] as HTMLElement
          const rect = card.getBoundingClientRect()
          const cardCenterX = rect.left + rect.width / 2
          
          if (e.clientY < rect.bottom && e.clientY > rect.top - 20) {
            if (e.clientX < cardCenterX) { targetIndex = i; break }
            else if (i === cards.length - 1 || e.clientX < rect.right) { targetIndex = i + 1; break }
          }
        }
        setDropTargetIndex(targetIndex)
      }
    }
  }, [selectedProject, sortedScreenshots.length, viewMode])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const relatedTarget = e.relatedTarget as HTMLElement
    if (!contentRef.current?.contains(relatedTarget)) {
      setIsDragOver(false)
      setDropTargetIndex(null)
    }
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    const targetIndex = dropTargetIndex ?? sortedScreenshots.length
    setIsDragOver(false)
    setDropTargetIndex(null)
    
    if (!selectedProject) { toast.error('请先选择一个项目'); return }

    const pendingData = e.dataTransfer.getData('application/x-pending-screenshot')
    if (pendingData) {
      try {
        const { filename } = JSON.parse(pendingData)
        const result = await importScreenshot(selectedProject, filename)
        if (result.success && result.new_filename) {
          const newScreenshot: Screenshot = { filename: result.new_filename, index: targetIndex }
          const current = useSortStore.getState().sortedScreenshots
          useSortStore.setState({
            sortedScreenshots: [...current.slice(0, targetIndex), newScreenshot, ...current.slice(targetIndex)],
            hasChanges: true
          })
          setUploadMessage(`✓ 已插入 ${result.new_filename}`)
          setNewlyAdded(result.new_filename)
          setTimeout(() => { setUploadMessage(null); setNewlyAdded(null) }, 3000)
        }
      } catch (error) {
        toast.error('导入失败: ' + (error as Error).message)
      }
      return
    }

    const files = Array.from(e.dataTransfer.files).filter(f => 
      f.type.startsWith('image/') || /\.(png|jpg|jpeg|webp)$/i.test(f.name)
    )
    if (files.length === 0) { toast.error('请拖入图片文件'); return }

    const uploadedFiles: string[] = []
    for (const file of files) {
      try {
        const result = await uploadScreenshot(selectedProject, file)
        if (result.success && result.new_filename) uploadedFiles.push(result.new_filename)
      } catch (error) { console.error('Upload failed:', error) }
    }

    if (uploadedFiles.length > 0) {
      const newScreenshots: Screenshot[] = uploadedFiles.map(filename => ({ filename, path: '' }))
      const current = useSortStore.getState().sortedScreenshots
      useSortStore.setState({
        sortedScreenshots: [...current.slice(0, targetIndex), ...newScreenshots, ...current.slice(targetIndex)],
        hasChanges: true
      })
      setUploadMessage(`✓ 已导入 ${uploadedFiles.length} 张截图`)
      setNewlyAdded(uploadedFiles[uploadedFiles.length - 1])
      setTimeout(() => { setUploadMessage(null); setNewlyAdded(null) }, 3000)
    }
  }, [selectedProject, dropTargetIndex, sortedScreenshots.length])

  const handleImportSuccess = useCallback(() => {
    if (selectedProject) fetchData(selectedProject)
  }, [selectedProject, fetchData])

  const handleDeleteSelected = useCallback(() => {
    if (!selectedProject) return
    const count = selectedFiles.size
    if (count <= 10 || window.confirm(`确定要删除 ${count} 张截图吗？`)) {
      deleteSelected(selectedProject)
    }
  }, [selectedProject, selectedFiles.size, deleteSelected])

  // ==================== Helper Functions ====================

  // 获取截图类型（分支点、汇合点、属于哪个分支）
  const getScreenType = useCallback((index: number) => {
    const isForkPoint = branchData.fork_points.some(fp => fp.index === index)
    const isMergePoint = branchData.merge_points.includes(index)
    const inBranch = branchData.branches.find(b => b.screens.includes(index))
    const isPending = pendingBranchScreens.includes(index)
    return { isForkPoint, isMergePoint, inBranch, isPending }
  }, [branchData, pendingBranchScreens])

  // ==================== Derived State ====================

  const activeScreenshot = activeId ? sortedScreenshots.find(s => s.filename === activeId) : null
  const previewScreenshot = previewIndex !== null ? sortedScreenshots[previewIndex] : null
  const displayProjectName = selectedProject?.replace('downloads_2024/', '') || ''

  // Onboarding 范围内的截图
  const onboardingScreenshots = onboardingRange.start >= 0 && onboardingRange.end >= 0
    ? sortedScreenshots.slice(onboardingRange.start, onboardingRange.end + 1)
    : sortedScreenshots

  // ==================== Styles ====================

  const pageStyles = {
    pendingSidebar: {
      width: '280px',
      flexShrink: 0,
      borderRight: '1px solid var(--border-default)',
      overflowY: 'auto' as const,
      padding: '12px',
    },
    mainContent: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column' as const,
      minWidth: 0,
    },
    topbarActions: {
      display: 'flex',
      gap: '8px',
      marginLeft: '16px',
      alignItems: 'center',
      flexShrink: 1,
      minWidth: 0,
      overflowX: 'auto' as const,
      overflowY: 'hidden' as const,
      paddingBottom: '2px',
    },
    btnGhost: {
      background: 'none',
      color: 'var(--text-muted)',
      border: '1px solid transparent',
      padding: '6px 12px',
      borderRadius: '6px',
      cursor: 'pointer',
      fontSize: '13px',
      fontWeight: 500,
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      whiteSpace: 'nowrap' as const,
      lineHeight: 1.4,
    },
    btnGhostDanger: {
      color: 'var(--danger)',
    },
    btnGhostActive: {
      color: '#fff',
      background: 'var(--bg-active)',
    },
    btnGhostSuccess: {
      background: 'var(--success)',
      color: '#fff',
    },
    contentArea: {
      flex: 1,
      overflow: 'auto',
      position: 'relative' as const,
    },
    dropOverlay: {
      position: 'absolute' as const,
      inset: 0,
      background: 'rgba(245, 158, 11, 0.05)',
      border: '3px dashed #f59e0b',
      borderRadius: '12px',
      zIndex: 5,
      display: 'flex',
      alignItems: 'flex-start' as const,
      justifyContent: 'center',
      paddingTop: '20px',
      pointerEvents: 'none' as const,
    },
    dropMessage: {
      background: 'rgba(0,0,0,0.9)',
      padding: '12px 24px',
      borderRadius: '8px',
      color: '#f59e0b',
      fontSize: '14px',
      fontWeight: 500,
    },
    uploadToast: {
      position: 'fixed' as const,
      bottom: '24px',
      left: '50%',
      transform: 'translateX(-50%)',
      background: '#22c55e',
      color: '#fff',
      padding: '12px 24px',
      borderRadius: '8px',
      fontSize: '14px',
      fontWeight: 500,
      zIndex: 100,
      boxShadow: '0 4px 20px rgba(34, 197, 94, 0.4)',
    },
    emptyState: {
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      justifyContent: 'center',
      height: '400px',
      color: 'var(--text-muted)',
      gap: '16px',
    },
    loadingState: {
      display: 'flex',
      height: '256px',
      alignItems: 'center',
      justifyContent: 'center',
    },
    errorMessage: {
      padding: '12px 16px',
      background: 'rgba(239, 68, 68, 0.2)',
      color: 'var(--danger)',
      borderRadius: '8px',
      marginBottom: '16px',
    },
    deletedPanel: {
      background: 'var(--bg-card)',
      borderRadius: '8px',
      marginBottom: '16px',
      padding: '16px',
    },
    deletedBatch: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '8px 12px',
      background: 'var(--bg-secondary)',
      borderRadius: '6px',
      marginTop: '8px',
      fontSize: '13px',
    },
    sortGrid: {
      display: 'grid',
      position: 'relative' as const,
      transition: 'gap 200ms ease',
    },
    dropIndicator: {
      position: 'absolute' as const,
      left: '-6px',
      top: 0,
      bottom: 0,
      width: '4px',
      background: '#f59e0b',
      borderRadius: '2px',
      zIndex: 10,
      boxShadow: '0 0 10px rgba(245, 158, 11, 0.8)',
    },
    viewToggle: {
      display: 'flex',
      gap: '4px',
      background: 'var(--bg-secondary)',
      padding: '4px',
      borderRadius: '8px',
    },
    viewToggleBtn: {
      padding: '6px 12px',
      borderRadius: '6px',
      border: 'none',
      cursor: 'pointer',
      fontSize: '13px',
      fontWeight: 500,
      display: 'flex',
      alignItems: 'center',
      gap: '6px',
      transition: 'all 0.2s',
    },
    branchToolbar: {
      display: 'flex',
      gap: '8px',
      padding: '8px 16px',
      background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-default)',
      alignItems: 'center',
    },
  }

  // ==================== Render ====================

  return (
    <AppLayout>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* 左侧待处理区 */}
        <div style={pageStyles.pendingSidebar}>
          <PendingPanel selectedProject={selectedProject} onImportSuccess={handleImportSuccess} />
        </div>

        {/* 主内容区 */}
        <div style={pageStyles.mainContent}>
          {/* 顶栏 */}
          <div className="topbar" style={{ overflow: 'visible' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FlaskConical size={18} color="#f59e0b" />
              <h1 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', whiteSpace: 'nowrap' }}>
                Flow Lab
              </h1>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', background: 'var(--bg-secondary)', padding: '2px 8px', borderRadius: '4px' }}>
                实验
              </span>
            </div>
            <div style={{ flex: 1, minWidth: '8px' }} />

            {/* 视图切换 */}
            {selectedProject && sortedScreenshots.length > 0 && (
              <div style={pageStyles.viewToggle}>
                <button
                  style={{
                    ...pageStyles.viewToggleBtn,
                    background: viewMode === 'grid' ? 'var(--bg-active)' : 'transparent',
                    color: viewMode === 'grid' ? '#fff' : 'var(--text-muted)',
                  }}
                  onClick={() => setViewMode('grid')}
                >
                  <LayoutGrid size={14} />
                  网格
                </button>
                <button
                  style={{
                    ...pageStyles.viewToggleBtn,
                    background: viewMode === 'flow' ? 'var(--bg-active)' : 'transparent',
                    color: viewMode === 'flow' ? '#fff' : 'var(--text-muted)',
                  }}
                  onClick={() => setViewMode('flow')}
                >
                  <GitBranch size={14} />
                  流程
                </button>
              </div>
            )}

            {/* 缩放控制 */}
            {selectedProject && sortedScreenshots.length > 0 && viewMode === 'grid' && (
              <ZoomControl
                zoom={zoom}
                onZoomIn={zoomIn}
                onZoomOut={zoomOut}
                onReset={resetZoom}
              />
            )}

            {/* 项目选择器 */}
            <div style={{ marginLeft: 12 }}>
              <ProjectSelector
                projects={projects}
                selectedProject={selectedProject}
                onSelect={setSelectedProject}
              />
            </div>

            {/* 操作按钮 - 网格模式 */}
            {selectedProject && sortedScreenshots.length > 0 && viewMode === 'grid' && (
              <div style={pageStyles.topbarActions}>
                <button style={pageStyles.btnGhost} onClick={() => selectedFiles.size > 0 ? deselectAll() : selectAll()}>
                  {selectedFiles.size > 0 ? <><X size={16} />取消 ({selectedFiles.size})</> : <><CheckSquare size={16} />全选</>}
                </button>

                {selectedFiles.size > 0 && (
                  <button style={{ ...pageStyles.btnGhost, ...pageStyles.btnGhostDanger }} onClick={handleDeleteSelected} disabled={saving}>
                    <Trash2 size={16} />删除 ({selectedFiles.size})
                  </button>
                )}

                {deletedBatches.length > 0 && (
                  <button style={{ ...pageStyles.btnGhost, ...(showDeleted ? pageStyles.btnGhostActive : {}) }} onClick={() => setShowDeleted(!showDeleted)}>
                    <RotateCcw size={16} />已删除 ({deletedBatches.reduce((a, b) => a + b.count, 0)})
                  </button>
                )}

                {hasChanges && (
                  <>
                    <button style={pageStyles.btnGhost} onClick={() => selectedProject && saveSortOrder(selectedProject)} disabled={saving}>
                      <Save size={16} />保存排序
                    </button>
                    <button 
                      style={{ ...pageStyles.btnGhost, ...pageStyles.btnGhostSuccess }}
                      onClick={() => selectedProject && applySortOrder(selectedProject)} 
                      disabled={saving}
                    >
                      <Check size={16} />{saving ? '应用中...' : '应用并重命名'}
                    </button>
                  </>
                )}
              </div>
            )}
          </div>

          {/* 分支工具栏 - 流程模式 */}
          {selectedProject && sortedScreenshots.length > 0 && viewMode === 'flow' && (
            <div style={pageStyles.branchToolbar}>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)', marginRight: '8px' }}>标记模式:</span>
              <button
                style={{
                  ...pageStyles.btnGhost,
                  ...(editMode === 'fork' ? { background: '#ef4444', color: '#fff' } : {}),
                }}
                onClick={() => setEditMode(editMode === 'fork' ? 'none' : 'fork')}
              >
                <GitFork size={14} />
                分支点
              </button>
              <button
                style={{
                  ...pageStyles.btnGhost,
                  ...(editMode === 'merge' ? { background: '#8b5cf6', color: '#fff' } : {}),
                }}
                onClick={() => setEditMode(editMode === 'merge' ? 'none' : 'merge')}
              >
                <GitMerge size={14} />
                汇合点
              </button>
              <button
                style={{
                  ...pageStyles.btnGhost,
                  ...(editMode === 'branch' ? { background: '#22c55e', color: '#fff' } : {}),
                }}
                onClick={() => setEditMode(editMode === 'branch' ? 'none' : 'branch')}
              >
                <GitBranch size={14} />
                选择分支截图
              </button>
              
              {/* 创建分支按钮 - 当有待选截图时显示 */}
              {pendingBranchScreens.length > 0 && branchData.fork_points.length > 0 && (
                <button
                  style={{
                    ...pageStyles.btnGhost,
                    background: '#3b82f6',
                    color: '#fff',
                  }}
                  onClick={() => {
                    // #region agent log
                    fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'flow-lab:createBranch',message:'Create branch clicked',data:{pendingScreens:pendingBranchScreens,forkPoints:branchData.fork_points},timestamp:Date.now(),hypothesisId:'H1'})}).catch(()=>{});
                    // #endregion
                    // 使用第一个分支点作为起点
                    const forkFrom = branchData.fork_points[0].index
                    createBranch(selectedProject, `分支${branchData.branches.length + 1}`, '#22c55e', forkFrom, null)
                  }}
                >
                  <Check size={14} />
                  创建分支 ({pendingBranchScreens.length}张)
                </button>
              )}
              
              <div style={{ flex: 1 }} />
              
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                分支点: {branchData.fork_points.length} | 汇合点: {branchData.merge_points.length} | 分支: {branchData.branches.length}
                {pendingBranchScreens.length > 0 && ` | 待选: ${pendingBranchScreens.length}`}
              </span>
            </div>
          )}

          {/* 状态栏 */}
          {selectedProject && sortedScreenshots.length > 0 && (
            <StatusBar
              projectName={displayProjectName}
              total={sortedScreenshots.length}
              selected={selectedFiles.size}
              moved={hasChanges ? 1 : 0}
              onboardingStart={onboardingRange.start}
              onboardingEnd={onboardingRange.end}
            />
          )}

          {/* 内容区 */}
          <div 
            ref={contentRef}
            style={pageStyles.contentArea}
            onDragOver={viewMode === 'grid' ? handleDragOver : undefined}
            onDragLeave={viewMode === 'grid' ? handleDragLeave : undefined}
            onDrop={viewMode === 'grid' ? handleDrop : undefined}
          >
            {/* 拖拽提示 */}
            {isDragOver && viewMode === 'grid' && (
              <div style={pageStyles.dropOverlay}>
                <div style={pageStyles.dropMessage}>
                  {dropTargetIndex !== null && dropTargetIndex < sortedScreenshots.length
                    ? `释放插入到位置 ${dropTargetIndex + 1}`
                    : '释放添加到末尾'}
                </div>
              </div>
            )}
            
            {/* 上传成功提示 */}
            {uploadMessage && <div style={pageStyles.uploadToast}>{uploadMessage}</div>}

            {/* 空状态 */}
            {!selectedProject && (
              <div style={pageStyles.emptyState}>
                <FlaskConical size={48} />
                <p>请选择一个项目来使用 Flow Lab</p>
              </div>
            )}

            {/* 加载中 */}
            {selectedProject && loading && (
              <div style={pageStyles.loadingState}><div className="spinner" /></div>
            )}

            {/* 错误 */}
            {error && <div style={pageStyles.errorMessage}>{error}</div>}

            {/* 已删除面板 */}
            <AnimatePresence>
              {showDeleted && deletedBatches.length > 0 && viewMode === 'grid' && (
                <div style={pageStyles.deletedPanel}>
                  <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px' }}>已删除的截图</h3>
                  {deletedBatches.map((batch) => (
                    <div key={batch.timestamp} style={pageStyles.deletedBatch}>
                      <span>{batch.count} 张截图 - {batch.timestamp}</span>
                      <button 
                        onClick={() => selectedProject && restoreBatch(selectedProject, batch.timestamp)} 
                        disabled={saving}
                        style={{
                          padding: '4px 8px',
                          fontSize: '12px',
                          background: 'transparent',
                          border: '1px solid var(--border-default)',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          color: 'var(--text-primary)',
                        }}
                      >
                        <RotateCcw size={12} />恢复
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </AnimatePresence>

            {/* 网格视图 */}
            {selectedProject && !loading && sortedScreenshots.length > 0 && viewMode === 'grid' && (
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
              >
                <SortableContext items={sortedScreenshots.map(s => s.filename)} strategy={rectSortingStrategy}>
                  <div
                    ref={gridRef}
                    style={{
                      ...pageStyles.sortGrid,
                      gridTemplateColumns: `repeat(auto-fill, minmax(${getCardMinWidth(zoom)}px, 1fr))`,
                      gap: `${Math.round(10 * (zoom / 100))}px`,
                    }}
                  >
                    {sortedScreenshots.map((screenshot, index) => (
                      <div key={screenshot.filename} style={{ position: 'relative' }}>
                        {isDragOver && dropTargetIndex === index && <div style={pageStyles.dropIndicator} />}
                        <div data-screenshot-card>
                          <SortableScreenshot
                            screenshot={screenshot}
                            projectName={selectedProject}
                            index={index}
                            isSelected={selectedFiles.has(screenshot.filename)}
                            isNewlyAdded={screenshot.filename === newlyAdded}
                            onCardClick={(e) => handleCardClick(e, index, screenshot.filename)}
                            onboardingStart={onboardingRange.start}
                            onboardingEnd={onboardingRange.end}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </SortableContext>

                <DragOverlay dropAnimation={dropAnimation}>
                  {activeScreenshot && selectedProject && (
                    <DragPreview screenshot={activeScreenshot} projectName={selectedProject} zoom={zoom} />
                  )}
                </DragOverlay>
              </DndContext>
            )}

            {/* 流程视图 */}
            {selectedProject && !loading && sortedScreenshots.length > 0 && viewMode === 'flow' && (
              <FlowView
                screenshots={sortedScreenshots}
                onboardingRange={onboardingRange}
                branchData={branchData}
                editMode={editMode}
                pendingBranchScreens={pendingBranchScreens}
                selectedProject={selectedProject}
                onScreenClick={handleCardClick}
                getScreenType={getScreenType}
              />
            )}

            {/* 空列表 */}
            {selectedProject && !loading && sortedScreenshots.length === 0 && (
              <div style={pageStyles.emptyState}>该项目没有截图</div>
            )}
          </div>
        </div>

        {/* 右侧预览面板 */}
        {selectedProject && (
          <PreviewPanel
            screenshot={previewScreenshot}
            projectName={selectedProject}
            currentIndex={previewIndex !== null ? previewIndex : -1}
            total={sortedScreenshots.length}
            onClose={() => setPreviewIndex(null)}
            onPrev={prevPreview}
            onNext={nextPreview}
            onboardingStart={onboardingRange.start}
            onboardingEnd={onboardingRange.end}
          />
        )}
      </div>

      {/* 快捷键提示 */}
      {selectedProject && <ShortcutsHint />}

      {/* 底部选择操作栏 */}
      <AnimatePresence>
        {selectedFiles.size > 0 && selectedProject && viewMode === 'grid' && (
          <SelectionBar
            selectedCount={selectedFiles.size}
            onDeselect={deselectAll}
            onDelete={handleDeleteSelected}
            disabled={saving}
          />
        )}
      </AnimatePresence>

    </AppLayout>
  )
}

// ==================== FlowView 组件 ====================

interface FlowViewProps {
  screenshots: Screenshot[]
  onboardingRange: { start: number; end: number }
  branchData: {
    fork_points: { index: number; name: string }[]
    merge_points: number[]
    branches: {
      id: string
      name: string
      color: string
      fork_from: number
      screens: number[]
      merge_to: number | null
    }[]
  }
  editMode: 'none' | 'fork' | 'merge' | 'branch'
  pendingBranchScreens: number[]
  selectedProject: string
  onScreenClick: (e: React.MouseEvent, index: number, filename: string) => void
  getScreenType: (index: number) => {
    isForkPoint: boolean
    isMergePoint: boolean
    inBranch: { id: string; name: string; color: string } | undefined
    isPending: boolean
  }
}

function FlowView({
  screenshots,
  onboardingRange,
  branchData,
  editMode,
  pendingBranchScreens,
  selectedProject,
  onScreenClick,
  getScreenType,
}: FlowViewProps) {
  // 计算 Onboarding 范围
  const startIdx = onboardingRange.start >= 0 ? onboardingRange.start : 0
  const endIdx = onboardingRange.end >= 0 ? onboardingRange.end + 1 : screenshots.length
  const onboardingScreenshots = screenshots.slice(startIdx, endIdx)
  
  // 缩略图 URL
  const getThumbnailUrl = (filename: string) => {
    const url = `/api/thumbnails/${encodeURIComponent(selectedProject)}/${encodeURIComponent(filename)}?size=small`
    // #region agent log
    if (filename === onboardingScreenshots[0]?.filename) {
      fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'flow-lab/page.tsx:getThumbnailUrl',message:'Thumbnail URL generated',data:{url,filename,project:selectedProject},timestamp:Date.now(),hypothesisId:'H1'})}).catch(()=>{});
    }
    // #endregion
    return url
  }

  // 计算每个截图的宽度（用于分支定位）
  const CARD_WIDTH = 60
  const CARD_GAP = 8
  const CARD_HEIGHT = 100

  return (
    <div style={{
      width: '100%',
      height: '100%',
      overflow: 'auto',
      padding: '24px',
    }}>
      <div style={{
        minWidth: 'fit-content',
      }}>
        {/* 主流程行 */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '24px',
        }}>
          <div style={{
            fontSize: '12px',
            color: 'var(--text-muted)',
            width: '60px',
            flexShrink: 0,
          }}>
            主流程
          </div>
          {onboardingScreenshots.map((screenshot, displayIndex) => {
            const realIndex = startIdx + displayIndex
            const { isForkPoint, isMergePoint, inBranch, isPending } = getScreenType(realIndex)
            const branchesFromHere = branchData.branches.filter(b => b.fork_from === realIndex)
            const ITEM_WIDTH = CARD_WIDTH + 16 // 固定宽度：图片60 + 箭头区域16
            
            return (
              <div
                key={screenshot.filename}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  width: displayIndex < onboardingScreenshots.length - 1 ? `${ITEM_WIDTH}px` : 'auto',
                  flexShrink: 0,
                }}
              >
                {/* 截图容器 */}
                <div style={{ position: 'relative' }}>
                  {/* 截图卡片 */}
                  <div
                    onClick={(e) => onScreenClick(e, realIndex, screenshot.filename)}
                    style={{
                      width: `${CARD_WIDTH}px`,
                      height: `${CARD_HEIGHT}px`,
                      borderRadius: '6px',
                      overflow: 'hidden',
                      cursor: 'pointer',
                      border: isForkPoint
                        ? '3px solid #ef4444'
                        : isMergePoint
                          ? '3px solid #8b5cf6'
                          : isPending
                            ? '3px solid #22c55e'
                            : inBranch
                              ? `2px solid ${inBranch.color}`
                              : '2px solid var(--border-default)',
                      opacity: inBranch && !isForkPoint && !isMergePoint ? 0.5 : 1,
                      transition: 'all 0.2s',
                      position: 'relative',
                    }}
                  >
                    <img
                      src={getThumbnailUrl(screenshot.filename)}
                      alt={screenshot.filename}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                      }}
                    />
                    {/* 序号 */}
                    <div style={{
                      position: 'absolute',
                      top: '2px',
                      left: '2px',
                      fontSize: '10px',
                      background: 'rgba(0,0,0,0.7)',
                      color: '#fff',
                      padding: '1px 4px',
                      borderRadius: '3px',
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
                        width: '16px',
                        height: '16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}>
                        <GitFork size={10} color="#fff" />
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
                        width: '16px',
                        height: '16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}>
                        <GitMerge size={10} color="#fff" />
                      </div>
                    )}
                  </div>
                  {/* 分支标记 - 显示该截图属于哪个分支 */}
                  {inBranch && !isForkPoint && (
                    <div style={{
                      position: 'absolute',
                      bottom: '-18px',
                      left: '50%',
                      transform: 'translateX(-50%)',
                      fontSize: '9px',
                      color: inBranch.color,
                      whiteSpace: 'nowrap',
                      background: 'var(--bg-primary)',
                      padding: '1px 4px',
                      borderRadius: '3px',
                    }}>
                      {inBranch.name}
                    </div>
                  )}
                </div>
                
                {/* 箭头 - 放在图片外部 */}
                {displayIndex < onboardingScreenshots.length - 1 && (
                  <div style={{
                    padding: '0 4px',
                    color: 'var(--text-muted)',
                    fontSize: '14px',
                    flexShrink: 0,
                  }}>
                    →
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* 分支行 */}
        {branchData.branches.map((branch, branchIdx) => {
          const ITEM_WIDTH = CARD_WIDTH + 16 // 图片宽度 + 箭头区域
          const forkDisplayIdx = branch.fork_from - startIdx
          // 分支从 fork_from + 1 开始显示
          const branchStartDisplayIdx = forkDisplayIdx + 1
          
          return (
            <div
              key={branch.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                marginTop: '20px',
              }}
            >
              {/* 分支标签 - 与主流程标签对齐 */}
              <div style={{
                width: '60px',
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}>
                {/* 颜色方块 */}
                <div style={{
                  width: '10px',
                  height: '10px',
                  background: branch.color,
                  borderRadius: '2px',
                  flexShrink: 0,
                }} />
                {/* 标签文字 */}
                <span style={{
                  fontSize: '11px',
                  color: branch.color,
                  fontWeight: 600,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  {branch.name || `分支${branchIdx + 1}`}
                </span>
              </div>
              
              {/* 占位元素 - 让分支截图与主流程对齐 */}
              {Array.from({ length: branchStartDisplayIdx }).map((_, i) => (
                <div
                  key={`placeholder-${i}`}
                  style={{
                    width: `${ITEM_WIDTH}px`,
                    height: `${CARD_HEIGHT}px`,
                    flexShrink: 0,
                    position: 'relative',
                  }}
                >
                  {/* 在分叉点位置画斜线 */}
                  {i === forkDisplayIdx && (
                    <svg
                      style={{
                        position: 'absolute',
                        top: '0',
                        left: `${CARD_WIDTH / 2}px`,
                        overflow: 'visible',
                        pointerEvents: 'none',
                      }}
                      width={ITEM_WIDTH}
                      height={CARD_HEIGHT + 20}
                    >
                      <line
                        x1="0"
                        y1="0"
                        x2={ITEM_WIDTH - 8}
                        y2={CARD_HEIGHT}
                        stroke={branch.color}
                        strokeWidth="2"
                      />
                    </svg>
                  )}
                </div>
              ))}
              
              {/* 分支截图 - 只显示分叉点之后的截图 */}
              {branch.screens
                .filter(screenIdx => screenIdx > branch.fork_from)
                .map((screenIdx, i, filteredScreens) => {
                const screenshot = screenshots[screenIdx]
                if (!screenshot) return null
                
                return (
                  <div key={screenIdx} style={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    width: i < filteredScreens.length - 1 ? `${ITEM_WIDTH}px` : 'auto',
                    flexShrink: 0,
                  }}>
                    <div
                      onClick={(e) => onScreenClick(e, screenIdx, screenshot.filename)}
                      style={{
                        width: `${CARD_WIDTH}px`,
                        height: `${CARD_HEIGHT}px`,
                        borderRadius: '6px',
                        overflow: 'hidden',
                        cursor: 'pointer',
                        border: `3px solid ${branch.color}`,
                        position: 'relative',
                      }}
                    >
                      <img
                        src={getThumbnailUrl(screenshot.filename)}
                        alt={screenshot.filename}
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                        }}
                      />
                      <div style={{
                        position: 'absolute',
                        top: '2px',
                        left: '2px',
                        fontSize: '10px',
                        background: branch.color,
                        color: '#fff',
                        padding: '1px 4px',
                        borderRadius: '3px',
                      }}>
                        {screenIdx + 1}
                      </div>
                    </div>
                    
                    {/* 箭头 - 放在图片外部 */}
                    {i < filteredScreens.length - 1 && (
                      <div style={{
                        padding: '0 4px',
                        color: branch.color,
                        fontSize: '14px',
                        flexShrink: 0,
                      }}>
                        →
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )
        })}

        {/* 图例 */}
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '340px',
          display: 'flex',
          gap: '16px',
          background: 'var(--bg-card)',
          padding: '8px 16px',
          borderRadius: '8px',
          fontSize: '12px',
          color: 'var(--text-muted)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', background: '#ef4444', borderRadius: '50%' }} />
            分支点
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', background: '#8b5cf6', borderRadius: '50%' }} />
            汇合点
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', background: '#22c55e', borderRadius: '2px' }} />
            待选截图
          </div>
        </div>
      </div>
    </div>
  )
}
