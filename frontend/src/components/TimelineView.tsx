import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Calendar,
  CheckCircle2,
  MessageSquare,
  ArrowRight,
  Clock,
  Sparkles,
  Flame,
  Lightbulb,
  Compass,
  ShieldCheck,
} from 'lucide-react';

interface TimelineViewProps {
  onOpenContext: (messageId: string) => void;
  onSearchQuery: (query: string) => void;
}

interface Milestone {
  date: string;
  month: string;
  title: string;
  category: string;
  tagType: 'decision' | 'debate' | 'plan' | 'announcement';
  description: string;
  quote: string;
  speaker: string;
  messageId?: string;
  searchTrigger: string;
}

const MILESTONES: Milestone[] = [
  {
    date: 'March 05, 2026',
    month: 'March',
    title: 'Spring Semester Kickoff & Fest Budget',
    category: 'College Fest',
    tagType: 'plan',
    description: 'First meeting notes recorded for Innovate 2026. Preliminary decorations and sponsorship committee formed.',
    quote: 'Stage decorations committee budget approved for early March kickoff.',
    speaker: 'Tanvi Malhotra',
    searchTrigger: 'First week of March meeting notes',
  },
  {
    date: 'April 10, 2026',
    month: 'April',
    title: 'Capstone Tech Stack Locked: FastAPI + React',
    category: 'Academics',
    tagType: 'decision',
    description: 'After testing Django and Flask, group finalized FastAPI for high-speed async ML inference and React for the UI.',
    quote: 'FastAPI with React confirmed as our build choice.',
    speaker: 'Sneha Rao',
    messageId: 'msg_1390',
    searchTrigger: 'Which technical stack was picked for the capstone?',
  },
  {
    date: 'April 25, 2026',
    month: 'April',
    title: 'Weekend Cricket Arena Tournament',
    category: 'Recreation',
    tagType: 'plan',
    description: 'Group reserved Apex Box Cricket arena for an early Sunday dawn tournament to celebrate midterm completions.',
    quote: 'Apex box cricket arena slot confirmed Sunday dawn.',
    speaker: 'Vikram Singh',
    messageId: 'msg_1774',
    searchTrigger: 'What sports facility did the group reserve?',
  },
  {
    date: 'May 16, 2026',
    month: 'May',
    title: 'Campus Internet Wi-Fi Outage',
    category: 'Hostel Life',
    tagType: 'debate',
    description: 'Entire hostel Wi-Fi collapsed during project submissions due to campus construction severing the main optical fiber line.',
    quote: 'Optical fiber line cut by backhoe excavator near campus main gate.',
    speaker: 'Rohan Mehta',
    searchTrigger: 'What caused the campus network outage?',
  },
  {
    date: 'June 07, 2026',
    month: 'June',
    title: 'Sunday Library Maintenance Notice',
    category: 'Campus Notice',
    tagType: 'announcement',
    description: 'Central library reading rooms were closed on Sunday morning due to urgent air conditioning repair work.',
    quote: 'Library air conditioning maintenance scheduled for Sunday morning.',
    speaker: 'Divya Nair',
    messageId: 'msg_2817',
    searchTrigger: 'What was the reason the library was closed on Sunday?',
  },
  {
    date: 'July 06, 2026',
    month: 'July',
    title: 'Group Vacation Budget Capped at ₹8,000',
    category: 'Trip Planning',
    tagType: 'decision',
    description: 'Priya fixed the maximum expenditure ceiling per person at 8,000 INR to keep the trip affordable for everyone.',
    quote: 'Sabhi log suno, total limit 8k fix kar di.',
    speaker: 'Priya Patel',
    messageId: 'msg_3542',
    searchTrigger: 'What is the maximum expenditure allowed per head?',
  },
  {
    date: 'July 14, 2026',
    month: 'July',
    title: 'Trip Destination Locked: Manali!',
    category: 'Trip Planning',
    tagType: 'decision',
    description: 'After heated debates between Goa, Rishikesh, and Manali, Aman officially locked Manali for the July 14-18 getaway.',
    quote: "Done bhai, Manali final. I'll book tomorrow.",
    speaker: 'Aman Sharma',
    messageId: 'msg_3769',
    searchTrigger: 'When did we finally settle on the destination?',
  },
  {
    date: 'August 14, 2026',
    month: 'August',
    title: 'Rahul Cisco Placement Treat at Barbeque Nation',
    category: 'Celebration',
    tagType: 'announcement',
    description: 'Celebrated Rahul landing his Cisco software engineer offer with a full group dinner treat at Barbeque Nation.',
    quote: 'Treat arranged inside Barbeque Nation Saturday evening.',
    speaker: 'Rohan Mehta',
    messageId: 'msg_4537',
    searchTrigger: "Which restaurant was selected to celebrate Rahul's placement offer?",
  },
  {
    date: 'August 22, 2026',
    month: 'August',
    title: 'Symposium Venue: Main Auditorium Approved',
    category: 'Innovate 2026',
    tagType: 'decision',
    description: 'Dean officially signed approval for the Main Auditorium slot for September 18 after Ananya submitted security waivers.',
    quote: 'Auditorium slot approved, booking receipt signed.',
    speaker: 'Ananya Gupta',
    messageId: 'msg_4720',
    searchTrigger: 'Where will the grand college summit take place?',
  },
  {
    date: 'August 30, 2026',
    month: 'August',
    title: 'Divya Takes Lead on Slide Deck Compilation',
    category: 'Academics',
    tagType: 'plan',
    description: 'Divya compiled the final IEEE capstone project slides and submitted the PDF deck to the project guide.',
    quote: 'Divya handles PPT compilation tonight.',
    speaker: 'Divya Nair',
    messageId: 'msg_4919',
    searchTrigger: 'Who accepted responsibility for creating the slide presentation?',
  },
];

