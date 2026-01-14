/**
 * NogicOS Overlay Controller
 * 
 * Usage electron-overlay-window Implement流畅的Window追踪 Overlay
 * Core体验：Connect时在Target应用UpDisplayState条
 */

const { BrowserWindow, ipcMain } = require('electron');
const path = require('path');

// Try to load electron-overlay-window
let OverlayController = null;
let OVERLAY_WINDOW_OPTS = {};

try {
  const overlayLib = require('electron-overlay-window');
  OverlayController = overlayLib.OverlayController;
  OVERLAY_WINDOW_OPTS = overlayLib.OVERLAY_WINDOW_OPTS;
  console.log('[OverlayController] electron-overlay-window loaded successfully');
} catch (e) {
  console.warn('[OverlayController] electron-overlay-window not available:', e.message);
}

/**
 * Overlay State
 */
const OverlayState = {
  IDLE: 'idle',
  ATTACHING: 'attaching',
  ATTACHED: 'attached',
  ERROR: 'error',
};

/**
 * NogicOS Overlay Manager
 * 管理Connect到Outer部应用的 Overlay Window
 */
class NogicOSOverlayManager {
  constructor() {
    this._overlayWindow = null;
    this._state = OverlayState.IDLE;
    this._targetTitle = null;
    this._hookType = null;
    this._eventListeners = [];
  }

  /**
   * Get当BeforeState
   */
  get state() {
    return this._state;
  }

  /**
   * Check overlay 功能YesNoAvailable
   */
  get isAvailable() {
    return OverlayController !== null;
  }

