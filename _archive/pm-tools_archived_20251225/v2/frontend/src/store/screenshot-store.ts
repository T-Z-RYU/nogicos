/**
 * 截图状态管理
 */
import { create } from 'zustand'
import type { Screenshot, ScreenshotListResponse } from '@/types'
import { getScreenshots } from '@/lib/api'

interface ScreenshotState {
  // 数据
  projectName: string | null
  screenshots: Screenshot[]
  total: number
  stages: Record<string, number>
  modules: Record<string, number>

  // 筛选
  stageFilter: string | null
  moduleFilter: string | null

  // 查看器
  selectedIndex: number | null

  // 状态
  loading: boolean
  error: string | null

  // 操作
  fetchScreenshots: (projectName: string) => Promise<void>
  setStageFilter: (stage: string | null) => void
  setModuleFilter: (module: string | null) => void
  setSelectedIndex: (index: number | null) => void
  nextScreenshot: () => void
  prevScreenshot: () => void
}

export const useScreenshotStore = create<ScreenshotState>((set, get) => ({
  // 初始状态
  projectName: null,
  screenshots: [],
  total: 0,
  stages: {},
  modules: {},
  stageFilter: null,
  moduleFilter: null,
  selectedIndex: null,
  loading: false,
  error: null,

  // 获取截图列表
  fetchScreenshots: async (projectName) => {
    set({ loading: true, error: null, projectName })

    try {
      const { stageFilter, moduleFilter } = get()
      const params: Record<string, string> = {}

      if (stageFilter) params.stage = stageFilter
      if (moduleFilter) params.module = moduleFilter

      const response = await getScreenshots(projectName, params)

      set({
        screenshots: response.screenshots,
        total: response.total,
        stages: response.stages || {},
        modules: response.modules || {},
        loading: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '获取截图失败',
        loading: false,
      })
    }
  },

  // 设置 Stage 筛选
  setStageFilter: (stage) => {
    set({ stageFilter: stage })
  },

  // 设置 Module 筛选
  setModuleFilter: (module) => {
    set({ moduleFilter: module })
  },

  // 设置选中索引
  setSelectedIndex: (index) => {
    set({ selectedIndex: index })
  },

  // 下一张
  nextScreenshot: () => {
    const { selectedIndex, screenshots } = get()
    if (selectedIndex !== null && selectedIndex < screenshots.length - 1) {
      set({ selectedIndex: selectedIndex + 1 })
    }
  },

  // 上一张
  prevScreenshot: () => {
    const { selectedIndex } = get()
    if (selectedIndex !== null && selectedIndex > 0) {
      set({ selectedIndex: selectedIndex - 1 })
    }
  },
}))


