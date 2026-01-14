/**
 * 缩放 Slice - 管理缩放状态
 */
import type { StateCreator } from 'zustand'
import type { ZoomSlice, SortStore } from '@/types/sort'
import { ZOOM_CONFIG } from '@/types/sort'

export const createZoomSlice: StateCreator<
  SortStore,
  [],
  [],
  ZoomSlice
> = (set, get) => ({
  zoom: ZOOM_CONFIG.default,

  zoomIn: () => {
    const { zoom } = get()
    set({ zoom: Math.min(zoom + ZOOM_CONFIG.step, ZOOM_CONFIG.max) })
  },

  zoomOut: () => {
    const { zoom } = get()
    set({ zoom: Math.max(zoom - ZOOM_CONFIG.step, ZOOM_CONFIG.min) })
  },

  resetZoom: () => {
    set({ zoom: ZOOM_CONFIG.default })
  },

  setZoom: (zoom: number) => {
    set({ zoom: Math.max(ZOOM_CONFIG.min, Math.min(ZOOM_CONFIG.max, zoom)) })
  },
})
