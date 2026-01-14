/**
 * PM Tool v2 - API 客户端
 */
import type {
  Project,
  ProjectListResponse,
  ProjectsQueryParams,
  ScreenshotListResponse,
  ScreenshotsQueryParams,
} from '@/types'

const API_BASE = '/api'

/**
 * 构建查询字符串
 */
function buildQueryString(params: object): string {
  const searchParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value))
    }
  }
  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

/**
 * 通用请求函数
 */
async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(error.detail || `API Error: ${response.status}`)
    }

    return response.json()
  } catch (err) {
    throw err
  }
}

// ==================== 项目 API ====================

/**
 * 获取项目列表
 */
export async function getProjects(params?: ProjectsQueryParams): Promise<ProjectListResponse> {
  const query = buildQueryString(params || {})
  return fetchApi<ProjectListResponse>(`/projects${query}`)
}

/**
 * 获取单个项目
 */
export async function getProject(name: string): Promise<Project> {
  return fetchApi<Project>(`/projects/${encodeURIComponent(name)}`)
}

// ==================== 截图 API ====================

/**
 * 获取项目截图列表
 */
export async function getScreenshots(
  projectName: string,
  params?: ScreenshotsQueryParams
): Promise<ScreenshotListResponse> {
  const query = buildQueryString(params || {})
  // 使用新的 API 路径避免与 /projects/{name} 路由冲突
  return fetchApi<ScreenshotListResponse>(
    `/project-screenshots/${encodeURIComponent(projectName)}${query}`
  )
}

/**
 * 缓存版本号 - 在应用排序后更新，用于强制刷新图片
 */
let imageCacheVersion = Date.now()

/**
 * 获取截图 URL（大图）
 */
export function getScreenshotUrl(projectName: string, filename: string): string {
  return `${API_BASE}/screenshots/${encodeURIComponent(projectName)}/${encodeURIComponent(filename)}?v=${imageCacheVersion}`
}

/**
 * 更新图片缓存版本（强制刷新所有图片，包括大图和缩略图）
 */
export function invalidateThumbnailCache(): void {
  imageCacheVersion = Date.now()
}

/**
 * 获取缩略图 URL
 */
export function getThumbnailUrl(
  projectName: string,
  filename: string,
  size: 'small' | 'medium' | 'large' = 'small'
): string {
  return `${API_BASE}/thumbnails/${encodeURIComponent(projectName)}/${encodeURIComponent(filename)}?size=${size}&v=${imageCacheVersion}`
}

// ==================== Onboarding API ====================

export interface OnboardingRange {
  start: number
  end: number
  updated_at?: string
}

export interface CheckStatus {
  checked: boolean
  checked_at?: string
  screen_count: number
}

/**
 * 获取项目 Onboarding 范围
 */
export async function getOnboardingRange(projectName: string): Promise<OnboardingRange> {
  return fetchApi<OnboardingRange>(`/onboarding-range/${encodeURIComponent(projectName)}`)
}

/**
 * 保存项目 Onboarding 范围
 */
export async function saveOnboardingRange(
  projectName: string,
  start: number,
  end: number
): Promise<{ success: boolean; data: OnboardingRange }> {
  return fetchApi(`/onboarding-range/${encodeURIComponent(projectName)}`, {
    method: 'POST',
    body: JSON.stringify({ start, end }),
  })
}

/**
 * 获取项目检查状态
 */
export async function getCheckStatus(projectName: string): Promise<CheckStatus> {
  return fetchApi<CheckStatus>(`/check-status/${encodeURIComponent(projectName)}`)
}

/**
 * 设置项目检查状态
 */
export async function setCheckStatus(
  projectName: string,
  checked: boolean
): Promise<{ success: boolean; data: CheckStatus }> {
  return fetchApi(`/check-status/${encodeURIComponent(projectName)}`, {
    method: 'POST',
    body: JSON.stringify({ checked }),
  })
}

/**
 * 获取所有 Onboarding 数据
 */
