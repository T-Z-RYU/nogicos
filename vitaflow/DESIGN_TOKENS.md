# VitaFlow Design Tokens

> **Version**: 1.0  
> **Updated**: 2025/01/05  
> **Source**: DESIGN_SYSTEM_AUDIT.md  
> **Usage**: Figma Variables / iOS Development / React Native

---

## 🎨 Colors

### Core Palette (Slate System)

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `slate-900` | `#0F172A` | `rgb(15, 23, 42)` | 主色、主文字、CTA 背景 |
| `slate-800` | `#1E293B` | `rgb(30, 41, 59)` | 食物名称 |
| `slate-700` | `#334155` | `rgb(51, 65, 85)` | 次要标签 |
| `slate-600` | `#475569` | `rgb(71, 85, 105)` | 图表中心文字、箭头图标 |
| `slate-500` | `#64748B` | `rgb(100, 116, 139)` | 辅助文字、图标 |
| `slate-400` | `#94A3B8` | `rgb(148, 163, 184)` | 弱化文字、未选中态、Placeholder |
| `slate-200` | `#E2E8F0` | `rgb(226, 232, 240)` | 分割线、进度条背景、Toggle Off |
| `slate-100` | `#F1F5F9` | `rgb(241, 245, 249)` | 容器背景、页面渐变起点 |
| `slate-50` | `#F8FAFC` | `rgb(248, 250, 252)` | 页面渐变终点、弹窗背景 |
| `white` | `#FFFFFF` | `rgb(255, 255, 255)` | 卡片背景、选中态背景 |

### Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `text-primary` | `#0F172A` | 主文字 |
| `text-secondary` | `#64748B` | 次要文字 |
| `text-tertiary` | `#94A3B8` | 辅助文字 |
| `text-label` | `#334155` | 标签文字 |
| `bg-page-start` | `#F1F5F9` | 页面渐变起点 |
| `bg-page-end` | `#F8FAFC` | 页面渐变终点 |
| `bg-card` | `#FFFFFF` | 卡片背景 |
| `bg-container` | `#F1F5F9` | 容器背景 |
| `bg-modal` | `#F8FAFC` | 弹窗背景 |

### Nutrition Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `color-calories` | `#61E0BD` | 卡路里、进度、积极状态 |
| `color-protein` | `#07D1EC` | 蛋白质 |
| `color-carbs` | `#FDCA91` | 碳水化合物 |
| `color-fat` | `#FB7D91` | 脂肪 |

### Status Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `color-success` | `#61E0BD` | 成功、积极变化 |
| `color-warning` | `#FB6C83` | 警告、消极变化 |
| `color-danger` | `#FF5555` | 危险操作（删除账户） |

### Health Score Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `color-energy` | `#FAE338` | Energy Level |
| `color-mental` | `#FB6CAC` | Mental Clarity |
| `color-diet` | `#A588EC` | Diet Quality |

### Glass Effect

| Token | Value | Usage |
|-------|-------|-------|
| `glass-bg` | `rgba(15, 23, 42, 0.4)` | 毛玻璃背景 |
| `glass-blur` | `blur(10px)` | 毛玻璃模糊 |

### Overlay

| Token | Value | Usage |
|-------|-------|-------|
| `overlay-dark` | `rgba(0, 0, 0, 0.5)` | 弹窗遮罩 |
| `overlay-scan` | `rgba(0, 0, 0, 0.7)` | 扫描遮罩 |

---

## 🔤 Typography

### Font Family

```css
font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
```

### Font Weights

| Token | Value | CSS |
|-------|-------|-----|
| `font-regular` | 400 | `font-weight: 400` |
| `font-medium` | 500 | `font-weight: 500` |
| `font-semibold` | 600 | `font-weight: 600` |

### Type Scale (Semantic Naming)

| Token | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `text/display` | 48px | 53px | Medium | 超大数值、Hero 数字 |
| `text/heading` | 28px | 34px | Medium | 页面标题 |
| `text/title` | 20px | 26px | Medium | 导航标题、弹窗标题、中等数值 |
| `text/body` | 14px | 20px | Medium | 正文（强调）、列表项 |
| `text/body-regular` | 14px | 20px | Regular | 正文（普通）、描述文字 |
| `text/caption` | 12px | 17px | Regular | 辅助说明、标签、单位 |
| `text/label` | 10px | 14px | Medium | 底部导航、环形图中心、小标签 |

