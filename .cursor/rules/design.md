# 设计规范详情

## 🎨 设计风格词典 (2025 Edition)

### 布局模式 (Layout Patterns)
| 模式 | 特征 | 适用场景 |
|------|------|----------|
| **Bento Grid** | 模块化卡片、不等尺寸、视觉层级分明 | 功能展示、Dashboard、Landing |
| **Editorial** | 杂志式网格、强排版层级、大标题 | 品牌故事、内容站、作品集 |
| **Horizontal Scroll** | 横向滚动、画廊式 | 作品展示、产品陈列 |
| **Sticky Sections** | 固定区块、滚动切换内容 | 产品介绍、时间线 |
| **Layered Depth** | 多层叠加、Z轴深度、视差 | 沉浸式叙事 |

### 视觉质感 (Visual Textures)
| 质感 | 特征 | 情感 | 实现方式 |
|------|------|------|----------|
| **Glassmorphism 2.0** | 深层透明、折射、模糊叠加 | 高级、轻盈 | `backdrop-filter: blur()` |
| **Liquid Glass** | 动态折射、光影响应 | 未来、沉浸 | WebGL + 实时光照 |
| **Aurora Gradients** | 极光色彩、流动渐变 | 梦幻、科技 | Mesh gradient + animation |
| **Mesh Gradients** | 多点渐变、有机过渡 | 温暖、现代 | CSS conic-gradient / SVG |
| **Grain/Noise** | 颗粒质感、复古胶片感 | 艺术、真实 | SVG filter / CSS noise |
| **Deep Glow** | 霓虹发光、暗底亮元素 | 科技、游戏 | `box-shadow` + blur |

### 风格类型定义
| 风格 | 视觉特征 | 情感传达 | 适用场景 |
|------|----------|----------|----------|
| **Minimalist** | 大量留白、细线字体、低对比度 | 专注、高效、信任 | 效率工具、SaaS |
| **Neo-Brutalist** | 明亮色块、粗边框、高对比 | 大胆、年轻、有态度 | 创意机构、潮牌 |
| **Swiss** | 网格、无衬线、极度规整 | 理性、清晰、秩序 | 企业官网 |
| **Organic** | 流动曲线、自然色彩、不规则形状 | 自然、亲和 | 健康、生活方式 |
| **Retro-Futurism** | 霓虹、渐变、像素、科幻字体 | 怀旧、创新 | 游戏、娱乐 |

### 情感-风格速查表
| 当用户表达... | AI 应选择... |
|--------------|-------------|
| "高级感" | Liquid Glass, 深色+留白, 精致微交互 |
| "科技感" | Aurora Gradient, Glow效果, 3D元素 |
| "年轻活力" | 明亮色彩, Neo-Brutalist, 趣味动效 |
| "专业可信" | Swiss网格, 清晰排版, 克制动效 |
| "沉浸叙事" | Parallax, Sticky Scroll, Kinetic Typography |
| "独特个性" | Neo-Brutalist, 不规则布局, 大胆配色 |

### 2025 年度热门组合
| 组合 | 构成元素 | 适合产品 |
|------|----------|----------|
| **Tech Minimal** | Bento Grid + Glassmorphism + 微交互 | SaaS、开发者工具 |
| **Immersive Dark** | 深色模式 + Deep Glow + 3D + Parallax | 游戏、创意、科技 |
| **Editorial Modern** | Editorial布局 + Kinetic Typography | 品牌官网、杂志 |
| **Apple-like Premium** | Liquid Glass + Bento + Sticky Scroll | 高端消费品 |

---

## 🌐 风格知识库

**Awwwards 年度获奖作品（风格学习）**：
- Igloo Inc - 沉浸式 3D 叙事的极致
- Immersive Garden - 极简与 3D 深度的平衡
- Locomotive - 现代编辑设计 + 滚动编排

**日常参考（实际产品）**：
- Vercel - 简洁、深色模式、精致微交互
- Linear - 极简高效、键盘驱动

---

## 🎯 设计令牌系统

设计令牌文件位置: `PM_Screenshot_Tool/static/css/tokens.css`

```css
:root {
    /* 颜色 - 使用 oklch 色彩空间 */
    --color-primary: oklch(0.65 0.2 250);
    --color-background: oklch(0.98 0 0);
    --color-text: oklch(0.15 0 0);
    
    /* 间距 */
    --spacing-xs: 0.25rem;  /* 4px */
    --spacing-sm: 0.5rem;   /* 8px */
    --spacing-md: 1rem;     /* 16px */
    --spacing-lg: 1.5rem;   /* 24px */
    --spacing-xl: 2rem;     /* 32px */
    
    /* 圆角 */
    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    
    /* 动效 */
    --transition-fast: 150ms ease;
    --transition-normal: 250ms ease;
    --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
}

@media (prefers-color-scheme: dark) {
    :root {
        --color-background: oklch(0.15 0 0);
        --color-text: oklch(0.95 0 0);
    }
}
```

---

## 🖥️ PM_Screenshot_Tool 完整 UI 规范

> 基于 Linear App 风格

### 设计基调
- **风格**: Linear App 风格 - 简洁、专业、现代
- **主题**: 深色模式 (Dark Mode)
- **字体**: Urbanist (主要) + SF Mono (代码/数字)

### 核心颜色
| 用途 | 颜色值 |
|------|--------|
| 背景-主 | `#0a0a0a` |
| 背景-卡片 | `#111111`, `#1a1a1a` |
| 边框-默认 | `rgba(255,255,255,0.06)` |
| 边框-悬停 | `rgba(255,255,255,0.15)` |
| 边框-选中 | `#fff` |
| 文字-主要 | `#ffffff` |
| 文字-次要 | `#9ca3af`, `#6b7280` |

### 交互状态设计原则
- **选中 vs 非选中**: 图片用 `filter: brightness()` 变暗，边框和文字保持清晰
- **悬停反馈**: 边框变亮，图片亮度提升
- **导航高亮**: 白色左边框 (`border-left: 2px solid #fff`)
- **亮度层级**:  
  - 非选中图片: `brightness(0.35)`
  - 悬停图片: `brightness(0.6)`
  - 选中图片: `brightness(1)`

### 组件规则
- **按钮**: 透明背景 + 边框，避免渐变色
- **图标**: 线性 SVG 图标，不用 emoji
- **卡片**: 圆角 8-12px，边框分层表达状态
- **导航**: 左边框高亮，不用背景色块
- **标题**: 中英双语 `<h3>中文 <span>English</span></h3>`

### 禁止使用
- ❌ 紫色渐变背景 (`linear-gradient(135deg, #5E6AD2, #8B5CF6)`)
- ❌ Emoji 作为 UI 图标
- ❌ 整体 `opacity` 降低（应只对图片用 `filter`）
- ❌ 彩色实心按钮背景

### 多页面一致性
- 以 `onboarding.html` 为设计基准
- 侧边栏结构和样式跨页面统一
- 公共样式放 `common.css`，页面特定用内联 `<style>`

