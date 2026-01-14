# Zino Next.js Template

基于 2025 设计规范的 Next.js 项目模板，集成 shadcn/ui、Framer Motion 和设计令牌系统。

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Next.js | 16+ | React 框架 (App Router) |
| React | 19+ | UI 库 |
| TypeScript | 5+ | 类型系统 |
| Tailwind CSS | 4+ | 原子化 CSS |
| shadcn/ui | latest | UI 组件库 |
| Framer Motion | 12+ | 动画库 |
| ESLint | 9+ | 代码检查 |
| Prettier | 3+ | 代码格式化 |
| Husky | 9+ | Git Hooks |

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 项目结构

```
src/
├── app/                    # Next.js App Router
│   ├── globals.css         # 全局样式 + shadcn/ui 变量
│   ├── layout.tsx          # 根布局
│   └── page.tsx            # 首页
├── components/
│   ├── demo/               # 示例组件
│   │   ├── bento-grid.tsx  # Bento Grid 布局示例
│   │   └── hero-section.tsx # Hero 区域示例
│   ├── motion/             # Framer Motion 封装
│   │   ├── fade-in.tsx     # 淡入动画
│   │   ├── stagger-children.tsx # 交错动画
│   │   └── index.ts        # 导出
│   └── ui/                 # shadcn/ui 组件
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       └── ...
├── lib/
│   └── utils.ts            # 工具函数 (cn)
└── styles/
    └── tokens.css          # 设计令牌
```

## 设计令牌

设计令牌定义在 `src/styles/tokens.css`，包含：

- **颜色系统** - 使用 oklch 色彩空间
- **间距系统** - xs/sm/md/lg/xl/2xl/3xl
- **圆角系统** - sm/md/lg/xl/2xl/full
- **字体系统** - 大小、粗细、行高
- **阴影系统** - sm/md/lg/xl + glass
- **动效系统** - 时长、缓动函数、预设过渡
- **层级系统** - z-index 规范
- **暗色模式** - 自动适配

## Motion 组件

### FadeIn

```tsx
import { FadeIn } from '@/components/motion'

<FadeIn delay={0.1} direction="up" distance={24}>
  <h1>Hello World</h1>
</FadeIn>
```

### StaggerChildren

```tsx
import { StaggerChildren, StaggerItem } from '@/components/motion'

<StaggerChildren delayChildren={0.2}>
  <StaggerItem>Item 1</StaggerItem>
  <StaggerItem>Item 2</StaggerItem>
</StaggerChildren>
```

## 添加 shadcn/ui 组件

```bash
npx shadcn@latest add [component-name]

# 示例
npx shadcn@latest add accordion
npx shadcn@latest add tabs
npx shadcn@latest add dropdown-menu
```

## 代码质量

- **ESLint** - 代码检查
- **Prettier** - 代码格式化 (含 Tailwind CSS 插件)
- **Husky** - Git pre-commit 钩子
- **lint-staged** - 仅检查暂存文件

提交代码时会自动运行 ESLint 和 Prettier。

## 设计风格参考

本模板遵循 Zino 全局设计规范 v3.0：

- **布局**: Bento Grid、Sticky Sections
- **质感**: Glassmorphism 2.0、Aurora Gradients
- **动效**: Kinetic Typography、Parallax Layers
- **交互**: Card Hover Effects、Progressive Reveal

## License

MIT