### Letter Spacing Rules

| 字号范围 | Letter Spacing | 场景 |
|----------|----------------|------|
| 10-12px | `-0.2px` | label, caption |
| 14-20px | `-0.4px` | body, title |
| 28px | `-0.4px` | heading |
| 48px | `-1.5px` | display |

---

## 🌫️ Shadows

### Shadow Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-sm` | `0px 1px 2px rgba(15,23,42,0.04), 0px 2px 4px rgba(15,23,42,0.03)` | 小控件（按钮、Pill） |
| `shadow-md` | `0px 1px 2px rgba(15,23,42,0.04), 0px 2px 6px -2px rgba(15,23,42,0.03)` | 次要卡片 |
| `shadow-lg` | `0px 1px 3px rgba(15,23,42,0.05), 0px 4px 12px rgba(15,23,42,0.03)` | 主卡片 |
| `shadow-cta` | `0px 2px 4px rgba(15,23,42,0.15)` | CTA 按钮 |
| `shadow-nav` | `0px -1px 3px rgba(15,23,42,0.04), 0px -4px 12px rgba(15,23,42,0.03)` | 底部导航 |

### Text Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-text-lg` | `0px 1px 2px rgba(15,23,42,0.08)` | 大数字 |
| `shadow-text-sm` | `0px 1px 2px rgba(15,23,42,0.05)` | 中等数字 |

### Toggle Knob Shadow

| Token | Value |
|-------|-------|
| `shadow-toggle` | `0px 0px 0px 1px rgba(15,23,42,0.04), 0px 3px 8px rgba(15,23,42,0.15), 0px 3px 1px rgba(15,23,42,0.06)` |

---

## 📐 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-sm` | `6px` | Tab 内部 |
| `radius-md` | `8px` | Tab 容器、小图片 |
| `radius-lg` | `12px` | 卡片、输入框、弹窗 |
| `radius-xl` | `16px` | 底部面板顶部 |
| `radius-2xl` | `24px` | 底部导航 |
| `radius-3xl` | `32px` | 模态框顶部 |
| `radius-full` | `1000px` | 按钮、Pills、头像、Toggle |

---

## 🖼️ Borders

| Token | Value | Usage |
|-------|-------|-------|
| `border-card` | `1px solid rgba(15,23,42,0.01)` | 卡片边框 |
| `border-container` | `1px solid rgba(15,23,42,0.03)` | 容器边框 |
| `border-image` | `1px solid rgba(15,23,42,0.05)` | 图片边框 |
| `border-input` | `2px solid #94A3B8` | 输入框默认 |
| `border-input-focus` | `2px solid #0F172A` | 输入框聚焦 |
| `border-button-secondary` | `2px solid #0F172A` | 次要按钮 |

---

## 📏 Spacing

### Base Scale (4px)

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | `4px` | 最小间距 |
| `space-2` | `8px` | 紧凑间距 |
| `space-3` | `12px` | 标准间距 |
| `space-4` | `16px` | 舒适间距 |
| `space-5` | `20px` | 区块间距 |
| `space-6` | `24px` | 大区块间距 |
| `space-8` | `32px` | 页面级间距 |
| `space-10` | `40px` | 底部安全区 |
| `space-12` | `48px` | 大安全区 |

### Common Patterns

| Pattern | Value | Usage |
|---------|-------|-------|
| `padding-card` | `16px` | 卡片内边距 |
| `padding-modal` | `24px` | 弹窗内边距 |
| `padding-page` | `20px` | 页面左右边距 |
| `gap-card` | `12px` | 卡片间距 |
| `gap-section` | `24px` | 区块间距 |
| `gap-form` | `16px` | 表单项间距 |

---

## 🎛️ Component Sizes

### Buttons

| Type | Height | Padding | Radius |
|------|--------|---------|--------|
| Primary (CTA) | `52px` | `12px 40px` | `1000px` |
| Secondary | `52px` | `12px 40px` | `1000px` |
| Small | `44px` | `0 24px` | `1000px` |
| Icon | `40px` | - | `1000px` |

### Inputs

| Type | Height | Padding | Radius |
|------|--------|---------|--------|
| Text Input | `48px` | `0 12px` | `12px` |
| List Item | `48px` | `0 12px` | `12px` |
| Card Input | `52px` | `16px` | `12px` |

### Toggle

