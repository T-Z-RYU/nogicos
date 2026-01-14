# 🍌 Nano Banana Pro UI 设计 Prompt 模板

> 基于 AIJasonZ 的 4 步工作流方法论

---

## 🎯 核心原则

1. **拆解任务** - 不要一次让模型"随便设计"，分步骤来
2. **专注单点** - 每个 prompt 只聚焦一个设计维度
3. **明确参考** - 提供具体的风格参考和约束
4. **迭代优化** - 生成后提取资产，再优化细节

---

## 📐 Step 1: 布局结构 Prompt

### 模板
```
Design a [页面类型] layout for a [产品类型] [平台].

Layout requirements:
- Screen size: [尺寸]
- Header: [顶部内容描述]
- Main content: [主要内容描述]
- Footer/Navigation: [底部内容描述]

Information hierarchy (from most to least important):
1. [最重要的信息]
2. [次重要的信息]
3. [辅助信息]

Style: Clean wireframe style, grayscale, focus on layout structure only.
```

### 示例
```
Design a home screen layout for a fitness tracking mobile app.

Layout requirements:
- Screen size: iPhone 14 Pro (393 x 852)
- Header: User greeting with avatar, notification bell
- Main content: Today's activity stats in card format, weekly progress chart
- Footer: Bottom navigation with 4 tabs (Home, Workout, Stats, Profile)

Information hierarchy:
1. Today's step count and calories burned
2. Quick-start workout buttons
3. Weekly activity trend chart
4. Recent achievements

Style: Clean wireframe style, grayscale, focus on layout structure only.
```

---

## 🎨 Step 2: 视觉风格 Prompt

### 模板
```
Create a high-fidelity UI design for a [产品类型] app [页面].

Visual style:
- Overall aesthetic: [风格关键词，如 minimal, modern, playful]
- Color scheme: Primary [主色], Secondary [辅色], Background [背景色]
- Typography: [字体风格]
- Corner radius: [圆角风格]
- Special effects: [特殊效果，如 glassmorphism, gradients]

The design should feel [情感描述，如 professional, friendly, premium].

Reference style: [参考 App 或网站名称]
```

### 示例
```
Create a high-fidelity UI design for a meditation app home screen.

Visual style:
- Overall aesthetic: calm, natural, minimal
- Color scheme: Primary #6B8E7D (sage green), Secondary #F5E6D3 (warm beige), Background #FAFAFA
- Typography: Rounded, friendly sans-serif (like Nunito)
- Corner radius: Large (20px) for cards, full radius for buttons
- Special effects: Soft shadows, subtle gradients, nature-inspired illustrations

The design should feel peaceful, welcoming, and premium.

Reference style: Calm app, Headspace
```

---

## 🧩 Step 3: 组件设计 Prompt

### 模板
```
Design a [组件名称] component for a [产品类型] app.

Component specifications:
- Purpose: [组件用途]
- States: [需要的状态，如 default, hover, active, disabled]
- Content: [包含的内容]
- Dimensions: [大小约束]

Visual requirements:
- Style: [风格要求]
- Colors: [配色要求]
- Must include: [必须包含的元素]

Show all states in a single image, arranged horizontally.
```

### 示例
```
Design a workout card component for a fitness app.

Component specifications:
- Purpose: Display a single workout session users can start
- States: Default, Hover/Pressed, Completed, Locked
- Content: Workout icon, title, duration, difficulty level, start button
- Dimensions: Full width, approximately 120px height

Visual requirements:
- Style: Modern, energetic, slightly rounded corners
- Colors: White background, blue accent (#4A90D9), green for completed (#34C759)
- Must include: Visual progress indicator, difficulty dots

Show all 4 states in a single image, arranged horizontally.
```

---

## 🖼️ Step 4: 完整页面 Prompt

### 模板
```
Design a complete [页面类型] for a [产品类型] [平台] app.

Page purpose: [页面目的]

Content sections (top to bottom):
1. [第一区域]: [内容描述]
2. [第二区域]: [内容描述]
3. [第三区域]: [内容描述]
4. [第四区域]: [内容描述]

Design specifications:
- Screen: [尺寸]
- Style: [风格]
- Colors: [配色]
- Key interactions: [关键交互说明]

The design should be realistic, high-fidelity, and ready for development handoff.
Include realistic content (not lorem ipsum).
```

