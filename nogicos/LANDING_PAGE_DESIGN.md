# NogicOS Landing Page 设计规范

> 基于 Bytebot.ai 的像素级分析
> 最后更新：2026/01/13

---

## 一、设计参考

**参考网站**：[https://www.bytebot.ai/](https://www.bytebot.ai/)

**为什么参考 Bytebot**：
- 同属 Desktop AI Agent 赛道
- YC 背书的产品
- 设计简洁专业，转化率高
- 技术产品的最佳实践

---

## 二、配色方案

### 2.1 背景色

| 用途 | 颜色 | 说明 |
|------|------|------|
| 浅色背景 | `#f5f5f5` | Hero、FAQ、Blog |
| 深色背景 | `#1a1a1a` | Features、CTA、Footer |
| 白色背景 | `#ffffff` | 卡片、模态框 |

### 2.2 文字色

| 用途 | 浅底 | 深底 |
|------|------|------|
| 主文字 | `#1a1a1a` | `#ffffff` |
| 副文字 | `#666666` | `#999999` |
| 弱文字 | `#888888` | `#666666` |

### 2.3 强调色

| 用途 | 颜色 |
|------|------|
| 主强调 | `#a855f7` (紫色) |
| 渐变起点 | `#a855f7` |
| 渐变终点 | `#7c3aed` |
| 成功 | `#22c55e` |
| 警告 | `#f59e0b` |

### 2.4 按钮

| 类型 | 样式 |
|------|------|
| Primary | 黑色背景 `#1a1a1a` + 白色文字 + 圆角 8px |
| Secondary | 透明背景 + 白色边框 + 白色文字 |
| Ghost | 透明背景 + 文字链接样式 |

---

## 三、字体系统

### 3.1 字体选择

```css
/* 主字体 */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* 代码/标签字体 */
font-family: 'JetBrains Mono', 'Fira Code', monospace;
```

### 3.2 字号规范

| 用途 | 桌面 | 移动 | 字重 |
|------|------|------|------|
| H1 主标题 | 56px | 36px | 700 |
| H2 Section 标题 | 42px | 28px | 700 |
| H3 卡片标题 | 24px | 20px | 600 |
| H4 小标题 | 18px | 16px | 600 |
| Body 正文 | 16px | 15px | 400 |
| Small 小字 | 14px | 13px | 400 |
| Label 标签 | 12px | 11px | 500 (monospace) |

### 3.3 行高

| 元素 | 行高 |
|------|------|
| 标题 | 1.2 |
| 副标题 | 1.4 |
| 正文 | 1.7 |

---

## 四、间距系统

### 4.1 基础间距

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 24px;
--space-6: 32px;
--space-7: 48px;
--space-8: 64px;
--space-9: 96px;
--space-10: 128px;
```

### 4.2 Section 间距

| 元素 | 间距 |
|------|------|
| Section 之间 | 120px |
| Section 内部 padding | 80px |
| 卡片之间 | 24px |
| 卡片内部 padding | 32px |

### 4.3 最大宽度

| 容器 | 宽度 |
|------|------|
| Content | 1200px |
| Text | 720px |
| Narrow | 560px |

---

## 五、页面结构

### 5.1 Section 顺序

```
1. Navigation      - 固定顶部导航
2. Hero            - 主视觉 + CTA
3. Quote           - 引用（可选）
4. Comparison      - 差异化对比 ⭐ NogicOS 特有
5. Features        - 核心功能（深色背景）
6. Use Cases       - 3个使用场景
7. Blog            - 最新文章（可选）
8. FAQ             - 常见问题
9. Final CTA       - 最终行动号召（深色背景）
10. Footer         - 页脚
```

### 5.2 各 Section 详解

#### Navigation
```
┌──────────────────────────────────────────────────────────────┐
│  Logo          Features  Docs  Blog        [Get Started →]  │
└──────────────────────────────────────────────────────────────┘
```
- 固定顶部，白色背景
- 滚动时添加阴影
- Logo 左对齐
- 链接居中或靠左
- CTA 按钮右对齐

#### Hero
```
┌──────────────────────────────────────────────────────────────┐
│                    [Backed by Y Combinator]                  │
│                                                              │
│         Workspace AI connects your                          │
│         tabs, files, and apps                               │
│                                                              │
│         The AI that connects your browser tabs,              │
│         local files, and desktop apps.                       │
│                                                              │
│         [Request Early Access]                               │
│         ● Only 50 spots left                                 │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                          │ │
│  │              [产品动画/GIF]                               │ │
│  │                                                          │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

#### Comparison (NogicOS 特有)
```
┌──────────────────────────────────────────────────────────────┐
│                    How we're different                       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ ChatGPT  │  │  Cursor  │  │  ramAIn  │  │ NogicOS  │    │
│  │          │  │          │  │          │  │    ✓     │    │
│  │ ❌ Tabs  │  │ ❌ Tabs  │  │ ❌ Tabs  │  │ ✓ Tabs   │    │
│  │ ❌ Files │  │ ✓ Code   │  │ ❌ Files │  │ ✓ Files  │    │
│  │ ❌ Apps  │  │ ❌ Apps  │  │ ✓ Msgs   │  │ ✓ Apps   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────────────────────────────────────┘
```

#### Features (深色背景)
```
┌──────────────────────────────────────────────────────────────┐
│  █████████████████████████████████████████████████████████  │
│                                                              │
│                  Why a Workspace AI                          │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ 🔗 Connecting    │  │ 🎯 Fine Control  │                 │
│  │                  │  │                  │                 │
│  │ [动画/截图]       │  │ [动画/截图]       │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ 🔄 Recovery      │  │ 📜 History       │  │ 🔒 Local   │ │
│  └──────────────────┘  └──────────────────┘  └────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

#### Use Cases
```
┌──────────────────────────────────────────────────────────────┐
│                      Live Demos                              │
│                                                              │
│  Use Case #1                                                 │
│  ───────────                                                 │
│  Competitive Analysis                                        │
│                                                              │
│  NogicOS opens competitor websites, extracts features,       │
│  and creates a comparison document in your local folder.     │
│                                                              │
│  [视频/GIF 演示]                                              │
│                                                              │
│  Use Case #2                                                 │
│  ───────────                                                 │
│  YC Application                                              │
│  ...                                                         │
└──────────────────────────────────────────────────────────────┘
```

#### FAQ
```
┌──────────────────────────────────────────────────────────────┐
│              Frequently Asked Questions                      │
│                                                              │
│  ✕ What is NogicOS?                                         │
│    NogicOS is a Workspace AI that connects your browser      │
│    tabs, local files, and desktop apps...                    │
│                                                              │
│  + How is NogicOS different from ramAIn?                    │
│  + What can NogicOS actually do?                            │
│  + Is my data secure?                                        │
│  + Do I need coding skills?                                  │
│  ...                                                         │
└──────────────────────────────────────────────────────────────┘
```

#### Final CTA (深色背景)
```
┌──────────────────────────────────────────────────────────────┐
│  █████████████████████████████████████████████████████████  │
│                                                              │
│          Ready to connect your workspace?                    │
│                                                              │
│          Start with full context in minutes —                │
│          no credit card required.                            │
│                                                              │
│                   [Get Started →]                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 六、组件规范

### 6.1 卡片 (Card)

```css
.card {
  background: #ffffff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* 深色卡片 */
.card-dark {
  background: #252525;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### 6.2 按钮 (Button)

```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 15px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #1a1a1a;
  color: #ffffff;
}

