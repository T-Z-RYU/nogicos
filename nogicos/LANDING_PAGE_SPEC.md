# NogicOS Landing Page 设计规范

> 给新窗口的完整开发指南
> 最后更新：2025/01/04
> 设计师：Claude (基于 frontend-design skill)

---

## 🎯 项目概述

### 目标
1. **展示 Demo** - 给 YC 面试官看
2. **收集 Waitlist** - 获取早期用户
3. **传达品牌** - 建立 NogicOS 独特视觉身份

### 上线时间
**2025/01/10 前**（YC 截止日期）

### 技术栈
```
Next.js 14 (App Router) + TypeScript + Tailwind CSS + Motion (Framer Motion) + Vercel
```

---

## 🎨 设计理念：「穿透」

### 核心概念

NogicOS 的本质是**打通三层**：浏览器、文件、桌面。设计语言应该体现这种「穿透」和「融合」。

**视觉隐喻：**
- 玻璃层叠 (Glassmorphism evolved)
- 透明边界
- 光线穿透
- 信息流动

**情感基调：**
- 专业但温暖（区别于 Cursor 的冷调技术感）
- 可信赖的智能（不是炫酷的 AI 噱头）
- 从容不迫的效率（不是焦虑的"快速"）

### 差异化定位

| 竞品 | 风格 | NogicOS 差异 |
|------|------|--------------|
| Cursor | 冷调紫色、代码感、开发者 | 温暖、融合感、知识工作者 |
| Linear | 彩虹渐变、极简、SaaS | 有深度、层次感、智能 |
| Notion | 黑白、插图、亲和 | 更专业、更有技术质感 |

---

## 🖌️ 视觉规范

### 色彩系统

```css
:root {
  /* 主色调 - 深空蓝（温暖的深色，不是纯黑） */
  --bg-primary: #0a0e14;
  --bg-secondary: #111822;
  --bg-tertiary: #1a2332;
  
  /* 强调色 - 琥珀金（温暖、智能、可信赖） */
  --accent-primary: #f5a623;
  --accent-secondary: #ffc857;
  --accent-glow: rgba(245, 166, 35, 0.15);
  
  /* 辅助色 - 三层代表色 */
  --layer-browser: #4ecdc4;    /* 浏览器 - 青绿 */
  --layer-files: #a78bfa;       /* 文件 - 紫罗兰 */
  --layer-desktop: #f472b6;     /* 桌面 - 粉红 */
  
  /* 文字 */
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-tertiary: #64748b;
  
  /* 玻璃效果 */
  --glass-bg: rgba(17, 24, 34, 0.7);
  --glass-border: rgba(255, 255, 255, 0.08);
  --glass-blur: 16px;
}
```

### 字体系统

```css
/* 显示字体 - 独特、有性格 */
--font-display: 'Clash Display', 'Satoshi', sans-serif;

/* 正文字体 - 优雅、易读 */
--font-body: 'General Sans', 'Plus Jakarta Sans', sans-serif;

/* 代码字体 - 技术感 */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

**字号规范：**
```css
--text-hero: clamp(3rem, 8vw, 6rem);      /* Hero 标题 */
--text-h1: clamp(2rem, 4vw, 3.5rem);      /* 章节标题 */
--text-h2: clamp(1.5rem, 3vw, 2rem);      /* 小标题 */
--text-body: 1.125rem;                     /* 正文 18px */
--text-small: 0.875rem;                    /* 辅助文字 */

