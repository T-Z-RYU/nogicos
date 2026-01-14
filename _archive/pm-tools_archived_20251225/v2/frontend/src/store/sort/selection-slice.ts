/**
 * 选择 Slice - 管理截图的选择状态
 */
import type { StateCreator } from 'zustand'
import type { SelectionSlice, SortStore } from '@/types/sort'

export const createSelectionSlice: StateCreator<
  SortStore,
  [],
  [],
  SelectionSlice
> = (set, get) => ({
  selectedFiles: new Set<string>(),
  lastClickedIndex: null,

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

  setLastClickedIndex: (index: number | null) => {
    set({ lastClickedIndex: index })
  },
})
