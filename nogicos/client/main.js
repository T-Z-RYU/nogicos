/**
 * NogicOS Desktop Client
 * 
 * Load nogicos-ui React Before端作为桌面应用
 * 支持On发模式（Vite dev server）和Production模式（dist File）
 * 
 * Features:
 * - Global快捷键唤醒 (Cmd/Ctrl+Space)
 * - System托盘
 * - 单InstanceLock定
 * - WindowState记忆
 */

const { app, BrowserWindow, ipcMain, globalShortcut, Tray, Menu, nativeImage, session } = require('electron');
const path = require('path');
const fs = require('fs');

// Overlay Manager (new version - using electron-overlay-window)
let overlayController = null;
try {
  overlayController = require('./overlay-controller');
  console.log('[Main] OverlayController loaded');
} catch (e) {
  console.log('[Main] OverlayController not available:', e.message);
}

// Legacy Overlay (compatibility)
let overlayModule = null;
try {
  overlayModule = require('./overlay');
} catch (e) {
  // Legacy optional
}

// Drag connector module
let dragConnector = null;
try {
  dragConnector = require('./drag-connector');
  console.log('[Main] DragConnector loaded');
} catch (e) {
  console.log('[Main] DragConnector not available:', e.message);
}

// Multi-window Overlay Manager (new version)
let multiOverlayManager = null;
try {
  multiOverlayManager = require('./multi-overlay-manager');
  console.log('[Main] MultiOverlayManager loaded');
} catch (e) {
  console.log('[Main] MultiOverlayManager not available:', e.message);
}

// Phase 7: Agent IPC Handlers
let agentIpc = null;
let agentIpcController = null;
try {
  agentIpc = require('./agent-ipc');
  console.log('[Main] Agent IPC module loaded');
} catch (e) {
  console.log('[Main] Agent IPC module not available:', e.message);
}

// Phase 7: CSP Configuration
let cspConfig = null;
try {
  cspConfig = require('./csp-config');
  console.log('[Main] CSP config module loaded');
} catch (e) {
  console.log('[Main] CSP config module not available:', e.message);
}

// Phase 7: Overlay Action Preview
let overlayActionPreview = null;
try {
  overlayActionPreview = require('./overlay-action-preview');
  console.log('[Main] Overlay Action Preview module loaded');
} catch (e) {
  console.log('[Main] Overlay Action Preview module not available:', e.message);
}

// Config
const DEV_SERVER_URL = process.env.DEV_SERVER_URL || 'http://localhost:5173';
const IS_DEV = process.env.NODE_ENV === 'development' || !app.isPackaged;
const CONFIG_PATH = path.join(app.getPath('userData'), 'window-state.json');

let mainWindow = null;
let tray = null; // Must be global variable, otherwise will be GC'd

// ============== Single Instance Lock ==============
const gotLock = app.requestSingleInstanceLock();

if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    // When second instance starts, focus existing window
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// ============== Window State Memory ==============
function loadWindowState() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    }
  } catch (e) {
    // Silently ignore load errors
  }
  return { width: 1400, height: 900 };
}

function saveWindowState() {
  if (!mainWindow) return;
  try {
    const bounds = mainWindow.getBounds();
    const isMaximized = mainWindow.isMaximized();
    fs.writeFileSync(CONFIG_PATH, JSON.stringify({ ...bounds, isMaximized }));
  } catch (e) {
    // Silently ignore save errors
  }
}

// ============== Node.js Version Check ==============
function checkNodeVersion() {
  const [major] = process.versions.node.split('.').map(Number);
  const MIN_NODE_VERSION = 18;
  if (major < MIN_NODE_VERSION) {
    console.error(`[Main] Node.js ${MIN_NODE_VERSION}+ required, found ${process.versions.node}`);
    return false;
  }
  return true;
}

// Check Node.js version at startup
if (!checkNodeVersion()) {
  app.quit();
}

