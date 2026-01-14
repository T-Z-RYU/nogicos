/**
 * Drag Connector - 拖拽Connect器Module
 * 
 * Implement拖拽Connect器功能：
 * 1. Create全屏Transparent Overlay
 * 2. 追踪鼠标Position，Get鼠标Down的Window
 * 3. High亮TargetWindow
 * 4. 松On时ReturnTargetWindowInfo
 */

const { BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');

// Safe console.log to avoid EPIPE errors when stdout is closed
const safeLog = (...args) => {
  try {
    console.log(...args);
  } catch (e) {
    // Ignore EPIPE errors
  }
};

let dragOverlayWindow = null;
let isActive = false;
let targetWindowInfo = null;
let pollInterval = null;

// Windows API（through koffi）
let koffi = null;
let user32 = null;
let WindowFromPoint = null;
let GetWindowTextW = null;
let GetWindowRect = null;
let GetCursorPos = null;
let GetAsyncKeyState = null;
let GetAncestor = null;

// Constant
const VK_LBUTTON = 0x01; // MouseLeftKey
const GA_ROOT = 2; // GetAncestor: GetRootWindow

try {
  koffi = require('koffi');
  user32 = koffi.load('user32.dll');
  
  // defineClasstype
  const POINT = koffi.struct('POINT', {
    x: 'long',
    y: 'long',
  });
  
  const RECT = koffi.struct('RECT', {
    left: 'long',
    top: 'long',
    right: 'long',
    bottom: 'long',
  });
  
  // bindFunction
  // Note：use 'int' replace 'void*' toGetnumberValueClasstype's  HWND
  WindowFromPoint = user32.func('WindowFromPoint', 'int', [POINT]);
  GetWindowTextW = user32.func('GetWindowTextW', 'int', ['int', 'str16', 'int']);
  GetWindowRect = user32.func('GetWindowRect', 'bool', ['int', koffi.out(koffi.pointer(RECT))]);
  GetCursorPos = user32.func('GetCursorPos', 'bool', [koffi.out(koffi.pointer(POINT))]);
  GetAsyncKeyState = user32.func('GetAsyncKeyState', 'short', ['int']);
  GetAncestor = user32.func('GetAncestor', 'int', ['int', 'uint']);
  
  safeLog('[DragConnector] koffi loaded, Windows API available');
} catch (e) {
  safeLog('[DragConnector] koffi not available:', e.message);
}

/**
 * 检测鼠标Left键YesNo按Down
 */
function isMouseButtonDown() {
  if (!GetAsyncKeyState) return true; // If API notAvailable，FalsesetbyDown
  try {
    const state = GetAsyncKeyState(VK_LBUTTON);
    // IfmostHighbitfor 1，TableshowbyKeywhenBeforebebyDown
    return (state & 0x8000) !== 0;
  } catch (e) {
    return true;
  }
}

// GetallDisplayer's totalSize（forFilter）
function getTotalScreenSize() {
  const displays = screen.getAllDisplays();
  let totalWidth = 0, totalHeight = 0;
  for (const d of displays) {
    totalWidth += d.bounds.width;
    totalHeight = Math.max(totalHeight, d.bounds.height);
  }
  return { totalWidth, totalHeight };
}

/**
 * Get鼠标PositionDown的WindowInfo
 */
function getWindowUnderCursor() {
  if (!WindowFromPoint || !GetCursorPos) {
    return null;
  }
  
  try {
    // GetMousePosition
    const point = { x: 0, y: 0 };
    GetCursorPos(point);
    
    // GetthisPosition's Windowhandle
    let hwnd = WindowFromPoint(point);
    if (!hwnd || hwnd === 0) return null;
    
    // GetRootWindow（avoidGettoChildWindowlike "Chrome Legacy Window"）
    if (GetAncestor) {
      const rootHwnd = GetAncestor(hwnd, GA_ROOT);
      if (rootHwnd && rootHwnd !== 0) {
        hwnd = rootHwnd;
      }
    }
    
    // GetWindowtitle
    const buffer = Buffer.alloc(512);
    const length = GetWindowTextW(hwnd, buffer, 256);
    const title = buffer.toString('utf16le', 0, length * 2);
    
    if (!title || title.length < 2) return null;
    
    // GetWindowPosition
    const rect = { left: 0, top: 0, right: 0, bottom: 0 };
    GetWindowRect(hwnd, rect);
    
    const width = rect.right - rect.left;
    const height = rect.bottom - rect.top;
    
    // Filterdrop obviousnotYesApplyWindow's Window
    const { totalWidth, totalHeight } = getTotalScreenSize();
    
    // exclude：OverrideentireScreen's Window（maybeYesdesktoporHideWindow）
    if (width >= totalWidth * 0.95 && height >= totalHeight * 0.95) {
      return null;
    }
    
    // exclude：tooSmall's Window
    if (width < 100 || height < 50) {
      return null;
    }
    
    // exclude：SystemWindow
    const lowerTitle = title.toLowerCase();
    if (lowerTitle === 'program manager' || 
        lowerTitle.includes('taskbar') ||
        lowerTitle.includes('start menu')) {
      return null;
    }
    
    return {
      hwnd: hwnd,
      title,
      x: rect.left,
      y: rect.top,
      width: width,
      height: height,
      cursorX: point.x,
      cursorY: point.y,
    };
  } catch (e) {
    console.error('[DragConnector] Error getting window:', e);
    return null;
  }
}

// whenBefore overlay Override's Displayer
let currentDisplay = null;

/**
 * Create或Update拖拽 Overlay Window（Dynamic跟随鼠标所在的Display器）
 */
function createDragOverlay() {
  // GetMouseplacein's Displayer
  const cursorPoint = screen.getCursorScreenPoint();
  const display = screen.getDisplayNearestPoint(cursorPoint);
  
  // IfalreadyhaveWindowandinsameDisplayer，directlyReturn
  if (dragOverlayWindow && !dragOverlayWindow.isDestroyed() && currentDisplay === display.id) {
    return dragOverlayWindow;
  }
  
  // IfSwitchDisplayer，DestroyOldWindow
  if (dragOverlayWindow && !dragOverlayWindow.isDestroyed()) {
    dragOverlayWindow.close();
    dragOverlayWindow = null;
  }
  
  currentDisplay = display.id;
  
  // UsageDisplayer's Boundary（logicPixel）
  const { x, y, width, height } = display.bounds;
  
  safeLog('[DragConnector] Creating overlay on display:', {
    id: display.id,
    bounds: display.bounds,
    scaleFactor: display.scaleFactor,
  });
  
  dragOverlayWindow = new BrowserWindow({
    x: x,
    y: y,
    width: width,
    height: height,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    focusable: false,
    resizable: false,
    movable: false,
    hasShadow: false,
    type: 'toolbar',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });
  
  // Setformosttoplayer
  dragOverlayWindow.setAlwaysOnTop(true, 'screen-saver');
  
  // AllowMousepenetrate
  dragOverlayWindow.setIgnoreMouseEvents(true);
  
  // Load Overlay Innercontent
  dragOverlayWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(generateOverlayHTML())}`);
  
  return dragOverlayWindow;
}

/**
 * 生成 Overlay HTML - Premium 视觉Effect
 */
function generateOverlayHTML() {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body { 
      background: rgba(0, 0, 0, 0.6); 
      overflow: hidden; 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
      backdrop-filter: blur(2px);
    }
    
    /* ============== 扫描线BackgroundEffect ============== */
    .scan-effect {
      position: fixed;
      inset: 0;
      background: 
        repeating-linear-gradient(
          0deg,
          transparent,
          transparent 2px,
          rgba(16, 185, 129, 0.03) 2px,
          rgba(16, 185, 129, 0.03) 4px
        );
      pointer-events: none;
      animation: scanMove 8s linear infinite;
    }
    
    @keyframes scanMove {
      0% { transform: translateY(0); }
      100% { transform: translateY(100px); }
    }
    
    /* ============== High亮框 - Premium Style ============== */
    #highlight {
      position: fixed;
      pointer-events: none;
      display: none;
      /* 不Usage border，用伪元素做角标 */
    }
    
    /* 四角 L 形标记 */
    .corner {
      position: absolute;
      width: 32px;
      height: 32px;
      pointer-events: none;
    }
    .corner::before, .corner::after {
      content: '';
      position: absolute;
      background: #10b981;
      box-shadow: 0 0 12px rgba(16, 185, 129, 0.8), 0 0 24px rgba(16, 185, 129, 0.4);
    }
    .corner::before { height: 4px; width: 32px; }
    .corner::after { width: 4px; height: 32px; }
    
    .corner-tl { top: 0; left: 0; }
    .corner-tl::before { top: 0; left: 0; }
    .corner-tl::after { top: 0; left: 0; }
    
    .corner-tr { top: 0; right: 0; }
    .corner-tr::before { top: 0; right: 0; }
    .corner-tr::after { top: 0; right: 0; }
    
    .corner-bl { bottom: 0; left: 0; }
    .corner-bl::before { bottom: 0; left: 0; }
    .corner-bl::after { bottom: 0; left: 0; }
    
    .corner-br { bottom: 0; right: 0; }
    .corner-br::before { bottom: 0; right: 0; }
    .corner-br::after { bottom: 0; right: 0; }
    
    /* Border发光Effect */
    .glow-border {
      position: absolute;
      inset: 0;
      border: 2px solid rgba(16, 185, 129, 0.4);
      border-radius: 8px;
      box-shadow: 
        inset 0 0 30px rgba(16, 185, 129, 0.1),
        0 0 20px rgba(16, 185, 129, 0.3);
      animation: borderPulse 2s ease-in-out infinite;
    }
    
    @keyframes borderPulse {
      0%, 100% { opacity: 0.6; box-shadow: inset 0 0 30px rgba(16, 185, 129, 0.1), 0 0 20px rgba(16, 185, 129, 0.3); }
      50% { opacity: 1; box-shadow: inset 0 0 40px rgba(16, 185, 129, 0.15), 0 0 40px rgba(16, 185, 129, 0.5); }
    }
    
    /* 扫描线Animation */
    .highlight-scan {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, transparent, #10b981, transparent);
      box-shadow: 0 0 20px #10b981;
      animation: highlightScan 1.5s ease-in-out infinite;
    }
    
    @keyframes highlightScan {
      0% { top: 0; opacity: 1; }
      100% { top: 100%; opacity: 0.3; }
    }
    
    /* ============== 光标Graph标 - Premium ============== */
    #cursor {
      position: fixed;
      width: 56px;
      height: 56px;
      pointer-events: none;
      transform: translate(-50%, -50%);
      transition: transform 0.1s ease;
    }
    
    .cursor-ring {
      position: absolute;
      inset: 0;
      border: 3px solid #10b981;
      border-radius: 50%;
      box-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
      animation: cursorPulse 1.5s ease-in-out infinite;
    }
    
    @keyframes cursorPulse {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .cursor-inner {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, #10b981, #059669);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    .cursor-inner::before, .cursor-inner::after {
      content: '';
      position: absolute;
      background: white;
      border-radius: 2px;
    }
    .cursor-inner::before { width: 16px; height: 3px; }
    .cursor-inner::after { width: 3px; height: 16px; }
    
    #cursor.on-target {
      transform: translate(-50%, -50%) scale(1.2);
    }
    #cursor.on-target .cursor-ring {
      border-color: #22c55e;
      box-shadow: 0 0 30px rgba(34, 197, 94, 0.8);
    }
    
    /* ============== Tooltip - Premium ============== */
    #tooltip {
      position: fixed;
      pointer-events: none;
      display: none;
      transform: translateY(8px);
      opacity: 0;
      transition: all 0.2s ease;
    }
    
    #tooltip.active {
      display: block;
      transform: translateY(0);
      opacity: 1;
    }
    
    .tooltip-card {
      background: rgba(10, 10, 10, 0.95);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 12px;
      padding: 12px 18px;
      box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.4),
        0 0 20px rgba(16, 185, 129, 0.2);
    }
    
    .tooltip-label {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #10b981;
      margin-bottom: 4px;
    }
    
    .tooltip-title {
      font-size: 14px;
      font-weight: 600;
      color: white;
      max-width: 250px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    /* ============== Bottom提示 - Premium ============== */
    #hint {
      position: fixed;
      bottom: 60px;
      left: 50%;
      transform: translateX(-50%);
      animation: hintFloat 3s ease-in-out infinite;
    }
    
    @keyframes hintFloat {
      0%, 100% { transform: translateX(-50%) translateY(0); }
      50% { transform: translateX(-50%) translateY(-8px); }
    }
    
    .hint-card {
      background: rgba(10, 10, 10, 0.9);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 16px 28px;
      display: flex;
      align-items: center;
      gap: 14px;
      box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4);
    }
    
    .hint-icon {
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #10b981, #059669);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .hint-icon svg {
      width: 22px;
      height: 22px;
      stroke: white;
      stroke-width: 2.5;
      fill: none;
    }
    
    .hint-text {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    
    .hint-main {
      font-size: 14px;
      font-weight: 600;
      color: white;
    }
    
    .hint-sub {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.5);
    }
    
    /* ============== 入场Animation ============== */
    body {
      animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    
    #hint {
      animation: hintFloat 3s ease-in-out infinite, slideUp 0.4s ease 0.1s both;
    }
    
    @keyframes slideUp {
      from { opacity: 0; transform: translateX(-50%) translateY(20px); }
      to { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
  </style>
</head>
<body>
  <div class="scan-effect"></div>
  
  <div id="highlight">
    <div class="glow-border"></div>
    <div class="highlight-scan"></div>
    <div class="corner corner-tl"></div>
    <div class="corner corner-tr"></div>
    <div class="corner corner-bl"></div>
    <div class="corner corner-br"></div>
  </div>
  
  <div id="cursor">
    <div class="cursor-ring"></div>
    <div class="cursor-inner"></div>
  </div>
  
  <div id="tooltip">
    <div class="tooltip-card">
      <div class="tooltip-label">Connect to</div>
      <div class="tooltip-title" id="tooltipTitle"></div>
    </div>
  </div>
  
  <div id="hint">
    <div class="hint-card">
      <div class="hint-icon">
        <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 8v8M8 12h8"/>
        </svg>
      </div>
      <div class="hint-text">
        <span class="hint-main">Release to connect</span>
        <span class="hint-sub">Move cursor to target window</span>
      </div>
    </div>
  </div>
  
  <script>
    const highlight = document.getElementById('highlight');
    const tooltip = document.getElementById('tooltip');
    const tooltipTitle = document.getElementById('tooltipTitle');
    const cursor = document.getElementById('cursor');
    
    window.updateCursor = function(x, y) {
      cursor.style.left = x + 'px';
      cursor.style.top = y + 'px';
    };
    
    window.showHighlight = function(x, y, w, h, title, cx, cy) {
      highlight.style.display = 'block';
      highlight.style.left = x + 'px';
      highlight.style.top = y + 'px';
      highlight.style.width = w + 'px';
      highlight.style.height = h + 'px';
      
      cursor.classList.add('on-target');
      
      tooltip.classList.add('active');
      tooltipTitle.textContent = title;
      tooltip.style.left = (cx + 30) + 'px';
      tooltip.style.top = (cy + 30) + 'px';
    };
    
    window.hideHighlight = function() {
      highlight.style.display = 'none';
      cursor.classList.remove('on-target');
      tooltip.classList.remove('active');
    };
    
    // enterfieldsound
    try {
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = 800;
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
      osc.start();
      osc.stop(ctx.currentTime + 0.15);
    } catch(e) {}
    
    console.log('[DragOverlay] Premium mode ready');
  </script>
</body>
</html>`;
}

