'use client';

import { useMemo } from 'react';
import { Button } from '@/components/ui/button';
import type { ScreenType } from '@/store/swimlane-store';

interface TypeFilterProps {
  types: ScreenType[];
  activeFilters: string[];
  onToggle: (type: string) => void;
  onClear: () => void;
}

/**
 * 页面类型筛选器组件
 */
export function TypeFilter({ types, activeFilters, onToggle, onClear }: TypeFilterProps) {
  const sortedTypes = useMemo(() => {
    return [...types].sort((a, b) => b.count - a.count);
  }, [types]);

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm text-gray-500 mr-2">筛选:</span>
      
      {sortedTypes.map((type) => {
        const isActive = activeFilters.includes(type.code);
        
        return (
          <button
            key={type.code}
            onClick={() => onToggle(type.code)}
            className={`
              inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
              transition-all duration-200
              ${isActive 
                ? 'ring-2 ring-offset-1 shadow-sm' 
                : 'opacity-70 hover:opacity-100'
              }
            `}
            style={{
              backgroundColor: isActive ? type.color : `${type.color}20`,
              color: isActive ? 'white' : type.color,
              borderColor: type.color,
              ringColor: type.color,
            }}
          >
            <span className="font-bold">{type.code}</span>
            <span>{type.label}</span>
            <span className="ml-1 text-[10px] opacity-80">({type.count})</span>
          </button>
        );
      })}
      
      {activeFilters.length > 0 && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onClear}
          className="text-xs text-gray-500 hover:text-gray-700"
        >
          清除筛选
        </Button>
      )}
    </div>
  );
}


