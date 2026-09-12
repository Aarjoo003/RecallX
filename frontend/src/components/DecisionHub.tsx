import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { DecisionItem } from '../types';
import {
  CheckCircle2,
  Mountain,
  Code,
  Calendar,
  Wallet,
  ChevronRight,
  Clock,
  Search,
  Tag,
  X,
  ShieldCheck,
} from 'lucide-react';

interface DecisionHubProps {
  decisions: DecisionItem[];
  onOpenContext: (messageId: string, threadId?: string) => void;
  isLoading: boolean;
}

export const DecisionHub: React.FC<DecisionHubProps> = ({
  decisions,
  onOpenContext,
  isLoading,
}) => {
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'mountain':
        return <Mountain className="h-4 w-4 text-indigo-600" />;
      case 'code':
        return <Code className="h-4 w-4 text-violet-600" />;
      case 'calendar':
        return <Calendar className="h-4 w-4 text-sky-600" />;
      case 'wallet':
        return <Wallet className="h-4 w-4 text-emerald-600" />;
      default:
        return <CheckCircle2 className="h-4 w-4 text-indigo-600" />;
    }
  };

  const getAvatarColor = (name: string) => {
    const colors = [
      'bg-indigo-600 text-white',
      'bg-violet-600 text-white',
      'bg-sky-600 text-white',
      'bg-slate-700 text-white',
      'bg-teal-600 text-white',
      'bg-amber-600 text-white',
    ];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  const filterChips = ['All', 'Finalized', 'Open', 'Polled', 'Rejected'];

  const filteredDecisions = decisions.filter((dec) => {
    // Status filter
    if (filterStatus !== 'all') {
      const normalizedStatus = dec.status.toLowerCase();
      if (filterStatus === 'finalized' && !(normalizedStatus === 'confirmed' || normalizedStatus === 'finalized')) {
        return false;
      }
      if (filterStatus !== 'finalized' && normalizedStatus !== filterStatus) {
        return false;
      }
    }

    // Search filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const match =
        dec.title.toLowerCase().includes(q) ||
        dec.decision.toLowerCase().includes(q) ||
        dec.topic.toLowerCase().includes(q) ||
        dec.participant.toLowerCase().includes(q) ||
        dec.context_summary.toLowerCase().includes(q);
      if (!match) return false;
    }

    return true;
  });

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Section 10 Header */}
      <div className="text-center pt-2">
        <div className="inline-flex items-center space-x-2 rounded-full border border-indigo-100 bg-indigo-50/60 px-3.5 py-1 text-xs font-medium text-indigo-800 mb-3 shadow-2xs">
          <ShieldCheck className="h-3.5 w-3.5 text-indigo-600" />
          <span>Consensus Mining & Decision Trail</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Decisions
        </h2>
        <p className="mt-2 text-xs sm:text-sm text-slate-600 max-w-lg mx-auto leading-relaxed">
          Find what your group actually decided.
        </p>
      </div>

      {/* Search Bar & Filter Chips */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
        {/* Filter Chips */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 w-full sm:w-auto">
          {filterChips.map((chip) => {
            const chipLower = chip.toLowerCase();
            const isActive = filterStatus === chipLower;
            return (
              <motion.button
                key={chip}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setFilterStatus(chipLower)}
                className={`rounded-xl px-3 py-1.5 text-xs font-medium transition-all shadow-2xs cursor-pointer ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'bg-white text-slate-600 border border-slate-200/90 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                {chip}
              </motion.button>
            );
          })}
        </div>

        {/* Search within decisions */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search decisions, topics..."
            className="w-full rounded-xl border border-slate-200 bg-white py-1.5 pl-9 pr-8 text-xs text-slate-900 placeholder-slate-400 focus:border-indigo-600 focus:outline-none focus:ring-1 focus:ring-indigo-600 shadow-2xs"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-2 text-slate-400 hover:text-slate-600"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Decisions Grid */}
      {isLoading ? (
        <div className="text-center py-16 text-slate-400 text-sm">
          Loading decision milestones...
        </div>
      ) : filteredDecisions.length === 0 ? (
        <div className="rounded-2xl bg-white p-12 text-center border border-slate-200 shadow-2xs">
          <Search className="h-8 w-8 text-slate-400 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-slate-800">No decisions match your filters</h3>
          <p className="text-xs text-slate-500 mt-1">
            Try resetting your search query or selecting &ldquo;All&rdquo;.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredDecisions.map((dec, idx) => {
            const formattedDate = new Date(dec.timestamp).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            });

            return (
              <motion.div
                key={dec.id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: Math.min(idx * 0.04, 0.3) }}
                whileHover={{ y: -4, transition: { duration: 0.15 } }}
                className="flex flex-col justify-between rounded-2xl bg-slate-900/95 border border-slate-800/90 p-5 sm:p-6 shadow-md shadow-slate-950/30 text-slate-100 hover:border-slate-700 hover:shadow-lg transition-all"
              >
                <div>
                  {/* Top Bar: Topic tag & Consensus Badge */}
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                    <div className="flex items-center space-x-2">
                      <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-800/90 border border-slate-700/80">
                        {getIcon(dec.icon)}
                      </div>
                      <span className="rounded-md bg-slate-800 text-slate-300 border border-slate-700/60 px-2 py-0.5 text-[10px] font-mono font-medium uppercase tracking-wider">
                        {dec.topic}
                      </span>
                    </div>

                    <span className="inline-flex items-center space-x-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 px-2.5 py-0.5 text-[11px] font-bold text-emerald-400 font-mono">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                      <span>{dec.status === 'Confirmed' ? 'Finalized' : dec.status}</span>
                    </span>
                  </div>

                  {/* Decision Statement (Bold & Clear) */}
                  <div className="my-3.5">
                    <h3 className="text-base font-bold text-white leading-snug">
                      {dec.decision}
                    </h3>
                  </div>

                  {/* Context Summary */}
                  <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
                    {dec.context_summary}
                  </p>
                </div>

                {/* Footer Bar: Avatar + Name, Date, View in conversation */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <div
                      className={`flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold shadow-2xs ${getAvatarColor(
                        dec.participant
                      )}`}
                    >
                      {dec.participant.charAt(0)}
                    </div>
                    <span className="font-semibold text-slate-200 text-xs">
                      {dec.participant}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-slate-400 text-[11px] flex items-center space-x-1">
                      <Clock className="h-3 w-3 text-slate-500" />
                      <span>{formattedDate}</span>
                    </span>
                  </div>

                  <motion.button
                    whileHover={{ x: 2 }}
                    onClick={() => onOpenContext(dec.message_id)}
                    className="inline-flex items-center space-x-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
                  >
                    <span>View in conversation</span>
                    <ChevronRight className="h-3.5 w-3.5" />
                  </motion.button>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
};

