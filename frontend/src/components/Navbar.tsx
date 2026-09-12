import React from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  CheckCircle2,
  Calendar,
  Award,
  Sliders,
  Sparkles,
} from 'lucide-react';

export type ActiveTab = 'search' | 'decisions' | 'timeline' | 'evaluation' | 'explorer';

interface NavbarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  indexedCount?: number;
  engineOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  indexedCount = 5207,
  engineOnline,
}) => {
  const tabs = [
    { id: 'search' as ActiveTab, label: 'Search', icon: Search },
    { id: 'decisions' as ActiveTab, label: 'Decisions', icon: CheckCircle2 },
    { id: 'timeline' as ActiveTab, label: 'Timeline', icon: Calendar },
    {
      id: 'evaluation' as ActiveTab,
      label: 'Evaluation',
      icon: Award,
      badge: '100%',
    },
    { id: 'explorer' as ActiveTab, label: 'Architecture', shortLabel: 'Engine', icon: Sliders },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 bg-white/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand & Wordmark */}
        <motion.div
          className="flex items-center space-x-3 cursor-pointer"
          onClick={() => setActiveTab('search')}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white shadow-xs font-bold">
            <span className="text-sm font-black tracking-wider">RX</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-black tracking-tight text-slate-900 font-mono">
                RECALL<span className="text-indigo-600">X</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-500 hidden sm:block">
              Semantic Search for Conversational Archives
            </p>
          </div>
        </motion.div>

        {/* Pill-Style Navigation Tabs with Framer Motion Sliding Pill */}
        <nav className="relative flex items-center space-x-1 rounded-xl bg-slate-100/90 border border-slate-200/80 p-1 shadow-2xs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className={`relative z-10 flex items-center space-x-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-medium transition-colors ${
                  isActive
                    ? 'text-slate-900 font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeNavTabPill"
                    className="absolute inset-0 -z-10 rounded-lg bg-white shadow-xs border border-slate-200/90"
                    transition={{ type: 'spring', bounce: 0.15, duration: 0.35 }}
                  />
                )}
                <Icon className={`h-3.5 w-3.5 ${isActive ? 'text-indigo-600' : 'text-slate-500'}`} />
                <span className={tab.shortLabel ? 'hidden sm:inline' : ''}>{tab.label}</span>
                {tab.shortLabel && <span className="sm:hidden">{tab.shortLabel}</span>}
                {tab.badge && (
                  <motion.span
                    animate={{ scale: [1, 1.06, 1] }}
                    transition={{ repeat: Infinity, duration: 3 }}
                    className="hidden md:inline-block rounded-full bg-emerald-50 border border-emerald-200 px-1.5 py-0.2 text-[10px] font-mono font-bold text-emerald-700"
                  >
                    {tab.badge}
                  </motion.span>
                )}
              </motion.button>
            );
          })}
        </nav>

        {/* Engine Telemetry Status Badge */}
        <div className="hidden lg:flex items-center space-x-2 rounded-xl border border-slate-200/80 bg-slate-50/80 px-3 py-1.5 text-xs shadow-2xs">
          <span className="relative flex h-2 w-2">
            <span
              className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${
                engineOnline ? 'bg-emerald-400' : 'bg-amber-400'
              }`}
            />
            <span
              className={`relative inline-flex h-2 w-2 rounded-full ${
                engineOnline ? 'bg-emerald-500' : 'bg-amber-500'
              }`}
            />
          </span>
          <span className="font-medium text-slate-700">
            {engineOnline ? `Index ready • ${indexedCount.toLocaleString()} msgs` : 'Connecting...'}
          </span>
          <span className="text-slate-300">|</span>
          <span className="font-mono text-slate-500 font-medium">384d Dense + BM25</span>
        </div>
      </div>
    </header>
  );
};

