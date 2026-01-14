import React from 'react';

// 本地资源导入 - 直接替换 Figma localhost 链接
import foodChicken from '../assets/food-chicken.png';
import iconBell from '../assets/icon-bell.svg';
import iconArm from '../assets/icon-arm.svg';
import iconBottle from '../assets/icon-bottle.svg';
import iconChicken from '../assets/icon-chicken.svg';
import iconCookie from '../assets/icon-cookie.svg';
import navHome from '../assets/nav-home.svg';
import navProgress from '../assets/nav-progress.svg';
import navExercise from '../assets/nav-exercise.svg';
import navScan from '../assets/nav-scan.svg';
import navProfile from '../assets/nav-profile.svg';
import ellipseBase from '../assets/ellipse-base.svg';
import ellipseSelectedBase from '../assets/ellipse-selected-base.svg';
import ellipseSelectedActive from '../assets/ellipse-selected-active.svg';
import circleBg from '../assets/circle-bg.svg';
import circleProgress from '../assets/circle-progress.svg';
import circleDot from '../assets/circle-dot.svg';
import progressCarbs from '../assets/progress-carbs.svg';
import progressFat from '../assets/progress-fat.svg';
import progressProtein from '../assets/progress-protein.svg';
import statusCellular from '../assets/status-cellular.svg';
import statusWifi from '../assets/status-wifi.svg';
import statusBattery from '../assets/status-battery.svg';
import line1 from '../assets/line-1.svg';
import line2 from '../assets/line-2.svg';
import line3 from '../assets/line-3.svg';

/**
 * HomePage - 像素级还原 Figma 设计稿
 * 
 * 数据源对照（按新规则）：
 * | 属性 | Figma 值 | 代码值 | 来源 |
 * |------|----------|--------|------|
 * | 容器宽度 | 402px | w-[402px] | Figma node 1932:20039 |
 * | 卡片尺寸 | 362×157px | w-[362px] h-[157px] | Figma node 1932:20092 |
 * | 圆环尺寸 | 125×125px | size-[125px] | Figma node 1932:20100 |
 * | 字体 | Outfit Medium | font-['Outfit:Medium',sans-serif] | Figma text styles |
 * | 主色 | #0f172a | text-[#0f172a] | Figma fill |
 * | 次色 | #334155 | text-[#334155] | Figma fill |
 * | 背景渐变 | #f1f5f9 → #f8fafc | from-[#f1f5f9] to-[#f8fafc] | Figma background |
 */

