/**
 * Overlay Preload Script
 * Phase 7: Security地暴露 IPC EventListen给 Overlay RenderProcess
 * 
 * 遵循 Electron Security最佳实践：
 * - nodeIntegration: false
 * - contextIsolation: true
 * - 只暴露必要的、受限的 API
 */

const { contextBridge, ipcRenderer } = require('electron');

// Allow's PreviewEventChannel（Whitelist）
const ALLOWED_PREVIEW_CHANNELS = [
  'preview:click',
  'preview:target',
  'preview:typing',
  'preview:shortcut',
  'preview:scroll',
  'preview:mouse-trajectory',
  'preview:window-action',
  'preview:clear',
];

// Allow's FocusEventChannel
const ALLOWED_FOCUS_CHANNELS = [
  'focus:active',
  'focus:inactive',
];

// Allow's StateUpdateChannel
const ALLOWED_STATE_CHANNELS = [
  'state:update',  // StateUpdate（status, action, progress）
];

/**
 * Security地暴露 Overlay API
 */
contextBridge.exposeInMainWorld('overlayAPI', {
  /**
   * 订阅预览Event
   * @param {string} channel - 频道名（必须在WhitelistMedium）
   * @param {function} callback - CallbackFunction（只Receive data，不暴露 event Object）
   * @returns {function} Cancel订阅Function
   */
  onPreview: (channel, callback) => {
    // VerifyChannelYesNoinWhitelistMedium
    if (!ALLOWED_PREVIEW_CHANNELS.includes(channel)) {
      console.warn(`[OverlayPreload] Blocked subscription to unauthorized channel: ${channel}`);
      return () => {};
    }
    
    // PackageinstallCallback，onlypass data，notexpose event Object
    const wrappedCallback = (_event, data) => {
      try {
        callback(data);
      } catch (e) {
        console.error(`[OverlayPreload] Callback error for ${channel}:`, e);
      }
    };
    
    ipcRenderer.on(channel, wrappedCallback);
    
    // ReturnCancelSubscribeFunction
    return () => {
      ipcRenderer.removeListener(channel, wrappedCallback);
    };
  },
  
  /**
   * 订阅焦点Event
   * @param {string} channel - 频道名（focus:active 或 focus:inactive）
   * @param {function} callback - CallbackFunction
   * @returns {function} Cancel订阅Function
   */
  onFocus: (channel, callback) => {
    if (!ALLOWED_FOCUS_CHANNELS.includes(channel)) {
      console.warn(`[OverlayPreload] Blocked subscription to unauthorized focus channel: ${channel}`);
      return () => {};
    }
    
    const wrappedCallback = () => {
      try {
        callback();
      } catch (e) {
        console.error(`[OverlayPreload] Focus callback error for ${channel}:`, e);
      }
    };
    
    ipcRenderer.on(channel, wrappedCallback);
    
    return () => {
      ipcRenderer.removeListener(channel, wrappedCallback);
    };
  },
  
  /**
   * 一次性订阅所有预览Event（便捷Method）
   * @param {object} handlers - { click, target, typing, shortcut, scroll, mouseTrajectory, windowAction, clear }
   * @returns {function} Cancel所有订阅的Function
   */
  onAllPreviews: (handlers) => {
    const unsubscribes = [];
    
    const channelMap = {
      'preview:click': handlers.click,
      'preview:target': handlers.target,
      'preview:typing': handlers.typing,
      'preview:shortcut': handlers.shortcut,
      'preview:scroll': handlers.scroll,
      'preview:mouse-trajectory': handlers.mouseTrajectory,
      'preview:window-action': handlers.windowAction,
      'preview:clear': handlers.clear,
    };
    
    for (const [channel, handler] of Object.entries(channelMap)) {
      if (typeof handler === 'function') {
        const wrappedCallback = (_event, data) => {
          try {
            handler(data);
          } catch (e) {
            console.error(`[OverlayPreload] Handler error for ${channel}:`, e);
          }
        };
        ipcRenderer.on(channel, wrappedCallback);
        unsubscribes.push(() => ipcRenderer.removeListener(channel, wrappedCallback));
      }
    }
    
    return () => unsubscribes.forEach(unsub => unsub());
  },

  /**
   * 订阅StateUpdateEvent
   * @param {function} callback - CallbackFunction (state) => void
   *   state: { status, action, progress }
   *   status: 'idle' | 'reading' | 'writing' | 'processing' | 'error'
   * @returns {function} Cancel订阅Function
   */
  onStateUpdate: (callback) => {
    const wrappedCallback = (_event, state) => {
      try {
        callback(state);
      } catch (e) {
        console.error('[OverlayPreload] State update callback error:', e);
      }
    };
    
    ipcRenderer.on('state:update', wrappedCallback);
    
    return () => {
      ipcRenderer.removeListener('state:update', wrappedCallback);
    };
  },
});

console.log('[OverlayPreload] Initialized with secure IPC bridge');
