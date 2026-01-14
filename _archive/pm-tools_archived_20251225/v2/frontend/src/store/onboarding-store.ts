/**
 * Onboarding 状态管理
 */
import { create } from 'zustand'
import type { Screenshot } from '@/types'
import {
  getScreenshots,
  getOnboardingRange,
  saveOnboardingRange,
  type OnboardingRange,
} from '@/lib/api'

interface OnboardingState {
  // 数据
  screenshots: Screenshot[]
  total: number
  onboardingRange: OnboardingRange
  
  // 选择状态
  selectionMode: 'start' | 'end' | null
  previewStart: number
  previewEnd: number
  
  // UI 状态
  loading: boolean
  saving: boolean
  error: string | null
  
  // 操作
  fetchData: (projectName: string) => Promise<void>
  setSelectionMode: (mode: 'start' | 'end' | null) => void
  selectScreenshot: (index: number, projectName?: string) => void
  saveRange: (projectName: string) => Promise<void>
  clearRange: (projectName: string) => Promise<void>
  reset: () => void
}

const initialState = {
  screenshots: [],
  total: 0,
  onboardingRange: { start: -1, end: -1 },
  selectionMode: null as 'start' | 'end' | null,
  previewStart: -1,
  previewEnd: -1,
  loading: false,
  saving: false,
  error: null as string | null,
}

export const useOnboardingStore = create<OnboardingState>((set, get) => ({
  ...initialState,

  fetchData: async (projectName: string) => {
    set({ loading: true, error: null })

    try {
      const [screenshotsRes, rangeRes] = await Promise.all([
        getScreenshots(projectName),
        getOnboardingRange(projectName),
      ])

      set({
        screenshots: screenshotsRes.screenshots,
        total: screenshotsRes.total,
        onboardingRange: rangeRes,
        previewStart: rangeRes.start,
        previewEnd: rangeRes.end,
        loading: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '加载失败',
        loading: false,
      })
    }
  },

  setSelectionMode: (mode) => {
    set({ selectionMode: mode })
  },

  selectScreenshot: (index: number, projectName?: string) => {
    const { selectionMode, previewStart, previewEnd } = get()

    if (selectionMode === 'start') {
      // 设置起点，如果起点大于终点，自动调整终点
      const newEnd = previewEnd >= 0 && index > previewEnd ? index : previewEnd
      set({
        previewStart: index,
        previewEnd: newEnd,
        selectionMode: null,
      })
      
      // 自动保存（如果起点和终点都设置好了）
      if (newEnd >= 0 && projectName) {
        get().saveRange(projectName)
      }
    } else if (selectionMode === 'end') {
      // 设置终点，如果终点小于起点，自动调整起点
      const newStart = previewStart >= 0 && index < previewStart ? index : previewStart
      set({
        previewStart: newStart,
        previewEnd: index,
        selectionMode: null,
      })
      
      // 自动保存（如果起点和终点都设置好了）
      if (newStart >= 0 && projectName) {
        get().saveRange(projectName)
      }
    }
  },

  saveRange: async (projectName: string) => {
    const { previewStart, previewEnd } = get()

    if (previewStart < 0 || previewEnd < 0) {
      set({ error: '请先设置起点和终点' })
      return
    }

    set({ saving: true, error: null })

    try {
      await saveOnboardingRange(projectName, previewStart, previewEnd)
      set({
        onboardingRange: { start: previewStart, end: previewEnd },
        saving: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '保存失败',
        saving: false,
      })
    }
  },

  clearRange: async (projectName: string) => {
    set({ saving: true, error: null })

    try {
      await saveOnboardingRange(projectName, -1, -1)
      set({
        onboardingRange: { start: -1, end: -1 },
        previewStart: -1,
        previewEnd: -1,
        saving: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '清除失败',
        saving: false,
      })
    }
  },

  reset: () => {
    set(initialState)
  },
}))






