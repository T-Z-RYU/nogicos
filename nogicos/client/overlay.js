/**
 * NogicOS Overlay Manager
 * 
 * 在被 Hook 的应用UpDisplayState指示
 * Usage Electron Transparent置顶WindowImplement
 */

const { BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');

// Shared utilities
const { OVERLAY_CONFIG, generateBasicOverlayHTML } = require('./shared-overlay-utils');

// Windows API for window tracking
let user32 = null;
let kernel32 = null;

if (process.platform === 'win32') {
  try {
    const ffi = require('ffi-napi');
    const ref = require('ref-napi');
    
    user32 = ffi.Library('user32', {
      'GetForegroundWindow': ['pointer', []],
      'GetWindowRect': ['bool', ['pointer', 'pointer']],
      'GetWindowTextW': ['int', ['pointer', 'pointer', 'int']],
      'GetWindowTextLengthW': ['int', ['pointer']],
      'IsWindowVisible': ['bool', ['pointer']],
      'GetClassNameW': ['int', ['pointer', 'pointer', 'int']],
    });
  } catch (e) {
    console.log('[Overlay] ffi-napi not available, using polling fallback');
  }
}

// Note: OVERLAY_CONFIG is now imported from shared-overlay-utils.js

/**
 * Overlay Manager
 * 
 * Manages overlay windows for hooked applications
 */
class OverlayManager {
  constructor() {
    this._overlays = new Map();  // hwnd -> BrowserWindow
    this._updateIntervals = new Map();
    this._isRunning = false;
  }

  /**
   * Create overlay for a window
   * @param {number} hwnd - Target window handle
   * @param {string} label - Label to display (e.g., "NogicOS Connected")
   * @returns {BrowserWindow|null}
   */
  createOverlay(hwnd, label = 'NogicOS Connected') {
    if (this._overlays.has(hwnd)) {
      return this._overlays.get(hwnd);
    }

    // Get target window position
    const rect = this._getWindowRect(hwnd);
    if (!rect) {
      console.error('[Overlay] Could not get window rect for hwnd:', hwnd);
      return null;
    }

    // Create transparent overlay window
    const overlay = new BrowserWindow({
      x: rect.x,
      y: rect.y,
      width: rect.width,
      height: OVERLAY_CONFIG.height,
      transparent: true,
      frame: false,
      alwaysOnTop: true,
      skipTaskbar: true,
      focusable: false,
      hasShadow: false,
      resizable: false,
      movable: false,
      minimizable: false,
      maximizable: false,
      closable: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
      },
    });

    // Make click-through
    overlay.setIgnoreMouseEvents(true, { forward: true });

    // Load overlay content
    const html = this._generateOverlayHTML(label);
    overlay.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);

    // Store overlay
    this._overlays.set(hwnd, overlay);

    // Start position tracking
    this._startTracking(hwnd, overlay);

    console.log(`[Overlay] Created overlay for hwnd ${hwnd}`);
    return overlay;
  }

  /**
   * Remove overlay for a window
   * @param {number} hwnd - Target window handle
   */
  removeOverlay(hwnd) {
    const overlay = this._overlays.get(hwnd);
    if (overlay) {
      this._stopTracking(hwnd);
      
      try {
        overlay.close();
      } catch (e) {
        // Window might already be destroyed
      }
      
      this._overlays.delete(hwnd);
      console.log(`[Overlay] Removed overlay for hwnd ${hwnd}`);
    }
  }

  /**
   * Remove all overlays
   */
  removeAllOverlays() {
    for (const hwnd of this._overlays.keys()) {
      this.removeOverlay(hwnd);
    }
  }

  /**
   * Update overlay label
   * @param {number} hwnd - Target window handle
   * @param {string} label - New label
   */
  updateLabel(hwnd, label) {
    const overlay = this._overlays.get(hwnd);
    if (overlay) {
      const html = this._generateOverlayHTML(label);
      overlay.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    }
  }

  /**
   * Get window rectangle (Windows only)
   * @param {number} hwnd - Window handle
   * @returns {{x: number, y: number, width: number, height: number}|null}
   */
  _getWindowRect(hwnd) {
    if (process.platform === 'win32' && user32) {
      try {
        const ref = require('ref-napi');
        const Struct = require('ref-struct-napi');
        
        const RECT = Struct({
          left: ref.types.int32,
          top: ref.types.int32,
          right: ref.types.int32,
          bottom: ref.types.int32,
        });
        
        const rect = new RECT();
        const hwndPtr = ref.alloc('pointer', hwnd);
        
        if (user32.GetWindowRect(hwndPtr, rect.ref())) {
          return {
            x: rect.left,
            y: rect.top,
            width: rect.right - rect.left,
            height: rect.bottom - rect.top,
          };
        }
      } catch (e) {
        console.error('[Overlay] GetWindowRect failed:', e);
      }
    }
    
    return null;
  }

  /**
   * Start tracking window position
   * @param {number} hwnd - Window handle
   * @param {BrowserWindow} overlay - Overlay window
   */
  _startTracking(hwnd, overlay) {
    if (this._updateIntervals.has(hwnd)) {
      return;
    }

    const interval = setInterval(() => {
      const rect = this._getWindowRect(hwnd);
      
      if (rect) {
        try {
          // Update overlay position to match target window
          overlay.setBounds({
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: OVERLAY_CONFIG.height,
          });
        } catch (e) {
          // Overlay window might be destroyed
          this._stopTracking(hwnd);
        }
      } else {
        // Target window might be closed/minimized
        // Keep overlay but hide it
        try {
          overlay.hide();
        } catch (e) {
          this._stopTracking(hwnd);
        }
      }
    }, OVERLAY_CONFIG.updateInterval);

    this._updateIntervals.set(hwnd, interval);
  }

  /**
   * Stop tracking window position
   * @param {number} hwnd - Window handle
   */
  _stopTracking(hwnd) {
    const interval = this._updateIntervals.get(hwnd);
    if (interval) {
      clearInterval(interval);
      this._updateIntervals.delete(hwnd);
    }
  }

  /**
   * Generate overlay HTML content
   * @param {string} label - Label text
   * @returns {string}
   */
  _generateOverlayHTML(label) {
    // Use shared utility for HTML generation
    return generateBasicOverlayHTML(label);
  }
}

// Singleton instance
let overlayManager = null;

/**
 * Get OverlayManager singleton
 * @returns {OverlayManager}
 */
function getOverlayManager() {
  if (!overlayManager) {
    overlayManager = new OverlayManager();
  }
  return overlayManager;
}

/**
 * Setup IPC handlers for overlay control
 * @param {Electron.IpcMain} ipc
 */
function setupOverlayIPC(ipc = ipcMain) {
  // Create overlay
  ipc.handle('overlay:create', async (event, { hwnd, label }) => {
    const manager = getOverlayManager();
    const overlay = manager.createOverlay(hwnd, label);
    return { success: !!overlay };
  });

  // Remove overlay
  ipc.handle('overlay:remove', async (event, { hwnd }) => {
    const manager = getOverlayManager();
    manager.removeOverlay(hwnd);
    return { success: true };
  });

  // Remove all overlays
  ipc.handle('overlay:removeAll', async () => {
    const manager = getOverlayManager();
    manager.removeAllOverlays();
    return { success: true };
  });

  // Update label
  ipc.handle('overlay:updateLabel', async (event, { hwnd, label }) => {
    const manager = getOverlayManager();
    manager.updateLabel(hwnd, label);
    return { success: true };
  });
}

module.exports = {
  OverlayManager,
  getOverlayManager,
  setupOverlayIPC,
  OVERLAY_CONFIG,
};