export async function getAllOnboarding(): Promise<{
  total: number
  items: Array<OnboardingRange & { project: string; source: string }>
}> {
  return fetchApi('/all-onboarding')
}

// ==================== 排序 API ====================

export interface SortItem {
  original_file: string
  new_index: number
}

export interface DeletedBatch {
  timestamp: string
  deleted_at: string | null
  files: string[]
  count: number
}

/**
 * 保存排序（不重命名文件）
 */
export async function saveSortOrder(
  project: string,
  order: SortItem[]
): Promise<{ success: boolean; message: string }> {
  return fetchApi('/save-sort-order', {
    method: 'POST',
    body: JSON.stringify({ project, order }),
  })
}

/**
 * 获取已保存的排序
 */
export async function getSortOrder(projectName: string): Promise<{
  project: string
  order: SortItem[]
  saved_at?: string
}> {
  return fetchApi(`/sort-order/${encodeURIComponent(projectName)}`)
}

/**
 * 应用排序（重命名文件）
 */
export async function applySortOrder(
  project: string,
  order: SortItem[]
): Promise<{ success: boolean; message: string }> {
  return fetchApi('/apply-sort-order', {
    method: 'POST',
    body: JSON.stringify({ project, order }),
  })
}

/**
 * 删除截图
 */
export async function deleteScreens(
  project: string,
  files: string[]
): Promise<{ success: boolean; deleted_count: number; batch: string }> {
  return fetchApi('/delete-screens', {
    method: 'POST',
    body: JSON.stringify({ project, files }),
  })
}

/**
 * 获取已删除的截图
 */
export async function getDeletedScreens(projectName: string): Promise<{
  total: number
  batches: DeletedBatch[]
}> {
  return fetchApi(`/deleted-screens/${encodeURIComponent(projectName)}`)
}

/**
 * 恢复已删除的截图
 */
export async function restoreScreens(
  project: string,
  batch: string
): Promise<{ success: boolean; restored_count: number }> {
  return fetchApi('/restore-screens', {
    method: 'POST',
    body: JSON.stringify({ project, batch }),
  })
}

// ==================== 分类 API ====================

export interface Taxonomy {
  stages: string[]
  modules: string[]
}

export interface ClassificationUpdate {
  stage?: string
  module?: string
  feature?: string
  page_role?: string
}

/**
 * 获取分类法
 */
export async function getTaxonomy(): Promise<{
  success: boolean
  taxonomy: Taxonomy
  synonyms: Record<string, string>
}> {
  return fetchApi('/taxonomy')
}

/**
 * 获取项目分类
 */
export async function getClassification(projectName: string): Promise<{
  project: string
  classifications: Record<string, ClassificationUpdate>
}> {
  return fetchApi(`/classification/${encodeURIComponent(projectName)}`)
}

/**
 * 更新分类
 */
export async function updateClassification(
  project: string,
  changes: Record<string, ClassificationUpdate>
): Promise<{ success: boolean; count: number }> {
  return fetchApi('/update-classification', {
    method: 'POST',
    body: JSON.stringify({ project, changes }),
  })
}

/**
 * 批量分类
 */
export async function batchClassify(
  project: string,
  files: string[],
  classification: ClassificationUpdate
): Promise<{ success: boolean; count: number }> {
  return fetchApi('/batch-classify', {
    method: 'POST',
    body: JSON.stringify({ project, files, classification }),
  })
}

// ==================== 商店对比 API ====================

export interface StoreApp {
  name: string
  folder_name: string
  track_name?: string
  description?: string
  price?: number
  rating?: number
  rating_count?: number
  revenue?: number
  downloads?: number
  arpu?: number
  growth_rate?: number
  dau?: number
  priority?: string
  icon_url?: string
  store_screenshots?: string[]
}

/**
 * 获取商店对比数据
 */
export async function getStoreComparison(): Promise<{
  apps: StoreApp[]
  total: number
}> {
  return fetchApi('/store-comparison')
}

/**
 * 获取单个应用商店信息
 */
