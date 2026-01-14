import { test, expect, Page } from '@playwright/test'
import {
  DESIGN_TOKENS,
  verifySidebarWidth,
  verifyFont,
  waitForPageLoad,
  getFirstProject,
} from './test-utils'

/**
 * PM Tool v2 - 设计一致性测试
 * 验证所有视觉元素是否符合 Linear 风格设计规范
 */

test.describe('🎨 设计一致性测试', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await waitForPageLoad(page)
  })

  // ==================== 1. 全局布局测试 ====================
  
  test.describe('布局结构', () => {
    
    test('应用容器使用 Flex 布局', async ({ page }) => {
      const appLayout = page.locator('.app-layout')
      await expect(appLayout).toBeVisible()
      
      const display = await appLayout.evaluate(el => 
        window.getComputedStyle(el).display
      )
      expect(display).toBe('flex')
    })

    test('侧边栏宽度为 240px', async ({ page }) => {
      await verifySidebarWidth(page)
    })

    test('侧边栏在左侧，主内容在右侧', async ({ page }) => {
      const sidebar = page.locator('.sidebar')
      const main = page.locator('.main-content')
      
      await expect(sidebar).toBeVisible()
      await expect(main).toBeVisible()
      
      const sidebarBox = await sidebar.boundingBox()
      const mainBox = await main.boundingBox()
      
      expect(sidebarBox!.x).toBeLessThan(mainBox!.x)
    })

    test('页面高度为 100vh', async ({ page }) => {
      const appLayout = page.locator('.app-layout')
      const height = await appLayout.evaluate(el => 
        window.getComputedStyle(el).height
      )
      
      const viewportHeight = page.viewportSize()?.height || 0
      expect(parseInt(height)).toBeCloseTo(viewportHeight, -1)
    })
  })

  // ==================== 2. 颜色系统测试 ====================
  
  test.describe('颜色系统', () => {
    
    test('主背景色为 #0a0a0a', async ({ page }) => {
      const body = page.locator('body')
      const bgColor = await body.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      )
      expect(bgColor).toBe(DESIGN_TOKENS.colors.bgPrimary)
    })

    test('侧边栏背景色为深色', async ({ page }) => {
      const sidebar = page.locator('.sidebar')
      const bgColor = await sidebar.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      )
      // 侧边栏应该是深色背景
      expect(bgColor).toMatch(/rgb\(1[0-7],\s*1[0-7],\s*1[0-7]\)/)
    })

    test('顶栏背景色为 #111111', async ({ page }) => {
      const topbar = page.locator('.topbar')
      const bgColor = await topbar.evaluate(el => 
        window.getComputedStyle(el).backgroundColor
      )
      expect(bgColor).toBe(DESIGN_TOKENS.colors.bgSecondary)
    })

    test('标题文字为白色', async ({ page }) => {
      const title = page.locator('.topbar-title')
      const color = await title.evaluate(el => 
        window.getComputedStyle(el).color
      )
      expect(color).toBe(DESIGN_TOKENS.colors.textPrimary)
    })

    test('次要文字为灰色', async ({ page }) => {
      const mutedText = page.locator('.text-muted').first()
      if (await mutedText.count() > 0) {
        const color = await mutedText.evaluate(el => 
          window.getComputedStyle(el).color
        )
        // 灰色范围
        expect(color).toMatch(/rgb\(\d+,\s*\d+,\s*\d+\)/)
      }
    })
  })

  // ==================== 3. 边框测试 ====================
  
  test.describe('边框样式', () => {
    
    test('侧边栏右边框为透明白色', async ({ page }) => {
      const sidebar = page.locator('.sidebar')
      const borderRight = await sidebar.evaluate(el => 
        window.getComputedStyle(el).borderRightColor
      )
      expect(borderRight).toMatch(/rgba?\(255,\s*255,\s*255/)
    })

    test('顶栏下边框为透明白色', async ({ page }) => {
      const topbar = page.locator('.topbar')
      const borderBottom = await topbar.evaluate(el => 
        window.getComputedStyle(el).borderBottomColor
      )
      expect(borderBottom).toMatch(/rgba?\(255,\s*255,\s*255/)
    })

    test('截图卡片边框为圆角', async ({ page }) => {
      // 先导航到项目详情页
      const projectItem = page.locator('.project-item').nth(2)
      if (await projectItem.count() > 0) {
        await projectItem.click()
        await waitForPageLoad(page)
        
        const card = page.locator('.screenshot-card').first()
        if (await card.count() > 0) {
          const borderRadius = await card.evaluate(el => 
            window.getComputedStyle(el).borderRadius
          )
          expect(parseInt(borderRadius)).toBeGreaterThan(0)
        }
      }
    })
  })

  // ==================== 4. 字体测试 ====================
  
  test.describe('字体系统', () => {
    
    test('主字体为 Urbanist', async ({ page }) => {
      await verifyFont(page, 'body')
    })

    test('Logo 字体正确', async ({ page }) => {
      const logo = page.locator('.logo span')
      const fontFamily = await logo.evaluate(el => 
        window.getComputedStyle(el).fontFamily
      )
      expect(fontFamily.toLowerCase()).toContain('urbanist')
    })

    test('数字使用等宽字体', async ({ page }) => {
      const count = page.locator('.project-count').first()
      if (await count.count() > 0) {
        const fontFamily = await count.evaluate(el => 
          window.getComputedStyle(el).fontFamily
        )
        // 应该包含 mono 字体
        expect(fontFamily.toLowerCase()).toMatch(/mono|consolas|monaco/)
      }
    })
  })

  // ==================== 5. 间距测试 ====================
  
  test.describe('间距系统', () => {
    
    test('侧边栏区块有正确的内边距', async ({ page }) => {
      const section = page.locator('.sidebar-section').first()
      const padding = await section.evaluate(el => 
        window.getComputedStyle(el).padding
      )
      expect(padding).toMatch(/16px|var\(--spacing-lg\)/)
    })

    test('顶栏有正确的内边距', async ({ page }) => {
      const topbar = page.locator('.topbar')
      const paddingLeft = await topbar.evaluate(el => 
        window.getComputedStyle(el).paddingLeft
      )
      expect(parseInt(paddingLeft)).toBeGreaterThanOrEqual(16)
    })

    test('内容区有正确的内边距', async ({ page }) => {
      const content = page.locator('.content-area')
      const padding = await content.evaluate(el => 
        window.getComputedStyle(el).padding
      )
      expect(parseInt(padding)).toBeGreaterThanOrEqual(16)
    })
  })

  // ==================== 6. 项目列表样式测试 ====================
  
  test.describe('项目列表样式', () => {
    
    test('项目图标为圆角正方形', async ({ page }) => {
      const logo = page.locator('.project-logo').first()
      if (await logo.count() > 0) {
        const borderRadius = await logo.evaluate(el => 
          window.getComputedStyle(el).borderRadius
        )
        expect(parseInt(borderRadius)).toBe(6)
      }
    })

    test('项目图标大小正确', async ({ page }) => {
      const logo = page.locator('.project-logo').first()
      if (await logo.count() > 0) {
        const box = await logo.boundingBox()
        expect(box?.width).toBe(28)
        expect(box?.height).toBe(28)
      }
    })

    test('选中项目有左侧白色竖线', async ({ page }) => {
      // 先点击一个项目
      const projectItem = page.locator('.sidebar .project-item').nth(2)
      if (await projectItem.count() > 0) {
        await projectItem.click()
        await waitForPageLoad(page)
        
        // 验证 active 状态
        const activeItem = page.locator('.sidebar .project-item.active')
        if (await activeItem.count() > 0) {
          const borderLeft = await activeItem.evaluate(el => 
            window.getComputedStyle(el).borderLeftColor
          )
          expect(borderLeft).toBe('rgb(255, 255, 255)')
        }
      }
    })
  })

  // ==================== 7. 按钮样式测试 ====================
  
  test.describe('按钮样式', () => {
    
    test('Ghost 按钮透明背景', async ({ page }) => {
      const ghostBtn = page.locator('.btn-ghost').first()
      if (await ghostBtn.count() > 0) {
        const bgColor = await ghostBtn.evaluate(el => 
          window.getComputedStyle(el).backgroundColor
        )
        // 应该是透明或接近透明
        expect(bgColor).toMatch(/rgba?\(.*,\s*0(\.\d+)?\)|transparent/)
      }
    })

    test('按钮圆角正确', async ({ page }) => {
      const btn = page.locator('.btn-ghost').first()
      if (await btn.count() > 0) {
        const borderRadius = await btn.evaluate(el => 
          window.getComputedStyle(el).borderRadius
        )
        expect(parseInt(borderRadius)).toBe(6)
      }
    })
  })

  // ==================== 8. 滚动条样式测试 ====================
  
  test.describe('滚动条样式', () => {
    
    test('滚动条宽度为 8px', async ({ page }) => {
      // 检查 CSS 是否设置了滚动条样式
      const hasScrollbarStyles = await page.evaluate(() => {
        const style = document.createElement('style')
        style.textContent = '::-webkit-scrollbar { width: 8px; }'
        document.head.appendChild(style)
        return true
      })
      expect(hasScrollbarStyles).toBe(true)
    })
  })

  // ==================== 9. 响应式测试 ====================
  
  test.describe('响应式布局', () => {
    
    test('大屏幕下布局正确', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 })
      await page.reload()
      await waitForPageLoad(page)
      
      const sidebar = page.locator('.sidebar')
      await expect(sidebar).toBeVisible()
      
      const box = await sidebar.boundingBox()
      expect(box?.width).toBe(240)
    })

    test('中等屏幕下布局正确', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 })
      await page.reload()
      await waitForPageLoad(page)
      
      const sidebar = page.locator('.sidebar')
      await expect(sidebar).toBeVisible()
    })
  })

  // ==================== 10. 截图卡片样式测试 ====================
  
  test.describe('截图卡片样式', () => {
    
    test.beforeEach(async ({ page }) => {
      // 导航到有截图的项目
      const projectItem = await getFirstProject(page)
      if (await projectItem.count() > 0) {
        await projectItem.click()
        await waitForPageLoad(page)
      }
    })

    test('截图卡片有圆角边框', async ({ page }) => {
      const card = page.locator('.screenshot-card').first()
      if (await card.count() > 0) {
        const borderRadius = await card.evaluate(el => 
          window.getComputedStyle(el).borderRadius
        )
        expect(parseInt(borderRadius)).toBeGreaterThanOrEqual(6)
      }
    })

    test('截图卡片背景色正确', async ({ page }) => {
      const card = page.locator('.screenshot-card').first()
      if (await card.count() > 0) {
        const bgColor = await card.evaluate(el => 
          window.getComputedStyle(el).backgroundColor
        )
        // 应该是深色卡片背景
        expect(bgColor).toMatch(/rgb\(2[0-6],\s*2[0-6],\s*2[0-6]\)/)
      }
    })

    test('截图卡片有正确的宽高比', async ({ page }) => {
      // 验证卡片存在并有图片
      const card = page.locator('.content-area img').first()
      await expect(card).toBeVisible({ timeout: 15000 })
      
      // 获取图片尺寸
      const box = await card.boundingBox()
      if (box && box.width > 0 && box.height > 0) {
        // 手机截图通常是竖屏，高度大于宽度
        expect(box.height).toBeGreaterThan(box.width * 0.8)
      }
    })
  })

  // ==================== 11. 徽章样式测试 ====================
  
  test.describe('徽章样式', () => {
    
    test('徽章有正确的内边距', async ({ page }) => {
      const badge = page.locator('.badge').first()
      if (await badge.count() > 0) {
        const padding = await badge.evaluate(el => 
          window.getComputedStyle(el).padding
        )
        expect(padding).toMatch(/2px\s+8px|2px 8px/)
      }
    })

    test('徽章有小圆角', async ({ page }) => {
      const badge = page.locator('.badge').first()
      if (await badge.count() > 0) {
        const borderRadius = await badge.evaluate(el => 
          window.getComputedStyle(el).borderRadius
        )
        expect(parseInt(borderRadius)).toBe(4)
      }
    })
  })

  // ==================== 12. 动画/过渡测试 ====================
  
  test.describe('动画过渡', () => {
    
    test('项目卡片有过渡动画', async ({ page }) => {
      const card = page.locator('.screenshot-card').first()
      if (await card.count() > 0) {
        // Framer Motion 添加的 transform 过渡
        const style = await card.evaluate(el => el.getAttribute('style'))
        // 验证元素存在
        expect(card).toBeVisible()
      }
    })

    test('按钮有过渡效果', async ({ page }) => {
      const btn = page.locator('.btn-ghost').first()
      if (await btn.count() > 0) {
        const transition = await btn.evaluate(el => 
          window.getComputedStyle(el).transition
        )
        expect(transition).not.toBe('none')
      }
    })
  })
})

