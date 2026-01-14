/**
 * 排序状态管理
 */
import { create } from 'zustand'
import type { Screenshot } from '@/types'
import {
  getScreenshots,
  saveSortOrder,
  applySortOrder,
  deleteScreens,
  getDeletedScreens,
  restoreScreens,
  getOnboardingRange,
  invalidateThumbnailCache,
  type SortItem,
  type DeletedBatch,
  type OnboardingRange,
} from '@/lib/api'

interface SortState {
  // 数据
  screenshots: Screenshot[]
  sortedScreenshots: Screenshot[]
  deletedBatches: DeletedBatch[]
  onboardingRange: OnboardingRange
  
  // 选择状态
  selectedFiles: Set<string>
  
  // 预览状态
  previewIndex: number | null
  
  // UI 状态
  loading: boolean
  saving: boolean
  error: string | null
  hasChanges: boolean
  
  // 操作
  fetchData: (projectName: string) => Promise<void>
  reorder: (oldIndex: number, newIndex: number) => void
  toggleSelect: (filename: string) => void
  selectAll: () => void
  deselectAll: () => void
  setSelectedFiles: (files: Set<string>) => void
  deleteSelected: (projectName: string) => Promise<void>
  restoreBatch: (projectName: string, batch: string) => Promise<void>
  saveSortOrder: (projectName: string) => Promise<void>
  applySortOrder: (projectName: string) => Promise<void>
  setPreviewIndex: (index: number | null) => void
  prevPreview: () => void
  nextPreview: () => void
  reset: () => void
  insertScreenshotAt: (screenshot: Screenshot, index: number) => void
  appendScreenshot: (screenshot: Screenshot) => void
}

const initialState = {
  screenshots: [],
  sortedScreenshots: [],
  deletedBatches: [],
  onboardingRange: { start: -1, end: -1 } as OnboardingRange,
  selectedFiles: new Set<string>(),
  previewIndex: null as number | null,
  loading: false,
  saving: false,
  error: null as string | null,
  hasChanges: false,
}

export const useSortStore = create<SortState>((set, get) => ({
  ...initialState,

  fetchData: async (projectName: string) => {
    set({ loading: true, error: null })
    
    // 每次获取数据时刷新缩略图缓存，确保显示最新内容
    invalidateThumbnailCache()

    try {
      const [screenshotsRes, deletedRes, onboardingRes] = await Promise.all([
        getScreenshots(projectName),
        getDeletedScreens(projectName),
        getOnboardingRange(projectName).catch(() => ({ start: -1, end: -1 })),
      ])

      set({
        screenshots: screenshotsRes.screenshots,
        sortedScreenshots: [...screenshotsRes.screenshots],
        deletedBatches: deletedRes.batches,
        onboardingRange: onboardingRes,
        selectedFiles: new Set(),
        previewIndex: null,
        hasChanges: false,
        loading: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '加载失败',
        loading: false,
      })
    }
  },

  reorder: (oldIndex: number, newIndex: number) => {
    const { sortedScreenshots } = get()
    const newSorted = [...sortedScreenshots]
    const [removed] = newSorted.splice(oldIndex, 1)
    newSorted.splice(newIndex, 0, removed)
    
    set({
      sortedScreenshots: newSorted,
      hasChanges: true,
    })
  },

  toggleSelect: (filename: string) => {
    const { selectedFiles } = get()
    const newSelected = new Set(selectedFiles)
    
    if (newSelected.has(filename)) {
      newSelected.delete(filename)
    } else {
      newSelected.add(filename)
    }
    
    set({ selectedFiles: newSelected })
  },

  selectAll: () => {
    const { sortedScreenshots } = get()
    set({
      selectedFiles: new Set(sortedScreenshots.map(s => s.filename))
    })
  },

  deselectAll: () => {
    set({ selectedFiles: new Set() })
  },

  setSelectedFiles: (files: Set<string>) => {
    set({ selectedFiles: files })
  },

  deleteSelected: async (projectName: string) => {
    const { selectedFiles, sortedScreenshots } = get()
    
    if (selectedFiles.size === 0) return

    set({ saving: true, error: null })

    try {
      await deleteScreens(projectName, Array.from(selectedFiles))
      
      // 从列表中移除已删除的截图
      const newSorted = sortedScreenshots.filter(
        s => !selectedFiles.has(s.filename)
      )
      
      // 重新加载已删除列表
      const deletedRes = await getDeletedScreens(projectName)
      
      set({
        sortedScreenshots: newSorted,
        deletedBatches: deletedRes.batches,
        selectedFiles: new Set(),
        hasChanges: true,
        saving: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '删除失败',
        saving: false,
      })
    }
  },

  restoreBatch: async (projectName: string, batch: string) => {
    set({ saving: true, error: null })

    try {
      await restoreScreens(projectName, batch)
      
      // 重新加载数据
      await get().fetchData(projectName)
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '恢复失败',
        saving: false,
      })
    }
  },

  saveSortOrder: async (projectName: string) => {
    const { sortedScreenshots } = get()

    set({ saving: true, error: null })

    try {
      const order: SortItem[] = sortedScreenshots.map((s, index) => ({
        original_file: s.filename,
        new_index: index + 1,
      }))

      await saveSortOrder(projectName, order)
      
      set({ saving: false, hasChanges: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '保存失败',
        saving: false,
      })
    }
  },

  applySortOrder: async (projectName: string) => {
    const { sortedScreenshots } = get()

    set({ saving: true, error: null })

    try {
      const order: SortItem[] = sortedScreenshots.map((s, index) => ({
        original_file: s.filename,
        new_index: index + 1,
      }))

      await applySortOrder(projectName, order)
      
      // 强制刷新缩略图缓存
      invalidateThumbnailCache()
      
      // 【优化】不再 fetchData，直接根据排序结果更新本地文件名
      // 重命名后文件名格式为 0001.png, 0002.png 等
      const updatedScreenshots = sortedScreenshots.map((s, index) => {
        // 获取文件扩展名
        const ext = s.filename.split('.').pop() || 'png'
        // 生成新文件名: 0001.png, 0002.png, ...
        const newFilename = `${String(index + 1).padStart(4, '0')}.${ext}`
        return {
          ...s,
          filename: newFilename,
        }
      })
      
      set({ 
        screenshots: updatedScreenshots,
        sortedScreenshots: updatedScreenshots,
        hasChanges: false, 
        saving: false 
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '应用失败',
        saving: false,
      })
    }
  },

  setPreviewIndex: (index: number | null) => {
    set({ previewIndex: index })
  },

  prevPreview: () => {
    const { previewIndex, sortedScreenshots } = get()
    if (previewIndex !== null && previewIndex > 0) {
      set({ previewIndex: previewIndex - 1 })
    }
  },

  nextPreview: () => {
    const { previewIndex, sortedScreenshots } = get()
    if (previewIndex !== null && previewIndex < sortedScreenshots.length - 1) {
      set({ previewIndex: previewIndex + 1 })
    }
  },

  reset: () => {
    set(initialState)
  },

  insertScreenshotAt: (screenshot: Screenshot, index: number) => {
    const { sortedScreenshots } = get()
    const newSorted = [...sortedScreenshots]
    
    // 在指定位置插入
    newSorted.splice(index, 0, screenshot)
    
    set({
      sortedScreenshots: newSorted,
      hasChanges: true,
    })
  },

  appendScreenshot: (screenshot: Screenshot) => {
    // 使用 set 函数形式确保获取最新状态（Zustand 最佳实践）
    set((state) => ({
      sortedScreenshots: [...state.sortedScreenshots, screenshot],
      hasChanges: true,
    }))
  },
}))






