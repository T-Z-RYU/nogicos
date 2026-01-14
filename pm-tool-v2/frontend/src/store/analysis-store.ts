/**
 * Analysis Store - 多产品分析状态管理
 * 支持阶段划分、序列模式、跨产品对比
 */
import { create } from 'zustand';

// 页面类型定义
export interface ScreenType {
  code: string;
  label: string;
  color: string;
  count: number;
}

// 文案数据
export interface ScreenCopy {
  headline: string | null;
  subheadline: string | null;
  cta: string | null;
}

// 截图数据定义
export interface ScreenData {
  index: number;
  filename: string;
  primary_type: string;
  secondary_type: string | null;
  phase: string;
  psychology: string[];
  ui_pattern: string;
  copy: ScreenCopy;
  insight: string;
}

// 阶段定义
export interface Phase {
  id: string;
  name: string;
  nameEn: string;
  purpose: string;
  startIndex: number;
  endIndex: number;
  dominantTypes: string[];
  psychologyTactics: string[];
  keyInsights: string[];
}

// 序列模式
export interface SequencePattern {
  pattern: string;
  name: string;
  occurrences: number;
  positions: number[];
  interpretation: string;
}

// 阶段分布
export interface PhaseDistribution {
  count: number;
  percentage: number;
}

// 分析摘要
export interface AnalysisSummary {
  total_pages: number;
  phase_distribution: Record<string, PhaseDistribution>;
  by_type: Record<string, ScreenType>;
  key_patterns: string[];
}

// 完整分析数据（包含阶段）
export interface PhaseAnalysis {
  app: string;
  appId: string;
  total_screens: number;
  analyzed_at: string;
  taxonomy_version: string;
  phases: Phase[];
  patterns: SequencePattern[];
  summary: AnalysisSummary;
  screens: ScreenData[];
  flow_patterns: Record<string, number[] | number[][]>;
  design_insights: Record<string, string>;
}

// 多产品对比数据
export interface CrossAppComparison {
  apps: string[];
  phaseMatrix: PhaseMatrixRow[];
  commonPatterns: CommonPattern[];
  uniqueStrategies: UniqueStrategy[];
}

export interface PhaseMatrixRow {
  phaseName: string;
  appData: Record<string, { count: number; percentage: number }>;
  average: number;
  recommendation: string;
}

export interface CommonPattern {
  pattern: string;
  frequency: string;
  importance: 'must-have' | 'recommended' | 'optional';
  evidence: string[];
}

export interface UniqueStrategy {
  app: string;
  strategy: string;
  description: string;
}

// Store 状态
interface AnalysisState {
  // 单产品分析
  currentAnalysis: PhaseAnalysis | null;
  selectedScreen: ScreenData | null;
  expandedPhases: string[];
  
  // 多产品对比
  comparisonApps: string[];
  analysisCache: Record<string, PhaseAnalysis>;
  comparison: CrossAppComparison | null;
  
  // UI 状态
  isLoading: boolean;
  error: string | null;
  activeTypeFilters: string[];
  showDetailPanel: boolean;
  
