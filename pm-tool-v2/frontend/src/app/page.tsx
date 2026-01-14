'use client'

import { AppLayout } from '@/components/layout'
import { FadeIn } from '@/components/motion'
import { ProjectFilters, ProjectGrid } from '@/components/project'
import { Toaster } from '@/components/ui/sonner'

export default function Home() {
  return (
    <AppLayout>
      {/* 顶栏 */}
      <div className="topbar">
        <h1 className="topbar-title">全部项目</h1>
        <div style={{ flex: 1 }} />
        <ProjectFilters />
      </div>

      {/* 内容区 */}
      <div className="content-area">
        <FadeIn delay={0.1}>
          <ProjectGrid />
        </FadeIn>
      </div>

      <Toaster />
    </AppLayout>
  )
}
