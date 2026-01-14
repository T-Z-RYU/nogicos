/**
 * VitaFlow Design Theme v2.0
 * 从 Figma 设计稿提取 - 2025.12.25
 * 
 * 🎨 配色系统：Slate 蓝灰阶（冷色调，与青绿主色搭配）
 * 
 * TypeScript 版本，可用于：
 * - Tailwind 配置
 * - CSS-in-JS (styled-components, emotion)
 * - Framer Motion 动效
 */

export const vitaflowTheme = {
  /* ============================================
   * 🎨 Slate 灰阶系统 (基于 Tailwind CSS)
   * ============================================ */
  slate: {
    50: '#F8FAFC',
    100: '#F1F5F9',
    200: '#E2E8F0',
    300: '#CBD5E1',
    400: '#94A3B8',
    500: '#64748B',
    600: '#475569',
    700: '#334155',
    800: '#1E293B',
    900: '#0F172A',
    950: '#020617',
  },

  colors: {
    // 背景色
    bg: {
      primary: '#F1F5F9',     // slate-100 页面背景
      card: '#FFFFFF',        // 卡片背景
      input: '#F1F5F9',       // 输入框背景
    },
    
    // 文字色 - 5级层次
    text: {
      primary: '#0F172A',     // slate-900 主文字、品牌名、主数字
      strong: '#1E293B',      // slate-800 食物名
      label: '#334155',       // slate-700 标签文字 Calories/Carbs
      secondary: '#475569',   // slate-600 次要文字
      muted: '#64748B',       // slate-500 数值文字
      tertiary: '#94A3B8',    // slate-400 弱化文字、时间戳
      disabled: '#CBD5E1',    // slate-300 禁用文字
      white: '#FFFFFF',       // 白色文字
    },
    
    // 图标色 - 3级层次
    icon: {
      active: '#0F172A',      // slate-900 选中图标
      default: '#475569',     // slate-600 默认图标
      muted: '#94A3B8',       // slate-400 弱化图标
    },
    
    // 边框色
    border: {
      default: '#E2E8F0',     // slate-200 默认边框
      light: '#F1F5F9',       // slate-100 轻边框
    },
    
    // 品牌色
    brand: {
      primary: '#0F172A',     // slate-900 FAB按钮
    },
    
    // 宏量营养素
    macro: {
      carbs: '#FDCA91',
      carbsLight: '#FEEAD3',
      fat: '#FB6C83',
      fatLight: '#FCA1AF',
      protein: '#07D1EC',
      proteinLight: '#9CEDF7',
    },
    
    // 进度
    progress: {
      ring: '#07D1EC',        // 正常状态
      ringOver: '#FB6C83',    // 超标状态
      bg: '#E2E8F0',          // slate-200 背景
    },
    
    // 状态色
    state: {
      success: '#07D1EC',     // 成功/正常 - 青色
      warning: '#FDCA91',     // 警告 - 橙色
      error: '#FB6C83',       // 错误/超标 - 红色
    },
    
    // 日历
    calendar: {
      active: '#0F172A',      // slate-900 当前日期
      selectedBg: '#07D1EC',  // 选中日期背景
      complete: '#FB6C83',    // 已完成日期
      circle: '#E2E8F0',      // slate-200 日期圆圈
    },
    
    // Health Score
    healthScore: {
      good: '#5DEFA6',
    },
    healthMetric: {
      energy: '#FAE338',
      mind: '#FB6CAC',
      nutrition: '#A588EC',
    },
    
    // Skin & Glow
    skin: {
      tooth: '#FCA84B',
      brain: '#FC4B83',
      feather: '#04DC57',
      yoga: '#4BA9FC',
      sleep: '#C169FC',
    },
    
    // Water 追踪
    water: {
      gradientStart: '#84DFFF',
      gradientEnd: '#42A5F5',
      progressBg: 'rgba(255, 255, 255, 0.24)',
    },
    
    // Steps 追踪
    steps: {
      gradientStart: '#FF8629',
      gradientEnd: '#FF7451',
    },
    
    // 删除状态
    delete: {
      bg: '#F1F5F9',          // slate-100
      bgConfirm: '#FFE0E5',
    },
    
    // 错误状态
    error: {
      red: '#FF1F41',
      bg: '#F1F5F9',          // slate-100
    },
    
    // 遮罩层
    overlay: {
      bg: 'rgba(0, 0, 0, 0.5)',
    },
  },
  
  /* ============================================
   * 📏 间距系统 - 基于 4px/8px 网格
   * ============================================ */
  spacing: {
    0: 0,
    0.5: 2,    // 底部导航图标与文字
    1: 4,      // 图标与文字
    2: 8,      // 基础单位 ⭐
    3: 12,     // 紧凑间距
    4: 16,     // 标准间距 ⭐
    5: 20,     // 舒适间距（页面边距）⭐
    6: 24,     // 分组间距
    8: 32,     // 区块间距
    10: 40,    // 大区块
    12: 48,    // 页面分隔
    
    // 语义化
    page: 20,
    cardGap: 12,
    sectionGap: 16,
  },
  
  /* ============================================
   * 📐 圆角系统 (Border Radius)
   * ============================================ */
  borderRadius: {
    xs: 2,     // Pagination dots
    sm: 4,     // 按钮、标签
    md: 8,     // 图片、小组件
    lg: 12,    // 卡片、主要容器 ⭐
    xl: 24,    // 底部导航
    full: 9999, // FAB、Pill
  },
  
  /* ============================================
   * 🔤 字体系统 (Typography)
   * ============================================ */
  typography: {
    fontFamily: "'Outfit', -apple-system, BlinkMacSystemFont, sans-serif",
    
    // 字号 - 标准梯度
    fontSize: {
      xs: 10,    // 小标签
      sm: 11,    // 底部导航、营养数值
      md: 12,    // 标签、日历文字
      lg: 14,    // 食物名、单位
      xl: 16,    // Status bar
      '2xl': 18, // Macro 数值、食物卡片卡路里
      '3xl': 28, // 品牌名
      '4xl': 48, // Hero 数字（主卡路里）
    },
    
    // 字重 - 3级层次
    fontWeight: {
      regular: 400,   // 标签、单位、辅助文字
      medium: 500,    // 品牌名、主数字、大部分文字
      semibold: 600,  // 食物卡片卡路里、Status bar
    },
    
    letterSpacing: {
      tight: -0.4,
      normal: -0.2,
      title: -0.28,
    },
  },
  
  /* ============================================
   * 🌑 阴影系统 v2.0 - Slate 基色双层阴影
   * ============================================
   * 阴影基色：Slate-900 (#0F172A) → rgba(15, 23, 42, x)
   */
  shadows: {
    // 主卡片阴影 - Summary/Macro/Tracker 等大卡片
    card: '0px 1px 3px 0px rgba(15, 23, 42, 0.05), 0px 4px 12px -2px rgba(15, 23, 42, 0.03)',
    
    // 轻量阴影 - Meal卡片/Tab/日历选择器/Pagination Dots
    cardLight: '0px 1px 2px 0px rgba(15, 23, 42, 0.04), 0px 2px 4px -1px rgba(15, 23, 42, 0.03)',
    
    // 底部导航阴影 - 向上投射
    nav: '0px -1px 3px 0px rgba(15, 23, 42, 0.04), 0px -4px 12px -2px rgba(15, 23, 42, 0.03)',
    
    // FAB 按钮阴影 - 最强立体感
    fab: '0px 2px 4px 0px rgba(15, 23, 42, 0.12), 0px 6px 16px -2px rgba(15, 23, 42, 0.08)',
    
    // 日历选中项阴影
    calendarSelected: '0px 1px 2px 0px rgba(15, 23, 42, 0.04), 0px 2px 4px -1px rgba(15, 23, 42, 0.03)',
    
    // 悬停状态阴影
    cardHover: '0px 2px 6px 0px rgba(15, 23, 42, 0.08), 0px 8px 16px -4px rgba(15, 23, 42, 0.05)',
    
    // 按压状态阴影
    cardPressed: '0px 0px 2px 0px rgba(15, 23, 42, 0.04), 0px 1px 2px -1px rgba(15, 23, 42, 0.02)',
  },
  
  /* ============================================
   * 📱 组件尺寸 (Component Sizes)
   * ============================================ */
  components: {
    nav: {
      height: 64,
      itemWidth: 72.5,
      fabSize: 56,
      iconSize: 24,
    },
    statusBar: {
      height: 62,
    },
    homeIndicator: {
      height: 34,
      width: 144,
    },
    calendar: {
      itemWidth: 48,
      dotSize: 36,
    },
    card: {
      padding: 16,
      paddingLg: 24,
    },
    mealCard: {
      height: 84,
      thumbSize: 64,
    },
    macroCard: {
      width: 112.667,
      height: 112,
    },
    summaryCard: {
      width: 362,
      ringSize: 125,
    },
    icon: {
      xs: 16,
      sm: 22,
      md: 24,
      lg: 27,
    },
    tab: {
      height: 32,
    },
    headerIcon: {
      size: 40,
    },
  },
  
  device: {
    width: 402,
    height: 874,
    safeAreaTop: 62,
    safeAreaBottom: 34,
  },
  
  animation: {
    fast: '150ms ease',
    normal: '250ms ease',
    slow: '350ms ease',
    easeOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeBounce: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
  },
} as const;

