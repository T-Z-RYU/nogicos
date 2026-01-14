import { useState } from 'react'

const tabs = ['Daily Meal', 'Exercise', 'Scanned']

export function MealTabs() {
  const [activeTab, setActiveTab] = useState(0)

  return (
    <div className="flex gap-0 mt-2" data-testid="meal-tabs">
      {tabs.map((tab, index) => (
        <button
          key={tab}
          onClick={() => setActiveTab(index)}
          className={`
            px-4 py-2 text-base font-medium transition-colors
            ${index === activeTab 
              ? 'text-text-primary border-b-2 border-text-primary' 
              : 'text-text-tertiary'
            }
          `}
          data-testid={`tab-${tab.toLowerCase().replace(' ', '-')}`}
        >
          {tab}
        </button>
      ))}
    </div>
  )
}
