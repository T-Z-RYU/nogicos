import React from 'react';
import { FigmaColors, FigmaFonts } from '../styles/figma-tokens';
import circleBg from '../assets/figma/circle-bg.svg';
import circleProgress from '../assets/figma/circle-progress.svg';
import circleDot from '../assets/figma/circle-dot.svg';
import iconArm from '../assets/figma/icon-arm.svg';
import { motion } from "motion/react";

export const CalorieCard: React.FC = () => {
  return (
    <div className="px-[20px] w-full mt-[24px]">
      <div 
        className="w-full bg-white rounded-[12px] p-[16px] flex justify-between relative overflow-hidden"
        style={{ boxShadow: FigmaColors.shadowCard }}
      >
        {/* Left Content */}
        <div className="flex flex-col justify-between h-[125px]">
          <span className="text-[12px]" style={{ color: FigmaColors.secondary, ...FigmaFonts.label }}>
            Calories
          </span>
          
          <div className="flex items-end gap-[4px] mt-auto">
            <motion.span 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-[48px] leading-[1.26] font-medium text-slate-900 tracking-[-1px]"
              style={{ textShadow: FigmaColors.textShadowMd }}
            >
              2,505
            </motion.span>
            <span 
              className="text-[12px] mb-[12px] text-slate-600"
              style={{ ...FigmaFonts.label }}
            >
              kcal
            </span>
          </div>
        </div>

        {/* Right Content - Circle Graph */}
        <div className="relative w-[125px] h-[125px]">
          {/* Background Circle */}
          <img src={circleBg} alt="" className="absolute inset-0 w-full h-full" />
          
          {/* Progress Circle - Rotated/Positioned exactly as Figma */}
          <div className="absolute inset-0 flex items-center justify-center">
             <motion.img 
               src={circleProgress} 
               alt="" 
               className="w-[133px] max-w-none h-[149px] absolute"
               style={{ 
                 top: '-12px', // Fine-tune based on visual check
                 right: '-4px'
               }}
               initial={{ rotate: -90, opacity: 0 }}
               animate={{ rotate: 0, opacity: 1 }}
               transition={{ duration: 1, ease: "easeOut" }}
             />
          </div>

          {/* Dot - Positioned absolutely based on Figma data (101, 19) */}
          <motion.img 
            src={circleDot} 
            alt="" 
            className="absolute w-[6px] h-[6px]"
            style={{ left: '101px', top: '19px' }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.8 }}
          />

          {/* Center Text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-[4px]">
            <img src={iconArm} alt="" className="w-[16px] h-[16px]" />
            <span className="text-[10px] text-slate-600 font-medium tracking-[-0.4px]">Left</span>
          </div>
        </div>
      </div>
    </div>
  );
};
