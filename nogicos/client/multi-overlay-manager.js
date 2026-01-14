/**
 * NogicOS Multi-Overlay Manager
 * 
 * Phase 1: 基础 Overlay Window（Create/Destroy/Display/Hide）
 * Phase 2: Position跟踪（跟随TargetWindowMove）
 * 
 * 这Yes一个纯 Electron Implement，不依赖 electron-overlay-window
 * 支持多Window同时管理
 * 
 * @author NogicOS Team
 * @version 2.0.0 - Phase 2
 */

const { BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');

// ============== Safe Console Logging (Prevent EPIPE) ==============
// Electron may disconnect stdout/stderr pipes in some cases, causing console.log to throw EPIPE error
const safeLog = (...args) => {
  try {
    console.log(...args);
  } catch (e) {
    // Ignore EPIPE errors - stdout may be closed
  }
};

const safeError = (...args) => {
  try {
    console.error(...args);
  } catch (e) {
    // Ignore EPIPE errors - stderr may be closed
  }
};

const safeWarn = (...args) => {
  try {
    console.warn(...args);
  } catch (e) {
    // Ignore EPIPE errors
  }
};

// ============== Windows API (via koffi) ==============
let koffi = null;
let user32 = null;
let GetWindowRect = null;
let IsIconic = null;
let IsWindowVisible = null;
let GetForegroundWindow = null;

try {
  koffi = require('koffi');
  user32 = koffi.load('user32.dll');
  
  // Define RECT structure
  const RECT = koffi.struct('RECT_OVERLAY', {
    left: 'long',
    top: 'long',
    right: 'long',
    bottom: 'long',
  });
  
  // Bind Windows API functions
  GetWindowRect = user32.func('GetWindowRect', 'bool', ['void*', koffi.out(koffi.pointer(RECT))]);
  IsIconic = user32.func('IsIconic', 'bool', ['void*']);
  IsWindowVisible = user32.func('IsWindowVisible', 'bool', ['void*']);
  // Use 'long' to return HWND, get number directly (instead of void* pointer object)
  GetForegroundWindow = user32.func('GetForegroundWindow', 'long', []);
  
  safeLog('[MultiOverlay] koffi loaded, Windows API available');
} catch (e) {
  safeLog('[MultiOverlay] koffi not available:', e.message);
}

// Polling interval (30fps = 33ms)
const POLL_INTERVAL_MS = 8; // ~120fps for smoother tracking

/**
 * Overlay InstanceState
 */
const OverlayState = {
  IDLE: 'idle',
  ATTACHED: 'attached',
  HIDDEN: 'hidden',
  ERROR: 'error',
};

/**
 * CheckTargetWindow的完整State
 * @param {number} hwnd - Window句柄
 * @returns {{
 *   isMinimized: boolean,
 *   isVisible: boolean,
 *   isForeground: boolean,
 *   isFullyCovered: boolean,
 *   shouldShowOverlay: boolean
 * }}
 */
function getWindowState(hwnd) {
  const state = {
    isMinimized: false,
    isVisible: true,
    isForeground: false,
    isFullyCovered: false,
    shouldShowOverlay: false,
  };
  
  // Check if minimized
  state.isMinimized = isWindowMinimized(hwnd);
  if (state.isMinimized) {
    return state;
  }
  
  // Check visibility
  state.isVisible = isWindowVisibleNative(hwnd);
  if (!state.isVisible) {
    return state;
  }
  
  // Check if foreground window
  state.isForeground = isWindowForeground(hwnd);
  if (state.isForeground) {
    state.shouldShowOverlay = true;
    return state;
  }
  
  // Not foreground window, check if fully occluded
  const targetBounds = getWindowBounds(hwnd);
  const fgHwnd = GetForegroundWindow ? GetForegroundWindow() : 0;
  
  if (targetBounds && fgHwnd && fgHwnd !== hwnd) {
    const fgBounds = getWindowBounds(fgHwnd);
    if (fgBounds) {
      // Check if foreground window fully covers target window
      state.isFullyCovered = (
        fgBounds.x <= targetBounds.x &&
        fgBounds.y <= targetBounds.y &&
        fgBounds.x + fgBounds.width >= targetBounds.x + targetBounds.width &&
        fgBounds.y + fgBounds.height >= targetBounds.y + targetBounds.height
      );
    }
  }
  
  // If not fully occluded, show Overlay
  state.shouldShowOverlay = !state.isFullyCovered;
  
  return state;
}

/**
 * GetTargetWindow的Position和Size
 * @param {number} hwnd - Window句柄
 * @returns {{x: number, y: number, width: number, height: number} | null}
 */
function getWindowBounds(hwnd) {
  if (!GetWindowRect) {
    return null;
  }

  try {
    const rect = { left: 0, top: 0, right: 0, bottom: 0 };

    // Pass number directly, koffi will auto-handle void* conversion
    const success = GetWindowRect(hwnd, rect);
    if (!success) {
      return null;
    }

    const width = rect.right - rect.left;
    const height = rect.bottom - rect.top;

    // [Fix #5] Multi-monitor window filter - filter out invalid or oversized windows
    const displays = screen.getAllDisplays();
    let totalWidth = 0, totalHeight = 0;
    for (const d of displays) {
      totalWidth += d.bounds.width;
      totalHeight = Math.max(totalHeight, d.bounds.height);
    }

    // Filter out windows covering entire screen or with invalid dimensions
    if (width <= 0 || height <= 0) {
      return null;
    }
    if (width >= totalWidth * 0.99 && height >= totalHeight * 0.99) {
      return null;
    }

    return {
      x: rect.left,
      y: rect.top,
      width: width,
      height: height,
    };
  } catch (e) {
    safeError('[MultiOverlay] GetWindowRect error:', e.message);
    return null;
  }
}

/**
 * CheckWindowYesNoMin化
 * @param {number} hwnd
 * @returns {boolean}
 */
function isWindowMinimized(hwnd) {
  if (!IsIconic) {
    return false;
  }
  
  try {
    // Pass number directly
    return IsIconic(hwnd);
  } catch (e) {
    return false;
  }
}

/**
 * CheckWindowYesNoVisible
 * @param {number} hwnd
 * @returns {boolean}
 */
function isWindowVisibleNative(hwnd) {
  if (!IsWindowVisible) {
    return true; // Default visible
  }
  
  try {
    // Pass number directly
    return IsWindowVisible(hwnd);
  } catch (e) {
    return true;
  }
}

/**
 * CheckWindowYesNo在Before台（未被遮挡）
 * @param {number} hwnd
 * @returns {boolean}
 */
function isWindowForeground(hwnd) {
  if (!GetForegroundWindow) {
    return true; // Default foreground
  }
  
  try {
    // GetForegroundWindow now returns long (number), can compare directly
    const foregroundHwnd = GetForegroundWindow();
    return foregroundHwnd === hwnd;
  } catch (e) {
    safeError('[MultiOverlay] isWindowForeground error:', e.message);
    return true;
  }
}

/**
 * 单个 Overlay Instance
 */
class OverlayInstance {
  constructor(hwnd, hookType) {
    this.hwnd = hwnd;
    this.hookType = hookType;
    this.window = null;
    this.state = OverlayState.IDLE;
    this.pollInterval = null;
    this.lastBounds = null;
    this.isTracking = false;
  }

  /**
   * CheckInstanceYesNo存活
   */
  isAlive() {
    return this.window && !this.window.isDestroyed();
  }
}

/**
 * Multi-Overlay Manager
 * 管理多个 Overlay WindowInstance
 */
class MultiOverlayManager {
  constructor() {
    /** @type {Map<number, OverlayInstance>} hwnd -> OverlayInstance */
    this._overlays = new Map();
    this._isAvailable = true;
    /** @type {number | null} 当BeforeActiveWindow句柄 */
    this._currentActiveHwnd = null;
  }

  /**
   * Check功能YesNoAvailable
   */
  get isAvailable() {
    return this._isAvailable;
  }

  /**
   * Get当BeforeActive的 Overlay Count
   */
  get activeCount() {
    return this._overlays.size;
  }

  /**
   * Create Overlay Window（Phase 1 Core）
   * @param {number} hwnd - TargetWindow句柄
   * @param {string} hookType - Hook Class型 (browser, desktop)
   * @param {string} targetTitle - TargetWindowtitle
   * @returns {{success: boolean, error?: string}}
   */
  createOverlay(hwnd, hookType, targetTitle = '') {
    safeLog(`[MultiOverlay] Creating overlay for HWND: ${hwnd}, type: ${hookType}`);
    
    // Check if already exists
    if (this._overlays.has(hwnd)) {
      const existing = this._overlays.get(hwnd);
      if (existing.isAlive()) {
        safeLog(`[MultiOverlay] Overlay already exists for HWND: ${hwnd}`);
        return { success: true, reused: true };
      } else {
        // Clean up dead instances
        this._overlays.delete(hwnd);
      }
    }

    try {
      // Create instance
      const instance = new OverlayInstance(hwnd, hookType);

      // Create BrowserWindow
      instance.window = new BrowserWindow({
        width: 400,
        height: 36,
        x: 100,  // Initial position (Phase 2 will update dynamically)
        y: 100,
        
        // Key config
        transparent: true,
        frame: false,
        alwaysOnTop: true,
        skipTaskbar: true,
        focusable: false,  // Don't steal focus
        resizable: false,
        movable: false,
        hasShadow: false,
        
        // Windows special settings
        type: 'toolbar',  // Tool window type
        
        webPreferences: {
          nodeIntegration: false,
          contextIsolation: true,
          preload: path.join(__dirname, 'overlay-preload.js'),
        },
      });

      // Mouse pass-through
      instance.window.setIgnoreMouseEvents(true);
      
      // Top-most level
      instance.window.setAlwaysOnTop(true, 'screen-saver');

      // Load HTML
      const html = this._generateOverlayHTML(hookType, targetTitle);
      instance.window.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);

      // Listen for window close
      instance.window.on('closed', () => {
        safeLog(`[MultiOverlay] Window closed for HWND: ${hwnd}`);
        this._overlays.delete(hwnd);
      });

      // Save instance
      instance.state = OverlayState.ATTACHED;
      this._overlays.set(hwnd, instance);

      // Phase 2: Auto-start position tracking
      this.startTracking(hwnd);

      safeLog(`[MultiOverlay] Overlay created successfully for HWND: ${hwnd}`);
      return { success: true };

    } catch (e) {
      safeError(`[MultiOverlay] Failed to create overlay:`, e);
      return { success: false, error: e.message };
    }
  }

  /**
   * Display Overlay
   * @param {number} hwnd - TargetWindow句柄
   */
  showOverlay(hwnd) {
    const instance = this._overlays.get(hwnd);
    if (!instance || !instance.isAlive()) {
      safeWarn(`[MultiOverlay] No overlay found for HWND: ${hwnd}`);
      return { success: false, error: 'Overlay not found' };
    }

    instance.window.showInactive();
    instance.state = OverlayState.ATTACHED;
    safeLog(`[MultiOverlay] Overlay shown for HWND: ${hwnd}`);
    return { success: true };
  }

  /**
   * Hide Overlay
   * @param {number} hwnd - TargetWindow句柄
   */
  hideOverlay(hwnd) {
    const instance = this._overlays.get(hwnd);
    if (!instance || !instance.isAlive()) {
      safeWarn(`[MultiOverlay] No overlay found for HWND: ${hwnd}`);
      return { success: false, error: 'Overlay not found' };
    }

    instance.window.hide();
    instance.state = OverlayState.HIDDEN;
    safeLog(`[MultiOverlay] Overlay hidden for HWND: ${hwnd}`);
    return { success: true };
  }

  /**
   * Destroy Overlay
   * @param {number} hwnd - TargetWindow句柄
   */
  destroyOverlay(hwnd) {
    const instance = this._overlays.get(hwnd);
    if (!instance) {
      safeWarn(`[MultiOverlay] No overlay found for HWND: ${hwnd}`);
      return { success: false, error: 'Overlay not found' };
    }

    // Stop polling (Phase 2)
    if (instance.pollInterval) {
      clearInterval(instance.pollInterval);
      instance.pollInterval = null;
    }

    // Destroy window
    if (instance.isAlive()) {
      instance.window.destroy();
    }

    // Remove instance
    this._overlays.delete(hwnd);
    safeLog(`[MultiOverlay] Overlay destroyed for HWND: ${hwnd}`);
    return { success: true };
  }

  /**
   * Destroy所有 Overlay
   */
  destroyAll() {
    const hwnds = Array.from(this._overlays.keys());
    hwnds.forEach(hwnd => this.destroyOverlay(hwnd));
    safeLog(`[MultiOverlay] All overlays destroyed, count: ${hwnds.length}`);
    return { success: true, count: hwnds.length };
  }

  /**
   * Begin跟踪TargetWindowPosition（Phase 2）
   * @param {number} hwnd - TargetWindow句柄
   */
  startTracking(hwnd) {
    const instance = this._overlays.get(hwnd);
    if (!instance || !instance.isAlive()) {
      safeWarn(`[MultiOverlay] Cannot start tracking, overlay not found: ${hwnd}`);
      return { success: false, error: 'Overlay not found' };
    }

    // If already tracking, stop first
    if (instance.pollInterval) {
      clearInterval(instance.pollInterval);
    }

    safeLog(`[MultiOverlay] Starting position tracking for HWND: ${hwnd}`);

    // Sync position immediately once
    this._syncPosition(instance);

    // Start polling (30fps)
    instance.pollInterval = setInterval(() => {
      this._syncPosition(instance);
    }, POLL_INTERVAL_MS);

    instance.isTracking = true;
    return { success: true };
  }

  /**
   * Stop跟踪TargetWindowPosition
   * @param {number} hwnd - TargetWindow句柄
   */
  stopTracking(hwnd) {
    const instance = this._overlays.get(hwnd);
    if (!instance) {
      return { success: false, error: 'Overlay not found' };
    }

    if (instance.pollInterval) {
      clearInterval(instance.pollInterval);
      instance.pollInterval = null;
    }

    instance.isTracking = false;
    safeLog(`[MultiOverlay] Stopped tracking for HWND: ${hwnd}`);
    return { success: true };
  }

  /**
   * Sync Overlay Position到TargetWindow（PrivateMethod）
   * @private
   * @param {OverlayInstance} instance
   */
  _syncPosition(instance) {
    if (!instance.isAlive()) {
      this.stopTracking(instance.hwnd);
      return;
    }

    // Get complete window state
    const windowState = getWindowState(instance.hwnd);
    
    /*
     * State逻辑：
     * - Min化 → Hide
     * - 不Visible → Hide  
     * - Before台Window → Display
     * - 不YesBefore台但没被完全覆盖 → Display
     * - 被完全覆盖 → Hide
     */
    
    if (!windowState.shouldShowOverlay) {
      if (instance.state !== OverlayState.HIDDEN) {
        instance.window.hide();
        instance.state = OverlayState.HIDDEN;
      }
      return;
    }

    // Get target window position (physical pixels)
    const physicalBounds = getWindowBounds(instance.hwnd);
    if (!physicalBounds) {
      // Window may have closed
      safeWarn(`[MultiOverlay] Cannot get bounds for HWND: ${instance.hwnd}`);
      return;
    }

    // If previously hidden, restore display
    if (instance.state === OverlayState.HIDDEN) {
      instance.window.showInactive();
      instance.state = OverlayState.ATTACHED;
      safeLog(`[MultiOverlay] Target restored, showing overlay: ${instance.hwnd}`);
    }

    // DPI conversion: physical pixels → logical pixels (DIP)
    // Find the monitor where target window is located
    const targetPoint = { x: physicalBounds.x + 10, y: physicalBounds.y + 10 };
    const display = screen.getDisplayNearestPoint(targetPoint);
    const scaleFactor = display.scaleFactor || 1;

    // Convert coordinates
    const dipBounds = {
      x: Math.round(physicalBounds.x / scaleFactor),
      y: Math.round(physicalBounds.y / scaleFactor),
      width: Math.round(physicalBounds.width / scaleFactor),
      height: Math.round(physicalBounds.height / scaleFactor),
    };

    // Overlay covers entire window (for full-window border effect on entry)
    // When persistent, only shows top bar + corner markers, rest is transparent
    const currentBounds = instance.window.getBounds();
    if (currentBounds.x !== dipBounds.x || 
        currentBounds.y !== dipBounds.y ||
        currentBounds.width !== dipBounds.width ||
        currentBounds.height !== dipBounds.height) {
      instance.window.setBounds({
        x: dipBounds.x,
        y: dipBounds.y,
        width: dipBounds.width,
        height: dipBounds.height,
      });
    }
  }

  /**
   * Get所有Active的 HWND List
   */
  getActiveHwnds() {
    return Array.from(this._overlays.keys());
  }

  /**
   * SetActiveWindow（Phase 7.6: 多Window焦点管理）
   * High亮SpecifyWindow，使其他Window变暗
   * @param {number} activeHwnd - ActiveWindow句柄
   */
  setActiveWindow(activeHwnd) {
    for (const [hwnd, instance] of this._overlays) {
      if (!instance.isAlive()) continue;
      
      if (hwnd === activeHwnd) {
        // Active window
        instance.window.webContents.send('focus:active');
        safeLog(`[MultiOverlay] Window ${hwnd} set to ACTIVE`);
      } else {
        // Inactive window
        instance.window.webContents.send('focus:inactive');
        safeLog(`[MultiOverlay] Window ${hwnd} set to INACTIVE`);
      }
    }
  }

  /**
   * LoopSwitchActiveWindow
   * @returns {number | null} New的ActiveWindow HWND
   */
  cycleActiveWindow() {
    const hwnds = this.getActiveHwnds();
    if (hwnds.length === 0) return null;
    
    // If no active window, initialize to first one
    if (this._currentActiveHwnd === null || !hwnds.includes(this._currentActiveHwnd)) {
      const firstHwnd = hwnds[0];
      this.setActiveWindow(firstHwnd);
      this._currentActiveHwnd = firstHwnd;
      safeLog(`[MultiOverlay] Initialized active window to first: ${firstHwnd}`);
      return firstHwnd;
    }
    
    // Find current active window index
    const currentIndex = hwnds.indexOf(this._currentActiveHwnd);
    
    // Next one
    const nextIndex = (currentIndex + 1) % hwnds.length;
    const nextHwnd = hwnds[nextIndex];
    
    this.setActiveWindow(nextHwnd);
    this._currentActiveHwnd = nextHwnd;
    
    safeLog(`[MultiOverlay] Cycled active window: ${this._currentActiveHwnd} -> ${nextHwnd}`);
    return nextHwnd;
  }

  /**
   * Get当BeforeActiveWindow
   * @returns {number | null}
   */
  getCurrentActiveHwnd() {
    return this._currentActiveHwnd;
  }

  /**
   * InitializeActiveWindow（如果有 overlay 但未SetActiveWindow）
   * 在First次Create overlay 或收到Event时Auto调用
   */
  initializeActiveIfNeeded() {
    if (this._currentActiveHwnd === null && this._overlays.size > 0) {
      const firstHwnd = this.getActiveHwnds()[0];
      if (firstHwnd) {
        this.setActiveWindow(firstHwnd);
        this._currentActiveHwnd = firstHwnd;
        safeLog(`[MultiOverlay] Auto-initialized active window: ${firstHwnd}`);
      }
    }
  }

  /**
   * Allow的预览Class型List（Whitelist）
   * 
   * 扩展指南：New增预览Class型需SyncUpdate：
   * 1. 此处AddClass型名到 Set
   * 2. _generateOverlayHTML() MediumAdd ipcRenderer.on('preview:NewClass型', ...) Listen
   * 3. _generateOverlayHTML() MediumAdd对应的 create*Preview() Function
   * 4. agent-ipc.js handleToolEventForPreview() MediumAdd switch case
   * 
   * @see agent-ipc.js Bottom的"预览Class型Whitelist说明"Get完整维护指南
   */
  static ALLOWED_PREVIEW_TYPES = new Set([
    'mouse-trajectory',  // Mouse movement trajectory (dashed line)
    'click',             // Click ripple effect
    'typing',            // Input text preview
    'target',            // Target position indicator (pulse ring)
    'scroll',            // Scroll direction indicator
    'shortcut',          // Shortcut key display
    'window-action',     // Window action prompt (move/resize/close etc.)
    'clear',             // Clear all previews
  ]);

  /**
   * Send动作预览到Specify Overlay
   * @param {number} hwnd - TargetWindow句柄
   * @param {string} previewType - 预览Class型
   * @param {object} data - 预览数据
   */
  sendActionPreview(hwnd, previewType, data) {
    // Parameter validation: hwnd
    if (typeof hwnd !== 'number' || hwnd <= 0 || !Number.isInteger(hwnd)) {
      safeWarn(`[MultiOverlay] Invalid hwnd for preview: ${hwnd}`);
      return { success: false, error: 'Invalid hwnd: must be a positive integer' };
    }

    // Parameter validation: previewType
    if (typeof previewType !== 'string' || !MultiOverlayManager.ALLOWED_PREVIEW_TYPES.has(previewType)) {
      safeWarn(`[MultiOverlay] Invalid or disallowed preview type: ${previewType}`);
      return { success: false, error: `Invalid preview type: ${previewType}. Allowed: ${[...MultiOverlayManager.ALLOWED_PREVIEW_TYPES].join(', ')}` };
    }

    // Parameter validation: data
    if (data !== null && typeof data !== 'object') {
      safeWarn(`[MultiOverlay] Invalid preview data type: ${typeof data}`);
      return { success: false, error: 'Invalid data: must be an object or null' };
    }

    const instance = this._overlays.get(hwnd);
    if (!instance || !instance.isAlive()) {
      safeWarn(`[MultiOverlay] Cannot send preview, overlay not found: ${hwnd}`);
      return { success: false, error: 'Overlay not found', hwnd };
    }

    try {
      instance.window.webContents.send(`preview:${previewType}`, data);
      return { success: true };
    } catch (e) {
      safeError(`[MultiOverlay] Failed to send preview:`, e.message);
      return { success: false, error: e.message };
    }
  }

  /**
   * Clear所有动作预览
   */
  clearAllPreviews() {
    for (const [hwnd, instance] of this._overlays) {
      if (instance.isAlive()) {
        instance.window.webContents.send('preview:clear');
      }
    }
  }

  /**
   * GetSpecify Overlay 的State
   * @param {number} hwnd
   */
  getStatus(hwnd) {
    const instance = this._overlays.get(hwnd);
    if (!instance) {
      return { exists: false };
    }
    return {
      exists: true,
      hwnd: instance.hwnd,
      hookType: instance.hookType,
      state: instance.state,
      isAlive: instance.isAlive(),
    };
  }

  /**
   * Update Overlay State（Phase 8: DynamicStateDisplay）
   * 用于Display AI 正在做什么：Read、Write、Handle等
   * 
   * @param {number} hwnd - TargetWindow句柄
   * @param {object} state - StateObject
   * @param {string} state.status - StateClass型: 'idle' | 'reading' | 'writing' | 'processing' | 'error'
   * @param {string} [state.action] - 操作描述（如 "Reading page content..."）
   * @param {number} [state.progress] - 进度 0-100
   * @returns {{success: boolean, error?: string}}
   */
  updateOverlayState(hwnd, state) {
    const instance = this._overlays.get(hwnd);
    if (!instance || !instance.isAlive()) {
      safeWarn(`[MultiOverlay] Cannot update state, overlay not found: ${hwnd}`);
      return { success: false, error: 'Overlay not found' };
    }

    try {
      instance.window.webContents.send('state:update', {
        status: state.status || 'idle',
        action: state.action || '',
        progress: state.progress,
      });
      safeLog(`[MultiOverlay] State updated for HWND ${hwnd}: ${state.status}`);
      return { success: true };
    } catch (e) {
      safeError(`[MultiOverlay] Failed to update state:`, e.message);
      return { success: false, error: e.message };
    }
  }

  /**
   * Update所有 Overlay 的State
   * @param {object} state - StateObject
   */
  updateAllOverlayStates(state) {
    for (const [hwnd, instance] of this._overlays) {
      if (instance.isAlive()) {
        this.updateOverlayState(hwnd, state);
      }
    }
  }

  /**
   * 生成 Overlay HTML - NogicOS 深色风格（Premium版）
   * 设计理念：全Window入场冲击 → Low调常驻 | 顶级视觉品质
   * @private
   */
  _generateOverlayHTML(hookType, targetTitle) {
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
    
    /* ============== 全WindowBorder闪光（入场时） ============== */
    .border-flash {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      pointer-events: none;
      border: 3px solid rgba(16, 185, 129, 0);
      border-radius: 8px;
      animation: borderFlashIn 1.2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }
    
    @keyframes borderFlashIn {
      0% { 
        border-color: rgba(16, 185, 129, 0);
        box-shadow: 
          inset 0 0 0 rgba(16, 185, 129, 0),
          0 0 0 rgba(16, 185, 129, 0);
      }
      15% { 
        border-color: rgba(16, 185, 129, 0.8);
        box-shadow: 
          inset 0 0 60px rgba(16, 185, 129, 0.15),
          0 0 30px rgba(16, 185, 129, 0.5);
      }
      40% {
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 
          inset 0 0 30px rgba(16, 185, 129, 0.08),
          0 0 20px rgba(16, 185, 129, 0.3);
      }
      100% { 
        border-color: rgba(16, 185, 129, 0);
        box-shadow: 
          inset 0 0 0 rgba(16, 185, 129, 0),
          0 0 0 rgba(16, 185, 129, 0);
      }
    }
    
    /* ============== 四角 L 形标记（精确对齐 + 统一粗细） ============== */
    .corner {
      position: fixed;
      width: 24px;
      height: 24px;
      pointer-events: none;
    }
    
    .corner::before,
    .corner::after {
      content: '';
      position: absolute;
      background: #10b981;
      /* 统一粗细：3px */
    }
    
    /* LeftUp角 */
    .corner-tl { top: 0; left: 0; }
    .corner-tl::before { width: 24px; height: 3px; top: 0; left: 0; }
    .corner-tl::after { width: 3px; height: 24px; top: 0; left: 0; }
    
    /* RightUp角 */
    .corner-tr { top: 0; right: 0; }
    .corner-tr::before { width: 24px; height: 3px; top: 0; right: 0; }
    .corner-tr::after { width: 3px; height: 24px; top: 0; right: 0; }
    
    /* LeftDown角 */
    .corner-bl { bottom: 0; left: 0; }
    .corner-bl::before { width: 24px; height: 3px; bottom: 0; left: 0; }
    .corner-bl::after { width: 3px; height: 24px; bottom: 0; left: 0; }
    
    /* RightDown角 */
    .corner-br { bottom: 0; right: 0; }
    .corner-br::before { width: 24px; height: 3px; bottom: 0; right: 0; }
    .corner-br::after { width: 3px; height: 24px; bottom: 0; right: 0; }
    
    /* 四角入场Animation：依次闪亮 */
    .corner { opacity: 0; }
    .corner::before, .corner::after {
      box-shadow: 0 0 10px rgba(16, 185, 129, 0.8);
    }
    
    .corner-tl { animation: cornerFlash 1.5s ease-out 0.1s forwards; }
    .corner-tr { animation: cornerFlash 1.5s ease-out 0.2s forwards; }
    .corner-br { animation: cornerFlash 1.5s ease-out 0.3s forwards; }
    .corner-bl { animation: cornerFlash 1.5s ease-out 0.4s forwards; }
    
    @keyframes cornerFlash {
      0% { 
        opacity: 0; 
        transform: scale(0.5);
      }
      20% { 
        opacity: 1; 
        transform: scale(1.1);
      }
      40% {
        opacity: 1;
        transform: scale(1);
      }
      100% { 
        opacity: 0.3;  /* 常驻：微弱但Visible */
        transform: scale(1);
      }
    }
    
    /* 常驻时四角微弱发光 */
    .corner::before, .corner::after {
      transition: box-shadow 0.5s ease;
    }
    
    /* ============== 扫描线（入场强 + 常驻弱Loop） ============== */
    .scan-line {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 100%;
      pointer-events: none;
      background: linear-gradient(180deg,
        rgba(16, 185, 129, 0.4) 0%,
        rgba(16, 185, 129, 0.15) 1.5%,
        transparent 4%
      );
      opacity: 0;
      /* 入场强扫描 + 常驻弱Loop */
      animation: 
        scanFirst 0.8s ease-out 0.1s forwards,
        scanLoop 6s linear 2s infinite;
    }
    
    /* 入场：强烈的First次扫描 */
    @keyframes scanFirst {
      0% { 
        opacity: 1;
        transform: translateY(-100%);
      }
      100% { 
        opacity: 0;
        transform: translateY(100%);
      }
    }
    
    /* 常驻：微弱的Loop扫描 */
    @keyframes scanLoop {
      0% { 
        opacity: 0;
        transform: translateY(-100%);
      }
      5% {
        opacity: 0.15;
      }
      95% {
        opacity: 0.15;
      }
      100% { 
        opacity: 0;
        transform: translateY(100%);
      }
    }
    
    /* ============== TopState条 - Premium ============== */
    .overlay-container {
      position: fixed;
      top: 0;
      left: 50%;
      transform: translateX(-50%) translateY(-100%);
      width: 280px;
      height: 32px;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 14px;
      
      /* Premium 毛玻璃Background */
      background: 
        linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.1) 100%),
        rgba(8, 8, 8, 0.85);
      
      border: 1px solid transparent;
      border-top: none;
      border-radius: 0 0 12px 12px;
      
      /* High级毛玻璃 */
      backdrop-filter: blur(24px) saturate(180%);
      -webkit-backdrop-filter: blur(24px) saturate(180%);
      
      /* Premium 字体 */
      font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.2px;
      color: rgba(255, 255, 255, 0.95);
      
      /* 多层阴影 */
      box-shadow: 
        0 8px 32px rgba(16, 185, 129, 0.3),
        0 4px 16px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(16, 185, 129, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
      
      opacity: 0;
      
      /* Delayed入场，在Border闪光之After */
      animation: 
        barSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s forwards,
        barSettleDown 1s ease-out 2s forwards;
    }
    
    /* 渐变Border */
    .overlay-container::before {
      content: '';
      position: absolute;
      inset: -1px;
      border-radius: 0 0 13px 13px;
      padding: 1px;
      background: linear-gradient(180deg, 
        rgba(16, 185, 129, 0.6) 0%, 
        rgba(16, 185, 129, 0.2) 50%,
        rgba(16, 185, 129, 0.05) 100%
      );
      -webkit-mask: 
        linear-gradient(#fff 0 0) content-box, 
        linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      pointer-events: none;
      animation: borderFadeBar 1s ease-out 2s forwards;
    }
    
    @keyframes borderFadeBar {
      to {
        background: linear-gradient(180deg, 
          rgba(255, 255, 255, 0.1) 0%, 
          rgba(255, 255, 255, 0.03) 100%
        );
      }
    }
    
    @keyframes barSlideIn {
      0% { 
        transform: translateX(-50%) translateY(-100%) scale(0.9); 
        opacity: 0;
        filter: blur(4px);
      }
      60% { 
        transform: translateX(-50%) translateY(4px) scale(1.02); 
        opacity: 1;
        filter: blur(0);
      }
      100% { 
        transform: translateX(-50%) translateY(0) scale(1); 
        opacity: 1;
        filter: blur(0);
      }
    }
    
    /* 常驻：优雅Low调 */
    @keyframes barSettleDown {
      to {
        background: 
          linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(0, 0, 0, 0.1) 100%),
          rgba(12, 12, 12, 0.92);
        box-shadow: 
          0 4px 16px rgba(0, 0, 0, 0.4),
          0 0 0 1px rgba(255, 255, 255, 0.05),
          inset 0 1px 0 rgba(255, 255, 255, 0.08);
      }
    }
    
    /* 噪点纹理 */
    .overlay-container::after {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: 0 0 12px 12px;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)'/%3E%3C/svg%3E");
      opacity: 0.03;
      mix-blend-mode: overlay;
      pointer-events: none;
    }
    
    /* ============== State指示器 ============== */
    .status-indicator {
      position: relative;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: radial-gradient(circle at 30% 30%, #34d399 0%, #10b981 50%, #059669 100%);
      box-shadow: 
        0 0 0 2px rgba(16, 185, 129, 0.2),
        0 0 12px rgba(16, 185, 129, 0.8),
        0 0 24px rgba(16, 185, 129, 0.4);
      animation: 
        indicatorFlash 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.4s forwards,
        indicatorPulse 4s ease-in-out 2.5s infinite;
      transform: scale(0);
    }
    
    .status-indicator::after {
      content: '';
      position: absolute;
      top: 1px;
      left: 2px;
      width: 3px;
      height: 2px;
      background: rgba(255, 255, 255, 0.6);
      border-radius: 50%;
      filter: blur(0.5px);
    }
    
    @keyframes indicatorFlash {
      0% { transform: scale(0); }
      50% { 
        transform: scale(2);
        box-shadow: 
          0 0 0 4px rgba(16, 185, 129, 0.3),
          0 0 30px rgba(16, 185, 129, 1),
          0 0 60px rgba(16, 185, 129, 0.6);
      }
      100% { 
        transform: scale(1);
        box-shadow: 
          0 0 0 2px rgba(16, 185, 129, 0.15),
          0 0 8px rgba(16, 185, 129, 0.5);
      }
    }
    
    @keyframes indicatorPulse {
      0%, 100% { 
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1), 0 0 6px rgba(16, 185, 129, 0.4);
      }
      50% { 
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15), 0 0 10px rgba(16, 185, 129, 0.5);
      }
    }
    
    /* ============== Logo ============== */
    .logo-icon {
      width: 18px;
      height: 18px;
      border-radius: 5px;
      background: 
        linear-gradient(135deg, rgba(255,255,255,0.25) 0%, transparent 50%),
        linear-gradient(135deg, #34d399 0%, #10b981 50%, #059669 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-weight: 800;
      color: #fff;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
      box-shadow: 
        0 2px 4px rgba(0, 0, 0, 0.3),
        0 4px 8px rgba(16, 185, 129, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
      animation: logoFlash 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.35s forwards;
      transform: scale(0) rotate(-180deg);
    }
    
    @keyframes logoFlash {
      0% { transform: scale(0) rotate(-180deg); filter: brightness(0.5); }
      60% { transform: scale(1.2) rotate(10deg); filter: brightness(1.3); }
      100% { transform: scale(1) rotate(0deg); filter: brightness(1); }
    }
    
    /* ============== 其他元素 ============== */
    .divider {
      width: 1px;
      height: 14px;
      background: linear-gradient(180deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
      opacity: 0;
      animation: fadeIn 0.4s ease-out 0.5s forwards;
    }
    
    .label {
      font-weight: 600;
      font-size: 11px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      background: linear-gradient(90deg, #34d399 0%, #10b981 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      opacity: 0;
      animation: 
        labelIn 0.4s ease-out 0.45s forwards,
        labelSettle 1s ease-out 2s forwards;
    }
    
    @keyframes fadeIn { to { opacity: 1; } }
    @keyframes labelIn {
      0% { opacity: 0; transform: translateX(-8px); }
      100% { opacity: 1; transform: translateX(0); }
    }
    @keyframes labelSettle {
      to { 
        background: linear-gradient(90deg, rgba(52,211,153,0.7) 0%, rgba(16,185,129,0.6) 100%);
        -webkit-background-clip: text;
      }
    }
    
    .app-name {
      font-size: 10px;
      font-weight: 500;
      color: rgba(255, 255, 255, 0.5);
      max-width: 80px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      opacity: 0;
      animation: appIn 0.4s ease-out 0.55s forwards;
    }
    
    @keyframes appIn {
      0% { opacity: 0; transform: translateX(8px); }
      100% { opacity: 1; transform: translateX(0); }
    }
  </style>
</head>
<body>
  <!-- 全WindowBorder闪光 -->
  <div class="border-flash"></div>
  
  <!-- 扫描线Effect -->
  <div class="scan-line"></div>
  
  <!-- 四角 L 形标记 -->
  <div class="corner corner-tl"></div>
  <div class="corner corner-tr"></div>
  <div class="corner corner-bl"></div>
  <div class="corner corner-br"></div>
  
  <!-- TopState条 -->
  <div id="overlay" class="overlay-container">
    <div class="logo-icon">N</div>
    <div class="divider"></div>
    <div class="status-indicator"></div>
    <span class="label">Connected</span>
    <span class="app-name">${targetTitle || ''}</span>
  </div>
  
  <!-- Phase 7: 预览Effect容器 -->
  <div id="preview-container" style="position: fixed; inset: 0; pointer-events: none; z-index: 1000;"></div>
  
  <!-- Phase 7: 焦点StateStyle -->
  <style id="focus-styles">
    body.focus-active .corner::before,
    body.focus-active .corner::after {
      background: #00ff88 !important;
      box-shadow: 0 0 15px rgba(0, 255, 136, 0.8) !important;
    }
    body.focus-inactive {
      opacity: 0.5;
      filter: grayscale(0.3);
    }
    body.focus-inactive .corner::before,
    body.focus-inactive .corner::after {
      background: rgba(255, 255, 255, 0.3) !important;
      box-shadow: none !important;
    }
  </style>
  
  <script>
    // ============== Premium Sound Effects ==============
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    function playPremiumConnectSound() {
      const now = audioContext.currentTime;
      const frequencies = [880, 1108.73, 1318.51];
      
      frequencies.forEach((freq, i) => {
        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();
        const filter = audioContext.createBiquadFilter();
        
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(2000, now);
        filter.frequency.exponentialRampToValueAtTime(4000, now + 0.1);
        filter.Q.value = 1;
        
        osc.connect(filter);
        filter.connect(gain);
        gain.connect(audioContext.destination);
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq * 0.5, now);
        osc.frequency.exponentialRampToValueAtTime(freq, now + 0.08);
        
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.06 - i * 0.015, now + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
        
        osc.start(now + i * 0.03);
        osc.stop(now + 0.3);
      });
      
      const shimmer = audioContext.createOscillator();
      const shimmerGain = audioContext.createGain();
      shimmer.connect(shimmerGain);
      shimmerGain.connect(audioContext.destination);
      shimmer.type = 'triangle';
      shimmer.frequency.setValueAtTime(2637, now + 0.05);
      shimmerGain.gain.setValueAtTime(0.02, now + 0.05);
      shimmerGain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
      shimmer.start(now + 0.05);
      shimmer.stop(now + 0.25);
    }
    
    setTimeout(() => playPremiumConnectSound(), 180);
    
    // ============== Phase 7: Preview Rendering System ==============
    const previewContainer = document.getElementById('preview-container');
    let activeElements = [];
    
    // Clear all preview elements
    function clearPreviews() {
      activeElements.forEach(el => el.remove());
      activeElements = [];
    }
    
    // Create click indicator
    function createClickIndicator(x, y, type = 'click') {
      const el = document.createElement('div');
      el.className = 'preview-click';
      el.style.cssText = \`
        position: absolute;
        left: \${x}px;
        top: \${y}px;
        width: 40px;
        height: 40px;
        border: 2px solid #00ff88;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        animation: preview-ripple 0.5s ease-out forwards;
      \`;
      if (type === 'double-click') {
        el.style.animation = 'preview-double-ripple 0.6s ease-out forwards';
      } else if (type === 'right-click') {
        el.style.borderColor = '#f59e0b';
      }
      previewContainer.appendChild(el);
      activeElements.push(el);
      setTimeout(() => el.remove(), 600);
    }
    
    // Create target indicator
    function createTargetIndicator(x, y, label) {
      clearPreviews();
      const el = document.createElement('div');
      el.className = 'preview-target';
      el.innerHTML = \`
        <div class="target-ring"></div>
        <div class="target-label">\${label || 'Target'}</div>
      \`;
      el.style.cssText = \`
        position: absolute;
        left: \${x}px;
        top: \${y}px;
        transform: translate(-50%, -50%);
      \`;
      previewContainer.appendChild(el);
      activeElements.push(el);
    }
    
    // Create input preview
    function createTypingPreview(text, isPassword) {
      clearPreviews();
      const el = document.createElement('div');
      el.className = 'preview-typing';
      el.innerHTML = \`
        <span>\${isPassword ? '•'.repeat(Math.min(text.length, 20)) : text.substring(0, 50)}</span>
        <span class="cursor"></span>
      \`;
      el.style.cssText = \`
        position: fixed;
        bottom: 60px;
        left: 50%;
        transform: translateX(-50%);
        padding: 8px 16px;
        background: rgba(0, 0, 0, 0.9);
        border: 1px solid \${isPassword ? '#f59e0b' : 'rgba(255,255,255,0.2)'};
        border-radius: 8px;
        color: \${isPassword ? '#f59e0b' : 'white'};
        font-family: monospace;
        font-size: 14px;
      \`;
      previewContainer.appendChild(el);
      activeElements.push(el);
      setTimeout(() => el.remove(), 2000);
    }
    
    // Create shortcut preview
    function createShortcutPreview(shortcut) {
      clearPreviews();
      const keys = shortcut.split('+');
      const el = document.createElement('div');
      el.className = 'preview-shortcut';
      el.innerHTML = keys.map(k => \`<kbd>\${k}</kbd>\`).join('');
      el.style.cssText = \`
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 16px 32px;
        background: rgba(0, 0, 0, 0.95);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 12px;
        display: flex;
        gap: 8px;
        animation: preview-scale-in 0.2s ease-out;
      \`;
      previewContainer.appendChild(el);
      activeElements.push(el);
      setTimeout(() => el.remove(), 1000);
    }
    
    // Create scroll preview
    function createScrollPreview(direction, amount) {
      const el = document.createElement('div');
      el.className = 'preview-scroll';
      el.innerHTML = direction === 'up' ? '↑' : direction === 'down' ? '↓' : direction === 'left' ? '←' : '→';
      el.style.cssText = \`
        position: fixed;
        top: 50%;
        right: 20px;
        transform: translateY(-50%);
        width: 40px;
        height: 40px;
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #00ff88;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #00ff88;
        font-size: 20px;
        animation: preview-bounce 0.5s ease-out;
      \`;
      previewContainer.appendChild(el);
      activeElements.push(el);
      setTimeout(() => el.remove(), 500);
    }
    
    // Create mouse trajectory
    function createMouseTrajectory(from, to) {
      clearPreviews();
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.style.cssText = 'position: absolute; inset: 0; width: 100%; height: 100%;';
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', \`M\${from.x},\${from.y} L\${to.x},\${to.y}\`);
      path.setAttribute('stroke', 'rgba(0, 255, 136, 0.8)');
      path.setAttribute('stroke-width', '2');
      path.setAttribute('stroke-dasharray', '5,5');
      path.setAttribute('fill', 'none');
      path.style.animation = 'preview-dash 0.3s linear forwards';
      svg.appendChild(path);
      previewContainer.appendChild(svg);
      activeElements.push(svg);
      setTimeout(() => svg.remove(), 1000);
    }
    
    // Create window action prompt
    function createWindowActionPreview(action, label) {
      clearPreviews();
      const icons = {
        move: '↔',
        resize: '⤢',
        close: '✕',
        maximize: '⬜',
        minimize: '—',
        open: '📂',
        generic: '⚡'
      };
      const el = document.createElement('div');
      el.className = 'preview-window-action';
      el.innerHTML = \`<span class="icon">\${icons[action] || '⚡'}</span><span class="label">\${label}</span>\`;
      el.style.cssText = \`
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 16px 24px;
        background: rgba(0, 0, 0, 0.9);
        border: 1px solid #00ff88;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: white;
        font-size: 14px;
        animation: preview-scale-in 0.2s ease-out;
      \`;
      previewContainer.appendChild(el);
      activeElements.push(el);
      setTimeout(() => el.remove(), 1500);
    }
    
    // ============== IPC Event Listening (via secure contextBridge API) ==============
    // Use window.overlayAPI exposed by overlay-preload.js
    if (window.overlayAPI) {
      // Register all preview event handlers at once
      window.overlayAPI.onAllPreviews({
        click: (data) => {
          if (data?.x != null && data?.y != null) {
            createClickIndicator(data.x, data.y, data.type);
          }
        },
        target: (data) => {
          if (data?.x != null && data?.y != null) {
            createTargetIndicator(data.x, data.y, data.label);
          }
        },
        typing: (data) => {
          if (data?.text) {
            createTypingPreview(data.text, data.isPassword);
          }
        },
        shortcut: (data) => {
          if (data?.shortcut) {
            createShortcutPreview(data.shortcut);
          }
        },
        scroll: (data) => {
          createScrollPreview(data?.direction || 'down', data?.amount || 100);
        },
        mouseTrajectory: (data) => {
          if (data?.from && data?.to) {
            createMouseTrajectory(data.from, data.to);
          }
        },
        windowAction: (data) => {
          createWindowActionPreview(data?.action || 'generic', data?.label || 'Execute操作');
        },
        clear: () => {
          clearPreviews();
        },
      });
      
      // Focus management events
      window.overlayAPI.onFocus('focus:active', () => {
        document.body.classList.remove('focus-inactive');
        document.body.classList.add('focus-active');
      });
      
      window.overlayAPI.onFocus('focus:inactive', () => {
        document.body.classList.remove('focus-active');
        document.body.classList.add('focus-inactive');
      });
      
      // Phase 8: State update listening
      window.overlayAPI.onStateUpdate((state) => {
        const overlay = document.getElementById('overlay');
        const labelEl = overlay.querySelector('.label');
        const indicatorEl = overlay.querySelector('.status-indicator');
        
        // Update status text
        const statusText = {
          idle: 'Connected',
          reading: 'Reading',
          writing: 'Writing',
          processing: 'Processing',
          error: 'Error',
        }[state.status] || 'Connected';
        
        if (labelEl) {
          labelEl.textContent = statusText;
        }
        
        // Update indicator color and animation
        if (indicatorEl) {
          // Clear previous state classes
          indicatorEl.classList.remove('state-idle', 'state-reading', 'state-writing', 'state-processing', 'state-error');
          indicatorEl.classList.add('state-' + state.status);
        }
        
        // Update data flow animation
        let flowContainer = document.getElementById('data-flow');
        if (state.status === 'reading' || state.status === 'writing') {
          if (!flowContainer) {
            flowContainer = document.createElement('div');
            flowContainer.id = 'data-flow';
            flowContainer.className = 'data-flow-container';
            flowContainer.innerHTML = \`
              <div class="flow-particle" style="animation-delay: 0s;"></div>
              <div class="flow-particle" style="animation-delay: 0.2s;"></div>
              <div class="flow-particle" style="animation-delay: 0.4s;"></div>
            \`;
            overlay.appendChild(flowContainer);
          }
          flowContainer.className = 'data-flow-container ' + (state.status === 'reading' ? 'flow-in' : 'flow-out');
          flowContainer.style.display = 'flex';
        } else if (flowContainer) {
          flowContainer.style.display = 'none';
        }
        
        // Display action description
        let actionEl = document.getElementById('action-text');
        if (state.action) {
          if (!actionEl) {
            actionEl = document.createElement('span');
            actionEl.id = 'action-text';
            actionEl.className = 'action-text';
            overlay.appendChild(actionEl);
          }
          actionEl.textContent = state.action;
          actionEl.style.display = 'inline';
        } else if (actionEl) {
          actionEl.style.display = 'none';
        }
        
        safeLog('[Overlay] State updated:', state.status, state.action || '');
      });
      
      safeLog('[Overlay] IPC events registered via secure contextBridge');
    } else {
      safeWarn('[Overlay] overlayAPI not available - preload may have failed');
    }
  </script>
  
  <!-- Phase 8: DynamicStateStyle -->
  <style>
    /* 数据流动容器 */
    .data-flow-container {
      display: none;
      align-items: center;
      gap: 3px;
      margin-left: 8px;
      padding: 2px 6px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 4px;
    }
    
    .flow-particle {
      width: 4px;
      height: 4px;
      background: #34d399;
      border-radius: 50%;
      animation: flowMove 1s infinite;
    }
    
    .flow-in .flow-particle {
      animation-name: flowMoveIn;
    }
    
    .flow-out .flow-particle {
      background: #f59e0b;
      animation-name: flowMoveOut;
    }
    
    @keyframes flowMoveIn {
      0% { opacity: 0; transform: translateX(8px); }
      50% { opacity: 1; }
      100% { opacity: 0; transform: translateX(-8px); }
    }
    
    @keyframes flowMoveOut {
      0% { opacity: 0; transform: translateX(-8px); }
      50% { opacity: 1; }
      100% { opacity: 0; transform: translateX(8px); }
    }
    
    /* State指示器颜色变化 */
    .status-indicator.state-reading {
      background: radial-gradient(circle at 30% 30%, #34d399 0%, #10b981 50%, #059669 100%) !important;
      animation: indicatorPulse 0.6s ease-in-out infinite !important;
    }
    
    .status-indicator.state-writing {
      background: radial-gradient(circle at 30% 30%, #fbbf24 0%, #f59e0b 50%, #d97706 100%) !important;
      box-shadow: 0 0 12px rgba(245, 158, 11, 0.8) !important;
      animation: indicatorPulse 0.6s ease-in-out infinite !important;
    }
    
    .status-indicator.state-processing {
      background: radial-gradient(circle at 30% 30%, #60a5fa 0%, #3b82f6 50%, #2563eb 100%) !important;
      box-shadow: 0 0 12px rgba(59, 130, 246, 0.8) !important;
      animation: indicatorSpin 1s linear infinite !important;
    }
    
    .status-indicator.state-error {
      background: radial-gradient(circle at 30% 30%, #f87171 0%, #ef4444 50%, #dc2626 100%) !important;
      box-shadow: 0 0 12px rgba(239, 68, 68, 0.8) !important;
    }
    
    @keyframes indicatorSpin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    /* 操作文字 */
    .action-text {
      display: none;
      font-size: 10px;
      color: rgba(255, 255, 255, 0.6);
      margin-left: 8px;
      max-width: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  </style>
  
  <!-- Phase 7: 预览AnimationStyle -->
  <style>
    @keyframes preview-ripple {
      0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
      100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
    }
    @keyframes preview-double-ripple {
      0%, 50% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
      25% { transform: translate(-50%, -50%) scale(1.5); opacity: 0.5; }
      75% { transform: translate(-50%, -50%) scale(1.5); opacity: 0.5; }
      100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
    }
    @keyframes preview-scale-in {
      from { transform: translate(-50%, -50%) scale(0.8); opacity: 0; }
      to { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    }
    @keyframes preview-bounce {
      0%, 100% { transform: translateY(-50%); }
      50% { transform: translateY(-60%); }
    }
    @keyframes preview-dash {
      from { stroke-dashoffset: 100; }
      to { stroke-dashoffset: 0; }
    }
    .target-ring {
      width: 60px;
      height: 60px;
      border: 2px solid #00ff88;
      border-radius: 50%;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      animation: preview-pulse-ring 1.5s ease-out infinite;
    }
    @keyframes preview-pulse-ring {
      0% { transform: translate(-50%, -50%) scale(1); opacity: 0.8; }
      100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
    }
    .target-label {
      position: absolute;
      top: 40px;
      left: 50%;
      transform: translateX(-50%);
      padding: 4px 12px;
      background: rgba(0, 0, 0, 0.8);
      border: 1px solid #00ff88;
      border-radius: 4px;
      color: #00ff88;
      font-size: 12px;
      white-space: nowrap;
    }
    .preview-typing .cursor {
      display: inline-block;
      width: 2px;
      height: 1em;
      background: #00ff88;
      margin-left: 2px;
      animation: blink 0.8s step-end infinite;
    }
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }
    .preview-shortcut kbd {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 40px;
      height: 40px;
      padding: 0 12px;
      background: linear-gradient(180deg, #444, #333);
      border: 1px solid #555;
      border-radius: 6px;
      color: white;
      font-family: system-ui;
      font-size: 16px;
      font-weight: 500;
      box-shadow: 0 2px 0 #222;
    }
    .preview-window-action .icon {
      font-size: 24px;
    }
  </style>
</body>
</html>
    `;
  }
}

// ============== Singleton Management ==============
let multiOverlayManager = null;

function getMultiOverlayManager() {
  if (!multiOverlayManager) {
    multiOverlayManager = new MultiOverlayManager();
  }
  return multiOverlayManager;
}

// ============== IPC Handlers ==============
function setupMultiOverlayIPC() {
  const manager = getMultiOverlayManager();

  // Create Overlay
  ipcMain.handle('multi-overlay:create', async (event, { hwnd, hookType, targetTitle }) => {
    return manager.createOverlay(hwnd, hookType, targetTitle);
  });

  // Show Overlay
  ipcMain.handle('multi-overlay:show', async (event, { hwnd }) => {
    return manager.showOverlay(hwnd);
  });

  // Hide Overlay
  ipcMain.handle('multi-overlay:hide', async (event, { hwnd }) => {
    return manager.hideOverlay(hwnd);
  });

  // Destroy Overlay
  ipcMain.handle('multi-overlay:destroy', async (event, { hwnd }) => {
    return manager.destroyOverlay(hwnd);
  });

  // Destroy all
  ipcMain.handle('multi-overlay:destroy-all', async () => {
    return manager.destroyAll();
  });

  // Get status
  ipcMain.handle('multi-overlay:status', async (event, { hwnd }) => {
    return manager.getStatus(hwnd);
  });

  // Get all active HWNDs
  ipcMain.handle('multi-overlay:list', async () => {
    return { hwnds: manager.getActiveHwnds(), count: manager.activeCount };
  });

  // Phase 2: Start tracking
  ipcMain.handle('multi-overlay:start-tracking', async (event, { hwnd }) => {
    return manager.startTracking(hwnd);
  });

  // Phase 2: Stop tracking
  ipcMain.handle('multi-overlay:stop-tracking', async (event, { hwnd }) => {
    return manager.stopTracking(hwnd);
  });

  // Phase 7: Set active window (multi-window focus management)
  ipcMain.handle('multi-overlay:set-active', async (event, { hwnd }) => {
    manager.setActiveWindow(hwnd);
    return { success: true, activeHwnd: hwnd };
  });

  // Phase 7: Cycle through active windows
  ipcMain.handle('multi-overlay:cycle-active', async () => {
    const nextHwnd = manager.cycleActiveWindow();
    return { success: true, activeHwnd: nextHwnd };
  });

  // Phase 7: Send action preview (with parameter validation)
  ipcMain.handle('multi-overlay:preview', async (event, { hwnd, previewType, data }) => {
    // Basic validation done inside manager.sendActionPreview
    const result = manager.sendActionPreview(hwnd, previewType, data);
    
    // If failed, log to console (for debugging)
    if (!result.success) {
      safeWarn(`[IPC multi-overlay:preview] Failed:`, result.error);
    }
    
    return result;
  });

  // Phase 7: Clear all action previews
  ipcMain.handle('multi-overlay:clear-previews', async () => {
    manager.clearAllPreviews();
    return { success: true };
  });

  // Phase 8: Update Overlay state (dynamic state display)
  ipcMain.handle('multi-overlay:update-state', async (event, { hwnd, state }) => {
    return manager.updateOverlayState(hwnd, state);
  });

  // Phase 8: Update all Overlay states
  ipcMain.handle('multi-overlay:update-all-states', async (event, { state }) => {
    manager.updateAllOverlayStates(state);
    return { success: true };
  });

  safeLog('[MultiOverlayManager] IPC handlers registered (Phase 2 + Phase 7 + Phase 8)');
}

// ============== Export ==============
module.exports = {
  MultiOverlayManager,
  OverlayInstance,
  OverlayState,
  getMultiOverlayManager,
  setupMultiOverlayIPC,
};

