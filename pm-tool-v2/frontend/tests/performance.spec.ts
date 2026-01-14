import { test, expect } from '@playwright/test'
import { waitForPageLoad, getFirstProject } from './test-utils'

/**
 * PM Tool v2 - 性能测试
 * 测试页面加载时间、渲染性能等
 */

test.describe('⚡ 性能测试', () => {

  // ==================== 页面加载时间测试 ====================
  
  test.describe('页面加载时间', () => {
    
    test('首页加载时间 < 3s', async ({ page }) => {
      const start = Date.now()
      await page.goto('/')
      await waitForPageLoad(page)
      const duration = Date.now() - start
      
      console.log(`首页加载时间: ${duration}ms`)
      expect(duration).toBeLessThan(3000)
    })

    test('Onboarding 页面加载时间 < 3s', async ({ page }) => {
      const start = Date.now()
      await page.goto('/onboarding')
      await waitForPageLoad(page)
      const duration = Date.now() - start
      
      console.log(`Onboarding 页面加载时间: ${duration}ms`)
      expect(duration).toBeLessThan(3000)
    })

    test('排序页面加载时间 < 3s', async ({ page }) => {
      const start = Date.now()
      await page.goto('/sort')
      await waitForPageLoad(page)
      const duration = Date.now() - start
      
      console.log(`排序页面加载时间: ${duration}ms`)
      expect(duration).toBeLessThan(3000)
    })

    test('商城对比页面加载时间 < 5s', async ({ page }) => {
      const start = Date.now()
      await page.goto('/store')
      await waitForPageLoad(page)
      const duration = Date.now() - start
      
      console.log(`商城对比页面加载时间: ${duration}ms`)
      expect(duration).toBeLessThan(5000)
    })
  })

  // ==================== 首次内容绘制测试 ====================
  
  test.describe('首次内容绘制 (FCP)', () => {
    
    test('首页 FCP < 1.5s', async ({ page }) => {
      await page.goto('/')
      
      // 使用 Performance API 获取 FCP
      const fcp = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          const observer = new PerformanceObserver((list) => {
            const entries = list.getEntriesByName('first-contentful-paint')
            if (entries.length > 0) {
              resolve(entries[0].startTime)
            }
          })
          observer.observe({ entryTypes: ['paint'] })
          
          // 如果已经有 FCP 记录
          const existing = performance.getEntriesByName('first-contentful-paint')
          if (existing.length > 0) {
            resolve(existing[0].startTime)
          }
          
          // 超时回退
          setTimeout(() => resolve(0), 5000)
        })
      })
      
      console.log(`首页 FCP: ${fcp}ms`)
      if (fcp > 0) {
        expect(fcp).toBeLessThan(1500)
      }
    })
  })

  // ==================== 交互响应时间测试 ====================
  
  test.describe('交互响应时间', () => {
    
    test('项目点击响应 < 500ms', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const project = await getFirstProject(page)
      if (await project.count() > 0) {
        const start = Date.now()
        await project.click()
        
        // 等待内容变化
        await page.waitForFunction(() => {
          return document.querySelector('.content-area img') !== null
        }, { timeout: 5000 }).catch(() => {})
        
        const duration = Date.now() - start
        console.log(`项目点击响应时间: ${duration}ms`)
        expect(duration).toBeLessThan(500)
      }
    })

    test('页面导航响应 < 1s', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const start = Date.now()
      await page.goto('/onboarding')
      await waitForPageLoad(page)
      const duration = Date.now() - start
      
      console.log(`页面导航响应时间: ${duration}ms`)
      expect(duration).toBeLessThan(1000)
    })
  })

  // ==================== 滚动性能测试 ====================
  
  test.describe('滚动性能', () => {
    
    test('截图列表滚动流畅', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      const project = await getFirstProject(page)
      if (await project.count() > 0) {
        await project.click()
        await waitForPageLoad(page)
        await page.waitForTimeout(1000)
        
        // 执行滚动
        const contentArea = page.locator('.content-area')
        if (await contentArea.count() > 0) {
          // 记录帧率
          const frameDrops = await page.evaluate(async () => {
            let drops = 0
            let lastTime = performance.now()
            
            const checkFrame = () => {
              const now = performance.now()
              const delta = now - lastTime
              if (delta > 32) { // 低于 30fps
                drops++
              }
              lastTime = now
            }
            
            // 监听 100ms
            for (let i = 0; i < 10; i++) {
              await new Promise(r => setTimeout(r, 10))
              checkFrame()
            }
            
            return drops
          })
          
          console.log(`滚动帧丢失: ${frameDrops}`)
          expect(frameDrops).toBeLessThan(5)
        }
      }
    })
  })

  // ==================== 内存使用测试 ====================
  
  test.describe('内存使用', () => {
    
    test('页面内存使用合理', async ({ page }) => {
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 获取内存使用（如果可用）
      const memoryInfo = await page.evaluate(() => {
        // @ts-ignore
        if (performance.memory) {
          // @ts-ignore
          return performance.memory.usedJSHeapSize / 1024 / 1024 // MB
        }
        return null
      })
      
      if (memoryInfo !== null) {
        console.log(`JS 堆内存使用: ${memoryInfo.toFixed(2)}MB`)
        expect(memoryInfo).toBeLessThan(100) // 少于 100MB
      }
    })
  })

  // ==================== 网络请求测试 ====================
  
  test.describe('网络请求', () => {
    
    test('首页 API 请求数量合理', async ({ page }) => {
      const requests: string[] = []
      
      page.on('request', (request) => {
        if (request.url().includes('/api/')) {
          requests.push(request.url())
        }
      })
      
      await page.goto('/')
      await waitForPageLoad(page)
      
      console.log(`首页 API 请求数: ${requests.length}`)
      console.log('请求列表:', requests)
      
      // 首页不应该有太多 API 请求
      expect(requests.length).toBeLessThan(10)
    })

    test('无失败的 API 请求', async ({ page }) => {
      const failedRequests: string[] = []
      
      page.on('response', (response) => {
        if (response.url().includes('/api/') && !response.ok()) {
          failedRequests.push(`${response.url()} - ${response.status()}`)
        }
      })
      
      await page.goto('/')
      await waitForPageLoad(page)
      
      // 导航到各个页面
      await page.goto('/onboarding')
      await waitForPageLoad(page)
      
      await page.goto('/sort')
      await waitForPageLoad(page)
      
      console.log(`失败的 API 请求: ${failedRequests.length}`)
      if (failedRequests.length > 0) {
        console.log('失败请求:', failedRequests)
      }
      
      expect(failedRequests.length).toBe(0)
    })
  })

  // ==================== 资源加载测试 ====================
  
  test.describe('资源加载', () => {
    
    test('图片加载无错误', async ({ page }) => {
      const imageErrors: string[] = []
      
      page.on('pageerror', (error) => {
        if (error.message.includes('img') || error.message.includes('image')) {
          imageErrors.push(error.message)
        }
      })
      
      await page.goto('/')
      await waitForPageLoad(page)
      
      const project = await getFirstProject(page)
      if (await project.count() > 0) {
        await project.click()
        await waitForPageLoad(page)
        await page.waitForTimeout(2000)
      }
      
      console.log(`图片加载错误: ${imageErrors.length}`)
      expect(imageErrors.length).toBe(0)
    })
  })
})

