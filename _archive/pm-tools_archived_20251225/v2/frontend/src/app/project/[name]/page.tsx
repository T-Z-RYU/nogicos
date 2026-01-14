'use client'

import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { AppLayout } from '@/components/layout'
import { FadeIn } from '@/components/motion'
import {
  ScreenshotGrid,
  ScreenshotFilters,
  ScreenshotViewer,
} from '@/components/screenshot'
import { Toaster } from '@/components/ui/sonner'
import { useProjectStore } from '@/store/project-store'

export default function ProjectPage() {
  const params = useParams()
  const projectName = decodeURIComponent(params.name as string)
  const { projects, fetchProjects } = useProjectStore()

  // 加载项目列表以获取 data_source
  useEffect(() => {
    if (projects.length === 0) {
      fetchProjects()
    }
  }, [projects.length, fetchProjects])

  // 获取显示名称（去除来源前缀）
  const displayName = projectName.includes('/')
    ? projectName.split('/').pop()
    : projectName

  // 获取当前项目的 data_source
  const currentProject = projects.find((p) => p.name === projectName)
  const dataSource = currentProject?.data_source

  return (
    <AppLayout>
      {/* 顶栏 */}
      <div className="topbar">
        <h1 className="topbar-title">{displayName}</h1>
        {dataSource && (
          <span
            className="ml-2 px-2 py-0.5 text-xs font-medium rounded"
            style={{
              backgroundColor: dataSource === 'Mobbin' ? 'rgba(139, 92, 246, 0.15)' : 'rgba(16, 185, 129, 0.15)',
              color: dataSource === 'Mobbin' ? '#A78BFA' : '#34D399',
            }}
          >
            {dataSource}
          </span>
        )}
        <span className="text-muted text-sm ml-2">截图浏览</span>
        <div style={{ flex: 1 }} />
        <ScreenshotFilters />
      </div>

      {/* 内容区 */}
      <div className="content-area">
        <FadeIn delay={0.1}>
          <ScreenshotGrid projectName={projectName} />
        </FadeIn>
      </div>

      {/* 全屏查看器 */}
      <ScreenshotViewer projectName={projectName} />

      <Toaster />
    </AppLayout>
  )
}


