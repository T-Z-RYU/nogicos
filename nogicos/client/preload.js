/**
 * NogicOS Preload Script
 * 
 * Security地暴露 Electron API 给RenderProcess
 * 遵循 contextIsolation 最佳实践
 * 
 * Phase 7: Add agentAPI 支持
 */

const { contextBridge, ipcRenderer } = require('electron');

// ============================================================================
// electronAPI - baseWindowcontrol API
// ============================================================================
contextBridge.exposeInMainWorld('electronAPI', {
  // ============== Windowcontrol ==============
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close'),
  
  // ============== PlatformInfo ==============
  platform: process.platform,
  isElectron: true,
  
  // ============== EventListen ==============
  // ListenNewbuildSession
  onNewSession: (callback) => {
    ipcRenderer.on('new-session', () => callback());
    // ReturnCleanupFunction
    return () => ipcRenderer.removeAllListeners('new-session');
  },
  
  // ListenCommandPanelSwitch
  onToggleCommandPalette: (callback) => {
    ipcRenderer.on('toggle-command-palette', () => callback());
    return () => ipcRenderer.removeAllListeners('toggle-command-palette');
  },
  
  // ============== mainProcesscommunication ==============
  // TriggerCommandPanel
  toggleCommandPalette: () => ipcRenderer.send('toggle-command-palette'),
  
  // ============== Overlay control (Newversion electron-overlay-window) ==============
  // DisplayConnectState overlay（PrioritytrackTargetWindow，FallbackSystemNotify）
  showConnectionOverlay: (hookType, target, hwnd = 0) => 
    ipcRenderer.invoke('overlay:show-connection', { hookType, target, targetHwnd: hwnd }),
  
  // HideConnectState overlay
  hideConnectionOverlay: (hookType) => 
    ipcRenderer.invoke('overlay:hide-connection', { hookType }),
  
  // DisplayConnectNotify（onlyNotify，nottrack）
  showConnectionNotification: (hookType, target) =>
    ipcRenderer.invoke('notification:show', { 
      title: `NogicOS Connected`, 
      body: `Now monitoring: ${hookType} (${target})` 
    }),
  
  // ============== Newversion Overlay API ==============
  // Attach overlay toTargetWindow（throughtitleMatch）
  attachOverlay: (targetTitle, hookType) =>
    ipcRenderer.invoke('overlay:attach', { targetTitle, hookType }),
  
  // Detach overlay
  detachOverlay: () =>
    ipcRenderer.invoke('overlay:detach'),
  
  // Update overlay Innercontent
  updateOverlay: (message, status) =>
    ipcRenderer.invoke('overlay:update', { message, status }),
  
  // playsound
  playOverlaySound: (soundType) =>
    ipcRenderer.invoke('overlay:sound', { soundType }),
  
  // Get overlay State
  getOverlayStatus: () =>
    ipcRenderer.invoke('overlay:status'),
  
  // ============== DragConnecter API ==============
  // BeginDragConnecterPattern
  startDragConnector: () =>
    ipcRenderer.invoke('drag-connector:start'),
  
  // EndDragConnecterPattern（ReturnTargetWindowInfo）
  endDragConnector: () =>
    ipcRenderer.invoke('drag-connector:end'),
  
  // ListenDragprocessMedium's WindowInfoUpdate
  onDragConnectorUpdate: (callback) => {
    const handler = (event, data) => callback(data);
    ipcRenderer.on('drag-connector:update', handler);
    return () => ipcRenderer.removeListener('drag-connector:update', handler);
  },
  
  // ListenDragCompleteEvent（MouseReleasetimeAutoTrigger）
  onDragConnectorComplete: (callback) => {
    const handler = (event, target) => callback(target);
    ipcRenderer.on('drag-connector:complete', handler);
    return () => ipcRenderer.removeListener('drag-connector:complete', handler);
  },
  
  // ============== multipleWindow Overlay API (Newversion) ==============
  // Create Overlay（SupportmultipleWindow）
  createMultiOverlay: (hwnd, hookType, targetTitle) =>
    ipcRenderer.invoke('multi-overlay:create', { hwnd, hookType, targetTitle }),
  
  // DisplaySpecify Overlay
  showMultiOverlay: (hwnd) =>
    ipcRenderer.invoke('multi-overlay:show', { hwnd }),
  
  // HideSpecify Overlay
  hideMultiOverlay: (hwnd) =>
    ipcRenderer.invoke('multi-overlay:hide', { hwnd }),
  
  // DestroySpecify Overlay
  destroyMultiOverlay: (hwnd) =>
    ipcRenderer.invoke('multi-overlay:destroy', { hwnd }),
  
  // Destroyall Overlay
  destroyAllMultiOverlays: () =>
    ipcRenderer.invoke('multi-overlay:destroy-all'),
  
  // GetSpecify Overlay State
  getMultiOverlayStatus: (hwnd) =>
    ipcRenderer.invoke('multi-overlay:status', { hwnd }),
  
  // ColumnexitallActive's  Overlay
  listMultiOverlays: () =>
    ipcRenderer.invoke('multi-overlay:list'),
  
  // Phase 2: BeginPositiontrack
  startMultiOverlayTracking: (hwnd) =>
    ipcRenderer.invoke('multi-overlay:start-tracking', { hwnd }),
  
  // Phase 2: StopPositiontrack
  stopMultiOverlayTracking: (hwnd) =>
    ipcRenderer.invoke('multi-overlay:stop-tracking', { hwnd }),

  // Phase 7: SetActiveWindow（multipleWindowFocusmanage）
  setActiveOverlay: (hwnd) =>
    ipcRenderer.invoke('multi-overlay:set-active', { hwnd }),

  // Phase 7: LoopSwitchActiveWindow
  cycleActiveOverlay: () =>
    ipcRenderer.invoke('multi-overlay:cycle-active'),

  // Phase 7: SendactionPreviewtoSpecify Overlay
  sendOverlayPreview: (hwnd, previewType, data) =>
    ipcRenderer.invoke('multi-overlay:preview', { hwnd, previewType, data }),

  // Phase 7: ClearallactionPreview
  clearOverlayPreviews: () =>
    ipcRenderer.invoke('multi-overlay:clear-previews'),
});