export default function HomePage() {
  return (
    <div className="bg-gradient-to-b from-[#f1f5f9] relative size-full to-[#f8fafc] min-h-screen" data-name="Home / Summary – Default">
      
      {/* Status Bar - 精确位置: top-0, w-402px */}
      <div className="absolute content-stretch flex gap-[154px] items-center justify-center left-1/2 px-[16px] py-[20px] top-0 translate-x-[-50%] w-[402px]">
        <div className="basis-0 content-stretch flex grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-[2px] px-0 relative shrink-0">
          <p className="font-['Outfit:SemiBold',sans-serif] font-semibold leading-[22px] relative shrink-0 text-[#0f172a] text-[16px] text-center text-nowrap">
            9:41
          </p>
        </div>
        <div className="basis-0 content-stretch flex gap-[7px] grow h-[22px] items-center justify-center min-h-px min-w-px pb-0 pt-px px-0 relative shrink-0">
          <img alt="" className="h-[12.226px] w-[19.2px]" src={statusCellular} />
          <img alt="" className="h-[12.328px] w-[17.142px]" src={statusWifi} />
          <img alt="" className="h-[13px] w-[27.328px]" src={statusBattery} />
        </div>
      </div>

      {/* Main Content - 精确位置: top-62px */}
      <div className="absolute content-stretch flex flex-col gap-[20px] items-center justify-center left-0 top-[62px] w-[402px] left-1/2 translate-x-[-50%]">
        
        {/* Header - 精确: px-20px, h-40px */}
        <div className="content-stretch flex items-center justify-between px-[20px] py-0 relative shrink-0 w-full">
          <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[40px] relative shrink-0 text-[#0f172a] text-[28px] text-nowrap text-shadow-[0px_1px_2px_rgba(15,23,42,0.05)] tracking-[-0.5px]">
            Vitaflow
          </p>
          <div className="bg-gradient-to-b from-[#ffffff] relative rounded-[12px] shadow-[0px_1px_2px_0px_rgba(15,23,42,0.04),0px_2px_4px_0px_rgba(15,23,42,0.03)] shrink-0 size-[40px] to-[#f8fafc] flex items-center justify-center">
            <img alt="" className="size-[24px]" src={iconBell} />
          </div>
        </div>

        {/* Calendar Strip - 精确: px-20px, gap-between */}
        <div className="content-stretch flex items-center justify-between px-[20px] py-0 relative shrink-0 w-[402px]">
          {/* Date Items - 非选中状态 */}
          {[
            { day: 'Thu', date: '27' },
            { day: 'Fri', date: '28' },
            { day: 'Sat', date: '29' },
            { day: 'Sun', date: '30' },
          ].map((item, index) => (
            <div key={index} className="content-stretch flex flex-col gap-[8px] items-center p-[4px] relative shrink-0 w-[48px]">
              <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] min-w-full relative shrink-0 text-[#475569] text-[12px] text-center tracking-[-0.4px] w-[min-content]">
                {item.day}
              </p>
              <div className="relative shrink-0 size-[36px]">
                <img alt="" className="absolute left-0 size-[36px] top-0" src={ellipseBase} />
                <p className="absolute font-['Outfit:Medium',sans-serif] font-medium leading-[normal] left-[50%] text-[#475569] text-[12px] text-center text-nowrap top-[10px] tracking-[-0.2px] translate-x-[-50%]">
                  {item.date}
                </p>
              </div>
            </div>
          ))}

          {/* Date Item - 选中状态 (Mon 31) */}
          <div className="bg-gradient-to-b content-stretch flex flex-col from-[#ffffff] gap-[8px] items-center p-[4px] relative rounded-[12px] shadow-[0px_1px_2px_0px_rgba(15,23,42,0.03),0px_2px_4px_0px_rgba(15,23,42,0.02)] shrink-0 to-[#f8fafc] w-[48px]">
            <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] min-w-full relative shrink-0 text-[#0f172a] text-[12px] text-center tracking-[-0.4px] w-[min-content]">
              Mon
            </p>
            <div className="relative shrink-0 size-[36px]">
              <img alt="" className="absolute left-0 size-[36px] top-0" src={ellipseSelectedBase} />
              <div className="absolute left-0 size-[36px] top-0">
                <div className="absolute inset-[-33.33%_-16.64%_-33.11%_-33.33%]">
                  <img alt="" className="block max-w-none size-full" src={ellipseSelectedActive} />
                </div>
              </div>
              <p className="absolute font-['Outfit:Medium',sans-serif] font-medium leading-[normal] left-[50%] text-[#0f172a] text-[12px] text-center text-nowrap top-[10px] tracking-[-0.2px] translate-x-[-50%]">
                31
              </p>
            </div>
          </div>

          {/* Date Items - 未来日期（灰色） */}
          {[
            { day: 'Tue', date: '1' },
            { day: 'Wed', date: '2' },
          ].map((item, index) => (
            <div key={index} className="content-stretch flex flex-col gap-[8px] items-center p-[4px] relative shrink-0 w-[48px]">
              <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] min-w-full relative shrink-0 text-[#94a3b8] text-[12px] text-center tracking-[-0.4px] w-[min-content]">
                {item.day}
              </p>
              <div className="relative shrink-0 size-[36px]">
                <img alt="" className="absolute left-0 size-[36px] top-0" src={ellipseBase} />
                <p className="absolute font-['Outfit:Medium',sans-serif] font-medium leading-[normal] left-[50%] text-[#94a3b8] text-[12px] text-center text-nowrap top-[10px] tracking-[-0.2px] translate-x-[-50%]">
                  {item.date}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Main Content Container */}
        <div className="content-stretch flex flex-col gap-[16px] items-start relative shrink-0 w-full">
          
          {/* Summary Section - 精确: px-20px */}
          <div className="content-stretch flex flex-col gap-[23px] h-[279px] items-center px-[20px] py-0 relative shrink-0 w-full">
            <div className="h-[249px] relative shrink-0 w-[362px]">
              <div className="absolute content-end flex flex-wrap gap-[16px_12px] items-end left-0 top-0 w-[362px]">
                
                {/* Calorie Card - 精确: 362×157px, p-16px */}
                <div className="bg-white content-stretch flex h-[157px] items-start justify-between overflow-clip p-[16px] relative rounded-[12px] shadow-[0px_1px_3px_0px_rgba(15,23,42,0.05),0px_4px_12px_0px_rgba(15,23,42,0.03)] shrink-0 w-[362px]">
                  <div className="basis-0 content-stretch flex flex-col grow h-full items-start justify-between min-h-px min-w-px relative shrink-0">
                    <p className="font-['Outfit:Regular',sans-serif] font-normal leading-[normal] relative shrink-0 text-[#334155] text-[12px] text-center text-nowrap tracking-[-0.4px]">
                      Calories
                    </p>
                    <div className="content-stretch flex items-end relative shrink-0 w-full">
                      <div className="content-stretch flex gap-[4px] items-end leading-[normal] relative shrink-0 text-center">
                        <p className="font-['Outfit:Medium',sans-serif] font-medium relative shrink-0 text-[#0f172a] text-[48px] text-nowrap text-shadow-[0px_1px_2px_rgba(15,23,42,0.08)] tracking-[-1px]">
                          2,505
                        </p>
                        <p className="font-['Outfit:Regular',sans-serif] font-normal h-[23px] relative shrink-0 text-[#334155] text-[12px] tracking-[-0.2px] w-[21px]">
                          kcal
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Circle Progress - 精确: 125×125px */}
                  <div className="content-stretch flex flex-col gap-[12px] items-start relative shrink-0">
                    <div className="relative shrink-0 size-[125px]">
                      <img alt="" className="block max-w-none size-full" src={circleBg} />
                    </div>
                    <div className="absolute flex items-center justify-center left-[calc(50%+0.01px)] size-[125px] top-[calc(50%+0.02px)] translate-x-[-50%] translate-y-[-50%]">
                      <div className="flex-none rotate-[180deg]">
                        <div className="relative size-[125px]">
                          <div className="absolute inset-[-9.49%_-9.6%_-9.6%_3.31%]">
                            <img alt="" className="block max-w-none size-full" src={circleProgress} />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="absolute left-[101px] size-[6px] top-[19px]">
                      <img alt="" className="block max-w-none size-full" src={circleDot} />
                    </div>
                    <div className="absolute content-stretch flex flex-col gap-[4px] items-center left-1/2 top-[calc(50%+0.5px)] translate-x-[-50%] translate-y-[-50%]">
                      <img alt="" className="shrink-0 size-[16px]" src={iconArm} />
                      <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] relative shrink-0 text-[#475569] text-[10px] text-nowrap tracking-[-0.4px]">
                        Left
                      </p>
                    </div>
                  </div>
                </div>

                {/* Macro Cards - 精确: 112.667px 宽度 */}
                {[
                  { label: 'Carbs', value: '165g', icon: iconBottle, progressImg: progressCarbs },
                  { label: 'Fat', value: '98g', icon: iconChicken, progressImg: progressFat },
                  { label: 'Protein', value: '43g', icon: iconCookie, progressImg: progressProtein },
                ].map((macro, index) => (
                  <div key={index} className="bg-white content-stretch flex flex-col gap-[16px] items-start p-[12px] relative rounded-[12px] shadow-[0px_1px_2px_0px_rgba(15,23,42,0.04),0px_2px_6px_-2px_rgba(15,23,42,0.03)] shrink-0 w-[112.667px]">
                    <div className="content-stretch flex items-start justify-between relative shrink-0 w-full">
                      <div className="content-stretch flex flex-col gap-[4px] items-start relative shrink-0 text-center text-nowrap">
                        <p className="font-['Outfit:Regular',sans-serif] font-normal leading-[normal] relative shrink-0 text-[#334155] text-[10px] tracking-[-0.4px]">
                          {macro.label}
                        </p>
                        <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] relative shrink-0 text-[#0f172a] text-[16px] text-shadow-[0px_1px_2px_rgba(15,23,42,0.05)] tracking-[-0.2px]">
                          {macro.value}
                        </p>
                      </div>
                      <img alt="" className="shrink-0 size-[16px]" src={macro.icon} />
                    </div>
                    <div className="flex h-[6px] items-center justify-center relative shrink-0 w-full">
                      <img alt="" className="h-[6px] w-full object-contain" src={macro.progressImg} />
                    </div>
                  </div>
                ))}
              </div>

              {/* Chart Lines */}
              <div className="absolute h-0 left-[15px] top-[241px] w-[41px]">
                <div className="absolute inset-[-11px_-19.51%_-11px_-26.83%]">
                  <img alt="" className="block max-w-none size-full" src={line1} />
                </div>
              </div>
              <div className="absolute h-0 left-[140px] top-[241px] w-[41px]">
                <div className="absolute inset-[-11px_-19.51%_-11px_-26.83%]">
                  <img alt="" className="block max-w-none size-full" src={line2} />
                </div>
              </div>
              <div className="absolute h-0 left-[264px] top-[241px] w-[42px]">
                <div className="absolute inset-[-11px_-19.05%_-11px_-26.19%]">
                  <img alt="" className="block max-w-none size-full" src={line3} />
                </div>
              </div>
            </div>

            {/* Pagination Dots */}
            <div className="bg-white h-[7px] relative rounded-[2px] shadow-[0px_1px_2px_0px_rgba(15,23,42,0.03),0px_2px_4px_0px_rgba(15,23,42,0.02)] shrink-0 w-[42px]">
              <div className="absolute bg-[#e2e8f0] h-[5px] left-px rounded-[2px] top-px w-[10px]" />
              <div className="absolute bg-[rgba(255,255,255,0)] h-[5px] left-[11px] rounded-[1000px] top-px w-[10px]" />
              <div className="absolute bg-[rgba(255,255,255,0)] h-[5px] left-[21px] rounded-[1000px] top-px w-[10px]" />
              <div className="absolute bg-[rgba(255,255,255,0)] h-[5px] left-[31px] rounded-[1000px] top-px w-[10px]" />
            </div>
          </div>

          {/* Recently Uploaded Section */}
          <div className="content-stretch flex flex-col gap-[12px] items-start px-[20px] py-0 relative shrink-0 w-full">
            {/* Header */}
            <div className="content-stretch flex h-[19px] items-center justify-between relative shrink-0 w-full">
              <p className="font-['Outfit:Medium',sans-serif] font-medium h-[8px] leading-[normal] relative shrink-0 text-[#0f172a] text-[12px] text-center tracking-[-0.2px] w-[96px]">
                Recently uploaded
              </p>
              <div className="content-stretch flex gap-[4px] items-center leading-[0] relative shrink-0 text-[10px] text-right tracking-[-0.4px]">
                <span className="font-['Outfit:Medium',sans-serif] font-medium text-[#94a3b8]">Last logged:</span>
                <span className="font-['Outfit:Medium',sans-serif] font-medium text-[#0f172a]">4</span>
                <span className="font-['Outfit:Medium',sans-serif] font-medium text-[#0f172a] tracking-[-0.4px]">h 31 m</span>
                <span className="font-['Outfit:Medium',sans-serif] font-medium text-[#94a3b8]">ago</span>
              </div>
            </div>

            {/* Food Items */}
            {[
              { name: "Hunter's Fried Chicken", calories: '945', macros: { carbs: '54g', fat: '39g', protein: '60g' } },
              { name: 'Salad', calories: '300', macros: { carbs: '54g', fat: '39g', protein: '60g' } },
              { name: "Hunter's Fried Chicken", calories: '945', macros: { carbs: '54g', fat: '39g', protein: '60g' } },
            ].map((food, index) => (
              <div key={index} className="bg-white content-stretch flex h-[88px] items-center justify-between p-[12px] relative rounded-[12px] shadow-[0px_1px_2px_0px_rgba(15,23,42,0.03),0px_2px_4px_0px_rgba(15,23,42,0.02)] shrink-0 w-[362px]">
                <div className="content-stretch flex gap-[16px] items-center relative shrink-0">
                  <div className="border border-[rgba(15,23,42,0.05)] border-solid relative rounded-[8px] shrink-0 size-[64px] overflow-hidden">
                    <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none rounded-[8px] size-full" src={foodChicken} />
                  </div>
                  <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0">
                    <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] relative shrink-0 text-[#1e293b] text-[14px] text-nowrap tracking-[-0.2px]">
                      {food.name}
                    </p>
                    <div className="content-stretch flex gap-[12px] items-center relative shrink-0 w-full">
                      <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
                        <img alt="" className="shrink-0 size-[16px]" src={iconCookie} />
                        <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] relative shrink-0 text-[#64748b] text-[11px] text-center text-nowrap tracking-[-0.2px]">
                          {food.macros.carbs}
                        </p>
                      </div>
                      <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
                        <img alt="" className="shrink-0 size-[16px]" src={iconBottle} />
                        <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] relative shrink-0 text-[#64748b] text-[11px] text-center text-nowrap tracking-[-0.2px]">
                          {food.macros.fat}
                        </p>
                      </div>
                      <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
                        <img alt="" className="shrink-0 size-[16px]" src={iconChicken} />
                        <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] relative shrink-0 text-[#64748b] text-[11px] text-center text-nowrap tracking-[-0.2px]">
                          {food.macros.protein}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="content-stretch flex flex-col font-['Outfit:Medium',sans-serif] font-medium gap-[4px] items-center leading-[normal] relative shrink-0 text-center">
                  <p className="relative shrink-0 text-[#0f172a] text-[18px] text-shadow-[0px_1px_2px_rgba(15,23,42,0.05)] tracking-[-0.2px] w-[35px]">
                    {food.calories}
                  </p>
                  <p className="relative shrink-0 text-[#94a3b8] text-[10px] text-nowrap tracking-[-0.4px]">
                    Calories
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Navigation Background */}
      <div className="absolute bg-[rgba(241,245,249,0)] bottom-0 h-[104px] left-1/2 rounded-bl-[60px] rounded-br-[60px] translate-x-[-50%] w-[402px]" />
      <div className="absolute bg-gradient-to-t bottom-0 from-[#f1f5f9] from-[17.857%] h-[125px] left-1/2 to-[rgba(241,245,249,0)] translate-x-[-50%] w-[402px]" />

      {/* Bottom Navigation */}
      <div className="absolute bottom-0 content-stretch flex flex-col items-center left-1/2 translate-x-[-50%] w-[402px]">
        <div className="content-stretch flex items-center px-[20px] py-0 relative shrink-0 w-full">
          <div className="basis-0 bg-white content-stretch flex grow items-center min-h-px min-w-px p-[4px] rounded-[24px] shadow-[0px_-1px_3px_0px_rgba(15,23,42,0.04),0px_-4px_12px_0px_rgba(15,23,42,0.03)] shrink-0 sticky top-0">
            
            {/* Home - Active */}
            <div className="basis-0 content-stretch flex flex-col gap-[4px] grow h-[56px] items-center justify-end min-h-px min-w-px pb-[6px] pt-[8px] px-0 relative rounded-[100px] shrink-0">
              <img alt="" className="shrink-0 size-[24px]" src={navHome} />
              <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] min-w-full relative shrink-0 text-[#0f172a] text-[11px] text-center tracking-[-0.2px] w-[min-content]">
                Home
              </p>
            </div>

            {/* Progress */}
            <div className="basis-0 content-stretch flex flex-col gap-[4px] grow h-[56px] items-center justify-end min-h-px min-w-px pb-[6px] pt-[8px] px-0 relative rounded-[100px] shrink-0">
              <img alt="" className="shrink-0 size-[24px]" src={navProgress} />
              <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] min-w-full relative shrink-0 text-[#94a3b8] text-[11px] text-center tracking-[-0.2px] w-[min-content]">
                Progress
              </p>
            </div>

            {/* Center Scan Button - 精确: 56×56px, bg-#0f172a */}
            <div className="absolute content-stretch flex items-center left-[153px] top-[3px]">
              <div className="bg-[#0f172a] content-stretch flex flex-col items-center justify-center p-[16px] relative rounded-[888.889px] shadow-[0px_2px_4px_0px_rgba(15,23,42,0.15),0px_6px_16px_0px_rgba(15,23,42,0.1)] shrink-0 size-[56px]">
                <img alt="" className="shrink-0 size-[26.947px]" src={navScan} />
              </div>
            </div>

            {/* Spacer for center button */}
            <div className="content-stretch flex flex-col gap-[2px] items-center opacity-0 px-0 py-[8px] relative rounded-[100px] shrink-0 w-[64px]">
              <div className="shrink-0 size-[22px]" />
              <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] min-w-full relative shrink-0 text-[#999] text-[10px] text-center w-[min-content]">
                Exercise
              </p>
            </div>

            {/* Exercise */}
            <div className="basis-0 content-stretch flex flex-col gap-[4px] grow h-[56px] items-center justify-end min-h-px min-w-px pb-[6px] pt-[8px] px-0 relative rounded-[100px] shrink-0">
              <img alt="" className="shrink-0 size-[24px]" src={navExercise} />
              <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] min-w-full relative shrink-0 text-[#94a3b8] text-[11px] text-center tracking-[-0.2px] w-[min-content]">
                Exercise
              </p>
            </div>

            {/* Profile */}
            <div className="basis-0 content-stretch flex flex-col gap-[4px] grow h-[56px] items-center justify-end min-h-px min-w-px pb-[6px] pt-[8px] px-0 relative rounded-[100px] shrink-0">
              <img alt="" className="shrink-0 size-[24px]" src={navProfile} />
              <p className="font-['Outfit:Medium',sans-serif] font-medium leading-[normal] min-w-full relative shrink-0 text-[#94a3b8] text-[11px] text-center tracking-[-0.2px] w-[min-content]">
                Profile
              </p>
            </div>
          </div>
        </div>

        {/* Home Indicator */}
        <div className="h-[34px] relative shrink-0 w-full">
          <div className="absolute bottom-[8px] flex h-[5px] items-center justify-center left-1/2 translate-x-[-50%] w-[144px]">
            <div className="bg-[#2b2735] h-[5px] rounded-[100px] w-[144px]" />
          </div>
        </div>
      </div>
    </div>
  );
}

