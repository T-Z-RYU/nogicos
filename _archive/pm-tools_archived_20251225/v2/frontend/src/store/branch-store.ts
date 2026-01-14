/**
 * 分支流程状态管理
 */
import { create } from 'zustand'
import type { Screenshot } from '@/types'
import { getOnboardingRange } from '@/lib/api'

// ============ 类型定义 ============

export interface ForkPoint {
  index: number
  name: string
}

export interface Branch {
  id: string
  name: string
  color: string
  fork_from: number
  screens: number[]
  merge_to: number | null
}

export interface BranchData {
  version: string
  fork_points: ForkPoint[]
  merge_points: number[]
  branches: Branch[]
  updated_at: string | null
}

// ============ API 函数 ============
// 新 URL 结构：操作类型在 project_name 之前，避免 :path 贪婪匹配

const API_BASE = '/api'

export async function getBranchData(projectName: string): Promise<BranchData> {
  const response = await fetch(`${API_BASE}/branch/data/${projectName}`)
  if (!response.ok) {
    throw new Error('获取分支数据失败')
  }
  return response.json()
}

export async function saveBranchData(
  projectName: string,
  data: { fork_points: ForkPoint[]; merge_points: number[]; branches: Branch[] }
): Promise<{ success: boolean; data: BranchData }> {
  const response = await fetch(`${API_BASE}/branch/data/${projectName}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error('保存分支数据失败')
  }
  return response.json()
}

export async function addForkPoint(
  projectName: string,
  index: number,
  name: string = ''
): Promise<{ success: boolean; fork_points: ForkPoint[] }> {
  const response = await fetch(`${API_BASE}/branch/fork-point/${projectName}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ index, name }),
  })
  if (!response.ok) {
    throw new Error('添加分支点失败')
  }
  return response.json()
}

export async function removeForkPoint(
  projectName: string,
  index: number
): Promise<{ success: boolean; fork_points: ForkPoint[] }> {
  const response = await fetch(
    `${API_BASE}/branch/fork-point/${index}/${projectName}`,
    { method: 'DELETE' }
  )
  if (!response.ok) {
    throw new Error('删除分支点失败')
  }
  return response.json()
}

export async function addMergePoint(
  projectName: string,
  index: number
): Promise<{ success: boolean; merge_points: number[] }> {
  const response = await fetch(`${API_BASE}/branch/merge-point/${projectName}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ index }),
  })
  if (!response.ok) {
    throw new Error('添加汇合点失败')
  }
  return response.json()
}

export async function removeMergePoint(
  projectName: string,
  index: number
): Promise<{ success: boolean; merge_points: number[] }> {
  const response = await fetch(
    `${API_BASE}/branch/merge-point/${index}/${projectName}`,
    { method: 'DELETE' }
  )
  if (!response.ok) {
    throw new Error('删除汇合点失败')
  }
  return response.json()
}

export async function addBranch(
  projectName: string,
  branch: Omit<Branch, 'id'>
): Promise<{ success: boolean; branch: Branch }> {
  const response = await fetch(`${API_BASE}/branch/path/${projectName}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(branch),
  })
  if (!response.ok) {
    throw new Error('添加分支失败')
  }
  return response.json()
}

export async function updateBranch(
  projectName: string,
  branchId: string,
  branch: Omit<Branch, 'id'>
): Promise<{ success: boolean; branch: Branch }> {
  const response = await fetch(
    `${API_BASE}/branch/path/${branchId}/${projectName}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(branch),
    }
  )
  if (!response.ok) {
    throw new Error('更新分支失败')
  }
  return response.json()
}

export async function deleteBranch(
  projectName: string,
  branchId: string
): Promise<{ success: boolean }> {
  const response = await fetch(
    `${API_BASE}/branch/path/${branchId}/${projectName}`,
    { method: 'DELETE' }
  )
  if (!response.ok) {
    throw new Error('删除分支失败')
  }
  return response.json()
}

export async function clearBranchData(projectName: string): Promise<{ success: boolean }> {
  const response = await fetch(`${API_BASE}/branch/clear/${projectName}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('清空分支数据失败')
  }
  return response.json()
}

// ============ 预定义颜色 ============

export const BRANCH_COLORS = [
  { name: '绿色', value: '#22c55e' },
  { name: '蓝色', value: '#3b82f6' },
  { name: '紫色', value: '#a855f7' },
  { name: '橙色', value: '#f59e0b' },
  { name: '粉色', value: '#ec4899' },
  { name: '青色', value: '#06b6d4' },
  { name: '红色', value: '#ef4444' },
  { name: '靛蓝', value: '#6366f1' },
]

// ============ Store 定义 ============

interface BranchState {
  // 数据
  branchData: BranchData
  screenshots: Screenshot[]
  onboardingRange: { start: number; end: number }
  
  // 编辑状态
  editMode: 'none' | 'fork' | 'merge' | 'branch'
  selectedBranch: string | null
  pendingBranchScreens: number[]
  
  // UI 状态
  loading: boolean
  saving: boolean
  error: string | null
  
  // 操作
  fetchData: (projectName: string) => Promise<void>
  setEditMode: (mode: 'none' | 'fork' | 'merge' | 'branch') => void
  
  // 分支点操作
  toggleForkPoint: (projectName: string, index: number) => Promise<void>
  updateForkPointName: (projectName: string, index: number, name: string) => Promise<void>
  
  // 汇合点操作
  toggleMergePoint: (projectName: string, index: number) => Promise<void>
  
