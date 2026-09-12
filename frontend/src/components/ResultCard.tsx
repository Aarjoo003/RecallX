import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SearchResult } from '../types';
import { getExportPdfUrl, getExportImageUrl } from '../api';
import {
  ShieldCheck,
  MessageSquare,
  HelpCircle,
  ChevronRight,
  Clock,
  Copy,
  Check,
  Hash,
  FileText,
  Image as ImageIcon,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Brain,
} from 'lucide-react';

interface ResultCardProps {
  result: SearchResult;
  rank: number;
  query: string;
  onOpenContext: (messageId: string, threadId: string) => void;
  onOpenExplanation: (result: SearchResult) => void;
  isBestMatch?: boolean;
}

export const ResultCard: React.FC<ResultCardProps> = ({
  result,
  rank,
  query,
  onOpenContext,
  onOpenExplanation,
  isBestMatch = false,
}) => {
  const [copied, setCopied] = useState(false);
  const [showZeroWordBreakdown, setShowZeroWordBreakdown] = useState(false);

  const {
    message_id,
    participant_name,
    timestamp,
    text,
    thread_id,
    final_score,
    semantic_score,
    lexical_score,
    word_overlap,
    is_zero_word_match,
    explanation,
    context,
  } = result;

  const dateObj = new Date(timestamp);
  const formattedTime = dateObj.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

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

  const handleCopyText = () => {
    navigator.clipboard.writeText(`"${text}" — ${participant_name} (${formattedTime}, #${message_id})`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const cleanThreadName = thread_id.replace('thread_', '').replace('_', ' ');

  // Extract query and message tokens for zero-word proof display
  const queryTokens = query
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter((w) => w.length > 1);

  const messageTokens = text
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter((w) => w.length > 1);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: Math.min(rank * 0.04, 0.3) }}
      whileHover={{ y: -3, transition: { duration: 0.15 } }}
      className={`group relative rounded-2xl bg-white border transition-all ${
        isBestMatch
          ? 'border-indigo-300 shadow-md shadow-indigo-100/50 p-6 ring-1 ring-indigo-500/10'
          : 'border-slate-200/90 shadow-2xs hover:border-slate-300 hover:shadow-sm p-4 sm:p-5'
      }`}
    >
      {/* Best Match Top Ribbon */}
      {isBestMatch && (
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-indigo-100/70">
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center space-x-1 rounded-full bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 text-[11px] font-bold text-indigo-700 uppercase tracking-wider">
              <Sparkles className="h-3 w-3 text-indigo-600" />
              <span>Best Match • Rank #1</span>
            </span>
            <span className="text-[11px] text-slate-500 hidden sm:inline">
              Highest scoring conversational message in corpus
            </span>
          </div>

          <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50/60 px-2 py-0.5 rounded border border-indigo-100">
            {(final_score * 100).toFixed(0)}% Relevance
          </span>
        </div>
      )}

      {/* Section 9: Dedicated Zero-Word Match Visual Moment Banner */}
      {is_zero_word_match && (
        <div className="mb-4 rounded-xl bg-gradient-to-r from-emerald-50 via-teal-50/50 to-indigo-50/40 border border-emerald-200/90 p-3.5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center space-x-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-2xs">
                <ShieldCheck className="h-3.5 w-3.5 stroke-[2.5]" />
              </div>
              <div>
                <span className="text-xs font-extrabold uppercase tracking-wider text-emerald-900 font-mono">
                  0 SHARED WORDS • PURE SEMANTIC RETRIEVAL
                </span>
                <p className="text-[11px] text-emerald-700">
                  Retrieved strictly by conceptual meaning, not keyword overlap
                </p>
              </div>
            </div>

            <button
              onClick={() => setShowZeroWordBreakdown(!showZeroWordBreakdown)}
              className="inline-flex items-center space-x-1 rounded-lg bg-white/90 hover:bg-white border border-emerald-200 px-2.5 py-1 text-xs font-semibold text-emerald-800 transition-colors shadow-2xs"
            >
              <Brain className="h-3.5 w-3.5 text-emerald-600" />
              <span>Semantic Proof</span>
              {showZeroWordBreakdown ? (
                <ChevronUp className="h-3 w-3 text-emerald-600" />
              ) : (
                <ChevronDown className="h-3 w-3 text-emerald-600" />
              )}
            </button>
          </div>

          {/* Expandable Zero-Word Proof Breakdown */}
          <AnimatePresence>
            {showZeroWordBreakdown && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="mt-3 pt-3 border-t border-emerald-200/70 text-xs space-y-2 text-slate-700 font-sans overflow-hidden"
              >
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                  <div className="rounded-lg bg-white/80 p-2 border border-emerald-100">
                    <span className="font-mono font-bold text-slate-500 uppercase block mb-1">
                      Query Tokens
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {queryTokens.map((tok, i) => (
                        <span
                          key={i}
                          className="font-mono px-1.5 py-0.2 rounded bg-slate-100 text-slate-700 text-[10px]"
                        >
                          {tok}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-lg bg-white/80 p-2 border border-emerald-100">
                    <span className="font-mono font-bold text-slate-500 uppercase block mb-1">
                      Message Tokens
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {messageTokens.slice(0, 10).map((tok, i) => (
                        <span
                          key={i}
                          className="font-mono px-1.5 py-0.2 rounded bg-slate-100 text-slate-700 text-[10px]"
                        >
                          {tok}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between gap-2 pt-1 font-mono text-[11px] text-slate-600">
                  <div className="flex items-center space-x-3">
                    <span>
                      Lexical Overlap: <strong className="text-emerald-800">0 words</strong>
                    </span>
                    <span>•</span>
                    <span>
                      Dense Cosine Score:{' '}
                      <strong className="text-emerald-800">
                        {(semantic_score * 100).toFixed(1)}%
                      </strong>
                    </span>
                  </div>
                </div>

                {(explanation?.semantic_relevance || explanation?.summary) && (
                  <p className="text-[11px] text-slate-600 italic bg-white/60 p-2 rounded-lg border border-emerald-100/80">
                    <strong className="text-emerald-900 not-italic font-semibold">Why it matched: </strong>
                    {explanation.semantic_relevance || explanation.summary}
                  </p>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Card Header: User, Time, Thread & Match Score */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2.5">
          {!isBestMatch && (
            <span className="flex h-5 w-5 items-center justify-center rounded-md bg-slate-100 text-[11px] font-mono font-bold text-slate-600">
              #{rank}
            </span>
          )}

          <div
            className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold shadow-2xs ${getAvatarColor(
              participant_name
            )}`}
          >
            {participant_name.charAt(0)}
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs sm:text-sm font-semibold text-slate-900">
                {participant_name}
              </span>
              <span className="inline-flex items-center space-x-0.5 rounded-md bg-slate-100 px-1.5 py-0.2 text-[10px] font-mono text-slate-600">
                <Hash className="h-2.5 w-2.5 text-slate-400" />
                <span>{cleanThreadName}</span>
              </span>
            </div>

            <div className="flex items-center space-x-1.5 text-[11px] text-slate-500 mt-0.5">
              <Clock className="h-3 w-3 text-slate-400" />
              <span>{formattedTime}</span>
              <span className="text-slate-300">•</span>
              <code className="text-[10px] text-slate-600 font-mono font-medium">#{message_id}</code>
            </div>
          </div>
        </div>

        {/* Right Match Score */}
        <div className="flex items-center space-x-2">
          {!isBestMatch && (
            <span className="rounded-md bg-slate-100 border border-slate-200 px-2 py-0.5 text-xs font-mono font-semibold text-slate-700">
              {(final_score * 100).toFixed(0)}% Match
            </span>
          )}
        </div>
      </div>

      {/* Main Message Chat Bubble */}
      <div className="my-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 p-3.5 sm:p-4 relative group/bubble">
        <p className={`${isBestMatch ? 'text-base' : 'text-sm'} text-slate-900 font-medium leading-relaxed`}>
          "{text}"
        </p>

        <button
          onClick={handleCopyText}
          className="absolute top-2.5 right-2.5 p-1.5 rounded-lg bg-white border border-slate-200 text-slate-500 hover:text-slate-800 opacity-0 group-hover/bubble:opacity-100 transition-opacity shadow-2xs"
          title="Copy message text"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* Surrounding Context Snippet Preview */}
      {context && context.length > 1 && (
        <div className="mb-3 rounded-xl bg-slate-50/50 border border-slate-200/60 p-2.5 text-xs space-y-1">
          <div className="flex items-center space-x-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            <MessageSquare className="h-3 w-3" />
            <span>Conversation Snippet</span>
          </div>
          {context.slice(0, 2).map((cm) => (
            <div
              key={cm.id}
              className={`flex items-start space-x-2 truncate text-[11px] ${
                cm.is_target ? 'font-semibold text-indigo-900' : 'text-slate-600'
              }`}
            >
              <span className="text-slate-400 shrink-0 font-medium">
                {cm.participant_name.split(' ')[0]}:
              </span>
              <span className="truncate">{cm.text}</span>
            </div>
          ))}
        </div>
      )}

      {/* Bottom Action Footer */}
      <div className="flex flex-wrap items-center justify-between gap-2.5 pt-2 border-t border-slate-100">
        <div className="flex items-center space-x-1.5 text-[11px] font-mono text-slate-500">
          <span className="rounded bg-slate-100 px-1.5 py-0.5">
            Dense: {(semantic_score * 100).toFixed(0)}%
          </span>
          <span className="rounded bg-slate-100 px-1.5 py-0.5">
            BM25: {lexical_score > 0 ? lexical_score.toFixed(1) : '0.0'}
          </span>
          <span className="rounded bg-slate-100 px-1.5 py-0.5">
            Overlap: {word_overlap}w
          </span>
        </div>

        <div className="flex items-center space-x-1.5">
          <motion.a
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            href={getExportPdfUrl({ threadId: thread_id, messageId: message_id, query })}
            download
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center space-x-1 rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
            title="Download full chat as PDF"
          >
            <FileText className="h-3 w-3 text-indigo-600" />
            <span>PDF</span>
          </motion.a>

          <motion.a
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            href={getExportImageUrl({ threadId: thread_id, messageId: message_id, query })}
            download
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center space-x-1 rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
            title="Download full chat as Picture (PNG)"
          >
            <ImageIcon className="h-3 w-3 text-violet-600" />
            <span>Image</span>
          </motion.a>

          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            type="button"
            onClick={() => onOpenExplanation(result)}
            className="inline-flex items-center space-x-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
          >
            <HelpCircle className="h-3 w-3 text-slate-400" />
            <span>Explain Match</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            type="button"
            onClick={() => onOpenContext(message_id, thread_id)}
            className="inline-flex items-center space-x-1 rounded-lg bg-indigo-50 border border-indigo-200 px-3 py-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 transition-colors shadow-2xs cursor-pointer"
          >
            <MessageSquare className="h-3 w-3" />
            <span>View Context</span>
            <ChevronRight className="h-3 w-3" />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

