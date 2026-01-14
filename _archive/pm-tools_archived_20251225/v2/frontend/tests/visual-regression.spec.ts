import { test, expect } from '@playwright/test'
import { waitForPageLoad, getFirstProject } from './test-utils'

/**
 * PM Tool v2 - 视觉回归测试
 * 使用 Playwright 的 toHaveScreenshot 进行像素级对比
 * 
 * 首次运行会生成基准截图，后续运行会对比变化
 * 更新基准：npx playwright test --update-snapshots
 */

test.describe('📸 视觉回归测试', () => {
  
  // ==================== 页面级截图 ====================
  
  test.describe('页面完整截图', () => {
    
    test('首页 - 全页截图', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      await page.waitForTimeout(500) // 等待动画完成
      
      await expect(page).toHaveScreenshot('home-page.png', {
        fullPage: true,
        maxDiffPixels: 100, // 允许少量像素差异
      })
    })

    test('Onboarding 页面 - 全页截图', async ({ page }) => {
      await page.goto('/onboarding')
      await waitForPageLoad(page)
      await page.waitForTimeout(500)
      
      await expect(page).toHaveScreenshot('onboarding-page.png', {
        fullPage: true,
        maxDiffPixels: 100,
      })
    })

    test('排序页面 - 全页截图', async ({ page }) => {
      await page.goto('/sort')
      await waitForPageLoad(page)
      await page.waitForTimeout(500)
      
      await expect(page).toHaveScreenshot('sort-page.png', {
        fullPage: true,
        maxDiffPixels: 100,
      })
    })

    test('商城对比页面 - 全页截图', async ({ page }) => {
      await page.goto('/store')
      await waitForPageLoad(page)
      await page.waitForTimeout(500)
      
      await expect(page).toHaveScreenshot('store-page.png', {
        fullPage: true,
        maxDiffPixels: 100,
      })
    })

    test('分类页面 - 全页截图', async ({ page }) => {
      await page.goto('/classify')
      await waitForPageLoad(page)
      await page.waitForTimeout(500)
      
      await expect(page).toHaveScreenshot('classify-page.png', {
        fullPage: true,
        maxDiffPixels: 100,
      })
    })
  })

  // ==================== 组件级截图 ====================
  
  test.describe('组件截图', () => {
    
    test('侧边栏组件', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const sidebar = page.locator('.sidebar')
      await expect(sidebar).toHaveScreenshot('sidebar.png', {
        maxDiffPixels: 50,
      })
    })

    test('顶部导航栏', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const topbar = page.locator('.topbar')
      await expect(topbar).toHaveScreenshot('topbar.png', {
        maxDiffPixels: 50,
      })
    })

    test('项目卡片', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 进入项目详情
      const project = await getFirstProject(page)
      if (await project.count() > 0) {
        await project.click()
        await waitForPageLoad(page)
        await page.waitForTimeout(1000)
        
        const card = page.locator('.screenshot-card').first()
        if (await card.count() > 0) {
          await expect(card).toHaveScreenshot('screenshot-card.png', {
            maxDiffPixels: 50,
          })
        }
      }
    })
  })

  // ==================== 响应式截图 ====================
  
  test.describe('响应式布局截图', () => {
    
    test('1920x1080 大屏', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 })
      await page.goto('/')
      await waitForPageLoad(page)
      
      await expect(page).toHaveScreenshot('home-1920x1080.png', {
        fullPage: true,
        maxDiffPixels: 100,
      })
    })

    test('1440x900 中等屏幕', async ({ page }) => {
      await page.setViewportSize({ width: 1440, height: 900 })
      await page.goto('/')
      await waitForPageLoad(page)
      
      await expect(page).toHaveScreenshot('home-1440x900.png', {
        fullPage: true,
        maxDiffPixels: 100,
      })
    })

    test('1280x720 小桌面', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 })
      await page.goto('/')
      await waitForPageLoad(page)
      
      await expect(page).toHaveScreenshot('home-1280x720.png', {
        fullPage: true,
        maxDiffPixels: 100,
      })
    })
  })

  // ==================== 交互状态截图 ====================
  
  test.describe('交互状态截图', () => {
    
    test('按钮 Hover 状态', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const btn = page.locator('.btn-ghost').first()
      if (await btn.count() > 0) {
        await btn.hover()
        await page.waitForTimeout(200)
        await expect(btn).toHaveScreenshot('button-hover.png', {
          maxDiffPixels: 30,
        })
      }
    })

    test('项目选中状态', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const project = page.locator('.sidebar .project-item').nth(2)
      if (await project.count() > 0) {
        await project.click()
        await waitForPageLoad(page)
        
        const activeItem = page.locator('.sidebar .project-item.active')
        if (await activeItem.count() > 0) {
          await expect(activeItem).toHaveScreenshot('project-active.png', {
            maxDiffPixels: 30,
          })
        }
      }
    })
  })
})

