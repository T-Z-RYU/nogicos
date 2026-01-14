import React from 'react';
import { FigmaColors } from '../styles/figma-tokens';
import foodChicken1 from '../assets/figma/food-chicken-1.png';

const foodSalad = foodChicken1;
const foodChicken2 = foodChicken1;
import iconCookie from '../assets/figma/icon-cookie.svg';
import iconBottle from '../assets/figma/icon-bottle.svg';
import iconLeg from '../assets/figma/icon-leg.svg';

interface FoodItemProps {
  name: string;
  image: string;
  macros: {
    carbs: string;
    fat: string;
    protein: string;
  };
  calories: string;
}

const FoodItem: React.FC<FoodItemProps> = ({ name, image, macros, calories }) => (
  <div 
    className="bg-white rounded-[12px] p-[12px] flex items-center justify-between w-full h-[88px]"
    style={{ boxShadow: FigmaColors.shadowMacro }}
  >
    <div className="flex items-center gap-[16px]">
      <img src={image} alt={name} className="w-[64px] h-[64px] rounded-[8px] object-cover border border-slate-50" />
      <div className="flex flex-col gap-[8px]">
        <span className="text-[14px] font-medium text-slate-800 tracking-[-0.2px]">{name}</span>
        <div className="flex items-center gap-[12px]">
          <div className="flex items-center gap-[4px]">
             <img src={iconCookie} className="w-[12px] h-[12px] opacity-70" style={{ filter: 'brightness(0) saturate(100%) invert(89%) sepia(21%) saturate(542%) hue-rotate(178deg) brightness(98%) contrast(92%)' }} alt="c" /> 
             {/* Note: Icon colors in Figma are tinted. Using CSS filter or just the raw SVG if it has color. 
                 The raw SVGs I downloaded might be monochrome if they were masks. 
                 Let's check. They seemed to have fills.
                 Actually, for this list, let's just use text for simplicity or the icons as is.
             */}
             <span className="text-[11px] text-slate-500 font-medium">{macros.carbs}</span>
          </div>
          <div className="flex items-center gap-[4px]">
             <img src={iconBottle} className="w-[12px] h-[12px] opacity-70" alt="f" />
             <span className="text-[11px] text-slate-500 font-medium">{macros.fat}</span>
          </div>
          <div className="flex items-center gap-[4px]">
             <img src={iconLeg} className="w-[12px] h-[12px] opacity-70" alt="p" />
             <span className="text-[11px] text-slate-500 font-medium">{macros.protein}</span>
          </div>
        </div>
      </div>
    </div>
    <div className="flex flex-col items-center gap-[4px]">
      <span className="text-[18px] font-medium text-slate-900 tracking-[-0.2px]">{calories}</span>
      <span className="text-[10px] text-slate-400">Calories</span>
    </div>
  </div>
);

export const FoodList: React.FC = () => {
  return (
    <div className="px-[20px] w-full mt-[24px] mb-[120px]">
      <div className="flex justify-between items-center mb-[12px]">
        <span className="text-[12px] font-medium text-slate-900 tracking-[-0.2px]">Recently uploaded</span>
        <div className="flex items-end gap-[4px] text-[10px]">
           <span className="text-slate-400 font-medium">Last logged:</span>
           <span className="text-slate-900">4 h 31 m</span>
           <span className="text-slate-400 font-medium">ago</span>
        </div>
      </div>
      
      <div className="flex flex-col gap-[12px]">
        <FoodItem 
          name="Hunter's Fried Chicken" 
          image={foodChicken1}
          macros={{ carbs: '54g', fat: '39g', protein: '60g' }}
          calories="945"
        />
        <FoodItem 
          name="Salad" 
          image={foodSalad}
          macros={{ carbs: '54g', fat: '39g', protein: '60g' }}
          calories="300"
        />
        <FoodItem 
          name="Hunter's Fried Chicken" 
          image={foodChicken2}
          macros={{ carbs: '54g', fat: '39g', protein: '60g' }}
          calories="945"
        />
      </div>
    </div>
  );
};
