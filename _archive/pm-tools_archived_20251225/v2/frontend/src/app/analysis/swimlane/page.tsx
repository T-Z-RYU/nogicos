'use client';

import { useEffect, useCallback, useMemo, useRef } from 'react';
import { ChevronLeft, BarChart3, Layers, Eye } from 'lucide-react';
import Link from 'next/link';

import { AppLayout } from '@/components/layout';
import { Button } from '@/components/ui/button';
import { SwimlaneFlow, ScreenDetail, TypeFilter } from '@/components/analysis';
import {
  useSwimlaneStore,
  selectFilteredScreens,
  selectScreenTypes,
} from '@/store/swimlane-store';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * 泳道图分析页面
 */
export default function SwimlaneAnalysisPage() {
  // 防止 React Strict Mode 双重执行
  const fetchedRef = useRef(false);

  // 使用单一store访问模式避免多次订阅冲突
  const store = useSwimlaneStore();
  const {
    analysis,
    selectedScreen,
    isLoading,
    error,
    activeTypeFilters,
    showDetailPanel,
    fetchAnalysis,
    setSelectedScreen,
    toggleTypeFilter,
    clearTypeFilters,
    setShowDetailPanel,
  } = store;

  // 派生状态 - 使用直接调用而非额外订阅
  const filteredScreens = selectFilteredScreens(store);
  const screenTypes = selectScreenTypes(store);

  // 类型颜色映射
  const typeColors = useMemo(() => {
    const colors: Record<string, string> = {};
    if (analysis?.summary?.by_type) {
      Object.entries(analysis.summary.by_type).forEach(([code, data]) => {
        colors[code] = data.color;
      });
    }
    return colors;
  }, [analysis]);

  // 获取截图图片URL
  const getImageUrl = useCallback(
    (filename: string) => {
      // 正确的 API 路径格式: /api/screenshots/{project}/{filename}
      return `${API_BASE}/api/screenshots/downloads_2024/Flo/${filename}`;
    },
    []
  );

  // 加载分析数据 - 使用 store 内置的 fetchAnalysis
  useEffect(() => {
    // 防止重复请求 (React Strict Mode)
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    fetchAnalysis('flo');
  }, [fetchAnalysis]);

  // 处理截图选择
  const handleScreenSelect = useCallback(
    (screen: typeof selectedScreen) => {
      if (selectedScreen?.index === screen?.index) {
        setSelectedScreen(null);
      } else {
        setSelectedScreen(screen);
      }
    },
    [selectedScreen, setSelectedScreen]
  );

  // 关闭详情面板
  const handleCloseDetail = useCallback(() => {
    setSelectedScreen(null);
    setShowDetailPanel(false);
  }, [setSelectedScreen, setShowDetailPanel]);

  // 错误状态优先
  if (error) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[80vh]">
          <div className="text-center">
            <p className="text-red-500 mb-4">加载失败: {error}</p>
            <Button onClick={() => window.location.reload()}>重试</Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  // 如果有数据，直接显示（忽略 isLoading 状态）
  // 如果没有数据且正在加载，显示加载中
  if (!analysis) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[80vh]">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-4 border-pink-500 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-gray-500">加载分析数据中...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="h-screen flex flex-col">
        {/* 头部 - 使用深色背景以匹配全局主题 */}
        <header className="flex-shrink-0 border-b border-[var(--border-default)] bg-[var(--bg-secondary)] px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="sm" className="text-[var(--text-secondary)] hover:text-white">
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  返回
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-bold flex items-center gap-2 text-white">
                  <Layers className="w-5 h-5 text-pink-500" />
                  {analysis.app} 泳道图分析
                </h1>
                <p className="text-sm text-[var(--text-muted)]">
                  共 {analysis.total_screens} 个页面 · {filteredScreens.length} 个显示
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* 统计摘要 */}
              <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-1.5">
                  <BarChart3 className="w-4 h-4 text-[var(--text-muted)]" />
                  <span className="text-[var(--text-secondary)]">
                    {Object.keys(analysis.summary.by_type).length} 种页面类型
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Eye className="w-4 h-4 text-[var(--text-muted)]" />
                  <span className="text-[var(--text-secondary)]">
                    {analysis.summary.key_patterns.length} 个关键模式
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 类型筛选器 */}
          <TypeFilter
            types={screenTypes}
            activeFilters={activeTypeFilters}
            onToggle={toggleTypeFilter}
            onClear={clearTypeFilters}
          />
        </header>

        {/* 主体内容 */}
        <main className="flex-1 flex overflow-hidden">
          {/* 泳道图区域 */}
          <div
            className={`flex-1 transition-all duration-300 ${
              showDetailPanel ? 'mr-0' : ''
            }`}
          >
            <SwimlaneFlow
              analysis={analysis}
              filteredScreens={filteredScreens}
              selectedScreen={selectedScreen}
              onScreenSelect={handleScreenSelect}
              getImageUrl={getImageUrl}
            />
          </div>

          {/* 详情面板 */}
          {showDetailPanel && selectedScreen && (
            <div className="w-[380px] flex-shrink-0 border-l border-gray-200 overflow-hidden">
              <ScreenDetail
                screen={selectedScreen}
                imageUrl={getImageUrl(selectedScreen.filename)}
                typeColors={typeColors}
                onClose={handleCloseDetail}
              />
            </div>
          )}
        </main>
      </div>
    </AppLayout>
  );
}