export async function getStoreInfo(projectName: string): Promise<StoreApp> {
  return fetchApi(`/store-info/${encodeURIComponent(projectName)}`)
}

/**
 * 获取商店截图 URL
 */
export function getStoreScreenshotUrl(projectName: string, filename: string): string {
  return `${API_BASE}/store-screenshot/${encodeURIComponent(projectName)}/${encodeURIComponent(filename)}`
}

/**
 * 获取应用图标 URL
 */
export function getStoreIconUrl(projectName: string): string {
  return `${API_BASE}/store-icon/${encodeURIComponent(projectName)}`
}

/**
 * 商城截图分析数据类型
 */
export interface StoreScreenshotAnalysis {
  index: number
  filename: string
  position: string
  type: string
  type_cn: string
  elements: string[]
  copywriting?: {
    headline?: string
    subheadline?: string
  }
  psychology?: {
    cialdini?: string[]
    cognitive_biases?: string[]
  }
  design_scores?: {
    visual_hierarchy?: number
    brand_consistency?: number
    readability?: number
  }
  analysis?: string
}

export interface StoreAnalysisData {
  app_name: string
  total_screenshots: number
  analyzed_at: string
  model: string
  screenshots: StoreScreenshotAnalysis[]
  overall_analysis?: {
    sequence_pattern: string
    strengths: string[]
    weaknesses: string[]
    recommendations: string[]
  }
}

/**
 * 获取商城截图分析数据
 */
export async function getStoreAnalysis(projectName: string): Promise<{
  success: boolean
  data: StoreAnalysisData | null
  error?: string
}> {
  return fetchApi(`/store-analysis/${encodeURIComponent(projectName)}`)
}

/**
 * 批量分析数据类型（用于表格视图）
 */
export interface StoreAnalysisAllItem {
  app_name: string
  track_name?: string
  rating?: number
  has_analysis: boolean
  screenshots: StoreScreenshotAnalysis[]
  sequence_pattern: string | null
  total_screenshots: number
  strengths?: string[]
  weaknesses?: string[]
}

/**
 * 获取所有应用的商城截图分析数据（表格对比视图）
 */
export async function getAllStoreAnalysis(): Promise<{
  success: boolean
  data: StoreAnalysisAllItem[]
  total: number
}> {
  return fetchApi('/store-analysis-all')
}

// ==================== 导出和历史 API ====================

export interface HistoryItem {
  action: string
  description: string
  project?: string
  timestamp: string
}

/**
 * 获取操作历史
 */
export async function getHistory(limit: number = 50): Promise<{
  total: number
  items: HistoryItem[]
}> {
  return fetchApi(`/history?limit=${limit}`)
}

/**
 * 清空历史记录
 */
export async function clearHistory(): Promise<{ success: boolean }> {
  return fetchApi('/history/clear', { method: 'POST' })
}

/**
 * 获取导出 JSON URL
 */
export function getExportJsonUrl(projectName: string): string {
  return `${API_BASE}/export/${encodeURIComponent(projectName)}/json`
}

/**
 * 获取导出 ZIP URL
 */
export function getExportZipUrl(projectName: string): string {
  return `${API_BASE}/export/${encodeURIComponent(projectName)}/zip`
}

// ==================== 待处理截图 API ====================

export interface PendingScreenshot {
  filename: string
  path: string
  size: number
  created_at: string
  thumbnail_url: string
}

export interface PendingListResponse {
  screenshots: PendingScreenshot[]
  total: number
  source_path: string | null
}

export interface ApowersoftConfig {
  path: string
  auto_import: boolean
  updated_at?: string
  detected?: boolean
}

/**
 * 获取待处理截图列表
 */
export async function getPendingScreenshots(): Promise<PendingListResponse> {
  return fetchApi<PendingListResponse>('/pending-screenshots')
}

/**
 * 获取待处理截图缩略图 URL
 */
export function getPendingThumbnailUrl(filename: string): string {
  return `${API_BASE}/pending-thumbnail/${encodeURIComponent(filename)}`
}

/**
 * 导入截图到项目
 */
