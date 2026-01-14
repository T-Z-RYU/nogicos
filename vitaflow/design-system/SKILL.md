---
name: vitaflow-design-system
description: VitaFlow iOS App 的完整设计系统规范。包含颜色体系(Slate)、字体系统(Outfit)、间距、圆角、阴影、渐变等所有 Design Token。当进行 VitaFlow 设计审查、精修、组件化、或开发交付时使用此技能。任何涉及 VitaFlow UI 样式的工作都应先加载此技能以确保设计一致性。
---

# VitaFlow Design System

## 快速参考

### 禁止使用的颜色
- `#999` / `#999999` → 改用 `#94A3B8` (Slate-400)
- `black` → 改用 `#0F172A` (Slate-900) 或 `#1E293B` (Slate-800)
- `#e6e6e6` / `#e8e8e8` → 改用 `#E2E8F0` (Slate-200)

### 颜色使用规则
| 用途 | Token | 色值 |
|------|-------|------|
| 主标题/强调 | Slate-900 | `#0F172A` |
| 食物名称 | Slate-800 | `#1E293B` |
| 描述文字 | Slate-700 | `#334155` |
| 次要文字 | Slate-600 | `#475569` |
| 辅助数值 | Slate-500 | `#64748B` |
| 未选中/禁用 | Slate-400 | `#94A3B8` |
| 分割线 | Slate-200 | `#E2E8F0` |
| 背景/容器 | Slate-100 | `#F1F5F9` |
| 卡片背景 | White | `#FFFFFF` |

---

## 详细规范

完整的设计规范请查看：
- **颜色系统**: [references/colors.md](references/colors.md)
- **字体系统**: [references/typography.md](references/typography.md)
- **间距与圆角**: [references/spacing.md](references/spacing.md)
- **阴影与渐变**: [references/effects.md](references/effects.md)
- **组件样式**: [references/components.md](references/components.md)

---

## 设计审查清单

检查页面时，按以下顺序扫描：

1. **颜色检查**
   - 搜索 `#999` → 应为 `#94A3B8`
   - 搜索 `black` → 应为 Slate 色值
   - 搜索非 Slate 体系的灰色

2. **字体检查**
   - 字体是否为 Outfit
   - 字号是否在规范内 (10/11/12/14/16/18/28/32/48px)
   - 字重是否正确 (400/500)

3. **间距检查**
   - 页面边距是否为 20px
   - 组件间距是否在规范内

4. **圆角检查**
   - 卡片圆角是否为 12px
   - 按钮/Tab 圆角是否一致

5. **阴影检查**
   - 是否使用了规范内的阴影值

