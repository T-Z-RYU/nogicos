'use client';

import { X } from 'lucide-react';
import type { ScreenData } from '@/store/swimlane-store';
import { Button } from '@/components/ui/button';

// 支持两种接口：旧的 typeColors 和新的 typeColor + typeLabel
interface ScreenDetailProps {
  screen: ScreenData;
  imageUrl?: string;
  typeColors?: Record<string, string>;
  typeColor?: string;
  typeLabel?: string;
  onClose: () => void;
}

// 默认颜色映射（后备用）
const DEFAULT_TYPE_COLORS: Record<string, string> = {
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

/**
 * 截图详情面板组件
 */
export function ScreenDetail({ 
  screen, 
  imageUrl, 
  typeColors, 
  typeColor,
  typeLabel,
  onClose 
}: ScreenDetailProps) {
  const {
    index,
    filename,
    primary_type,
    secondary_type,
    psychology,
    ui_pattern,
    copy,
    insight,
  } = screen;

  // 支持两种颜色获取方式
  const colors = typeColors || DEFAULT_TYPE_COLORS;
  const primaryColor = typeColor || colors[primary_type] || '#E5E5E5';
  const secondaryColor = secondary_type ? colors[secondary_type] : null;

  return (
    <div className="h-full flex flex-col bg-[var(--bg-secondary)]">
      {/* 头部 */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--border-default)]">
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold text-white">#{index}</span>
          <div className="flex gap-1">
            <span
              className="px-2 py-0.5 rounded text-xs font-bold text-white"
              style={{ backgroundColor: primaryColor }}
            >
              {typeLabel || primary_type}
            </span>
            {secondary_type && secondaryColor && (
              <span
                className="px-2 py-0.5 rounded text-xs font-bold text-white"
                style={{ backgroundColor: secondaryColor }}
              >
                {secondary_type}
              </span>
            )}
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} className="text-[var(--text-muted)] hover:text-white">
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* 截图预览 */}
        <div className="bg-[var(--bg-tertiary)] rounded-lg overflow-hidden">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={`Screen ${index}`}
              className="w-full h-auto max-h-[400px] object-contain mx-auto"
            />
          ) : (
            <div className="aspect-[9/16] flex items-center justify-center text-[var(--text-muted)]">
              {filename}
            </div>
          )}
        </div>

        {/* 文案信息 */}
        <section>
          <h3 className="text-sm font-semibold text-[var(--text-muted)] mb-2">📝 文案</h3>
          <div className="space-y-2 bg-[var(--bg-tertiary)] rounded-lg p-3">
            {copy?.headline && (
              <div>
                <span className="text-xs text-[var(--text-muted)]">标题</span>
                <p className="text-sm font-medium text-white">{copy.headline}</p>
              </div>
            )}
            {copy?.subheadline && (
              <div>
                <span className="text-xs text-[var(--text-muted)]">副标题</span>
                <p className="text-sm text-[var(--text-secondary)]">{copy.subheadline}</p>
              </div>
            )}
            {copy?.cta && (
              <div>
                <span className="text-xs text-[var(--text-muted)]">CTA</span>
                <p className="text-sm text-pink-400 font-medium">{copy.cta}</p>
              </div>
            )}
          </div>
        </section>

        {/* UI 模式 */}
        <section>
          <h3 className="text-sm font-semibold text-[var(--text-muted)] mb-2">🎨 UI 模式</h3>
          <span className="inline-block px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-sm">
            {ui_pattern}
          </span>
        </section>

        {/* 心理策略 */}
        <section>
          <h3 className="text-sm font-semibold text-[var(--text-muted)] mb-2">🧠 心理策略</h3>
          <div className="flex flex-wrap gap-1.5">
            {psychology.map((tactic, i) => (
              <span
                key={i}
                className="px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded text-xs"
              >
                {tactic}
              </span>
            ))}
          </div>
        </section>

        {/* 设计洞察 */}
        <section>
          <h3 className="text-sm font-semibold text-[var(--text-muted)] mb-2">💡 设计洞察</h3>
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
            {insight}
          </p>
        </section>
      </div>
    </div>
  );
}


