/**
 * PM Tool v2 - 综合测试运行器
 * 
 * 运行方式：
 * npx ts-node tests/run-all-tests.ts
 * 
 * 或者使用 npm scripts:
 * npm run test:all
 */

import { execSync } from 'child_process'

interface TestSuite {
  name: string
  command: string
  critical: boolean
}

const testSuites: TestSuite[] = [
  {
    name: '🔧 API 测试',
    command: 'npx playwright test tests/api.spec.ts',
    critical: true,
  },
  {
    name: '🎨 设计一致性测试',
    command: 'npx playwright test tests/design-consistency.spec.ts',
    critical: true,
  },
  {
    name: '📸 视觉回归测试',
    command: 'npx playwright test tests/visual-regression.spec.ts',
    critical: false,
  },
  {
    name: '♿ 可访问性测试',
    command: 'npx playwright test tests/accessibility.spec.ts',
    critical: false,
  },
  {
    name: '🚀 用户流程测试',
    command: 'npx playwright test tests/user-flow.spec.ts',
    critical: true,
  },
  {
    name: '🎯 Onboarding 功能测试',
    command: 'npx playwright test tests/features/onboarding.spec.ts',
    critical: true,
  },
  {
    name: '📋 排序功能测试',
    command: 'npx playwright test tests/features/sort.spec.ts',
    critical: true,
  },
  {
    name: '⚡ 性能测试',
    command: 'npx playwright test tests/performance.spec.ts',
    critical: false,
  },
]

interface TestResult {
  suite: string
  passed: boolean
  duration: number
  error?: string
}

async function runTests(): Promise<void> {
  console.log('╔════════════════════════════════════════════════════════════╗')
  console.log('║           PM Tool v2 - 综合测试运行器                       ║')
  console.log('╚════════════════════════════════════════════════════════════╝')
  console.log('')

  const results: TestResult[] = []
  const startTime = Date.now()

  for (const suite of testSuites) {
    console.log(`\n▶ 运行 ${suite.name}...`)
    console.log('─'.repeat(60))

    const suiteStart = Date.now()
    
    try {
      execSync(suite.command, {
        stdio: 'inherit',
        encoding: 'utf-8',
      })
      
      results.push({
        suite: suite.name,
        passed: true,
        duration: Date.now() - suiteStart,
      })
      
      console.log(`✅ ${suite.name} 通过`)
    } catch (error) {
      results.push({
        suite: suite.name,
        passed: false,
        duration: Date.now() - suiteStart,
        error: error instanceof Error ? error.message : String(error),
      })
      
      console.log(`❌ ${suite.name} 失败`)
      
      if (suite.critical) {
        console.log('\n⚠️  关键测试失败，建议修复后继续')
      }
    }
  }

  // 打印总结
  const totalDuration = Date.now() - startTime
  const passed = results.filter(r => r.passed).length
  const failed = results.filter(r => !r.passed).length

  console.log('\n')
  console.log('╔════════════════════════════════════════════════════════════╗')
  console.log('║                       测试总结                              ║')
  console.log('╚════════════════════════════════════════════════════════════╝')
  console.log('')

  for (const result of results) {
    const status = result.passed ? '✅' : '❌'
    const duration = `${(result.duration / 1000).toFixed(1)}s`
    console.log(`${status} ${result.suite.padEnd(30)} ${duration}`)
  }

  console.log('')
  console.log('─'.repeat(60))
  console.log(`总计: ${passed} 通过, ${failed} 失败`)
  console.log(`耗时: ${(totalDuration / 1000).toFixed(1)}s`)
  console.log('')

  if (failed > 0) {
    console.log('❌ 部分测试失败，请查看上方详细信息')
    process.exit(1)
  } else {
    console.log('✅ 所有测试通过!')
    process.exit(0)
  }
}

runTests().catch(console.error)

