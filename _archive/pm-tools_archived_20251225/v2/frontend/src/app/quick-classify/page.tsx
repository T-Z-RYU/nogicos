'use client'

import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AppLayout } from '@/components/layout'
import { useProjectStore } from '@/store/project-store'
import { getScreenshots, getTaxonomy, updateClassification, getScreenshotUrl } from '@/lib/api'
import type { Screenshot } from '@/types'
import {
  Zap,
  ChevronLeft,
  ChevronRight,
  Check,
  SkipForward,
} from 'lucide-react'

// 快捷键映射
const keyboardShortcuts: Record<string, number> = {
  '1': 0,
  '2': 1,
  '3': 2,
  '4': 3,
  '5': 4,
  '6': 5,
  '7': 6,
  '8': 7,
  '9': 8,
  '0': 9,
}

export default function QuickClassifyPage() {
  const { projects, fetchProjects } = useProjectStore()

  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [screenshots, setScreenshots] = useState<Screenshot[]>([])
  const [stages, setStages] = useState<string[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [classified, setClassified] = useState<Set<string>>(new Set())

  // 当前截图
  const currentScreenshot = screenshots[currentIndex]
  const progress = screenshots.length > 0 ? ((currentIndex + 1) / screenshots.length) * 100 : 0
  const remainingCount = screenshots.length - classified.size

  // 加载项目列表
  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  // 切换项目时加载数据
  useEffect(() => {
    if (selectedProject) {
      loadData()
    }
  }, [selectedProject])

  const loadData = async () => {
    if (!selectedProject) return

    setLoading(true)
    try {
      const [screenshotsRes, taxonomyRes] = await Promise.all([
        getScreenshots(selectedProject),
        getTaxonomy(),
      ])

      // 只显示未分类的截图
      const unclassified = screenshotsRes.screenshots.filter(
        (s) => !s.classification?.stage
      )

      setScreenshots(unclassified)
      setStages(taxonomyRes.taxonomy.stages)
      setCurrentIndex(0)
      setClassified(new Set())
    } catch (error) {
      console.error('加载失败:', error)
    }
    setLoading(false)
  }

  // 分类当前截图
  const classifyCurrentAs = useCallback(
    async (stage: string) => {
      if (!selectedProject || !currentScreenshot || saving) return

      setSaving(true)
      try {
        await updateClassification(selectedProject, {
          [currentScreenshot.filename]: { stage },
        })

        setClassified((prev) => new Set([...prev, currentScreenshot.filename]))

        // 自动跳转到下一个
        if (currentIndex < screenshots.length - 1) {
          setCurrentIndex((prev) => prev + 1)
        }
      } catch (error) {
        console.error('分类失败:', error)
      }
      setSaving(false)
    },
    [selectedProject, currentScreenshot, currentIndex, screenshots.length, saving]
  )

  // 跳过当前截图
  const skipCurrent = useCallback(() => {
    if (currentIndex < screenshots.length - 1) {
      setCurrentIndex((prev) => prev + 1)
    }
  }, [currentIndex, screenshots.length])

  // 上一个
  const goPrev = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1)
    }
  }, [currentIndex])

  // 下一个
  const goNext = useCallback(() => {
    if (currentIndex < screenshots.length - 1) {
      setCurrentIndex((prev) => prev + 1)
    }
  }, [currentIndex, screenshots.length])

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 数字键分类
      if (e.key in keyboardShortcuts) {
        const stageIndex = keyboardShortcuts[e.key]
        if (stageIndex < stages.length) {
          classifyCurrentAs(stages[stageIndex])
        }
      }
      // 左右导航
      else if (e.key === 'ArrowLeft') {
        goPrev()
      } else if (e.key === 'ArrowRight') {
        goNext()
      }
      // 空格跳过
      else if (e.key === ' ') {
        e.preventDefault()
        skipCurrent()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [classifyCurrentAs, goPrev, goNext, skipCurrent, stages])

  return (
    <AppLayout>
      {/* 顶栏 */}
      <div className="topbar">
        <h1 className="topbar-title">快速分类</h1>
        <div style={{ flex: 1 }} />

        {/* 项目选择器 */}
        <select
          value={selectedProject || ''}
          onChange={(e) => setSelectedProject(e.target.value || null)}
          style={{
            padding: '8px 12px',
            borderRadius: '6px',
            background: 'var(--bg-secondary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-default)',
            fontSize: '14px',
            minWidth: '200px',
            cursor: 'pointer',
          }}
        >
          <option value="">选择项目...</option>
          {projects.map((project) => (
            <option key={project.name} value={project.name}>
              {project.display_name} ({project.screen_count})
            </option>
          ))}
        </select>

        {/* 进度 */}
        {selectedProject && screenshots.length > 0 && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginLeft: '16px',
            }}
          >
            <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              {currentIndex + 1} / {screenshots.length}
            </span>
            <div
              style={{
                width: '100px',
                height: '4px',
                background: 'var(--bg-secondary)',
                borderRadius: '2px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${progress}%`,
                  height: '100%',
                  background: 'var(--success)',
                  transition: 'width 0.2s',
                }}
              />
            </div>
            <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              剩余 {remainingCount}
            </span>
          </div>
        )}
      </div>

      {/* 内容区 */}
      <div className="content-area" style={{ display: 'flex', gap: '24px' }}>
        {/* 未选择项目 */}
        {!selectedProject && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '400px',
              color: 'var(--text-muted)',
              gap: '16px',
              width: '100%',
            }}
          >
            <Zap size={48} />
            <p>请选择一个项目开始快速分类</p>
            <p style={{ fontSize: '13px' }}>使用数字键 1-0 快速分配阶段</p>
          </div>
        )}

        {/* 加载中 */}
        {selectedProject && loading && (
          <div
            style={{
              display: 'flex',
              height: '256px',
              alignItems: 'center',
              justifyContent: 'center',
              width: '100%',
            }}
          >
            <div className="spinner" />
          </div>
        )}

        {/* 全部完成 */}
        {selectedProject && !loading && screenshots.length === 0 && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '400px',
              color: 'var(--text-muted)',
              gap: '16px',
              width: '100%',
            }}
          >
            <Check size={48} color="var(--success)" />
            <p>该项目所有截图都已分类</p>
          </div>
        )}

        {/* 主要内容 */}
        {selectedProject && !loading && currentScreenshot && (
          <>
            {/* 左侧：截图预览 */}
            <div
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
              }}
            >
              <AnimatePresence mode="wait">
                <motion.img
                  key={currentScreenshot.filename}
                  src={getScreenshotUrl(selectedProject, currentScreenshot.filename)}
                  alt={currentScreenshot.filename}
                  style={{
                    maxHeight: 'calc(100vh - 200px)',
                    maxWidth: '100%',
                    objectFit: 'contain',
                    borderRadius: '8px',
                  }}
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                  transition={{ duration: 0.2 }}
                />
              </AnimatePresence>

              {/* 导航按钮 */}
              <button
                onClick={goPrev}
                disabled={currentIndex === 0}
                style={{
                  position: 'absolute',
                  left: '0',
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: 'none',
                  color: '#fff',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: currentIndex === 0 ? 0.3 : 1,
                }}
              >
                <ChevronLeft size={24} />
              </button>

              <button
                onClick={goNext}
                disabled={currentIndex === screenshots.length - 1}
                style={{
                  position: 'absolute',
                  right: '0',
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: 'none',
                  color: '#fff',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: currentIndex === screenshots.length - 1 ? 0.3 : 1,
                }}
              >
                <ChevronRight size={24} />
              </button>
            </div>

            {/* 右侧：分类选项 */}
            <div
              style={{
                width: '240px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <div
                style={{
                  padding: '12px',
                  background: 'var(--bg-card)',
                  borderRadius: '8px',
                  marginBottom: '8px',
                }}
              >
                <p
                  style={{
                    fontSize: '12px',
                    color: 'var(--text-muted)',
                    marginBottom: '8px',
                  }}
                >
                  快捷键提示
                </p>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  数字键 1-0: 选择阶段
                  <br />
                  ← →: 前后切换
                  <br />
                  空格: 跳过
                </p>
              </div>

              {/* 跳过按钮 */}
              <button
                onClick={skipCurrent}
                className="btn-ghost"
                style={{
                  width: '100%',
                  justifyContent: 'flex-start',
                  padding: '12px 16px',
                }}
              >
                <SkipForward size={16} />
                跳过 (空格)
              </button>

              <div
                style={{
                  height: '1px',
                  background: 'var(--border-default)',
                  margin: '8px 0',
                }}
              />

              {/* 阶段按钮 */}
              {stages.map((stage, index) => {
                const isClassified = classified.has(currentScreenshot.filename)
                const shortcut = index < 10 ? (index + 1) % 10 : null

                return (
                  <motion.button
                    key={stage}
                    onClick={() => classifyCurrentAs(stage)}
                    disabled={saving || isClassified}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-default)',
                      borderRadius: '8px',
                      color: 'var(--text-primary)',
                      cursor: saving ? 'wait' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      fontSize: '14px',
                      textAlign: 'left',
                      opacity: isClassified ? 0.5 : 1,
                    }}
                  >
                    {shortcut !== null && (
                      <span
                        style={{
                          width: '24px',
                          height: '24px',
                          background: 'var(--bg-primary)',
                          borderRadius: '4px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '12px',
                          fontFamily: 'var(--font-mono)',
                        }}
                      >
                        {shortcut}
                      </span>
                    )}
                    <span style={{ flex: 1 }}>{stage}</span>
                  </motion.button>
                )
              })}
            </div>
          </>
        )}
      </div>
    </AppLayout>
  )
}
