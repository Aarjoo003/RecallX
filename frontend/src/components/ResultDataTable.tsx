import React from 'react';
import { SearchResult } from '../types';
import { MessageSquare, HelpCircle, ShieldCheck, Clock, ArrowUpRight } from 'lucide-react';

interface ResultDataTableProps {
  results: SearchResult[];
  onOpenContext: (messageId: string, threadId: string) => void;
  onOpenExplanation: (result: SearchResult) => void;
}

export const ResultDataTable: React.FC<ResultDataTableProps> = ({
  results,
  onOpenContext,
  onOpenExplanation,
}) => {
  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-200/80 bg-white shadow-sm">
      <table className="w-full text-left text-xs text-slate-700">
        <thead className="bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-200">
          <tr>
            <th className="py-3 px-3">Rank</th>
            <th className="py-3 px-3">Message ID</th>
            <th className="py-3 px-4">Participant</th>
            <th className="py-3 px-4">Message Content</th>
            <th className="py-3 px-3">Final Match</th>
            <th className="py-3 px-3">Dense Cosine</th>
            <th className="py-3 px-3">BM25</th>
            <th className="py-3 px-3">Overlap</th>
            <th className="py-3 px-3">Timestamp</th>
            <th className="py-3 px-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 font-mono">
          {results.map((res, index) => {
            const isZero = res.is_zero_word_match;
            const formattedTime = new Date(res.timestamp).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            });

            return (
              <tr
                key={res.message_id}
                className="hover:bg-slate-50/80 transition-colors font-sans"
              >
                <td className="py-3 px-3 font-mono font-bold text-slate-400">
                  #{index + 1}
                </td>
                <td className="py-3 px-3 font-mono text-indigo-600 font-semibold text-xs">
                  {res.message_id}
                </td>
                <td className="py-3 px-4 whitespace-nowrap">
                  <div className="font-semibold text-slate-900">{res.participant_name}</div>
                  <div className="text-[10px] text-slate-500">#{res.thread_id.replace('thread_', '')}</div>
                </td>
                <td className="py-3 px-4 max-w-xs sm:max-w-md truncate text-slate-800" title={res.text}>
                  "{res.text}"
                </td>
                <td className="py-3 px-3 font-mono font-bold text-slate-900">
                  {(res.final_score * 100).toFixed(0)}%
                </td>
                <td className="py-3 px-3 font-mono text-slate-600">
                  {(res.semantic_score * 100).toFixed(0)}%
                </td>
                <td className="py-3 px-3 font-mono text-slate-600">
                  {res.lexical_score > 0 ? res.lexical_score.toFixed(1) : '0.0'}
                </td>
                <td className="py-3 px-3 whitespace-nowrap">
                  {isZero ? (
                    <span className="inline-flex items-center rounded-md bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 text-[10px] font-bold text-emerald-700 font-mono">
                      0 words
                    </span>
                  ) : (
                    <span className="text-slate-500 font-mono text-xs">{res.word_overlap}</span>
                  )}
                </td>
                <td className="py-3 px-3 whitespace-nowrap text-slate-500 text-[11px]">
                  {formattedTime}
                </td>
                <td className="py-3 px-3 text-right whitespace-nowrap">
                  <div className="inline-flex items-center space-x-1.5">
                    <button
                      onClick={() => onOpenExplanation(res)}
                      className="p-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 transition-colors"
                      title="Why this rank?"
                    >
                      <HelpCircle className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => onOpenContext(res.message_id, res.thread_id)}
                      className="p-1 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 transition-colors"
                      title="View Conversation"
                    >
                      <MessageSquare className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
