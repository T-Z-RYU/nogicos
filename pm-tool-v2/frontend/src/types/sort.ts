/**
 * 排序模块类型定义
 */
import type { Screenshot, Project } from './index'

// ==================== 缩放配置 ====================

export interface ZoomConfig {
  min: number
  max: number
  step: number
  default: number
}

export const ZOOM_CONFIG: ZoomConfig = {
  min: 50,
  max: 200,
  step: 25,
  default: 100,
}

// ==================== 拖拽相关 ====================

export interface DragState {
  activeId: string | null
  overId: string | null
}

export interface DropAnimationConfig {
  duration: number
  easing: string
}

// ==================== Store Slices ====================

export interface DataSlice {
  screenshots: Screenshot[]
  sortedScreenshots: Screenshot[]
  deletedBatches: DeletedBatch[]
  onboardingRange: OnboardingRange
  
  fetchData: (projectName: string) => Promise<void>
  reorder: (oldIndex: number, newIndex: number) => void
  deleteSelected: (projectName: string) => Promise<void>
  restoreBatch: (projectName: string, batch: string) => Promise<void>
  saveSortOrder: (projectName: string) => Promise<void>
  applySortOrder: (projectName: string) => Promise<void>
  insertScreenshotAt: (screenshot: Screenshot, index: number) => void
}

export interface SelectionSlice {
  selectedFiles: Set<string>
  lastClickedIndex: number | null
  
  toggleSelect: (filename: string) => void
  selectAll: () => void
  deselectAll: () => void
  setSelectedFiles: (files: Set<string>) => void
  setLastClickedIndex: (index: number | null) => void
}

export interface PreviewSlice {
  previewIndex: number | null
  
  setPreviewIndex: (index: number | null) => void
  prevPreview: () => void
  nextPreview: () => void
}

export interface UISlice {
  loading: boolean
  saving: boolean
  error: string | null
  hasChanges: boolean
  
  setLoading: (loading: boolean) => void
  setSaving: (saving: boolean) => void
  setError: (error: string | null) => void
  setHasChanges: (hasChanges: boolean) => void
}

export interface ZoomSlice {
  zoom: number
  
  zoomIn: () => void
  zoomOut: () => void
  resetZoom: () => void
  setZoom: (zoom: number) => void
}

// 合并的 Store 类型
export type SortStore = DataSlice & SelectionSlice & PreviewSlice & UISlice & ZoomSlice & {
  reset: () => void
}

// ==================== API 相关 ====================

export interface DeletedBatch {
  timestamp: string
  count: number
  files: string[]
}

export interface OnboardingRange {
  start: number
  end: number
}

export interface SortItem {
  original_file: string
  new_index: number
}

// ==================== 组件 Props ====================

export interface ProjectSelectorProps {
  projects: Project[]
  selectedProject: string | null
  onSelect: (name: string | null) => void
}

export interface SortableScreenshotProps {
  screenshot: Screenshot
  projectName: string
  index: number
  isSelected: boolean
  isNewlyAdded?: boolean
  isDragging?: boolean
  onCardClick: (e: React.MouseEvent) => void
  onboardingStart: number
  onboardingEnd: number
}

export interface DragPreviewProps {
  screenshot: Screenshot
  projectName: string
  zoom?: number
}

export interface ZoomControlProps {
  zoom: number
  onZoomIn: () => void
  onZoomOut: () => void
  onReset: () => void
  min?: number
  max?: number
}

export interface SelectionBarProps {
  selectedCount: number
  onDeselect: () => void
  onDelete: () => void
  disabled?: boolean
}

export interface SortGridProps {
  screenshots: Screenshot[]
  projectName: string
  selectedFiles: Set<string>
  newlyAdded: string | null
  zoom: number
  onboardingStart: number
  onboardingEnd: number
  onCardClick: (e: React.MouseEvent, index: number, filename: string) => void
  dropTargetIndex: number | null
  isDragOver: boolean
}
