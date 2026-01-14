/**
 * Swimlane Store - 泳道图状态管理
 */
import { create } from 'zustand';

// 页面类型定义
export interface ScreenType {
  code: string;
  label: string;
  color: string;
  count: number;
}

// 截图数据定义
export interface ScreenData {
  index: number;
  filename: string;
  primary_type: string;
  secondary_type: string | null;
  psychology: string[];
  ui_pattern: string;
  copy: {
    headline: string;
    subheadline: string | null;
    cta: string | null;
  };
  insight: string;
}

// 分析摘要
export interface AnalysisSummary {
  total_pages: number;
  by_type: Record<string, ScreenType>;
  funnel_stages: Record<string, { screens: number[]; percentage: number }>;
  key_patterns: string[];
}

// 完整分析数据
export interface SwimlaneAnalysis {
  app: string;
  total_screens: number;
  analyzed_at: string;
  taxonomy_version: string;
  summary: AnalysisSummary;
  screens: ScreenData[];
  flow_patterns: Record<string, number[]>;
  design_insights: Record<string, string>;
}

interface SwimlaneState {
  // 数据
  analysis: SwimlaneAnalysis | null;
  selectedScreen: ScreenData | null;
  
  // UI 状态
  isLoading: boolean;
  error: string | null;
  activeTypeFilters: string[];
  zoomLevel: number;
  showDetailPanel: boolean;
  
  // Actions
  fetchAnalysis: (appId: string) => Promise<void>;
  setAnalysis: (analysis: SwimlaneAnalysis) => void;
  setSelectedScreen: (screen: ScreenData | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  toggleTypeFilter: (type: string) => void;
  clearTypeFilters: () => void;
  setZoomLevel: (level: number) => void;
  setShowDetailPanel: (show: boolean) => void;
  reset: () => void;
}

const initialState = {
  analysis: null,
  selectedScreen: null,
  isLoading: true,  // 默认为 true，避免 SSR 闪烁
  error: null,
  activeTypeFilters: [],
  zoomLevel: 1,
  showDetailPanel: false,
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useSwimlaneStore = create<SwimlaneState>((set, get) => ({
  ...initialState,
  
  // 异步获取分析数据 - 遵循 Zustand 最佳实践
  fetchAnalysis: async (appId: string) => {
    set({ isLoading: true, error: null });
    
    try {
      const url = `${API_BASE}/api/analysis/swimlane/${appId}`;
      const res = await fetch(url);
      
      if (!res.ok) {
        throw new Error(`Failed to load analysis: ${res.status}`);
      }
      
      const data: SwimlaneAnalysis = await res.json();
      set({ analysis: data, isLoading: false, error: null });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      set({ error: errorMsg, isLoading: false });
    }
  },
  
  setAnalysis: (analysis) => set({ analysis, error: null, isLoading: false }),
  
  setSelectedScreen: (screen) => set({ 
    selectedScreen: screen,
    showDetailPanel: screen !== null 
  }),
  
  setLoading: (isLoading) => set({ isLoading }),
  
  setError: (error) => set({ error, isLoading: false }),
  
  toggleTypeFilter: (type) => set((state) => ({
    activeTypeFilters: state.activeTypeFilters.includes(type)
      ? state.activeTypeFilters.filter(t => t !== type)
      : [...state.activeTypeFilters, type]
  })),
  
  clearTypeFilters: () => set({ activeTypeFilters: [] }),
  
  setZoomLevel: (zoomLevel) => set({ zoomLevel }),
  
  setShowDetailPanel: (showDetailPanel) => set({ showDetailPanel }),
  
  reset: () => set(initialState),
}));

// 空数组常量，避免每次返回新引用导致无限重渲染
const EMPTY_SCREENS: ScreenData[] = [];
const EMPTY_TYPES: Array<{ code: string } & ScreenType> = [];

// 选择器
export const selectFilteredScreens = (state: SwimlaneState) => {
  if (!state.analysis) return EMPTY_SCREENS;
  if (state.activeTypeFilters.length === 0) return state.analysis.screens;
  
  return state.analysis.screens.filter(screen =>
    state.activeTypeFilters.includes(screen.primary_type)
  );
};

export const selectScreenTypes = (state: SwimlaneState) => {
  if (!state.analysis) return EMPTY_TYPES;
  
  const byType = state.analysis.summary.by_type;
  return Object.entries(byType).map(([code, data]) => ({
    code,
    ...data
  }));
};