/* Letter Spacing */
--tracking-tight: -0.02em;                 /* 大标题 */
--tracking-normal: -0.01em;                /* 正文 */
```

### 间距系统

```css
--space-xs: 0.5rem;    /* 8px */
--space-sm: 1rem;      /* 16px */
--space-md: 1.5rem;    /* 24px */
--space-lg: 2.5rem;    /* 40px */
--space-xl: 4rem;      /* 64px */
--space-2xl: 6rem;     /* 96px */
--space-section: 8rem; /* 128px - 章节间距 */
```

### 圆角系统

```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 20px;
--radius-xl: 28px;
--radius-full: 9999px;
```

---

## 🏗️ 页面结构

### 信息架构

```
Landing Page
├── Navigation (固定顶部)
│   ├── Logo
│   ├── Links: Features | Demo | Pricing
│   └── CTA: Join Waitlist
│
├── Hero Section
│   ├── Headline: "The AI that works where you work"
│   ├── Subline: Browser. Files. Desktop. Complete context.
│   ├── CTA Buttons: [Watch Demo] [Join Waitlist]
│   └── Hero Visual: 三层穿透动画
│
├── Problem Section
│   ├── Headline: "AI is blind to your workspace"
│   └── Comparison Cards: ChatGPT | Claude | Cursor | NogicOS
│
├── Solution Section
│   ├── Headline: "One AI. Three layers. Complete context."
│   └── Layer Visualization: Browser + Files + Desktop
│
├── Demo Section
│   ├── Video/GIF: 实际操作演示
│   └── Caption: 展示关键功能
│
├── Features Section
│   ├── Feature 1: Complete Context (sees everything)
│   ├── Feature 2: Direct Action (not just chat)
│   └── Feature 3: Local-first privacy
│
├── Waitlist Section
│   ├── Headline: "Be the first to try NogicOS"
│   ├── Email Input
│   └── Submit Button
│
└── Footer
    ├── Logo
    ├── Links
    └── Social / YC Badge (if applicable)
```

---

## 🎬 动效规范

### 入场动画 (Page Load)

```tsx
// Hero 标题 - 从下方淡入
const heroTitle = {
  initial: { opacity: 0, y: 40 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] }
  }
}

// 子元素交错
const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.3
    }
  }
}

const staggerItem = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] }
  }
}
```

### 滚动触发 (Scroll Reveal)

```tsx
// 滚动进入视口时触发（只执行一次）
<motion.section
  initial={{ opacity: 0, y: 60 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: "-100px" }}
  transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
/>
```

### 三层穿透动画 (Hero Visual)

```tsx
// 三个层级依次出现，形成穿透效果
const layers = [
  { name: 'desktop', color: 'var(--layer-desktop)', delay: 0 },
  { name: 'files', color: 'var(--layer-files)', delay: 0.2 },
  { name: 'browser', color: 'var(--layer-browser)', delay: 0.4 },
]

// 每层有微妙的浮动效果
const floatAnimation = {
  y: [0, -10, 0],
  transition: {
    duration: 4,
    repeat: Infinity,
    ease: "easeInOut"
  }
}
```

### 按钮交互

```tsx
// 主按钮 - 发光效果
<motion.button
  whileHover={{ 
    scale: 1.02,
    boxShadow: "0 0 30px var(--accent-glow)"
  }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 25 }}
/>

// 次按钮 - 边框闪烁
<motion.button
  whileHover={{
    borderColor: "var(--accent-primary)",
    transition: { duration: 0.2 }
  }}
/>
```

---

## 🧩 核心组件

### 1. 玻璃卡片 (GlassCard)

```tsx
// components/GlassCard.tsx
import { motion } from 'framer-motion'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  glow?: boolean
}

export function GlassCard({ children, className, glow }: GlassCardProps) {
  return (
    <motion.div
      className={`
        relative overflow-hidden rounded-xl
        bg-[var(--glass-bg)] backdrop-blur-[var(--glass-blur)]
        border border-[var(--glass-border)]
        ${glow ? 'shadow-[0_0_40px_var(--accent-glow)]' : ''}
        ${className}
      `}
      whileHover={{
        borderColor: 'rgba(255, 255, 255, 0.15)',
        transition: { duration: 0.2 }
      }}
    >
      {children}
    </motion.div>
  )
}
```

### 2. 三层可视化 (LayerVisualization)

```tsx
// components/LayerVisualization.tsx
import { motion } from 'framer-motion'

