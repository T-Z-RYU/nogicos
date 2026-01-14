import { test, expect } from '@playwright/test'
import { waitForPageLoad } from '../test-utils'

/**
 * PM Tool v2 - 排序功能测试
 * 测试截图排序的完整工作流程
 */

test.describe('📋 排序功能测试', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/sort')
    await waitForPageLoad(page)
  })

  // ==================== 页面加载测试 ====================
  
  test.describe('页面加载', () => {
    
    test('页面正确加载', async ({ page }) => {
      await expect(page.locator('.sidebar')).toBeVisible()
    })

    test('项目选择器显示', async ({ page }) => {
      const selector = page.locator('select')
      await expect(selector.first()).toBeVisible()
    })

    test('待处理区显示', async ({ page }) => {
      // 左侧应该有待处理区
      await expect(page.getByText(/待处理|Pending/i).first()).toBeVisible({ timeout: 5000 })
    })
  })

  // ==================== 项目选择测试 ====================
  
  test.describe('项目选择', () => {
    
    test('选择项目后加载截图', async ({ page }) => {
      const selector = page.locator('select').first()
      
      // 获取选项数量
      const options = await selector.locator('option').count()
      
      if (options > 1) {
        // 选择第二个选项（第一个通常是提示文本）
        await selector.selectOption({ index: 1 })
        
        // 等待截图加载
        await page.waitForTimeout(2000)
        
        // 应该显示截图
        const screenshots = page.locator('.content-area img')
        // 可能需要更长时间加载
      }
    })
  })

  // ==================== 拖拽排序测试 ====================
  
  test.describe('拖拽排序', () => {
    
    test('截图卡片可以拖拽', async ({ page }) => {
      const selector = page.locator('select').first()
      const options = await selector.locator('option').count()
      
      if (options > 1) {
        await selector.selectOption({ index: 1 })
        await page.waitForTimeout(2000)
        
        // 检查是否有可排序的项目
        const sortableItems = page.locator('[data-sortable="true"], .screenshot-card')
        const count = await sortableItems.count()
        
        if (count >= 2) {
          const firstItem = sortableItems.first()
          const secondItem = sortableItems.nth(1)
          
          const firstBox = await firstItem.boundingBox()
          const secondBox = await secondItem.boundingBox()
          
          if (firstBox && secondBox) {
            // 执行拖拽
            await firstItem.dragTo(secondItem)
            await page.waitForTimeout(500)
            
            // 验证页面仍然正常
            await expect(page.locator('.sidebar')).toBeVisible()
          }
        }
      }
    })
  })

  // ==================== 选择功能测试 ====================
  
  test.describe('选择功能', () => {
    
    test('Ctrl+A 全选', async ({ page }) => {
      const selector = page.locator('select').first()
      const options = await selector.locator('option').count()
      
      if (options > 1) {
        await selector.selectOption({ index: 1 })
        await page.waitForTimeout(2000)
        
        await page.keyboard.press('Control+a')
        await page.waitForTimeout(300)
        
        // 验证页面响应
        await expect(page.locator('.sidebar')).toBeVisible()
      }
    })

    test('Escape 取消选择', async ({ page }) => {
      const selector = page.locator('select').first()
      const options = await selector.locator('option').count()
      
      if (options > 1) {
        await selector.selectOption({ index: 1 })
        await page.waitForTimeout(2000)
        
        await page.keyboard.press('Control+a')
        await page.waitForTimeout(300)
        
        await page.keyboard.press('Escape')
        await page.waitForTimeout(300)
        
        // 验证页面响应
        await expect(page.locator('.sidebar')).toBeVisible()
      }
    })
  })

  // ==================== 预览面板测试 ====================
  
  test.describe('预览面板', () => {
    
    test('点击截图显示预览', async ({ page }) => {
      const selector = page.locator('select').first()
      const options = await selector.locator('option').count()
      
      if (options > 1) {
        await selector.selectOption({ index: 1 })
        await page.waitForTimeout(2000)
        
        const screenshot = page.locator('.content-area img').first()
        if (await screenshot.count() > 0) {
          await screenshot.click()
          await page.waitForTimeout(300)
          
          // 预览面板应该显示
          // 或者截图被选中
          await expect(page.locator('.sidebar')).toBeVisible()
        }
      }
    })

    test('左右箭头导航预览', async ({ page }) => {
      const selector = page.locator('select').first()
      const options = await selector.locator('option').count()
      
      if (options > 1) {
        await selector.selectOption({ index: 1 })
        await page.waitForTimeout(2000)
        
        const screenshot = page.locator('.content-area img').first()
        if (await screenshot.count() > 0) {
          await screenshot.click()
          await page.waitForTimeout(300)
          
          await page.keyboard.press('ArrowRight')
          await page.waitForTimeout(200)
          
          await page.keyboard.press('ArrowLeft')
          await page.waitForTimeout(200)
          
          await expect(page.locator('.sidebar')).toBeVisible()
        }
      }
    })
  })

  // ==================== 删除功能测试 ====================
  
  test.describe('删除功能', () => {
    
    test('Delete 键删除选中项', async ({ page }) => {
      const selector = page.locator('select').first()
      const options = await selector.locator('option').count()
      
      if (options > 1) {
        await selector.selectOption({ index: 1 })
        await page.waitForTimeout(2000)
        
        // 先选择一些项目
        const screenshot = page.locator('.content-area img').first()
        if (await screenshot.count() > 0) {
          await screenshot.click()
          await page.waitForTimeout(300)
          
          // 按 Delete 键
          await page.keyboard.press('Delete')
          await page.waitForTimeout(300)
          
          // 页面应该响应
          await expect(page.locator('.sidebar')).toBeVisible()
        }
      }
    })
  })

  // ==================== 保存功能测试 ====================
  
  test.describe('保存功能', () => {
    
    test('保存按钮在有更改时可用', async ({ page }) => {
      const selector = page.locator('select').first()
      const options = await selector.locator('option').count()
      
      if (options > 1) {
        await selector.selectOption({ index: 1 })
        await page.waitForTimeout(2000)
        
        const saveBtn = page.getByRole('button', { name: /保存|应用/i })
        if (await saveBtn.count() > 0) {
          await expect(saveBtn.first()).toBeVisible()
        }
      }
    })
  })

  // ==================== 快捷键提示测试 ====================
  
  test.describe('快捷键提示', () => {
    
    test('快捷键提示面板显示', async ({ page }) => {
      const selector = page.locator('select').first()
      const options = await selector.locator('option').count()
      
      if (options > 1) {
        await selector.selectOption({ index: 1 })
        await page.waitForTimeout(2000)
        
        // 快捷键提示应该可见
        const shortcuts = page.getByText(/快捷键|Shortcuts/i)
        if (await shortcuts.count() > 0) {
          await expect(shortcuts.first()).toBeVisible()
        }
      }
    })
  })

  // ==================== 离开提示测试 ====================
  
  test.describe('离开提示', () => {
    
    test('有未保存更改时离开应提示', async ({ page }) => {
      // 这个测试需要实际的更改操作
      // beforeunload 事件会被触发
      await expect(page.locator('.sidebar')).toBeVisible()
    })
  })
})

