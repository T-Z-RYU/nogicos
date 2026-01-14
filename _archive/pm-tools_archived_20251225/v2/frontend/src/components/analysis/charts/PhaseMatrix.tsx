'use client';

import { useMemo } from 'react';
import type { PhaseAnalysis, PhaseMatrixRow } from '@/store/analysis-store';

interface PhaseMatrixProps {
  analyses: PhaseAnalysis[];
  matrixData?: PhaseMatrixRow[];
}

// 规范化阶段名称映射
const PHASE_NAME_MAP: Record<string, string> = {
  'trust-building': '信任建立',
  'goal-setting': '目标设定',
  'goal-commitment': '目标承诺',
  'data-collection-a': '数据收集A',
  'data-collection-b': '数据收集B',
  'data-collection-c': '数据收集C',
  'data-collection': '数据收集',
  'psychology-education': '心理学教育',
  'ai-demo': 'AI演示',
  'feature-showcase': '功能展示',
  'personalization': '个性化设置',
  'final-setup': '最终设置',
  'coach-introduction': '教练介绍',
  'conversion': '转化',
};

// 通用阶段分类
const GENERIC_PHASES = [
  { id: 'trust', name: '信任建立', keywords: ['信任', 'trust'] },
  { id: 'goal', name: '目标/承诺', keywords: ['目标', 'goal', '承诺', 'commit'] },
  { id: 'data-a', name: '数据收集A', keywords: ['数据收集a', '周期', 'data-collection-a'] },
  { id: 'data-b', name: '数据收集B', keywords: ['数据收集b', '健康', 'data-collection-b'] },
  { id: 'value', name: '价值/功能', keywords: ['功能', '演示', 'feature', 'demo', 'ai'] },
  { id: 'final', name: '最终设置', keywords: ['最终', '设置', 'final', 'personalization'] },
  { id: 'conversion', name: '转化', keywords: ['转化', 'conversion'] },
];

export function PhaseMatrix({ analyses, matrixData }: PhaseMatrixProps) {
  // 如果提供了 matrixData 直接使用，否则从 analyses 生成
  const data = useMemo(() => {
    if (matrixData && matrixData.length > 0) return matrixData;
    
    // 从分析数据生成矩阵
    return generateMatrixData(analyses);
  }, [analyses, matrixData]);

  const apps = analyses.map(a => a.app);

  // 获取热力图颜色
  const getHeatColor = (value: number, average: number) => {
    if (value === 0) return 'bg-gray-800/50';
    const ratio = value / average;
    if (ratio < 0.7) return 'bg-red-500/30';
    if (ratio > 1.3) return 'bg-green-500/30';
    return 'bg-blue-500/30';
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-[var(--border-default)]">
            <th className="text-left p-3 text-sm font-semibold text-[var(--text-muted)]">
              阶段
            </th>
            {apps.map(app => (
              <th key={app} className="text-center p-3 text-sm font-semibold text-white">
                {app}
              </th>
            ))}
            <th className="text-center p-3 text-sm font-semibold text-[var(--text-muted)]">
              平均
            </th>
            <th className="text-center p-3 text-sm font-semibold text-green-400">
              建议
            </th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr 
              key={row.phaseName} 
              className={`border-b border-[var(--border-default)] ${
                index % 2 === 0 ? 'bg-[var(--bg-secondary)]' : ''
              }`}
            >
              <td className="p-3 text-sm font-medium text-white">
                {row.phaseName}
              </td>
              {apps.map(app => {
                const appData = row.appData[app];
                const value = appData?.count || 0;
                const percentage = appData?.percentage || 0;
                
                return (
                  <td 
                    key={app} 
                    className={`p-3 text-center ${getHeatColor(value, row.average)}`}
                  >
                    <span className="text-sm font-semibold text-white">{value}</span>
                    <span className="text-xs text-[var(--text-muted)] ml-1">
                      ({percentage}%)
                    </span>
                  </td>
                );
              })}
              <td className="p-3 text-center">
                <span className="text-sm font-semibold text-[var(--text-secondary)]">
                  {row.average.toFixed(1)}
                </span>
              </td>
              <td className="p-3 text-center">
                <span className="text-sm font-medium text-green-400">
                  {row.recommendation}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-[var(--border-default)]">
            <td className="p-3 text-sm font-semibold text-[var(--text-muted)]">
              总计
            </td>
            {apps.map(app => {
              const analysis = analyses.find(a => a.app === app);
              return (
                <td key={app} className="p-3 text-center">
                  <span className="text-sm font-bold text-white">
                    {analysis?.total_screens || 0}
                  </span>
                </td>
              );
            })}
            <td className="p-3 text-center">
              <span className="text-sm font-semibold text-[var(--text-secondary)]">
                {(analyses.reduce((sum, a) => sum + a.total_screens, 0) / analyses.length).toFixed(0)}
              </span>
            </td>
            <td className="p-3 text-center">
              <span className="text-sm font-medium text-green-400">-</span>
            </td>
          </tr>
        </tfoot>
      </table>

      {/* 图例 */}
      <div className="flex items-center gap-6 mt-4 pt-4 border-t border-[var(--border-default)]">
        <span className="text-xs text-[var(--text-muted)]">热力图：</span>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500/30 rounded" />
          <span className="text-xs text-[var(--text-muted)]">低于平均</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500/30 rounded" />
          <span className="text-xs text-[var(--text-muted)]">接近平均</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500/30 rounded" />
          <span className="text-xs text-[var(--text-muted)]">高于平均</span>
        </div>
      </div>
    </div>
  );
}

