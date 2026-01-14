'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface PhoneFrameProps {
  children: ReactNode
}

export function PhoneFrame({ children }: PhoneFrameProps) {
  return (
    <div className="relative mx-auto">
      {/* 外部光晕效果 - VitaFlow 风格 */}
      <div className="absolute -inset-4 rounded-[60px] bg-gradient-to-br from-gray-400/10 via-gray-300/5 to-gray-400/10 blur-2xl opacity-60" />
      
      {/* 手机外框 */}
      <div className="relative bg-black rounded-[50px] p-3 shadow-2xl">
        {/* 内部边框（模拟金属质感） */}
        <div className="absolute inset-[3px] rounded-[47px] bg-gradient-to-b from-gray-700 via-gray-800 to-gray-900 opacity-50" />
        
        {/* 手机屏幕区域 - VitaFlow 背景色 */}
        <div className="relative rounded-[40px] overflow-hidden" style={{ width: '375px', height: '812px', background: '#F2F1F6' }}>
          {/* 状态栏 */}
          <StatusBar />
          
          {/* 内容区域 */}
          <div className="relative h-[calc(100%-94px)] overflow-hidden">
            {children}
          </div>
          
          {/* Home Indicator */}
          <HomeIndicator />
        </div>
      </div>
    </div>
  )
}

function StatusBar() {
  return (
    <div className="h-[62px] px-6 flex items-end justify-between pb-2" style={{ background: '#F2F1F6' }}>
      {/* 时间 - VitaFlow 样式 */}
      <span className="text-[15px] font-semibold" style={{ color: '#2B2735', fontFamily: 'var(--font-outfit)' }}>9:41</span>
      
      {/* 刘海（灵动岛） */}
      <div className="absolute left-1/2 -translate-x-1/2 top-3">
        <div className="w-[126px] h-[37px] bg-black rounded-full" />
      </div>
      
      {/* 信号、WiFi、电池 */}
      <div className="flex items-center gap-1.5">
        {/* 信号 */}
        <svg width="18" height="12" viewBox="0 0 18 12" fill="none">
          <rect x="0" y="6" width="3" height="6" rx="1" fill="#2B2735" />
          <rect x="5" y="4" width="3" height="8" rx="1" fill="#2B2735" />
          <rect x="10" y="2" width="3" height="10" rx="1" fill="#2B2735" />
          <rect x="15" y="0" width="3" height="12" rx="1" fill="#2B2735" />
        </svg>
        {/* WiFi */}
        <svg width="17" height="12" viewBox="0 0 17 12" fill="none">
          <path d="M8.5 2.5C11.5 2.5 14 4 15.5 6L14 7.5C12.8 5.8 10.8 4.5 8.5 4.5C6.2 4.5 4.2 5.8 3 7.5L1.5 6C3 4 5.5 2.5 8.5 2.5Z" fill="#2B2735" />
          <path d="M8.5 6C10.2 6 11.7 6.8 12.7 8L11.2 9.5C10.5 8.5 9.6 8 8.5 8C7.4 8 6.5 8.5 5.8 9.5L4.3 8C5.3 6.8 6.8 6 8.5 6Z" fill="#2B2735" />
          <circle cx="8.5" cy="11" r="1.5" fill="#2B2735" />
        </svg>
        {/* 电池 */}
        <div className="flex items-center">
          <div className="w-[25px] h-[12px] border-[1.5px] rounded-[3px] p-[1px]" style={{ borderColor: '#2B2735' }}>
            <div className="w-full h-full rounded-[1px]" style={{ background: '#2B2735' }} />
          </div>
          <div className="w-[2px] h-[5px] rounded-r-full ml-[1px]" style={{ background: '#2B2735' }} />
        </div>
      </div>
    </div>
  )
}

function HomeIndicator() {
  return (
    <div className="h-[34px] flex items-center justify-center" style={{ background: '#F2F1F6' }}>
      <motion.div 
        className="w-[134px] h-[5px] rounded-full"
        style={{ background: '#2B2735' }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      />
    </div>
  )
}







