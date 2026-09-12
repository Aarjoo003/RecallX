from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .message import ContextMessage

class SearchFilterInput(BaseModel):
    participant: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    thread_id: Optional[str] = None
    is_decision_only: Optional[bool] = False

class SearchRequest(BaseModel):
    query: str
    filters: Optional[SearchFilterInput] = None
    limit: Optional[int] = 10
    include_context: Optional[bool] = True
    context_window: Optional[int] = 3

class InterpretedFilters(BaseModel):
    participant_id: Optional[str] = None
    participant_name: Optional[str] = None
    date_range_label: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    detected_topics: List[str] = []
    is_decision_intent: bool = False
    cleaned_query: str

class Explanation(BaseModel):
    semantic_relevance: str  # "High", "Medium", "Low"
    person_match: str        # "Exact", "None"
    time_match: str          # "Exact", "Within Range", "None"
    decision_signal: str     # "Strong", "Moderate", "None"
    summary: str

class SearchResult(BaseModel):
    message_id: str
    participant_id: str
    participant_name: str
    timestamp: str
    text: str
    thread_id: str
    semantic_score: float
    lexical_score: float
    person_score: float
    time_score: float
    decision_score: float
    final_score: float
    word_overlap: int
    is_zero_word_match: bool
    explanation: Explanation
    context: Optional[List[ContextMessage]] = []

class KeyDataPoint(BaseModel):
    label: str
    value: str

class SynthesizedAnswer(BaseModel):
    direct_answer: str
    summary: str
    confidence: float
    key_data_points: List[KeyDataPoint] = []
    primary_quote: str
    primary_source_id: str
    primary_author: str
    primary_timestamp: str
    consensus_status: str
    supporting_points: List[str] = []

class SearchResponse(BaseModel):
    query: str
    query_type: str
    interpreted_filters: InterpretedFilters
    total_found: int
    search_latency_ms: float
    results: List[SearchResult]
    synthesized_answer: Optional[SynthesizedAnswer] = None
    debug_trace: Optional[Dict[str, Any]] = None

