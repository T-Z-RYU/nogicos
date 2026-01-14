# NogicOS 控制权管理 - 实现方案

> 基于 CONTROL_ARCHITECTURE.md 的具体实现计划

## 参考项目清单

| 项目 | 借鉴内容 | 优先级 |
|------|---------|--------|
| **Microsoft UFO** | FSM 状态机、CONFIRM 状态、分层 Agent | ⭐⭐⭐ |
| **ByteBot** | Agent 循环、工具定义、上下文压缩 | ⭐⭐⭐ |
| **Anthropic Computer Use** | 安全机制、工具验证 | ⭐⭐ |
| **PyAutoGUI** | Fail-Safe 机制 | ⭐⭐ |
| **OS-Copilot** | 自我修正、规划执行 | ⭐ |

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            NogicOS 控制层架构                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        用户界面层 (Electron)                         │   │
│  │  • Overlay 窗口                                                     │   │
│  │  • 确认对话框                                                        │   │
│  │  • 状态通知                                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       控制管理层 (Electron Main)                     │   │
│  │  • EmergencyController    - L0 紧急停止                              │   │
│  │  • InputMonitor           - L1 用户输入监测                          │   │
│  │  • WindowIsolation        - L2 窗口隔离                              │   │
│  │  • ActionClassifier       - L3 操作分级                              │   │
│  │  • OverlayFeedback        - L4 视觉反馈                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        输入执行层 (Windows API)                      │   │
│  │  • WindowMessageInput     - 窗口消息输入                             │   │
│  │  • PhysicalInput          - 物理输入（回退）                         │   │
│  │  • InputMarker            - AI 输入标记                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Agent 层 (Python)                            │   │
│  │  • Orchestrator           - 任务编排（参考 UFO HostAgent）           │   │
│  │  • ActionExecutor         - 动作执行（参考 UFO AppAgent）            │   │
│  │  • ContextManager         - 上下文管理                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 基础控制层 (Week 1)

### 1.1 紧急停止控制器

**文件**: `nogicos/client/emergency-controller.js`

```javascript
const { globalShortcut, ipcMain } = require('electron');

class EmergencyController {
  constructor() {
    this.isEmergencyStopped = false;
    this.escapeCount = 0;
    this.escapeTimer = null;
  }

  setup(mainWindow) {
    // 主快捷键: Ctrl+Shift+P
    globalShortcut.register('Ctrl+Shift+P', () => {
      this.triggerEmergencyStop('keyboard_shortcut');
    });

    // 备用: 连按 3 次 Escape
    globalShortcut.register('Escape', () => {
      this.handleEscapePress();
    });

    // IPC 通道
    ipcMain.handle('emergency:status', () => this.isEmergencyStopped);
    ipcMain.handle('emergency:resume', () => this.resume());
  }

  handleEscapePress() {
    this.escapeCount++;
    
    if (this.escapeTimer) clearTimeout(this.escapeTimer);
    
    if (this.escapeCount >= 3) {
      this.triggerEmergencyStop('escape_triple');
      this.escapeCount = 0;
    } else {
      this.escapeTimer = setTimeout(() => {
        this.escapeCount = 0;
      }, 1000);
    }
  }

  triggerEmergencyStop(reason) {
    this.isEmergencyStopped = true;
    
    // 通知所有模块
    this.emit('emergency:stop', { reason, timestamp: Date.now() });
    
    // 显示紧急停止 Overlay
    this.showEmergencyOverlay(reason);
    
    // 播放提示音
    this.playAlertSound();
  }

  resume() {
    this.isEmergencyStopped = false;
    this.emit('emergency:resume');
  }
}

module.exports = { EmergencyController };
```

### 1.2 用户输入监测器

**文件**: `nogicos/client/input-monitor.js`