const layers = [
  { 
    id: 'browser', 
    label: 'Browser', 
    color: 'var(--layer-browser)',
    icon: '🌐',
    offset: { x: -20, y: -30 }
  },
  { 
    id: 'files', 
    label: 'Files', 
    color: 'var(--layer-files)',
    icon: '📁',
    offset: { x: 0, y: 0 }
  },
  { 
    id: 'desktop', 
    label: 'Desktop', 
    color: 'var(--layer-desktop)',
    icon: '🖥️',
    offset: { x: 20, y: 30 }
  },
]

export function LayerVisualization() {
  return (
    <div className="relative w-[500px] h-[400px]">
      {layers.map((layer, i) => (
        <motion.div
          key={layer.id}
          className="absolute w-[300px] h-[200px] rounded-xl"
          style={{
            background: `linear-gradient(135deg, ${layer.color}20, ${layer.color}05)`,
            border: `1px solid ${layer.color}40`,
            left: `calc(50% - 150px + ${layer.offset.x}px)`,
            top: `calc(50% - 100px + ${layer.offset.y}px)`,
            zIndex: 3 - i,
          }}
          initial={{ opacity: 0, scale: 0.8, y: 50 }}
          animate={{ 
            opacity: 1, 
            scale: 1, 
            y: 0,
            transition: { delay: i * 0.2, duration: 0.6 }
          }}
          whileHover={{ scale: 1.02 }}
        >
          <div className="p-4 flex items-center gap-2">
            <span className="text-2xl">{layer.icon}</span>
            <span style={{ color: layer.color }}>{layer.label}</span>
          </div>
        </motion.div>
      ))}
      
      {/* 连接线动画 */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <motion.path
          d="M150,100 Q250,200 350,100"
          stroke="var(--accent-primary)"
          strokeWidth="2"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ delay: 0.8, duration: 1 }}
        />
      </svg>
    </div>
  )
}
```

### 3. 对比卡片 (ComparisonGrid)

```tsx
// components/ComparisonGrid.tsx
const aiTools = [
  {
    name: 'ChatGPT',
    canSee: 'Text you paste',
    cantSee: 'Your files, browser',
    limited: true
  },
  {
    name: 'Claude',
    canSee: 'Uploaded files',
    cantSee: 'Your workflow, screen',
    limited: true
  },
  {
    name: 'Cursor',
    canSee: 'Your codebase',
    cantSee: 'Browser, design files',
    limited: true
  },
  {
    name: 'NogicOS',
    canSee: 'Browser + Files + Desktop',
    cantSee: 'Nothing',
    limited: false,
    highlight: true
  },
]

export function ComparisonGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {aiTools.map((tool, i) => (
        <motion.div
          key={tool.name}
          className={`
            p-6 rounded-xl border
            ${tool.highlight 
              ? 'bg-[var(--accent-glow)] border-[var(--accent-primary)]' 
              : 'bg-[var(--glass-bg)] border-[var(--glass-border)]'
            }
          `}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: i * 0.1 }}
        >
          <h3 className="text-xl font-semibold mb-4">{tool.name}</h3>
          <div className="space-y-2 text-sm">
            <p className="text-green-400">✓ {tool.canSee}</p>
            <p className={tool.limited ? 'text-red-400' : 'text-[var(--text-secondary)]'}>
              {tool.limited ? '✗' : '—'} {tool.cantSee}
            </p>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
```

### 4. Waitlist 表单 (WaitlistForm)

```tsx
// components/WaitlistForm.tsx
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'

export function WaitlistForm() {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('loading')
    
    try {
      // TODO: 替换为实际的 API 端点
      const res = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })
      
      if (res.ok) {
        setStatus('success')
        setEmail('')
      } else {
        setStatus('error')
      }
    } catch {
      setStatus('error')
    }
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
    >
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
        className="
          flex-1 px-4 py-3 rounded-lg
          bg-[var(--bg-secondary)] border border-[var(--glass-border)]
          text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]
          focus:outline-none focus:border-[var(--accent-primary)]
          transition-colors
        "
      />
      <motion.button
        type="submit"
        disabled={status === 'loading'}
        className="
          px-6 py-3 rounded-lg font-medium
          bg-[var(--accent-primary)] text-[var(--bg-primary)]
          hover:bg-[var(--accent-secondary)]
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors
        "
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {status === 'loading' ? 'Joining...' : 'Join Waitlist'}
      </motion.button>
      
      {status === 'success' && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-green-400 text-sm mt-2"
        >
          You're on the list! 🎉
        </motion.p>
      )}
    </motion.form>
  )
}
```

---

## 📁 项目结构

```
nogicos-landing/
├── app/
│   ├── layout.tsx          # Root layout + fonts + metadata
│   ├── page.tsx            # Landing page
│   ├── globals.css         # CSS variables + Tailwind
│   └── api/
│       └── waitlist/
│           └── route.ts    # Waitlist API endpoint
├── components/
│   ├── Navigation.tsx
│   ├── Hero.tsx
│   ├── Problem.tsx
│   ├── Solution.tsx
│   ├── Demo.tsx
│   ├── Features.tsx
│   ├── Waitlist.tsx
│   ├── Footer.tsx
│   └── ui/
│       ├── GlassCard.tsx
│       ├── Button.tsx
│       └── LayerVisualization.tsx
├── public/
│   ├── fonts/              # Clash Display, General Sans
│   ├── images/
│   └── demo.mp4            # Demo 视频
├── lib/
│   └── utils.ts
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 🚀 快速开始