// ============================================================================
// agentAPI - Agent control API (Phase 7)
// ⚠️ Securityneedrequest：Usage contextBridge Packageinstall，permanentnotdirectlyexpose ipcRenderer
// ============================================================================
contextBridge.exposeInMainWorld('agentAPI', {
  // ============== Agent control ==============
  
  /**
   * Start任务
   * @param {string} task - 任务描述
   * @param {number[]} targetHwnds - TargetWindow句柄Array
   * @returns {Promise<{taskId: string}>}
   */
  startTask: (task, targetHwnds) => 
    ipcRenderer.invoke('agent:start', { task, targetHwnds }),
  
  /**
   * Stop任务
   * @param {string} taskId - 任务 ID
   */
  stopTask: (taskId) => 
    ipcRenderer.invoke('agent:stop', { taskId }),
  
  /**
   * Resume任务
   * @param {string} taskId - 任务 ID
   */
  resumeTask: (taskId) => 
    ipcRenderer.invoke('agent:resume', { taskId }),

  // ============== StateSubscribe ==============
  
  /**
   * 订阅 Agent Event（Security的单向推送）
   * @param {Function} callback - EventCallback
   * @returns {Function} Cancel订阅Function
   */
  onAgentEvent: (callback) => {
    // ⚠️ Important：notpassOriginal event Object，onlypass data
    const handler = (_event, data) => callback(data);
    ipcRenderer.on('agent:event', handler);
    return () => ipcRenderer.removeListener('agent:event', handler);
  },
  
  /**
   * 订阅批量Event（Performance优化）
   * @param {Function} callback - 批量EventCallback
   * @returns {Function} Cancel订阅Function
   */
  onBatchEvents: (callback) => {
    const handler = (_event, events) => callback(events);
    ipcRenderer.on('agent:event:batch', handler);
    return () => ipcRenderer.removeListener('agent:event:batch', handler);
  },

  // ============== UserConfirm ==============
  
  /**
   * Response敏感操作Confirm
   * @param {string} taskId - 任务 ID
   * @param {string} actionId - 操作 ID
   * @param {boolean} approved - YesNo批准
   */
  confirmSensitiveAction: (taskId, actionId, approved) =>
    ipcRenderer.invoke('agent:confirm', { taskId, actionId, approved }),

  // ============== StateQuery ==============
  
  /**
   * Get任务State
   * @param {string} taskId - 任务 ID
   */
  getTaskStatus: (taskId) =>
    ipcRenderer.invoke('agent:status', { taskId }),
  
  /**
   * Get所有Active任务
   */
  getActiveTasks: () =>
    ipcRenderer.invoke('agent:active-tasks'),

  // ============== Overlay actionPreview ==============
  
  /**
   * 订阅动作预览Event
   * @param {Function} callback - 预览EventCallback
   * @returns {Function} Cancel订阅Function
   */
  onActionPreview: (callback) => {
    const channels = [
      'preview:mouse-trajectory',
      'preview:click',
      'preview:typing',
      'preview:target',
      'preview:scroll',
      'preview:shortcut',
      'preview:window-action',
      'preview:clear',
    ];
    
    const handlers = channels.map(channel => {
      const handler = (_event, data) => callback({ type: channel, data });
      ipcRenderer.on(channel, handler);
      return { channel, handler };
    });
    
    return () => {
      handlers.forEach(({ channel, handler }) => {
        ipcRenderer.removeListener(channel, handler);
      });
    };
  },

  // ============== WindowFocusmanage ==============
  
  /**
   * 订阅Window焦点变化
   * @param {Function} callback - 焦点变化Callback
   * @returns {Function} Cancel订阅Function
   */
  onFocusChange: (callback) => {
    const activeHandler = (_event) => callback({ active: true });
    const inactiveHandler = (_event) => callback({ active: false });
    
    ipcRenderer.on('focus:active', activeHandler);
    ipcRenderer.on('focus:inactive', inactiveHandler);
    
    return () => {
      ipcRenderer.removeListener('focus:active', activeHandler);
      ipcRenderer.removeListener('focus:inactive', inactiveHandler);
    };
  },
});