```javascript
const koffi = require('koffi');

const user32 = koffi.load('user32.dll');
const SetWindowsHookEx = user32.func('SetWindowsHookExW', 'void*', ['int', 'void*', 'void*', 'uint']);
const CallNextHookEx = user32.func('CallNextHookEx', 'long', ['void*', 'int', 'uintptr_t', 'intptr_t']);
const GetKeyState = user32.func('GetKeyState', 'short', ['int']);

const WH_MOUSE_LL = 14;
const WH_KEYBOARD_LL = 13;
const NOGICOS_MARKER = 0x4E4F4749;

class InputMonitor {
  constructor() {
    this.mouseHook = null;
    this.keyboardHook = null;
    this.lastUserInputTime = 0;
    this.callbacks = {
      onUserInput: null,
    };
  }

  start() {
    // 注意: 低级钩子需要在消息循环中运行
    // 实际实现需要更复杂的设置
    console.log('[InputMonitor] Started monitoring user input');
  }

  stop() {
    // 移除钩子
  }

  // 检查是否是 AI 输入
  isAIInput(extraInfo) {
    return extraInfo === NOGICOS_MARKER;
  }

  // 获取自上次用户输入的时间
  getTimeSinceLastUserInput() {
    return Date.now() - this.lastUserInputTime;
  }

  onUserInput(callback) {
    this.callbacks.onUserInput = callback;
  }
}

module.exports = { InputMonitor, NOGICOS_MARKER };
```

### 1.3 状态机管理器

**文件**: `nogicos/client/state-machine.js`

```javascript
// 参考 Microsoft UFO 的 FSM 设计

const AIState = {
  IDLE: 'idle',           // 空闲
  ACTIVE: 'active',       // 执行中
  PENDING: 'pending',     // 等待用户输入
  CONFIRM: 'confirm',     // 等待确认
  PAUSED: 'paused',       // 已暂停
  ERROR: 'error',         // 错误
};

class StateMachine {
  constructor() {
    this.state = AIState.IDLE;
    this.stateData = {};
    this.listeners = [];
  }

  transition(newState, data = {}) {
    const oldState = this.state;
    this.state = newState;
    this.stateData = data;

    console.log(`[StateMachine] ${oldState} → ${newState}`);
    
    this.listeners.forEach(cb => cb(oldState, newState, data));
  }

  // 用户输入检测到时调用
  onUserInput() {
    if (this.state === AIState.ACTIVE) {
      this.transition(AIState.PENDING, {
        reason: 'user_input_detected',
        resumeAfter: 3000,
      });
    }
  }

  // 敏感操作需要确认
  requestConfirmation(action) {
    this.transition(AIState.CONFIRM, {
      action,
      timeout: 10000,
    });
  }

  // 恢复执行
  resume() {
    if (this.state === AIState.PENDING || this.state === AIState.PAUSED) {
      this.transition(AIState.ACTIVE);
    }
  }

  // 用户完全接管
  userTakeover() {
    this.transition(AIState.IDLE, {
      reason: 'user_takeover',
    });
  }

  onStateChange(callback) {
    this.listeners.push(callback);
  }
}

module.exports = { StateMachine, AIState };
```

---

## Phase 2: 窗口隔离层 (Week 2)

### 2.1 窗口消息输入

**文件**: `nogicos/client/window-input.js`

```javascript
const koffi = require('koffi');

const user32 = koffi.load('user32.dll');
const PostMessage = user32.func('PostMessageW', 'bool', ['int', 'uint', 'uintptr_t', 'intptr_t']);
const SendMessage = user32.func('SendMessageW', 'intptr_t', ['int', 'uint', 'uintptr_t', 'intptr_t']);

// Windows 消息常量
const WM_LBUTTONDOWN = 0x0201;
const WM_LBUTTONUP = 0x0202;
const WM_RBUTTONDOWN = 0x0204;
const WM_RBUTTONUP = 0x0205;
const WM_MOUSEMOVE = 0x0200;
const WM_MOUSEWHEEL = 0x020A;
const WM_KEYDOWN = 0x0100;
const WM_KEYUP = 0x0101;
const WM_CHAR = 0x0102;
const MK_LBUTTON = 0x0001;
const MK_RBUTTON = 0x0002;

class WindowInput {
  constructor() {
    this.defaultDelay = 50; // ms
  }

  /**
   * 在窗口内点击（不移动物理鼠标）
   */
  async click(hwnd, x, y, options = {}) {
    const { button = 'left', count = 1 } = options;
    const lParam = this._makeLParam(x, y);
    
    const downMsg = button === 'left' ? WM_LBUTTONDOWN : WM_RBUTTONDOWN;
    const upMsg = button === 'left' ? WM_LBUTTONUP : WM_RBUTTONUP;
    const wParam = button === 'left' ? MK_LBUTTON : MK_RBUTTON;

    for (let i = 0; i < count; i++) {
      PostMessage(hwnd, downMsg, wParam, lParam);
      await this._delay(this.defaultDelay);
      PostMessage(hwnd, upMsg, 0, lParam);
      await this._delay(this.defaultDelay);
    }

    return true;
  }

  /**
   * 在窗口内输入文字（不影响物理键盘）
   */
  async type(hwnd, text, options = {}) {
    const { interval = 30 } = options;

    for (const char of text) {
      PostMessage(hwnd, WM_CHAR, char.charCodeAt(0), 0);
      await this._delay(interval);
    }

    return true;
  }

  /**
   * 在窗口内按键
   */
  async pressKey(hwnd, keyCode, options = {}) {
    const { hold = false } = options;

    PostMessage(hwnd, WM_KEYDOWN, keyCode, 0);
    
    if (!hold) {
      await this._delay(this.defaultDelay);
      PostMessage(hwnd, WM_KEYUP, keyCode, 0);
    }

    return true;
  }

  /**
   * 在窗口内滚动
   */
  async scroll(hwnd, x, y, delta) {
    const lParam = this._makeLParam(x, y);
    const wParam = (delta * 120) << 16; // WHEEL_DELTA = 120

    PostMessage(hwnd, WM_MOUSEWHEEL, wParam, lParam);
    return true;
  }

  _makeLParam(x, y) {
    return (y << 16) | (x & 0xFFFF);
  }

  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = { WindowInput };
```

