# VitaFlow 阴影与渐变系统

## 阴影系统 (Shadows)

### 卡片阴影

| 名称 | 值 | 用途 |
|------|-----|------|
| shadow-card | `0px 1px 3px rgba(15,23,42,0.05), 0px 4px 12px rgba(15,23,42,0.03)` | 主卡片、Health Score 卡片 |
| shadow-card-sm | `0px 1px 2px rgba(15,23,42,0.04), 0px 2px 6px -2px rgba(15,23,42,0.03)` | 小卡片、指标卡片 |
| shadow-tab | `0px 1px 2px rgba(15,23,42,0.03), 0px 2px 4px rgba(15,23,42,0.02)` | Tab 选中态、日期选中态 |
| shadow-nav | `0px -1px 3px rgba(15,23,42,0.04), 0px -4px 12px rgba(15,23,42,0.03)` | 底部导航 |
| shadow-button | `0px 2px 4px rgba(15,23,42,0.15), 0px 6px 16px rgba(15,23,42,0.1)` | Scan 按钮 |
| shadow-minimal | `0px 0px 2px #e8e8e8` | 食物卡片、轻量卡片 |

### 文字阴影

| 名称 | 值 | 用途 |
|------|-----|------|
| text-shadow-sm | `0px 1px 2px rgba(15,23,42,0.05)` | 标题文字 |
| text-shadow-md | `0px 1px 2px rgba(15,23,42,0.08)` | 强调文字 |

---

## 渐变系统 (Gradients)

### 背景渐变

| 名称 | 值 | 用途 |
|------|-----|------|
| bg-gradient | `linear-gradient(180deg, #F1F5F9 0%, #F8FAFC 100%)` | 页面主背景 |
| nav-gradient | `linear-gradient(0deg, #F2F1F6 17.857%, transparent 100%)` | 底部导航背景 |
| card-gradient | `linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)` | 卡片背景（可选） |

### 进度条渐变

进度条不使用渐变，使用纯色 + 圆角端点

---

## 边框系统 (Borders)

| 名称 | 值 | 用途 |
|------|-----|------|
| border-light | `1px solid rgba(15,23,42,0.01)` | Tab 选中态边框 |
| border-ring | `4.633px solid #830E8B` | Health Score 圆环 |
| border-progress | `3px` | 进度环粗细 |

---

## SwiftUI 映射

```swift
extension View {
    func shadowCard() -> some View {
        self.shadow(color: Color(hex: "0F172A").opacity(0.05), radius: 1.5, x: 0, y: 1)
            .shadow(color: Color(hex: "0F172A").opacity(0.03), radius: 6, x: 0, y: 4)
    }
    
    func shadowCardSM() -> some View {
        self.shadow(color: Color(hex: "0F172A").opacity(0.04), radius: 1, x: 0, y: 1)
            .shadow(color: Color(hex: "0F172A").opacity(0.03), radius: 3, x: 0, y: 2)
    }
    
    func shadowTab() -> some View {
        self.shadow(color: Color(hex: "0F172A").opacity(0.03), radius: 1, x: 0, y: 1)
            .shadow(color: Color(hex: "0F172A").opacity(0.02), radius: 2, x: 0, y: 2)
    }
    
    func shadowNav() -> some View {
        self.shadow(color: Color(hex: "0F172A").opacity(0.04), radius: 1.5, x: 0, y: -1)
            .shadow(color: Color(hex: "0F172A").opacity(0.03), radius: 6, x: 0, y: -4)
    }
    
    func shadowButton() -> some View {
        self.shadow(color: Color(hex: "0F172A").opacity(0.15), radius: 2, x: 0, y: 2)
            .shadow(color: Color(hex: "0F172A").opacity(0.1), radius: 8, x: 0, y: 6)
    }
}

// 背景渐变
struct BackgroundGradient: View {
    var body: some View {
        LinearGradient(
            gradient: Gradient(colors: [Color.slate100, Color.slate50]),
            startPoint: .top,
            endPoint: .bottom
        )
    }
}
```

