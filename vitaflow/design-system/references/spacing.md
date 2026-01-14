# VitaFlow 间距与圆角系统

## 间距系统 (Spacing)

### 基础间距

| Token | 值 | 用途 |
|-------|-----|------|
| spacing-20 | 20px | 页面边距、大组件间距 |
| spacing-16 | 16px | 组件内主间距、图片与文字间距 |
| spacing-12 | 12px | 组件间距、宏量元素间距 |
| spacing-10 | 10px | 卡片内边距、食物卡片间距 |
| spacing-8 | 8px | Tab 内边距、日期组件间距 |
| spacing-6 | 6px | 小元素间距 |
| spacing-4 | 4px | 图标与文字间距、紧凑间距 |
| spacing-2 | 2px | 微间距 |

### 页面布局

```
┌────────────────────────────────────┐
│←─20px─→ Content Area ←─20px─→     │
│                                    │
│  Header                            │
│  ↓ 20px                            │
│  Calendar Strip                    │
│  ↓ 20px                            │
│  Main Cards                        │
│  ↓ 16px                            │
│  Tab Bar                           │
│  ↓ 12px                            │
│  Food List                         │
│                                    │
└────────────────────────────────────┘
```

### 卡片内部

```
┌─────────────────────────────────┐
│ ←10px→                    ←10px→│
│ ↑10px                           │
│ [Image] ←16px→ [Content]        │
│                    ↓10px        │
│                [Macros] gap:12px│
│ ↓10px                           │
└─────────────────────────────────┘
```

---

## 圆角系统 (Border Radius)

| Token | 值 | 用途 |
|-------|-----|------|
| radius-full | 1000px / 100% | 圆形按钮、头像 |
| radius-24 | 24px | 底部导航容器 |
| radius-12 | 12px | 卡片、日期选中态、Header 图标 |
| radius-8 | 8px | Tab 容器、食物图片 |
| radius-6 | 6px | Tab 选中项 |
| radius-4 | 4px | 小图标容器 |
| radius-2 | 2px | Pagination Dots |

### 圆角应用规则

| 组件 | 外圆角 | 内圆角 |
|------|--------|--------|
| 底部导航 | 24px | - |
| 主卡片 | 12px | - |
| Tab 容器 | 8px | 6px (选中项) |
| 食物卡片 | 12px | 8px (图片) |
| 按钮 | 1000px | - |

---

## SwiftUI 映射

```swift
extension CGFloat {
    // Spacing
    static let spacingXL: CGFloat = 20
    static let spacingLG: CGFloat = 16
    static let spacingMD: CGFloat = 12
    static let spacingSM: CGFloat = 10
    static let spacingXS: CGFloat = 8
    static let spacingXXS: CGFloat = 6
    static let spacingTiny: CGFloat = 4
    static let spacingMicro: CGFloat = 2
    
    // Radius
    static let radiusFull: CGFloat = 1000
    static let radiusXL: CGFloat = 24
    static let radiusLG: CGFloat = 12
    static let radiusMD: CGFloat = 8
    static let radiusSM: CGFloat = 6
    static let radiusXS: CGFloat = 4
    static let radiusTiny: CGFloat = 2
}
```

