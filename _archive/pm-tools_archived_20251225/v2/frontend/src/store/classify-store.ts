/**
 * 分类状态管理
 */
import { create } from 'zustand'
import type { Screenshot } from '@/types'
import {
  getScreenshots,
  getTaxonomy,
  updateClassification,
  type Taxonomy,
  type ClassificationUpdate,
} from '@/lib/api'

interface ClassifyState {
  // 数据
  screenshots: Screenshot[]
  unclassified: Screenshot[]
  classified: Record<string, Screenshot[]>  // stage -> screenshots
  taxonomy: Taxonomy | null
  
  // UI 状态
  loading: boolean
  saving: boolean
  error: string | null
  
  // 当前选择
  selectedFiles: Set<string>
  draggedFile: string | null
  
  // 操作
  fetchData: (projectName: string) => Promise<void>
  toggleSelect: (filename: string) => void
  selectAll: () => void
  deselectAll: () => void
  setDraggedFile: (filename: string | null) => void
  assignToStage: (projectName: string, filenames: string[], stage: string) => Promise<void>
  removeFromStage: (projectName: string, filename: string) => Promise<void>
  reset: () => void
}

const initialState = {
  screenshots: [],
  unclassified: [],
  classified: {} as Record<string, Screenshot[]>,
  taxonomy: null as Taxonomy | null,
  loading: false,
  saving: false,
  error: null as string | null,
  selectedFiles: new Set<string>(),
  draggedFile: null as string | null,
}

export const useClassifyStore = create<ClassifyState>((set, get) => ({
  ...initialState,

  fetchData: async (projectName: string) => {
    set({ loading: true, error: null })

    try {
      const [screenshotsRes, taxonomyRes] = await Promise.all([
        getScreenshots(projectName),
        getTaxonomy(),
      ])

      const screenshots = screenshotsRes.screenshots
      const taxonomy = taxonomyRes.taxonomy

      // 分组：未分类 vs 已分类
      const unclassified: Screenshot[] = []
      const classified: Record<string, Screenshot[]> = {}

      // 初始化所有阶段
      taxonomy.stages.forEach(stage => {
        classified[stage] = []
      })

      screenshots.forEach(screenshot => {
        const stage = screenshot.classification?.stage
        if (stage && taxonomy.stages.includes(stage)) {
          classified[stage].push(screenshot)
        } else {
          unclassified.push(screenshot)
        }
      })

      set({
        screenshots,
        unclassified,
        classified,
        taxonomy,
        selectedFiles: new Set(),
        loading: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '加载失败',
        loading: false,
      })
    }
  },

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
    const { unclassified } = get()
    set({
      selectedFiles: new Set(unclassified.map(s => s.filename))
    })
  },

  deselectAll: () => {
    set({ selectedFiles: new Set() })
  },

  setDraggedFile: (filename: string | null) => {
    set({ draggedFile: filename })
  },

  assignToStage: async (projectName: string, filenames: string[], stage: string) => {
    set({ saving: true, error: null })

    try {
      const changes: Record<string, ClassificationUpdate> = {}
      filenames.forEach(f => {
        changes[f] = { stage }
      })

      await updateClassification(projectName, changes)

      // 更新本地状态
      const { unclassified, classified, screenshots } = get()
      
      const newUnclassified = unclassified.filter(s => !filenames.includes(s.filename))
      const movedScreenshots = screenshots.filter(s => filenames.includes(s.filename))
      
      const newClassified = { ...classified }
      newClassified[stage] = [...(newClassified[stage] || []), ...movedScreenshots]

      set({
        unclassified: newUnclassified,
        classified: newClassified,
        selectedFiles: new Set(),
        saving: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '分类失败',
        saving: false,
      })
    }
  },

  removeFromStage: async (projectName: string, filename: string) => {
    set({ saving: true, error: null })

    try {
      await updateClassification(projectName, {
        [filename]: { stage: '' }
      })

      // 更新本地状态
      const { unclassified, classified, screenshots } = get()
      
      const screenshot = screenshots.find(s => s.filename === filename)
      if (!screenshot) return

      const newClassified = { ...classified }
      
      // 从所有阶段中移除
      Object.keys(newClassified).forEach(stage => {
        newClassified[stage] = newClassified[stage].filter(s => s.filename !== filename)
      })

      set({
        unclassified: [...unclassified, screenshot],
        classified: newClassified,
        saving: false,
      })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '移除失败',
        saving: false,
      })
    }
  },

  reset: () => {
    set(initialState)
  },
}))
