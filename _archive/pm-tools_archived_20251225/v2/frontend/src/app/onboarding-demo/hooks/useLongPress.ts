'use client'

import { useCallback, useRef, useState, useEffect } from 'react'

interface UseLongPressOptions {
  threshold?: number // 触发完成所需时间 (ms)
  onStart?: () => void
  onProgress?: (progress: number) => void
  onComplete?: () => void
  onCancel?: () => void
}

interface UseLongPressReturn {
  isPressed: boolean
  progress: number // 0 to 1
  handlers: {
    onMouseDown: () => void
    onMouseUp: () => void
    onMouseLeave: () => void
    onTouchStart: () => void
    onTouchEnd: () => void
  }
}

export function useLongPress(options: UseLongPressOptions = {}): UseLongPressReturn {
  const {
    threshold = 2000,
    onStart,
    onProgress,
    onComplete,
    onCancel
  } = options
  
  const [isPressed, setIsPressed] = useState(false)
  const [progress, setProgress] = useState(0)
  
  const startTimeRef = useRef<number | null>(null)
  const animationRef = useRef<number | null>(null)
  const completedRef = useRef(false)
  
  const updateProgress = useCallback(() => {
    if (!startTimeRef.current || completedRef.current) return
    
    const elapsed = Date.now() - startTimeRef.current
    const newProgress = Math.min(elapsed / threshold, 1)
    
    setProgress(newProgress)
    onProgress?.(newProgress)
    
    if (newProgress >= 1) {
      completedRef.current = true
      onComplete?.()
      return
    }
    
    animationRef.current = requestAnimationFrame(updateProgress)
  }, [threshold, onProgress, onComplete])
  
  const start = useCallback(() => {
    if (completedRef.current) return
    
    setIsPressed(true)
    setProgress(0)
    startTimeRef.current = Date.now()
    completedRef.current = false
    onStart?.()
    animationRef.current = requestAnimationFrame(updateProgress)
  }, [onStart, updateProgress])
  
  const stop = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = null
    }
    
    if (isPressed && !completedRef.current) {
      onCancel?.()
    }
    
    setIsPressed(false)
    if (!completedRef.current) {
      setProgress(0)
    }
    startTimeRef.current = null
  }, [isPressed, onCancel])
  
  // 清理
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [])
  
  // 重置 completed 状态的方法（可以通过设置 progress 为 0 触发）
  useEffect(() => {
    if (progress === 0) {
      completedRef.current = false
    }
  }, [progress])
  
  return {
    isPressed,
    progress,
    handlers: {
      onMouseDown: start,
      onMouseUp: stop,
      onMouseLeave: stop,
      onTouchStart: start,
      onTouchEnd: stop
    }
  }
}







