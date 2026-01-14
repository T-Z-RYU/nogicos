import { Page, expect } from '@playwright/test'

/**
 * PM Tool v2 - 测试工具函数
 * 设计系统验证 + 交互测试辅助
 */

// ==================== 设计系统期望值（复刻老版参数）====================

export const DESIGN_TOKENS = {
  // 背景色
  colors: {
    bgPrimary: 'rgb(10, 10, 10)',       // #0a0a0a
    bgSecondary: 'rgb(17, 17, 17)',     // #111111
    bgCard: 'rgb(26, 26, 26)',          // #1a1a1a
    bgSidebar: 'rgb(13, 13, 13)',       // #0d0d0d
    textPrimary: 'rgb(255, 255, 255)',  // #ffffff
    textSecondary: 'rgb(156, 163, 175)', // #9ca3af
    textMuted: 'rgb(107, 114, 128)',    // #6b7280
    success: 'rgb(34, 197, 94)',        // #22c55e
    danger: 'rgb(239, 68, 68)',         // #ef4444
    warning: 'rgb(245, 158, 11)',       // #f59e0b
  },
  
  // 圆角
  radius: {
    sm: '4px',
    md: '6px',
    lg: '8px',
    xl: '12px',
  },
  
  // 间距
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
  },
  
  // 侧边栏
  sidebar: {
    width: '240px',
  },
  
  // 字体
  fonts: {
    primary: 'Urbanist',
  },
}

// ==================== 设计验证函数 ====================

/**
 * 验证元素的 CSS 属性
 */
export async function verifyCSSProperty(
  page: Page,
  selector: string,
  property: string,
  expectedValue: string | RegExp
) {
  const element = page.locator(selector).first()
  await expect(element).toBeVisible()
  
  const value = await element.evaluate((el, prop) => {
    return window.getComputedStyle(el).getPropertyValue(prop)
  }, property)
  
  if (typeof expectedValue === 'string') {
    expect(value.trim()).toBe(expectedValue)
  } else {
    expect(value.trim()).toMatch(expectedValue)
  }
}

/**
 * 验证背景色
 */
export async function verifyBackgroundColor(page: Page, selector: string, expectedColor: string) {
  await verifyCSSProperty(page, selector, 'background-color', expectedColor)
}

/**
 * 验证文字颜色
 */
export async function verifyTextColor(page: Page, selector: string, expectedColor: string) {
  await verifyCSSProperty(page, selector, 'color', expectedColor)
}

/**
 * 验证边框
 */
export async function verifyBorder(page: Page, selector: string) {
  const element = page.locator(selector).first()
  const borderColor = await element.evaluate((el) => {
    return window.getComputedStyle(el).borderColor
  })
  // 边框应该是半透明白色
  expect(borderColor).toMatch(/rgba?\(255,\s*255,\s*255/)
}

/**
 * 验证侧边栏宽度
 */
export async function verifySidebarWidth(page: Page) {
  const sidebar = page.locator('.sidebar').first()
  await expect(sidebar).toBeVisible()
  const box = await sidebar.boundingBox()
  expect(box?.width).toBe(240)
}

/**
 * 验证字体
 */
export async function verifyFont(page: Page, selector: string) {
  const element = page.locator(selector).first()
  const fontFamily = await element.evaluate((el) => {
    return window.getComputedStyle(el).fontFamily
  })
  expect(fontFamily.toLowerCase()).toContain('urbanist')
}

// ==================== 交互测试函数 ====================

/**
 * 等待页面完全加载
 */
export async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle')
  // 等待 spinner 消失
  await page.waitForSelector('.spinner', { state: 'hidden', timeout: 10000 }).catch(() => {})
}

/**
 * 验证导航跳转
 */
export async function verifyNavigation(page: Page, clickSelector: string, expectedUrl: string | RegExp) {
  await page.locator(clickSelector).first().click()
  await waitForPageLoad(page)
  await expect(page).toHaveURL(expectedUrl)
}

/**
 * 验证 hover 效果
 */
export async function verifyHoverEffect(page: Page, selector: string) {
  const element = page.locator(selector).first()
  await expect(element).toBeVisible()
  
  // 获取初始样式
  const initialBg = await element.evaluate((el) => {
    return window.getComputedStyle(el).backgroundColor
  })
  
  // 悬停
  await element.hover()
  await page.waitForTimeout(300) // 等待过渡动画
  
  // 验证样式变化（可能是背景色、边框色等）
  const hoverBg = await element.evaluate((el) => {
    return window.getComputedStyle(el).backgroundColor
  })
  
  // 至少应该有某种变化或保持设计要求
  return { initialBg, hoverBg }
}

/**
 * 验证截图查看器
 */
export async function verifyScreenshotViewer(page: Page) {
  // 点击第一张截图
  const screenshotCard = page.locator('.screenshot-card').first()
  await expect(screenshotCard).toBeVisible()
  await screenshotCard.click()
  
  // 验证查看器打开
  await page.waitForTimeout(300)
  const viewer = page.locator('[style*="position: fixed"]').first()
  await expect(viewer).toBeVisible()
  
  return viewer
}

/**
 * 验证键盘导航
 */
export async function verifyKeyboardNavigation(page: Page) {
  // 验证左右箭头键导航
  const initialIndex = await page.locator('span:has-text("#")').first().textContent()
  
  await page.keyboard.press('ArrowRight')
  await page.waitForTimeout(300)
  
  const newIndex = await page.locator('span:has-text("#")').first().textContent()
  
  return { initialIndex, newIndex }
}

/**
 * 获取项目列表（仅项目，不包括导航和工具链接）
 */
export async function getProjectList(page: Page) {
  await waitForPageLoad(page)
  // 使用 CSS 选择器选择"项目"区域中的项目
  const projectSection = page.locator('.sidebar-section:has(.sidebar-title:text("项目")), .sidebar-section:has(h3:text("项目"))')
  if (await projectSection.count() > 0) {
    return projectSection.locator('.project-item')
  }
  // 如果没有明确的项目区域标题，回退到第四个 sidebar-section
  const sections = page.locator('.sidebar-section')
  const sectionCount = await sections.count()
  if (sectionCount >= 3) {
    return sections.nth(2).locator('.project-item')
  }
  return page.locator('.sidebar .project-item')
}

/**
 * 获取第一个真实项目（跳过导航链接）
 */
export async function getFirstProject(page: Page) {
  const projects = await getProjectList(page)
  return projects.first()
}

/**
 * 统计测试结果
 */
export class TestReporter {
  private passed: string[] = []
  private failed: string[] = []
  
  pass(testName: string) {
    this.passed.push(testName)
  }
  
  fail(testName: string, error: string) {
    this.failed.push(`${testName}: ${error}`)
  }
  
  getSummary() {
    return {
      total: this.passed.length + this.failed.length,
      passed: this.passed.length,
      failed: this.failed.length,
      details: {
        passed: this.passed,
        failed: this.failed,
      }
    }
  }
}
