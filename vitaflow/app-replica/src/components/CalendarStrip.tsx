import React from 'react';
import { FigmaColors } from '../styles/figma-tokens';
import ringBase from '../assets/figma/ring-base.svg';
import ringActive from '../assets/figma/ring-active.svg';

const days = [
  { day: 'Thu', date: '27', active: false },
  { day: 'Fri', date: '28', active: false },
  { day: 'Sat', date: '29', active: false },
  { day: 'Sun', date: '30', active: false },
  { day: 'Mon', date: '31', active: true },
  { day: 'Tue', date: '1', active: false },
  { day: 'Wed', date: '2', active: false },
];

export const CalendarStrip: React.FC = () => {
  return (
    <div className="flex justify-between items-center px-[20px] w-full mt-[20px]">
      {days.map((item, index) => (
        <div 
          key={index}
          className={`flex flex-col items-center gap-[8px] w-[48px] p-[4px] rounded-[12px] ${item.active ? 'bg-gradient-to-b from-white to-slate-50 shadow-sm' : ''}`}
          style={item.active ? {
            boxShadow: '0px 2px 4px 0px rgba(15, 23, 42, 0.02), 0px 1px 2px 0px rgba(15, 23, 42, 0.03)'
          } : {}}
        >
          <span 
            className="text-[12px] font-medium"
            style={{ 
              color: item.active ? FigmaColors.primary : FigmaColors.secondary,
              fontFamily: 'Outfit',
              letterSpacing: '-0.4px'
            }}
          >
            {item.day}
          </span>
          
          <div className="relative w-[36px] h-[36px] flex items-center justify-center">
            {/* Base Ring */}
            <img src={ringBase} className="absolute inset-0 w-full h-full" alt="" />
            
            {/* Active Ring Glow - only if active */}
            {item.active && (
              <img 
                src={ringActive} 
                className="absolute w-[54px] max-w-none h-[60px] top-[-12px] left-[-9px]" 
                alt="" 
                style={{ pointerEvents: 'none' }}
              />
            )}
            
            <span 
              className="relative z-10 text-[12px] font-medium"
              style={{ 
                color: item.active ? FigmaColors.primary : FigmaColors.secondary,
                fontFamily: 'Outfit',
                letterSpacing: '-0.2px'
              }}
            >
              {item.date}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
