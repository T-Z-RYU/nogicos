/**
 * Sort Store - 使用 Slices Pattern 组织的排序状态管理
 * 
 * 遵循 Zustand 最佳实践：
 * - 状态按功能拆分为独立 Slices
 * - 每个 Slice 管理自己的状态和操作
 * - 合并为单一 Store 导出
 */
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import type { SortStore } from '@/types/sort'
import { ZOOM_CONFIG } from '@/types/sort'

import { createDataSlice } from './data-slice'
import { createSelectionSlice } from './selection-slice'
import { createPreviewSlice } from './preview-slice'
import { createUISlice } from './ui-slice'
import { createZoomSlice } from './zoom-slice'

// 初始状态（用于 reset）
const initialState = {
  // Data
  screenshots: [],
  sortedScreenshots: [],
  deletedBatches: [],
  onboardingRange: { start: -1, end: -1 },
  // Selection
  selectedFiles: new Set<string>(),
  lastClickedIndex: null,
  // Preview
  previewIndex: null,
  // UI
  loading: false,
  saving: false,
  error: null,
  hasChanges: false,
  // Zoom
  zoom: ZOOM_CONFIG.default,
}

/**
 * 排序模块的统一 Store
 * 
 * 使用方式：
 * ```tsx
 * const { sortedScreenshots, zoom, zoomIn } = useSortStore()
 * // 或使用选择器优化性能
 * const zoom = useSortStore(state => state.zoom)
 * ```
 */
export const useSortStore = create<SortStore>()(
  devtools(
    (...args) => ({
      ...createDataSlice(...args),
      ...createSelectionSlice(...args),
      ...createPreviewSlice(...args),
      ...createUISlice(...args),
      ...createZoomSlice(...args),
      
      // 重置所有状态
      reset: () => {
        const [set] = args
        set(initialState)
      },
    }),
    { name: 'SortStore' }
  )
)

// 导出类型供外部使用
export type { SortStore }
