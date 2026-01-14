'use client'

import { useEffect, useState } from 'react'
import { useProjectStore } from '@/store/project-store'
import { Search, Folder, Download } from 'lucide-react'

export function ProjectFilters() {
  const { search, sourceFilter, setSearch, setSourceFilter, stats, total } = useProjectStore()
  const [inputValue, setInputValue] = useState(search)

  // 防抖搜索
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(inputValue)
    }, 300)
    return () => clearTimeout(timer)
  }, [inputValue, setSearch])

  return (
    <div className="flex items-center gap-4">
      {/* 统计信息 - 精简显示 */}
      {stats && (
        <div className="hidden md:flex items-center gap-3 text-sm" style={{ color: 'var(--text-muted)' }}>
          <span>
            <strong style={{ color: 'var(--text-primary)' }}>{total}</strong> 项目
          </span>
          <span>·</span>
          <span>
            <strong style={{ color: 'var(--text-primary)' }}>{stats.total_screens}</strong> 截图
          </span>
        </div>
      )}

      {/* 来源筛选 - 老版样式 */}
      <div className="flex gap-1">
        <button
          className={`btn-ghost ${sourceFilter === 'all' ? 'active' : ''}`}
          onClick={() => setSourceFilter('all')}
        >
          全部
        </button>
        <button
          className={`btn-ghost ${sourceFilter === 'projects' ? 'active' : ''}`}
          onClick={() => setSourceFilter('projects')}
        >
          <Folder size={14} style={{ opacity: 0.7 }} />
          Projects
        </button>
        <button
          className={`btn-ghost ${sourceFilter === 'downloads_2024' ? 'active' : ''}`}
          onClick={() => setSourceFilter('downloads_2024')}
        >
          <Download size={14} style={{ opacity: 0.7 }} />
          Downloads
        </button>
      </div>

      {/* 搜索框 - 老版样式 */}
      <div className="relative">
        <Search 
          size={16} 
          style={{ 
            position: 'absolute', 
            left: '12px', 
            top: '50%', 
            transform: 'translateY(-50%)',
            color: 'var(--text-muted)'
          }} 
        />
        <input
          type="text"
          placeholder="搜索项目..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          style={{
            padding: '8px 12px 8px 36px',
            borderRadius: '6px',
            background: 'var(--bg-secondary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-default)',
            fontSize: '14px',
            width: '200px',
            transition: 'var(--transition-fast)',
            outline: 'none',
          }}
          onFocus={(e) => {
            e.target.style.borderColor = 'var(--border-hover)'
          }}
          onBlur={(e) => {
            e.target.style.borderColor = 'var(--border-default)'
          }}
        />
      </div>
    </div>
  )
}


