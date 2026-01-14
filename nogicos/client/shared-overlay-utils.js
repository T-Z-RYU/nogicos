/**
 * NogicOS Shared Overlay Utilities
 *
 * Centralized utilities for overlay HTML generation and sound effects.
 * Used by: overlay.js, overlay-controller.js, multi-overlay-manager.js
 */

/**
 * Overlay visual configuration
 */
const OVERLAY_CONFIG = {
  height: 28,
  padding: 8,
  backgroundColor: 'rgba(16, 185, 129, 0.9)',
  textColor: '#ffffff',
  borderRadius: 4,
  fontSize: 12,
  updateInterval: 100,
};

/**
 * HTML escape utility to prevent XSS
 * @param {string} str - String to escape
 * @returns {string} Escaped string
 */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Generate overlay HTML content - Basic style
 * @param {string} label - Label text
 * @returns {string} HTML content
 */
function generateBasicOverlayHTML(label) {
  const safeLabel = escapeHtml(label);

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
    .overlay-bar {
      position: absolute;
      top: 0;
      left: ${OVERLAY_CONFIG.padding}px;
      right: ${OVERLAY_CONFIG.padding}px;
      height: ${OVERLAY_CONFIG.height}px;
      display: flex;
      align-items: center;
      padding: 0 12px;
      background: ${OVERLAY_CONFIG.backgroundColor};
      border-radius: 0 0 ${OVERLAY_CONFIG.borderRadius}px ${OVERLAY_CONFIG.borderRadius}px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: ${OVERLAY_CONFIG.fontSize}px;
      color: ${OVERLAY_CONFIG.textColor};
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    .status-dot {
      width: 8px;
      height: 8px;
      background: #fff;
      border-radius: 50%;
      margin-right: 8px;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    .label { font-weight: 500; letter-spacing: 0.3px; }
  </style>
</head>
<body>
  <div class="overlay-bar">
    <div class="status-dot"></div>
    <span class="label">${safeLabel}</span>
  </div>
</body>
</html>
  `;
}

/**
 * Generate sound effect script for overlay HTML
 * @returns {string} JavaScript code for sound effects
 */
function generateSoundEffectScript() {
  return `
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();

    function playSound(type) {
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      if (type === 'connect') {
        oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(800, audioContext.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15);
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.15);
      } else if (type === 'disconnect') {
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(300, audioContext.currentTime + 0.15);
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
      } else if (type === 'action') {
        oscillator.frequency.setValueAtTime(1000, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.05);
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.05);
      }
    }
  `;
}

/**
 * Hook type icons mapping
 */
const HOOK_ICONS = {
  browser: '🌐',
  desktop: '🖥️',
  file: '📁',
};

/**
 * Status colors mapping
 */
const STATUS_COLORS = {
  connected: '#10b981',
  working: '#f59e0b',
  error: '#ef4444',
};

module.exports = {
  OVERLAY_CONFIG,
  escapeHtml,
  generateBasicOverlayHTML,
  generateSoundEffectScript,
  HOOK_ICONS,
  STATUS_COLORS,
};
