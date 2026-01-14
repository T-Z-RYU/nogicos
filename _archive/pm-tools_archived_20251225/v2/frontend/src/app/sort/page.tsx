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
import { importScreenshot, uploadScreenshot } from '@/lib/api'
import type { Screenshot } from '@/types'
import { ZOOM_CONFIG } from '@/types/sort'
import {
  ArrowUpDown,
  Save,
  Check,
  Trash2,
  RotateCcw,
  CheckSquare,
  X,
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

export default function SortPage() {
  // Store
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
    insertScreenshotAt,
  } = useSortStore()

  // Local State
  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [showDeleted, setShowDeleted] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)
  const [dropTargetIndex, setDropTargetIndex] = useState<number | null>(null)
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [newlyAdded, setNewlyAdded] = useState<string | null>(null)
  const [externalImportedFile, setExternalImportedFile] = useState<string | null>(null) // 外部拖拽导入的文件名
  
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
    } else {
      reset()
    }
  }, [selectedProject, fetchData, reset])

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
      if (e.key === 'Escape') { deselectAll(); setPreviewIndex(null) }
      if (e.key === 'ArrowLeft' && previewIndex !== null) { prevPreview() }
      if (e.key === 'ArrowRight' && previewIndex !== null) { nextPreview() }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedProject, selectedFiles, previewIndex, selectAll, deselectAll, 
      deleteSelected, setPreviewIndex, prevPreview, nextPreview, zoomIn, zoomOut, resetZoom])

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
      
      // 更新预览索引：如果正在预览的图片被移动了，跟随它的新位置
      if (previewIndex !== null) {
        if (previewIndex === oldIndex) {
          // 正在预览的图片被拖动，更新到新位置
          setPreviewIndex(newIndex)
        } else if (oldIndex < previewIndex && newIndex >= previewIndex) {
          // 图片从预览位置前面移到后面，预览索引减 1
          setPreviewIndex(previewIndex - 1)
        } else if (oldIndex > previewIndex && newIndex <= previewIndex) {
          // 图片从预览位置后面移到前面，预览索引加 1
          setPreviewIndex(previewIndex + 1)
        }
      }
      
        reorder(oldIndex, newIndex)
      }
  }, [sortedScreenshots, reorder, previewIndex, setPreviewIndex])

  const handleCardClick = useCallback((e: React.MouseEvent, index: number, filename: string) => {
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
  }, [lastClickedIndex, sortedScreenshots, setPreviewIndex, setSelectedFiles, toggleSelect, setLastClickedIndex])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!selectedProject) return
    
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
  }, [selectedProject, sortedScreenshots.length])

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

    // 处理待处理区拖来的截图
    const pendingData = e.dataTransfer.getData('application/x-pending-screenshot')
    if (pendingData) {
      try {
        const { filename } = JSON.parse(pendingData)
        const result = await importScreenshot(selectedProject, filename)
        if (result.success && result.new_filename) {
          const newScreenshot: Screenshot = { filename: result.new_filename, path: '' }
          const current = useSortStore.getState().sortedScreenshots
          useSortStore.setState({
            sortedScreenshots: [...current.slice(0, targetIndex), newScreenshot, ...current.slice(targetIndex)],
            hasChanges: true
          })
          setUploadMessage(`✓ 已插入 ${result.new_filename}`)
          setNewlyAdded(result.new_filename)
          setTimeout(() => { setUploadMessage(null); setNewlyAdded(null) }, 3000)
          // 通知 PendingPanel 标记该文件为已导入
          setExternalImportedFile(filename)
        }
      } catch (error) {
        toast.error('导入失败: ' + (error as Error).message)
      }
      return
    }

    // 处理外部文件
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

  // 自动导入时直接追加截图（不刷新整个列表）
  const handleAppendScreenshot = useCallback((filename: string) => {
    insertScreenshotAt({ filename, path: '' }, sortedScreenshots.length)
  }, [sortedScreenshots.length, insertScreenshotAt])

  const handleDeleteSelected = useCallback(() => {
    if (!selectedProject) return
    const count = selectedFiles.size
    if (count <= 10 || window.confirm(`确定要删除 ${count} 张截图吗？`)) {
      deleteSelected(selectedProject)
    }
  }, [selectedProject, selectedFiles.size, deleteSelected])

  // ==================== Derived State ====================

  const activeScreenshot = activeId ? sortedScreenshots.find(s => s.filename === activeId) : null
  const previewScreenshot = previewIndex !== null ? sortedScreenshots[previewIndex] : null
  const displayProjectName = selectedProject?.replace('downloads_2024/', '') || ''

  // ==================== Render ====================

  // 内联样式定义
  const pageStyles = {
    pendingSidebar: {
      width: '320px',
      flexShrink: 0,
      borderRight: '1px solid var(--border-default)',
      overflow: 'hidden' as const,
      padding: '12px',
      display: 'flex',
      flexDirection: 'column' as const,
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
      paddingBottom: '2px', // 防止滚动条遮挡
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
      paddingBottom: '300px', // 底部留白，方便滚动查看
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
  }

  return (
    <AppLayout>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* 左侧待处理区 */}
        <div style={pageStyles.pendingSidebar}>
          <PendingPanel selectedProject={selectedProject} onImportSuccess={handleImportSuccess} onAppendScreenshot={handleAppendScreenshot} externalImportedFile={externalImportedFile} />
        </div>

        {/* 主内容区 */}
        <div style={pageStyles.mainContent}>
          {/* 顶栏 */}
          <div className="topbar" style={{ overflow: 'visible' }}>
            <h1 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', whiteSpace: 'nowrap', flexShrink: 0 }}>截图排序</h1>
            <div style={{ flex: 1, minWidth: '8px' }} />

            {/* 缩放控制 */}
            {selectedProject && sortedScreenshots.length > 0 && (
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

            {/* 操作按钮 */}
            {selectedProject && sortedScreenshots.length > 0 && (
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
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {/* 拖拽提示 */}
            {isDragOver && (
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
                <ArrowUpDown size={48} />
                <p>请选择一个项目来排序截图</p>
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
              {showDeleted && deletedBatches.length > 0 && (
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

            {/* 排序网格 */}
            {selectedProject && !loading && sortedScreenshots.length > 0 && (
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
        {selectedFiles.size > 0 && selectedProject && (
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
