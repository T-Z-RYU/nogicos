import React from 'react';
import { Header } from '../components/Header';
import { CalendarStrip } from '../components/CalendarStrip';
import { CalorieCard } from '../components/CalorieCard';
import { MacroCards } from '../components/MacroCards';
import { FoodList } from '../components/FoodList';
import { BottomNavigation } from '../components/BottomNavigation';
import { FigmaColors } from '../styles/figma-tokens';

export const HomePage: React.FC = () => {
  return (
    <div 
      className="w-full min-h-screen relative overflow-hidden"
      style={{ background: FigmaColors.bgGradient }}
    >
      <div className="max-w-[402px] mx-auto min-h-screen relative pb-[120px]">
        {/* Status Bar Placeholder (22px + padding) */}
        <div className="h-[44px]" /> 
        
        <Header />
        <CalendarStrip />
        <CalorieCard />
        <MacroCards />
        <FoodList />
        <BottomNavigation />
      </div>
    </div>
  );
};
