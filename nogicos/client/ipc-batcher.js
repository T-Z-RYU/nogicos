/**
 * IPC 批量Send器
 * Phase 7.14: IPC 批量优化
 * 
 * 将High频Event批量Send，减少 IPC 调用次数
 */

class IPCBatcher {
  /**
   * @param {Electron.WebContents} webContents - Target webContents
   * @param {number} interval - 批量Send间隔（毫Second），Default 50ms
   */
  constructor(webContents, interval = 50) {
    this.webContents = webContents;
    this.queue = [];
    this.interval = interval;
    this._timer = null;
    this._destroyed = false;
    
    // TimerRefresh
    this._timer = setInterval(() => this.flush(), this.interval);
  }

  /**
   * AddEvent到Queue
   * @param {string} channel - IPC 通道名
   * @param {*} data - Event数据
   */
  send(channel, data) {
    if (this._destroyed) {
      console.warn('[IPCBatcher] Attempted to send after destroy');
      return;
    }
    
    this.queue.push({
      channel,
      data,
      timestamp: Date.now(),
    });
    
    // IfQueueoverLong，ImmediateRefresh
    if (this.queue.length >= 10) {
      this.flush();
    }
  }

  /**
   * RefreshQueue，批量Send
   */
  flush() {
    if (this.queue.length === 0) return;
    if (this._destroyed) return;
    
    // Check webContents YesNostillthenValid
    if (!this.webContents || this.webContents.isDestroyed()) {
      console.warn('[IPCBatcher] WebContents destroyed, clearing queue');
      this.queue = [];
      return;
    }
    
    // bychannelGroup
    const grouped = this._groupByChannel(this.queue);
    
    // SendBatchEvent
    for (const [channel, events] of Object.entries(grouped)) {
      if (events.length === 1) {
        // singleEventdirectlySend
        this.webContents.send(channel, events[0].data);
      } else {
        // multipleaEventBatchSend
        this.webContents.send(`${channel}:batch`, events.map(e => e.data));
      }
    }
    
    // clearEmptyQueue
    this.queue = [];
  }

  /**
   * 按通道分组
   * @private
   */
  _groupByChannel(events) {
    return events.reduce((acc, event) => {
      if (!acc[event.channel]) {
        acc[event.channel] = [];
      }
      acc[event.channel].push(event);
      return acc;
    }, {});
  }

  /**
   * GetQueueLength
   */
  getQueueLength() {
    return this.queue.length;
  }

  /**
   * 清EmptyQueue（不Send）
   */
  clear() {
    this.queue = [];
  }

  /**
   * Destroy批Handle器
   */
  destroy() {
    this._destroyed = true;
    
    // mostAfteronceRefresh
    this.flush();
    
    // ClearTimerer
    if (this._timer) {
      clearInterval(this._timer);
      this._timer = null;
    }
    
    this.queue = [];
    this.webContents = null;
  }

  /**
   * CheckYesNo已Destroy
   */
  isDestroyed() {
    return this._destroyed;
  }
}

/**
 * Create节流版本的 IPC Send器
 * 用于非常High频的Event（如鼠标Move）
 * @param {Electron.WebContents} webContents 
 * @param {string} channel 
 * @param {number} minInterval - MinSend间隔（毫Second）
 */
function createThrottledSender(webContents, channel, minInterval = 16) {
  let lastSendTime = 0;
  let pendingData = null;
  let timeoutId = null;

  return function send(data) {
    const now = Date.now();
    const timeSinceLastSend = now - lastSendTime;

    if (timeSinceLastSend >= minInterval) {
      // CanImmediateSend
      if (!webContents.isDestroyed()) {
        webContents.send(channel, data);
        lastSendTime = now;
      }
    } else {
      // StorageData，slightlyAfterSend
      pendingData = data;
      
      if (!timeoutId) {
        timeoutId = setTimeout(() => {
          if (!webContents.isDestroyed() && pendingData !== null) {
            webContents.send(channel, pendingData);
            lastSendTime = Date.now();
            pendingData = null;
          }
          timeoutId = null;
        }, minInterval - timeSinceLastSend);
      }
    }
  };
}

module.exports = { IPCBatcher, createThrottledSender };