  /**
   * Create并Attach Overlay 到TargetWindow
   * @param {string} targetTitle - TargetWindowtitle（精确Match）
   * @param {string} hookType - Hook Class型 (browser, desktop, file)
   * @param {object} options - ConfigOptions
   */
  attach(targetTitle, hookType, options = {}) {
    if (!this.isAvailable) {
      console.error('[OverlayManager] electron-overlay-window not available');
      return { success: false, error: 'Overlay library not available' };
    }

    // [Critical Fix] electron-overlay-window can only initialize once
    // If already initialized, just show existing window instead of re-attach
    // [Fix #2] Check if isInitialized is null
    if (OverlayController && OverlayController.isInitialized) {
      console.log('[OverlayManager] Already initialized, reusing existing overlay');
      // [P0 FIX Round 2] Removed hardcoded debug log - security risk
      
      if (this._overlayWindow && !this._overlayWindow.isDestroyed()) {
        // Restore overlay state (was hidden during detach)
        this._hookType = hookType;
        this._targetTitle = targetTitle;
        
        // 1. Restore opacity
        this._overlayWindow.setOpacity(1);
        
        // 2. Get current position (for diagnostics)
        const currentBounds = this._overlayWindow.getBounds();
        // [P0 FIX Round 2] Removed hardcoded debug log
        
        // 3. Reload overlay content
        const overlayHTML = this._generateOverlayHTML(hookType, targetTitle);
        this._overlayWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(overlayHTML)}`);
        
        // 4. Show window (position auto-synced by electron-overlay-window)
        this._overlayWindow.showInactive();
        
        this._state = OverlayState.ATTACHED;
        // Sound will auto-play after HTML loads
        console.log('[OverlayManager] Overlay reused, bounds:', currentBounds);
        return { success: true, reused: true };
      } else {
        console.warn('[OverlayManager] Overlay window destroyed, cannot reattach');
        return { success: false, error: 'Overlay window destroyed, restart app to reconnect' };
      }
    }

    this._state = OverlayState.ATTACHING;
    this._targetTitle = targetTitle;
    this._hookType = hookType;
    this._hasPlayedSound = false; // Reset sound flag

    try {
      // Create Overlay window
      this._overlayWindow = new BrowserWindow({
        width: 400,
        height: 36,
        webPreferences: {
          nodeIntegration: false,
          contextIsolation: true,
        },
        ...OVERLAY_WINDOW_OPTS,
      });

      // Load Overlay UI
      const overlayHTML = this._generateOverlayHTML(hookType, targetTitle);
      this._overlayWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(overlayHTML)}`);
      
      // [Plan B] Prevent Overlay from hiding when losing focus
      // Override hide method to do nothing
      const originalHide = this._overlayWindow.hide.bind(this._overlayWindow);
      this._overlayWindow.hide = () => {
        // Don't hide, keep always visible
        console.log('[OverlayManager] Blocked hide() - keeping overlay visible');
      };
      // Save original method for when hiding is really needed (e.g. detach)
      this._overlayWindow._originalHide = originalHide;

      // [Fix #1] Save detach method for restoration
      this._overlayWindow._restoreHide = () => {
        this._overlayWindow.hide = originalHide;
      };

      // Attach to target window
      OverlayController.attachByTitle(this._overlayWindow, targetTitle, {
        hasTitleBarOnMac: true,
      });

      // Listen to events
      this._setupEventListeners();

      console.log(`[OverlayManager] Attaching to "${targetTitle}" for ${hookType}`);
      
      // [Fix] Show Overlay and play sound immediately, don't wait for focus event
      setTimeout(() => {
        if (this._overlayWindow && !this._overlayWindow.isDestroyed()) {
          this._overlayWindow.showInactive();
          this.playSound('connect');
          console.log('[OverlayManager] Overlay shown and sound played after attach');
        }
      }, 100);
      
      return { success: true };
    } catch (e) {
      console.error('[OverlayManager] Failed to attach:', e);
      this._state = OverlayState.ERROR;
      return { success: false, error: e.message };
    }
  }

  /**
   * Detach Overlay（Hide但不Destroy，因为 electron-overlay-window 只能Initialize一次）
   */
  detach() {
    // [P0 FIX Round 2] Removed hardcoded debug log path

    if (this._overlayWindow && !this._overlayWindow.isDestroyed()) {
      try {
        // [Important] Cannot destroy window! electron-overlay-window native code will crash
        // Solution: Only set transparent, don't move position (keep position synced)

        // 1. Set window fully transparent (hide but keep position tracking)
        this._overlayWindow.setOpacity(0);
        
        // 2. clearEmpty HTML Innercontent（visualUpdisappear）
        this._overlayWindow.webContents.executeJavaScript(`
          document.body.innerHTML = '';
          document.body.style.background = 'transparent';
        `).catch(() => {});
        
        // 3. playDisconnectsound
        this.playSound('disconnect');
        
        // [Key]notMovePosition！let electron-overlay-window continuetrackTargetWindow
        // thisstyleheavyNewConnecttimePositionstillthencorrect
        
      } catch (e) {
        console.warn('[OverlayManager] Error hiding overlay:', e);
      }
    }
    
    this._state = OverlayState.IDLE;
    // notClear targetTitle，retaintoconvenientLibrarycontinuetrack（avoidCrash）
    this._hookType = null;
    this._hasPlayedSound = false;
    // notRemoveEventListener（avoidCrash）
    
    console.log('[OverlayManager] Detached (overlay hidden, not destroyed)');
    return { success: true };
  }

  /**
   * Update Overlay DisplayInner容
   * @param {string} message - Display的Message
   * @param {string} status - State (connected, working, error)
   */
  updateContent(message, status = 'connected') {
    if (!this._overlayWindow) return;

    this._overlayWindow.webContents.executeJavaScript(`
      updateOverlay("${message}", "${status}");
    `).catch(() => {});
  }

  /**
   * 播放音效
   * @param {string} soundType - 音效Class型 (connect, disconnect, action)
   */
  playSound(soundType = 'connect') {
    if (!this._overlayWindow) return;

    this._overlayWindow.webContents.executeJavaScript(`
      playSound("${soundType}");
    `).catch(() => {});
  }

  /**
   * SetEventListen器
   */
  _setupEventListeners() {
    if (!OverlayController) return;

    const onAttach = (e) => {
      console.log('[OverlayManager] Attached to target window, bounds:', e);
      this._state = OverlayState.ATTACHED;
      
      // Check bounds YesNoValid
      if (e && e.width > 0 && e.height > 0) {
        console.log('[OverlayManager] Valid bounds received, overlay positioned correctly');
      } else {
        console.log('[OverlayManager] Invalid bounds, target window position unknown');
      }
      
      // soundin attach() MethodMediumplay，herenotDuplicateplay
    };

    const onDetach = () => {
      console.log('[OverlayManager] Detached from target window');
      this._state = OverlayState.IDLE;
    };

    const onBlur = () => {
      console.log('[OverlayManager] Target window lost focus (overlay stays visible)');
      // hide() alreadybeOverride，Not NeedquotaOuterHandle
    };

    const onFocus = () => {
      console.log('[OverlayManager] Target window gained focus');
    };

    OverlayController.events.on('attach', onAttach);
    OverlayController.events.on('detach', onDetach);
    OverlayController.events.on('blur', onBlur);
    OverlayController.events.on('focus', onFocus);

    this._eventListeners = [
      { event: 'attach', handler: onAttach },
      { event: 'detach', handler: onDetach },
      { event: 'blur', handler: onBlur },
      { event: 'focus', handler: onFocus },
    ];
  }

  /**
   * 移除EventListen器
   */
  _removeEventListeners() {
    if (!OverlayController) return;

    this._eventListeners.forEach(({ event, handler }) => {
      OverlayController.events.removeListener(event, handler);
    });
    this._eventListeners = [];
  }

  /**
   * 生成 Overlay HTML - 增强版：发光Border + 脉冲Animation
   */
  _generateOverlayHTML(hookType, targetTitle) {
    const icons = {
      browser: '🌐',
      desktop: '🖥️',
      file: '📁',
    };

    const colors = {
      connected: '#10b981',  // emerald-500
      working: '#f59e0b',    // amber-500
      error: '#ef4444',      // red-500
    };

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    html, body {
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: transparent;
      -webkit-app-region: no-drag;
    }
    
    /* ============================================
       发光BorderEffect - 整个Window边缘
       ============================================ */
    .glow-border {
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 999;
    }
    
    .glow-border::before {
      content: '';
      position: absolute;
      inset: 0;
      border: 3px solid var(--glow-color, #10b981);
      border-radius: 4px;
      box-shadow: 
        inset 0 0 20px var(--glow-color, #10b981),
        0 0 30px var(--glow-color, #10b981),
        0 0 60px var(--glow-shadow, rgba(16, 185, 129, 0.5));
      animation: borderGlow 2s ease-in-out infinite;
    }
    
    /* Connect时的脉冲爆发 */
    .glow-border.connecting::before {
      animation: connectPulse 0.6s ease-out forwards;
    }
    
    /* 工作Medium的流动Effect */
    .glow-border.working::before {
      --glow-color: #f59e0b;
      --glow-shadow: rgba(245, 158, 11, 0.5);
      animation: workingGlow 0.8s ease-in-out infinite;
    }
    
    @keyframes borderGlow {
      0%, 100% { 
        opacity: 0.7;
        box-shadow: 
          inset 0 0 15px var(--glow-color, #10b981),
          0 0 25px var(--glow-color, #10b981),
          0 0 50px var(--glow-shadow, rgba(16, 185, 129, 0.4));
      }
      50% { 
        opacity: 1;
        box-shadow: 
          inset 0 0 25px var(--glow-color, #10b981),
          0 0 40px var(--glow-color, #10b981),
          0 0 80px var(--glow-shadow, rgba(16, 185, 129, 0.6));
      }
    }
    
    @keyframes connectPulse {
      0% {
        opacity: 1;
        box-shadow: 
          inset 0 0 30px #10b981,
          0 0 60px #10b981,
          0 0 120px rgba(16, 185, 129, 0.8);
        transform: scale(1.02);
      }
      100% {
        opacity: 0.7;
        box-shadow: 
          inset 0 0 15px #10b981,
          0 0 25px #10b981,
          0 0 50px rgba(16, 185, 129, 0.4);
        transform: scale(1);
      }
    }
    
    @keyframes workingGlow {
      0%, 100% {
        opacity: 0.8;
        box-shadow: 
          inset 0 0 20px var(--glow-color),
          0 0 35px var(--glow-color),
          0 0 70px var(--glow-shadow);
      }
      50% {
        opacity: 1;
        box-shadow: 
          inset 0 0 35px var(--glow-color),
          0 0 55px var(--glow-color),
          0 0 110px var(--glow-shadow);
      }
    }
    
    /* ============================================
       TopState条
       ============================================ */
    .overlay-container {
      position: absolute;
      top: 0;
      left: 8px;
      right: 8px;
      height: 36px;
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 0 14px;
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.95) 0%, rgba(5, 150, 105, 0.95) 100%);
      border-radius: 0 0 10px 10px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 12px;
      color: #fff;
      box-shadow: 
        0 4px 20px rgba(16, 185, 129, 0.4),
        0 8px 32px rgba(0, 0, 0, 0.2);
      transform: translateY(-100%);
      animation: slideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
      z-index: 1000;
    }
    
    @keyframes slideIn {
      from {
        transform: translateY(-100%);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }
    
    @keyframes slideOut {
      from {
        transform: translateY(0);
        opacity: 1;
      }
      to {
        transform: translateY(-100%);
        opacity: 0;
      }
    }
    
    .overlay-container.hiding {
      animation: slideOut 0.2s ease-in forwards;
    }
    
    /* State指示器 - 增强版 */
    .status-indicator {
      position: relative;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #fff;
    }
    
    .status-indicator::before {
      content: '';
      position: absolute;
      inset: -4px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      animation: statusPulse 2s ease-in-out infinite;
    }
    
    @keyframes statusPulse {
      0%, 100% { transform: scale(1); opacity: 0.5; }
      50% { transform: scale(1.5); opacity: 0; }
    }
    
    .status-indicator.working {
      background: #fff;
    }
    
    .status-indicator.working::before {
      animation: statusSpin 1s linear infinite;
    }
    
    @keyframes statusSpin {
      from { transform: rotate(0deg) scale(1.2); }
      to { transform: rotate(360deg) scale(1.2); }
    }
    
    .icon {
      font-size: 16px;
      filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.5));
    }
    
    .label {
      font-weight: 600;
      letter-spacing: 0.4px;
      flex: 1;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .logo {
      font-weight: 800;
      font-size: 11px;
      letter-spacing: 1px;
      text-transform: uppercase;
      opacity: 0.9;
      text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }
    
    /* State颜色 */
    .overlay-container.connected { 
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.95) 0%, rgba(5, 150, 105, 0.95) 100%);
      box-shadow: 0 4px 20px rgba(16, 185, 129, 0.5), 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .overlay-container.working { 
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.95) 0%, rgba(217, 119, 6, 0.95) 100%);
      box-shadow: 0 4px 20px rgba(245, 158, 11, 0.5), 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .overlay-container.error { 
      background: linear-gradient(135deg, rgba(239, 68, 68, 0.95) 0%, rgba(185, 28, 28, 0.95) 100%);
      box-shadow: 0 4px 20px rgba(239, 68, 68, 0.5), 0 8px 32px rgba(0, 0, 0, 0.2);
    }
  </style>
</head>
<body>
  <!-- 发光Border层 -->
  <div id="glowBorder" class="glow-border connecting"></div>
  
  <!-- TopState条 -->
  <div id="overlay" class="overlay-container connected">
    <div class="status-indicator"></div>
    <span class="icon">${icons[hookType] || '🔗'}</span>
    <span class="label" id="message">NogicOS Connected</span>
    <span class="logo">NogicOS</span>
  </div>
  
  <script>
    // sound (Web Audio API)
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    function playSound(type) {
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      if (type === 'connect') {
        // Connectsound：Upupgradeandstring
        oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(600, audioContext.currentTime + 0.05);
        oscillator.frequency.exponentialRampToValueAtTime(800, audioContext.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.35, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
      } else if (type === 'disconnect') {
        // Disconnectsound：Downdecreasetone
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(300, audioContext.currentTime + 0.15);
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
      } else if (type === 'action') {
        // Actionsound：ShortpromptClick
        oscillator.frequency.setValueAtTime(1200, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(800, audioContext.currentTime + 0.03);
        gainNode.gain.setValueAtTime(0.25, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.08);
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.08);
      }
    }
    
    function updateOverlay(message, status) {
      const overlay = document.getElementById('overlay');
      const messageEl = document.getElementById('message');
      const glowBorder = document.getElementById('glowBorder');
      
      messageEl.textContent = message;
      overlay.className = 'overlay-container ' + status;
      
      // UpdateemitlightBorderState
      glowBorder.className = 'glow-border ' + status;
      
      // Update indicator Animation
      const indicator = overlay.querySelector('.status-indicator');
      if (status === 'working') {
        indicator.classList.add('working');
      } else {
        indicator.classList.remove('working');
      }
    }
    
    function hideOverlay() {
      const overlay = document.getElementById('overlay');
      overlay.classList.add('hiding');
      
      // HideemitlightBorder
      const glowBorder = document.getElementById('glowBorder');
      glowBorder.style.opacity = '0';
      glowBorder.style.transition = 'opacity 0.3s ease-out';
    }
    
    // ConnectpulseAnimationCompleteAfterSwitchtobreathingAnimation
    setTimeout(() => {
      const glowBorder = document.getElementById('glowBorder');
      glowBorder.classList.remove('connecting');
      glowBorder.classList.add('connected');
    }, 600);
    
    // InitializetimeplayConnectsound
    setTimeout(() => playSound('connect'), 200);
  </script>
</body>
</html>
    `;
  }
}

// SingletonInstance
let overlayManager = null;

/**
 * Get OverlayManager Singleton
 */
function getOverlayManager() {
  if (!overlayManager) {
    overlayManager = new NogicOSOverlayManager();
  }
  return overlayManager;
}

/**
 * Set Overlay IPC handlers
 */
function setupOverlayIPC() {
  // Attach overlay toTargetWindow
  ipcMain.handle('overlay:attach', async (event, { targetTitle, hookType }) => {
    const manager = getOverlayManager();
    return manager.attach(targetTitle, hookType);
  });

  // Detach overlay
  ipcMain.handle('overlay:detach', async () => {
    const manager = getOverlayManager();
    return manager.detach();
  });

  // Update overlay Innercontent
  ipcMain.handle('overlay:update', async (event, { message, status }) => {
    const manager = getOverlayManager();
    manager.updateContent(message, status);
    return { success: true };
  });

  // playsound
  ipcMain.handle('overlay:sound', async (event, { soundType }) => {
    const manager = getOverlayManager();
    manager.playSound(soundType);
    return { success: true };
  });

  // GetState
  ipcMain.handle('overlay:status', async () => {
    const manager = getOverlayManager();
    return {
      available: manager.isAvailable,
      state: manager.state,
      targetTitle: manager._targetTitle,
      hookType: manager._hookType,
    };
  });

  console.log('[OverlayController] IPC handlers registered');
}

module.exports = {
  NogicOSOverlayManager,
  getOverlayManager,
  setupOverlayIPC,
  OverlayState,
};