// ============== Check Dev Server ==============
async function checkDevServer() {
  try {
    const response = await fetch(DEV_SERVER_URL, { method: 'HEAD' });
    return response.ok;
  } catch {
    return false;
  }
}

// ============== Create Tray Icon ==============
function createTray() {
  // Try to load custom icon, use default if not found
  const iconPath = path.join(__dirname, 'assets', 'tray-icon.png');
  if (fs.existsSync(iconPath)) {
    tray = new Tray(iconPath);
  } else {
    // Create a simple icon
    tray = new Tray(nativeImage.createFromDataURL(
      'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAABhSURBVDiNY2AYBaNgGAAGBgaG/1D8H4ofMDAwSFCi+T8U/4fi/wwMDEzkanZiYGD4D8X/GRgYJBkYGP5TMgZNLzoYLIb8p8CAQWkI/KPAgEEdAsOGqiEwbKgaAsOGqiEDAACiHRH0tC9lSgAAAABJRU5ErkJggg=='
    ));
  }

  const contextMenu = Menu.buildFromTemplate([
    { 
      label: 'Show NogicOS', 
      click: () => {
        mainWindow?.show();
        mainWindow?.focus();
      }
    },
    { 
      label: 'New Session', 
      click: () => {
        mainWindow?.show();
        mainWindow?.focus();
        mainWindow?.webContents.send('new-session');
      }
    },
    { type: 'separator' },
    { 
      label: 'Quit', 
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('NogicOS - AI Desktop Assistant');
  tray.setContextMenu(contextMenu);

  // Click tray icon to toggle show/hide
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });

}

// ============== Register Global Shortcuts ==============
function registerGlobalShortcuts() {
  // Alt+N: Wake/hide window (N for NogicOS, avoids conflict with IME switch Ctrl+Space)
  const toggleRegistered = globalShortcut.register('Alt+N', () => {
    if (mainWindow) {
      if (mainWindow.isVisible() && mainWindow.isFocused()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });

  // Alt+N registered (or failed if in use)

  // Cmd/Ctrl+Shift+N: New session
  const newSessionRegistered = globalShortcut.register('CommandOrControl+Shift+N', () => {
    mainWindow?.show();
    mainWindow?.focus();
    mainWindow?.webContents.send('new-session');
  });

}

// ============== Create Main Window ==============
async function createWindow() {
  const windowState = loadWindowState();

  mainWindow = new BrowserWindow({
    width: windowState.width,
    height: windowState.height,
    x: windowState.x,
    y: windowState.y,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
    titleBarStyle: 'hidden',
    frame: false,
    backgroundColor: '#0a0a0a',
    show: false,
  });

  // Restore maximized state
  if (windowState.isMaximized) {
    mainWindow.maximize();
  }

  // Show window elegantly
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Load UI
  if (IS_DEV) {
    const devServerRunning = await checkDevServer();
    
    if (devServerRunning) {
      mainWindow.loadURL(DEV_SERVER_URL);
      
      // DevTools: Use F12 or Ctrl+Shift+I to open manually
      // mainWindow.webContents.openDevTools();
    } else {
      loadFromDist();
    }
  } else {
    loadFromDist();
  }

  // Universal shortcut support (works in both dev and prod modes)
  mainWindow.webContents.on('before-input-event', (event, input) => {
    // F12 or Ctrl+Shift+I to open DevTools
    if (input.key === 'F12' || 
        (input.control && input.shift && input.key.toLowerCase() === 'i')) {
      mainWindow.webContents.toggleDevTools();
    }
    // F5 or Ctrl+R to refresh page
    if (input.key === 'F5' || 
        (input.control && !input.shift && input.key.toLowerCase() === 'r')) {
      mainWindow.webContents.reload();
      event.preventDefault();
    }
    // Ctrl+Shift+R force refresh (clear cache)
    if (input.control && input.shift && input.key.toLowerCase() === 'r') {
      mainWindow.webContents.reloadIgnoringCache();
      event.preventDefault();
    }
  });

  // Hide to tray instead of quit when closed
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  // Save window state
  mainWindow.on('resize', saveWindowState);
  mainWindow.on('move', saveWindowState);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Load from build files
function loadFromDist() {
  const distPath = path.join(__dirname, '..', 'nogicos-ui', 'dist', 'index.html');
  mainWindow.loadFile(distPath);
}

// ============== IPC Handlers ==============
ipcMain.on('window-minimize', () => {
  mainWindow?.minimize();
});

ipcMain.on('window-maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});

ipcMain.on('window-close', () => {
  mainWindow?.hide(); // Hide instead of close
});

// New: Toggle command palette
ipcMain.on('toggle-command-palette', () => {
  mainWindow?.webContents.send('toggle-command-palette');
});

// ============== App Lifecycle ==============

// [P0 FIX Round 1] IPC sender validation helper
function isValidSender(event) {
  return event.sender === mainWindow?.webContents;
}

app.whenReady().then(() => {
  // [Phase 7] Use unified CSP config module
  if (cspConfig) {
    if (IS_DEV) {
      // Dev mode: Use relaxed CSP (allow HMR)
      cspConfig.setupDevCSP();
      console.log('[Main] Development CSP configured');
    } else {
      // Prod mode: Use strict CSP + security headers
      cspConfig.setupAllSecurity();
      console.log('[Main] Production security configured');
    }
  } else {
    // Fallback: Use legacy CSP config
    session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
      callback({
        responseHeaders: {
          ...details.responseHeaders,
          'Content-Security-Policy': [
            "default-src 'self'; " +
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; " +
            "style-src 'self' 'unsafe-inline'; " +
            "img-src 'self' data: https: blob:; " +
            "font-src 'self' data:; " +
            "connect-src 'self' ws://localhost:* http://localhost:* https:; " +
            "frame-src 'none';"
          ]
        }
      });
    });
    console.log('[Main] Legacy CSP configured (fallback)');
  }

  createWindow();
  createTray();
  registerGlobalShortcuts();
  
  // ============== New Overlay (electron-overlay-window) ==============
  if (overlayController && overlayController.setupOverlayIPC) {
    overlayController.setupOverlayIPC();
    console.log('[Main] New OverlayController IPC handlers registered');
  }
  
  // Setup old overlay IPC handlers (fallback)
  if (overlayModule && overlayModule.setupOverlayIPC) {
    overlayModule.setupOverlayIPC(ipcMain);
    console.log('[Main] Legacy Overlay IPC handlers registered');
  }
  
  // Setup drag connector IPC handlers
  // [Fix #3] Ensure mainWindow is initialized
  if (dragConnector && dragConnector.setupDragConnectorIPC && mainWindow) {
    dragConnector.setupDragConnectorIPC(mainWindow);
    console.log('[Main] DragConnector IPC handlers registered');
  } else if (dragConnector && dragConnector.setupDragConnectorIPC) {
    console.warn('[Main] DragConnector IPC handlers deferred - mainWindow not ready');
  }
  
  // Setup multi-overlay manager IPC handlers (new multi-window Overlay)
  if (multiOverlayManager && multiOverlayManager.setupMultiOverlayIPC) {
    multiOverlayManager.setupMultiOverlayIPC();
    console.log('[Main] MultiOverlayManager IPC handlers registered');
  }
  
  // [Phase 7] Setup Agent IPC handlers
  if (agentIpc && agentIpc.registerAgentIpcHandlers && mainWindow) {
    // Get MultiOverlayManager instance for action preview
    const overlayManager = multiOverlayManager?.getMultiOverlayManager?.() || null;
    agentIpcController = agentIpc.registerAgentIpcHandlers(mainWindow, {
      multiOverlayManager: overlayManager,
    });
    console.log('[Main] Agent IPC handlers registered (with overlay preview support)');
  } else if (agentIpc && agentIpc.registerAgentIpcHandlers) {
    console.warn('[Main] Agent IPC handlers deferred - mainWindow not ready');
  }
  
  // ============== Connection Status Overlay / Notification ==============
  ipcMain.handle('overlay:show-connection', async (event, { hookType, target, targetHwnd }) => {
    // [P0 FIX Round 1] Validate IPC sender
    if (!isValidSender(event)) {
      console.warn('[Main] Unauthorized IPC call to overlay:show-connection');
      return { success: false, error: 'Unauthorized' };
    }

    // [P0 FIX Round 1] Validate parameters
    const validHookTypes = ['browser', 'desktop', 'file', 'terminal'];
    if (!validHookTypes.includes(hookType)) {
      console.warn(`[Main] Invalid hookType: ${hookType}`);
      return { success: false, error: 'Invalid hook type' };
    }
    if (typeof target !== 'string' || target.length > 256) {
      console.warn('[Main] Invalid target parameter');
      return { success: false, error: 'Invalid target' };
    }

    console.log(`[Main] Show connection: ${hookType} -> ${target} (HWND: ${targetHwnd})`);

    let overlayResult = { success: false };
    
    // [Core] Call OverlayController to show Overlay
    if (overlayController) {
      const manager = overlayController.getOverlayManager();
      if (manager.isAvailable && target) {
        console.log(`[Main] Calling OverlayManager.attach("${target}", "${hookType}")`);
        overlayResult = manager.attach(target, hookType);
        console.log(`[Main] OverlayManager.attach result:`, overlayResult);
      } else {
        console.log(`[Main] OverlayManager not available or no target`);
      }
    }
    
    // Fallback: System notification (if Overlay unavailable)
    if (!overlayResult.success) {
      const { Notification } = require('electron');
      if (Notification.isSupported()) {
        const notification = new Notification({
          title: '✅ NogicOS Connected',
          body: `Now monitoring: ${hookType}\n${target || 'system'}`,
          silent: false,
          urgency: 'normal',
        });
        notification.show();
        console.log(`[Main] Fallback: System notification shown for ${hookType}`);
      }
    }
    
    // Flash taskbar icon
    if (mainWindow && !mainWindow.isFocused()) {
      mainWindow.flashFrame(true);
      setTimeout(() => mainWindow.flashFrame(false), 2000);
    }
    
    return { success: true, method: overlayResult.success ? 'overlay' : 'notification', target };
  });
  
  ipcMain.handle('overlay:hide-connection', async (event, { hookType }) => {
    console.log(`[Main] Hide connection overlay: ${hookType}`);
    
    // New overlay
    if (overlayController) {
      const manager = overlayController.getOverlayManager();
      manager.detach();
    }
    
    // Legacy overlay
    if (overlayModule) {
      try {
        const manager = overlayModule.getOverlayManager();
        manager.removeAllOverlays();
      } catch (e) {}
    }
    return { success: true };
  });
  
  ipcMain.handle('notification:show', async (event, { title, body }) => {
    const { Notification } = require('electron');
    if (Notification.isSupported()) {
      new Notification({ title, body, silent: true }).show();
    }
    return { success: true };
  });
});

// Cleanup before exit
app.on('will-quit', () => {
  // Unregister all global shortcuts
  globalShortcut.unregisterAll();
  
  // [Phase 7] Clean up Agent IPC resources
  if (agentIpcController && agentIpcController.cleanup) {
    agentIpcController.cleanup();
    console.log('[Main] Agent IPC resources cleaned up');
  }
  if (agentIpc && agentIpc.unregisterAgentIpcHandlers) {
    agentIpc.unregisterAgentIpcHandlers();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
});

// macOS: Show window when dock icon clicked
app.on('activate', () => {
  if (mainWindow) {
    mainWindow.show();
  } else {
    createWindow();
  }
});

// Don't quit when all windows closed (because of tray)
app.on('window-all-closed', () => {
  // Don't quit, stay in tray
});