### 2.2 窗口隔离管理器

**文件**: `nogicos/client/window-isolation.js`

```javascript
const { WindowInput } = require('./window-input');

class WindowIsolation {
  constructor() {
    this.connectedWindows = new Map(); // hwnd -> WindowControl
    this.windowInput = new WindowInput();
  }

  /**
   * 连接窗口
   */
  connect(hwnd, info) {
    this.connectedWindows.set(hwnd, {
      hwnd,
      title: info.title,
      appName: info.appName,
      userActive: false,
      aiPaused: false,
      connectedAt: Date.now(),
    });

    console.log(`[WindowIsolation] Connected to window: ${info.title}`);
  }

  /**
   * 断开窗口
   */
  disconnect(hwnd) {
    this.connectedWindows.delete(hwnd);
  }

  /**
   * 检查是否可以操作窗口
   */
  canOperate(hwnd) {
    if (!this.connectedWindows.has(hwnd)) {
      return { allowed: false, reason: 'not_connected' };
    }

    const control = this.connectedWindows.get(hwnd);

    if (control.userActive) {
      return { allowed: false, reason: 'user_active' };
    }

    if (control.aiPaused) {
      return { allowed: false, reason: 'ai_paused' };
    }

    return { allowed: true };
  }

  /**
   * 执行窗口操作
   */
  async executeAction(hwnd, action) {
    const check = this.canOperate(hwnd);
    if (!check.allowed) {
      return { success: false, reason: check.reason };
    }

    try {
      switch (action.type) {
        case 'click':
          await this.windowInput.click(hwnd, action.x, action.y, action.options);
          break;
        case 'type':
          await this.windowInput.type(hwnd, action.text, action.options);
          break;
        case 'pressKey':
          await this.windowInput.pressKey(hwnd, action.keyCode, action.options);
          break;
        case 'scroll':
          await this.windowInput.scroll(hwnd, action.x, action.y, action.delta);
          break;
        default:
          return { success: false, reason: 'unknown_action' };
      }

      return { success: true };
    } catch (error) {
      return { success: false, reason: error.message };
    }
  }

  /**
   * 标记窗口为用户活跃状态
   */
  setUserActive(hwnd, active) {
    if (this.connectedWindows.has(hwnd)) {
      this.connectedWindows.get(hwnd).userActive = active;
    }
  }
}

module.exports = { WindowIsolation };
```

---

## Phase 3: 操作分级层 (Week 3)

### 3.1 操作分类器

**文件**: `nogicos/client/action-classifier.js`

