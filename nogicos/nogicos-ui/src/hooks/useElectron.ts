/**
 * useElectron Hook
 * 
 * 提供对 Electron API 的Securityvisit
 * 在浏览器EnvironmentMediumReturnEmpty操作
 */

import { useEffect, useCallback, useState } from 'react'

interface ElectronAPI {
  // Windowcontrol
  minimize: () => void
  maximize: () => void
  close: () => void
  
  // PlatformInfo
  platform: string
  isElectron: boolean
  
  // EventListen
  onNewSession: (callback: () => void) => () => void
  onToggleCommandPalette: (callback: () => void) => () => void
  
  // mainProcesscommunication
  toggleCommandPalette: () => void
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI
  }
}

export function useElectron() {
  const [isElectron, setIsElectron] = useState(false)
  const [platform, setPlatform] = useState<string>('web')

  useEffect(() => {
    const api = window.electronAPI
    if (api?.isElectron) {
      /* eslint-disable react-hooks/set-state-in-effect -- intentional: one-time initialization */
      setIsElectron(true)
      setPlatform(api.platform || 'unknown')
      /* eslint-enable react-hooks/set-state-in-effect */
    }
  }, [])

  // Windowcontrol
  const minimize = useCallback(() => {
    window.electronAPI?.minimize?.()
  }, [])

  const maximize = useCallback(() => {
    window.electronAPI?.maximize?.()
  }, [])

  const close = useCallback(() => {
    window.electronAPI?.close?.()
  }, [])

  // CommandPanel
  const toggleCommandPalette = useCallback(() => {
    window.electronAPI?.toggleCommandPalette?.()
  }, [])

  // EventListen
  const onNewSession = useCallback((callback: () => void) => {
    const api = window.electronAPI
    if (api?.onNewSession) {
      return api.onNewSession(callback)
    }
    return () => {}
  }, [])

  const onToggleCommandPalette = useCallback((callback: () => void) => {
    const api = window.electronAPI
    if (api?.onToggleCommandPalette) {
      return api.onToggleCommandPalette(callback)
    }
    return () => {}
  }, [])

  return {
    isElectron,
    platform,
    isMac: platform === 'darwin',
    isWindows: platform === 'win32',
    isLinux: platform === 'linux',
    
    // Windowcontrol
    minimize,
    maximize,
    close,
    
    // CommandPanel
    toggleCommandPalette,
    
    // EventListen
    onNewSession,
    onToggleCommandPalette,
  }
}

export default useElectron

