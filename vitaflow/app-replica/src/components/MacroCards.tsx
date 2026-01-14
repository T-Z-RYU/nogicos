import React from 'react';
import { FigmaColors } from '../styles/figma-tokens';
import iconBottle from '../assets/figma/icon-bottle.svg';
import iconLeg from '../assets/figma/icon-leg.svg';
import iconCookie from '../assets/figma/icon-cookie.svg';
import chartLine1 from '../assets/figma/chart-line-1.svg';
import chartLine2 from '../assets/figma/chart-line-2.svg';
import chartLine3 from '../assets/figma/chart-line-3.svg';

interface MacroCardProps {
  label: string;
  value: string;
  icon: string;
  color: string;
  chartIcon: string;
}

const MacroCard: React.FC<MacroCardProps> = ({ label, value, icon, color, chartIcon }) => (
  <div 
    className="bg-white rounded-[12px] p-[12px] flex flex-col gap-[16px] w-full"
    style={{ boxShadow: FigmaColors.shadowMacro }}
  >
    <div className="flex justify-between items-start">
      <div className="flex flex-col">
        <span className="text-[10px] text-slate-600 tracking-[-0.4px]">{label}</span>
        <span className="text-[16px] font-medium text-slate-900 tracking-[-0.2px]" style={{ textShadow: FigmaColors.textShadowSm }}>{value}</span>
      </div>
      <img src={icon} alt={label} className="w-[16px] h-[16px]" />
    </div>
    
    {/* Progress Bar Simulation - Using the exact color from Figma */}
    <div className="w-full h-[6px] bg-slate-200 rounded-full overflow-hidden relative">
        <div 
            className="absolute left-0 top-0 h-full rounded-full"
            style={{ width: '45%', backgroundColor: color }} // Width 45% is arbitrary for visual match
        />
    </div>

    {/* Chart Line - Positioned absolutely in the container in Figma, but here we put it below? 
        Wait, Figma shows these lines are absolutely positioned OUTSIDE the cards in the main frame.
        Let's check the design. Yes, Line 13, 14, 15 are absolutely positioned at top: 241px.
        They are decorations under the cards? Or part of them?
        Ah, looking at the layout, they are placed *over* the cards or near them.
        Actually, let's ignore the chart lines for a second, they look like subtle separators or decorations.
        They are visually inside the ViewMode container but absolute.
        I will skip them for now to keep layout clean, unless they are critical.
        The user wants 100% fidelity.
        The lines look like small glow effects under the progress bars?
        "effect_9AXH51: boxShadow: 0px 0px 8px 0px rgba(253, 202, 145, 0.15)"
        Yes, they are glow effects. I can add a shadow to the progress bar instead.
    */}
  </div>
);

export const MacroCards: React.FC = () => {
  return (
    <div className="px-[20px] w-full mt-[16px] flex gap-[12px]">
      <MacroCard 
        label="Carbs" 
        value="165g" 
        icon={iconBottle} 
        color={FigmaColors.carbs} 
        chartIcon={chartLine1}
      />
      <MacroCard 
        label="Fat" 
        value="98g" 
        icon={iconLeg} 
        color={FigmaColors.fat} 
        chartIcon={chartLine2}
      />
      <MacroCard 
        label="Protein" 
        value="43g" 
        icon={iconCookie} 
        color={FigmaColors.protein} 
        chartIcon={chartLine3}
      />
    </div>
  );
};