// Storage mainWindow Reference
let mainWindowRef = null;

/**
 * Start拖拽模式
 */
function startDragMode(mainWindow) {
  if (isActive) return { success: false, reason: 'Already active' };
  
  isActive = true;
  targetWindowInfo = null;
  mainWindowRef = mainWindow;
  
  // Create Overlay
  createDragOverlay();
  dragOverlayWindow.show();
  
  // WaitpageLoadComplete
  dragOverlayWindow.webContents.on('did-finish-load', () => {
    safeLog('[DragConnector] Overlay page loaded');
  });
  
  // BeginPollMousePosition + DetectionMouseRelease
  let lastHwnd = 0;
  let mouseWasDown = true; // BegintimeMouseYesbyDown's 
  
  pollInterval = setInterval(() => {
    // DetectionMouseYesNoRelease
    const mouseDown = isMouseButtonDown();
    
    if (mouseWasDown && !mouseDown) {
      // Mousejust nowRelease！UsagemostAfterValid's TargetWindow
      safeLog('[DragConnector] Mouse released, using last valid target:', targetWindowInfo?.title);
      
      // directlyUsagealreadySave's  targetWindowInfo，notneedagainDetection
      const finalTarget = targetWindowInfo ? {
        hwnd: targetWindowInfo.hwnd,
        title: targetWindowInfo.title,
      } : null;
      
      // EndDragPattern
      endDragMode();
      
      // NotifyRenderProcessConnectComplete
      if (mainWindowRef && !mainWindowRef.isDestroyed() && finalTarget) {
        safeLog('[DragConnector] Sending complete event with target:', finalTarget);
        mainWindowRef.webContents.send('drag-connector:complete', finalTarget);
      }
      return;
    }
    mouseWasDown = mouseDown;
    
    // CheckYesNoNeedSwitchDisplayer（MousemovetoanotherDisplayer）
    const cursorScreenPoint = screen.getCursorScreenPoint();
    const currentDisplayNow = screen.getDisplayNearestPoint(cursorScreenPoint);
    
    if (currentDisplay !== currentDisplayNow.id) {
      // MousemovetoanotherDisplayer，heavyNewCreate overlay
      safeLog('[DragConnector] Mouse moved to different display, recreating overlay');
      if (dragOverlayWindow && !dragOverlayWindow.isDestroyed()) {
        dragOverlayWindow.close();
        dragOverlayWindow = null;
      }
      createDragOverlay();
      // Load HTML
      dragOverlayWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(generateOverlayHTML())}`);
    }
    
    // GetwhenBeforeMousePosition
    let cursorX = 0, cursorY = 0;
    
    if (GetCursorPos && dragOverlayWindow && !dragOverlayWindow.isDestroyed()) {
      const point = { x: 0, y: 0 };
      GetCursorPos(point);
      
      // GetwhenBeforeDisplayerInfo
      const display = screen.getDisplayNearestPoint({ x: point.x, y: point.y });
      const scaleFactor = display.scaleFactor || 1;
      
      // Get overlay WindowBoundary（logicPixel）
      const overlayBounds = dragOverlayWindow.getBounds();
      
      // Convert：physicalPixel -> Relativeat overlay 's logicPixel
      // Windows API ReturnphysicalPixel，Needexceptto scaleFactor ConvertforlogicPixel
      cursorX = Math.round((point.x / scaleFactor) - overlayBounds.x);
      cursorY = Math.round((point.y / scaleFactor) - overlayBounds.y);
      
      // UpdatecursorGraphmarkPosition
      dragOverlayWindow.webContents.executeJavaScript(`window.updateCursor(${cursorX}, ${cursorY})`).catch(() => {});
    }
    
    // WindowDetection
    const windowInfo = getWindowUnderCursor();
    
    if (windowInfo) {
      // GetwhenBeforeDisplayer's  DPI Scaling
      const display = screen.getDisplayNearestPoint({ x: windowInfo.x + 10, y: windowInfo.y + 10 });
      const scaleFactor = display.scaleFactor || 1;
      
      // Get overlay WindowBoundary（logicPixel）
      const overlayBounds = dragOverlayWindow ? dragOverlayWindow.getBounds() : { x: 0, y: 0 };
      
      // Convert：physicalPixel -> Relativeat overlay 's logicPixel
      const relX = Math.round((windowInfo.x / scaleFactor) - overlayBounds.x);
      const relY = Math.round((windowInfo.y / scaleFactor) - overlayBounds.y);
      const relW = Math.round(windowInfo.width / scaleFactor);
      const relH = Math.round(windowInfo.height / scaleFactor);
      
      // alwaysUpdate targetWindowInfo
      targetWindowInfo = windowInfo;
      
      if (windowInfo.hwnd !== lastHwnd) {
        lastHwnd = windowInfo.hwnd;
        safeLog('[DragConnector] Target window:', windowInfo.title, 'at', { relX, relY, relW, relH });
      }
      
      // UpdateHighbright
      // [Repair #4]AddExceptionHandle，preventWindowDestroytime's CallError
      // [P0-6 FIX] UsageSecurity's Argumentpass，avoid XSS inject
      if (dragOverlayWindow && !dragOverlayWindow.isDestroyed()) {
        try {
          // [P0-6 FIX] Usage JSON.stringify SecurityturnmeaningCharacterstring，prevent XSS
          const safeParams = JSON.stringify({
            x: relX,
            y: relY,
            w: relW,
            h: relH,
            title: windowInfo.title,  // JSON.stringify willAutoturnmeaningspecialspecialCharacter
            cx: cursorX,
            cy: cursorY
          });
          dragOverlayWindow.webContents.executeJavaScript(
            `(function() { const p = ${safeParams}; window.showHighlight(p.x, p.y, p.w, p.h, p.title, p.cx, p.cy); })()`
          ).catch((err) => {
            console.debug('[DragConnector] executeJavaScript error:', err.message);
          });
        } catch (err) {
          console.debug('[DragConnector] Overlay update error:', err.message);
        }
      }
      
      // NotifyRenderProcess
      if (mainWindowRef && !mainWindowRef.isDestroyed()) {
        mainWindowRef.webContents.send('drag-connector:update', windowInfo);
      }
    } else {
      // noDetectiontoValidWindow，butretainmostAfter's  targetWindowInfo
      // onlyHideHighbright，notClearTarget
      if (lastHwnd !== 0) {
        safeLog('[DragConnector] No target window (keeping last valid)');
        lastHwnd = 0;
      }
      if (dragOverlayWindow && !dragOverlayWindow.isDestroyed()) {
        dragOverlayWindow.webContents.executeJavaScript(`window.hideHighlight()`).catch(() => {});
      }
    }
  }, 16); // ~60 FPS，morestreamsmooth's visualFeedback
  
  safeLog('[DragConnector] Drag mode started');
  return { success: true };
}

/**
 * End拖拽模式
 */
function endDragMode() {
  if (!isActive) return { success: false, target: null };
  
  isActive = false;
  
  // StopPoll
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
  
  // Close Overlay
  if (dragOverlayWindow && !dragOverlayWindow.isDestroyed()) {
    dragOverlayWindow.close();
    dragOverlayWindow = null;
  }
  
  const result = {
    success: true,
    target: targetWindowInfo ? {
      hwnd: targetWindowInfo.hwnd,
      title: targetWindowInfo.title,
    } : null,
  };
  
  targetWindowInfo = null;
  
  safeLog('[DragConnector] Drag mode ended, target:', result.target);
  return result;
}

/**
 * Set IPC Handle器
 */
function setupDragConnectorIPC(mainWindow) {
  ipcMain.handle('drag-connector:start', async () => {
    return startDragMode(mainWindow);
  });
  
  ipcMain.handle('drag-connector:end', async () => {
    return endDragMode();
  });
  
  safeLog('[DragConnector] IPC handlers registered');
}

module.exports = {
  setupDragConnectorIPC,
  startDragMode,
  endDragMode,
  isActive: () => isActive,
};

