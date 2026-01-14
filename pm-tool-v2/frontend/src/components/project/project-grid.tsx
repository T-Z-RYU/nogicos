'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { ProjectCard } from './project-card'
import { useProjectStore } from '@/store/project-store'

export function ProjectGrid() {
  const { projects, loading, error, fetchProjects, search, sourceFilter } = useProjectStore()

  // 初始加载和筛选变化时重新获取
  useEffect(() => {
    fetchProjects()
  }, [fetchProjects, search, sourceFilter])

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        height: '256px', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        <div className="spinner" />
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        height: '256px', 
        alignItems: 'center', 
        justifyContent: 'center',
        textAlign: 'center',
      }}>
        <p style={{ color: 'var(--danger)' }}>{error}</p>
        <button
          onClick={() => fetchProjects()}
          className="btn-ghost"
          style={{ marginTop: '16px' }}
        >
          重试
        </button>
      </div>
    )
  }

  if (projects.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        height: '256px', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: 'var(--text-muted)',
        gap: 'var(--spacing-md)',
      }}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        <p style={{ fontSize: '14px' }}>没有找到项目</p>
        {(search || sourceFilter !== 'all') && (
          <button
            onClick={() => {
              useProjectStore.getState().setSearch('')
              useProjectStore.getState().setSourceFilter('all')
            }}
            className="btn-ghost"
            style={{ fontSize: '13px' }}
          >
            清除筛选条件
          </button>
        )}
      </div>
    )
  }

  return (
    <motion.div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: 'var(--spacing-md)',
      }}
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: 0.03,
          },
        },
      }}
    >
      {projects.map((project) => (
        <motion.div
          key={project.name}
          variants={{
            hidden: { opacity: 0, y: 15, scale: 0.98 },
            visible: { opacity: 1, y: 0, scale: 1 },
          }}
          transition={{ 
            duration: 0.25, 
            ease: [0.4, 0, 0.2, 1],
          }}
        >
          <ProjectCard project={project} />
        </motion.div>
      ))}
    </motion.div>
  )
}


