# PM Screenshot Tool V2

> 产品经理竞品分析工具 - 截图管理、分类、AI 分析一站式解决方案

[![Backend](https://img.shields.io/badge/backend-FastAPI-009688.svg)]()
[![Frontend](https://img.shields.io/badge/frontend-Next.js%2016-black.svg)]()
[![Status](https://img.shields.io/badge/status-开发中-yellow.svg)]()

## ✨ 功能亮点

- **截图批量下载** - 从 screensdesign.com 等网站批量获取竞品截图
- **智能分类** - 自动识别 Onboarding、Paywall、Core 等流程阶段
- **AI 视觉分析** - 使用 Vision API 分析 UI 设计模式
- **Onboarding 分析** - 深度解析竞品 Onboarding 流程
- **导出功能** - 支持 CSV、Markdown 报告导出

## 🎯 使用场景

| 场景 | 说明 |
|------|------|
| 竞品分析 | 快速获取和分析竞品 App 截图 |
| Onboarding 研究 | 分析竞品的用户引导流程 |
| UI 灵感收集 | 建立设计参考库 |
| 产品报告 | 生成可视化竞品分析报告 |

## 🚀 快速开始

### 前置要求

- Python >= 3.10
- Node.js >= 18
- Chrome (用于截图下载)

### 启动后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8004
```

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

## 📁 项目结构

```
pm-tool-v2/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── config.py         # 配置
│   │   ├── models/           # 数据模型
│   │   ├── routers/          # API 路由
│   │   │   ├── projects.py   # 项目管理
│   │   │   ├── screenshots.py # 截图管理
│   │   │   ├── analysis.py   # AI 分析
│   │   │   ├── onboarding.py # Onboarding 分析
│   │   │   └── export.py     # 导出功能
│   │   └── services/         # 业务逻辑
│   ├── scripts/              # 工具脚本
│   │   ├── download_screensdesign.py
│   │   └── batch_analyze.py
│   └── data/                 # 数据存储
│       ├── projects/         # 项目截图
│       └── analysis/         # 分析结果
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # UI 组件
│   │   └── store/            # 状态管理
│   └── tests/                # Playwright 测试
├── exports/                  # 导出文件
│   └── onboarding-screens-v2/
└── scripts/                  # 全局脚本
```

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 后端 | Python 3.11, FastAPI, Pydantic |
| 前端 | Next.js 16, React 19, TypeScript |
| UI | Tailwind CSS 4, shadcn/ui, Framer Motion |
| AI | OpenAI Vision API |
| 测试 | Playwright |
| 自动化 | Selenium (截图下载) |

## 📊 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/projects` | GET | 获取项目列表 |
| `/api/projects/{id}/screenshots` | GET | 获取项目截图 |
| `/api/analysis/vision` | POST | AI 视觉分析 |
| `/api/onboarding/analyze` | POST | Onboarding 分析 |
| `/api/export/csv` | GET | 导出 CSV |
| `/api/export/markdown` | GET | 导出 Markdown |

## 🎨 设计规范

遵循 Zino 全局设计规范 v3.0：

- **背景**: `#0a0a0a` 主色调
- **边框**: `rgba(255,255,255,0.06)` → hover `0.15`
- **图片亮度**: 非选中 `0.35` → hover `0.6` → 选中 `1`
- **按钮**: 透明背景 + 边框，无渐变

详见 [frontend/README.md](./frontend/README.md)

## ⚠️ 重要规则

> **截图排序不可打乱**：Screen_001 → 002 → 003 的顺序是**绝对的**，
> 反映了视频播放/下载的原始顺序。任何分类只是标签，**不能改变展示顺序**。

## 📖 文档

- [前端说明](./frontend/README.md) - 技术栈和组件使用
- [测试说明](./frontend/tests/README.md) - 测试用例
- [Onboarding 演示](./frontend/ONBOARDING_DEMO_HANDOFF.md) - 功能演示

## 🔧 常用命令

```bash
# 启动后端
cd backend && python -m uvicorn app.main:app --reload --port 8004

# 启动前端
cd frontend && npm run dev

# 运行测试
cd frontend && npx playwright test

# 批量分析截图
cd backend && python scripts/batch_analyze.py
```

## 📄 License

Private - 仅供内部使用

