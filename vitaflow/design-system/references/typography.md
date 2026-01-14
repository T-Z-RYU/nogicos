# VitaFlow 字体系统

## 字体家族

**主字体**: Outfit

- 官网: https://fonts.google.com/specimen/Outfit
- 字重: Regular (400), Medium (500)
- 特点: 现代几何无衬线，适合数字展示

---

## 字体规格

| 名称 | 字号 | 字重 | 行高 | 字间距 | 用途 |
|------|------|------|------|--------|------|
| Display | 48px | Medium | 1.26 | -1px | 大数字 (2,505 kcal) |
| Heading | 28px | Medium | 1.42 | -0.5px | 页面标题 (Vitaflow) |
| Title | 32px | Medium | 32px | -0.32px | Health Score 数字 |
| Large | 18px | Medium | normal | -0.2px | 卡路里数字 (945) |
| Body | 16px | Medium | normal | -0.2px | 指标数值 (7.5) |
| Body-SM | 14px | Medium | normal | -0.4px | Tab 文字、正文 |
| Label | 12px | Medium | normal | -0.2px | 日期数字、食物名称 |
| Label-SM | 12px | Regular | normal | -0.4px | 日期星期、小标签 |
| Caption | 11px | Medium | normal | -0.2px | 底部导航文字 |
| Micro | 10px | Regular | normal | -0.4px | "Calories"、时间戳 |

---

## 字间距规则

| 字间距 | 适用场景 |
|--------|----------|
| -1px (-2.08%) | 大数字 (48px) |
| -0.5px (-1.78%) | 标题 (28px) |
| -0.4px (-3.33%) | 小标签 (10-12px) |
| -0.32px | 中等数字 (32px) |
| -0.2px | 正文、中等文字 (14-18px) |

---

## 颜色搭配

| 文字类型 | 颜色 | Token |
|----------|------|-------|
| 主标题 | `#0F172A` | Slate-900 |
| 食物名称 | `#1E293B` | Slate-800 |
| 描述文字 | `#334155` | Slate-700 |
| 日期文字 | `#475569` | Slate-600 |
| 宏量数值 | `#64748B` | Slate-500 |
| 未选中/标签 | `#94A3B8` | Slate-400 |

---

## SwiftUI 映射

```swift
extension Font {
    static let vitaDisplay = Font.custom("Outfit", size: 48).weight(.medium)
    static let vitaHeading = Font.custom("Outfit", size: 28).weight(.medium)
    static let vitaTitle = Font.custom("Outfit", size: 32).weight(.medium)
    static let vitaLarge = Font.custom("Outfit", size: 18).weight(.medium)
    static let vitaBody = Font.custom("Outfit", size: 16).weight(.medium)
    static let vitaBodySM = Font.custom("Outfit", size: 14).weight(.medium)
    static let vitaLabel = Font.custom("Outfit", size: 12).weight(.medium)
    static let vitaLabelSM = Font.custom("Outfit", size: 12).weight(.regular)
    static let vitaCaption = Font.custom("Outfit", size: 11).weight(.medium)
    static let vitaMicro = Font.custom("Outfit", size: 10).weight(.regular)
}

// 字间距需要通过 .tracking() 修饰符应用
Text("2,505")
    .font(.vitaDisplay)
    .tracking(-1)
```