// 从分析数据生成矩阵数据
function generateMatrixData(analyses: PhaseAnalysis[]): PhaseMatrixRow[] {
  const matrix: PhaseMatrixRow[] = [];

  GENERIC_PHASES.forEach(genericPhase => {
    const appData: Record<string, { count: number; percentage: number }> = {};
    let total = 0;
    let count = 0;

    analyses.forEach(analysis => {
      // 查找匹配的阶段
      const matchingPhase = analysis.phases.find(phase => {
        const phaseLower = phase.name.toLowerCase();
        const phaseIdLower = phase.id.toLowerCase();
        return genericPhase.keywords.some(keyword => 
          phaseLower.includes(keyword.toLowerCase()) ||
          phaseIdLower.includes(keyword.toLowerCase())
        );
      });

      if (matchingPhase) {
        const screenCount = matchingPhase.endIndex - matchingPhase.startIndex + 1;
        const percentage = Math.round((screenCount / analysis.total_screens) * 100);
        appData[analysis.app] = { count: screenCount, percentage };
        total += screenCount;
        count++;
      } else {
        appData[analysis.app] = { count: 0, percentage: 0 };
      }
    });

    const average = count > 0 ? total / count : 0;
    const min = Math.max(1, Math.floor(average * 0.7));
    const max = Math.ceil(average * 1.3);

    matrix.push({
      phaseName: genericPhase.name,
      appData,
      average,
      recommendation: `${min}-${max}页`
    });
  });

  return matrix;
}

// 简化版矩阵 - 仅显示百分比
interface SimpleMatrixProps {
  analyses: PhaseAnalysis[];
}

export function SimplePhaseMatrix({ analyses }: SimpleMatrixProps) {
  const apps = analyses.map(a => a.app);
  const maxPhases = Math.max(...analyses.map(a => a.phases.length));

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="p-2 text-left text-[var(--text-muted)]">App</th>
            {Array.from({ length: maxPhases }, (_, i) => (
              <th key={i} className="p-2 text-center text-[var(--text-muted)]">
                阶段{i + 1}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {analyses.map(analysis => (
            <tr key={analysis.appId} className="border-t border-[var(--border-default)]">
              <td className="p-2 font-medium text-white">{analysis.app}</td>
              {analysis.phases.map((phase, i) => {
                const count = phase.endIndex - phase.startIndex + 1;
                const percentage = Math.round((count / analysis.total_screens) * 100);
                return (
                  <td key={i} className="p-2 text-center">
                    <div 
                      className="inline-block px-2 py-1 rounded text-xs font-medium"
                      style={{ 
                        backgroundColor: `hsl(${(i * 40) % 360}, 70%, 30%)`,
                        color: '#fff'
                      }}
                    >
                      {percentage}%
                    </div>
                  </td>
                );
              })}
              {/* 填充空白列 */}
              {Array.from({ length: maxPhases - analysis.phases.length }, (_, i) => (
                <td key={`empty-${i}`} className="p-2 text-center text-[var(--text-muted)]">
                  -
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PhaseMatrix;

