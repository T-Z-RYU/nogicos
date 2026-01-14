/**
 * Agent IPC Handlers
 * Phase 7.12: Main Process IPC Handlers
 * 
 * Handle Agent 相Off的 IPC 通信，Package含严格的ArgumentVerify
 */

const { ipcMain } = require('electron');
const { IPCBatcher } = require('./ipc-batcher');

// UUID Verifyregex
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// Afterend API base URL
const API_BASE = process.env.NOGICOS_API_URL || 'http://localhost:8000';

/**
 * Verify UUID 格式
 * @param {string} str 
 * @returns {boolean}
 */
function isValidUUID(str) {
  return typeof str === 'string' && UUID_REGEX.test(str);
}

/**
 * Verify任务文本
 * @param {string} task 
 * @returns {{valid: boolean, error?: string}}
 */
function validateTask(task) {
  if (!task || typeof task !== 'string') {
    return { valid: false, error: 'Invalid task: must be a non-empty string' };
  }
  if (task.length > 5000) {
    return { valid: false, error: 'Task too long: max 5000 characters' };
  }
  // basically's  XSS protection（althoughmainlyrely CSP）
  if (/<script|javascript:|on\w+=/i.test(task)) {
    return { valid: false, error: 'Invalid task: contains suspicious content' };
  }
  return { valid: true };
}

/**
 * VerifyWindow句柄Array
 * 
 * Phase 8 Repair: AllowEmptyArray，支持 HostAgent Auto检测Before景Window功能。
 * 当 targetHwnds 为Empty时，After端会调用 _detect_target_windows() Auto检测。
 * 
 * @param {number[]} hwnds 
 * @returns {{valid: boolean, error?: string}}
 */
function validateHwnds(hwnds) {
  if (!Array.isArray(hwnds)) {
    return { valid: false, error: 'Invalid targetHwnds: must be an array' };
  }
  // Phase 8 Repair: AllowEmptyArray，AfterendwillAutoDetectionBeforesceneWindow
  // if (hwnds.length === 0) {
  //   return { valid: false, error: 'Invalid targetHwnds: array cannot be empty' };
  // }
  if (hwnds.length > 10) {
    return { valid: false, error: 'Invalid targetHwnds: max 10 windows' };
  }
  // onlyhavenonEmptytimeonly thenVerifyElements
  if (hwnds.length > 0 && !hwnds.every(h => typeof h === 'number' && h > 0 && Number.isInteger(h))) {
    return { valid: false, error: 'Invalid targetHwnds: must contain positive integers' };
  }
  return { valid: true };
}

/**
 * Security的 fetch Package装
 * @param {string} url 
 * @param {RequestInit} options 
 */
