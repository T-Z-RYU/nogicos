'use client'

import { motion } from 'framer-motion'
import * as LucideIcons from 'lucide-react'
import { LucideIcon } from 'lucide-react'

interface OptionCardProps {
  icon: string
  title: string
  subtitle?: string
  selected?: boolean
  onClick?: () => void
  index?: number
}

// 动态获取 Lucide 图标
function getIcon(name: string): LucideIcon {
  const icons = LucideIcons as Record<string, LucideIcon>
  return icons[name] || LucideIcons.Circle
}

export function OptionCard({ 
  icon, 
  title, 
  subtitle, 
  selected = false, 
  onClick,
  index = 0
}: OptionCardProps) {
  const Icon = getIcon(icon)
  
  return (
    <motion.button
      onClick={onClick}
      className="relative w-full p-4 rounded-[16px] text-left transition-all duration-200"
      style={{
        background: '#FFFFFF',
        boxShadow: selected 
          ? '0px 0px 0px 2px #2B2735, 0px 0px 8px 0px rgba(43, 39, 53, 0.15)' 
          : '0px 0px 2px 0px #E8E8E8',
        fontFamily: 'var(--font-outfit)'
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.4,
        delay: index * 0.08,
        ease: [0.25, 0.46, 0.45, 0.94]
      }}
      whileHover={{ scale: 1.01, boxShadow: '0px 0px 4px 0px #E8E8E8' }}
      whileTap={{ scale: 0.99 }}
    >
      <div className="relative flex items-center gap-4">
        {/* 图标容器 - VitaFlow 样式 */}
        <motion.div 
          className="flex-shrink-0 w-12 h-12 rounded-[12px] flex items-center justify-center"
          style={{
            background: selected ? '#2B2735' : '#F2F1F6'
          }}
          animate={{
            scale: selected ? [1, 1.05, 1] : 1
          }}
          transition={{ duration: 0.3 }}
        >
          <Icon 
            className="w-6 h-6"
            style={{ color: selected ? '#FFFFFF' : '#2B2735' }}
            strokeWidth={2}
          />
        </motion.div>
        
        {/* 文本 */}
        <div className="flex-1 min-w-0">
          <p 
            className="font-medium text-[15px]"
            style={{ color: '#2B2735' }}
          >
            {title}
          </p>
          {subtitle && (
            <p 
              className="text-[13px] mt-0.5"
              style={{ color: '#999999' }}
            >
              {subtitle}
            </p>
          )}
        </div>
        
        {/* 选中指示器 - VitaFlow 样式 */}
        <motion.div 
          className="flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center"
          style={{
            borderColor: selected ? '#2B2735' : '#E8E8E8',
            background: selected ? '#2B2735' : 'transparent'
          }}
        >
          {selected && (
            <motion.svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.2, delay: 0.1 }}
            >
              <path
                d="M2 6L5 9L10 3"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </motion.svg>
          )}
        </motion.div>
      </div>
    </motion.button>
  )
}

// VitaFlow 多选版本
export function OptionCardMulti({ 
  icon, 
  title, 
  subtitle, 
  selected = false, 
  onClick,
  index = 0
}: OptionCardProps) {
  const Icon = getIcon(icon)
  
  return (
    <motion.button
      onClick={onClick}
      className="relative w-full p-4 rounded-[16px] text-left transition-all duration-200"
      style={{
        background: '#FFFFFF',
        boxShadow: selected 
          ? '0px 0px 0px 2px #2B2735, 0px 0px 8px 0px rgba(43, 39, 53, 0.15)' 
          : '0px 0px 2px 0px #E8E8E8',
        fontFamily: 'var(--font-outfit)'
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.4,
        delay: index * 0.06,
        ease: [0.25, 0.46, 0.45, 0.94]
      }}
      whileHover={{ scale: 1.01, boxShadow: '0px 0px 4px 0px #E8E8E8' }}
      whileTap={{ scale: 0.99 }}
    >
      <div className="relative flex items-center gap-3">
        {/* 复选框 - VitaFlow 样式 */}
        <motion.div 
          className="flex-shrink-0 w-6 h-6 rounded-[8px] border-2 flex items-center justify-center"
          style={{
            borderColor: selected ? '#2B2735' : '#E8E8E8',
            background: selected ? '#2B2735' : '#FFFFFF'
          }}
        >
          {selected && (
            <motion.svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
            >
              <path
                d="M2 6L5 9L10 3"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </motion.svg>
          )}
        </motion.div>
        
        {/* 图标 */}
        <div 
          className="flex-shrink-0 w-10 h-10 rounded-[12px] flex items-center justify-center"
          style={{
            background: selected ? 'rgba(43, 39, 53, 0.1)' : '#F2F1F6'
          }}
        >
          <Icon 
            className="w-5 h-5"
            style={{ color: selected ? '#2B2735' : '#999999' }}
            strokeWidth={2}
          />
        </div>
        
        {/* 文本 */}
        <div className="flex-1 min-w-0">
          <p 
            className="font-medium text-[15px]"
            style={{ color: '#2B2735' }}
          >
            {title}
          </p>
          {subtitle && (
            <p 
              className="text-[12px] mt-0.5"
              style={{ color: '#999999' }}
            >
              {subtitle}
            </p>
          )}
        </div>
      </div>
    </motion.button>
  )
}







