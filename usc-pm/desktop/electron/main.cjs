const { app, BrowserWindow, shell, ipcMain, protocol } = require("electron");
const path = require("path");

const isDev = !app.isPackaged;

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1180,
    height: 760,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: "#0a0a0a",
    autoHideMenuBar: true,
    title: "USC PM",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    mainWindow.loadURL("http://localhost:1420");
  } else {
    mainWindow.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }

  // External links open in user's real browser, not inside Electron
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
}

// Register a custom protocol so backend can deep-link tokens back into the app:
// usc-pm://auth?token=xxx
app.setAsDefaultProtocolClient("usc-pm");

// Single instance — needed for protocol handler on Windows
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on("second-instance", (_event, argv) => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
      // On Windows, the deep-link URL is in argv
      const deepLink = argv.find((a) => a.startsWith("usc-pm://"));
      if (deepLink) mainWindow.webContents.send("deep-link", deepLink);
    }
  });

  app.whenReady().then(() => {
    createWindow();
    // macOS deep link
    app.on("open-url", (event, url) => {
      event.preventDefault();
      if (mainWindow) mainWindow.webContents.send("deep-link", url);
    });
  });
}

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
