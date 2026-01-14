import React from 'react';
import { FigmaColors } from '../styles/figma-tokens';
import navHome from '../assets/figma/nav-home.svg';
import navProgress from '../assets/figma/nav-progress.svg';
import navExercise from '../assets/figma/nav-exercise.svg';
import navProfile from '../assets/figma/nav-profile.svg';
import navScan from '../assets/figma/nav-scan.svg';

const NavItem: React.FC<{ icon: string; label: string; active?: boolean }> = ({ icon, label, active }) => (
  <div className={`flex flex-col items-center justify-end h-[56px] w-full pb-[6px] gap-[4px] rounded-[100px] ${active ? 'bg-slate-100' : ''}`}>
    <img src={icon} alt={label} className="w-[24px] h-[24px]" />
    <span className={`text-[11px] font-medium tracking-[-0.2px] ${active ? 'text-slate-900' : 'text-slate-400'}`}>
      {label}
    </span>
  </div>
);

export const BottomNavigation: React.FC = () => {
  return (
    <div className="fixed bottom-0 w-full max-w-[402px] left-1/2 -translate-x-1/2 h-[104px] z-50 pointer-events-none">
      {/* Background Gradient */}
      <div 
        className="absolute bottom-0 w-full h-[125px] pointer-events-none"
        style={{ background: FigmaColors.navGradient }}
      />
      
      {/* Navigation Container */}
      <div className="absolute bottom-[34px] w-full px-[20px] pointer-events-auto">
        <div 
          className="bg-white rounded-[24px] p-[4px] flex items-center justify-between relative h-[72px]"
          style={{ boxShadow: FigmaColors.shadowNav }}
        >
          <div className="flex-1 flex gap-[4px]">
             <NavItem icon={navHome} label="Home" active />
             <NavItem icon={navProgress} label="Progress" />
          </div>
          
          {/* Spacer for Center Button */}
          <div className="w-[80px]" />
          
          <div className="flex-1 flex gap-[4px]">
             <NavItem icon={navExercise} label="Exercise" />
             <NavItem icon={navProfile} label="Profile" />
          </div>

          {/* Floating Scan Button */}
          <div className="absolute left-1/2 top-[-24px] -translate-x-1/2">
             <div 
               className="w-[56px] h-[56px] rounded-full bg-slate-900 flex items-center justify-center shadow-lg"
               style={{ 
                 boxShadow: '0px 6px 16px 0px rgba(15, 23, 42, 0.1), 0px 2px 4px 0px rgba(15, 23, 42, 0.15)'
               }}
             >
                {/* Use the SVG directly or a placeholder icon if the SVG is complex */}
                {/* The downloaded nav-scan.svg likely includes the button background, let's check dimensions. 
                    If nav-scan.svg is 88x88, it might be the whole button + glow. 
                    Let's try using it directly as an image if it looks like the button.
                */}
                <img src={navScan} alt="Scan" className="w-[28px] h-[28px]" style={{ filter: 'brightness(0) invert(1)' }} /> 
                {/* The SVG might be black, inverting to white for the dark button */}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};
