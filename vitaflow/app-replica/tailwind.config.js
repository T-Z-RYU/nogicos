/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // === Figma Design Tokens (from Framelink globalVars.styles) ===
        
        // Slate palette (主要文字/背景色)
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
        },
        
        // 主色 - Teal/Cyan
        primary: {
          DEFAULT: '#61E0BD',
          light: '#5EDCEC',
          cyan: '#07D1EC',
          glow: 'rgba(7, 209, 236, 0.1)',
        },
        
        // 营养素颜色
        macro: {
          carbs: '#FDCA91',
          carbsLight: '#FEEAD3',
          fat: '#FB7D91',
          fatLight: '#FCBDC7',
          protein: '#5EDCEC',
          proteinLight: '#B2EFF7',
        },
        
        // 进度环颜色
        ring: {
          progress: 'rgba(251, 108, 131, 0.25)',
          today: 'rgba(97, 224, 189, 0.25)',
          selected: '#61E0BD',
          default: '#E2E8F0',
          future: 'rgba(226, 232, 240, 0.5)',
        },
      },
      
      fontFamily: {
        // Figma 使用 Outfit 字体
        sans: ['Outfit', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      
      fontSize: {
        // Figma 字体大小
        '2xs': ['10px', { lineHeight: '1.26', letterSpacing: '-0.04em' }],
        'xs': ['11px', { lineHeight: '1.26', letterSpacing: '-0.018em' }],
        'sm': ['12px', { lineHeight: '1.26', letterSpacing: '-0.017em' }],
        'base': ['14px', { lineHeight: '1.26', letterSpacing: '-0.014em' }],
        'lg': ['16px', { lineHeight: '1.26', letterSpacing: '-0.0125em' }],
        'xl': ['18px', { lineHeight: '1.26', letterSpacing: '-0.011em' }],
        '2xl': ['28px', { lineHeight: '1.43', letterSpacing: '-0.018em' }],
        '3xl': ['48px', { lineHeight: '1.26', letterSpacing: '-0.02em' }],
      },
      
      spacing: {
        // Figma 间距
        '4.5': '18px',
        '5.5': '22px',
        '15': '60px',
      },
      
      borderRadius: {
        // Figma 圆角
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px',
        '4xl': '60px',
        'full': '9999px',
      },
      
      boxShadow: {
        // Figma 阴影 (from effect_xxx)
        'card': '0px 4px 12px 0px rgba(15, 23, 42, 0.03), 0px 1px 3px 0px rgba(15, 23, 42, 0.05)',
        'card-sm': '0px 2px 6px -2px rgba(15, 23, 42, 0.03), 0px 1px 2px 0px rgba(15, 23, 42, 0.04)',
        'card-xs': '0px 2px 4px 0px rgba(15, 23, 42, 0.02), 0px 1px 2px 0px rgba(15, 23, 42, 0.03)',
        'nav': '0px -4px 12px 0px rgba(15, 23, 42, 0.03), 0px -1px 3px 0px rgba(15, 23, 42, 0.04)',
        'glow-cyan': '0px 0px 12px 0px rgba(7, 209, 236, 0.1)',
        'glow-carbs': '0px 0px 8px 0px rgba(253, 202, 145, 0.15)',
        'glow-fat': '0px 0px 8px 0px rgba(251, 126, 145, 0.15)',
        'glow-protein': '0px 0px 8px 0px rgba(94, 219, 236, 0.15)',
      },
      
      backgroundImage: {
        // Figma 渐变 (from fill_xxx)
        'page': 'linear-gradient(180deg, #F1F5F9 0%, #F8FAFC 100%)',
        'card': 'linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)',
        'nav-fade': 'linear-gradient(0deg, #F1F5F9 18%, transparent 100%)',
      },
      
      width: {
        'device': '402px',
      },
      
      height: {
        'device': '874px',
        'status-bar': '62px',
        'bottom-nav': '98px',
      },
    },
  },
  plugins: [],
}
