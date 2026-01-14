'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { 
  ChevronLeft, 
  Download,
  FileJson,
  FileText,
  Sparkles,
  Target,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Copy,
  Check
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { AppLayout } from '@/components/layout';
import { Button } from '@/components/ui/button';

// 类型颜色映射
const TYPE_COLORS: Record<string, string> = {
  W: '#E5E5E5', Q: '#3B82F6', V: '#22C516', S: '#EAB308',
  A: '#6366F1', R: '#A855F7', D: '#F97316', C: '#D97706',
  G: '#14B8A6', L: '#1F2937', X: '#6B7280', P: '#EF4444',
};

// 源 App 列表 - 8 个竞品
const SOURCE_APPS = ['flo', 'yazio', 'cal_ai', 'noom', 'myfitnesspal', 'loseit', 'macrofactor', 'weightwatchers'];

// API 响应类型
interface VitaFlowAPIResponse {
  industry_ratio: Record<string, { label: string; percentage: number; count: number }>;
  common_patterns: Array<{ pattern: string; name: string; interpretation: string; apps: string[]; total_occurrences: number }>;
  recommended_sequence: Array<{
    index: number;
    type: string;
    name: string;
    purpose: string;
    psychology: string[];
    ui_pattern: string;
    recommended_copy: { headline: string; subheadline: string | null; cta: string | null };
  }>;
  best_practices: Record<string, Array<{
    source_app: string;
    filename: string;
    ui_pattern: string;
    copy: { headline?: string; subheadline?: string; cta?: string };
    insight: string;
    confidence: number;
  }>>;
  total_screens_analyzed: number;
  apps_analyzed: number;
}

/**
 * VitaFlow 模板生成器页面
 */
