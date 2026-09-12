import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SynthesizedAnswer } from '../types';
import { getExportPdfUrl, getExportImageUrl } from '../api';
import {
  ShieldCheck,
  Check,
  Copy,
  ArrowRight,
  Clock,
  FileText,
  Image as ImageIcon,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Info,
} from 'lucide-react';

interface AnswerBoxProps {
  answer: SynthesizedAnswer;
  query: string;
  latencyMs: number;
  onOpenContext: (messageId: string) => void;
}

export const AnswerBox: React.FC<AnswerBoxProps> = ({
  answer,
  query,
  latencyMs,
  onOpenContext,
}) => {
  const [copied, setCopied] = useState(false);
  const [showSupporting, setShowSupporting] = useState(false);

  const {
    direct_answer,
    summary,
    confidence,
    key_data_points,
    primary_quote,
    primary_source_id,
    primary_author,
    primary_timestamp,
    consensus_status,
    supporting_points,
  } = answer;

  const formattedDate = new Date(primary_timestamp).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  const handleCopy = () => {
    const textToCopy = `Q: ${query}\nAnswer: ${direct_answer}\nSource: "${primary_quote}" — ${primary_author} (${primary_source_id}, ${formattedDate})\nStatus: ${consensus_status}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper to render markdown bold in answer
  const renderFormattedText = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={index} className="text-indigo-400 font-bold">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/95 p-5 sm:p-6 shadow-xl shadow-slate-900/20 text-slate-100 backdrop-blur-sm"
    >
      {/* Radiant top brand gradient bar */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-violet-500 to-indigo-400" />

      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3.5 border-b border-slate-800/80">
        <div className="flex items-center space-x-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 shadow-inner">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 font-mono">
                Synthesized Direct Answer
              </span>
              <motion.span
                animate={{ opacity: [0.85, 1, 0.85] }}
                transition={{ repeat: Infinity, duration: 2.5 }}
                className="rounded-full bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.2 text-[10px] font-bold text-emerald-400 font-mono"
              >
                {(confidence * 100).toFixed(0)}% Grounded
              </motion.span>
            </div>
            <p className="text-[11px] text-slate-400">
              Extracted from archive • Grounded in message #{primary_source_id}
            </p>
          </div>
        </div>

        {/* Action badges */}
        <div className="flex items-center space-x-2">
          <span className="hidden sm:inline-flex items-center space-x-1 rounded-md bg-slate-800/80 border border-slate-700/80 px-2 py-0.5 text-xs font-medium text-slate-300 font-mono">
            <Clock className="h-3 w-3 text-slate-400" />
            <span>{latencyMs.toFixed(1)}ms</span>
          </span>

          <span className="rounded-md bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 text-xs font-semibold text-amber-300">
            {consensus_status}
          </span>

          <motion.a
            href={getExportPdfUrl({ messageId: primary_source_id, query, directAnswer: direct_answer })}
            download
            target="_blank"
            rel="noreferrer"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="hidden sm:inline-flex items-center space-x-1.5 rounded-lg bg-slate-800/90 hover:bg-slate-700 border border-slate-700/80 px-2.5 py-1 text-xs font-medium text-slate-200 hover:text-white transition-colors shadow-2xs"
            title="Download full chat conversation as PDF"
          >
            <FileText className="h-3.5 w-3.5 text-indigo-400" />
            <span>PDF</span>
          </motion.a>

          <motion.a
            href={getExportImageUrl({ messageId: primary_source_id, query, directAnswer: direct_answer })}
            download
            target="_blank"
            rel="noreferrer"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="hidden sm:inline-flex items-center space-x-1.5 rounded-lg bg-slate-800/90 hover:bg-slate-700 border border-slate-700/80 px-2.5 py-1 text-xs font-medium text-slate-200 hover:text-white transition-colors shadow-2xs"
            title="Download full chat conversation as Picture (PNG)"
          >
            <ImageIcon className="h-3.5 w-3.5 text-violet-400" />
            <span>Image</span>
          </motion.a>

          <motion.button
            onClick={handleCopy}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center space-x-1.5 rounded-lg bg-slate-800/90 hover:bg-slate-700 border border-slate-700/80 px-2.5 py-1 text-xs font-medium text-slate-200 hover:text-white transition-colors shadow-2xs"
            title="Copy answer and citation"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-semibold">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-slate-400" />
                <span>Copy</span>
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* Main Answer Content */}
      <div className="py-3.5">
        <h3 className="text-base sm:text-lg text-white font-medium leading-relaxed">
          {renderFormattedText(direct_answer)}
        </h3>

        {summary && summary !== direct_answer && (
          <p className="mt-2 text-xs sm:text-sm text-slate-300 leading-relaxed">
            {summary}
          </p>
        )}
      </div>

      {/* Structured Key Data Points Grid */}
      {key_data_points && key_data_points.length > 0 && (
        <div className="my-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {key_data_points.map((dp, idx) => (
            <motion.div
              key={idx}
              whileHover={{ y: -2, transition: { duration: 0.15 } }}
              className="flex flex-col rounded-xl bg-slate-950/60 border border-slate-800/90 p-2.5 shadow-2xs"
            >
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                {dp.label}
              </span>
              <span className="mt-0.5 text-xs font-semibold text-slate-100 truncate">
                {dp.value}
              </span>
            </motion.div>
          ))}
        </div>
      )}

      {/* Primary Quoted Grounding Box */}
      <div className="mt-3 rounded-xl bg-slate-950/70 border border-slate-800/90 p-3.5 sm:p-4">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
          <div className="flex items-center space-x-2">
            <div className="h-5 w-5 rounded-full bg-indigo-600 flex items-center justify-center text-[10px] font-bold text-white shadow-2xs">
              {primary_author.charAt(0)}
            </div>
            <span className="font-semibold text-slate-200">{primary_author}</span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400">{formattedDate}</span>
            <span className="text-slate-600">•</span>
            <code className="text-[11px] text-indigo-400 font-mono bg-indigo-500/10 px-1.5 py-0.2 rounded border border-indigo-500/20">
              #{primary_source_id}
            </code>
          </div>

          <motion.button
            onClick={() => onOpenContext(primary_source_id)}
            whileHover={{ x: 3 }}
            className="inline-flex items-center space-x-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            <span>Jump to Context</span>
            <ArrowRight className="h-3 w-3" />
          </motion.button>
        </div>

        <p className="text-xs sm:text-sm font-medium text-slate-200 italic border-l-2 border-indigo-500 pl-3 py-0.5">
          "{primary_quote}"
        </p>
      </div>

      {/* Supporting context collapsible */}
      {supporting_points && supporting_points.length > 0 && (
        <div className="mt-3 pt-2.5 border-t border-slate-800/80">
          <button
            onClick={() => setShowSupporting(!showSupporting)}
            className="flex items-center justify-between w-full text-left text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors"
          >
            <span className="flex items-center space-x-1.5">
              <Info className="h-3.5 w-3.5 text-slate-400" />
              <span>Corroborating Chat Evidence ({supporting_points.length} statements)</span>
            </span>
            {showSupporting ? (
              <ChevronUp className="h-3.5 w-3.5 text-slate-400" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
            )}
          </button>

          <AnimatePresence>
            {showSupporting && (
              <motion.ul
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="mt-2 space-y-1 text-xs text-slate-300 pl-5 list-disc overflow-hidden"
              >
                {supporting_points.map((pt, i) => (
                  <li key={i} className="leading-relaxed">
                    {pt}
                  </li>
                ))}
              </motion.ul>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
};


