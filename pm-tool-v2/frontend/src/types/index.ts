/**
 * PM Tool v2 - TypeScript 类型定义
 * 与后端 Pydantic 模型对应
 */

// ==================== 分类相关 ====================

export interface Classification {
  stage?: string // Onboarding, Core, Monetization
  module?: string // Login, Permission, Paywall 等
  feature?: string // 功能点描述
  page_role?: string // 页面角色
  screen_type?: string // 页面类型（旧格式兼容）
  confidence: number // 分类置信度
  manually_adjusted: boolean // 是否手动调整过
}

// ==================== 截图相关 ====================

export interface Screenshot {
  filename: string // 文件名
  index: number // 排序索引
  classification?: Classification // 分类信息
  description?: string // 截图描述
  url?: string // 原图 URL
  thumb_url?: string // 缩略图 URL
}

export interface ScreenshotListResponse {
  project: string // 项目名称
  screenshots: Screenshot[] // 截图列表
  total: number // 截图总数
  stages?: Record<string, number> // Stage 统计
  modules?: Record<string, number> // Module 统计
}

// ==================== 项目相关 ====================

export interface Project {
  name: string // 项目名称（目录名）
  display_name: string // 显示名称
  screen_count: number // 截图数量
  source: 'projects' | 'downloads_2024' // 来源
  data_source?: 'SD' | 'Mobbin' // 数据来源（SD 或 Mobbin）
  color: string // 项目颜色
  initial: string // 首字母
  category?: string // 分类
  description_cn?: string // 中文描述
  description_en?: string // 英文描述
  created?: string // 创建时间
  checked: boolean // 是否已检查
  checked_at?: string // 检查时间
  onboarding_start: number // Onboarding 开始位置
  onboarding_end: number // Onboarding 结束位置
}

export interface ProjectListResponse {
  projects: Project[] // 项目列表
  total: number // 项目总数
  stats?: {
    total_screens: number
    checked: number
    onboarding_marked: number
  }
}

// ==================== API 参数 ====================

export interface ProjectsQueryParams {
  source?: 'projects' | 'downloads_2024'
  search?: string
  checked?: boolean
}

export interface ScreenshotsQueryParams {
  stage?: string
  module?: string
}


