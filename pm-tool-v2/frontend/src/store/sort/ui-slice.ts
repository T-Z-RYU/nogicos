/**
 * UI Slice - 管理 UI 状态
 */
import type { StateCreator } from 'zustand'
import type { UISlice, SortStore } from '@/types/sort'

export const createUISlice: StateCreator<
  SortStore,
  [],
  [],
  UISlice
> = (set) => ({
  loading: false,
  saving: false,
  error: null,
  hasChanges: false,

  setLoading: (loading: boolean) => {
    set({ loading })
  },

  setSaving: (saving: boolean) => {
    set({ saving })
  },

  setError: (error: string | null) => {
    set({ error })
  },

  setHasChanges: (hasChanges: boolean) => {
    set({ hasChanges })
  },
})
