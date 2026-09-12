import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Filter, User, Calendar, CheckSquare, ShieldCheck, Terminal, Cpu } from 'lucide-react';
import { Participant, SearchFilterInput } from '../types';

interface SearchHeroProps {
  query: string;
  setQuery: (query: string) => void;
  onSearch: (q: string, filters?: SearchFilterInput) => void;
  isLoading: boolean;
  participants: Participant[];
  activeFilters: SearchFilterInput;
  setActiveFilters: React.Dispatch<React.SetStateAction<SearchFilterInput>>;
}

const PRESET_QUERIES = [
  {
    label: 'When did we decide on the trip?',
    query: 'When did we finally settle on the destination?',
    badge: 'Zero-Word Match',
    badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  {
    label: 'What did Priya say about the budget?',
    query: 'What did Priya say about the budget limit?',
    badge: 'Person + Topic',
    badgeClass: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  },
  {
    label: 'What did we discuss last month?',
    query: 'What was announced in late August?',
    badge: 'Temporal',
    badgeClass: 'bg-amber-50 text-amber-700 border-amber-200',
  },
  {
    label: 'mera bday kab hai?',
    query: 'mera bday kab hai',
    badge: 'Hinglish',
    badgeClass: 'bg-violet-50 text-violet-700 border-violet-200',
  },
  {
    label: 'Where did we finally decide to go?',
    query: 'Where did we finally decide to go?',
    badge: 'Consensus',
    badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  {
    label: 'trip ka final kya hua?',
    query: 'trip ka final kya hua',
    badge: 'Hinglish Decision',
    badgeClass: 'bg-violet-50 text-violet-700 border-violet-200',
  },
  {
    label: 'Which technical stack was picked for the capstone?',
    query: 'Which technical stack was picked for the capstone?',
    badge: 'Zero-Word Match',
    badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
];

export const SearchHero: React.FC<SearchHeroProps> = ({
  query,
  setQuery,
  onSearch,
  isLoading,
  participants,
  activeFilters,
  setActiveFilters,
}) => {
  const [showFilters, setShowFilters] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim(), activeFilters);
    }
  };

  const handlePresetClick = (presetQuery: string) => {
    setQuery(presetQuery);
    onSearch(presetQuery, activeFilters);
  };

  const clearQuery = () => {
    setQuery('');
  };

  const handleFilterChange = (updates: Partial<SearchFilterInput>) => {
    const updated = { ...activeFilters, ...updates };
    setActiveFilters(updated);
    if (query.trim()) {
      onSearch(query.trim(), updated);
    }
  };

  const resetFilters = () => {
    const cleared: SearchFilterInput = {
      participant: undefined,
      start_date: undefined,
      end_date: undefined,
      thread_id: undefined,
      is_decision_only: false,
    };
    setActiveFilters(cleared);
    if (query.trim()) {
      onSearch(query.trim(), cleared);
    }
  };

  const hasActiveFilters =
    Boolean(activeFilters.participant) ||
    Boolean(activeFilters.start_date) ||
    Boolean(activeFilters.end_date) ||
    Boolean(activeFilters.is_decision_only);

  return (
    <div className="w-full">
      {/* Title & Product Tagline */}
      <div className="text-center mb-7 pt-2">
        <div className="inline-flex items-center space-x-2 rounded-full border border-indigo-100 bg-indigo-50/60 px-3.5 py-1 text-xs font-medium text-indigo-800 mb-3.5 shadow-2xs">
          <span className="flex h-1.5 w-1.5 rounded-full bg-indigo-600 animate-pulse" />
          <span>Semantic Group Chat Search • 100% Offline & Private</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-5xl max-w-3xl mx-auto leading-tight">
          Search what your group <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-indigo-700 bg-clip-text text-transparent">meant</span> — not just what they typed.
        </h1>
        <p className="mt-3 text-xs sm:text-base text-slate-600 max-w-xl mx-auto leading-relaxed">
          Find decisions, conversations, people and moments across thousands of messages using semantic search.
        </p>
      </div>

      {/* Main Search Bar */}
      <form onSubmit={handleSubmit} className="relative max-w-3xl mx-auto">
        <div className="relative flex items-center rounded-2xl bg-white border border-slate-300/90 focus-within:border-indigo-600 focus-within:ring-4 focus-within:ring-indigo-500/10 shadow-md shadow-slate-200/60 transition-all">
          <div className="pl-4 text-indigo-600">
            <Search className="h-5 w-5 stroke-[2.2]" />
          </div>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about your group chat..."
            className="w-full py-4 pl-3.5 pr-36 text-sm sm:text-base text-slate-900 placeholder-slate-400 bg-transparent focus:outline-none"
            autoFocus
          />

          {/* Right action buttons */}
          <div className="absolute right-2 flex items-center space-x-1.5">
            <kbd className="hidden md:inline-flex items-center px-2 py-0.5 text-[10px] font-mono font-medium text-slate-400 bg-slate-100 rounded border border-slate-200">
              Ctrl+K
            </kbd>

            {query && (
              <button
                type="button"
                onClick={clearQuery}
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors"
                title="Clear query"
              >
                <X className="h-4 w-4" />
              </button>
            )}

            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded-xl text-xs font-medium flex items-center space-x-1 transition-colors ${
                hasActiveFilters
                  ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                  : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
              }`}
              title="Toggle filters"
            >
              <Filter className="h-4 w-4" />
              {hasActiveFilters && (
                <span className="flex h-1.5 w-1.5 rounded-full bg-indigo-600" />
              )}
            </button>

            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              type="submit"
              disabled={isLoading || !query.trim()}
              className="rounded-xl bg-indigo-600 px-4 py-2 text-xs sm:text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-xs cursor-pointer"
            >
              {isLoading ? 'Searching...' : 'Search'}
            </motion.button>
          </div>
        </div>

        {/* Filter Drawer with smooth height & opacity transition */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0, overflow: 'hidden' }}
              animate={{ opacity: 1, height: 'auto', overflow: 'visible' }}
              exit={{ opacity: 0, height: 0, overflow: 'hidden' }}
              transition={{ duration: 0.2 }}
              className="mt-3 p-4 rounded-2xl bg-white border border-slate-200 shadow-lg text-slate-700"
            >
              <div className="flex items-center justify-between pb-3 border-b border-slate-200">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Manual Filter Overrides
                </span>
                {hasActiveFilters && (
                  <button
                    type="button"
                    onClick={resetFilters}
                    className="text-xs font-medium text-rose-600 hover:underline cursor-pointer"
                  >
                    Reset all filters
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3">
                {/* Participant Filter */}
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1 flex items-center space-x-1">
                    <User className="h-3.5 w-3.5 text-slate-400" />
                    <span>Participant</span>
                  </label>
                  <select
                    value={activeFilters.participant || ''}
                    onChange={(e) =>
                      handleFilterChange({ participant: e.target.value || undefined })
                    }
                    className="w-full rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  >
                    <option value="">All 10 Participants</option>
                    {participants.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.role})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Start Date */}
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1 flex items-center space-x-1">
                    <Calendar className="h-3.5 w-3.5 text-slate-400" />
                    <span>From Date</span>
                  </label>
                  <input
                    type="date"
                    value={activeFilters.start_date || ''}
                    onChange={(e) =>
                      handleFilterChange({ start_date: e.target.value || undefined })
                    }
                    className="w-full rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  />
                </div>

                {/* Decision Only */}
                <div className="flex items-end pb-1">
                  <label className="flex items-center space-x-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={Boolean(activeFilters.is_decision_only)}
                      onChange={(e) =>
                        handleFilterChange({ is_decision_only: e.target.checked })
                      }
                      className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                    />
                    <span className="text-xs font-medium text-slate-700 flex items-center space-x-1">
                      <CheckSquare className="h-3.5 w-3.5 text-emerald-600" />
                      <span>Decision messages only</span>
                    </span>
                  </label>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </form>

      {/* Preset Suggestions Bar */}
      <div className="max-w-4xl mx-auto mt-4">
        <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none">
          <span className="text-xs font-semibold text-slate-500 whitespace-nowrap">
            Try Queries:
          </span>
          {PRESET_QUERIES.map((preset, idx) => (
            <motion.button
              key={idx}
              whileHover={{ scale: 1.04, y: -1 }}
              whileTap={{ scale: 0.96 }}
              onClick={() => handlePresetClick(preset.query)}
              className="inline-flex items-center space-x-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-700 hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-900 transition-all whitespace-nowrap shadow-2xs cursor-pointer"
            >
              <span>{preset.label}</span>
              <span
                className={`rounded-full px-1.5 py-0.2 text-[10px] font-mono font-semibold border ${preset.badgeClass}`}
              >
                {preset.badge}
              </span>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
};
