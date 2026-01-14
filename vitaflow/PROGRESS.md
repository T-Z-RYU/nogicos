# VitaFlow 进度追踪

> 最后更新：2024-12-26
> 当前阶段：设计 + 竞品分析
> 整体进度：待定

---

## 项目信息

| 项目 | VitaFlow |
|------|----------|
| 类型 | iOS AI 卡路里追踪 App |
| 模式 | Hard Paywall |
| 目标 | Q1 2025 上线 |
| 竞品 | Cal AI, Noom, MyFitnessPal, Yazio |

---

## 检查点总览

| # | 检查点 | 截止日期 | 状态 | 验收标准 |
|---|--------|----------|------|----------|
| M1 | | | 🔴 | |
| M2 | | | 🔴 | |
| M3 | | | 🔴 | |
| M4 | | | 🔴 | |

> 检查点待规划

---

## 已完成工作

### App 复刻 `app-replica/`

| 组件 | 状态 | 文件 |
|------|------|------|
| StatusBar | ✅ | `components/StatusBar.tsx` |
| Header | ✅ | `components/Header.tsx` |
| CalendarStrip | ✅ | `components/CalendarStrip.tsx` |
| CalorieCard | ✅ | `components/CalorieCard.tsx` |
| MacroCards | ✅ | `components/MacroCards.tsx` |
| MealTabs | ✅ | `components/MealTabs.tsx` |
| FoodList | ✅ | `components/FoodList.tsx` |
| BottomNavigation | ✅ | `components/BottomNavigation.tsx` |

| 基础设施 | 状态 |
|----------|------|
| 设计令牌 | ✅ `styles/design-tokens.css` |
| Tailwind 配置 | ✅ `tailwind.config.js` |
| Playwright 测试 | ✅ `tests/` |

### 竞品分析 `competitor-analysis/`

**已分析（6/30）：**

| 产品 | 类型 | 月收入 | 状态 |
|------|------|--------|------|
| MyFitnessPal | 营养追踪 | $9.4M | ✅ |
| Cal AI | AI 识别 | $2.0M | ✅ |
| Calm | 冥想 | $3.7M | ✅ |
| Flo | 女性健康 | $8.6M | ✅ |
| Strava | 运动社交 | $7.0M | ✅ |
| Runna | 跑步训练 | $2.5M | ✅ |

**待分析 P0 竞品：**
- Peloton, WeightWatchers, Zwift, LADDER, Fitbit, Carbon, Headspace

### 设计迭代 `design-iterations/`

| 版本 | 文件 |
|------|------|
| v1 | `vitaflow_improved_v1.jpeg` |
| v2 | `vitaflow_premium_v2.jpeg` |
| v3 | `vitaflow_dribbble_v3.jpeg` |
| v4 | `vitaflow_clean_v4.jpeg` |

---

## 风险登记

| 风险 | 等级 | 状态 | 应对措施 |
|------|------|------|----------|
| | | | |

---

## 进度日志

### 2024-12-26
- 📁 建立项目文档体系（PROGRESS.md, ROADMAP.md, CHANGELOG.md）
- 📖 回顾设计令牌
- 📖 学习 NogicOS V2 工作方式

---

## 动态调整机制

### 当遇到问题时

```
问题发生
    │
    ▼
评估影响（影响哪个检查点？）
    │
    ├─► 小问题（30分钟内能解决）──► 直接解决
    │
    └─► 大问题 ──► 记录 CHANGELOG.md
                        │
                        ▼
                   评估选项
                   ┌─────────────────┐
                   │ 1. 绕过（换方案）│
                   │ 2. 延期（调时间）│
                   │ 3. 砍功能（减范围）│
                   └─────────────────┘
```

### 调整原则
1. **Q1 上线是硬约束** - 不能动
2. **砍功能 > 降质量** - 宁可少做，不做烂
3. **每次调整必记录** - 写 CHANGELOG

