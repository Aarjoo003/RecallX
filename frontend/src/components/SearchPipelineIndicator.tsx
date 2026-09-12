import React from 'react';
import { SearchResponse } from '../types';
import { Zap, Target, User, Calendar, Tag, CheckCircle2, Clock } from 'lucide-react';

interface SearchPipelineIndicatorProps {
  response: SearchResponse;
}

export const SearchPipelineIndicator: React.FC<SearchPipelineIndicatorProps> = ({ response }) => {
  const { query_type, interpreted_filters, search_latency_ms, total_found } = response;

  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-2xs">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        {/* Left: Execution stats */}
        <div className="flex items-center space-x-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
            <Zap className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-slate-900">
                Hybrid Retrieval Pipeline
              </span>
              <span className="rounded-full bg-slate-100 border border-slate-200 px-2 py-0.5 text-[11px] font-mono font-medium text-slate-700 flex items-center space-x-1">
                <Clock className="h-2.5 w-2.5 text-slate-400" />
                <span>{search_latency_ms.toFixed(1)} ms</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-500">
              {total_found} messages ranked • Dense Cosine (384d) + Inverted Lexical (FTS5 BM25)
            </p>
          </div>
        </div>

        {/* Right: Clean Neutral Interpreted Query Chips */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          {/* Query Type / Semantic chip */}
          <span className="rounded-lg bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 border border-slate-200/90 flex items-center space-x-1.5 shadow-2xs">
            <Target className="h-3 w-3 text-slate-400" />
            <span className="capitalize">{query_type.replace('_', ' ')}</span>
          </span>

          {/* Participant chip */}
          {interpreted_filters?.participant_name && (
            <span className="rounded-lg bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 border border-slate-200/90 flex items-center space-x-1.5 shadow-2xs">
              <User className="h-3 w-3 text-slate-400" />
              <span>Person: {interpreted_filters.participant_name}</span>
            </span>
          )}

          {/* Time chip */}
          {interpreted_filters?.date_range_label && (
            <span className="rounded-lg bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 border border-slate-200/90 flex items-center space-x-1.5 shadow-2xs">
              <Calendar className="h-3 w-3 text-slate-400" />
              <span>Time: {interpreted_filters.date_range_label}</span>
            </span>
          )}

          {/* Decision Intent chip */}
          {interpreted_filters?.is_decision_intent && (
            <span className="rounded-lg bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 border border-slate-200/90 flex items-center space-x-1.5 shadow-2xs">
              <CheckCircle2 className="h-3 w-3 text-emerald-600" />
              <span>Decision</span>
            </span>
          )}

          {/* Detected Topics chip */}
          {interpreted_filters?.detected_topics && interpreted_filters.detected_topics.length > 0 && (
            <span className="rounded-lg bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 border border-slate-200/90 flex items-center space-x-1.5 shadow-2xs">
              <Tag className="h-3 w-3 text-slate-400" />
              <span>Topic: {interpreted_filters.detected_topics.join(', ')}</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

