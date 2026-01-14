/**
 * 预览 Slice - 管理截图预览状态
 */
import type { StateCreator } from 'zustand'
import type { PreviewSlice, SortStore } from '@/types/sort'

export const createPreviewSlice: StateCreator<
  SortStore,
  [],
  [],
  PreviewSlice
> = (set, get) => ({
  previewIndex: null,

  setPreviewIndex: (index: number | null) => {
    set({ previewIndex: index })
  },

  prevPreview: () => {
    const { previewIndex } = get()
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
})