.btn-primary:hover {
  background: #333333;
  transform: scale(1.02);
}

.btn-secondary {
  background: transparent;
  border: 1px solid #ffffff;
  color: #ffffff;
}
```

### 6.3 FAQ 手风琴 (Accordion)

```css
.faq-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 24px 0;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  font-size: 18px;
}

.faq-answer {
  padding-top: 16px;
  color: #666666;
  line-height: 1.7;
}
```

### 6.4 标签 (Badge)

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 500;
}

.badge-yc {
  background: #ff6600;
  color: #ffffff;
}

.badge-beta {
  background: rgba(168, 85, 247, 0.1);
  color: #a855f7;
}
```

---

## 七、动画规范

### 7.1 缓动函数

```css
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
--ease-out-quad: cubic-bezier(0.25, 0.46, 0.45, 0.94);
```

### 7.2 入场动画

```css
/* Fade in from bottom */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: fadeInUp 0.8s var(--ease-out-expo) forwards;
}
```

### 7.3 交错动画

```javascript
// Motion (Framer Motion) 配置
const staggerContainer = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  show: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] }
  },
};
```

---

## 八、视觉素材清单

### 8.1 AI 可以生成的 ✅

| 素材 | 说明 | 格式 |
|------|------|------|
| Logo | 几何图形 + 文字 | SVG |
| 图标 (tabs) | 浏览器标签图标 | SVG |
| 图标 (files) | 文件/文件夹图标 | SVG |
| 图标 (apps) | 应用/窗口图标 | SVG |
| Connects 动画 | 三个元素连接的动画 | CSS/JS |
| 差异化对比图 | vs ChatGPT/Cursor/ramAIn | React 组件 |
| 产品流程图 | Think → Act → Observe | SVG/React |
| 代码片段高亮 | 语法高亮 | CSS |

