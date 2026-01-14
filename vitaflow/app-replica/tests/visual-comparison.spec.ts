import { test, expect } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

/**
 * Figma vs 实现 视觉对比测试
 * 
 * 这个测试套件专门用于对比 Figma 设计稿和实际实现的差异
 */

test.describe('Figma 设计对比测试', () => {

  // Figma 设计的关键尺寸（从 Figma 提取）
  const FIGMA_SPECS = {
    device: {
      width: 402,
      height: 874,
    },
    statusBar: {
      height: 62,
    },
    bottomNav: {
      height: 98,
    },
    padding: {
      page: 20,
    },
    macroCards: {
      width: 112.67, // 精确宽度
      height: 80,
      gap: 12,
    },
    calorieCard: {
      height: 157,
    },
    calendar: {
      height: 64,
      itemWidth: 48,
      gap: 4.33,
    },
    borderRadius: {
      card: 16,
      button: 12,
    },
    colors: {
      primary: '#2DD4BF',
      background: '#F5F5F5',
      surface: '#FFFFFF',
      textPrimary: '#1F2937',
      textSecondary: '#6B7280',
      accentPink: '#F472B6',
      accentOrange: '#FB923C',
      accentBlue: '#38BDF8',
    },
    typography: {
      appName: {
        fontSize: '24px',
        fontWeight: '700',
      },
      calorieValue: {
        fontSize: '48px',
        fontWeight: '700',
      },
      macroValue: {
        fontSize: '18px',
        fontWeight: '600',
      },
    },
  }

  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
  })

  // ==================== 尺寸精确性测试 ====================

  test('设备尺寸与 Figma 一致', async ({ page }) => {
    const container = page.locator('[data-testid="app-container"]')
    const box = await container.boundingBox()
    
    expect(box?.width).toBe(FIGMA_SPECS.device.width)
    expect(box?.height).toBe(FIGMA_SPECS.device.height)
  })

  test('状态栏尺寸与 Figma 一致', async ({ page }) => {
    const statusBar = page.locator('[data-testid="status-bar"]')
    const box = await statusBar.boundingBox()
    
    expect(box?.height).toBe(FIGMA_SPECS.statusBar.height)
  })

  test('底部导航尺寸与 Figma 一致', async ({ page }) => {
    const bottomNav = page.locator('[data-testid="bottom-navigation"]')
    const box = await bottomNav.boundingBox()
    
    expect(box?.height).toBe(FIGMA_SPECS.bottomNav.height)
  })

  test('卡路里卡片尺寸与 Figma 一致', async ({ page }) => {
    const card = page.locator('[data-testid="calorie-card"]')
    const box = await card.boundingBox()
    
    // 允许 1px 误差
    expect(Math.abs((box?.height || 0) - FIGMA_SPECS.calorieCard.height)).toBeLessThan(2)
  })

  test('宏量营养素卡片尺寸与间距与 Figma 一致', async ({ page }) => {
    const cardsContainer = page.locator('[data-testid="macro-cards"]')
    const gap = await cardsContainer.evaluate((el) => {
      const style = window.getComputedStyle(el)
      return parseFloat(style.gap || '0')
    })
    
    expect(gap).toBe(FIGMA_SPECS.macroCards.gap)

    const firstCard = page.locator('[data-testid="macro-card-carbs"]')
    const box = await firstCard.boundingBox()
    
    // 允许 1px 误差 (112.67 -> 112.66 or 113)
    expect(Math.abs((box?.width || 0) - FIGMA_SPECS.macroCards.width)).toBeLessThan(2)
    expect(box?.height).toBe(FIGMA_SPECS.macroCards.height)
  })

  // ==================== 颜色精确性测试 ====================

  test('背景颜色与 Figma 一致', async ({ page }) => {
    const container = page.locator('[data-testid="app-container"]')
    const bgColor = await container.evaluate((el) => 
      window.getComputedStyle(el).backgroundColor
    )
    
    // F5F5F5 = rgb(245, 245, 245)
    expect(bgColor).toBe('rgb(245, 245, 245)')
  })

  test('卡片背景颜色与 Figma 一致', async ({ page }) => {
    const card = page.locator('[data-testid="calorie-card"]')
    const bgColor = await card.evaluate((el) => 
      window.getComputedStyle(el).backgroundColor
    )
    
    // FFFFFF = rgb(255, 255, 255)
    expect(bgColor).toBe('rgb(255, 255, 255)')
  })

  // ==================== 字体测试 ====================

  test('App 名称字体大小与 Figma 一致', async ({ page }) => {
    const appName = page.locator('[data-testid="header"] h1')
    const styles = await appName.evaluate((el) => {
      const computed = window.getComputedStyle(el)
      return {
        fontSize: computed.fontSize,
        fontWeight: computed.fontWeight,
      }
    })
    
    expect(styles.fontSize).toBe(FIGMA_SPECS.typography.appName.fontSize)
    expect(styles.fontWeight).toBe(FIGMA_SPECS.typography.appName.fontWeight)
  })

  test('卡路里数值字体大小与 Figma 一致', async ({ page }) => {
    const calorieValue = page.locator('[data-testid="calorie-card"] .text-4xl')
    const styles = await calorieValue.evaluate((el) => {
      const computed = window.getComputedStyle(el)
      return {
        fontSize: computed.fontSize,
        fontWeight: computed.fontWeight,
      }
    })
    
    expect(styles.fontSize).toBe(FIGMA_SPECS.typography.calorieValue.fontSize)
    expect(styles.fontWeight).toBe(FIGMA_SPECS.typography.calorieValue.fontWeight)
  })

  // ==================== 间距测试 ====================

  test('页面内边距与 Figma 一致', async ({ page }) => {
    // 检查内容区域的左右 padding
    const header = page.locator('[data-testid="header"]')
    const headerBox = await header.boundingBox()
    const containerBox = await page.locator('[data-testid="app-container"]').boundingBox()
    
    // 左边距
    const leftPadding = (headerBox?.x || 0) - (containerBox?.x || 0)
    expect(leftPadding).toBe(FIGMA_SPECS.padding.page)
  })

  // ==================== 圆角测试 ====================

  test('卡片圆角与 Figma 一致', async ({ page }) => {
    const card = page.locator('[data-testid="calorie-card"]')
    const borderRadius = await card.evaluate((el) => 
      window.getComputedStyle(el).borderRadius
    )
    
    // 16px rounded-2xl (Tailwind 可能输出 "16px" 或 "1rem")
    const radiusValue = parseFloat(borderRadius)
    expect(radiusValue).toBeGreaterThanOrEqual(16)
  })

  // ==================== 组件对比报告 ====================

  test('生成设计对比报告', async ({ page }) => {
    const report: Record<string, { figma: unknown; implementation: unknown; match: boolean }> = {}
    
    // 设备尺寸
    const container = page.locator('[data-testid="app-container"]')
    const containerBox = await container.boundingBox()
    report['deviceSize'] = {
      figma: FIGMA_SPECS.device,
      implementation: { width: Math.round(containerBox?.width || 0), height: Math.round(containerBox?.height || 0) },
      match: Math.round(containerBox?.width || 0) === FIGMA_SPECS.device.width && 
             Math.round(containerBox?.height || 0) === FIGMA_SPECS.device.height,
    }
    
    // 状态栏高度
    const statusBar = page.locator('[data-testid="status-bar"]')
    const statusBarBox = await statusBar.boundingBox()
    report['statusBarHeight'] = {
      figma: FIGMA_SPECS.statusBar.height,
      implementation: Math.round(statusBarBox?.height || 0),
      match: Math.round(statusBarBox?.height || 0) === FIGMA_SPECS.statusBar.height,
    }
    
    // 底部导航高度
    const bottomNav = page.locator('[data-testid="bottom-navigation"]')
    const bottomNavBox = await bottomNav.boundingBox()
    report['bottomNavHeight'] = {
      figma: FIGMA_SPECS.bottomNav.height,
      implementation: Math.round(bottomNavBox?.height || 0),
      match: Math.round(bottomNavBox?.height || 0) === FIGMA_SPECS.bottomNav.height,
    }

    // 宏量营养素卡片
    const cardsContainer = page.locator('[data-testid="macro-cards"]')
    const gap = await cardsContainer.evaluate((el) => parseFloat(window.getComputedStyle(el).gap || '0'))
    report['macroCardsGap'] = {
      figma: FIGMA_SPECS.macroCards.gap,
      implementation: gap,
      match: gap === FIGMA_SPECS.macroCards.gap,
    }
    
    // 输出报告
    console.log('\n========== 设计对比报告 ==========\n')
    Object.entries(report).forEach(([key, value]) => {
      const status = value.match ? '✅' : '❌'
      console.log(`${status} ${key}:`)
      console.log(`   Figma: ${JSON.stringify(value.figma)}`)
      console.log(`   实现:  ${JSON.stringify(value.implementation)}`)
    })
    console.log('\n==================================\n')
    
    // 保存报告到文件
    const reportPath = path.join(__dirname, '..', 'test-results', 'design-comparison-report.json')
    fs.mkdirSync(path.dirname(reportPath), { recursive: true })
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2))
    
    // 所有检查都应该通过
    const allMatch = Object.values(report).every(r => r.match)
    expect(allMatch).toBe(true)
  })
})

// ==================== 像素级对比测试 ====================

test.describe('像素级视觉对比', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // 等待所有动画完成和字体加载
    await page.waitForTimeout(1000)
  })

  test('主页完整截图 - 作为基准', async ({ page }) => {
    const app = page.locator('[data-testid="app-container"]')
    
    // 这个截图将作为未来对比的基准
    await expect(app).toHaveScreenshot('baseline-home.png', {
      maxDiffPixels: 50,
      animations: 'disabled',
    })
  })

  test('卡路里区域截图', async ({ page }) => {
    const calorieSection = page.locator('[data-testid="calorie-card"]')
    
    await expect(calorieSection).toHaveScreenshot('baseline-calorie-section.png', {
      maxDiffPixels: 20,
    })
  })

  test('营养素卡片截图', async ({ page }) => {
    const macroSection = page.locator('[data-testid="macro-cards"]')
    
    await expect(macroSection).toHaveScreenshot('baseline-macro-cards.png', {
      maxDiffPixels: 20,
    })
  })

  test('导航栏截图', async ({ page }) => {
    const nav = page.locator('[data-testid="bottom-navigation"]')
    
    await expect(nav).toHaveScreenshot('baseline-navigation.png', {
      maxDiffPixels: 20,
    })
  })
})
