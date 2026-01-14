'use client'

import { ReactNode } from 'react'
import { motion, HTMLMotionProps } from 'framer-motion'

interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  loading?: boolean
  icon?: ReactNode
  iconPosition?: 'left' | 'right'
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  icon,
  iconPosition = 'left',
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  // VitaFlow 设计系统样式
  const baseStyles = `
    relative inline-flex items-center justify-center gap-2
    transition-all duration-200 overflow-hidden
    disabled:opacity-50 disabled:cursor-not-allowed
  `
  
  // VitaFlow 风格按钮变体
  const variants = {
    primary: `
      bg-[#2B2735] text-white font-medium rounded-[24px]
      shadow-[0px_1px_4.5px_0px_#b9b9b9]
      hover:opacity-90
      active:opacity-80
    `,
    secondary: `
      bg-white text-[#2B2735] font-medium rounded-[24px]
      shadow-[0px_0px_2px_0px_#E8E8E8]
      hover:bg-gray-50
    `,
    ghost: `
      bg-transparent text-[#999] font-medium rounded-[12px]
      hover:bg-white/50
    `,
    outline: `
      bg-transparent border-2 border-[#E8E8E8] text-[#2B2735] font-medium rounded-[24px]
      hover:border-[#2B2735]
    `
  }
  
  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-4 text-base',
    lg: 'px-8 py-4 text-[17px]'
  }
  
  return (
    <motion.button
      className={`
        ${baseStyles}
        ${variants[variant]}
        ${sizes[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
      style={{ fontFamily: 'var(--font-outfit)' }}
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      disabled={disabled || loading}
      {...props}
    >
      {/* 内容 */}
      <span className="relative flex items-center gap-2">
        {loading ? (
          <motion.svg
            className="w-5 h-5"
            viewBox="0 0 24 24"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          >
            <circle
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="3"
              fill="none"
              strokeDasharray="30 60"
              strokeLinecap="round"
            />
          </motion.svg>
        ) : (
          <>
            {icon && iconPosition === 'left' && icon}
            {children}
            {icon && iconPosition === 'right' && icon}
          </>
        )}
      </span>
    </motion.button>
  )
}

// VitaFlow 返回按钮
export function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      onClick={onClick}
      className="w-10 h-10 rounded-[14px] bg-white flex items-center justify-center shadow-[0px_0px_2px_0px_#E8E8E8]"
      style={{ color: '#2B2735' }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path
          d="M12.5 15L7.5 10L12.5 5"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </motion.button>
  )
}

// VitaFlow 跳过按钮
export function SkipButton({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      onClick={onClick}
      className="text-sm font-medium transition-colors"
      style={{ color: '#999', fontFamily: 'var(--font-outfit)' }}
      whileHover={{ x: 3, color: '#2B2735' }}
      whileTap={{ scale: 0.95 }}
    >
      Skip
    </motion.button>
  )
}







