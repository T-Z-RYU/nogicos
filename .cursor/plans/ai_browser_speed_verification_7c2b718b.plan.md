---
name: AI Browser Speed Verification
overview: 创建技术验证脚本，对比"传统 AI 从零理解页面"与"操作知识库直接执行"的速度差异，验证核心假设：有了操作知识，执行能快几十倍。
todos:
  - id: init-project
    content: 初始化 Node.js 项目，安装 Playwright、OpenAI SDK、Anthropic SDK
    status: pending
  - id: ai-client
    content: 实现 AI 客户端封装，支持 GPT-4 和 Claude API 调用
    status: pending
  - id: page-analyzer
    content: 实现页面分析器：截图/DOM 提取 + 发送给 AI 分析
    status: pending
  - id: baseline-executor
    content: 实现传统 AI 方式执行器（对照组）
    status: pending
  - id: knowledge-files
    content: 创建 Uniswap、Amazon、GitHub 的操作知识库 JSON
    status: pending
  - id: knowledge-executor
    content: 实现知识库方式执行器（实验组）
    status: pending
  - id: test-scenarios
    content: 编写三个测试场景脚本
    status: pending
  - id: run-and-report
    content: 运行测试，生成对比报告
    status: pending
---

# 技术验证：操作知识库 vs 传统 AI 方式速度对比

## 核心假设

如果浏览器"已经知道"网站怎么操作，执行速度可以比传统 AI 方式快 10-50 倍。

## 实验设计

### 对照组：传统 AI 方式（Baseline）

```javascript
打开页面 → 获取页面信息 → 发送给 AI 分析 → AI 返回操作 → 执行 → 重复
```

每一步都需要 AI 理解页面，预计每步 2-5 秒。

### 实验组：操作知识库方式（Our Approach）

```javascript
打开页面 → 识别网站 → 查询知识库 → 直接执行预定义流程
```

不需要 AI 分析，预计每步 100ms 以内。

## 测试场景

### 场景 1: Uniswap Swap（DeFi）

- 任务：从首页到 Swap 确认页面（不实际交易）
- 步骤：访问 → 点击 Swap → 选择代币 → 输入金额 → 到达确认界面
- 预计步骤数：5-6 步

### 场景 2: Amazon 商品搜索（电商）

- 任务：搜索商品并查看详情
- 步骤：访问 → 输入搜索词 → 搜索 → 点击第一个商品 → 查看详情
- 预计步骤数：4-5 步

### 场景 3: GitHub 仓库搜索（开发者工具）

- 任务：搜索仓库并查看 README
- 步骤：访问 → 搜索 → 点击仓库 → 查看信息
- 预计步骤数：4 步

## 技术实现

### 项目结构

```javascript
browser-speed-test/
├── package.json
├── src/
│   ├── baseline/           # 对照组：传统 AI 方式
│   │   ├── ai-client.ts    # AI API 封装（GPT-4 + Claude）
│   │   ├── page-analyzer.ts # 页面分析逻辑
│   │   └── executor.ts     # AI 驱动的执行器
│   │
│   ├── knowledge/          # 实验组：知识库方式
│   │   ├── sites/          # 网站操作知识
│   │   │   ├── uniswap.json
│   │   │   ├── amazon.json
│   │   │   └── github.json
│   │   ├── matcher.ts      # 网站识别
│   │   └── executor.ts     # 知识库驱动的执行器
│   │
│   ├── tests/              # 测试场景
│   │   ├── uniswap-swap.ts
│   │   ├── amazon-search.ts
│   │   └── github-search.ts
│   │
│   └── utils/
│       ├── metrics.ts      # 性能测量
│       └── reporter.ts     # 结果报告
│
├── results/                # 测试结果
└── README.md
```



### 知识库数据结构（示例：Uniswap）

```json
{
  "site": "app.uniswap.org",
  "type": "DEX",
  "tasks": {
    "swap": {
      "description": "Swap tokens",
      "steps": [
        {"action": "click", "selector": "[data-testid='swap-nav-link']", "wait": 1000},
        {"action": "click", "selector": "[data-testid='token-select']", "wait": 500},
        {"action": "type", "selector": "input[placeholder*='Search']", "value": "{{fromToken}}"},
        {"action": "click", "selector": "[data-testid='token-option-{{fromToken}}']"},
        {"action": "type", "selector": "input[inputmode='decimal']", "value": "{{amount}}"}
      ]
    }
  }
}
```



### 测量指标

- total_time: 任务总耗时（ms）
- steps_count: 执行步骤数
- ai_calls: AI API 调用次数
- ai_time: AI 分析耗时（ms）
- execution_time: 实际执行耗时（ms）
- success: 是否成功完成
- cost_estimate: 预估 API 成本（$）

### 结果输出格式

```javascript
┌─────────────────────────────────────────────────────────────────┐
│                    Speed Test Results                           │
├───────────────┬───────────────┬───────────────┬────────────────┤
│ Scenario      │ Baseline(GPT) │ Baseline(Claude)│ Knowledge     │
├───────────────┼───────────────┼───────────────┼────────────────┤
│ Uniswap Swap  │ 28.5s (5步)   │ 32.1s (5步)   │ 0.8s (5步)    │
│ Amazon Search │ 22.3s (4步)   │ 25.7s (4步)   │ 0.6s (4步)    │
│ GitHub Search │ 18.9s (4步)   │ 21.2s (4步)   │ 0.5s (4步)    │
├───────────────┼───────────────┼───────────────┼────────────────┤
│ Average       │ 23.2s         │ 26.3s         │ 0.63s         │
│ Speedup       │ 1x            │ 0.88x         │ 36.8x ⚡       │
└─────────────────────────────────────────────────────────────────┘
```



## 执行步骤

1. 初始化项目，安装依赖（Playwright, OpenAI SDK, Anthropic SDK）
2. 实现 AI 客户端封装（支持 GPT-4 和 Claude）
3. 实现页面分析器（截图/DOM 提取 + AI 分析）
4. 实现传统方式执行器（Baseline）
5. 创建三个网站的操作知识库 JSON
6. 实现知识库方式执行器
7. 编写三个测试场景
8. 运行测试并生成报告
9. 分析结果，验证假设

## 预期结果

- Baseline（GPT-4）：每个任务 20-35 秒
- Baseline（Claude）：每个任务 20-35 秒
- Knowledge 方式：每个任务 0.5-1 秒
- **预期加速比：30-50 倍**

## 风险与备选方案