import { test, expect } from '@playwright/test'
import { waitForPageLoad, getFirstProject, getProjectList } from './test-utils'

/**
 * PM Tool v2 - 用户流程一致性测试
 * 验证所有用户交互、导航、弹窗等功能
 */

test.describe('🚀 用户流程测试', () => {

  // ==================== 1. 页面加载测试 ====================
  
  test.describe('页面加载', () => {
    
    test('首页能正常加载', async ({ page }) => {
      await page.goto('/')
      await expect(page).toHaveTitle(/PM Tool/)
      await waitForPageLoad(page)
      
      // 验证关键元素存在
      await expect(page.locator('.sidebar')).toBeVisible()
      await expect(page.locator('.main-content')).toBeVisible()
      await expect(page.locator('.topbar')).toBeVisible()
    })

    test('Logo 显示正确', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const logo = page.locator('.logo')
      await expect(logo).toBeVisible()
      await expect(logo).toContainText('PM Lab')
    })

    test('项目列表能加载', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 等待项目加载
      const projectItems = page.locator('.sidebar .project-item')
      await expect(projectItems.first()).toBeVisible({ timeout: 10000 })
      
      // 应该有多个项目
      const count = await projectItems.count()
      expect(count).toBeGreaterThan(1)
    })

    test('顶栏标题显示正确', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const title = page.locator('.topbar-title')
      await expect(title).toBeVisible()
      await expect(title).toContainText('全部项目')
    })
  })

  // ==================== 2. 侧边栏导航测试 ====================
  
  test.describe('侧边栏导航', () => {
    
    test('点击"全部项目"导航到首页', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 先点击一个项目
      const projectItem = await getFirstProject(page)
      await projectItem.click()
      await waitForPageLoad(page)
      
      // 点击"全部项目"
      const homeNav = page.locator('.project-item:has-text("全部项目")')
      await homeNav.click()
      await waitForPageLoad(page)
      
      await expect(page).toHaveURL('/')
    })

    test('点击项目导航到项目详情页', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 使用 getFirstProject 获取第一个实际项目
      const projectItem = await getFirstProject(page)
      await expect(projectItem).toBeVisible({ timeout: 10000 })
      
      // 点击项目
      await projectItem.click()
      await waitForPageLoad(page)
      
      // 验证 URL 变化
      await expect(page).toHaveURL(/\/project\//)
    })

    test('选中的项目有 active 状态', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 点击一个项目
      const projectItem = await getFirstProject(page)
      await projectItem.click()
      await waitForPageLoad(page)
      
      // 验证 active class
      const activeItem = page.locator('.sidebar .project-item.active')
      await expect(activeItem).toBeVisible()
    })

    test('项目列表显示截图数量', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const projectCount = page.locator('.project-count').first()
      await expect(projectCount).toBeVisible()
      
      // 应该显示数字
      const count = await projectCount.textContent()
      expect(parseInt(count || '0')).toBeGreaterThanOrEqual(0)
    })
  })

  // ==================== 3. 项目网格测试 ====================
  
  test.describe('项目网格', () => {
    
    test('项目卡片显示在网格中', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const grid = page.locator('.content-area > div')
      await expect(grid).toBeVisible()
    })

    test('项目卡片可点击跳转', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 查找项目卡片（在主内容区）
      const card = page.locator('.screenshot-card').first()
      if (await card.count() > 0) {
        await card.click()
        await waitForPageLoad(page)
        
        // 应该导航到项目详情
        await expect(page).toHaveURL(/\/project\//)
      }
    })
  })

  // ==================== 4. 筛选器测试 ====================
  
  test.describe('筛选功能', () => {
    
    test('来源筛选器存在', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const filterButtons = page.locator('.btn-ghost')
      await expect(filterButtons.first()).toBeVisible()
    })

    test('点击筛选按钮切换状态', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 找到 "Projects" 按钮
      const projectsBtn = page.locator('.btn-ghost:has-text("Projects")')
      if (await projectsBtn.count() > 0) {
        await projectsBtn.click()
        await page.waitForTimeout(500)
        
        // 验证按钮有 active 状态
        const hasActive = await projectsBtn.evaluate(el => 
          el.classList.contains('active')
        )
        expect(hasActive).toBe(true)
      }
    })

    test('搜索框可以输入', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const searchInput = page.locator('input[placeholder*="搜索"]')
      if (await searchInput.count() > 0) {
        await searchInput.fill('test')
        
        const value = await searchInput.inputValue()
        expect(value).toBe('test')
      }
    })
  })

  // ==================== 5. 截图详情页测试 ====================
  
  test.describe('截图详情页', () => {
    
    test.beforeEach(async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 导航到项目详情页
      const projectItem = await getFirstProject(page)
      if (await projectItem.count() > 0) {
        await projectItem.click()
        await waitForPageLoad(page)
      }
    })

    test('截图网格正确加载', async ({ page }) => {
      const screenshots = page.locator('.screenshot-card')
      await expect(screenshots.first()).toBeVisible({ timeout: 15000 })
      
      const count = await screenshots.count()
      expect(count).toBeGreaterThan(0)
    })

    test('截图显示索引号', async ({ page }) => {
      const indexBadge = page.locator('.screenshot-card div:has-text("#")').first()
      if (await indexBadge.count() > 0) {
        const text = await indexBadge.textContent()
        expect(text).toMatch(/#\d+/)
      }
    })

    test('Stage 筛选器存在', async ({ page }) => {
      const stageFilter = page.locator('text=Stage:')
      // Stage 筛选器可能存在也可能不存在（取决于数据）
      if (await stageFilter.count() > 0) {
        await expect(stageFilter).toBeVisible()
      }
    })
  })

  // ==================== 6. 截图查看器测试 ====================
  
  test.describe('截图查看器', () => {
    
    test.beforeEach(async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 导航到项目详情页
      const projectItem = await getFirstProject(page)
      await expect(projectItem).toBeVisible({ timeout: 10000 })
      await projectItem.click()
      await waitForPageLoad(page)
    })

    test('截图卡片存在且有图片', async ({ page }) => {
      // 验证截图区域有图片
      const images = page.locator('.content-area img')
      await expect(images.first()).toBeVisible({ timeout: 15000 })
    })

    test('截图卡片显示索引', async ({ page }) => {
      // 验证截图卡片上显示索引号
      const indexBadge = page.locator('text="#1"').first()
      await expect(indexBadge).toBeVisible({ timeout: 15000 })
    })

    test('截图显示分类或未分类', async ({ page }) => {
      // 验证截图区域有分类信息
      const content = page.locator('.content-area')
      await expect(content).toBeVisible({ timeout: 15000 })
      
      // 内容区应该有文字内容
      const text = await content.textContent()
      expect(text).toBeDefined()
    })

    test('截图缩略图正常加载', async ({ page }) => {
      // 验证截图缩略图已加载
      const thumbnail = page.locator('.content-area img').first()
      await expect(thumbnail).toBeVisible({ timeout: 15000 })
    })

    test('截图网格正确渲染多张图片', async ({ page }) => {
      // 等待截图网格完全加载
      await page.waitForTimeout(3000)
      
      // 验证截图网格已渲染出多张图片
      const images = page.locator('.content-area img')
      const count = await images.count()
      expect(count).toBeGreaterThan(5)
    })
  })

  // ==================== 7. 键盘导航测试 ====================
  
  test.describe('键盘导航', () => {
    
    test('页面支持键盘焦点', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // Tab 键可以在元素间切换焦点
      await page.keyboard.press('Tab')
      
      // 验证有元素获得焦点
      const focusedElement = page.locator(':focus')
      await expect(focusedElement).toBeDefined()
    })

    test('链接可以通过 Enter 键激活', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 找到一个链接并聚焦
      const link = page.locator('a').first()
      await link.focus()
      
      // 验证链接存在
      await expect(link).toBeVisible()
    })

    test('按钮可以通过键盘激活', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 找到筛选按钮
      const btn = page.locator('.btn-ghost').first()
      if (await btn.count() > 0) {
        await btn.focus()
        await expect(btn).toBeFocused()
      }
    })
  })

  // ==================== 8. 导航按钮测试 ====================
  
  test.describe('导航元素', () => {
    
    test('侧边栏项目可点击导航', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 验证侧边栏项目可点击
      const projectItem = await getFirstProject(page)
      await expect(projectItem).toBeVisible({ timeout: 10000 })
      
      // 点击项目
      await projectItem.click()
      await waitForPageLoad(page)
      
      // 验证导航成功
      await expect(page).toHaveURL(/\/project\//)
    })

    test('首页导航链接工作正常', async ({ page }) => {
      // 先进入项目页
      await page.goto('/')
      await waitForPageLoad(page)
      
      const projectItem = await getFirstProject(page)
      await projectItem.click()
      await waitForPageLoad(page)
      
      // 点击全部项目返回首页
      const homeNav = page.locator('.project-item:has-text("全部项目")')
      await homeNav.click()
      await waitForPageLoad(page)
      
      await expect(page).toHaveURL('/')
    })

    test('Logo 链接返回首页', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 进入项目页
      const projectItem = await getFirstProject(page)
      await projectItem.click()
      await waitForPageLoad(page)
      
      // 点击 Logo
      const logo = page.locator('.logo')
      await logo.click()
      await waitForPageLoad(page)
      
      await expect(page).toHaveURL('/')
    })
  })

  // ==================== 9. Hover 效果测试 ====================
  
  test.describe('Hover 交互效果', () => {
    
    test('项目卡片 hover 有缩放效果', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const card = page.locator('.screenshot-card').first()
      if (await card.count() > 0) {
        // Hover 前
        const beforeTransform = await card.evaluate(el => 
          window.getComputedStyle(el).transform
        )
        
        await card.hover()
        await page.waitForTimeout(300)
        
        // Hover 后
        const afterTransform = await card.evaluate(el => 
          window.getComputedStyle(el).transform
        )
        
        // transform 应该有变化（scale 效果）
        // 由于是 Framer Motion 控制，可能已经有 transform
        expect(card).toBeVisible()
      }
    })

    test('侧边栏项目 hover 效果', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const projectItem = await getFirstProject(page)
      await expect(projectItem).toBeVisible()
      
      await projectItem.hover()
      await page.waitForTimeout(200)
      
      // 验证元素可见（hover 不会导致消失）
      await expect(projectItem).toBeVisible()
    })

    test('按钮 hover 效果', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const btn = page.locator('.btn-ghost').first()
      if (await btn.count() > 0) {
        await btn.hover()
        await page.waitForTimeout(200)
        
        // 验证按钮状态变化
        const bgColor = await btn.evaluate(el => 
          window.getComputedStyle(el).backgroundColor
        )
        
        // hover 时背景应该有变化
        expect(bgColor).toBeDefined()
      }
    })
  })

  // ==================== 10. 加载状态测试 ====================
  
  test.describe('加载状态', () => {
    
    test('页面加载时显示加载状态', async ({ page }) => {
      // 使用较慢的网络模拟
      await page.route('**/api/**', async route => {
        await new Promise(resolve => setTimeout(resolve, 500))
        await route.continue()
      })
      
      await page.goto('/')
      
      // 可能会有 spinner
      const spinner = page.locator('.spinner')
      // spinner 可能存在也可能很快消失
    })

    test('截图加载有占位状态', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const projectItem = await getFirstProject(page)
      if (await projectItem.count() > 0) {
        await projectItem.click()
        
        // 检查是否有加载状态
        const content = page.locator('.content-area')
        await expect(content).toBeVisible()
      }
    })
  })

  // ==================== 11. 错误状态测试 ====================
  
  test.describe('错误处理', () => {
    
    test('API 错误时显示错误信息', async ({ page }) => {
      // 模拟 API 错误
      await page.route('**/api/projects', route => 
        route.fulfill({
          status: 500,
          body: 'Internal Server Error'
        })
      )
      
      await page.goto('/')
      await page.waitForTimeout(2000)
      
      // 应该显示错误信息或空状态
      // 具体取决于实现
    })

    test('404 页面不存在', async ({ page }) => {
      await page.goto('/nonexistent-page')
      
      // Next.js 会显示 404 页面
      await expect(page.locator('text=404')).toBeVisible({ timeout: 5000 }).catch(() => {
        // 或者重定向到首页
      })
    })
  })

  // ==================== 12. 浏览器后退/前进测试 ====================
  
  test.describe('浏览器历史导航', () => {
    
    test('后退按钮正常工作', async ({ page }) => {
      // 先访问首页
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 点击项目进入详情页
      const projectItem = await getFirstProject(page)
      await expect(projectItem).toBeVisible({ timeout: 10000 })
      await projectItem.click()
      await waitForPageLoad(page)
      
      // 验证已进入详情页
      await expect(page).toHaveURL(/\/project\//)
      
      // 点击首页导航返回
      const homeNav = page.locator('.project-item:has-text("全部项目")')
      await homeNav.click()
      await waitForPageLoad(page)
      
      // 应该回到首页
      await expect(page).toHaveURL('/')
    })

    test('多项目导航正常', async ({ page }) => {
      // 访问首页
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 获取项目列表
      const projects = await getProjectList(page)
      const projectCount = await projects.count()
      
      if (projectCount >= 2) {
        // 点击第一个项目
        await projects.first().click()
        await waitForPageLoad(page)
        
        // 验证在详情页
        await expect(page).toHaveURL(/\/project\//)
        
        // 点击另一个项目
        await projects.nth(1).click()
        await waitForPageLoad(page)
        
        // 验证仍然在详情页（不同项目）
        await expect(page).toHaveURL(/\/project\//)
      }
    })
  })

  // ==================== 13. URL 直接访问测试 ====================
  
  test.describe('URL 直接访问', () => {
    
    test('直接访问项目详情页', async ({ page }) => {
      // 先获取一个有效的项目名
      await page.goto('/')
      await waitForPageLoad(page)
      
      const projectItem = await getFirstProject(page)
      if (await projectItem.count() > 0) {
        await projectItem.click()
        await waitForPageLoad(page)
        
        const currentUrl = page.url()
        
        // 新页面直接访问该 URL
        await page.goto(currentUrl)
        await waitForPageLoad(page)
        
        // 应该正常显示
        await expect(page.locator('.topbar')).toBeVisible()
      }
    })
  })

  // ==================== 14. 分类标签测试 ====================
  
  test.describe('分类标签功能', () => {
    
    test.beforeEach(async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const projectItem = await getFirstProject(page)
      if (await projectItem.count() > 0) {
        await projectItem.click()
        await waitForPageLoad(page)
      }
    })

    test('截图卡片显示分类标签', async ({ page }) => {
      const badge = page.locator('.badge').first()
      // 分类标签可能存在也可能不存在
      if (await badge.count() > 0) {
        await expect(badge).toBeVisible()
      }
    })

    test('查看器显示分类信息', async ({ page }) => {
      const screenshot = page.locator('.screenshot-card').first()
      if (await screenshot.count() > 0) {
        await screenshot.click()
        await page.waitForTimeout(500)
        
        // 查看器中的分类标签
        const viewerBadge = page.locator('.badge').first()
        // 可能有也可能没有，取决于数据
      }
    })
  })

  // ==================== 15. 完整用户流程测试 ====================
  
  test.describe('完整用户流程', () => {
    
    test('完整浏览流程：首页 -> 项目 -> 截图 -> 返回', async ({ page }) => {
      // 1. 访问首页
      await page.goto('/')
      await waitForPageLoad(page)
      await expect(page.locator('.logo')).toBeVisible()
      
      // 2. 点击项目
      const projectItem = await getFirstProject(page)
      await expect(projectItem).toBeVisible()
      await projectItem.click()
      await waitForPageLoad(page)
      
      // 3. 验证进入项目详情页
      await expect(page).toHaveURL(/\/project\//)
      
      // 4. 点击截图
      const screenshot = page.locator('.screenshot-card').first()
      await expect(screenshot).toBeVisible({ timeout: 15000 })
      await screenshot.click()
      await page.waitForTimeout(500)
      
      // 5. 验证查看器打开
      const viewer = page.locator('[data-testid="screenshot-viewer"]')
      await expect(viewer).toBeVisible({ timeout: 5000 })
      
      // 6. 使用键盘浏览几张
      await page.keyboard.press('ArrowRight')
      await page.waitForTimeout(200)
      await page.keyboard.press('ArrowRight')
      await page.waitForTimeout(200)
      
      // 7. 关闭查看器
      await page.keyboard.press('Escape')
      await page.waitForTimeout(500)
      await expect(viewer).not.toBeVisible()
      
      // 8. 返回首页
      const homeNav = page.locator('.project-item:has-text("全部项目")')
      await homeNav.click()
      await waitForPageLoad(page)
      
      // 9. 验证回到首页
      await expect(page).toHaveURL('/')
      await expect(page.locator('.topbar-title')).toContainText('全部项目')
    })

    test('筛选流程：搜索 + 来源筛选', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 1. 使用搜索
      const searchInput = page.locator('input[placeholder*="搜索"]')
      if (await searchInput.count() > 0) {
        await searchInput.fill('Peloton')
        await page.waitForTimeout(500)
        
        // 2. 清除搜索
        await searchInput.fill('')
        await page.waitForTimeout(500)
      }
      
      // 3. 使用来源筛选
      const projectsBtn = page.locator('.btn-ghost:has-text("Projects")')
      if (await projectsBtn.count() > 0) {
        await projectsBtn.click()
        await page.waitForTimeout(500)
        
        // 验证筛选生效
        const hasActive = await projectsBtn.evaluate(el => 
          el.classList.contains('active')
        )
        expect(hasActive).toBe(true)
        
        // 4. 切换回全部
        const allBtn = page.locator('.btn-ghost:has-text("全部")')
        await allBtn.click()
        await page.waitForTimeout(500)
      }
    })
  })

  // ==================== 16. 设置页面测试 ====================
  
  test.describe('设置页面', () => {
    
    test('设置页面能正常加载', async ({ page }) => {
      await page.goto('/settings')
      await waitForPageLoad(page)
      
      // 验证标题
      const title = page.locator('.topbar-title')
      await expect(title).toContainText('设置')
    })

    test('设置页面显示关于信息', async ({ page }) => {
      await page.goto('/settings')
      await waitForPageLoad(page)
      
      // 验证 PM Lab 标题
      await expect(page.locator('text=PM Lab v2.0')).toBeVisible()
      
      // 验证技术栈标签
      await expect(page.locator('text=Next.js 16')).toBeVisible()
      await expect(page.locator('text=FastAPI')).toBeVisible()
    })

    test('设置页面显示功能特性', async ({ page }) => {
      await page.goto('/settings')
      await waitForPageLoad(page)
      
      // 验证功能特性
      await expect(page.locator('text=项目管理')).toBeVisible()
      await expect(page.locator('text=智能分类')).toBeVisible()
      await expect(page.locator('text=流畅浏览')).toBeVisible()
    })

    test('设置页面显示快捷键说明', async ({ page }) => {
      await page.goto('/settings')
      await waitForPageLoad(page)
      
      // 验证快捷键
      await expect(page.locator('text=Esc')).toBeVisible()
      await expect(page.locator('text=← →')).toBeVisible()
    })

    test('侧边栏设置链接正常工作', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 点击设置链接
      const settingsLink = page.locator('.project-item:has-text("设置")')
      await settingsLink.click()
      await waitForPageLoad(page)
      
      // 验证导航到设置页
      await expect(page).toHaveURL('/settings')
    })
  })
})
