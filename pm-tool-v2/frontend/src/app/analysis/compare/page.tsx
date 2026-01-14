'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { 
  ChevronLeft, 
  Check,
  BarChart3, 
  Table2,
  Sparkles,
  Target,
  Lightbulb,
  ArrowRight,
  Download
} from 'lucide-react';

import { AppLayout } from '@/components/layout';
import { Button } from '@/components/ui/button';
import { 
  MultiAppSwimlane, 
  PhaseMatrix
} from '@/components/analysis';
import { 
  useAnalysisStore, 
  type PhaseAnalysis 
} from '@/store/analysis-store';

// 可用的 App 列表 - 8 个竞品
const AVAILABLE_APPS = [
  { id: 'flo', name: 'Flo', category: '女性健康' },
  { id: 'yazio', name: 'Yazio', category: '营养追踪' },
  { id: 'cal_ai', name: 'Cal AI', category: 'AI卡路里' },
  { id: 'noom', name: 'Noom', category: '心理减重' },
  { id: 'myfitnesspal', name: 'MyFitnessPal', category: '卡路里追踪' },
  { id: 'loseit', name: 'LoseIt', category: '减肥追踪' },
  { id: 'macrofactor', name: 'MacroFactor', category: '宏量营养素' },
  { id: 'weightwatchers', name: 'WeightWatchers', category: '减肥计划' },
];

/**
 * 多产品对比分析页面
 */
// 类型分布数据类型
interface TypeDistribution {
  [key: string]: {
    label: string;
    color: string;
    count: number;
    percentage: number;
    apps: { appId: string; count: number }[];
  };
}

// 通用模式类型
interface CommonPattern {
  pattern: string;
  name: string;
  interpretation: string;
  apps: string[];
  total_occurrences: number;
}

// 比较 API 响应类型
interface CompareResponse {
  apps: PhaseAnalysis[];
  aggregate: {
    total_apps: number;
    total_screens: number;
    type_distribution: TypeDistribution;
    common_patterns: CommonPattern[];
  };
}

