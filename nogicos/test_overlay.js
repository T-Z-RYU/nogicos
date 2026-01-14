/**
 * FastTest Overlay 功能
 * 在 Electron 主Process控制台Running
 */

const { BrowserWindow } = require('electron');

// Import overlay Controller
const overlayController = require('./client/overlay-controller');

async function testOverlay() {
  console.log('=== Testing Overlay ===');
  
  const manager = overlayController.getOverlayManager();
  console.log('Overlay available:', manager.isAvailable);
  
  if (manager.isAvailable) {
    // tryAttachto Notepad
    console.log('Attaching to Notepad...');
    const result = manager.attach('Notepad', 'desktop');
    console.log('Result:', result);
  }
}

testOverlay();
