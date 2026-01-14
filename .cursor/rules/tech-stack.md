# 技术栈与代码规范

## 🚀 技术栈分层策略

### 新项目（强制采用）
| 层级 | 技术 | 说明 |
|------|------|------|
| 框架 | React 18+ / Next.js App Router | Server Components 优先 |
| UI组件 | shadcn/ui + Radix UI | 可定制、无障碍 |
| 样式 | Tailwind CSS v4 | 原子化CSS |
| 动效 | Framer Motion | 声明式动画 |
| 类型 | TypeScript | 全量类型覆盖 |
| 质量 | ESLint + Prettier + Husky | 提交前检查 |

### 现有项目（PM_Screenshot_Tool）
保持 Flask + Native JS 架构，渐进式增强：
- 动效：GSAP + ScrollTrigger
- 轻量交互：Alpine.js（可选）
- 样式：Design Tokens (CSS Variables)

---

## 💫 动效规范

### 时长标准
| 场景 | 时长 | 缓动函数 |
|------|------|----------|
| 微交互（按钮、开关） | 100-200ms | ease-out |
| 组件切换（Modal、Tab） | 200-400ms | ease-in-out |
| 页面过渡 | 400-800ms | cubic-bezier(0.4, 0, 0.2, 1) |

### 动效类型 (Motion Patterns)
| 动效 | 触发方式 | 技术实现 |
|------|----------|----------|
| **Kinetic Typography** | 入场/滚动 | GSAP SplitText, Framer Motion |
| **Morphing Shapes** | 持续/悬停 | SVG morphing, Flubber.js |
| **Magnetic Cursor** | 鼠标移动 | GSAP, Custom JS |
| **Parallax Layers** | 滚动 | ScrollTrigger, Lenis |
| **Scroll-triggered 3D** | 滚动 | Three.js + ScrollTrigger |
| **Liquid Transitions** | 导航 | WebGL, GSAP |

### Framer Motion 最佳实践 (React)
```jsx
const variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
};

<motion.div
    variants={variants}
    initial="hidden"
    animate="visible"
    transition={{ duration: 0.3, ease: "easeOut" }}
/>
```

### GSAP 最佳实践 (原生 JS)
```javascript
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

// 使用 context 管理动画生命周期
const ctx = gsap.context(() => {
    gsap.timeline()
        .to(".hero", { opacity: 1, duration: 0.5 })
        .to(".content", { y: 0, stagger: 0.1 }, "-=0.2");
});
// 清理时调用: ctx.revert();
```

---

## 🔧 调试规范

### 功能性 Bug
1. 生成假设 → 2. 添加日志 → 3. 复现分析 → 4. 修复验证 → 5. 清理日志

### 样式问题
- 检查 CSS 选择器优先级
- 检查内联样式覆盖关系
- 确认 JS 变量初始值与 HTML 默认状态同步

### 常见陷阱
- JS 变量默认值需与 HTML 初始显示状态一致
- 函数可能被后续代码重新定义覆盖
- `opacity` 会影响整个元素（含子元素），`filter` 只影响目标

---

## 🔒 代码备份规则

### 触发备份的情况
- 完成重要功能开发
- 修复关键 Bug
- 对话即将结束
- 用户说"备份"、"保存"、"提交"

### 备份执行步骤
1. **Git 提交** - `git add -A; git commit -m "描述"`
2. **GitHub 推送** - `git push github changes:main`
3. **本地备份** - 运行 `python backup.py`（可选）

### 快捷命令
- 双击 `backup.bat` 可一键完成所有备份
- 备份保存到 `C:\Users\WIN\Desktop\Cursor_Backups\`

---

## 🔧 MCP 工具

| MCP | 用途 |
|-----|------|
| **Playwright** | 浏览器自动化、打开网页、截图 |
| **Context7** | 查询框架/库的最新官方文档 |
| **DeepWiki** | 查询 GitHub 开源项目架构/源码 |
| **Notion** | 操作 Notion 页面、数据库 |
| **Figma** | 获取 Figma 设计信息 |
| **WebSearch** | 搜索网络最新信息（内置） |

---

## Chrome 调试模式（下载会员网站截图）
```bash
# 启动 Chrome 调试模式
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# Playwright 连接
browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
```