  // Actions
  fetchAnalysis: (appId: string) => Promise<PhaseAnalysis | null>;
  setSelectedScreen: (screen: ScreenData | null) => void;
  togglePhaseExpand: (phaseId: string) => void;
  expandAllPhases: () => void;
  collapseAllPhases: () => void;
  toggleTypeFilter: (type: string) => void;
  clearTypeFilters: () => void;
  setShowDetailPanel: (show: boolean) => void;
  addComparisonApp: (appId: string) => void;
  removeComparisonApp: (appId: string) => void;
  loadComparison: () => Promise<void>;
  reset: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const initialState = {
  currentAnalysis: null,
  selectedScreen: null,
  expandedPhases: [] as string[],
  comparisonApps: [] as string[],
  analysisCache: {} as Record<string, PhaseAnalysis>,
  comparison: null,
  isLoading: false,
  error: null,
  activeTypeFilters: [] as string[],
  showDetailPanel: false,
};

export const useAnalysisStore = create<AnalysisState>((set, get) => ({
  ...initialState,

  fetchAnalysis: async (appId: string) => {
    // 检查缓存
    const cached = get().analysisCache[appId];
    if (cached) {
      set({ 
        currentAnalysis: cached, 
        isLoading: false, 
        error: null,
        // 默认展开所有阶段
        expandedPhases: cached.phases.map(p => p.id)
      });
      return cached;
    }

    set({ isLoading: true, error: null });

    try {
      const url = `${API_BASE}/api/analysis/swimlane/${appId}`;
      const res = await fetch(url);

      if (!res.ok) {
        throw new Error(`Failed to load analysis: ${res.status}`);
      }

      const data: PhaseAnalysis = await res.json();
      
      set((state) => ({
        currentAnalysis: data,
        analysisCache: { ...state.analysisCache, [appId]: data },
        isLoading: false,
        error: null,
        // 默认展开所有阶段
        expandedPhases: data.phases?.map(p => p.id) || []
      }));

      return data;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      set({ error: errorMsg, isLoading: false });
      return null;
    }
  },

  setSelectedScreen: (screen) => set({
    selectedScreen: screen,
    showDetailPanel: screen !== null
  }),

  togglePhaseExpand: (phaseId) => set((state) => ({
    expandedPhases: state.expandedPhases.includes(phaseId)
      ? state.expandedPhases.filter(id => id !== phaseId)
      : [...state.expandedPhases, phaseId]
  })),

  expandAllPhases: () => set((state) => ({
    expandedPhases: state.currentAnalysis?.phases.map(p => p.id) || []
  })),

  collapseAllPhases: () => set({ expandedPhases: [] }),

  toggleTypeFilter: (type) => set((state) => ({
    activeTypeFilters: state.activeTypeFilters.includes(type)
      ? state.activeTypeFilters.filter(t => t !== type)
      : [...state.activeTypeFilters, type]
  })),

  clearTypeFilters: () => set({ activeTypeFilters: [] }),

  setShowDetailPanel: (show) => set({ showDetailPanel: show }),

  addComparisonApp: (appId) => set((state) => ({
    comparisonApps: state.comparisonApps.includes(appId)
      ? state.comparisonApps
      : [...state.comparisonApps, appId]
  })),

  removeComparisonApp: (appId) => set((state) => ({
    comparisonApps: state.comparisonApps.filter(id => id !== appId)
  })),

  loadComparison: async () => {
    const { comparisonApps, fetchAnalysis, analysisCache } = get();
    
    if (comparisonApps.length < 2) {
      set({ error: 'Need at least 2 apps to compare' });
      return;
    }

    set({ isLoading: true, error: null });

    try {
      // 加载所有需要对比的 app 数据
      const analyses: PhaseAnalysis[] = [];
      for (const appId of comparisonApps) {
        let analysis = analysisCache[appId];
        if (!analysis) {
          analysis = await fetchAnalysis(appId) as PhaseAnalysis;
        }
        if (analysis) {
          analyses.push(analysis);
        }
      }

      // 生成对比数据
      const comparison = generateComparison(analyses);
      set({ comparison, isLoading: false });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      set({ error: errorMsg, isLoading: false });
    }
  },

  reset: () => set(initialState),
}));

// 生成跨产品对比数据
function generateComparison(analyses: PhaseAnalysis[]): CrossAppComparison {
  const apps = analyses.map(a => a.app);
  
  // 生成阶段矩阵
  const phaseNames = ['信任建立', '数据收集A', '数据收集B', '数据收集C', '最终设置', '转化'];
  const phaseMatrix: PhaseMatrixRow[] = phaseNames.map(phaseName => {
    const appData: Record<string, { count: number; percentage: number }> = {};
    let total = 0;
    let appCount = 0;

    analyses.forEach(analysis => {
      const phase = analysis.phases.find(p => 
        p.name.includes(phaseName.replace(/[ABC]/, '')) || 
        p.nameEn.toLowerCase().includes(phaseName.toLowerCase().replace(/[abc]/i, ''))
      );
      if (phase) {
        const count = phase.endIndex - phase.startIndex + 1;
        const percentage = Math.round((count / analysis.total_screens) * 100);
        appData[analysis.app] = { count, percentage };
        total += count;
        appCount++;
      }
    });

    const average = appCount > 0 ? Math.round(total / appCount) : 0;
    const recommendation = `${Math.max(1, average - 2)}-${average + 2}页`;

    return { phaseName, appData, average, recommendation };
  });

  // 生成通用模式
  const commonPatterns: CommonPattern[] = [
    {
      pattern: '前5页内出现权威背书',
      frequency: `${analyses.length}/${analyses.length} apps`,
      importance: 'must-have',
      evidence: analyses.map(a => `${a.app}: 页面 ${a.flow_patterns?.authority_placement?.[0] || 'N/A'}`)
    },
    {
      pattern: '每4-6个问题穿插价值页',
      frequency: `${analyses.length}/${analyses.length} apps`,
      importance: 'must-have',
      evidence: analyses.map(a => `${a.app}: ${Object.keys(a.flow_patterns?.value_after_questions || {}).length || 0}次`)
    },
    {
      pattern: '付费墙前展示个性化结果',
      frequency: `${analyses.length}/${analyses.length} apps`,
      importance: 'must-have',
      evidence: analyses.map(a => `${a.app}: 有Loading+Result序列`)
    }
  ];

  // 生成差异化策略
  const uniqueStrategies: UniqueStrategy[] = analyses.map(a => ({
    app: a.app,
    strategy: Object.keys(a.design_insights)[0] || '',
    description: Object.values(a.design_insights)[0] || ''
  }));

  return { apps, phaseMatrix, commonPatterns, uniqueStrategies };
}

// 选择器：获取阶段内的截图
export const selectScreensInPhase = (state: AnalysisState, phaseId: string): ScreenData[] => {
  if (!state.currentAnalysis) return [];
  
  const phase = state.currentAnalysis.phases.find(p => p.id === phaseId);
  if (!phase) return [];

  return state.currentAnalysis.screens.filter(
    s => s.index >= phase.startIndex && s.index <= phase.endIndex
  );
};

// 选择器：获取过滤后的截图
export const selectFilteredScreens = (state: AnalysisState): ScreenData[] => {
  if (!state.currentAnalysis) return [];
  if (state.activeTypeFilters.length === 0) return state.currentAnalysis.screens;
  
  return state.currentAnalysis.screens.filter(screen =>
    state.activeTypeFilters.includes(screen.primary_type)
  );
};

// 选择器：获取页面类型统计
export const selectScreenTypes = (state: AnalysisState): Array<{ code: string } & ScreenType> => {
  if (!state.currentAnalysis) return [];
  
  const byType = state.currentAnalysis.summary.by_type;
  return Object.entries(byType).map(([code, data]) => ({
    code,
    ...data
  }));
};

