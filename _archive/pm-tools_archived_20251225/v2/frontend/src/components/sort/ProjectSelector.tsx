'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import type { ProjectSelectorProps } from '@/types/sort'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

function getLogoUrl(projectName: string): string {
  const appName = projectName.includes('/') 
    ? projectName.split('/').pop() 
    : projectName
  return `${API_BASE}/api/logo/${appName}`
}

// 内联样式定义（替代 style jsx 解决 scoped CSS 问题）
const styles = {
  container: {
    position: 'relative' as const,
    minWidth: '240px',
  },
  trigger: {
    width: '100%',
    padding: '8px 12px',
    borderRadius: '8px',
    background: 'var(--bg-secondary)',
    color: 'var(--text-primary)',
    border: '1px solid var(--border-default)',
    fontSize: '14px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  logo: {
    width: '24px',
    height: '24px',
    borderRadius: '5px',
    objectFit: 'cover' as const,
  },
  name: {
    flex: 1,
    textAlign: 'left' as const,
  },
  count: {
    color: 'var(--text-secondary)',
    fontSize: '12px',
  },
  placeholder: {
    flex: 1,
    textAlign: 'left' as const,
    color: 'var(--text-secondary)',
  },
  icon: {
    opacity: 0.5,
  },
  dropdown: {
    position: 'absolute' as const,
    top: '100%',
    left: 0,
    right: 0,
    marginTop: '4px',
    background: '#1a1a1a',
    border: '1px solid var(--border-default)',
    borderRadius: '8px',
    boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
    maxHeight: '400px',
    overflowY: 'auto' as const,
    zIndex: 100,
  },
  option: {
    width: '100%',
    padding: '10px 12px',
    background: 'transparent',
    border: 'none',
    borderBottom: '1px solid rgba(255,255,255,0.04)',
    color: '#fff',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '13px',
    textAlign: 'left' as const,
  },
  optionSelected: {
    background: 'rgba(255,255,255,0.08)',
  },
  optionLogo: {
    width: '28px',
    height: '28px',
    borderRadius: '6px',
    objectFit: 'cover' as const,
  },
  optionName: {
    flex: 1,
  },
  optionCount: {
    color: '#6b7280',
    fontSize: '12px',
  },
}

export function ProjectSelector({
  projects,
  selectedProject,
  onSelect,
}: ProjectSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [hoveredOption, setHoveredOption] = useState<string | null>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const selectedProjectData = projects.find(p => p.name === selectedProject)

  return (
    <div ref={dropdownRef} style={styles.container}>
      {/* 触发按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={styles.trigger}
      >
        {selectedProjectData ? (
          <>
            <img
              src={getLogoUrl(selectedProjectData.name)}
              alt={selectedProjectData.display_name}
              style={styles.logo}
              onError={(e) => {
                const target = e.target as HTMLImageElement
                target.style.display = 'none'
              }}
            />
            <span style={styles.name}>
              {selectedProjectData.display_name}
            </span>
            <span style={styles.count}>
              ({selectedProjectData.screen_count})
            </span>
          </>
        ) : (
          <span style={styles.placeholder}>
            选择项目...
          </span>
        )}
        <ChevronDown size={16} style={styles.icon} />
      </button>

      {/* 下拉列表 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
            style={styles.dropdown}
          >
            {projects.map((project) => (
              <button
                key={project.name}
                onClick={() => {
                  onSelect(project.name)
                  setIsOpen(false)
                }}
                onMouseEnter={() => setHoveredOption(project.name)}
                onMouseLeave={() => setHoveredOption(null)}
                style={{
                  ...styles.option,
                  ...(selectedProject === project.name ? styles.optionSelected : {}),
                  ...(hoveredOption === project.name ? { background: 'rgba(255,255,255,0.05)' } : {}),
                }}
              >
                <img
                  src={getLogoUrl(project.name)}
                  alt={project.display_name}
                  style={styles.optionLogo}
                  onError={(e) => {
                    const target = e.target as HTMLImageElement
                    target.style.display = 'none'
                  }}
                />
                <span style={styles.optionName}>
                  {project.display_name}
                </span>
                <span style={styles.optionCount}>
                  {project.screen_count}
                </span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
