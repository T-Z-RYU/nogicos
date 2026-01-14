'use client';

import { useEffect, useRef, useCallback, useMemo } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { 
  ChevronLeft, 
  BarChart3, 
  Layers, 
  ChevronDown, 
  ChevronUp,
  Sparkles,
  TrendingUp
} from 'lucide-react';

import { AppLayout } from '@/components/layout';
import { Button } from '@/components/ui/button';
import { PhaseAccordion, ScreenDetail, TypeFilter } from '@/components/analysis';
import { 
  useAnalysisStore, 
  selectScreensInPhase,
  selectScreenTypes
} from '@/store/analysis-store';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 类型颜色映射
const TYPE_COLORS: Record<string, string> = {
  W: '#E5E5E5',
  Q: '#3B82F6',
  V: '#22C516',
  S: '#EAB308',
  A: '#6366F1',
  R: '#A855F7',
  D: '#F97316',
  C: '#D97706',
  G: '#14B8A6',
  L: '#1F2937',
  X: '#6B7280',
  P: '#EF4444',
};

const TYPE_LABELS: Record<string, string> = {
  W: 'Welcome',
  Q: 'Question',
  V: 'Value',
  S: 'Social',
  A: 'Authority',
  R: 'Result',
  D: 'Demo',
  C: 'Commit',
  G: 'Gamified',
  L: 'Loading',
  X: 'Permission',
  P: 'Paywall',
};

/**
 * 单产品阶段分析页面
 */
