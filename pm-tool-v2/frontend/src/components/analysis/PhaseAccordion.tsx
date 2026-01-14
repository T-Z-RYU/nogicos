'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Target, Brain, Lightbulb } from 'lucide-react';
import type { Phase, ScreenData } from '@/store/analysis-store';

interface PhaseAccordionProps {
  phase: Phase;
  screens: ScreenData[];
  isExpanded: boolean;
  onToggle: () => void;
  onScreenClick: (screen: ScreenData) => void;
  selectedScreenIndex?: number;
  getImageUrl: (filename: string) => string;
  typeColors: Record<string, string>;
}

export function PhaseAccordion({
  phase,
  screens,
  isExpanded,
  onToggle,
  onScreenClick,
  selectedScreenIndex,
  getImageUrl,
  typeColors,
}: PhaseAccordionProps) {
  const screenCount = phase.endIndex - phase.startIndex + 1;
  const percentage = Math.round((screenCount / 100) * 100); // 假设总数为100

  return (
    <div className="border border-[var(--border-default)] rounded-lg overflow-hidden bg-[var(--bg-secondary)]">
      {/* 阶段头部 */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-[var(--bg-tertiary)] transition-colors"
      >
        <div className="flex items-center gap-4">
          {/* 展开/收起图标 */}
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-5 h-5 text-[var(--text-muted)]" />
          </motion.div>

          {/* 阶段信息 */}
          <div className="text-left">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              {phase.name}
              <span className="text-sm font-normal text-[var(--text-muted)]">
                ({phase.nameEn})
              </span>
            </h3>
            <p className="text-sm text-[var(--text-secondary)]">
              第 {phase.startIndex}-{phase.endIndex} 页 · {screenCount} 页 · {percentage}%
            </p>
          </div>
        </div>

        {/* 主要类型标签 */}
        <div className="flex items-center gap-2">
          {phase.dominantTypes.slice(0, 4).map((type) => (
            <span
              key={type}
              className="px-2 py-1 text-xs font-medium rounded"
              style={{
                backgroundColor: typeColors[type] || '#6B7280',
                color: '#fff',
              }}
            >
              {type}
            </span>
          ))}
        </div>
      </button>

      {/* 可折叠内容 */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-4 pt-0 space-y-4">
              {/* 阶段目的和策略 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-[var(--bg-tertiary)] rounded-lg">
                {/* 目的 */}
                <div className="flex items-start gap-2">
                  <Target className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-[var(--text-muted)] mb-1">目的</p>
                    <p className="text-sm text-[var(--text-secondary)]">{phase.purpose}</p>
                  </div>
                </div>

                {/* 心理策略 */}
                <div className="flex items-start gap-2">
                  <Brain className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-[var(--text-muted)] mb-1">心理策略</p>
                    <div className="flex flex-wrap gap-1">
                      {phase.psychologyTactics.slice(0, 3).map((tactic) => (
                        <span
                          key={tactic}
                          className="px-1.5 py-0.5 text-xs bg-purple-500/20 text-purple-300 rounded"
                        >
                          {tactic}
                        </span>
                      ))}
                      {phase.psychologyTactics.length > 3 && (
                        <span className="text-xs text-[var(--text-muted)]">
                          +{phase.psychologyTactics.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* 关键洞察 */}
                <div className="flex items-start gap-2">
                  <Lightbulb className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-[var(--text-muted)] mb-1">关键洞察</p>
                    <ul className="text-sm text-[var(--text-secondary)] space-y-0.5">
                      {phase.keyInsights.slice(0, 2).map((insight, i) => (
                        <li key={i} className="text-xs">• {insight}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* 截图网格 */}
              <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 xl:grid-cols-12 gap-2">
                {screens.map((screen) => (
                  <ScreenThumbnail
                    key={screen.index}
                    screen={screen}
                    isSelected={selectedScreenIndex === screen.index}
                    onClick={() => onScreenClick(screen)}
                    imageUrl={getImageUrl(screen.filename)}
                    typeColor={typeColors[screen.primary_type] || '#6B7280'}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// 截图缩略图组件
interface ScreenThumbnailProps {
  screen: ScreenData;
  isSelected: boolean;
  onClick: () => void;
  imageUrl: string;
  typeColor: string;
}

function ScreenThumbnail({
  screen,
  isSelected,
  onClick,
  imageUrl,
  typeColor,
}: ScreenThumbnailProps) {
  return (
    <motion.button
      onClick={onClick}
      className={`
        relative aspect-[9/16] rounded-lg overflow-hidden border-2 transition-all
        ${isSelected 
          ? 'border-pink-500 ring-2 ring-pink-500/30' 
          : 'border-transparent hover:border-[var(--border-default)]'
        }
      `}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* 截图图片 */}
      <img
        src={imageUrl}
        alt={`Screen ${screen.index}`}
        className="w-full h-full object-cover"
        loading="lazy"
      />

      {/* 类型标签 */}
      <div
        className="absolute top-1 left-1 px-1.5 py-0.5 text-[10px] font-bold rounded"
        style={{ backgroundColor: typeColor, color: '#fff' }}
      >
        {screen.primary_type}
      </div>

      {/* 页码 */}
      <div className="absolute bottom-1 right-1 px-1.5 py-0.5 text-[10px] font-medium bg-black/60 text-white rounded">
        {screen.index}
      </div>

      {/* 选中状态遮罩 */}
      {isSelected && (
        <div className="absolute inset-0 bg-pink-500/20 pointer-events-none" />
      )}
    </motion.button>
  );
}

export default PhaseAccordion;

