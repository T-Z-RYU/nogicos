'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Image, CheckCircle2 } from 'lucide-react'
import type { Project } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

// Logo URL helper
function getLogoUrl(projectName: string): string {
  const appName = projectName.includes('/') 
    ? projectName.split('/').pop() 
    : projectName
  return `${API_BASE}/api/logo/${appName}`
}

interface ProjectCardProps {
  project: Project
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link href={`/project/${encodeURIComponent(project.name)}`}>
      <motion.div
        className="group"
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      >
        <div 
          className="screenshot-card"
          style={{
            padding: 'var(--spacing-lg)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-md)',
          }}
        >
          {/* App Logo */}
          <div
            style={{ 
              width: '44px',
              height: '44px',
              borderRadius: '10px',
              overflow: 'hidden',
              flexShrink: 0,
              background: project.color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '16px',
              fontWeight: 600,
              color: '#fff',
              position: 'relative',
            }}
          >
            {/* 首字母作为后备（底层） */}
            <span>{project.initial}</span>
            {/* Logo 覆盖在上面 */}
            <img
              src={getLogoUrl(project.name)}
              alt={project.display_name}
              style={{
                position: 'absolute',
                inset: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
              onError={(e) => {
                // 加载失败时隐藏图片，显示首字母
                const target = e.target as HTMLImageElement
                target.style.display = 'none'
              }}
            />
          </div>

          {/* 项目信息 */}
          <div style={{ flex: 1, minWidth: 0 }}>
            {/* 项目名 */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              marginBottom: '4px',
            }}>
              <h3 style={{ 
                fontSize: '14px', 
                fontWeight: 600,
                color: 'var(--text-primary)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {project.display_name}
              </h3>
              {project.checked && (
                <CheckCircle2 size={14} style={{ color: 'var(--success)', flexShrink: 0 }} />
              )}
            </div>

            {/* 统计信息 */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px',
              fontSize: '12px',
              color: 'var(--text-muted)',
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Image size={12} />
                <span style={{ fontFamily: 'var(--font-mono)' }}>{project.screen_count}</span>
              </span>
              {project.onboarding_start > 0 && (
                <span>
                  Onboarding: {project.onboarding_start}-{project.onboarding_end}
                </span>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </Link>
  )
}