export default function PhaseAnalysisPage() {
  const params = useParams();
  const appId = params.appId as string;
  const fetchedRef = useRef(false);

  const {
    currentAnalysis,
    selectedScreen,
    expandedPhases,
    isLoading,
    error,
    activeTypeFilters,
    showDetailPanel,
    fetchAnalysis,
    setSelectedScreen,
    togglePhaseExpand,
    expandAllPhases,
    collapseAllPhases,
    toggleTypeFilter,
    clearTypeFilters,
    setShowDetailPanel,
  } = useAnalysisStore();

  // 获取截图图片URL
  const getImageUrl = useCallback(
    (filename: string) => {
      // 根据 appId 确定项目路径
      const projectPath = `downloads_2024/${appId.charAt(0).toUpperCase() + appId.slice(1)}`;
      return `${API_BASE}/api/screenshots/${projectPath}/${filename}`;
    },
    [appId]
  );

  // 加载分析数据
  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    fetchAnalysis(appId);
  }, [appId, fetchAnalysis]);

  // 关闭详情面板
  const handleCloseDetail = useCallback(() => {
    setSelectedScreen(null);
    setShowDetailPanel(false);
  }, [setSelectedScreen, setShowDetailPanel]);

  // 获取页面类型
  const screenTypes = useMemo(() => {
    if (!currentAnalysis) return [];
    return selectScreenTypes(useAnalysisStore.getState());
  }, [currentAnalysis]);

  // 错误状态
  if (error) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[80vh]">
          <div className="text-center">
            <p className="text-red-500 mb-4">加载失败: {error}</p>
            <Button onClick={() => { fetchedRef.current = false; fetchAnalysis(appId); }}>
              重试
            </Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  // 加载状态
  if (!currentAnalysis) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[80vh]">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-4 border-pink-500 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-[var(--text-muted)]">加载分析数据中...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  const allExpanded = expandedPhases.length === currentAnalysis.phases.length;

  return (
    <AppLayout>
      <div className="h-screen flex flex-col">
        {/* 头部 */}
        <header className="flex-shrink-0 border-b border-[var(--border-default)] bg-[var(--bg-secondary)] px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Link href="/analysis/swimlane">
                <Button variant="ghost" size="sm" className="text-[var(--text-secondary)] hover:text-white">
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  返回
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-bold flex items-center gap-2 text-white">
                  <Layers className="w-5 h-5 text-pink-500" />
                  {currentAnalysis.app} 阶段分析
                </h1>
                <p className="text-sm text-[var(--text-muted)]">
                  共 {currentAnalysis.total_screens} 个页面 · {currentAnalysis.phases.length} 个阶段
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* 统计摘要 */}
              <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-1.5">
                  <BarChart3 className="w-4 h-4 text-[var(--text-muted)]" />
                  <span className="text-[var(--text-secondary)]">
                    {Object.keys(currentAnalysis.summary.by_type).length} 种页面类型
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-[var(--text-muted)]" />
                  <span className="text-[var(--text-secondary)]">
                    {currentAnalysis.patterns.length} 个序列模式
                  </span>
                </div>
              </div>

              {/* 展开/收起全部 */}
              <Button
                variant="outline"
                size="sm"
                onClick={allExpanded ? collapseAllPhases : expandAllPhases}
                className="text-[var(--text-secondary)]"
              >
                {allExpanded ? (
                  <>
                    <ChevronUp className="w-4 h-4 mr-1" />
                    收起全部
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4 mr-1" />
                    展开全部
                  </>
                )}
              </Button>

              {/* 对比模式按钮 */}
              <Link href="/analysis/compare">
                <Button variant="default" size="sm" className="bg-pink-500 hover:bg-pink-600">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  对比模式
                </Button>
              </Link>
            </div>
          </div>

          {/* 类型过滤器 */}
          <TypeFilter
            types={screenTypes}
            activeFilters={activeTypeFilters}
            onToggle={toggleTypeFilter}
            onClear={clearTypeFilters}
          />
        </header>

        {/* 主内容区 */}
        <div className="flex-1 overflow-hidden flex">
          {/* 阶段列表 */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {/* 概览卡片 */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4">
                <p className="text-sm text-[var(--text-muted)] mb-1">总页面</p>
                <p className="text-2xl font-bold text-white">{currentAnalysis.total_screens}</p>
              </div>
              <div className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4">
                <p className="text-sm text-[var(--text-muted)] mb-1">阶段数</p>
                <p className="text-2xl font-bold text-white">{currentAnalysis.phases.length}</p>
              </div>
              <div className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4">
                <p className="text-sm text-[var(--text-muted)] mb-1">页面类型</p>
                <p className="text-2xl font-bold text-white">{Object.keys(currentAnalysis.summary.by_type).length}</p>
              </div>
              <div className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4">
                <p className="text-sm text-[var(--text-muted)] mb-1">主要模式</p>
                <p className="text-lg font-bold text-white truncate">
                  {currentAnalysis.patterns[0]?.pattern || 'N/A'}
                </p>
              </div>
            </div>

            {/* 阶段折叠列表 */}
            {currentAnalysis.phases.map((phase) => {
              const screensInPhase = currentAnalysis.screens.filter(
                s => s.index >= phase.startIndex && s.index <= phase.endIndex
              );
              // 如果有类型过滤，进一步过滤
              const filteredScreens = activeTypeFilters.length > 0
                ? screensInPhase.filter(s => activeTypeFilters.includes(s.primary_type))
                : screensInPhase;

              return (
                <PhaseAccordion
                  key={phase.id}
                  phase={phase}
                  screens={filteredScreens}
                  isExpanded={expandedPhases.includes(phase.id)}
                  onToggle={() => togglePhaseExpand(phase.id)}
                  onScreenClick={setSelectedScreen}
                  selectedScreenIndex={selectedScreen?.index}
                  getImageUrl={getImageUrl}
                  typeColors={TYPE_COLORS}
                />
              );
            })}

            {/* 序列模式卡片 */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-yellow-400" />
                检测到的序列模式
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {currentAnalysis.patterns.map((pattern, index) => (
                  <div
                    key={index}
                    className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <code className="text-pink-400 font-mono text-sm bg-pink-500/10 px-2 py-1 rounded">
                        {pattern.pattern}
                      </code>
                      <span className="text-xs text-[var(--text-muted)]">×{pattern.occurrences}</span>
                    </div>
                    <p className="text-sm font-medium text-white mb-1">{pattern.name}</p>
                    <p className="text-xs text-[var(--text-muted)]">{pattern.interpretation}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* 设计洞察 */}
            <div className="mt-8 mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                设计洞察
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(currentAnalysis.design_insights).map(([key, value]) => (
                  <div
                    key={key}
                    className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4"
                  >
                    <p className="text-sm font-medium text-[var(--text-secondary)] mb-1 capitalize">
                      {key.replace(/_/g, ' ')}
                    </p>
                    <p className="text-sm text-white">{value}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 详情侧边栏 */}
          {showDetailPanel && selectedScreen && (
            <div className="w-[400px] border-l border-[var(--border-default)] bg-[var(--bg-secondary)] overflow-y-auto">
              <ScreenDetail
                screen={{
                  ...selectedScreen,
                  // 兼容旧数据结构
                  copy: {
                    headline: selectedScreen.copy.headline || '',
                    subheadline: selectedScreen.copy.subheadline,
                    cta: selectedScreen.copy.cta,
                  }
                }}
                imageUrl={getImageUrl(selectedScreen.filename)}
                typeColor={TYPE_COLORS[selectedScreen.primary_type] || '#6B7280'}
                typeLabel={TYPE_LABELS[selectedScreen.primary_type] || selectedScreen.primary_type}
                onClose={handleCloseDetail}
              />
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}

