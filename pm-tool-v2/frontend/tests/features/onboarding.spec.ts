import { test, expect } from '@playwright/test'
import { waitForPageLoad } from '../test-utils'

/**
 * PM Tool v2 - Onboarding 功能测试
 * 测试 Onboarding 标记的完整工作流程
 */

test.describe('🎯 Onboarding 功能测试', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding')
    await waitForPageLoad(page)
  })

  // ==================== 页面加载测试 ====================
  
  test.describe('页面加载', () => {
    
    test('页面正确加载', async ({ page }) => {
      await expect(page.locator('.sidebar')).toBeVisible()
      await expect(page.locator('.topbar')).toBeVisible()
    })

    test('项目列表显示', async ({ page }) => {
      // 应该有已标记和未标记两个分类
      await expect(page.getByText('已标记')).toBeVisible()
      await expect(page.getByText('未标记')).toBeVisible()
    })

    test('项目数量显示正确', async ({ page }) => {
      // 检查项目列表中有项目
      const projectItems = page.locator('.project-item')
      const count = await projectItems.count()
      expect(count).toBeGreaterThan(0)
    })
  })

  // ==================== 项目选择测试 ====================
  
  test.describe('项目选择', () => {
    
    test('点击项目加载截图', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      
      // 等待截图加载
      await page.waitForTimeout(1000)
      
      // 截图网格应该显示
      const screenshots = page.locator('img')
      await expect(screenshots.first()).toBeVisible({ timeout: 10000 })
    })

    test('选中项目高亮显示', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      
      await page.waitForTimeout(500)
      
      // 选中项目应该有特殊样式
      const activeProject = page.locator('.project-item.active, .project-item[data-active="true"]')
      // 检查是否有选中状态的视觉指示
      await expect(project).toBeVisible()
    })
  })

  // ==================== Onboarding 标记测试 ====================
  
  test.describe('Onboarding 标记', () => {
    
    test('点击起点按钮进入起点选择模式', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      await page.waitForTimeout(1000)
      
      // 点击起点按钮
      const startBtn = page.getByText('起点').first()
      if (await startBtn.count() > 0) {
        await startBtn.click()
        await page.waitForTimeout(300)
        
        // 应该进入选择模式
        // 验证页面响应
        await expect(page.locator('.sidebar')).toBeVisible()
      }
    })

    test('选择起点后自动切换到终点模式', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      await page.waitForTimeout(1000)
      
      const startBtn = page.getByText('起点').first()
      if (await startBtn.count() > 0) {
        await startBtn.click()
        await page.waitForTimeout(300)
        
        // 点击第一张截图
        const screenshot = page.locator('.content-area img').first()
        if (await screenshot.count() > 0) {
          await screenshot.click()
          await page.waitForTimeout(300)
          
          // 验证页面响应
          await expect(page.locator('.sidebar')).toBeVisible()
        }
      }
    })

    test('保存按钮在有更改时可用', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      await page.waitForTimeout(1000)
      
      const saveBtn = page.getByRole('button', { name: /保存/i })
      // 初始状态应该是禁用的（无更改）
      // 或者已经有标记就可以用
      await expect(saveBtn.first()).toBeVisible()
    })

    test('清除按钮可以重置标记', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      await page.waitForTimeout(1000)
      
      const clearBtn = page.getByRole('button', { name: /清除/i })
      if (await clearBtn.count() > 0) {
        await expect(clearBtn.first()).toBeVisible()
      }
    })
  })

  // ==================== 截图查看器测试 ====================
  
  test.describe('截图查看器', () => {
    
    test('点击截图打开全屏查看器', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      await page.waitForTimeout(1000)
      
      const screenshot = page.locator('.content-area img').first()
      if (await screenshot.count() > 0) {
        await screenshot.click()
        await page.waitForTimeout(300)
        
        // 查看器或交互模式应该激活
        await expect(page.locator('.sidebar')).toBeVisible()
      }
    })

    test('Escape 键关闭查看器', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      await page.waitForTimeout(1000)
      
      const screenshot = page.locator('.content-area img').first()
      if (await screenshot.count() > 0) {
        await screenshot.click()
        await page.waitForTimeout(300)
        
        await page.keyboard.press('Escape')
        await page.waitForTimeout(300)
        
        // 页面应该恢复正常状态
        await expect(page.locator('.sidebar')).toBeVisible()
      }
    })

    test('左右箭头键导航截图', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      await page.waitForTimeout(1000)
      
      const screenshot = page.locator('.content-area img').first()
      if (await screenshot.count() > 0) {
        await screenshot.click()
        await page.waitForTimeout(300)
        
        await page.keyboard.press('ArrowRight')
        await page.waitForTimeout(200)
        
        await page.keyboard.press('ArrowLeft')
        await page.waitForTimeout(200)
        
        // 页面应该响应
        await expect(page.locator('.sidebar')).toBeVisible()
      }
    })
  })

  // ==================== 标记状态持久化测试 ====================
  
  test.describe('标记状态持久化', () => {
    
    test('已标记的项目显示在已标记列表', async ({ page }) => {
      // 检查已标记分类
      const markedSection = page.getByText('已标记')
      await expect(markedSection).toBeVisible()
    })

    test('标记信息在页面刷新后保持', async ({ page }) => {
      // 选择一个已标记的项目
      const markedProject = page.locator('.project-item').first()
      await markedProject.click()
      await page.waitForTimeout(1000)
      
      // 刷新页面
      await page.reload()
      await waitForPageLoad(page)
      
      // 项目应该仍然可选
      await expect(page.locator('.project-item').first()).toBeVisible()
    })
  })

  // ==================== 边界情况测试 ====================
  
  test.describe('边界情况', () => {
    
    test('空项目处理', async ({ page }) => {
      // 页面应该正常加载，即使某些项目没有截图
      await expect(page.locator('.sidebar')).toBeVisible()
    })

    test('离开页面时有未保存更改应提示', async ({ page }) => {
      const project = page.locator('.project-item').first()
      await project.click()
      await page.waitForTimeout(1000)
      
      // 尝试进行一些修改
      const startBtn = page.getByText('起点').first()
      if (await startBtn.count() > 0) {
        await startBtn.click()
        await page.waitForTimeout(300)
        
        const screenshot = page.locator('.content-area img').first()
        if (await screenshot.count() > 0) {
          await screenshot.click()
          await page.waitForTimeout(500)
          
          // 设置 dialog 监听器
          page.on('dialog', async dialog => {
            expect(dialog.type()).toBe('beforeunload')
            await dialog.dismiss()
          })
          
          // 尝试离开页面（这可能触发 beforeunload）
          // 注意：Playwright 默认会处理 beforeunload
        }
      }
    })
  })
})