### 8.2 需要录制的 ❌

| 素材 | 说明 | 建议工具 |
|------|------|---------|
| Hero 产品动画 | AI 操作 tabs+files+apps | OBS + 剪辑 |
| Demo 1: 竞品分析 | 完整流程录屏 | Loom |
| Demo 2: YC 申请 | 完整流程录屏 | Loom |
| Demo 3: 数据整合 | 完整流程录屏 | Loom |

### 8.3 可选的

| 素材 | 说明 | 如何获取 |
|------|------|---------|
| YC 徽章 | "Backed by Y Combinator" | 拿到 YC 后 |
| 用户头像 | Testimonials | 真实用户 |
| 博客封面 | 插画风格 | Midjourney |

---

## 九、FAQ 内容

### 9.1 必须有的问题

1. **What is NogicOS?**
2. **How is NogicOS different from ChatGPT/Claude?**
3. **How is NogicOS different from ramAIn?**
4. **What can NogicOS actually do?**
5. **Is my data secure?**
6. **Do I need coding skills?**
7. **How quickly can I get started?**
8. **What platforms does NogicOS support?**
9. **How much does it cost?**
10. **What AI models does it use?**

### 9.2 完整 FAQ 内容

#### Q: What is NogicOS?

A: NogicOS is a Workspace AI that connects your browser tabs, local files, and desktop apps. Unlike ChatGPT which only sees what you paste, NogicOS sees your complete work environment and takes action directly in it.

Think of it as an AI assistant that can browse websites, read your files, and work across your apps—all in one unified context.

#### Q: How is NogicOS different from ChatGPT/Claude?

A: ChatGPT and Claude are chat-based AI—they only see what you copy-paste into the conversation. NogicOS connects to your actual workspace:

- **ChatGPT**: Only sees text you paste
- **Claude**: Only sees files you upload
- **NogicOS**: Sees your browser tabs, local files, and desktop apps

This means no more copy-pasting context. No more explaining what's on your screen.

#### Q: How is NogicOS different from ramAIn?

A: ramAIn focuses on communication automation—WhatsApp, Email, Slack. NogicOS focuses on research and analysis:

- **ramAIn**: Helps you reply to messages faster
- **NogicOS**: Helps you do competitive analysis, market research, document integration

Different users, different use cases. ramAIn is your messaging assistant. NogicOS is your research assistant.

