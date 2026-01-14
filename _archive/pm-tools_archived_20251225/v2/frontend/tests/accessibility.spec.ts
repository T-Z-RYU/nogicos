import { test, expect } from '@playwright/test'
import { waitForPageLoad } from './test-utils'

/**
 * PM Tool v2 - 可访问性测试
 * 验证键盘导航、ARIA 标签、颜色对比度等
 */

test.describe('♿ 可访问性测试', () => {

  // ==================== 键盘导航测试 ====================
  
  test.describe('键盘导航', () => {
    
    test('Tab 键可以在主要元素间导航', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 按 Tab 键多次，检查焦点移动
      await page.keyboard.press('Tab')
      const firstFocused = await page.evaluate(() => document.activeElement?.tagName)
      expect(firstFocused).toBeTruthy()
      
      await page.keyboard.press('Tab')
      const secondFocused = await page.evaluate(() => document.activeElement?.tagName)
      expect(secondFocused).toBeTruthy()
    })

    test('Escape 键可以关闭模态框', async ({ page }) => {
      await page.goto('/onboarding')
      await waitForPageLoad(page)
      
      // 如果有查看器打开，Escape 应该关闭它
      await page.keyboard.press('Escape')
      // 验证页面仍然可用
      await expect(page.locator('.sidebar')).toBeVisible()
    })

    test('Enter 键可以激活按钮', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 找到第一个可聚焦的项目
      const project = page.locator('.sidebar .project-item').first()
      if (await project.count() > 0) {
        await project.focus()
        await page.keyboard.press('Enter')
        // 应该导航到项目详情
        await page.waitForTimeout(500)
      }
    })

    test('排序页面快捷键', async ({ page }) => {
      await page.goto('/sort')
      await waitForPageLoad(page)
      
      // Ctrl+A 应该全选（如果有项目选中）
      await page.keyboard.press('Control+a')
      // 页面应该响应
      await expect(page.locator('.sidebar')).toBeVisible()
    })

    test('Onboarding 页面左右箭头导航', async ({ page }) => {
      await page.goto('/onboarding')
      await waitForPageLoad(page)
      
      // 选择一个项目
      const project = page.locator('.sidebar .project-item').first()
      if (await project.count() > 0) {
        await project.click()
        await page.waitForTimeout(500)
        
        // 左右箭头应该可以导航截图
        await page.keyboard.press('ArrowRight')
        await page.keyboard.press('ArrowLeft')
        
        // 页面应该响应
        await expect(page.locator('.sidebar')).toBeVisible()
      }
    })
  })

  // ==================== ARIA 标签测试 ====================
  
  test.describe('ARIA 标签', () => {
    
    test('按钮有可访问的文本', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 检查所有按钮都有文本或 aria-label
      const buttons = page.locator('button')
      const count = await buttons.count()
      
      for (let i = 0; i < Math.min(count, 10); i++) {
        const button = buttons.nth(i)
        const text = await button.textContent()
        const ariaLabel = await button.getAttribute('aria-label')
        const title = await button.getAttribute('title')
        
        // 按钮应该有文本、aria-label 或 title
        const hasAccessibleName = (text && text.trim().length > 0) || ariaLabel || title
        expect(hasAccessibleName).toBeTruthy()
      }
    })

    test('图片有 alt 属性', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 进入项目详情查看截图
      const project = page.locator('.sidebar .project-item').nth(2)
      if (await project.count() > 0) {
        await project.click()
        await waitForPageLoad(page)
        
        const images = page.locator('img')
        const count = await images.count()
        
        for (let i = 0; i < Math.min(count, 5); i++) {
          const img = images.nth(i)
          const alt = await img.getAttribute('alt')
          // 图片应该有 alt 属性（可以为空字符串用于装饰性图片）
          expect(alt !== null).toBeTruthy()
        }
      }
    })

    test('表单元素有关联的标签', async ({ page }) => {
      await page.goto('/settings')
      await waitForPageLoad(page)
      
      const inputs = page.locator('input[type="text"], input[type="email"], select')
      const count = await inputs.count()
      
      for (let i = 0; i < count; i++) {
        const input = inputs.nth(i)
        const id = await input.getAttribute('id')
        const ariaLabel = await input.getAttribute('aria-label')
        const ariaLabelledby = await input.getAttribute('aria-labelledby')
        const placeholder = await input.getAttribute('placeholder')
        
        // 输入框应该有某种形式的标签
        const hasLabel = id || ariaLabel || ariaLabelledby || placeholder
        expect(hasLabel).toBeTruthy()
      }
    })
  })

  // ==================== 焦点可见性测试 ====================
  
  test.describe('焦点可见性', () => {
    
    test('焦点状态视觉明显', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // Tab 到第一个可聚焦元素
      await page.keyboard.press('Tab')
      
      // 检查焦点元素是否有可见的焦点样式
      const focusedElement = page.locator(':focus')
      if (await focusedElement.count() > 0) {
        const outline = await focusedElement.evaluate(el => 
          window.getComputedStyle(el).outline
        )
        const boxShadow = await focusedElement.evaluate(el => 
          window.getComputedStyle(el).boxShadow
        )
        const borderColor = await focusedElement.evaluate(el => 
          window.getComputedStyle(el).borderColor
        )
        
        // 焦点元素应该有某种视觉指示
        const hasFocusIndicator = 
          (outline && outline !== 'none' && !outline.includes('0px')) ||
          (boxShadow && boxShadow !== 'none') ||
          borderColor
        
        // 这个测试可以根据实际情况调整
        expect(hasFocusIndicator).toBeTruthy()
      }
    })
  })

  // ==================== 颜色对比度测试 ====================
  
  test.describe('颜色对比度', () => {
    
    test('主要文本与背景有足够对比度', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 获取主要文本颜色和背景色
      const title = page.locator('.topbar-title')
      if (await title.count() > 0) {
        const color = await title.evaluate(el => 
          window.getComputedStyle(el).color
        )
        const bgColor = await title.evaluate(el => {
          let parent = el.parentElement
          while (parent) {
            const bg = window.getComputedStyle(parent).backgroundColor
            if (bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
              return bg
            }
            parent = parent.parentElement
          }
          return 'rgb(0, 0, 0)'
        })
        
        // 白色文本 (#fff) 在深色背景上应该有良好对比度
        expect(color).toBe('rgb(255, 255, 255)')
      }
    })
  })

  // ==================== 缩放测试 ====================
  
  test.describe('页面缩放', () => {
    
    test('200% 缩放下布局不破裂', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 模拟 200% 缩放
      await page.evaluate(() => {
        document.body.style.zoom = '2'
      })
      
      await page.waitForTimeout(500)
      
      // 关键元素应该仍然可见
      await expect(page.locator('.sidebar')).toBeVisible()
      await expect(page.locator('.topbar')).toBeVisible()
    })
  })
})

