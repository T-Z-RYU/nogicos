import { Signal, Wifi, BatteryFull } from 'lucide-react'

export function StatusBar() {
  return (
    <div 
      className="flex items-center justify-between px-6 py-3 bg-surface"
      style={{ height: 'var(--status-bar-height)' }}
      data-testid="status-bar"
    >
      {/* 时间 */}
      <span className="text-base font-semibold text-text-primary">9:41</span>
      
      {/* 状态图标 */}
      <div className="flex items-center gap-1.5">
        <Signal size={16} className="text-text-primary" />
        <Wifi size={16} className="text-text-primary" />
        <BatteryFull size={20} className="text-text-primary" />
      </div>
    </div>
  )
}
