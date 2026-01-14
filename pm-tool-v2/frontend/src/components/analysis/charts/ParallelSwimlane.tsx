'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from 'recharts';
import type { PhaseAnalysis } from '@/store/analysis-store';

// 阶段颜色
const PHASE_COLORS: Record<string, string> = {
  'trust-building': '#3B82F6',
  'goal-setting': '#22C55E',
  'data-collection-a': '#A855F7',
  'data-collection-b': '#EC4899',
  'data-collection-c': '#F97316',
  'psychology-education': '#8B5CF6',
  'ai-demo': '#06B6D4',
  'feature-showcase': '#84CC16',
  'personalization': '#F59E0B',
  'final-setup': '#6366F1',
  'coach-introduction': '#14B8A6',
  'conversion': '#EF4444',
  'goal-commitment': '#10B981',
};

// 获取阶段简称
const getPhaseShortName = (name: string): string => {
  const shortNames: Record<string, string> = {
    '信任建立': '信任',
    '目标设定': '目标',
    '目标承诺': '承诺',
    '数据收集A - 周期信息': '周期',
    '数据收集B - 健康信息': '健康',
    '数据收集C - 生活方式': '生活',
    '数据收集': '数据',
    '心理学教育': '心理',
    'AI功能演示': 'AI演示',
    '功能展示': '功能',
    '个性化设置': '个性化',
    '最终设置': '设置',
    '教练介绍': '教练',
    '结果与转化': '转化',
    '转化': '转化',
  };
  return shortNames[name] || name.slice(0, 4);
};

interface ParallelSwimlaneProps {
  analyses: PhaseAnalysis[];
  height?: number;
}

export function ParallelSwimlane({ analyses, height = 300 }: ParallelSwimlaneProps) {
  // 转换数据为堆叠条形图格式
  const chartData = analyses.map((analysis) => {
    const data: Record<string, number | string> = {
      name: analysis.app,
      total: analysis.total_screens,
    };

    // 添加每个阶段的数据
    analysis.phases.forEach((phase) => {
      const count = phase.endIndex - phase.startIndex + 1;
      data[phase.name] = count;
    });

    return data;
  });

  // 获取所有阶段名称（用于堆叠）
  const allPhaseNames = new Set<string>();
  analyses.forEach((analysis) => {
    analysis.phases.forEach((phase) => {
      allPhaseNames.add(phase.name);
    });
  });

  // 自定义 Tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || payload.length === 0) return null;

    return (
      <div className="bg-[var(--bg-tertiary)] border border-[var(--border-default)] rounded-lg p-3 shadow-lg">
        <p className="font-semibold text-white mb-2">{label}</p>
        <div className="space-y-1">
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-[var(--text-secondary)]">
                {getPhaseShortName(entry.dataKey)}:
              </span>
              <span className="text-white font-medium">{entry.value} 页</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 60, bottom: 5 }}
        >
          <XAxis 
            type="number" 
            stroke="#6B7280"
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
            axisLine={{ stroke: '#374151' }}
          />
          <YAxis 
            type="category" 
            dataKey="name" 
            stroke="#6B7280"
            tick={{ fill: '#E5E7EB', fontSize: 14, fontWeight: 500 }}
            axisLine={{ stroke: '#374151' }}
            width={80}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            verticalAlign="top"
            wrapperStyle={{ paddingBottom: 20 }}
            formatter={(value: string) => (
              <span className="text-[var(--text-secondary)] text-xs">
                {getPhaseShortName(value)}
              </span>
            )}
          />
          
          {/* 为每个阶段创建一个 Bar */}
          {Array.from(allPhaseNames).map((phaseName, index) => {
            // 找到对应的阶段 ID 来获取颜色
            const phaseId = analyses[0]?.phases.find(p => p.name === phaseName)?.id || '';
            const color = PHASE_COLORS[phaseId] || `hsl(${index * 30}, 70%, 50%)`;
            
            return (
              <Bar
                key={phaseName}
                dataKey={phaseName}
                stackId="phases"
                fill={color}
                radius={index === 0 ? [4, 0, 0, 4] : index === allPhaseNames.size - 1 ? [0, 4, 4, 0] : 0}
              />
            );
          })}
        </BarChart>
      </ResponsiveContainer>

      {/* 时间轴刻度 */}
      <div className="flex justify-between px-20 text-xs text-[var(--text-muted)] mt-2">
        <span>0</span>
        <span>25</span>
        <span>50</span>
        <span>75</span>
        <span>100+</span>
      </div>
    </div>
  );
}

// 简化版泳道图 - 仅显示阶段条
interface SimpleSwimlaneProps {
  analysis: PhaseAnalysis;
}

export function SimpleSwimlane({ analysis }: SimpleSwimlaneProps) {
  const totalScreens = analysis.total_screens;

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="w-16 text-sm font-medium text-white truncate">
          {analysis.app}
        </span>
        <div className="flex-1 flex h-6 rounded-lg overflow-hidden">
          {analysis.phases.map((phase) => {
            const width = ((phase.endIndex - phase.startIndex + 1) / totalScreens) * 100;
            const color = PHASE_COLORS[phase.id] || '#6B7280';
            
            return (
              <div
                key={phase.id}
                className="h-full relative group cursor-pointer"
                style={{ 
                  width: `${width}%`,
                  backgroundColor: color 
                }}
                title={`${phase.name}: ${phase.startIndex}-${phase.endIndex}页`}
              >
                {/* 悬停时显示阶段名 */}
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="text-[10px] text-white font-medium truncate px-1">
                    {getPhaseShortName(phase.name)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
        <span className="w-12 text-xs text-[var(--text-muted)] text-right">
          {totalScreens}页
        </span>
      </div>
    </div>
  );
}

// 多产品并行泳道
interface MultiAppSwimlaneProps {
  analyses: PhaseAnalysis[];
}

export function MultiAppSwimlane({ analyses }: MultiAppSwimlaneProps) {
  return (
    <div className="space-y-3">
      {analyses.map((analysis) => (
        <SimpleSwimlane key={analysis.appId} analysis={analysis} />
      ))}
      
      {/* 图例 */}
      <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-[var(--border-default)]">
        {Object.entries(PHASE_COLORS).slice(0, 6).map(([id, color]) => {
          const displayName = id.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
          return (
            <div key={id} className="flex items-center gap-1.5">
              <div 
                className="w-3 h-3 rounded-sm" 
                style={{ backgroundColor: color }}
              />
              <span className="text-xs text-[var(--text-muted)]">{displayName}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ParallelSwimlane;

