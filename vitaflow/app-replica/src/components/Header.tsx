import React from 'react';
import { FigmaColors, FigmaFonts } from '../styles/figma-tokens';
import iconBell from '../assets/figma/icon-bell.svg';

export const Header: React.FC = () => {
  return (
    <div className="flex justify-between items-center px-[20px] w-full h-[62px] shrink-0">
      <h1 
        style={{
          fontFamily: FigmaFonts.header.family,
          fontWeight: FigmaFonts.header.weight,
          fontSize: FigmaFonts.header.size,
          lineHeight: FigmaFonts.header.lineHeight,
          letterSpacing: FigmaFonts.header.letterSpacing,
          color: FigmaColors.primary,
          textShadow: FigmaColors.textShadowSm
        }}
      >
        Vitaflow
      </h1>
      
      <div 
        className="w-[40px] h-[40px] rounded-[12px] flex items-center justify-center bg-gradient-to-b from-white to-slate-50"
        style={{
          boxShadow: '0px 2px 4px 0px rgba(15, 23, 42, 0.03), 0px 1px 2px 0px rgba(15, 23, 42, 0.04)'
        }}
      >
        <img src={iconBell} alt="Notifications" className="w-[24px] h-[24px]" />
      </div>
    </div>
  );
};