| State | Width | Height | Knob Size |
|-------|-------|--------|-----------|
| Default | `51px` | `31px` | `27px` |

### Navigation

| Element | Size |
|---------|------|
| Back Button | `40x40px` |
| Scan Button | `56x56px` |
| Bottom Nav Height | ~`83px` |
| Nav Bar Height | ~`44px` |

---

## 🌈 Gradients

### Page Background

```css
background: linear-gradient(to bottom, #F1F5F9, #F8FAFC);
```

### Card Selection (Calendar)

```css
background: linear-gradient(to bottom, #FFFFFF, #F8FAFC);
```

---

## 📱 iOS Specific

### Safe Areas

| Area | Value |
|------|-------|
| Status Bar | `47px` (Dynamic Island) |
| Home Indicator | `34px` |
| Bottom Safe Area | `34px` |

### Home Indicator

| Property | Value |
|----------|-------|
| Background | `rgba(218,218,218,0.8)` |
| Size | `48 x 5px` |
| Radius | `100px` |

---

## 🔧 CSS Variables Export

```css
:root {
  /* Colors - Slate */
  --color-slate-900: #0F172A;
  --color-slate-800: #1E293B;
  --color-slate-700: #334155;
  --color-slate-600: #475569;
  --color-slate-500: #64748B;
  --color-slate-400: #94A3B8;
  --color-slate-200: #E2E8F0;
  --color-slate-100: #F1F5F9;
  --color-slate-50: #F8FAFC;
  --color-white: #FFFFFF;
  
  /* Colors - Nutrition */
  --color-calories: #61E0BD;
  --color-protein: #07D1EC;
  --color-carbs: #FDCA91;
  --color-fat: #FB7D91;
  
  /* Colors - Status */
  --color-success: #61E0BD;
  --color-warning: #FB6C83;
  --color-danger: #FF5555;
  
  /* Typography */
  --font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-regular: 400;
  --font-medium: 500;
  --font-semibold: 600;
  
  /* Shadows */
  --shadow-sm: 0px 1px 2px rgba(15,23,42,0.04), 0px 2px 4px rgba(15,23,42,0.03);
  --shadow-md: 0px 1px 2px rgba(15,23,42,0.04), 0px 2px 6px -2px rgba(15,23,42,0.03);
  --shadow-lg: 0px 1px 3px rgba(15,23,42,0.05), 0px 4px 12px rgba(15,23,42,0.03);
  --shadow-cta: 0px 2px 4px rgba(15,23,42,0.15);
  
  /* Border Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-3xl: 32px;
  --radius-full: 1000px;
  
  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
}
```

---

## 📋 Figma Variables Structure

```
📁 VitaFlow Design System
├── 📂 Colors
│   ├── 📂 Slate
│   │   ├── slate-900
│   │   ├── slate-800
│   │   ├── ...
│   │   └── slate-50
│   ├── 📂 Nutrition
│   │   ├── calories
│   │   ├── protein
│   │   ├── carbs
│   │   └── fat
│   ├── 📂 Status
│   │   ├── success
│   │   ├── warning
│   │   └── danger
│   └── 📂 Semantic
│       ├── text-primary
│       ├── text-secondary
│       ├── bg-page
│       └── bg-card
├── 📂 Typography
│   ├── font-family
│   ├── font-weight-regular
│   ├── font-weight-medium
│   └── font-weight-semibold
├── 📂 Effects
│   ├── shadow-sm
│   ├── shadow-md
│   ├── shadow-lg
│   └── shadow-cta
├── 📂 Radius
│   ├── radius-sm
│   ├── radius-md
│   ├── radius-lg
│   └── radius-full
└── 📂 Spacing
    ├── space-1
    ├── space-2
    ├── ...
    └── space-12
```

---

## ✅ Checklist for Implementation

### Figma Setup
- [x] Create Variables Collection "VitaFlow Tokens" (64 variables)
- [x] Add all Color variables (primitive + semantic)
- [x] Add all Effect styles (shadow/sm, md, lg, cta, nav)
- [x] Add all Text styles (display, heading, title, body, body-regular, caption, label)
- [ ] Link variables to components
- [ ] Create Design Guide page

### Development Handoff
- [ ] Export CSS variables file
- [ ] Export iOS Swift constants (if needed)
- [ ] Export React Native theme file (if needed)

---

*Last updated: 2025/01/05*


