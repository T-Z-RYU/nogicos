/**
 * 项目状态管理
 */
import { create } from 'zustand'
import type { Project, ProjectListResponse } from '@/types'
import { getProjects } from '@/lib/api'

interface ProjectState {
  // 数据
  projects: Project[]
  total: number
  stats: {
    total_screens: number
    checked: number
    onboarding_marked: number
  } | null

  // 筛选
  search: string
  sourceFilter: 'all' | 'projects' | 'downloads_2024'

  // 状态
  loading: boolean
  error: string | null

  // 操作
  fetchProjects: () => Promise<void>
  setSearch: (search: string) => void
  setSourceFilter: (source: 'all' | 'projects' | 'downloads_2024') => void
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  // 初始状态
  projects: [],
  total: 0,
  stats: null,
  search: '',
  sourceFilter: 'all',
  loading: false,
  error: null,

  // 获取项目列表
  fetchProjects: async () => {
    set({ loading: true, error: null })

    try {
      const { search, sourceFilter } = get()
      const params: Record<string, string> = {}

      if (search) params.search = search
      if (sourceFilter !== 'all') params.source = sourceFilter

      const response = await getProjects(params)

      set({
        projects: response.projects,
        total: response.total,
        stats: response.stats || null,
        loading: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '获取项目失败',
        loading: false,
      })
    }
  },

  // 设置搜索
  setSearch: (search) => {
    set({ search })
  },

  // 设置来源筛选
  setSourceFilter: (source) => {
    set({ sourceFilter: source })
  },
}))


