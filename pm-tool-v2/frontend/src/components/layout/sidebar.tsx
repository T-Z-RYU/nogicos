'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useProjectStore } from '@/store/project-store'
import { Home, Settings, LayoutGrid, Play, ArrowUpDown, Tags, Store, GitBranch, FlaskConical, BarChart3, Sparkles, Smartphone } from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

// Logo URL helper
function getLogoUrl(projectName: string): string {
  // 从 downloads_2024/Fitbit 提取 Fitbit
  const appName = projectName.includes('/') 
    ? projectName.split('/').pop() 
    : projectName
  return `${API_BASE}/api/logo/${appName}`
}

export function Sidebar() {
  const pathname = usePathname()
  const { projects, fetchProjects, loading } = useProjectStore()

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  // 获取当前选中的项目
  const currentProject = pathname.startsWith('/project/')
    ? decodeURIComponent(pathname.replace('/project/', ''))
    : null

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-header">
        <Link href="/" className="logo">
          <LayoutGrid className="logo-icon" />
          <span>PM Lab</span>
        </Link>
      </div>

      {/* 导航 */}
      <div className="sidebar-section">
        <h3>导航</h3>
        <nav className="project-list">
          <Link href="/">
            <motion.div
              className={`project-item ${pathname === '/' ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <Home size={18} style={{ opacity: 0.7 }} />
              <span className="project-name">全部项目</span>
            </motion.div>
          </Link>
        </nav>
      </div>

      {/* 工具 */}
      <div className="sidebar-section">
        <h3>工具</h3>
        <nav className="project-list">
          <Link href="/onboarding">
            <motion.div
              className={`project-item ${pathname === '/onboarding' ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <Play size={18} style={{ opacity: 0.7 }} />
              <span className="project-name">Onboarding</span>
            </motion.div>
          </Link>
          <Link href="/sort">
            <motion.div
              className={`project-item ${pathname === '/sort' ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <ArrowUpDown size={18} style={{ opacity: 0.7 }} />
              <span className="project-name">排序</span>
            </motion.div>
          </Link>
          <Link href="/classify">
            <motion.div
              className={`project-item ${pathname.startsWith('/classify') ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <Tags size={18} style={{ opacity: 0.7 }} />
              <span className="project-name">分类</span>
            </motion.div>
          </Link>
          <Link href="/branch">
            <motion.div
              className={`project-item ${pathname === '/branch' ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <GitBranch size={18} style={{ opacity: 0.7 }} />
              <span className="project-name">分支流程</span>
            </motion.div>
          </Link>
          <Link href="/store">
            <motion.div
              className={`project-item ${pathname === '/store' ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <Store size={18} style={{ opacity: 0.7 }} />
              <span className="project-name">商店对比</span>
            </motion.div>
          </Link>
          <Link href="/flow-lab">
            <motion.div
              className={`project-item ${pathname === '/flow-lab' ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <FlaskConical size={18} style={{ opacity: 0.7, color: '#f59e0b' }} />
              <span className="project-name">Flow Lab</span>
              <span style={{ fontSize: '10px', color: '#f59e0b', marginLeft: '4px' }}>实验</span>
            </motion.div>
          </Link>
          <Link href="/analysis/compare">
            <motion.div
              className={`project-item ${pathname.startsWith('/analysis') ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <BarChart3 size={18} style={{ opacity: 0.7, color: '#ec4899' }} />
              <span className="project-name">竞品分析</span>
              <span style={{ fontSize: '10px', color: '#ec4899', marginLeft: '4px' }}>NEW</span>
            </motion.div>
          </Link>
          <Link href="/builder">
            <motion.div
              className={`project-item ${pathname === '/builder' ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <Sparkles size={18} style={{ opacity: 0.7, color: '#a855f7' }} />
              <span className="project-name">构建器</span>
              <span style={{ fontSize: '10px', color: '#a855f7', marginLeft: '4px' }}>NEW</span>
            </motion.div>
          </Link>
          <Link href="/onboarding-demo">
            <motion.div
              className={`project-item ${pathname === '/onboarding-demo' ? 'active' : ''}`}
              whileHover={{ x: 2 }}
              transition={{ duration: 0.15 }}
            >
              <Smartphone size={18} style={{ opacity: 0.7, color: '#ec4899' }} />
              <span className="project-name">VitaFlow Demo</span>
              <span style={{ fontSize: '10px', color: '#ec4899', marginLeft: '4px' }}>🎯</span>
            </motion.div>
          </Link>
        </nav>
      </div>

      {/* 项目列表 */}
      <div className="sidebar-section" style={{ flex: 1, overflow: 'auto', borderBottom: 'none' }}>
        <h3>
          项目 <span>{projects.length}</span>
        </h3>
        <div className="project-list">
          {loading ? (
            <div className="project-item" style={{ cursor: 'default' }}>
              <span className="text-muted">加载中...</span>
            </div>
          ) : (
            <AnimatePresence>
              {projects.map((project, index) => {
                const isActive = currentProject === project.name
                return (
                  <Link href={`/project/${encodeURIComponent(project.name)}`} key={project.name}>
                    <motion.div
                      className={`project-item ${isActive ? 'active' : ''}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.02, duration: 0.2 }}
                      whileHover={{ x: 2 }}
                    >
                      {/* 项目 Logo */}
                      <div
                        className="project-logo"
                        style={{ 
                          backgroundColor: 'transparent',
                          overflow: 'hidden',
                          padding: 0,
                        }}
                      >
                        <img
                          src={getLogoUrl(project.name)}
                          alt={project.display_name}
                          width={24}
                          height={24}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            borderRadius: '6px',
                          }}
                          onError={(e) => {
                            // 加载失败时显示首字母
                            const target = e.target as HTMLImageElement
                            target.style.display = 'none'
                            const parent = target.parentElement
                            if (parent) {
                              parent.style.backgroundColor = project.color
                              parent.textContent = project.initial
                            }
                          }}
                        />
                      </div>
                      {/* 项目名 */}
                      <span className="project-name">{project.display_name}</span>
                      {/* 来源标签 */}
                      {project.data_source && (
                        <span
                          className="text-xs"
                          style={{
                            color: project.data_source === 'Mobbin' ? '#A78BFA' : '#34D399',
                            opacity: 0.8,
                            marginLeft: '4px',
                          }}
                        >
                          {project.data_source === 'Mobbin' ? 'M' : 'S'}
                        </span>
                      )}
                      {/* 截图数量 */}
                      <span className="project-count">{project.screen_count}</span>
                    </motion.div>
                  </Link>
                )
              })}
            </AnimatePresence>
          )}
        </div>
      </div>

      {/* 底部设置 */}
      <div className="sidebar-section" style={{ borderTop: '1px solid var(--border-subtle)' }}>
        <Link href="/settings">
          <motion.div
            className={`project-item ${pathname === '/settings' ? 'active' : ''}`}
            whileHover={{ x: 2 }}
            transition={{ duration: 0.15 }}
          >
            <Settings size={18} style={{ opacity: 0.7 }} />
            <span className="project-name">设置</span>
          </motion.div>
        </Link>
      </div>
    </aside>
  )
}