  // 分支操作
  toggleScreenInPending: (index: number) => void
  clearPendingScreens: () => void
  createBranch: (projectName: string, name: string, color: string, forkFrom: number, mergeTo: number | null) => Promise<void>
  removeBranch: (projectName: string, branchId: string) => Promise<void>
  selectBranch: (branchId: string | null) => void
  
  // 清空
  clearAll: (projectName: string) => Promise<void>
  reset: () => void
}

const initialState = {
  branchData: {
    version: '1.0',
    fork_points: [],
    merge_points: [],
    branches: [],
    updated_at: null,
  } as BranchData,
  screenshots: [],
  onboardingRange: { start: -1, end: -1 },
  editMode: 'none' as const,
  selectedBranch: null as string | null,
  pendingBranchScreens: [] as number[],
  loading: false,
  saving: false,
  error: null as string | null,
}

export const useBranchStore = create<BranchState>((set, get) => ({
  ...initialState,

  fetchData: async (projectName: string) => {
    set({ loading: true, error: null })

    try {
      // 并行获取分支数据、截图列表和 Onboarding 范围
      const [branchData, screenshotsRes, onboardingRange] = await Promise.all([
        getBranchData(projectName),
        fetch(`/api/project-screenshots/${encodeURIComponent(projectName)}`).then(r => r.json()),
        getOnboardingRange(projectName),
      ])

      set({
        branchData,
        screenshots: screenshotsRes.screenshots || [],
        onboardingRange,
        loading: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '加载失败',
        loading: false,
      })
    }
  },

  setEditMode: (mode) => {
    set({ editMode: mode, pendingBranchScreens: [] })
  },

  toggleForkPoint: async (projectName: string, index: number) => {
    const { branchData } = get()
    set({ saving: true, error: null })

    try {
      const exists = branchData.fork_points.some((fp) => fp.index === index)
      
      if (exists) {
        const result = await removeForkPoint(projectName, index)
        set((state) => ({
          branchData: { ...state.branchData, fork_points: result.fork_points },
          saving: false,
        }))
      } else {
        const result = await addForkPoint(projectName, index)
        set((state) => ({
          branchData: { ...state.branchData, fork_points: result.fork_points },
          saving: false,
        }))
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '操作失败',
        saving: false,
      })
    }
  },

  updateForkPointName: async (projectName: string, index: number, name: string) => {
    set({ saving: true, error: null })

    try {
      const result = await addForkPoint(projectName, index, name)
      set((state) => ({
        branchData: { ...state.branchData, fork_points: result.fork_points },
        saving: false,
      }))
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '操作失败',
        saving: false,
      })
    }
  },

  toggleMergePoint: async (projectName: string, index: number) => {
    const { branchData } = get()
    set({ saving: true, error: null })

    try {
      const exists = branchData.merge_points.includes(index)
      
      if (exists) {
        const result = await removeMergePoint(projectName, index)
        set((state) => ({
          branchData: { ...state.branchData, merge_points: result.merge_points },
          saving: false,
        }))
      } else {
        const result = await addMergePoint(projectName, index)
        set((state) => ({
          branchData: { ...state.branchData, merge_points: result.merge_points },
          saving: false,
        }))
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '操作失败',
        saving: false,
      })
    }
  },

  toggleScreenInPending: (index: number) => {
    set((state) => {
      const exists = state.pendingBranchScreens.includes(index)
      return {
        pendingBranchScreens: exists
          ? state.pendingBranchScreens.filter((i) => i !== index)
          : [...state.pendingBranchScreens, index].sort((a, b) => a - b),
      }
    })
  },

  clearPendingScreens: () => {
    set({ pendingBranchScreens: [] })
  },

  createBranch: async (projectName: string, name: string, color: string, forkFrom: number, mergeTo: number | null) => {
    const { pendingBranchScreens } = get()
    
    if (pendingBranchScreens.length === 0) {
      set({ error: '请先选择分支包含的截图' })
      return
    }

    set({ saving: true, error: null })

    try {
      const result = await addBranch(projectName, {
        name,
        color,
        fork_from: forkFrom,
        screens: pendingBranchScreens,
        merge_to: mergeTo,
      })

      set((state) => ({
        branchData: {
          ...state.branchData,
          branches: [...state.branchData.branches, result.branch],
        },
        pendingBranchScreens: [],
        editMode: 'none',
        saving: false,
      }))
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '创建分支失败',
        saving: false,
      })
    }
  },

  removeBranch: async (projectName: string, branchId: string) => {
    set({ saving: true, error: null })

    try {
      await deleteBranch(projectName, branchId)
      
      set((state) => ({
        branchData: {
          ...state.branchData,
          branches: state.branchData.branches.filter((b) => b.id !== branchId),
        },
        selectedBranch: state.selectedBranch === branchId ? null : state.selectedBranch,
        saving: false,
      }))
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '删除分支失败',
        saving: false,
      })
    }
  },

  selectBranch: (branchId: string | null) => {
    set({ selectedBranch: branchId })
  },

  clearAll: async (projectName: string) => {
    set({ saving: true, error: null })

    try {
      await clearBranchData(projectName)
      set({
        branchData: {
          version: '1.0',
          fork_points: [],
          merge_points: [],
          branches: [],
          updated_at: null,
        },
        selectedBranch: null,
        pendingBranchScreens: [],
        saving: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '清空失败',
        saving: false,
      })
    }
  },

  reset: () => {
    set(initialState)
  },
}))
