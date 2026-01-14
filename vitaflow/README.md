# VitaFlow

> AI 驱动的卡路里追踪 iOS App，让健康饮食变得简单

[![Platform](https://img.shields.io/badge/platform-iOS-blue.svg)]()
[![Status](https://img.shields.io/badge/status-开发中-yellow.svg)]()
[![Target](https://img.shields.io/badge/release-Q1%202025-green.svg)]()

## ✨ 功能亮点

- **AI 食物识别** - 拍照即可识别食物并计算卡路里
- **智能营养分析** - 自动追踪蛋白质、碳水、脂肪摄入
- **个性化建议** - 基于目标体重提供饮食建议
- **精美界面** - 现代化 UI 设计，流畅的用户体验

## 🎯 商业模式

| 项目 | 说明 |
|------|------|
| 付费模式 | Hard Paywall |
| 目标用户 | 关注健康饮食的 iOS 用户 |
| 主要竞品 | Cal AI, MyFitnessPal, Noom, Yazio |

## 🚀 快速开始

### 前置要求

- Node.js >= 18
- pnpm / npm
- Xcode (iOS 开发)

### App 复刻版本 (Web)

```bash
cd app-replica
npm install
npm run dev
```

访问 http://localhost:5173 查看 Web 预览版

### 运行测试

```bash
cd app-replica
npx playwright test
```

## 📁 项目结构

```
vitaflow/
├── app-replica/           # Web 复刻版本
│   ├── src/
│   │   ├── components/    # UI 组件
│   │   ├── pages/         # 页面
│   │   └── styles/        # 设计令牌
│   └── tests/             # Playwright 测试
├── app-v2/                # V2 版本
├── competitor-analysis/   # 竞品分析
│   ├── myfitnesspal/
│   └── _video-analysis/
├── design-iterations/     # 设计迭代
├── PROGRESS.md            # 进度追踪
├── ROADMAP.md             # 路线图
└── CHANGELOG.md           # 变更日志
```

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 前端 (Web) | React 18, TypeScript, Tailwind CSS, Vite |
| 移动端 | Swift, SwiftUI (计划中) |
| AI | 食物识别 API (待定) |
| 测试 | Playwright |
| 设计 | Figma |

## 📊 开发进度

### 已完成

- ✅ UI 组件库 (8/8 组件)
- ✅ 设计令牌系统
- ✅ Playwright 测试框架
- ✅ 竞品分析 (6/30)

### 进行中

- 🔄 更多竞品分析
- 🔄 设计迭代

### 待开始

- ⏳ iOS 原生开发
- ⏳ AI 食物识别集成
- ⏳ 后端 API

详见 [PROGRESS.md](./PROGRESS.md) 和 [ROADMAP.md](./ROADMAP.md)

## 📖 文档

- [进度追踪](./PROGRESS.md) - 每日进度和检查点
- [路线图](./ROADMAP.md) - 功能规划和时间表
- [变更日志](./CHANGELOG.md) - 版本更新记录
- [竞品分析](./competitor-analysis/竞品分析_健康健身App.md) - 市场研究

## 🎨 设计迭代

| 版本 | 预览 |
|------|------|
| v1 | `design-iterations/vitaflow_improved_v1.jpeg` |
| v2 | `design-iterations/vitaflow_premium_v2.jpeg` |
| v3 | `design-iterations/vitaflow_dribbble_v3.jpeg` |
| v4 (当前) | `design-iterations/vitaflow_clean_v4.jpeg` |

## 📄 License

Private - 仅供内部使用

---

> 目标：Q1 2025 上线 App Store