export default function TemplateGeneratorPage() {
  const [apiData, setApiData] = useState<VitaFlowAPIResponse | null>(null);
  const [expandedPhases, setExpandedPhases] = useState<number[]>([0]);
  const [isLoading, setIsLoading] = useState(true);
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  // 从 API 加载模板数据
  useEffect(() => {
    const loadTemplate = async () => {
      setIsLoading(true);
      try {
        const res = await fetch('http://localhost:8002/api/analysis/template/vitaflow');
        if (!res.ok) throw new Error('Failed to fetch template');
        const data: VitaFlowAPIResponse = await res.json();
        setApiData(data);
      } catch (err) {
        console.error('Failed to load template:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadTemplate();
  }, []);

  // 切换阶段展开
  const togglePhase = useCallback((index: number) => {
    setExpandedPhases(prev =>
      prev.includes(index)
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  }, []);

  // 展开/收起全部
  const toggleAll = useCallback(() => {
    if (!apiData) return;
    const totalPages = apiData.recommended_sequence.length;
    if (expandedPhases.length === totalPages) {
      setExpandedPhases([]);
    } else {
      setExpandedPhases(apiData.recommended_sequence.map((_, i) => i));
    }
  }, [apiData, expandedPhases]);

  // 复制到剪贴板
  const copyToClipboard = useCallback(async (content: string, section: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  }, []);

  // 导出为 Markdown
  const exportMarkdown = useCallback(() => {
    if (!apiData) return;

    let md = `# VitaFlow Onboarding 模板\n\n`;
    md += `> 基于 ${apiData.apps_analyzed} 款竞品分析自动生成\n`;
    md += `> 分析了 ${apiData.total_screens_analyzed} 张截图\n\n`;
    
    md += `## 行业类型分布\n\n`;
    md += `| 类型 | 占比 | 数量 |\n`;
    md += `|------|------|------|\n`;
    Object.entries(apiData.industry_ratio)
      .sort((a, b) => b[1].percentage - a[1].percentage)
      .forEach(([code, info]) => {
        md += `| ${code} (${info.label}) | ${info.percentage}% | ${info.count} |\n`;
      });
    
    md += `\n## 推荐页面序列\n\n`;
    apiData.recommended_sequence.forEach(page => {
      md += `### ${page.index}. ${page.name} [${page.type}]\n\n`;
      md += `- **目的**: ${page.purpose}\n`;
      md += `- **心理策略**: ${page.psychology.join(', ')}\n`;
      md += `- **UI模式**: ${page.ui_pattern}\n`;
      md += `- **文案建议**:\n`;
      md += `  - 标题: ${page.recommended_copy.headline}\n`;
      if (page.recommended_copy.subheadline) {
        md += `  - 副标题: ${page.recommended_copy.subheadline}\n`;
      }
      if (page.recommended_copy.cta) {
        md += `  - CTA: ${page.recommended_copy.cta}\n`;
      }
      md += `\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vitaflow-onboarding-template.md';
    a.click();
    URL.revokeObjectURL(url);
  }, [apiData]);

  // 导出为 JSON
  const exportJSON = useCallback(() => {
    if (!apiData) return;

    const blob = new Blob([JSON.stringify(apiData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vitaflow-onboarding-template.json';
    a.click();
    URL.revokeObjectURL(url);
  }, [apiData]);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[80vh]">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-4 border-pink-500 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-[var(--text-muted)]">正在分析竞品数据并生成模板...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (!apiData) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[80vh]">
          <div className="text-center">
            <p className="text-red-500 mb-4">模板生成失败</p>
            <Link href="/analysis/compare">
              <Button>返回对比分析</Button>
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  const allExpanded = expandedPhases.length === apiData.recommended_sequence.length;

  return (
    <AppLayout>
      <div className="h-screen flex flex-col">
        {/* 头部 */}
        <header className="flex-shrink-0 border-b border-[var(--border-default)] bg-[var(--bg-secondary)] px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Link href="/analysis/compare">
                <Button variant="ghost" size="sm" className="text-[var(--text-secondary)] hover:text-white">
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  返回对比
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-bold flex items-center gap-2 text-white">
                  <Target className="w-5 h-5 text-pink-500" />
                  VitaFlow Onboarding 模板
                </h1>
                <p className="text-sm text-[var(--text-muted)]">
                  基于 {apiData.apps_analyzed} 款竞品 · {apiData.total_screens_analyzed} 张截图分析
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={toggleAll}
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
              <Button
                variant="outline"
                size="sm"
                onClick={exportMarkdown}
                className="text-[var(--text-secondary)]"
              >
                <FileText className="w-4 h-4 mr-1" />
                导出 Markdown
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={exportJSON}
                className="text-[var(--text-secondary)]"
              >
                <FileJson className="w-4 h-4 mr-1" />
                导出 JSON
              </Button>
            </div>
          </div>

          {/* 行业类型分布概览 */}
          <div className="grid grid-cols-6 md:grid-cols-12 gap-2">
            {Object.entries(apiData.industry_ratio)
              .sort((a, b) => b[1].percentage - a[1].percentage)
              .slice(0, 12)
              .map(([code, info]) => (
                <div 
                  key={code}
                  className="p-2 bg-[var(--bg-tertiary)] rounded-lg text-center"
                >
                  <div 
                    className="w-6 h-6 rounded mx-auto mb-1 flex items-center justify-center text-white text-xs font-bold"
                    style={{ backgroundColor: TYPE_COLORS[code] || '#6B7280' }}
                  >
                    {code}
                  </div>
                  <p className="text-sm font-bold text-white">{info.percentage}%</p>
                </div>
              ))}
          </div>
        </header>

        {/* 主内容区 */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* 检测到的模式 */}
          {apiData.common_patterns.length > 0 && (
            <div className="bg-gradient-to-r from-pink-500/10 to-purple-500/10 border border-pink-500/30 rounded-xl p-4 mb-6">
              <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-yellow-400" />
                检测到的序列模式
              </h3>
              <div className="flex flex-wrap gap-2">
                {apiData.common_patterns.map((pattern, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 bg-[var(--bg-secondary)] text-[var(--text-secondary)] rounded-full text-sm"
                  >
                    {pattern.pattern} ({pattern.apps.length} apps)
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 推荐页面序列 */}
          <h2 className="text-lg font-semibold text-white mb-4">
            推荐的 {apiData.recommended_sequence.length} 页 Onboarding 序列
          </h2>
          
          {apiData.recommended_sequence.map((page, index) => (
            <div 
              key={index}
              className="border border-[var(--border-default)] rounded-xl overflow-hidden bg-[var(--bg-secondary)]"
            >
              <button
                onClick={() => togglePhase(index)}
                className="w-full flex items-center justify-between p-4 hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div 
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: TYPE_COLORS[page.type] || '#6B7280' }}
                  >
                    {page.type}
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-semibold text-white">
                      #{page.index} {page.name}
                    </h3>
                    <p className="text-sm text-[var(--text-secondary)]">
                      {page.purpose}
                    </p>
                  </div>
                </div>
                <motion.div
                  animate={{ rotate: expandedPhases.includes(index) ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDown className="w-5 h-5 text-[var(--text-muted)]" />
                </motion.div>
              </button>

              <AnimatePresence>
                {expandedPhases.includes(index) && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="p-4 pt-0 space-y-4">
                      {/* 心理策略 */}
                      <div>
                        <p className="text-xs text-[var(--text-muted)] mb-2">心理策略</p>
                        <div className="flex flex-wrap gap-1">
                          {page.psychology.map((p, i) => (
                            <span key={i} className="px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded text-xs">
                              {p}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* UI 模式 */}
                      <div>
                        <p className="text-xs text-[var(--text-muted)] mb-1">UI 模式</p>
                        <p className="text-sm text-white">{page.ui_pattern}</p>
                      </div>

                      {/* 文案建议 */}
                      <div className="bg-[var(--bg-tertiary)] rounded-lg p-4">
                        <p className="text-xs text-[var(--text-muted)] mb-2">推荐文案</p>
                        <p className="text-lg font-semibold text-white mb-1">
                          {page.recommended_copy.headline}
                        </p>
                        {page.recommended_copy.subheadline && (
                          <p className="text-sm text-[var(--text-secondary)] mb-2">
                            {page.recommended_copy.subheadline}
                          </p>
                        )}
                        {page.recommended_copy.cta && (
                          <span className="inline-block px-4 py-2 bg-pink-500 text-white rounded-lg text-sm font-medium">
                            {page.recommended_copy.cta}
                          </span>
                        )}
                      </div>

                      {/* 最佳实践参考 */}
                      {apiData.best_practices[page.type] && (
                        <div>
                          <p className="text-xs text-[var(--text-muted)] mb-2">最佳实践参考</p>
                          <div className="flex gap-2 overflow-x-auto">
                            {apiData.best_practices[page.type].slice(0, 3).map((bp, i) => (
                              <div key={i} className="flex-shrink-0 p-2 bg-[var(--bg-tertiary)] rounded-lg text-xs">
                                <span className="text-pink-400">{bp.source_app}</span>
                                <span className="text-[var(--text-muted)]"> · {bp.ui_pattern}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}


