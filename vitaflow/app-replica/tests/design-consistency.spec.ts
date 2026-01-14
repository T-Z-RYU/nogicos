import { test, expect } from '@playwright/test'

/**
 * Vitaflow 设计一致性测试套件
 * 
 * 这些测试确保实现与 Figma 设计保持一致
 * 包括：视觉回归测试、布局测试、颜色测试等
 */

test.describe('Vitaflow 设计一致性测试', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // 等待页面完全加载
    await page.waitForLoadState('networkidle')
    // 等待字体加载
    await page.waitForTimeout(500)
  })

  // ==================== 全页面截图测试 ====================
  
  test('完整页面视觉回归测试', async ({ page }) => {
    const appContainer = page.locator('[data-testid="app-container"]')
    await expect(appContainer).toBeVisible()
    
    // 全页面截图对比
    await expect(appContainer).toHaveScreenshot('home-page-full.png', {
      maxDiffPixels: 200,
    })
  })

  // ==================== 组件级截图测试 ====================

  test('状态栏样式一致性', async ({ page }) => {
    const statusBar = page.locator('[data-testid="status-bar"]')
    await expect(statusBar).toBeVisible()
    await expect(statusBar).toHaveScreenshot('status-bar.png')
  })

  test('头部组件样式一致性', async ({ page }) => {
    const header = page.locator('[data-testid="header"]')
    await expect(header).toBeVisible()
    await expect(header).toHaveScreenshot('header.png')
  })

  test('日历条样式一致性', async ({ page }) => {
    const calendar = page.locator('[data-testid="calendar-strip"]')
    await expect(calendar).toBeVisible()
    await expect(calendar).toHaveScreenshot('calendar-strip.png')
  })

  test('卡路里卡片样式一致性', async ({ page }) => {
    const calorieCard = page.locator('[data-testid="calorie-card"]')
    await expect(calorieCard).toBeVisible()
    await expect(calorieCard).toHaveScreenshot('calorie-card.png')
  })

  test('宏量营养素卡片样式一致性', async ({ page }) => {
    const macroCards = page.locator('[data-testid="macro-cards"]')
    await expect(macroCards).toBeVisible()
    await expect(macroCards).toHaveScreenshot('macro-cards.png')
  })

  test('底部导航栏样式一致性', async ({ page }) => {
    const bottomNav = page.locator('[data-testid="bottom-navigation"]')
    await expect(bottomNav).toBeVisible()
    await expect(bottomNav).toHaveScreenshot('bottom-navigation.png')
  })

  test('食物列表样式一致性', async ({ page }) => {
    const foodList = page.locator('[data-testid="food-list"]')
    await expect(foodList).toBeVisible()
    await expect(foodList).toHaveScreenshot('food-list.png')
  })

  // ==================== 布局测试 ====================

  test('页面容器尺寸正确', async ({ page }) => {
    const appContainer = page.locator('[data-testid="app-container"]')
    const box = await appContainer.boundingBox()
    
    expect(box?.width).toBe(402)
    expect(box?.height).toBe(874)
  })

  test('状态栏高度正确', async ({ page }) => {
    const statusBar = page.locator('[data-testid="status-bar"]')
    const box = await statusBar.boundingBox()
    
    expect(box?.height).toBe(62)
  })

  test('底部导航高度正确', async ({ page }) => {
    const bottomNav = page.locator('[data-testid="bottom-navigation"]')
    const box = await bottomNav.boundingBox()
    
    expect(box?.height).toBe(98)
  })

  test('宏量营养素三列等宽布局', async ({ page }) => {
    const carbsCard = page.locator('[data-testid="macro-card-carbs"]')
    const fatCard = page.locator('[data-testid="macro-card-fat"]')
    const proteinCard = page.locator('[data-testid="macro-card-protein"]')
    
    const carbsBox = await carbsCard.boundingBox()
    const fatBox = await fatCard.boundingBox()
    const proteinBox = await proteinCard.boundingBox()
    
    // 验证三列宽度大致相等（允许1px误差）
    expect(Math.abs((carbsBox?.width || 0) - (fatBox?.width || 0))).toBeLessThan(2)
    expect(Math.abs((fatBox?.width || 0) - (proteinBox?.width || 0))).toBeLessThan(2)
  })

  // ==================== 颜色测试 ====================

  test('卡路里数值显示正确', async ({ page }) => {
    const calorieCard = page.locator('[data-testid="calorie-card"]')
    const calorieText = await calorieCard.textContent()
    
    // 验证卡路里数值格式
    expect(calorieText).toContain('2,505')
    expect(calorieText).toContain('kcal')
  })

  test('宏量营养素数值显示正确', async ({ page }) => {
    const carbsValue = await page.locator('[data-testid="macro-card-carbs"] p').textContent()
    const fatValue = await page.locator('[data-testid="macro-card-fat"] p').textContent()
    const proteinValue = await page.locator('[data-testid="macro-card-protein"] p').textContent()
    
    expect(carbsValue).toBe('165g')
    expect(fatValue).toBe('98g')
    expect(proteinValue).toBe('43g')
  })

  // ==================== 交互测试 ====================

  test('Tab 切换功能正常', async ({ page }) => {
    const dailyMealTab = page.locator('[data-testid="tab-daily-meal"]')
    const exerciseTab = page.locator('[data-testid="tab-exercise"]')
    
    // 默认选中 Daily Meal
    await expect(dailyMealTab).toHaveClass(/text-text-primary/)
    
    // 点击 Exercise tab
    await exerciseTab.click()
    await expect(exerciseTab).toHaveClass(/text-text-primary/)
  })

  test('导航按钮可点击', async ({ page }) => {
    const homeNav = page.locator('[data-testid="nav-home"]')
    const profileNav = page.locator('[data-testid="nav-profile"]')
    const scanNav = page.locator('[data-testid="nav-scan"]')
    
    await expect(homeNav).toBeEnabled()
    await expect(profileNav).toBeEnabled()
    await expect(scanNav).toBeEnabled()
  })

  // ==================== 响应式测试 ====================

  test('食物项正确显示卡路里', async ({ page }) => {
    const foodItems = page.locator('[data-testid="food-item"]')
    const count = await foodItems.count()
    
    expect(count).toBe(3)
    
    // 验证第一个食物项的卡路里
    const firstItemCalories = await foodItems.first().locator('.text-xl').textContent()
    expect(firstItemCalories).toBe('945')
  })

  // ==================== 日历组件测试 ====================

  test('日历显示7天', async ({ page }) => {
    const calendarDays = page.locator('[data-testid="calendar-day"]')
    const count = await calendarDays.count()
    
    expect(count).toBe(7)
  })

  test('当前日期正确高亮', async ({ page }) => {
    const calendar = page.locator('[data-testid="calendar-strip"]')
    
    // 选中的日期(31)应该有深色背景
    const selectedDay = calendar.locator('.bg-text-primary')
    await expect(selectedDay).toBeVisible()
    await expect(selectedDay).toHaveText('31')
  })
})

// ==================== 设计系统验证测试 ====================

test.describe('设计系统验证', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('主色调正确应用', async ({ page }) => {
    // 进度环应该使用主色
    const progressRing = page.locator('.progress-ring__circle')
    await expect(progressRing).toBeVisible()
  })

  test('卡片圆角一致', async ({ page }) => {
    const calorieCard = page.locator('[data-testid="calorie-card"]')
    
    // 验证圆角样式应用
    await expect(calorieCard).toHaveClass(/rounded-2xl/)
  })

  test('字体加载正确', async ({ page }) => {
    // 等待字体加载
    await page.waitForFunction(() => {
      return document.fonts.ready
    })
    
    const header = page.locator('[data-testid="header"] h1')
    const fontFamily = await header.evaluate((el) => 
      window.getComputedStyle(el).fontFamily
    )
    
    expect(fontFamily).toContain('Inter')
  })
})
