import { defineConfig, devices } from '@playwright/test'

/**
 * Vitaflow 设计一致性测试配置
 */
export default defineConfig({
  testDir: './tests',
  
  /* 并行运行测试 */
  fullyParallel: true,
  
  /* CI 上禁止 test.only */
  forbidOnly: !!process.env.CI,
  
  /* 失败重试次数 */
  retries: process.env.CI ? 2 : 0,
  
  /* 并行工作线程数 */
  workers: process.env.CI ? 1 : undefined,
  
  /* 测试报告 */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],
  
  /* 全局设置 */
  use: {
    /* 基础URL */
    baseURL: 'http://localhost:5173',
    
    /* 收集失败测试的trace */
    trace: 'on-first-retry',
    
    /* 截图设置 */
    screenshot: 'only-on-failure',
    
    /* 视频录制 */
    video: 'on-first-retry',
  },

  /* 截图对比设置 */
  expect: {
    toHaveScreenshot: {
      /* 允许的像素差异阈值 */
      maxDiffPixels: 100,
      
      /* 允许的像素差异百分比 */
      maxDiffPixelRatio: 0.02,
      
      /* 动画稳定等待时间 */
      animations: 'disabled',
      
      /* 截图比较阈值 */
      threshold: 0.2,
    },
  },

  /* 项目配置 - 模拟移动设备 */
  projects: [
    {
      name: 'Mobile Design Test',
      use: {
        /* 自定义移动设备视口 - 匹配 Figma 设计尺寸 */
        viewport: { width: 402, height: 874 },
        deviceScaleFactor: 2,
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'Desktop Preview',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 900 },
      },
    },
  ],

  /* 本地开发服务器 */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
})
