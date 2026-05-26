import React from 'react';
import './TabDock.css';

/**
 * TabDock — Fixed bottom-left floating navigation dock.
 * Renders 4 icon buttons with tooltips for switching tabs.
 * Props:
 *   - activeTab: string ('home' | 'operations' | 'analytics' | 'pathplanning')
 *   - onTabChange: (tab: string) => void
 */
const tabs = [
  {
    id: 'home',
    label: 'Home',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8" />
        <path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      </svg>
    ),
  },
  {
    id: 'operations',
    label: 'Operations',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.934a.5.5 0 0 0-.777-.416L16 11" />
        <rect x="2" y="6" width="14" height="12" rx="2" />
      </svg>
    ),
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 3v16a2 2 0 0 0 2 2h16" />
        <path d="m19 9-5 5-4-4-3 3" />
      </svg>
    ),
  },
  {
    id: 'pathplanning',
    label: 'Path Planning',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 13V2l8 4-8 4" />
        <path d="M20.561 10.222a9 9 0 1 1-12.55-5.29" />
        <path d="M8.002 16.293a3.5 3.5 0 0 1 6.056-1.862" />
      </svg>
    ),
  },
];

export default function TabDock({ activeTab, onTabChange }) {
  return (
    <nav className="tab-dock" aria-label="Main Navigation">
      {tabs.map((tab, idx) => (
        <React.Fragment key={tab.id}>
          {idx === 1 && <div className="tab-dock-separator" />}
          <button
            className={`tab-dock-btn${activeTab === tab.id ? ' active' : ''}`}
            onClick={() => onTabChange(tab.id)}
            aria-label={tab.label}
            aria-current={activeTab === tab.id ? 'page' : undefined}
            id={`tab-dock-${tab.id}`}
          >
            {tab.icon}
            <span className="tab-dock-tooltip">{tab.label}</span>
          </button>
        </React.Fragment>
      ))}
    </nav>
  );
}
