'use client'

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export type FlowVersion = 'v1' | 'v2'

interface ABTestState {
  // 当前选择的流程版本
  currentVersion: FlowVersion
  
  // 是否启用 A/B 测试模式
  abTestEnabled: boolean
  
  // 切换版本
  setVersion: (version: FlowVersion) => void
  
  // 切换 A/B 测试模式
  toggleABTest: () => void
}

export const useABTestStore = create<ABTestState>()(
  persist(
    (set) => ({
      currentVersion: 'v1',
      abTestEnabled: false,
      
      setVersion: (version) => set({ currentVersion: version }),
      
      toggleABTest: () => set((state) => ({ abTestEnabled: !state.abTestEnabled }))
    }),
    {
      name: 'vitaflow-ab-test',
      storage: createJSONStorage(() => localStorage)
    }
  )
)

// 版本信息
export const VERSION_INFO = {
  v1: {
    name: 'Original Flow',
    pages: 37,
    description: '当前版本 - 基础流程',
    highlights: [
      '37页完整流程',
      '权限集中在后段',
      '标准问题节奏'
    ]
  },
  v2: {
    name: 'Optimized Flow',
    pages: 40,
    description: '优化版本 - 基于竞品分析',
    highlights: [
      '40页优化流程',
      '权限分散：间隔7-9页',
      '问题节奏：最多3连问',
      '软承诺设计：打断0-input',
      '更多鼓励过渡页'
    ]
  }
}

