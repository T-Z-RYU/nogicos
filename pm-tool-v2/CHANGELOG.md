# 更新日志

本项目的所有重要变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 待发布的新功能

---

## [2.0.0] - 2025-12-29

### Added
- **全新前端** - Next.js 16 + React 19 重构
  - shadcn/ui 组件库
  - Framer Motion 动画
  - 设计令牌系统
- **Onboarding 分析功能** - 深度解析竞品 Onboarding 流程
  - 阶段标记 (Launch, Welcome, Goal, Paywall 等)
  - 截图顺序锁定
  - 批量标记和导出
- **Vision API 集成** - AI 视觉分析截图内容
- **项目管理增强**
  - 项目分支支持
  - 截图分类和排序
  - CSV/Markdown 导出
- **Playwright 测试** - E2E 测试覆盖
- **文档系统** - README、设计规范

### Changed
- **后端重构** - FastAPI 路由模块化
  - 拆分为 12 个路由模块
  - 服务层分离
- **设计系统** - Zino 全局设计规范 v3.0
  - 深色主题 (#0a0a0a)
  - 透明边框效果
  - 图片亮度状态控制

### Fixed
- 修复截图排序被打乱的问题
- 修复大项目加载性能问题

---

## [1.0.0] - 2024-12-15

### Added
- 基础截图下载功能
- Selenium 自动化脚本
- 简单的项目管理
- 截图分类脚本

---

## [0.1.0] - 2024-12-01

### Added
- 项目初始化
- screensdesign.com 下载脚本原型

