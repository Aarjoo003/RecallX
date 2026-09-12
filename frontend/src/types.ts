export interface ContextMessage {
  id: string;
  participant_id: string;
  participant_name: string;
  timestamp: string;
  text: string;
  thread_id?: string;
  is_target?: boolean;
  is_forwarded?: boolean;
  is_media?: boolean;
}

export interface Explanation {
  semantic_relevance: string;
  person_match: string;
  time_match: string;
  decision_signal: string;
  summary: string;
}

export interface SearchResult {
  message_id: string;
  participant_id: string;
  participant_name: string;
  timestamp: string;
  text: string;
  thread_id: string;
  semantic_score: number;
  lexical_score: number;
  person_score: number;
  time_score: number;
  decision_score: number;
  final_score: number;
  word_overlap: number;
  is_zero_word_match: boolean;
  explanation: Explanation;
  context: ContextMessage[];
}

export interface InterpretedFilters {
  participant_id?: string | null;
  participant_name?: string | null;
  date_range_label?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  detected_topics: string[];
  is_decision_intent: boolean;
  cleaned_query: string;
}

export interface KeyDataPoint {
  label: string;
  value: string;
}

export interface SynthesizedAnswer {
  direct_answer: string;
  summary: string;
  confidence: number;
  key_data_points: KeyDataPoint[];
  primary_quote: string;
  primary_source_id: string;
  primary_author: string;
  primary_timestamp: string;
  consensus_status: string;
  supporting_points: string[];
}

export interface SearchResponse {
  query: string;
  query_type: string;
  interpreted_filters: InterpretedFilters;
  total_found: number;
  search_latency_ms: number;
  results: SearchResult[];
  synthesized_answer?: SynthesizedAnswer;
  debug_trace?: {
    raw_query?: string;
    normalized_query?: string;
    cleaned_query?: string;
    query_type?: string;
    detected_topics?: string[];
    entity_need?: string | null;
    expanded_queries?: string[];
    matched_threads?: string[];
    candidates_count?: number;
    retrieval_sources?: Record<string, number>;
    latency_breakdown?: {
      retrieval_ms: number;
      rerank_ms: number;
      total_ms: number;
    };
  };
}

export interface SearchFilterInput {
  participant?: string;
  start_date?: string;
  end_date?: string;
  thread_id?: string;
  is_decision_only?: boolean;
}

export interface SearchRequest {
  query: string;
  filters?: SearchFilterInput;
  limit?: number;
  include_context?: boolean;
  context_window?: number;
}

export interface Participant {
  id: string;
  name: string;
  handle: string;
  role: string;
  color: string;
  avatar: string;
}

export interface DecisionItem {
  id: string;
  title: string;
  topic: string;
  decision: string;
  message_id: string;
  participant: string;
  timestamp: string;
  context_summary: string;
  status: string;
  icon: string;
}

export interface EvalQueryItem {
  id: string;
  category: string;
  query: string;
  expected_id?: string;
  expected_message_id?: string;
  top1_id?: string;
  predicted_message_id?: string;
  top3_ids?: string[];
  is_top1?: boolean;
  top1_match?: boolean;
  is_top3?: boolean;
  top3_match?: boolean;
  word_overlap: number;
  shared_tokens?: string[];
  latency_ms?: number;
}

export interface CategoryBreakdown {
  total: number;
  top1_correct: number;
  top3_correct: number;
  top1_accuracy: number;
  top3_accuracy: number;
}

export interface EvaluationReport {
  timestamp: string;
  total_queries: number;
  overall_top1_accuracy: number;
  overall_top3_accuracy: number;
  zero_overlap_top1_accuracy: number;
  zero_overlap_top3_accuracy: number;
  avg_latency_ms: number;
  category_breakdown: Record<string, CategoryBreakdown>;
  results: EvalQueryItem[];
}
