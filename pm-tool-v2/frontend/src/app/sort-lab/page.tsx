'use client'

import { useEffect, useState } from 'react'
import { Tldraw, createShapeId, useEditor, AssetRecordType } from 'tldraw'
import 'tldraw/tldraw.css'
import { useSortStore } from '@/store/sort-store'
import { useProjectStore } from '@/store/project-store'

// 自动排列工具栏
function ArrangeToolbar() {
  const editor = useEditor()

  // 自动排列成网格
  const arrangeToGrid = () => {
    const shapes = editor.getCurrentPageShapes()
    const imageShapes = shapes.filter((s) => s.type === 'image')

    const COLS = 4
    const GAP_X = 220
    const GAP_Y = 320

    editor.batch(() => {
      imageShapes.forEach((shape, i) => {
        const col = i % COLS
        const row = Math.floor(i / COLS)

        editor.updateShape({
          id: shape.id,
          x: col * GAP_X + 50,
          y: row * GAP_Y + 50,
        })
      })
    })
  }

  // 对齐选中的图形
  const alignSelected = (operation: 'left' | 'right' | 'top' | 'bottom' | 'center-horizontal' | 'center-vertical') => {
    const selectedIds = editor.getSelectedShapeIds()
    if (selectedIds.length > 1) {
      editor.alignShapes(selectedIds, operation)
    }
  }

  // 均匀分布选中的图形
  const distributeSelected = (operation: 'horizontal' | 'vertical') => {
    const selectedIds = editor.getSelectedShapeIds()
    if (selectedIds.length > 2) {
      editor.distributeShapes(selectedIds, operation)
    }
  }

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 80,
        left: '50%',
        transform: 'translateX(-50%)',
        display: 'flex',
        gap: 8,
        padding: '12px 16px',
        background: 'white',
        borderRadius: 12,
        boxShadow: '0 2px 12px rgba(0,0,0,0.15)',
        zIndex: 1000,
      }}
    >
      <button
        onClick={arrangeToGrid}
        style={{
          padding: '8px 16px',
          borderRadius: 8,
          border: 'none',
          background: '#3b82f6',
          color: 'white',
          cursor: 'pointer',
          fontWeight: 500,
        }}
      >
        🔲 自动排列
      </button>
      <button
        onClick={() => alignSelected('left')}
        style={{
          padding: '8px 12px',
          borderRadius: 8,
          border: '1px solid #e5e7eb',
          background: 'white',
          cursor: 'pointer',
        }}
      >
        ⬅️ 左对齐
      </button>
      <button
        onClick={() => alignSelected('top')}
        style={{
          padding: '8px 12px',
          borderRadius: 8,
          border: '1px solid #e5e7eb',
          background: 'white',
          cursor: 'pointer',
        }}
      >
        ⬆️ 顶对齐
      </button>
      <button
        onClick={() => distributeSelected('horizontal')}
        style={{
          padding: '8px 12px',
          borderRadius: 8,
          border: '1px solid #e5e7eb',
          background: 'white',
          cursor: 'pointer',
        }}
      >
        ↔️ 水平分布
      </button>
      <button
        onClick={() => distributeSelected('vertical')}
        style={{
          padding: '8px 12px',
          borderRadius: 8,
          border: '1px solid #e5e7eb',
          background: 'white',
          cursor: 'pointer',
        }}
      >
        ↕️ 垂直分布
      </button>
    </div>
  )
}

// 项目选择器
function ProjectSelector({
  projects,
  selectedProject,
  onSelect,
}: {
  projects: { name: string; display_name: string }[]
  selectedProject: string | null
  onSelect: (project: string) => void
}) {
  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        left: 16,
        zIndex: 1000,
        display: 'flex',
        gap: 8,
        alignItems: 'center',
        padding: '8px 12px',
        background: 'white',
        borderRadius: 8,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <span style={{ fontWeight: 500, color: '#374151' }}>项目:</span>
      <select
        value={selectedProject || ''}
        onChange={(e) => onSelect(e.target.value)}
        style={{
          padding: '6px 12px',
          borderRadius: 6,
          border: '1px solid #e5e7eb',
          background: 'white',
          cursor: 'pointer',
        }}
      >
        <option value="">选择项目...</option>
        {projects.map((p) => (
          <option key={p.name} value={p.name}>
            {p.display_name || p.name}
          </option>
        ))}
      </select>
    </div>
  )
}

// 返回按钮
function BackButton() {
  return (
    <a
      href="/sort"
      style={{
        position: 'absolute',
        top: 16,
        right: 16,
        zIndex: 1000,
        padding: '8px 16px',
        background: '#f3f4f6',
        borderRadius: 8,
        textDecoration: 'none',
        color: '#374151',
        fontWeight: 500,
        display: 'flex',
        alignItems: 'center',
        gap: 6,
      }}
    >
      ← 返回原版排序
    </a>
  )
}