### 1. 创建项目

```bash
npx create-next-app@latest nogicos-landing --typescript --tailwind --app --src-dir=false
cd nogicos-landing
```

### 2. 安装依赖

```bash
npm install framer-motion
npm install @fontsource/jetbrains-mono
```

### 3. 配置字体

从 [Fontshare](https://www.fontshare.com/) 下载：
- Clash Display
- General Sans

或使用 Google Fonts 替代：
```tsx
// app/layout.tsx
import { Space_Grotesk, DM_Sans } from 'next/font/google'

const display = Space_Grotesk({ 
  subsets: ['latin'],
  variable: '--font-display'
})

const body = DM_Sans({ 
  subsets: ['latin'],
  variable: '--font-body'
})
```

### 4. 配置 Tailwind

```ts
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#0a0e14',
          secondary: '#111822',
          tertiary: '#1a2332',
        },
        accent: {
          primary: '#f5a623',
          secondary: '#ffc857',
        },
        layer: {
          browser: '#4ecdc4',
          files: '#a78bfa',
          desktop: '#f472b6',
        },
      },
      fontFamily: {
        display: ['var(--font-display)', 'sans-serif'],
        body: ['var(--font-body)', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}

export default config
```

### 5. 部署到 Vercel

```bash
npm i -g vercel
vercel
```

---

## 📋 Checklist

### 设计
- [ ] Hero 动画流畅
- [ ] 三层可视化清晰
- [ ] 对比图直观
- [ ] 移动端适配
- [ ] 暗色主题一致

### 功能
- [ ] Waitlist 表单工作
- [ ] Demo 视频加载
- [ ] 页面性能优化 (LCP < 2.5s)
- [ ] SEO 元数据完整

### 上线前
- [ ] 域名绑定
- [ ] 分析代码（Vercel Analytics / Plausible）
- [ ] 测试所有链接
- [ ] 压缩图片/视频

---

## 🔗 资源链接

### 字体
- [Fontshare - Clash Display](https://www.fontshare.com/fonts/clash-display)
- [Fontshare - General Sans](https://www.fontshare.com/fonts/general-sans)

### 图标
- [Lucide Icons](https://lucide.dev/)
- [Phosphor Icons](https://phosphoricons.com/)

### 动画参考
- [Motion Documentation](https://motion.dev/)
- [Framer Motion Examples](https://www.framer.com/motion/examples/)

### 设计灵感
- [Awwwards](https://www.awwwards.com/)
- [Godly.website](https://godly.website/)

---

## 📝 开发命令

```bash
# 开发
npm run dev

# 构建
npm run build

# 预览
npm run start

# 部署
vercel --prod
```

---

*此文档由 Claude 基于 frontend-design skill 生成*
*在新窗口中打开此文件，让 AI 帮你完成开发*