```javascript
const ActionRisk = {
  SAFE: 'safe',
  MODERATE: 'moderate',
  HIGH: 'high',
  FORBIDDEN: 'forbidden',
};

const ActionPolicy = {
  AUTO_EXECUTE: 'auto_execute',
  EXECUTE_WITH_NOTICE: 'execute_with_notice',
  REQUIRE_CONFIRMATION: 'require_confirmation',
  MANUAL_ONLY: 'manual_only',
};

class ActionClassifier {
  constructor() {
    // 操作风险规则
    this.riskRules = new Map([
      // 安全操作
      ['scroll', ActionRisk.SAFE],
      ['copy', ActionRisk.SAFE],
      ['read', ActionRisk.SAFE],
      ['navigate', ActionRisk.SAFE],
      ['select', ActionRisk.SAFE],
      ['hover', ActionRisk.SAFE],

      // 中等风险
      ['save', ActionRisk.MODERATE],
      ['edit', ActionRisk.MODERATE],
      ['create_file', ActionRisk.MODERATE],
      ['send_message', ActionRisk.MODERATE],

      // 高风险
      ['delete', ActionRisk.HIGH],
      ['send_email', ActionRisk.HIGH],
      ['publish', ActionRisk.HIGH],
      ['install', ActionRisk.HIGH],
      ['uninstall', ActionRisk.HIGH],
      ['system_setting', ActionRisk.HIGH],

      // 禁止操作
      ['input_password', ActionRisk.FORBIDDEN],
      ['financial_transaction', ActionRisk.FORBIDDEN],
      ['admin_operation', ActionRisk.FORBIDDEN],
    ]);

    // 风险等级对应的策略
    this.policyMap = new Map([
      [ActionRisk.SAFE, ActionPolicy.AUTO_EXECUTE],
      [ActionRisk.MODERATE, ActionPolicy.EXECUTE_WITH_NOTICE],
      [ActionRisk.HIGH, ActionPolicy.REQUIRE_CONFIRMATION],
      [ActionRisk.FORBIDDEN, ActionPolicy.MANUAL_ONLY],
    ]);
  }

  /**
   * 分类操作风险
   */
  classify(action) {
    const actionType = action.type.toLowerCase();

    // 检查是否匹配已知规则
    for (const [pattern, risk] of this.riskRules) {
      if (actionType.includes(pattern)) {
        return risk;
      }
    }

    // 默认为中等风险
    return ActionRisk.MODERATE;
  }

  /**
   * 获取操作策略
   */
  getPolicy(action) {
    const risk = this.classify(action);
    return this.policyMap.get(risk);
  }

  /**
   * 检查是否需要确认
   */
  needsConfirmation(action) {
    const policy = this.getPolicy(action);
    return policy === ActionPolicy.REQUIRE_CONFIRMATION;
  }

  /**
   * 检查是否禁止执行
   */
  isForbidden(action) {
    const policy = this.getPolicy(action);
    return policy === ActionPolicy.MANUAL_ONLY;
  }
}

module.exports = { ActionClassifier, ActionRisk, ActionPolicy };
```

### 3.2 确认管理器

**文件**: `nogicos/client/confirmation-manager.js`

```javascript
const { BrowserWindow, ipcMain } = require('electron');

class ConfirmationManager {
  constructor() {
    this.pendingConfirmations = new Map();
  }

  /**
   * 请求用户确认
   */
  async requestConfirmation(action, options = {}) {
    const {
      timeout = 10000,
      defaultResult = false,
    } = options;

    const confirmId = `confirm_${Date.now()}`;

    return new Promise((resolve) => {
      // 创建确认 Overlay
      this.showConfirmationOverlay(confirmId, action);

      // 设置超时
      const timer = setTimeout(() => {
        this.resolveConfirmation(confirmId, defaultResult);
        resolve(defaultResult);
      }, timeout);

      // 保存待确认信息
      this.pendingConfirmations.set(confirmId, {
        action,
        timer,
        resolve,
      });
    });
  }

  /**
   * 显示确认 Overlay
   */
  showConfirmationOverlay(confirmId, action) {
    // 通过 IPC 发送到渲染进程显示 Overlay
    // 这里简化处理，实际需要完整的 Overlay 实现
    console.log(`[Confirmation] Showing overlay for: ${action.description}`);
  }

  /**
   * 处理用户响应
   */
  handleUserResponse(confirmId, result) {
    const pending = this.pendingConfirmations.get(confirmId);
    if (!pending) return;

    clearTimeout(pending.timer);
    pending.resolve(result);
    this.pendingConfirmations.delete(confirmId);
  }

  /**
   * 解决确认（超时或取消）
   */
  resolveConfirmation(confirmId, result) {
    this.handleUserResponse(confirmId, result);
  }

  setup() {
    // 监听用户确认响应
    ipcMain.handle('confirmation:respond', (event, { confirmId, result }) => {
      this.handleUserResponse(confirmId, result);
    });
  }
}

module.exports = { ConfirmationManager };
```

---

## Phase 4: 反馈层 (Week 4)

