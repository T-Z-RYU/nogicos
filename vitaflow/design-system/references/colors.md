# VitaFlow 颜色系统

## Slate 灰阶体系（主色板）

| Token | 色值 | 用途 |
|-------|------|------|
| Slate-900 | `#0F172A` | 主标题、选中态文字、强调数字 |
| Slate-800 | `#1E293B` | 食物名称、次级标题 |
| Slate-700 | `#334155` | 描述文字、Health Score 标签 |
| Slate-600 | `#475569` | 日历日期、次要文字 |
| Slate-500 | `#64748B` | 宏量元素数值 (54g, 39g, 60g) |
| Slate-400 | `#94A3B8` | 未选中态、禁用态、"Calories" 标签、未来日期 |
| Slate-300 | `#CBD5E1` | 备用（暂未使用） |
| Slate-200 | `#E2E8F0` | 分割线、Pagination Dots |
| Slate-100 | `#F1F5F9` | 背景、Tab 容器背景 |
| Slate-50 | `#F8FAFC` | 渐变终点 |

---

## 功能色

### 卡路里进度
| Token | 色值 | 用途 |
|-------|------|------|
| Teal | `#61E0BD` | 卡路里进度环主色 |
| Teal-Light | `rgba(97,224,189,0.15)` | 进度环背景 |

### 宏量元素
| 宏量 | 主色 | 图标色 | 背景色 |
|------|------|--------|--------|
| Carbs | `#FDCA91` | `#9CEDF7` | `rgba(156,237,247,0.15)` |
| Fat | `#FB7D91` | `#FCA1AF` | `rgba(252,161,175,0.15)` |
| Protein | `#07D1EC` | `#FEDAD3` | `rgba(254,234,211,0.15)` |

### 状态色
| Token | 色值 | 用途 |
|-------|------|------|
| Error | `#EF4444` | Badge 红点、错误状态 |
| Warning | `#FAE338` | Energy 黄色 |
| Success | `#61E0BD` | 成功状态 |

### Health Score 指标色
| 指标 | 色值 | 背景色 |
|------|------|--------|
| Energy | `#FAE338` | `rgba(250,227,56,0.15)` |
| Mental | `#FB6CAC` | `rgba(251,108,172,0.15)` |
| Diet | `#A588EC` | `rgba(165,136,236,0.15)` |
| Health Ring | `#830E8B` | - |

---

## 禁止使用的颜色

以下颜色**绝对禁止**在 VitaFlow 中使用：

| 禁止 | 替代方案 |
|------|----------|
| `#999` / `#999999` | `#94A3B8` (Slate-400) |
| `black` / `#000000` | `#0F172A` (Slate-900) |
| `#e6e6e6` | `#E2E8F0` (Slate-200) |
| `#e8e8e8` | `#E2E8F0` (Slate-200) |
| `#333` / `#333333` | `#334155` (Slate-700) |
| `#666` / `#666666` | `#64748B` (Slate-500) |

---

## SwiftUI 映射

```swift
extension Color {
    static let slate900 = Color(hex: "0F172A")
    static let slate800 = Color(hex: "1E293B")
    static let slate700 = Color(hex: "334155")
    static let slate600 = Color(hex: "475569")
    static let slate500 = Color(hex: "64748B")
    static let slate400 = Color(hex: "94A3B8")
    static let slate200 = Color(hex: "E2E8F0")
    static let slate100 = Color(hex: "F1F5F9")
    static let slate50 = Color(hex: "F8FAFC")
    
    static let teal = Color(hex: "61E0BD")
    static let carbsIcon = Color(hex: "9CEDF7")
    static let fatIcon = Color(hex: "FCA1AF")
    static let proteinIcon = Color(hex: "FEDAD3")
}
```