// 类型导出
export type VitaflowTheme = typeof vitaflowTheme;
export type VitaflowColors = typeof vitaflowTheme.colors;
export type VitaflowSpacing = typeof vitaflowTheme.spacing;

// 便捷访问函数
export const vf = {
  color: (path: string) => {
    const keys = path.split('.');
    let value: any = vitaflowTheme.colors;
    for (const key of keys) {
      value = value[key];
    }
    return value as string;
  },
  
  spacing: (key: keyof typeof vitaflowTheme.spacing) => 
    `${vitaflowTheme.spacing[key]}px`,
  
  radius: (key: keyof typeof vitaflowTheme.borderRadius) => 
    `${vitaflowTheme.borderRadius[key]}px`,
  
  fontSize: (key: keyof typeof vitaflowTheme.typography.fontSize) => 
    `${vitaflowTheme.typography.fontSize[key]}px`,
  
  // Slate 灰阶快捷访问
  slate: (level: keyof typeof vitaflowTheme.slate) =>
    vitaflowTheme.slate[level],
};

// Tailwind 扩展配置
export const tailwindExtend = {
  colors: {
    // Slate 灰阶
    'vf-slate': vitaflowTheme.slate,
    
    // 语义化颜色
    'vf-bg': vitaflowTheme.colors.bg,
    'vf-text': vitaflowTheme.colors.text,
    'vf-icon': vitaflowTheme.colors.icon,
    'vf-border': vitaflowTheme.colors.border,
    'vf-brand': vitaflowTheme.colors.brand,
    'vf-macro': {
      carbs: vitaflowTheme.colors.macro.carbs,
      'carbs-light': vitaflowTheme.colors.macro.carbsLight,
      fat: vitaflowTheme.colors.macro.fat,
      'fat-light': vitaflowTheme.colors.macro.fatLight,
      protein: vitaflowTheme.colors.macro.protein,
      'protein-light': vitaflowTheme.colors.macro.proteinLight,
    },
    'vf-state': vitaflowTheme.colors.state,
  },
  fontFamily: {
    outfit: ['Outfit', 'sans-serif'],
  },
  fontSize: {
    'vf-xs': '10px',
    'vf-sm': '11px',
    'vf-md': '12px',
    'vf-lg': '14px',
    'vf-xl': '16px',
    'vf-2xl': '18px',
    'vf-3xl': '28px',
    'vf-4xl': '48px',
  },
  borderRadius: {
    'vf-xs': '2px',
    'vf-sm': '4px',
    'vf-md': '8px',
    'vf-lg': '12px',
    'vf-xl': '24px',
  },
  boxShadow: {
    'vf-card': vitaflowTheme.shadows.card,
    'vf-card-light': vitaflowTheme.shadows.cardLight,
    'vf-nav': vitaflowTheme.shadows.nav,
    'vf-fab': vitaflowTheme.shadows.fab,
    'vf-calendar-selected': vitaflowTheme.shadows.calendarSelected,
    'vf-card-hover': vitaflowTheme.shadows.cardHover,
    'vf-card-pressed': vitaflowTheme.shadows.cardPressed,
  },
};

/* ============================================
 * 📋 设计系统速查表
 * ============================================
 * 
 * 灰阶层级（从深到浅）：
 * - slate-900 #0F172A → 主文字、品牌名、选中图标
 * - slate-800 #1E293B → 食物名
 * - slate-700 #334155 → 标签文字
 * - slate-600 #475569 → 次要文字、默认图标
 * - slate-500 #64748B → 数值文字
 * - slate-400 #94A3B8 → 弱化文字、未选中图标
 * - slate-200 #E2E8F0 → 边框、进度条背景
 * - slate-100 #F1F5F9 → 页面背景
 * 
 * 字号梯度：10 → 11 → 12 → 14 → 16 → 18 → 28 → 48
 * 字重层次：Regular 400 | Medium 500 | SemiBold 600
 * 间距梯度：2 → 4 → 8 → 12 → 16 → 20 → 24 → 32
 * 圆角梯度：2 → 4 → 8 → 12 → 24 → full
 */