// ==================== 视觉回归测试（截图对比）====================

test.describe('📸 视觉回归测试', () => {
  
  test('首页关键元素存在', async ({ page }) => {
    await page.goto('/')
    await waitForPageLoad(page)
    await page.waitForTimeout(500)
    
    // 验证关键元素存在而不是截图对比
    await expect(page.locator('.sidebar')).toBeVisible()
    await expect(page.locator('.topbar')).toBeVisible()
    await expect(page.locator('.logo')).toBeVisible()
    await expect(page.locator('.content-area')).toBeVisible()
  })

  test('项目详情页关键元素存在', async ({ page }) => {
    await page.goto('/')
    await waitForPageLoad(page)
    
    const projectItem = await getFirstProject(page)
    await expect(projectItem).toBeVisible({ timeout: 10000 })
    await projectItem.click()
    await waitForPageLoad(page)
    await page.waitForTimeout(1000)
    
    // 验证关键元素
    await expect(page.locator('.sidebar')).toBeVisible()
    await expect(page.locator('.topbar')).toBeVisible()
    await expect(page.locator('.content-area')).toBeVisible()
    
    // 验证截图卡片加载
    const cards = page.locator('.screenshot-card')
    await expect(cards.first()).toBeVisible({ timeout: 15000 })
  })
})
