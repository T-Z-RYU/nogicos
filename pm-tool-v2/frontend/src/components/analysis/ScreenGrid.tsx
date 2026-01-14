'use client';

import { motion } from 'framer-motion';
import { Eye, Layers, Zap } from 'lucide-react';
import type { ScreenData } from '@/store/analysis-store';

interface ScreenGridProps {
  screens: ScreenData[];
  selectedScreenIndex?: number;
  onScreenClick: (screen: ScreenData) => void;
  getImageUrl: (filename: string) => string;
  typeColors: Record<string, string>;
  typeLabels: Record<string, string>;
  columns?: number;
  showDetails?: boolean;
}

export function ScreenGrid({
  screens,
  selectedScreenIndex,
  onScreenClick,
  getImageUrl,
  typeColors,
  typeLabels,
  columns = 10,
  showDetails = false,
}: ScreenGridProps) {
  return (
    <div
      className="grid gap-3"
      style={{
        gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
      }}
    >
      {screens.map((screen, index) => (
        <ScreenCard
          key={screen.index}
          screen={screen}
          isSelected={selectedScreenIndex === screen.index}
          onClick={() => onScreenClick(screen)}
          imageUrl={getImageUrl(screen.filename)}
          typeColor={typeColors[screen.primary_type] || '#6B7280'}
          typeLabel={typeLabels[screen.primary_type] || screen.primary_type}
          showDetails={showDetails}
          animationDelay={index * 0.02}
        />
      ))}
    </div>
  );
}

// 截图卡片组件
interface ScreenCardProps {
  screen: ScreenData;
  isSelected: boolean;
  onClick: () => void;
  imageUrl: string;
  typeColor: string;
  typeLabel: string;
  showDetails: boolean;
  animationDelay: number;
}

function ScreenCard({
  screen,
  isSelected,
  onClick,
  imageUrl,
  typeColor,
  typeLabel,
  showDetails,
  animationDelay,
}: ScreenCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: animationDelay, duration: 0.3 }}
      className={`
        group relative rounded-xl overflow-hidden cursor-pointer
        bg-[var(--bg-tertiary)] border-2 transition-all duration-200
        ${isSelected 
          ? 'border-pink-500 ring-2 ring-pink-500/30 scale-[1.02]' 
          : 'border-transparent hover:border-[var(--border-default)] hover:scale-[1.02]'
        }
      `}
      onClick={onClick}
    >
      {/* 截图预览 */}
      <div className="aspect-[9/16] relative overflow-hidden">
        <img
          src={imageUrl}
          alt={`Screen ${screen.index}`}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
        />

        {/* 悬停遮罩 */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

        {/* 悬停时显示的详情 */}
        <div className="absolute bottom-0 left-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <p className="text-[10px] text-white/90 line-clamp-2">
            {screen.copy.headline || screen.insight.slice(0, 50)}
          </p>
        </div>
      </div>

      {/* 类型标签 - 左上角 */}
      <div
        className="absolute top-1.5 left-1.5 px-1.5 py-0.5 text-[10px] font-bold rounded-md shadow-sm"
        style={{ backgroundColor: typeColor, color: '#fff' }}
      >
        {screen.primary_type}
      </div>

      {/* 次要类型标签 - 右上角 */}
      {screen.secondary_type && (
        <div
          className="absolute top-1.5 right-1.5 px-1 py-0.5 text-[9px] font-medium rounded-md bg-black/50 text-white/80"
        >
          +{screen.secondary_type}
        </div>
      )}

      {/* 页码 - 右下角 */}
      <div className="absolute bottom-1.5 right-1.5 px-1.5 py-0.5 text-[10px] font-semibold bg-black/70 text-white rounded-md">
        {screen.index}
      </div>

      {/* 选中状态指示器 */}
      {isSelected && (
        <div className="absolute inset-0 border-2 border-pink-500 rounded-xl pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <Eye className="w-6 h-6 text-pink-500 drop-shadow-lg" />
          </div>
        </div>
      )}

      {/* 详情卡片（可选） */}
      {showDetails && (
        <div className="p-2 border-t border-[var(--border-default)]">
          <div className="flex items-center justify-between mb-1">
            <span
              className="text-[10px] font-medium px-1.5 py-0.5 rounded"
              style={{ backgroundColor: typeColor + '20', color: typeColor }}
            >
              {typeLabel}
            </span>
            <span className="text-[10px] text-[var(--text-muted)]">
              #{screen.index}
            </span>
          </div>
          <p className="text-[10px] text-[var(--text-secondary)] line-clamp-2">
            {screen.ui_pattern}
          </p>
        </div>
      )}
    </motion.div>
  );
}

// 带统计信息的截图网格
interface ScreenGridWithStatsProps extends ScreenGridProps {
  title?: string;
  totalScreens: number;
}

export function ScreenGridWithStats({
  title,
  totalScreens,
  screens,
  ...props
}: ScreenGridWithStatsProps) {
  const typeDistribution = screens.reduce((acc, screen) => {
    acc[screen.primary_type] = (acc[screen.primary_type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-4">
      {/* 头部统计 */}
      <div className="flex items-center justify-between">
        {title && (
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-pink-500" />
            {title}
          </h3>
        )}
        <div className="flex items-center gap-4 text-sm text-[var(--text-secondary)]">
          <span className="flex items-center gap-1">
            <Zap className="w-4 h-4" />
            {screens.length} / {totalScreens} 页
          </span>
          <div className="flex gap-1">
            {Object.entries(typeDistribution)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 5)
              .map(([type, count]) => (
                <span
                  key={type}
                  className="px-1.5 py-0.5 text-[10px] font-medium rounded"
                  style={{
                    backgroundColor: props.typeColors[type] || '#6B7280',
                    color: '#fff',
                  }}
                >
                  {type}:{count}
                </span>
              ))}
          </div>
        </div>
      </div>

      {/* 网格 */}
      <ScreenGrid screens={screens} {...props} />
    </div>
  );
}

export default ScreenGrid;