export default function CompareAnalysisPage() {
  const [selectedApps, setSelectedApps] = useState<string[]>(['flo', 'yazio', 'noom', 'myfitnesspal']);
  const [loadedAnalyses, setLoadedAnalyses] = useState<PhaseAnalysis[]>([]);
  const [compareData, setCompareData] = useState<CompareResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { fetchAnalysis, analysisCache } = useAnalysisStore();

  // 切换 App 选择
  const toggleApp = useCallback((appId: string) => {
    setSelectedApps(prev => {
      if (prev.includes(appId)) {
        return prev.filter(id => id !== appId);
      }
      return [...prev, appId];
    });
  }, []);

  // 加载比较数据
  useEffect(() => {
    const loadData = async () => {
      if (selectedApps.length === 0) {
        setLoadedAnalyses([]);
        setCompareData(null);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // 获取跨产品比较数据
        const compareRes = await fetch('http://localhost:8002/api/analysis/compare');
        if (!compareRes.ok) throw new Error('Failed to fetch compare data');
        const compare: CompareResponse = await compareRes.json();
        setCompareData(compare);

        // 只加载选中的 App 的详细数据
        const analyses: PhaseAnalysis[] = [];
        for (const appId of selectedApps) {
          // 从比较数据中获取
          const appData = compare.apps.find(a => a.appId === appId);
          if (appData) {
            analyses.push(appData);
          } else {
            // 否则单独获取
            let analysis = analysisCache[appId];
            if (!analysis) {
              analysis = await fetchAnalysis(appId) as PhaseAnalysis;
            }
            if (analysis) {
              analyses.push(analysis);
            }
          }
        }
        setLoadedAnalyses(analyses);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [selectedApps, fetchAnalysis, analysisCache]);

  // 从 API 获取通用模式
  const commonPatterns = compareData?.aggregate?.common_patterns || [];
  
  // 类型分布统计
  const typeDistribution = compareData?.aggregate?.type_distribution || {};
  
  // 生成差异化策略
  const uniqueStrategies = loadedAnalyses.map(a => ({
    app: a.app,
    appId: a.appId,
    strategy: a.patterns?.[0]?.name || '',
    description: a.patterns?.[0]?.interpretation || ''
  }));

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
                  <BarChart3 className="w-5 h-5 text-pink-500" />
                  多产品对比分析
                </h1>
                <p className="text-sm text-[var(--text-muted)]">
                  对比 {loadedAnalyses.length} 款 App 的 onboarding 结构
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Link href="/analysis/template">
                <Button variant="default" size="sm" className="bg-pink-500 hover:bg-pink-600">
                  <ArrowRight className="w-4 h-4 mr-1" />
                  生成 VitaFlow 模板
                </Button>
              </Link>
            </div>
          </div>

          {/* App 选择器 */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-[var(--text-muted)] mr-2">选择 App:</span>
            {AVAILABLE_APPS.map(app => (
              <button
                key={app.id}
                onClick={() => toggleApp(app.id)}
                className={`
                  px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                  ${selectedApps.includes(app.id)
                    ? 'bg-pink-500 text-white'
                    : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]/80'
                  }
                `}
              >
                {selectedApps.includes(app.id) && <Check className="w-3 h-3 inline mr-1" />}
                {app.name}
                <span className="text-xs opacity-70 ml-1">({app.category})</span>
              </button>
            ))}
          </div>
        </header>

        {/* 主内容区 */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin w-8 h-8 border-4 border-pink-500 border-t-transparent rounded-full mx-auto mb-4" />
                <p className="text-[var(--text-muted)]">加载分析数据中...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <p className="text-red-500 mb-4">{error}</p>
                <Button onClick={() => setSelectedApps([...selectedApps])}>重试</Button>
              </div>
            </div>
          ) : loadedAnalyses.length === 0 ? (
            <div className="flex items-center justify-center h-64">
              <p className="text-[var(--text-muted)]">请选择至少一个 App 进行分析</p>
            </div>
          ) : (
            <>
              {/* 并行泳道视图 */}
              <section className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-400" />
                  并行泳道视图
                </h2>
                <MultiAppSwimlane analyses={loadedAnalyses} />
              </section>

              {/* 阶段矩阵 */}
              <section className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Table2 className="w-5 h-5 text-purple-400" />
                  阶段矩阵对比
                </h2>
                <PhaseMatrix analyses={loadedAnalyses} />
              </section>

              {/* 类型分布统计 */}
              {Object.keys(typeDistribution).length > 0 && (
                <section className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-xl p-6">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-green-400" />
                    行业类型分布 ({compareData?.aggregate?.total_screens} 页)
                  </h2>
                  <div className="grid grid-cols-4 md:grid-cols-6 gap-3">
                    {Object.entries(typeDistribution)
                      .sort((a, b) => b[1].count - a[1].count)
                      .map(([code, info]) => (
                        <div 
                          key={code}
                          className="p-3 bg-[var(--bg-tertiary)] rounded-lg text-center"
                        >
                          <div 
                            className="w-8 h-8 rounded-lg mx-auto mb-2 flex items-center justify-center text-white font-bold"
                            style={{ backgroundColor: info.color }}
                          >
                            {code}
                          </div>
                          <p className="text-xs text-[var(--text-muted)]">{info.label}</p>
                          <p className="text-lg font-bold text-white">{info.percentage}%</p>
                          <p className="text-xs text-[var(--text-muted)]">{info.count} 页</p>
                        </div>
                      ))}
                  </div>
                </section>
              )}

              {/* 通用模式 */}
              {commonPatterns.length > 0 && (
                <section className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-xl p-6">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-yellow-400" />
                    检测到的序列模式
                  </h2>
                  <div className="space-y-3">
                    {commonPatterns.map((pattern, index) => (
                      <div 
                        key={index}
                        className={`
                          flex items-start gap-3 p-4 rounded-lg border
                          ${pattern.apps.length >= 4
                            ? 'bg-green-500/10 border-green-500/30' 
                            : pattern.apps.length >= 2
                            ? 'bg-blue-500/10 border-blue-500/30'
                            : 'bg-gray-500/10 border-gray-500/30'
                          }
                        `}
                      >
                        <div className={`
                          flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                          ${pattern.apps.length >= 4
                            ? 'bg-green-500 text-white' 
                            : pattern.apps.length >= 2
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-500 text-white'
                          }
                        `}>
                          {pattern.apps.length}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-mono font-medium text-white">{pattern.pattern}</span>
                            <span className="text-xs px-2 py-0.5 bg-[var(--bg-tertiary)] text-[var(--text-muted)] rounded">
                              {pattern.apps.length} Apps · {pattern.total_occurrences} 次
                            </span>
                          </div>
                          <p className="text-sm text-[var(--text-secondary)] mb-2">
                            {pattern.name}: {pattern.interpretation}
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {pattern.apps.map(appId => (
                              <span key={appId} className="text-xs px-2 py-0.5 bg-pink-500/20 text-pink-300 rounded">
                                {appId}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* 差异化策略 */}
              <section className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-orange-400" />
                  差异化策略 (可选借鉴)
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {uniqueStrategies.map((strategy, index) => (
                    <div 
                      key={index}
                      className="p-4 bg-[var(--bg-tertiary)] rounded-lg"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold text-pink-400">{strategy.app}</span>
                        <span className="text-xs text-[var(--text-muted)]">
                          {strategy.strategy}
                        </span>
                      </div>
                      <p className="text-sm text-[var(--text-secondary)]">
                        {strategy.description}
                      </p>
                    </div>
                  ))}
                </div>
              </section>

              {/* VitaFlow 推荐总结 */}
              <section className="bg-gradient-to-r from-pink-500/10 to-purple-500/10 border border-pink-500/30 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-pink-400" />
                  VitaFlow 推荐结构
                </h2>
                <div className="grid grid-cols-6 gap-4 text-center">
                  {[
                    { phase: '信任建立', pages: '2-4页', tactics: 'Authority + Social Proof' },
                    { phase: '目标设定', pages: '3-5页', tactics: 'Goal + Commitment' },
                    { phase: '数据收集', pages: '15-25页', tactics: 'Q→V穿插模式' },
                    { phase: '功能演示', pages: '5-10页', tactics: 'Interactive Demo' },
                    { phase: '最终设置', pages: '5-8页', tactics: 'Permission Pre-priming' },
                    { phase: '转化', pages: '8-12页', tactics: 'Premium Value Chain' },
                  ].map((item, index) => (
                    <div key={index} className="p-3 bg-[var(--bg-secondary)] rounded-lg">
                      <p className="text-xs text-[var(--text-muted)] mb-1">{item.phase}</p>
                      <p className="text-lg font-bold text-white mb-1">{item.pages}</p>
                      <p className="text-[10px] text-[var(--text-muted)]">{item.tactics}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-4 flex justify-center">
                  <Link href="/analysis/template">
                    <Button className="bg-pink-500 hover:bg-pink-600">
                      <Download className="w-4 h-4 mr-2" />
                      生成完整 VitaFlow 模板
                    </Button>
                  </Link>
                </div>
              </section>
            </>
          )}
        </div>
      </div>
    </AppLayout>
  );
}


