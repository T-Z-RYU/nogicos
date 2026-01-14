# VitaFlow Onboarding Demo - 工作交接文档

## 📍 项目位置
```
c:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\frontend\src\app\onboarding-demo\
```

## 🚀 启动方式
```bash
cd "c:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\frontend"
npm run dev
# 访问 http://localhost:3001/onboarding-demo
```

## ✅ 已完成工作

### 1. VitaFlow 设计风格复刻
- **配色**: 浅灰紫背景 `#F2F1F6`, 深色主色 `#2B2735`, 次要色 `#999999`
- **字体**: Outfit (已在 `layout.tsx` 添加)
- **圆角**: 按钮 24px, 卡片 16px, 返回按钮 14px
- **阴影**: 卡片 `0px 0px 2px 0px #E8E8E8`

### 2. 已更新的组件
| 组件 | 路径 | 说明 |
|------|------|------|
| Button | `components/ui/Button.tsx` | 深色主按钮, 白色次按钮, ghost, outline |
| OptionCard | `components/ui/OptionCard.tsx` | 单选/多选卡片 |
| ProgressBar | `components/ui/ProgressBar.tsx` | 3px 细线进度条 |
| PhoneFrame | `components/ui/PhoneFrame.tsx` | 手机外框 + 状态栏 |
| NumberSlider | `components/ui/NumberPicker.tsx` | 数字滑块 |

### 3. 已更新的屏幕 (共 39 页)
- `LaunchScreen.tsx` - 启动页
- `WelcomeScreen.tsx` - 欢迎页 (AI 扫描动画)
- `QuestionSingleScreen.tsx` - 单选问题
- `QuestionMultiScreen.tsx` - 多选问题
- `NumberInputScreen.tsx` - 数字输入
- `TextInputScreen.tsx` - 文本输入
- `TransitionScreen.tsx` - 过渡页
- `LoadingScreen.tsx` - 加载动画 (已修复图标时序)
- `ResultScreen.tsx` - 结果展示
- `PaywallScreen.tsx` - 付费墙

### 4. 全局样式
- `globals.css` - 添加 VitaFlow CSS 变量和 `.scrollbar-hide` 类
- `layout.tsx` - 添加 Outfit 字体

## 🔧 待完成任务

### 高优先级
1. **缺少的页面**:
   - 减重速度选择页 (Weekly Loss Rate: 0.5kg/1kg/1.5kg)
   - Referral Code 输入页
   - 追踪权限 (ATT) 请求页

2. **页面优化**:
   - 付费墙后的页面过多 (6页 → 建议精简到 2-3页)
   - 合并两个"庆祝"屏幕

3. **流程调整**:
   - "伏笔问题" 应移到 Loading 页面之前

### 可选优化
- 添加更多过渡动画
- 优化数字选择器交互
- 添加键盘快捷键提示

## 📁 关键文件

### 配置文件
```
data/screens-config.ts  # 所有 39 页的配置
```

### 状态管理
```
store/onboarding-store.ts  # Zustand store (currentStep, userData, results)
```

### 工具函数
```
utils/personalize.ts  # 个性化文本替换 {name} → 用户名
```

## 🎨 设计参考

### VitaFlow 设计系统 CSS 变量
```css
:root {
  --vitaflow-bg: #F2F1F6;
  --vitaflow-primary: #2B2735;
  --vitaflow-secondary: #999999;
  --vitaflow-card: #FFFFFF;
  --vitaflow-shadow: 0px 0px 2px 0px #E8E8E8;
  --font-outfit: 'Outfit', sans-serif;
}
```

### 常用样式
```tsx
// 页面容器
<div style={{ background: '#F2F1F6', fontFamily: 'var(--font-outfit)' }}>

// 标题
<h1 className="text-[24px] font-semibold tracking-[-0.5px]" style={{ color: '#2B2735' }}>

// 副标题
<p className="text-[14px]" style={{ color: '#999999' }}>

// 卡片
<div className="rounded-[16px] bg-white" style={{ boxShadow: '0px 0px 2px 0px #E8E8E8' }}>
```

## 🔗 相关资源

- Figma 设计稿: VitaFlow (需要用 Figma MCP 查看)
- Git 分支: `changes`
- 最新提交: `feat(onboarding-demo): 完成 VitaFlow 设计风格复刻`

## 📝 注意事项

1. 开发服务器端口是 **3001** (不是 3000)
2. 如果页面加载不出来，尝试 `Ctrl+Shift+R` 强制刷新
3. 可以用键盘 `← →` 切换页面，`R` 重置，`Space` 下一页

---
*最后更新: 2024-12-23*
