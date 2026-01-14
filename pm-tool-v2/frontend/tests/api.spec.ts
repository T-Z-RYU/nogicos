import { test, expect } from '@playwright/test'

/**
 * PM Tool v2 - API 测试
 * 测试后端接口响应和数据格式
 */

const API_BASE = 'http://localhost:8001/api'

test.describe('📡 API 测试', () => {

  // ==================== 项目 API ====================
  
  test.describe('项目 API', () => {
    
    test('GET /api/projects 返回项目列表', async ({ request }) => {
      const response = await request.get(`${API_BASE}/projects`)
      
      expect(response.ok()).toBeTruthy()
      expect(response.status()).toBe(200)
      
      const data = await response.json()
      expect(data).toHaveProperty('projects')
      expect(Array.isArray(data.projects)).toBeTruthy()
      
      // 验证项目数据结构
      if (data.projects.length > 0) {
        const project = data.projects[0]
        expect(project).toHaveProperty('name')
        expect(project).toHaveProperty('display_name')
        expect(project).toHaveProperty('screen_count')
      }
    })

    test('GET /api/project-screenshots/{name} 返回截图列表', async ({ request }) => {
      // 首先获取一个项目
      const projectsRes = await request.get(`${API_BASE}/projects`)
      const projectsData = await projectsRes.json()
      
      if (projectsData.projects.length > 0) {
        // 使用路径格式的项目名（不编码斜杠）
        const projectName = projectsData.projects[0].name
        const response = await request.get(`${API_BASE}/project-screenshots/${projectName}`)
        
        expect(response.ok()).toBeTruthy()
        
        const data = await response.json()
        expect(data).toHaveProperty('screenshots')
        expect(Array.isArray(data.screenshots)).toBeTruthy()
      }
    })
  })

  // ==================== Onboarding API ====================
  
  test.describe('Onboarding API', () => {
    
    test('GET /api/onboarding/{project} 返回 Onboarding 范围', async ({ request }) => {
      const projectsRes = await request.get(`${API_BASE}/projects`)
      const projectsData = await projectsRes.json()
      
      if (projectsData.projects.length > 0) {
        const projectName = encodeURIComponent(projectsData.projects[0].name)
        const response = await request.get(`${API_BASE}/onboarding/${projectName}`)
        
        expect(response.ok()).toBeTruthy()
        
        const data = await response.json()
        expect(data).toHaveProperty('start')
        expect(data).toHaveProperty('end')
        expect(typeof data.start).toBe('number')
        expect(typeof data.end).toBe('number')
      }
    })

    test('POST /api/onboarding/{project} 保存 Onboarding 范围', async ({ request }) => {
      const projectsRes = await request.get(`${API_BASE}/projects`)
      const projectsData = await projectsRes.json()
      
      if (projectsData.projects.length > 0) {
        const projectName = encodeURIComponent(projectsData.projects[0].name)
        
        // 先获取当前值
        const currentRes = await request.get(`${API_BASE}/onboarding/${projectName}`)
        const currentData = await currentRes.json()
        
        // 保存（使用当前值，避免实际修改数据）
        const response = await request.post(`${API_BASE}/onboarding/${projectName}`, {
          data: {
            start: currentData.start,
            end: currentData.end,
          },
        })
        
        expect(response.ok()).toBeTruthy()
        
        const data = await response.json()
        expect(data).toHaveProperty('success')
      }
    })
  })

  // ==================== 排序 API ====================
  
  test.describe('排序 API', () => {
    
    test('GET /api/sort/{project} 返回排序数据', async ({ request }) => {
      const projectsRes = await request.get(`${API_BASE}/projects`)
      const projectsData = await projectsRes.json()
      
      if (projectsData.projects.length > 0) {
        const projectName = encodeURIComponent(projectsData.projects[0].name)
        const response = await request.get(`${API_BASE}/sort/${projectName}`)
        
        // 可能返回 200 或 404（如果没有排序数据）
        expect([200, 404]).toContain(response.status())
      }
    })

    test('GET /api/sort/{project}/deleted 返回已删除截图', async ({ request }) => {
      const projectsRes = await request.get(`${API_BASE}/projects`)
      const projectsData = await projectsRes.json()
      
      if (projectsData.projects.length > 0) {
        const projectName = encodeURIComponent(projectsData.projects[0].name)
        const response = await request.get(`${API_BASE}/sort/${projectName}/deleted`)
        
        expect(response.ok()).toBeTruthy()
        
        const data = await response.json()
        expect(data).toHaveProperty('batches')
        expect(Array.isArray(data.batches)).toBeTruthy()
      }
    })
  })

  // ==================== 商城对比 API ====================
  
  test.describe('商城对比 API', () => {
    
    test('GET /api/store-comparison 返回商城对比数据', async ({ request }) => {
      const response = await request.get(`${API_BASE}/store-comparison`)
      
      expect(response.ok()).toBeTruthy()
      
      const data = await response.json()
      expect(data).toHaveProperty('apps')
      expect(Array.isArray(data.apps)).toBeTruthy()
    })
  })

  // ==================== 分类 API ====================
  
  test.describe('分类 API', () => {
    
    test('GET /api/classify/{project} 返回分类数据', async ({ request }) => {
      const projectsRes = await request.get(`${API_BASE}/projects`)
      const projectsData = await projectsRes.json()
      
      if (projectsData.projects.length > 0) {
        const projectName = encodeURIComponent(projectsData.projects[0].name)
        const response = await request.get(`${API_BASE}/classify/${projectName}`)
        
        // 可能返回 200 或 404
        expect([200, 404]).toContain(response.status())
      }
    })
  })

  // ==================== 待处理截图 API ====================
  
  test.describe('待处理截图 API', () => {
    
    test('GET /api/pending-screenshots 返回待处理截图', async ({ request }) => {
      const response = await request.get(`${API_BASE}/pending-screenshots`)
      
      expect(response.ok()).toBeTruthy()
      
      const data = await response.json()
      expect(data).toHaveProperty('screenshots')
      expect(Array.isArray(data.screenshots)).toBeTruthy()
    })
  })

  // ==================== 错误处理测试 ====================
  
  test.describe('错误处理', () => {
    
    test('不存在的项目返回 404', async ({ request }) => {
      const response = await request.get(`${API_BASE}/projects/nonexistent-project-12345/screenshots`)
      
      expect(response.status()).toBe(404)
    })

    test('无效的请求体返回 422', async ({ request }) => {
      const projectsRes = await request.get(`${API_BASE}/projects`)
      const projectsData = await projectsRes.json()
      
      if (projectsData.projects.length > 0) {
        const projectName = encodeURIComponent(projectsData.projects[0].name)
        
        const response = await request.post(`${API_BASE}/onboarding/${projectName}`, {
          data: {
            // 缺少必要字段
            invalid: 'data',
          },
        })
        
        expect(response.status()).toBe(422)
      }
    })
  })

  // ==================== 性能测试 ====================
  
  test.describe('性能', () => {
    
    test('项目列表响应时间 < 2s', async ({ request }) => {
      const start = Date.now()
      const response = await request.get(`${API_BASE}/projects`)
      const duration = Date.now() - start
      
      expect(response.ok()).toBeTruthy()
      expect(duration).toBeLessThan(2000)
    })

    test('商城对比响应时间 < 3s', async ({ request }) => {
      const start = Date.now()
      const response = await request.get(`${API_BASE}/store-comparison`)
      const duration = Date.now() - start
      
      expect(response.ok()).toBeTruthy()
      expect(duration).toBeLessThan(3000)
    })
  })
})