### 示例
```
Design a complete dashboard page for a personal finance iOS app.

Page purpose: Help users quickly understand their financial health and take action

Content sections (top to bottom):
1. Header: User greeting "Good morning, Alex", current date, notification icon
2. Balance overview: Total balance card with spending trend indicator
3. Quick actions: Send, Request, Pay bills, Invest - as icon buttons
4. Recent transactions: List of 4-5 recent transactions with merchant logo, name, amount
5. Bottom navigation: Home, Cards, Analytics, Profile

Design specifications:
- Screen: iPhone 14 Pro (393 x 852)
- Style: Clean, minimal, professional with subtle depth
- Colors: Primary #1A1A2E (dark blue), Accent #4ECDC4 (teal), Background #F8F9FA
- Key interactions: Balance card is tappable, transactions are swipeable

The design should be realistic, high-fidelity, and ready for development handoff.
Use realistic dollar amounts and merchant names.
```

---

## ✂️ Step 5: 资产提取 Prompt

### 提取图标
```
Extract and generate a set of [数量] icons for a [产品类型] app.

Icon requirements:
- Style: [线性/填充/双色调]
- Size: [尺寸] pixels
- Stroke width: [线条粗细] (if line icons)
- Corner style: [圆角/直角]

Icons needed:
1. [图标1描述]
2. [图标2描述]
3. [图标3描述]
...

Arrange all icons in a grid on a white background.
Each icon should be clearly separated.
```

### 提取插画元素
```
Generate a decorative illustration element for a [产品类型] app.

Illustration requirements:
- Style: [扁平/3D/手绘]
- Subject: [主题]
- Mood: [情感]
- Colors: [配色]
- Usage: [用途，如 empty state, onboarding, header decoration]

The illustration should be on a transparent or solid [颜色] background.
Keep it simple enough to work at small sizes.
```

---

## 🔄 迭代优化 Prompt

### 调整布局
```
Based on the previous design, please modify:
- Move [元素] to [新位置]
- Make [元素] larger/smaller
- Add more spacing between [元素A] and [元素B]
- Remove [不需要的元素]

Keep all other elements unchanged.
```

### 调整风格
```
Keep the same layout, but change the visual style:
- New color scheme: [新配色]
- New typography: [新字体风格]
- Add/Remove: [效果，如 shadows, gradients]

The content and layout should remain exactly the same.
```

### 添加细节
```
Add the following details to the design:
- [细节1]
- [细节2]
- [细节3]

Keep the overall design unchanged, only add these specific elements.
```

---

## 💡 高级技巧

### 1. 使用参考图
```
Using the attached image as a reference for [风格/布局/配色], 
design a [页面类型] for a [产品类型] app.

Keep the [要保留的元素] but change [要改变的元素].
```

### 2. 多方案对比
```
Generate 3 different design variations for a [页面类型]:

Variation A: [风格描述]
Variation B: [风格描述]
Variation C: [风格描述]

Arrange all 3 variations side by side in a single image.
```

### 3. 深色/浅色模式
```
Design both light mode and dark mode versions of this [页面类型].

Light mode:
- Background: [浅色]
- Text: [深色]

Dark mode:
- Background: [深色]
- Text: [浅色]

Show both versions side by side.
```

### 4. 响应式设计
```
Design the same [页面类型] for 3 different screen sizes:

1. Mobile (375 x 812)
2. Tablet (820 x 1180)
3. Desktop (1440 x 900)

Show all 3 versions in a single image, scaled appropriately.
```

---

## 📋 快速 Prompt 公式

```
Design a [保真度: wireframe/high-fidelity] [页面类型] 
for a [产品类型] [平台: mobile/web/desktop] app.

Style: [3-5个风格关键词]
Colors: [主色/辅色/背景色]
Must include: [关键元素列表]
Reference: [参考 App/网站]

[额外要求]
```

### 一句话快速版
```
[风格] [页面类型] for [产品类型] [平台], [配色], include [关键元素], like [参考]
```

**示例**:
```
Minimal onboarding screen for a language learning iOS app, blue and white, include mascot character and progress indicator, like Duolingo
```

---

*模板版本: v1.0*  
*创建日期: 2025-12-19*  
*适用于: Nano Banana Pro + Gemini 3 Pro*
