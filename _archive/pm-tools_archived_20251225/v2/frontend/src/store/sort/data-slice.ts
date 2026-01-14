/**
 * 数据 Slice - 管理截图数据的加载、保存和操作
 */
import type { StateCreator } from 'zustand'
import type { Screenshot } from '@/types'
import type { DataSlice, SelectionSlice, UISlice, SortStore, DeletedBatch, OnboardingRange, SortItem } from '@/types/sort'
import {
  getScreenshots,
  saveSortOrder as apiSaveSortOrder,
  applySortOrder as apiApplySortOrder,
  deleteScreens,
  getDeletedScreens,
  restoreScreens,
  getOnboardingRange,
  invalidateThumbnailCache,
} from '@/lib/api'

export const createDataSlice: StateCreator<
  SortStore,
  [],
  [],
  DataSlice
> = (set, get) => ({
  screenshots: [],
  sortedScreenshots: [],
  deletedBatches: [],
  onboardingRange: { start: -1, end: -1 },

  fetchData: async (projectName: string) => {
    set({ loading: true, error: null })
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

  deleteSelected: async (projectName: string) => {
    const { selectedFiles, sortedScreenshots } = get()
    
    if (selectedFiles.size === 0) return

    set({ saving: true, error: null })

    try {
      await deleteScreens(projectName, Array.from(selectedFiles))
      
      const newSorted = sortedScreenshots.filter(
        s => !selectedFiles.has(s.filename)
      )
      
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

      await apiSaveSortOrder(projectName, order)
      
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

      await apiApplySortOrder(projectName, order)
      
      invalidateThumbnailCache()
      
      const updatedScreenshots = sortedScreenshots.map((s, index) => {
        const ext = s.filename.split('.').pop() || 'png'
        const newFilename = `${String(index + 1).padStart(4, '0')}.${ext}`
        return { ...s, filename: newFilename }
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

  insertScreenshotAt: (screenshot: Screenshot, index: number) => {
    const { sortedScreenshots } = get()
    const newSorted = [...sortedScreenshots]
    newSorted.splice(index, 0, screenshot)
    
    set({
      sortedScreenshots: newSorted,
      hasChanges: true,
    })
  },
})