// 主页面
export default function SortLabPage() {
  const { projects, fetchProjects } = useProjectStore()
  const { screenshots, fetchData } = useSortStore()
  const [selectedProject, setSelectedProject] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  // #region agent log
  const [screenshotsReady, setScreenshotsReady] = useState(false)
  // #endregion

  // 加载项目列表
  useEffect(() => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:useEffect',message:'fetchProjects called',data:{},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    fetchProjects()
  }, [fetchProjects])

  // #region agent log
  useEffect(() => {
    fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:projects-effect',message:'projects changed',data:{projectsLength:projects.length,projectNames:projects.slice(0,5).map(p=>p.name)},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B'})}).catch(()=>{});
  }, [projects])
  // #endregion

  // 选择项目时加载截图
  const handleSelectProject = async (project: string) => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:handleSelectProject',message:'project selected',data:{project},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'C'})}).catch(()=>{});
    // #endregion
    setSelectedProject(project)
    setIsLoading(true)
    setScreenshotsReady(false)
    await fetchData(project)
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:handleSelectProject-after',message:'fetchData completed',data:{project,screenshotsLength:screenshots.length},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'C'})}).catch(()=>{});
    // #endregion
    setScreenshotsReady(true)
    setIsLoading(false)
  }

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {/* 项目选择器 */}
      <ProjectSelector
        projects={projects}
        selectedProject={selectedProject}
        onSelect={handleSelectProject}
      />

      {/* 返回按钮 */}
      <BackButton />

      {/* tldraw 画布 */}
      {selectedProject && screenshotsReady ? (
        <Tldraw
          key={`${selectedProject}-${Date.now()}`}
          onMount={(editor) => {
            // 【修复】使用 getState() 获取最新状态，而不是闭包中的旧值
            const currentScreenshots = useSortStore.getState().screenshots
            
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:onMount',message:'tldraw onMount',data:{selectedProject,screenshotsLength:currentScreenshots.length,firstScreenshot:currentScreenshots[0]?.filename},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'D',runId:'post-fix'})}).catch(()=>{});
            // #endregion
            
            // 开启网格模式
            editor.updateInstanceState({ isGridMode: true })

            // 如果有截图数据，创建图片
            if (currentScreenshots.length > 0) {
              const COLS = 4
              const GAP_X = 220
              const GAP_Y = 320
              const IMG_W = 200
              const IMG_H = 300

              // #region agent log
              const sampleUrl = `http://127.0.0.1:8000/screenshots/${selectedProject}/${currentScreenshots[0].filename}`
              fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:createShapes',message:'creating shapes',data:{count:currentScreenshots.length,sampleUrl},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E',runId:'post-fix2'})}).catch(()=>{});
              // #endregion

              // 【修复】先创建 Assets，再创建 Shapes
              // 根据文件扩展名设置正确的 mimeType
              const getMimeType = (filename: string) => {
                const ext = filename.split('.').pop()?.toLowerCase()
                switch (ext) {
                  case 'webp': return 'image/webp'
                  case 'jpg':
                  case 'jpeg': return 'image/jpeg'
                  case 'gif': return 'image/gif'
                  default: return 'image/png'
                }
              }
              
              const assets = currentScreenshots.map((img) => {
                const assetId = AssetRecordType.createId()
                return {
                  id: assetId,
                  type: 'image' as const,
                  typeName: 'asset' as const,
                  props: {
                    name: img.filename,
                    src: `http://127.0.0.1:8000/screenshots/${selectedProject}/${img.filename}`,
                    w: IMG_W,
                    h: IMG_H,
                    mimeType: getMimeType(img.filename),
                    isAnimated: false,
                  },
                  meta: {},
                }
              })

              // #region agent log
              try {
                editor.createAssets(assets)
                const createdAssets = editor.getAssets()
                fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:afterCreateAssets',message:'assets created',data:{inputCount:assets.length,createdCount:createdAssets.length,firstAssetId:assets[0]?.id,firstCreatedAsset:createdAssets[0]},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H',runId:'post-fix3'})}).catch(()=>{});
              } catch (err) {
                fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:createAssetsError',message:'createAssets failed',data:{error:String(err)},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'I',runId:'post-fix3'})}).catch(()=>{});
              }
              // #endregion

              // #region agent log
              try {
                // 【修复】tldraw 新版本用 createShapes (复数) 批量创建
                const shapesToCreate = currentScreenshots.map((img, i) => {
                  const col = i % COLS
                  const row = Math.floor(i / COLS)
                  return {
                    id: createShapeId(),
                    type: 'image' as const,
                    x: col * GAP_X + 50,
                    y: row * GAP_Y + 50,
                    props: {
                      assetId: assets[i].id,
                      w: IMG_W,
                      h: IMG_H,
                    },
                  }
                })
                
                editor.createShapes(shapesToCreate)

                const createdShapes = editor.getCurrentPageShapes()
                fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:afterCreateShapes',message:'shapes created',data:{shapesCount:createdShapes.length,imageShapes:createdShapes.filter(s=>s.type==='image').length},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'J',runId:'post-fix5'})}).catch(()=>{});
              } catch (shapeErr) {
                fetch('http://127.0.0.1:7242/ingest/1146cc51-3fe3-46a3-9e1a-4801e1a50de0',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sort-lab/page.tsx:createShapesError',message:'createShapes failed',data:{error:String(shapeErr),errorName:(shapeErr as Error).name,errorStack:(shapeErr as Error).stack?.slice(0,500)},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'J',runId:'post-fix5'})}).catch(()=>{});
              }
              // #endregion

              // 缩放到适合视图
              setTimeout(() => {
                editor.zoomToFit()
              }, 100)
            }
          }}
        >
          {/* 自动排列工具栏 */}
          <ArrangeToolbar />
        </Tldraw>
      ) : (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: '#9ca3af',
            fontSize: 18,
          }}
        >
          {isLoading ? '加载中...' : selectedProject ? '准备画布...' : '请选择一个项目开始'}
        </div>
      )}

      {/* 实验标签 */}
      <div
        style={{
          position: 'absolute',
          top: 16,
          left: '50%',
          transform: 'translateX(-50%)',
          padding: '6px 16px',
          background: '#fef3c7',
          color: '#92400e',
          borderRadius: 20,
          fontSize: 14,
          fontWeight: 500,
          zIndex: 1000,
        }}
      >
        🧪 实验版 - 无限画布排序
      </div>
    </div>
  )
}

