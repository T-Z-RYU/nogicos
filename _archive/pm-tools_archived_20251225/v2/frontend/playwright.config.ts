import { defineConfig, devices } from '@playwright/test'

/**
 * PM Tool v2 - Playwright 测试配置
 * 全面测试：设计一致性 + 用户流程 + 可访问性 + 性能 + API
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  // 测试报告
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['list'],
    ['json', { outputFile: 'test-results/results.json' }],
  ],
  
  // 全局配置
  use: {
    baseURL: 'http://localhost:3001',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    
    // 视觉回归测试配置
    ignoreHTTPSErrors: true,
    
    // 动作超时
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // 全局超时
  timeout: 60000,
  
  // 期望配置
  expect: {
    // 视觉对比配置
    toHaveScreenshot: {
      maxDiffPixels: 100,
      threshold: 0.3,
      animations: 'disabled',
    },
    toMatchSnapshot: {
      maxDiffPixels: 100,
    },
  },

  // 测试项目（多浏览器）
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    // 移动端测试（可选）
    // {
    //   name: 'mobile-chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
  ],

  // 测试前确保服务已启动
  webServer: [
    {
      command: 'npm run dev',
      url: 'http://localhost:3001',
      reuseExistingServer: true,
      timeout: 120 * 1000,
    },
  ],

  // 快照目录
  snapshotDir: './tests/snapshots',
  
  // 输出目录
  outputDir: './test-results',
})