export const TimelineView: React.FC<TimelineViewProps> = ({
  onOpenContext,
  onSearchQuery,
}) => {
  const [selectedMonth, setSelectedMonth] = useState<string>('All');

  const months = ['All', 'March', 'April', 'May', 'June', 'July', 'August'];

  const filteredMilestones =
    selectedMonth === 'All'
      ? MILESTONES
      : MILESTONES.filter((m) => m.month === selectedMonth);

  const getTagBadge = (type: Milestone['tagType']) => {
    switch (type) {
      case 'decision':
        return (
          <span className="inline-flex items-center space-x-1 rounded-md bg-emerald-50 border border-emerald-200 px-2 py-0.5 text-[10px] font-bold text-emerald-800 uppercase tracking-wider">
            <CheckCircle2 className="h-2.5 w-2.5" />
            <span>Decision</span>
          </span>
        );
      case 'debate':
        return (
          <span className="inline-flex items-center space-x-1 rounded-md bg-rose-50 border border-rose-200 px-2 py-0.5 text-[10px] font-bold text-rose-800 uppercase tracking-wider">
            <Flame className="h-2.5 w-2.5" />
            <span>Debate</span>
          </span>
        );
      case 'plan':
        return (
          <span className="inline-flex items-center space-x-1 rounded-md bg-indigo-50 border border-indigo-200 px-2 py-0.5 text-[10px] font-bold text-indigo-800 uppercase tracking-wider">
            <Compass className="h-2.5 w-2.5" />
            <span>Plan</span>
          </span>
        );
      case 'announcement':
        return (
          <span className="inline-flex items-center space-x-1 rounded-md bg-amber-50 border border-amber-200 px-2 py-0.5 text-[10px] font-bold text-amber-800 uppercase tracking-wider">
            <Sparkles className="h-2.5 w-2.5" />
            <span>Milestone</span>
          </span>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Section 11 Header */}
      <div className="text-center pt-2">
        <div className="inline-flex items-center space-x-2 rounded-full border border-indigo-100 bg-indigo-50/60 px-3.5 py-1 text-xs font-medium text-indigo-800 shadow-2xs mb-3">
          <Calendar className="h-3.5 w-3.5 text-indigo-600" />
          <span>Chronological Group Chat Memory (March – Sept 2026)</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Conversation Timeline
        </h2>
        <p className="mt-2 text-xs sm:text-sm text-slate-600 max-w-lg mx-auto leading-relaxed">
          Browse your group chat archives chronologically or by major milestones.
        </p>

        {/* Month Quick Jumps Scrubber */}
        <div className="mt-5 flex items-center justify-center space-x-1.5 overflow-x-auto pb-1">
          {months.map((m) => (
            <motion.button
              key={m}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedMonth(m)}
              className={`rounded-xl px-3 py-1.5 text-xs font-medium transition-all shadow-2xs cursor-pointer ${
                selectedMonth === m
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'bg-white text-slate-600 border border-slate-200/90 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              {m}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Timeline track */}
      <div className="relative pl-6 sm:pl-8 border-l-2 border-slate-200 space-y-6 pt-4">
        {filteredMilestones.map((m, idx) => (
          <div key={idx} className="relative group">
            {/* Dot on line */}
            <div className="absolute -left-[31px] sm:-left-[39px] top-2 flex h-5 w-5 items-center justify-center rounded-full bg-white border-2 border-indigo-600 shadow-2xs">
              <div className="h-1.5 w-1.5 rounded-full bg-indigo-600" />
            </div>

            {/* Card with Framer Motion entrance and hover lift */}
            <motion.div
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: Math.min(idx * 0.04, 0.3) }}
              whileHover={{ y: -3, transition: { duration: 0.15 } }}
              onClick={() => m.messageId && onOpenContext(m.messageId)}
              className="rounded-2xl bg-slate-900/95 border border-slate-800/90 p-5 shadow-md shadow-slate-950/30 text-slate-100 hover:border-slate-700 hover:shadow-lg transition-all cursor-pointer"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-slate-800/80">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono font-bold text-indigo-400">
                    {m.date}
                  </span>
                  <span className="text-slate-600">•</span>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-300 bg-slate-800 border border-slate-700/60 px-2 py-0.2 rounded">
                    {m.category}
                  </span>
                  {getTagBadge(m.tagType)}
                </div>
                <span className="text-xs text-slate-400">
                  By <strong className="text-slate-200 font-semibold">{m.speaker}</strong>
                </span>
              </div>

              <h3 className="text-sm sm:text-base font-bold text-white mt-2.5">
                {m.title}
              </h3>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                {m.description}
              </p>

              {/* Exact Quote */}
              <div className="my-3 rounded-xl bg-slate-950/70 border border-slate-800/90 p-3 border-l-2 border-indigo-500">
                <p className="text-xs font-medium text-slate-200 italic">
                  "{m.quote}"
                </p>
              </div>

              {/* Action buttons */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80" onClick={(e) => e.stopPropagation()}>
                <motion.button
                  whileHover={{ x: 2 }}
                  onClick={() => onSearchQuery(m.searchTrigger)}
                  className="inline-flex items-center space-x-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors cursor-pointer"
                >
                  <span>Search: &ldquo;{m.searchTrigger}&rdquo;</span>
                  <ArrowRight className="h-3 w-3" />
                </motion.button>

                {m.messageId && (
                  <motion.button
                    whileHover={{ scale: 1.04 }}
                    whileTap={{ scale: 0.96 }}
                    onClick={() => onOpenContext(m.messageId!)}
                    className="inline-flex items-center space-x-1 text-xs text-slate-400 hover:text-slate-200 transition-colors font-medium cursor-pointer"
                  >
                    <MessageSquare className="h-3.5 w-3.5" />
                    <span>View Context</span>
                  </motion.button>
                )}
              </div>
            </motion.div>
          </div>
        ))}
      </div>
    </div>
  );
};