export async function importScreenshot(
  project: string,
  filename: string,
  position: number = -1
): Promise<{ success: boolean; message: string; new_filename?: string; position?: number }> {
  return fetchApi('/import-screenshot', {
    method: 'POST',
    body: JSON.stringify({ project, filename, position }),
  })
}

/**
 * 上传截图文件到项目
 */
export async function uploadScreenshot(
  project: string,
  file: File
): Promise<{ success: boolean; message: string; new_filename?: string; position?: number }> {
  const formData = new FormData()
  formData.append('project', project)
  formData.append('file', file)
  
  const response = await fetch(`${API_BASE}/upload-screenshot`, {
    method: 'POST',
    body: formData,
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(error.detail || 'Upload failed')
  }
  
  return response.json()
}

/**
 * 获取傲软配置
 */
export async function getApowersoftConfig(): Promise<ApowersoftConfig> {
  return fetchApi<ApowersoftConfig>('/apowersoft-config')
}

/**
 * 保存傲软配置
 */
export async function saveApowersoftConfig(
  path: string,
  auto_import: boolean = false
): Promise<{ success: boolean; message: string }> {
  return fetchApi('/apowersoft-config', {
    method: 'POST',
    body: JSON.stringify({ path, auto_import }),
  })
}

/**
 * 从傲软导入所有截图
 */
export async function importFromApowersoft(): Promise<{ success: boolean; imported: number }> {
  return fetchApi('/import-from-apowersoft', { method: 'POST' })
}

/**
 * 清除傲软目录中的所有截图
 */
export async function clearPendingScreenshots(): Promise<{ success: boolean; deleted: number; message: string }> {
  return fetchApi('/clear-pending-screenshots', { method: 'POST' })
}

// ==================== 商店设计决策 API (v2) ====================

/**
 * V2 截图分析数据类型（5层分析框架）
 */
export interface StoreAnalysisV2Screenshot {
  index: number
  filename: string
  position: string
  model_used: string
  L1_extraction: {
    text_extraction: {
      headline: string
      subheadline: string
      body_copy: string[]
      cta_button: string
      small_print: string[]
      data_numbers: string[]
      language: string
    }
    visual_extraction: {
      dominant_colors: string[]
      color_mood: string
      layout_type: string
      device_mockup: { present: boolean; type: string; position: string }
      human_presence: { present: boolean; type: string }
      food_images: { present: boolean; style: string }
      data_visualization: { present: boolean; types: string[] }
      brand_elements: string[]
      background_style: string
    }
  }
  L2_understanding: {
    page_type: { primary: string; primary_cn: string; secondary: string | null }
    message_strategy: {
      primary_message: string
      supporting_evidence: string
      emotional_appeal: string
      value_proposition: string
    }
    psychology_tactics: {
      cialdini_principles: string[]
      cognitive_biases: string[]
      persuasion_technique: string
    }
  }
  L3_design: {
    visual_hierarchy: {
      eye_flow: string
      focal_point: string
      information_density: string
      hierarchy_score: number
    }
    typography: {
      headline_style: string
      headline_size: string
      text_alignment: string
      text_contrast: string
    }
    color_strategy: {
      primary_color: string
      color_scheme: string
      contrast_level: string
      brand_color_dominance: string
    }
    layout_pattern: {
      template_type: string
      whitespace_usage: string
      element_count: number
      symmetry: string
    }
    design_scores: {
      visual_appeal: number
      clarity: number
      brand_consistency: number
      uniqueness: number
    }
  }
  L4_insights: {
    differentiation: {
      unique_elements: string[]
      category_conventions: string[]
      innovations: string[]
    }
    competitive_positioning: string
    target_audience_signals: string[]
  }
  L5_recommendations: {
    vitaflow_applicability: string
    reusable_elements: string[]
    avoid_elements: string[]
    adaptation_notes: string
  }
}

export interface StoreAnalysisV2Data {
  app_name: string
  folder_name?: string
  track_name?: string
  rating?: number
  total_screenshots: number
  analyzed_at: string
  model: string
  schema_version: string
  screenshots: StoreAnalysisV2Screenshot[]
  overall_analysis: {
    sequence_pattern: string
    sequence_cluster: string
    narrative_arc: string
    strengths: string[]
    weaknesses: string[]
    key_takeaways: string[]
  }
  statistics: {
    type_distribution: Record<string, number>
    element_frequency: Record<string, number>
    psychology_coverage: {
      cialdini: string[]
      cognitive_biases: string[]
    }
    design_score_averages: Record<string, number>
  }
}

/**
 * 获取单个应用的 v2 分析数据
 */
export async function getStoreAnalysisV2(projectName: string): Promise<{
  success: boolean
  data: StoreAnalysisV2Data | null
  version: string
  error?: string
}> {
  return fetchApi(`/store-analysis-v2/${encodeURIComponent(projectName)}`)
}

/**
 * 获取所有应用的 v2 分析数据
 */
export async function getAllStoreAnalysisV2(): Promise<{
  success: boolean
  data: StoreAnalysisV2Data[]
  total: number
}> {
  return fetchApi('/store-analysis-v2-all')
}

/**
 * 统计数据类型
 */
export interface StoreStatistics {
  generated_at: string
  sample_size: number
  total_screenshots: number
  type_distribution: Record<string, { count: number; percentage: string; positions: string[] }>
  position_type_matrix: Record<string, Record<string, { count: number; percentage: string }>>
  element_frequency: Record<string, { count: number; percentage: string }>
  psychology_coverage: {
    cialdini_principles: Record<string, { count: number; percentage: string }>
    cognitive_biases: Record<string, { count: number; percentage: string }>
  }
  element_cooccurrence: Record<string, { count: number; percentage: string }>
  sequence_clusters: Record<string, { count: number; percentage: string; apps: string[] }>
  word_frequency: { headlines: Record<string, number> }
  design_score_averages: Record<string, number>
  color_distribution: Record<string, { count: number; percentage: string }>
  app_summaries: Array<{
    app_name: string
    total_screenshots: number
    sequence_pattern: string
    sequence_cluster: string
    type_distribution: Record<string, number>
    avg_design_score: number
  }>
}

/**
 * 获取商店统计数据
 */
export async function getStoreStatistics(): Promise<{
  success: boolean
  data: StoreStatistics | null
  error?: string
}> {
  return fetchApi('/store-statistics')
}

/**
 * 设计模式库类型
 */
export interface DesignPatterns {
  generated_at: string
  headline_patterns: Array<{
    text: string
    app: string
    position: string
    type: string
  }>
  layout_patterns: Record<string, { count: number; percentage: string }>
  color_schemes: Array<{
    app: string
    colors: string[]
    mood: string
  }>
}

/**
 * 获取设计模式库
 */
export async function getDesignPatterns(): Promise<{
  success: boolean
  data: DesignPatterns | null
  error?: string
}> {
  return fetchApi('/store-design-patterns')
}

/**
 * VitaFlow 推荐类型
 */
export interface VitaFlowRecommendations {
  generated_at: string
  recommended_sequence: {
    cluster: string
    positions: Record<string, {
      recommended_type: string
      confidence: number
      alternatives: string[]
    }>
  }
  must_have_elements: string[]
  recommended_psychology: string[]
  design_guidelines: Record<string, string>
}

/**
 * 获取 VitaFlow 推荐
 */
export async function getVitaFlowRecommendations(): Promise<{
  success: boolean
  data: VitaFlowRecommendations | null
  error?: string
}> {
  return fetchApi('/store-vitaflow-recommendations')
}

/**
 * 获取指定位置的截图对比数据
 */
export async function getPositionComparison(position: string): Promise<{
  success: boolean
  data: Array<{
    app_name: string
    filename: string
    analysis: StoreAnalysisV2Screenshot
  }>
  position: string
  total: number
}> {
  return fetchApi(`/store-position-comparison/${encodeURIComponent(position)}`)
}