### 4.1 Overlay 反馈管理器

**文件**: `nogicos/client/overlay-feedback.js`

```javascript
const { BrowserWindow, screen } = require('electron');

class OverlayFeedback {
  constructor() {
    this.overlays = new Map(); // hwnd -> overlay window
  }

  /**
   * 显示操作意图
   */
  showIntent(hwnd, intent) {
    const overlay = this.getOrCreateOverlay(hwnd);
    overlay.webContents.send('overlay:show-intent', intent);
  }

  /**
   * 显示执行进度
   */
  showProgress(hwnd, progress) {
    const overlay = this.getOrCreateOverlay(hwnd);
    overlay.webContents.send('overlay:show-progress', progress);
  }

  /**
   * 显示完成状态
   */
  showCompletion(hwnd, result) {
    const overlay = this.getOrCreateOverlay(hwnd);
    overlay.webContents.send('overlay:show-completion', result);
    
    // 1.5 秒后隐藏
    setTimeout(() => {
      overlay.webContents.send('overlay:hide-completion');
    }, 1500);
  }

  /**
   * 显示暂停状态
   */
  showPaused(hwnd, reason) {
    const overlay = this.getOrCreateOverlay(hwnd);
    overlay.webContents.send('overlay:show-paused', { reason });
  }

  /**
   * 显示错误
   */
  showError(hwnd, error) {
    const overlay = this.getOrCreateOverlay(hwnd);
    overlay.webContents.send('overlay:show-error', error);
  }

  /**
   * 获取或创建 Overlay
   */
  getOrCreateOverlay(hwnd) {
    if (this.overlays.has(hwnd)) {
      return this.overlays.get(hwnd);
    }

    // 创建新的 Overlay 窗口
    const overlay = new BrowserWindow({
      transparent: true,
      frame: false,
      alwaysOnTop: true,
      skipTaskbar: true,
      focusable: false,
      type: 'toolbar',
      webPreferences: {
        contextIsolation: true,
        preload: require('path').join(__dirname, 'overlay-preload.js'),
      },
    });

    overlay.setIgnoreMouseEvents(true);
    overlay.loadFile('overlay.html');

    this.overlays.set(hwnd, overlay);
    return overlay;
  }

  /**
   * 销毁 Overlay
   */
  destroyOverlay(hwnd) {
    const overlay = this.overlays.get(hwnd);
    if (overlay && !overlay.isDestroyed()) {
      overlay.close();
    }
    this.overlays.delete(hwnd);
  }
}

module.exports = { OverlayFeedback };
```

---

## 集成：控制管理器

**文件**: `nogicos/client/control-manager.js`

