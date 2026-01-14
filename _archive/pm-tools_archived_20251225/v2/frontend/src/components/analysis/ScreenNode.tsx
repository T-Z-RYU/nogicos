'use client';

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { ScreenData } from '@/store/swimlane-store';

interface ScreenNodeData extends ScreenData {
  imageUrl?: string;
  isSelected?: boolean;
  typeColor?: string;
}

/**
 * 自定义节点组件 - 显示单个截图卡片
 */
function ScreenNodeComponent({ data, selected }: NodeProps<ScreenNodeData>) {
  const {
    index,
    filename,
    primary_type,
    secondary_type,
    copy,
    insight,
    imageUrl,
    isSelected,
    typeColor = '#E5E5E5',
  } = data;

  return (
    <div
      className={`
        relative w-[120px] rounded-lg overflow-hidden shadow-md transition-all
        ${isSelected || selected ? 'ring-2 ring-pink-500 shadow-lg scale-105' : 'hover:shadow-lg hover:scale-102'}
        bg-white
      `}
    >
      {/* 连接点 */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2 !h-2 !bg-gray-400"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="!w-2 !h-2 !bg-gray-400"
      />

      {/* 类型标签 */}
      <div
        className="absolute top-1 left-1 z-10 px-1.5 py-0.5 rounded text-[10px] font-bold text-white shadow"
        style={{ backgroundColor: typeColor }}
      >
        {primary_type}
        {secondary_type && `+${secondary_type}`}
      </div>

      {/* 序号 */}
      <div className="absolute top-1 right-1 z-10 w-5 h-5 rounded-full bg-gray-900/80 text-white text-[10px] flex items-center justify-center font-medium">
        {index}
      </div>

      {/* 截图预览 */}
      <div className="relative aspect-[9/19.5] bg-gray-100">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={`Screen ${index}`}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
            {filename}
          </div>
        )}
      </div>

      {/* 标题预览 */}
      <div className="p-1.5 border-t border-gray-100">
        <p className="text-[9px] text-gray-700 line-clamp-2 leading-tight">
          {copy?.headline || 'No headline'}
        </p>
      </div>
    </div>
  );
}

export const ScreenNode = memo(ScreenNodeComponent);


