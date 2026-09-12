import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Search, Layers, MessageSquare, Check, Sparkles } from 'lucide-react';

interface LoadingStagesProps {
  query: string;
}

const STAGES = [
  {
    id: 1,
    title: 'Understanding your question',
    subtitle: 'Parsing semantic intent, Hinglish terms & entities',
    icon: Brain,
  },
  {
    id: 2,
    title: 'Finding relevant conversations',
    subtitle: 'Scanning 5,200+ message embeddings & BM25 inverted index',
    icon: Search,
  },
  {
    id: 3,
    title: 'Ranking semantic matches',
    subtitle: 'Applying multi-signal weights & agreement boost',
    icon: Layers,
  },
  {
    id: 4,
    title: 'Reconstructing context',
    subtitle: 'Assembling conversational thread & grounded citations',
    icon: MessageSquare,
  },
];

export const LoadingStages: React.FC<LoadingStagesProps> = ({ query }) => {
  const [currentStage, setCurrentStage] = useState(1);

  useEffect(() => {
    const timer1 = setTimeout(() => setCurrentStage(2), 220);
    const timer2 = setTimeout(() => setCurrentStage(3), 500);
    const timer3 = setTimeout(() => setCurrentStage(4), 850);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
      className="relative mx-auto max-w-2xl rounded-2xl border border-indigo-100/80 bg-white/95 p-6 shadow-md shadow-indigo-100/30 backdrop-blur-sm my-6 overflow-hidden"
    >
      {/* Animated Top Progress Line */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-slate-100 overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-indigo-500 via-violet-500 to-sky-400"
          initial={{ width: '20%' }}
          animate={{ width: `${(currentStage / 4) * 100}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        />
      </div>

      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div className="flex items-center space-x-2.5">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 4, ease: 'linear' }}
            className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 shadow-2xs"
          >
            <Sparkles className="h-4 w-4 text-indigo-600" />
          </motion.div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Retrieval Pipeline in Progress
            </span>
            <p className="text-xs text-slate-800 font-medium truncate max-w-sm">
              &ldquo;{query}&rdquo;
            </p>
          </div>
        </div>

        <motion.span
          key={currentStage}
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          className="rounded-full bg-indigo-50 border border-indigo-100 px-2.5 py-0.5 text-[11px] font-mono font-medium text-indigo-700 shadow-2xs"
        >
          Stage {currentStage} of 4
        </motion.span>
      </div>

      <div className="mt-5 space-y-3">
        {STAGES.map((st, idx) => {
          const isDone = st.id < currentStage;
          const isCurrent = st.id === currentStage;
          const Icon = st.icon;

          return (
            <motion.div
              key={st.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.08, duration: 0.25 }}
              className={`flex items-center justify-between p-3 rounded-xl border transition-all duration-200 ${
                isCurrent
                  ? 'bg-indigo-50/70 border-indigo-200 shadow-xs'
                  : isDone
                  ? 'bg-slate-50/50 border-slate-200/60'
                  : 'bg-transparent border-transparent opacity-40'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-lg text-xs font-semibold transition-colors ${
                    isDone
                      ? 'bg-emerald-100 text-emerald-700'
                      : isCurrent
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-400'
                  }`}
                >
                  <AnimatePresence mode="wait">
                    {isDone ? (
                      <motion.div
                        key="check"
                        initial={{ scale: 0, rotate: -45 }}
                        animate={{ scale: 1, rotate: 0 }}
                        transition={{ type: 'spring', stiffness: 450, damping: 20 }}
                      >
                        <Check className="h-4 w-4 stroke-[3]" />
                      </motion.div>
                    ) : (
                      <motion.div
                        key="icon"
                        initial={{ scale: 0.8 }}
                        animate={{ scale: 1 }}
                      >
                        <Icon className="h-4 w-4" />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
                <div>
                  <h4
                    className={`text-xs font-semibold ${
                      isCurrent ? 'text-indigo-950' : isDone ? 'text-slate-800' : 'text-slate-500'
                    }`}
                  >
                    {st.title}
                  </h4>
                  <p className="text-[11px] text-slate-500">{st.subtitle}</p>
                </div>
              </div>

              {isCurrent && (
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-indigo-600" />
                </span>
              )}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};