```javascript
const { EmergencyController } = require('./emergency-controller');
const { InputMonitor } = require('./input-monitor');
const { StateMachine, AIState } = require('./state-machine');
const { WindowIsolation } = require('./window-isolation');
const { ActionClassifier, ActionPolicy } = require('./action-classifier');
const { ConfirmationManager } = require('./confirmation-manager');
const { OverlayFeedback } = require('./overlay-feedback');

class ControlManager {
  constructor() {
    this.emergency = new EmergencyController();
    this.inputMonitor = new InputMonitor();
    this.stateMachine = new StateMachine();
    this.windowIsolation = new WindowIsolation();
    this.actionClassifier = new ActionClassifier();
    this.confirmationManager = new ConfirmationManager();
    this.overlayFeedback = new OverlayFeedback();
  }

  setup(mainWindow) {
    // 设置紧急停止
    this.emergency.setup(mainWindow);
    this.emergency.on('emergency:stop', () => {
      this.stateMachine.transition(AIState.PAUSED, { reason: 'emergency_stop' });
    });

    // 设置输入监测
    this.inputMonitor.start();
    this.inputMonitor.onUserInput((type) => {
      this.stateMachine.onUserInput();
    });

    // 设置确认管理
    this.confirmationManager.setup();

    // 状态变化时更新 Overlay
    this.stateMachine.onStateChange((oldState, newState, data) => {
      this.handleStateChange(oldState, newState, data);
    });

    console.log('[ControlManager] Setup complete');
  }

  /**
   * 执行操作（核心方法）
   */
  async executeAction(hwnd, action) {
    // 检查紧急停止
    if (this.emergency.isEmergencyStopped) {
      return { success: false, reason: 'emergency_stopped' };
    }

    // 检查状态
    if (this.stateMachine.state !== AIState.ACTIVE) {
      return { success: false, reason: `state_${this.stateMachine.state}` };
    }

    // 检查窗口权限
    const canOperate = this.windowIsolation.canOperate(hwnd);
    if (!canOperate.allowed) {
      return { success: false, reason: canOperate.reason };
    }

    // 检查操作策略
    const policy = this.actionClassifier.getPolicy(action);

    if (policy === ActionPolicy.MANUAL_ONLY) {
      // 禁止操作，只显示提示
      this.overlayFeedback.showIntent(hwnd, {
        message: `请手动完成：${action.description}`,
        manual: true,
      });
      return { success: false, reason: 'manual_only' };
    }

    if (policy === ActionPolicy.REQUIRE_CONFIRMATION) {
      // 需要确认
      this.stateMachine.requestConfirmation(action);
      const confirmed = await this.confirmationManager.requestConfirmation(action);
      
      if (!confirmed) {
        this.stateMachine.resume();
        return { success: false, reason: 'not_confirmed' };
      }
      this.stateMachine.resume();
    }

    // 显示意图
    this.overlayFeedback.showIntent(hwnd, {
      message: action.description,
    });

    // 执行操作
    const result = await this.windowIsolation.executeAction(hwnd, action);

    // 显示结果
    if (result.success) {
      this.overlayFeedback.showCompletion(hwnd, { success: true });
    } else {
      this.overlayFeedback.showError(hwnd, { message: result.reason });
    }

    return result;
  }

  /**
   * 处理状态变化
   */
  handleStateChange(oldState, newState, data) {
    // 根据状态显示不同的 Overlay
    switch (newState) {
      case AIState.PENDING:
        // 显示暂停状态
        for (const hwnd of this.windowIsolation.connectedWindows.keys()) {
          this.overlayFeedback.showPaused(hwnd, data.reason);
        }
        
        // 设置自动恢复
        if (data.resumeAfter) {
          setTimeout(() => {
            if (this.stateMachine.state === AIState.PENDING) {
              this.stateMachine.resume();
            }
          }, data.resumeAfter);
        }
        break;

      case AIState.CONFIRM:
        // 显示确认请求
        // ...
        break;

      case AIState.ACTIVE:
        // 隐藏暂停状态
        // ...
        break;
    }
  }

  /**
   * 连接窗口
   */
  connectWindow(hwnd, info) {
    this.windowIsolation.connect(hwnd, info);
  }

  /**
   * 断开窗口
   */
  disconnectWindow(hwnd) {
    this.windowIsolation.disconnect(hwnd);
    this.overlayFeedback.destroyOverlay(hwnd);
  }

  /**
   * 开始 AI 任务
   */
  startTask() {
    this.stateMachine.transition(AIState.ACTIVE);
  }

  /**
   * 暂停 AI 任务
   */
  pauseTask() {
    this.stateMachine.transition(AIState.PAUSED);
  }
}

module.exports = { ControlManager };
```

---

## 文件结构

```
nogicos/client/
├── main.js                    # 主入口
├── control-manager.js         # 控制管理器（集成）
├── emergency-controller.js    # L0 紧急停止
├── input-monitor.js           # L1 输入监测
├── state-machine.js           # 状态机
├── window-isolation.js        # L2 窗口隔离
├── window-input.js            # 窗口消息输入
├── action-classifier.js       # L3 操作分级
├── confirmation-manager.js    # 确认管理
├── overlay-feedback.js        # L4 反馈层
├── multi-overlay-manager.js   # 多窗口 Overlay（已实现）
└── drag-connector.js          # 拖拽连接器（已实现）
```

---

## 测试计划

### Phase 1 测试
- [ ] Ctrl+Shift+P 能立即暂停
- [ ] 连按 3 次 Escape 能暂停
- [ ] 状态机正确切换

### Phase 2 测试
- [ ] 窗口消息点击有效
- [ ] 窗口消息输入有效
- [ ] 用户操作其他窗口不受影响

### Phase 3 测试
- [ ] 安全操作自动执行
- [ ] 高风险操作弹出确认
- [ ] 禁止操作只显示提示

### Phase 4 测试
- [ ] Overlay 正确显示意图
- [ ] Overlay 正确显示进度
- [ ] Overlay 正确显示结果

---

## 下一步

1. 确认方案后开始 Phase 1 实现
2. 每个 Phase 完成后进行测试验证
3. 根据测试结果调整设计