async function safeFetch(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000); // 30SecondTimeout
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error (${response.status}): ${errorText}`);
    }
    
    return response.json();
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * Register Agent IPC Handlers
 * @param {Electron.BrowserWindow} mainWindow 
 * @param {object} [options] - OptionalConfig
 * @param {object} [options.multiOverlayManager] - 多Window Overlay 管理器（用于动作预览）
 */
function registerAgentIpcHandlers(mainWindow, options = {}) {
  let agentWs = null;
  let batcher = null;
  const { multiOverlayManager } = options;

  // ============== Agent control Handlers ==============

  /**
   * Start任务
   */
  ipcMain.handle('agent:start', async (event, { task, targetHwnds }) => {
    // ArgumentVerify
    const taskValidation = validateTask(task);
    if (!taskValidation.valid) {
      throw new Error(taskValidation.error);
    }
    
    const hwndsValidation = validateHwnds(targetHwnds);
    if (!hwndsValidation.valid) {
      throw new Error(hwndsValidation.error);
    }
    
    console.log(`[Agent] Starting task with ${targetHwnds.length} target windows`);
    
    const result = await safeFetch(`${API_BASE}/api/agent/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task, target_hwnds: targetHwnds }),
    });
    
    // Connect WebSocket toReceiverealtimeEvent
    if (result.taskId) {
      connectAgentWebSocket(result.taskId);
    }
    
    return result;
  });

  /**
   * Stop任务
   */
  ipcMain.handle('agent:stop', async (event, { taskId }) => {
    if (!taskId || !isValidUUID(taskId)) {
      throw new Error('Invalid taskId: must be a valid UUID');
    }
    
    console.log(`[Agent] Stopping task: ${taskId}`);
    
    // Disconnect WebSocket
    disconnectAgentWebSocket();
    
    return safeFetch(`${API_BASE}/api/agent/stop?task_id=${taskId}`, {
      method: 'POST',
    });
  });

  /**
   * Resume任务
   */
  ipcMain.handle('agent:resume', async (event, { taskId }) => {
    if (!taskId || !isValidUUID(taskId)) {
      throw new Error('Invalid taskId: must be a valid UUID');
    }
    
    console.log(`[Agent] Resuming task: ${taskId}`);
    
    const result = await safeFetch(`${API_BASE}/api/agent/resume?task_id=${taskId}`, {
      method: 'POST',
    });
    
    // heavyNewConnect WebSocket
    connectAgentWebSocket(taskId);
    
    return result;
  });

  /**
   * Confirm敏感操作
   */
  ipcMain.handle('agent:confirm', async (event, { taskId, actionId, approved }) => {
    // strictVerify
    if (!taskId || !isValidUUID(taskId)) {
      throw new Error('Invalid taskId: must be a valid UUID');
    }
    if (!actionId || typeof actionId !== 'string' || actionId.length > 100) {
      throw new Error('Invalid actionId: must be a non-empty string');
    }
    if (typeof approved !== 'boolean') {
      throw new Error('Invalid approved: must be boolean');
    }
    
    // RecordAuditLog
    const auditLog = {
      timestamp: new Date().toISOString(),
      taskId,
      actionId,
      decision: approved ? 'APPROVED' : 'REJECTED',
    };
    console.log(`[Audit] Sensitive action: ${JSON.stringify(auditLog)}`);
    
    return safeFetch(`${API_BASE}/api/agent/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_id: taskId, action_id: actionId, approved }),
    });
  });

  /**
   * Get任务State
   */
  ipcMain.handle('agent:status', async (event, { taskId }) => {
    if (!taskId || !isValidUUID(taskId)) {
      throw new Error('Invalid taskId: must be a valid UUID');
    }
    
    return safeFetch(`${API_BASE}/api/agent/status/${taskId}`);
  });

  /**
   * Get所有Active任务
   */
  ipcMain.handle('agent:active-tasks', async () => {
    return safeFetch(`${API_BASE}/api/agent/active`);
  });

  // ============== WebSocket bridge ==============

  /**
   * Connect Agent WebSocket
   * @param {string} taskId 
   */
  function connectAgentWebSocket(taskId) {
    // firstDisconnectappearhaveConnect
    disconnectAgentWebSocket();
    
    const wsUrl = API_BASE.replace('http', 'ws');
    
    try {
      // Node.js EnvironmentmaybeNeed ws Library
      const WebSocket = require('ws');
      agentWs = new WebSocket(`${wsUrl}/ws/agent/${taskId}`);
      
      // CreatebatchHandleer
      if (mainWindow && !mainWindow.isDestroyed()) {
        batcher = new IPCBatcher(mainWindow.webContents);
      }
      
      agentWs.on('open', () => {
        console.log('[Agent WS] Connected');
      });
      
      agentWs.on('message', (rawData) => {
        try {
          const data = JSON.parse(rawData.toString());
          
          // ForwardtoRenderProcess
          if (batcher && !batcher.isDestroyed()) {
            batcher.send('agent:event', data);
          }
          
          // Phase 7: actionPreviewForwardto Overlay（transmitenter mainWindow forNone hwnd time's Notify）
          if (multiOverlayManager && data.type === 'tool') {
            handleToolEventForPreview(data, multiOverlayManager, mainWindow);
          }
          
          // Phase 7: InitializeActiveWindow（FirsttimereceivetoToolEventtime）
          if (multiOverlayManager && multiOverlayManager.initializeActiveIfNeeded) {
            multiOverlayManager.initializeActiveIfNeeded();
          }
          
          // Phase 7: multipleWindowFocusmanage
          if (multiOverlayManager && data.type === 'focus' && data.data?.hwnd) {
            multiOverlayManager.setActiveWindow(data.data.hwnd);
          }
          
        } catch (e) {
          console.error('[Agent WS] Failed to parse message:', e);
        }
      });
      
      agentWs.on('error', (error) => {
        console.error('[Agent WS] Error:', error.message);
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('agent:event', {
            type: 'error',
            data: { 
              type: 'connection_error',
              message: error.message,
              recoverable: true,
            },
          });
        }
      });
      
      agentWs.on('close', (code, reason) => {
        console.log(`[Agent WS] Closed (${code}): ${reason}`);
        cleanup();
      });
      
    } catch (error) {
      console.error('[Agent WS] Failed to create WebSocket:', error);
      // WebSocket ConnectFailednotShouldblockOtherfunction
    }
  }

  /**
   * Disconnect Agent WebSocket
   */
  function disconnectAgentWebSocket() {
    if (agentWs) {
      try {
        agentWs.close();
      } catch (e) {
        // IgnoreCloseError
      }
      agentWs = null;
    }
    cleanup();
  }

  /**
   * Cleanup资Source
   */
  function cleanup() {
    if (batcher) {
      batcher.destroy();
      batcher = null;
    }
  }

  // ReturncontrolFunctionprovideOuterpartUsage
  return {
    connectAgentWebSocket,
    disconnectAgentWebSocket,
    cleanup,
  };
}

/**
 * Unregister所有 Agent IPC Handlers
 */
function unregisterAgentIpcHandlers() {
  const channels = [
    'agent:start',
    'agent:stop',
    'agent:resume',
    'agent:confirm',
    'agent:status',
    'agent:active-tasks',
  ];
  
  channels.forEach(channel => {
    ipcMain.removeHandler(channel);
  });
  
  console.log('[Agent] IPC handlers unregistered');
}

/**
 * 需要可视预览的ToolList（用于Default提示）
 */
const TOOLS_WITH_PREVIEW = new Set([
  'window_click', 'click', 'double_click', 'right_click',
  'window_type', 'type', 'input_text',
  'keyboard_shortcut', 'hotkey', 'key_press',
  'scroll', 'scroll_to',
  'drag', 'drag_and_drop',
  'window_move', 'window_resize', 'window_close', 'window_maximize', 'window_minimize',
  'open_application', 'open_file', 'open_url',
  'copy', 'paste', 'cut', 'select_all',
]);

/**
 * Tool名到人Class可Read描述的映射
 */
const TOOL_LABELS = {
  'window_click': '点击',
  'click': '点击',
  'double_click': '双击',
  'right_click': 'Right键点击',
  'window_type': 'Input文字',
  'type': 'Input文字',
  'input_text': 'Input文字',
  'keyboard_shortcut': '快捷键',
  'hotkey': '快捷键',
  'key_press': '按键',
  'scroll': '滚动',
  'scroll_to': '滚动到',
  'drag': '拖拽',
  'drag_and_drop': '拖放',
  'window_move': 'MoveWindow',
  'window_resize': '调整Size',
  'window_close': 'CloseWindow',
  'window_maximize': 'Max化',
  'window_minimize': 'Min化',
  'open_application': 'Open应用',
  'open_file': 'OpenFile',
  'open_url': 'Open链接',
  'copy': 'Copy',
  'paste': '粘贴',
  'cut': '剪切',
  'select_all': '全选',
};

/**
 * HandleToolEvent并转发动作预览到 Overlay
 * @param {object} event - ToolEvent
 * @param {object} manager - MultiOverlayManager Instance
 * @param {Electron.BrowserWindow} [mainWindow] - 主Window（用于无 hwnd 时SendNotify）
 */
function handleToolEventForPreview(event, manager, mainWindow = null) {
  const { data } = event;
  if (!data) return;
  
  const { tool_name, args, hwnd, coordinates, element_name } = data;
  
  // Argumentvalidate
  if (!tool_name || typeof tool_name !== 'string') {
    console.warn('[Preview] Invalid tool_name:', tool_name);
    return;
  }
  
  // hwnd validate（Optional，someToolmaybeNot Need）
  const validHwnd = typeof hwnd === 'number' && hwnd > 0;
  
  // HelperFunction：forNone hwnd 's ActionSend renderer sideTip
  const sendRendererToast = (message) => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('agent:event', {
        type: 'toast',
        data: {
          message,
          tool_name,
          timestamp: Date.now(),
        },
      });
    }
  };
  
  // RootdataToolClasstypeSenddifferent's Preview
  switch (tool_name) {
    case 'window_click':
    case 'click':
    case 'double_click':
    case 'right_click':
      if (validHwnd && coordinates) {
        const clickType = tool_name === 'double_click' ? 'double-click' 
                        : tool_name === 'right_click' ? 'right-click' 
                        : 'click';
        manager.sendActionPreview(hwnd, 'target', {
          x: coordinates.x,
          y: coordinates.y,
          label: `即将${TOOL_LABELS[tool_name] || '点击'}: ${element_name || ''}`,
        });
        // ShorttempDelayedAfterDisplayClickEffect
        setTimeout(() => {
          manager.sendActionPreview(hwnd, 'click', {
            x: coordinates.x,
            y: coordinates.y,
            type: clickType,
          });
        }, 500);
      }
      break;
      
    case 'window_type':
    case 'type':
    case 'input_text':
      if (validHwnd && args?.text) {
        manager.sendActionPreview(hwnd, 'typing', {
          text: args.text,
          isPassword: args.is_password || false,
        });
      }
      break;
      
    case 'keyboard_shortcut':
    case 'hotkey':
    case 'key_press':
      if (validHwnd) {
        const shortcut = args?.shortcut || args?.key || args?.keys;
        if (shortcut) {
          manager.sendActionPreview(hwnd, 'shortcut', {
            shortcut: Array.isArray(shortcut) ? shortcut.join('+') : shortcut,
          });
        }
      }
      break;
      
    case 'scroll':
    case 'scroll_to':
      if (validHwnd) {
        manager.sendActionPreview(hwnd, 'scroll', {
          direction: args?.direction || 'down',
          amount: args?.amount || args?.distance || 100,
        });
      }
      break;
      
    case 'drag':
    case 'drag_and_drop':
      if (validHwnd && args) {
        const from = args.from || args.start || coordinates;
        const to = args.to || args.end;
        if (from && to) {
          // DisplayDragtrajectory
          manager.sendActionPreview(hwnd, 'mouse-trajectory', {
            from: { x: from.x, y: from.y },
            to: { x: to.x, y: to.y },
          });
        }
      }
      break;
      
    case 'window_move':
    case 'window_resize':
    case 'window_close':
    case 'window_maximize':
    case 'window_minimize':
      if (validHwnd) {
        manager.sendActionPreview(hwnd, 'window-action', {
          action: tool_name.replace('window_', ''),
          label: TOOL_LABELS[tool_name] || tool_name,
        });
      }
      break;
      
    case 'open_application':
    case 'open_file':
    case 'open_url':
      // theseActionmaybeno hwnd
      if (validHwnd) {
        manager.sendActionPreview(hwnd, 'window-action', {
          action: 'open',
          label: `${TOOL_LABELS[tool_name]}: ${args?.path || args?.url || args?.name || ''}`,
        });
      } else {
        // None hwnd：Send renderer sideTip
        const target = args?.path || args?.url || args?.name || '';
        sendRendererToast(`${TOOL_LABELS[tool_name]}: ${target}`);
      }
      break;
      
    case 'copy':
    case 'paste':
    case 'cut':
    case 'select_all':
      if (validHwnd) {
        manager.sendActionPreview(hwnd, 'shortcut', {
          shortcut: `Ctrl+${tool_name === 'copy' ? 'C' : tool_name === 'paste' ? 'V' : tool_name === 'cut' ? 'X' : 'A'}`,
        });
      }
      break;
      
    default:
      // UnknownbutmaybeNeedPreview's Tool：SendDefaultTip
      if (TOOLS_WITH_PREVIEW.has(tool_name)) {
        console.warn(`[Preview] Unhandled preview tool: ${tool_name}`);
      }
      // forhave hwnd 's UnknownTool，SendgeneralActionTip
      if (validHwnd) {
        manager.sendActionPreview(hwnd, 'window-action', {
          action: 'generic',
          label: `Execute: ${TOOL_LABELS[tool_name] || tool_name}`,
        });
      } else {
        // None hwnd 's UnknownTool：Send renderer sideTip
        sendRendererToast(`Execute: ${TOOL_LABELS[tool_name] || tool_name}`);
      }
      break;
  }
}

/**
 * 预览Class型Whitelist说明（维护指南）
 * ========================================
 * 当New增预览Class型时，需SyncUpdate以DownPosition：
 * 
 * 1. multi-overlay-manager.js:
 *    - MultiOverlayManager.ALLOWED_PREVIEW_TYPES (StaticSet)
 * 
 * 2. multi-overlay-manager.js (_generateOverlayHTML):
 *    - ipcRenderer.on('preview:NewClass型', ...) EventListen
 *    - 对应的 create*Preview() RenderFunction
 *    - 相Off CSS AnimationStyle
 * 
 * 3. agent-ipc.js (handleToolEventForPreview):
 *    - switch case MediumAdd对应Tool名Handle
 *    - 调用 manager.sendActionPreview(hwnd, 'NewClass型', data)
 * 
 * 当Before支持的预览Class型：
 * - mouse-trajectory: 鼠标Move轨迹（虚线）
 * - click: 点击涟漪Effect
 * - typing: Input文字预览
 * - target: TargetPosition指示器
 * - scroll: 滚动方向指示
 * - shortcut: 快捷键Display
 * - window-action: Window操作提示
 * - clear: Clear所有预览
 */

module.exports = {
  registerAgentIpcHandlers,
  unregisterAgentIpcHandlers,
  isValidUUID,
  validateTask,
  validateHwnds,
  handleToolEventForPreview,
};
