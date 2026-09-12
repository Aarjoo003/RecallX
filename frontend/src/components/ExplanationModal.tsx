import React from 'react';
import { motion } from 'framer-motion';
import { SearchResult } from '../types';
import { X, ShieldCheck, CheckCircle2, Scale, Clock, Hash } from 'lucide-react';

interface ExplanationModalProps {
  result: SearchResult;
  query: string;
  onClose: () => void;
}

export const ExplanationModal: React.FC<ExplanationModalProps> = ({
  result,
  query,
  onClose,
}) => {
  const {
    text,
    participant_name,
    timestamp,
    final_score,
    semantic_score,
    lexical_score,
    person_score,
    time_score,
    decision_score,
    word_overlap,
    is_zero_word_match,
    explanation,
    message_id,
    thread_id,
  } = result;

  const formattedTime = new Date(timestamp).toLocaleString('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.15 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 16 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 16 }}
        transition={{ type: 'spring', duration: 0.25, bounce: 0.1 }}
        className="relative w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl border border-slate-200 max-h-[90vh] overflow-y-auto text-slate-800"
      >
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center space-x-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600">
              <Scale className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-bold text-slate-900">Scoring Signal Diagnostic</h3>
              <p className="text-xs text-slate-500">
                Deterministic multi-signal retrieval decomposition for #{message_id}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Target Message Snippet */}
        <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-semibold text-slate-900">{participant_name}</span>
            <div className="flex items-center space-x-2">
              <span>{formattedTime}</span>
              <span className="text-slate-300">•</span>
              <span className="font-mono text-emerald-600 font-semibold">#{message_id}</span>
            </div>
          </div>
          <p className="text-sm font-medium text-slate-900 italic">"{text}"</p>
        </div>

        {/* Zero Word Overlap Proof */}
        {is_zero_word_match && (
          <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50/60 p-4">
            <div className="flex items-start space-x-3">
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700">
                <ShieldCheck className="h-4 w-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800">
                  Mathematical Verification: 0 Word Overlap
                </h4>
                <p className="mt-1 text-xs text-slate-700 leading-relaxed">
                  The query <code className="bg-white px-1.5 py-0.5 rounded text-emerald-800 border border-emerald-200 font-mono">"{query}"</code> and 
                  the target message share <strong className="text-emerald-700 font-bold underline">exactly 0 words</strong> in common.
                </p>
                <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                  Traditional keyword search (grep, standard BM25) fails completely here. RecallX successfully retrieved this using dense semantic embeddings + thread consensus alignment.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Multi-Signal Score Breakdown */}
        <div className="mt-5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
            Scoring Signal Decomposition
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Semantic Score */}
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-700">Dense Semantic Vector</span>
                <span className="font-mono font-bold text-emerald-700">
                  {(semantic_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-1.5">
                <div
                  className="bg-emerald-600 h-1.5 rounded-full"
                  style={{ width: `${Math.min(100, Math.max(0, semantic_score * 100))}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5">
                Cosine similarity across 384 dimensions.
              </p>
            </div>

            {/* Lexical BM25 */}
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-700">Lexical BM25 Score</span>
                <span className="font-mono font-bold text-sky-700">
                  {lexical_score > 0 ? lexical_score.toFixed(1) : '0.0'}
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-1.5">
                <div
                  className="bg-sky-600 h-1.5 rounded-full"
                  style={{ width: `${Math.min(100, (lexical_score / 20) * 100)}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5">
                Inverted index token overlap: {word_overlap} shared words.
              </p>
            </div>

            {/* Person Match */}
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-700">Participant Entity Match</span>
                <span className="font-mono font-bold text-indigo-700">
                  {(person_score * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-1.5">
                <div
                  className="bg-indigo-600 h-1.5 rounded-full"
                  style={{ width: `${person_score * 100}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5">
                Status: {explanation.person_match}
              </p>
            </div>

            {/* Decision Consensus */}
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-700">Decision Consensus Signal</span>
                <span className="font-mono font-bold text-amber-700">
                  {(decision_score * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-1.5">
                <div
                  className="bg-amber-600 h-1.5 rounded-full"
                  style={{ width: `${decision_score * 100}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5">
                Signal: {explanation.decision_signal}
              </p>
            </div>
          </div>
        </div>

        {/* Overall Conclusion Summary */}
        <div className="mt-5 p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Composite Retrieval Verdict
            </span>
            <span className="font-mono font-bold text-emerald-700 text-sm">
              {(final_score * 100).toFixed(1)}% Match
            </span>
          </div>
          <p className="text-xs text-slate-700 leading-relaxed">
            {explanation.summary}
          </p>
        </div>

        {/* Close Button */}
        <div className="mt-6 flex justify-end">
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={onClose}
            className="rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-200 px-5 py-2 text-xs font-semibold text-slate-700 transition-colors cursor-pointer"
          >
            Close Diagnostic
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  );
};