#### Q: What can NogicOS actually do?

A: NogicOS can handle tasks that span multiple apps:

- **Competitive Analysis**: Open competitor websites, extract features, create comparison docs
- **Market Research**: Search the web, gather data, organize into reports
- **Document Integration**: Read files, extract data, combine into new documents
- **Form Filling**: Read your documents, understand form questions, fill in answers
- **Data Extraction**: Scrape websites, process the data, save to local files

#### Q: Is my data secure?

A: Yes. NogicOS runs entirely on your machine:

- All data stays local—nothing is uploaded to our servers
- Your files are never sent anywhere
- Browser sessions are sandboxed
- You control what NogicOS can access

We're local-first by design.

#### Q: Do I need coding skills?

A: No coding required. Just describe what you want in plain English:

- "Analyze this competitor's pricing page"
- "Find all PDFs in my Downloads folder and summarize them"
- "Fill out this form using my resume"

NogicOS figures out how to do it.

#### Q: How quickly can I get started?

A: About 5 minutes:

1. Download NogicOS
2. Add your API key (Anthropic Claude)
3. Start working

No complex setup, no cloud configuration.

#### Q: What platforms does NogicOS support?

A: Currently Windows and macOS. Linux support coming soon.

#### Q: How much does it cost?

A: NogicOS is free during beta. You only pay for the AI API usage (Anthropic Claude), which is typically a few cents per task.

#### Q: What AI models does NogicOS use?

A: NogicOS uses Anthropic's Claude models (Claude 3.5 Sonnet by default). We chose Claude for its superior reasoning and vision capabilities.

---

## 十、SEO 规范

### 10.1 Meta Tags

```html
<title>NogicOS - Workspace AI connects your tabs, files, and apps</title>
<meta name="description" content="NogicOS is a Workspace AI that connects your browser tabs, local files, and desktop apps. Do research and analysis without copy-pasting context." />
<meta name="keywords" content="AI, workspace, desktop agent, browser automation, file management, productivity" />
```

### 10.2 Open Graph

```html
<meta property="og:title" content="NogicOS - Workspace AI" />
<meta property="og:description" content="The AI that connects your tabs, files, and apps" />
<meta property="og:image" content="/og-image.png" />
<meta property="og:url" content="https://nogicos.ai" />
<meta property="og:type" content="website" />
```

### 10.3 OG Image 规范

- **尺寸**: 1200 x 630 px
- **内容**: Logo + Tagline + 产品截图
- **背景**: 深色 (#1a1a1a)
- **格式**: PNG

---

## 十一、文案风格

### 11.1 语气

- **简洁**: 不啰嗦，直击要点
- **自信**: 不用 "try to"、"might"、"hopefully"
- **具体**: 用数字和例子，不用模糊的形容词
- **行动导向**: 多用动词

### 11.2 示例

❌ "NogicOS might help you work more efficiently by potentially automating some tasks"

✅ "NogicOS connects your tabs, files, and apps. No more copy-pasting."

❌ "Our advanced AI technology leverages cutting-edge machine learning"

✅ "AI that sees your screen and takes action"

---

## 十二、下一步

### 12.1 Phase 1: 基础页面（本周）

- [ ] 更新 Hero 文案
- [ ] 创建 Comparison Section
- [ ] 创建 Features Section
- [ ] 创建 FAQ Section
- [ ] 创建 Final CTA

### 12.2 Phase 2: 视觉增强（下周）

- [ ] 录制 Hero 产品动画
- [ ] 录制 3 个 Demo 视频
- [ ] 设计 Logo
- [ ] 创建 OG Image

### 12.3 Phase 3: 上线准备

- [ ] SEO 优化
- [ ] 性能优化
- [ ] 移动端适配
- [ ] 部署

---

*文档版本: 1.0*
*最后更新: 2026/01/13*
*基于: Bytebot.ai 设计分析*
