'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  getPendingScreenshots,
  getPendingThumbnailUrl,
  importScreenshot,
  getApowersoftConfig,
  saveApowersoftConfig,
  clearPendingScreenshots,
  type PendingScreenshot,
  type ApowersoftConfig,
} from '@/lib/api'
import {
  FolderOpen,
  Settings,
  RefreshCw,
  Check,
  ImageIcon,
  Trash2,
  Zap,
} from 'lucide-react'
import { toast } from 'sonner'

interface PendingPanelProps {
  selectedProject: string | null
  onImportSuccess: () => void
  onAppendScreenshot?: (filename: string) => void // 自动导入时追加截图到父组件
  externalImportedFile?: string | null // 外部导入的文件名（通过拖拽导入）
}

export function PendingPanel({ selectedProject, onImportSuccess, onAppendScreenshot, externalImportedFile }: PendingPanelProps) {
  const [screenshots, setScreenshots] = useState<PendingScreenshot[]>([])
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState<ApowersoftConfig | null>(null)
  const [showConfig, setShowConfig] = useState(false)
  const [configPath, setConfigPath] = useState('')
  const [saving, setSaving] = useState(false)
  const [importing, setImporting] = useState<string | null>(null)
  const [lastImported, setLastImported] = useState<string | null>(null)
  const [importedFiles, setImportedFiles] = useState<Set<string>>(new Set()) // 已导入的文件列表
  
  // 自动导入模式
  const [autoImport, setAutoImport] = useState(false)
  const knownFilesRef = useRef<Set<string>>(new Set()) // 使用 ref 避免 stale closure
  const isAutoImportingRef = useRef(false) // 锁机制防止并发
  const selectedProjectRef = useRef(selectedProject) // 保持最新引用

  // 同步 selectedProject 到 ref
  useEffect(() => {
    selectedProjectRef.current = selectedProject
    // 切换项目时关闭自动导入
    if (!selectedProject) {
      setAutoImport(false)
    }
  }, [selectedProject])

  // 处理外部导入（从拖拽导入）
  useEffect(() => {
    if (externalImportedFile) {
      setImportedFiles(prev => new Set(prev).add(externalImportedFile))
    }
  }, [externalImportedFile])

  // 自动导入新截图
  const autoImportNewFiles = useCallback(async (newScreenshots: PendingScreenshot[]) => {
    const currentProject = selectedProjectRef.current
    if (!currentProject || isAutoImportingRef.current) return
    
    // 检测新文件
    const newFiles = newScreenshots.filter(s => !knownFilesRef.current.has(s.filename))
    if (newFiles.length === 0) return
    
    // 按创建时间排序（确保顺序正确）
    const sortedNewFiles = newFiles.sort((a, b) => 
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
    
    isAutoImportingRef.current = true
    
    try {
      for (const file of sortedNewFiles) {
        // 再次检查项目是否改变
        if (selectedProjectRef.current !== currentProject) break
        
        const result = await importScreenshot(currentProject, file.filename)
        if (result.success && result.new_filename) {
          // 使用父组件回调追加截图，确保使用同一个 store 实例
          if (onAppendScreenshot) {
            onAppendScreenshot(result.new_filename)
          }
          
          setImportedFiles(prev => new Set(prev).add(file.filename))
          setLastImported(result.new_filename)
          toast.success(`自动导入 ${result.new_filename}`, { duration: 1500 })
        }
      }
    } finally {
      isAutoImportingRef.current = false
    }
  }, [onAppendScreenshot])

  // 加载待处理截图
  const loadPending = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getPendingScreenshots()
      const currentFiles = new Set(data.screenshots.map(s => s.filename))
      
      // 自动导入模式：检测并导入新文件
      if (autoImport && selectedProjectRef.current) {
        await autoImportNewFiles(data.screenshots)
      }
      
      // 更新已知文件列表
      knownFilesRef.current = currentFiles
      setScreenshots(data.screenshots)
    } catch (error) {
      console.error('Failed to load pending screenshots:', error)
    } finally {
      setLoading(false)
    }
  }, [autoImport, autoImportNewFiles])

  // 加载配置
  const loadConfig = useCallback(async () => {
    try {
      const data = await getApowersoftConfig()
      setConfig(data)
      setConfigPath(data.path || '')
    } catch (error) {
      console.error('Failed to load config:', error)
    }
  }, [])

  // 初始化
  useEffect(() => {
    loadPending()
    loadConfig()
    
    // 每 1 秒刷新一次
    const interval = setInterval(loadPending, 1000)
    return () => clearInterval(interval)
  }, [loadPending, loadConfig])
  
  // 切换自动导入模式
  const toggleAutoImport = useCallback(() => {
    if (!selectedProject) {
      toast.error('请先选择一个项目')
      return
    }
    
    setAutoImport(prev => {
      const newValue = !prev
      if (newValue) {
        // 开启时，记录当前所有文件为已知（不导入旧文件）
        knownFilesRef.current = new Set(screenshots.map(s => s.filename))
        toast.success('自动导入已开启：新截图将自动追加到项目末尾')
      } else {
        toast.info('自动导入已关闭')
      }
      return newValue
    })
  }, [selectedProject, screenshots])

  // 保存配置
  const handleSaveConfig = async () => {
    setSaving(true)
    try {
      await saveApowersoftConfig(configPath, config?.auto_import || false)
      await loadConfig()
      await loadPending()
      setShowConfig(false)
    } catch (error) {
      console.error('Failed to save config:', error)
      toast.error('保存配置失败: ' + (error as Error).message)
    } finally {
      setSaving(false)
    }
  }

  // 清除所有待处理截图
  const handleClearAll = async () => {
    if (screenshots.length === 0) {
      toast.info('没有需要清除的截图')
      return
    }
    
    if (!confirm(`确定要清除全部 ${screenshots.length} 张待处理截图吗？\n\n此操作不可恢复！`)) {
      return
    }
    
    try {
      const result = await clearPendingScreenshots()
      if (result.success) {
        toast.success(result.message)
        setImportedFiles(new Set()) // 清空已导入标记
        await loadPending()
      }
    } catch (error) {
      console.error('Failed to clear screenshots:', error)
      toast.error('清除失败: ' + (error as Error).message)
    }
  }

  // 导入截图
  const handleImport = async (filename: string) => {
    if (!selectedProject) {
      toast.error('请先选择一个项目')
      return
    }

    setImporting(filename)
    try {
      const result = await importScreenshot(selectedProject, filename)
      if (result.success) {
        // 显示成功提示
        setLastImported(result.new_filename || filename)
        toast.success(`已导入 ${result.new_filename || filename}`)
        setTimeout(() => setLastImported(null), 3000)
        
        // 标记为已导入
        setImportedFiles(prev => new Set(prev).add(filename))
        
        await loadPending()
        onImportSuccess()
      } else {
        toast.error('导入失败: ' + result.message)
      }
    } catch (error) {
      console.error('Failed to import:', error)
      toast.error('导入失败: ' + (error as Error).message)
    } finally {
      setImporting(null)
    }
  }

  // 处理拖拽
  const handleDragStart = (e: React.DragEvent, screenshot: PendingScreenshot) => {
    e.dataTransfer.setData('application/x-pending-screenshot', JSON.stringify({
      filename: screenshot.filename,
      type: 'pending',
    }))
    e.dataTransfer.effectAllowed = 'copy'
  }

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        borderRadius: '8px',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      {/* 标题栏 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          borderBottom: '1px solid var(--border-default)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ImageIcon size={16} style={{ color: 'var(--text-muted)' }} />
          <span style={{ fontWeight: 500, fontSize: '13px' }}>
            待处理 Pending
          </span>
          <span
            style={{
              padding: '2px 6px',
              background: 'var(--bg-secondary)',
              borderRadius: '10px',
              fontSize: '11px',
              color: 'var(--text-muted)',
            }}
          >
            {screenshots.length}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '4px' }}>
          {/* 自动导入开关 */}
          <button
            onClick={toggleAutoImport}
            disabled={!selectedProject}
            style={{
              padding: '4px',
              background: autoImport ? 'var(--warning)' : 'transparent',
              border: 'none',
              color: autoImport ? '#000' : (selectedProject ? 'var(--text-muted)' : 'var(--text-muted)'),
              cursor: selectedProject ? 'pointer' : 'not-allowed',
              borderRadius: '4px',
              opacity: selectedProject ? 1 : 0.5,
              transition: 'all 0.2s',
            }}
            title={autoImport ? '关闭自动导入' : '开启自动导入（新截图自动追加到末尾）'}
          >
            <Zap size={14} />
          </button>
          <button
            onClick={loadPending}
            disabled={loading}
            style={{
              padding: '4px',
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              borderRadius: '4px',
            }}
            title="刷新"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={handleClearAll}
            disabled={screenshots.length === 0}
            style={{
              padding: '4px',
              background: 'transparent',
              border: 'none',
              color: screenshots.length > 0 ? 'var(--error)' : 'var(--text-muted)',
              cursor: screenshots.length > 0 ? 'pointer' : 'not-allowed',
              borderRadius: '4px',
              opacity: screenshots.length === 0 ? 0.5 : 1,
            }}
            title="清除全部"
          >
            <Trash2 size={14} />
          </button>
          <button
            onClick={() => setShowConfig(!showConfig)}
            style={{
              padding: '4px',
              background: showConfig ? 'var(--bg-secondary)' : 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              borderRadius: '4px',
            }}
            title="配置"
          >
            <Settings size={14} />
          </button>
        </div>
      </div>

      {/* 配置面板 */}
      <AnimatePresence>
        {showConfig && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid var(--border-default)',
              background: 'var(--bg-secondary)',
            }}
          >
            <div style={{ marginBottom: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
              傲软投屏截图目录
            </div>
            {/* 改为上下布局，避免保存按钮被挤掉 */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <input
                type="text"
                value={configPath}
                onChange={(e) => setConfigPath(e.target.value)}
                placeholder="C:\Users\...\Pictures\Apowersoft"
                style={{
                  width: '100%',
                  padding: '8px 10px',
                  background: 'var(--bg-primary)',
                  border: '1px solid var(--border-default)',
                  borderRadius: '4px',
                  color: 'var(--text-primary)',
                  fontSize: '12px',
                  boxSizing: 'border-box',
                }}
              />
              <button
                onClick={handleSaveConfig}
                disabled={saving}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  background: 'var(--success)',
                  border: 'none',
                  borderRadius: '4px',
                  color: '#fff',
                  fontSize: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px',
                }}
              >
                {saving ? <RefreshCw size={12} className="animate-spin" /> : <Check size={12} />}
                保存配置
              </button>
            </div>
            {config?.detected && (
              <div style={{ marginTop: '6px', fontSize: '11px', color: 'var(--success)' }}>
                ✓ 已自动检测到傲软目录
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 截图列表 */}
      <div
        style={{
          padding: '12px',
          flex: 1,
          overflowY: 'auto',
        }}
      >
        {loading && screenshots.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)', fontSize: '12px' }}>
            加载中...
          </div>
        ) : screenshots.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)', fontSize: '12px' }}>
            <FolderOpen size={24} style={{ marginBottom: '8px', opacity: 0.5 }} />
            <div>暂无待处理截图</div>
            {!config?.path && (
              <div style={{ marginTop: '4px', fontSize: '11px' }}>
                请先配置傲软截图目录
              </div>
            )}
          </div>
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '10px',
            }}
          >
            {screenshots.slice(0, 12).map((screenshot) => {
              const isImported = importedFiles.has(screenshot.filename)
              return (
              <div
                key={screenshot.filename}
                draggable={!!selectedProject}
                onDragStart={(e) => handleDragStart(e, screenshot)}
                style={{
                  aspectRatio: '9/16',
                  background: 'var(--bg-secondary)',
                  borderRadius: '4px',
                  overflow: 'hidden',
                  cursor: selectedProject ? 'grab' : 'not-allowed',
                  position: 'relative',
                  opacity: importing === screenshot.filename ? 0.5 : isImported ? 0.6 : 1,
                  transition: 'transform 0.15s, box-shadow 0.15s',
                  border: isImported ? '2px solid var(--success)' : 'none',
                }}
                title={isImported ? '已导入' : (selectedProject ? `拖拽到右侧排序区域导入` : '请先选择项目')}
                onMouseEnter={(e) => {
                  if (selectedProject) {
                    e.currentTarget.style.transform = 'scale(1.05)'
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                <img
                  src={getPendingThumbnailUrl(screenshot.filename)}
                  alt={screenshot.filename}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                  loading="lazy"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement
                    target.style.display = 'none'
                    // 显示占位图标
                    const parent = target.parentElement
                    if (parent && !parent.querySelector('.img-placeholder')) {
                      const placeholder = document.createElement('div')
                      placeholder.className = 'img-placeholder'
                      placeholder.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--text-muted);'
                      placeholder.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21,15 16,10 5,21"/></svg>'
                      parent.appendChild(placeholder)
                    }
                  }}
                />
                {importing === screenshot.filename && (
                  <div
                    style={{
                      position: 'absolute',
                      inset: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: 'rgba(0,0,0,0.5)',
                    }}
                  >
                    <RefreshCw size={16} className="animate-spin" style={{ color: '#fff' }} />
                  </div>
                )}
                {/* 已导入标记 */}
                {isImported && !importing && (
                  <div
                    style={{
                      position: 'absolute',
                      top: '4px',
                      right: '4px',
                      background: 'var(--success)',
                      borderRadius: '50%',
                      width: '20px',
                      height: '20px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Check size={12} style={{ color: '#fff' }} />
                  </div>
                )}
              </div>
            )})}
          </div>
        )}

        {screenshots.length > 12 && (
          <div
            style={{
              textAlign: 'center',
              marginTop: '8px',
              fontSize: '11px',
              color: 'var(--text-muted)',
            }}
          >
            还有 {screenshots.length - 12} 张截图...
          </div>
        )}
      </div>

      {/* 底部提示 */}
        <div
          style={{
            padding: '8px 12px',
            borderTop: '1px solid var(--border-default)',
            fontSize: '11px',
          color: autoImport ? 'var(--warning)' : (lastImported ? 'var(--success)' : 'var(--text-muted)'),
            textAlign: 'center',
            transition: 'color 0.2s',
          background: autoImport ? 'rgba(251, 191, 36, 0.1)' : 'transparent',
          }}
        >
        {autoImport ? (
          <>⚡ 自动导入中... 截图将自动追加</>
        ) : lastImported ? (
            <>✓ 已导入 {lastImported}</>
          ) : selectedProject ? (
          <>拖拽到右侧导入 或 点击 ⚡ 开启自动导入</>
          ) : (
            <>请先选择项目</>
          )}
        </div>
    </div>
  )
}

export default PendingPanel
