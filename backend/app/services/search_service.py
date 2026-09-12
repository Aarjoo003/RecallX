import time
from typing import Dict, Any, Optional, List
from ..nlp.query_analyzer import analyze_query
from ..retrieval.hybrid_retriever import HybridRetriever
from ..retrieval.reranker import Reranker
from ..retrieval.context_reconstructor import ContextReconstructor
from ..retrieval.answer_synthesizer import AnswerSynthesizer
from ..models.search import SearchRequest, SearchResponse, SearchResult
from ..config import DEFAULT_RESULTS_LIMIT, DEFAULT_CONTEXT_WINDOW, TOP_K_CANDIDATES

class SearchService:
    _instance = None

    def __init__(self):
        self.retriever = HybridRetriever()
        self.reranker = Reranker()
        self.context_reconstructor = ContextReconstructor(self.retriever.index_manager.lexical_index)
        self.answer_synthesizer = AnswerSynthesizer()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def search(self, request: SearchRequest) -> SearchResponse:
        """
        End-to-end retrieval pipeline:
        1. Query Analysis (intent, person, time, topics)
        2. Hybrid Retrieval (Semantic Dense + Lexical FTS5 BM25)
        3. Multi-Signal Reranking (scores, overlap, decision boost, explanations)
        4. Conversation Context Reconstruction
        5. Grounded Direct Answer & Key Data Synthesis
        """
        t_start = time.perf_counter()
        raw_query = request.query.strip()
        if not raw_query:
            return SearchResponse(
                query="",
                query_type="empty",
                interpreted_filters=None,
                total_found=0,
                search_latency_ms=0.0,
                results=[],
                synthesized_answer=None
            )

        # 1. Query Analysis
        analysis = analyze_query(raw_query)
        interpreted = analysis["interpreted_filters"]

        # 2. Extract manual filters from request if provided
        manual_dict = None
        if request.filters:
            manual_dict = request.filters.model_dump()

        # Determine active start_date, end_date, participant_id
        start_date = manual_dict.get("start_date") if manual_dict else None
        end_date = manual_dict.get("end_date") if manual_dict else None
        if not start_date and interpreted and interpreted.start_date:
            start_date = interpreted.start_date
            end_date = interpreted.end_date

        target_pid = manual_dict.get("participant") if manual_dict else None
        if not target_pid and interpreted and interpreted.participant_id:
            target_pid = interpreted.participant_id

        # 3. Hybrid Candidate Retrieval
        t_retrieval_start = time.perf_counter()
        candidates = self.retriever.retrieve_candidates(
            query=analysis["cleaned_query"],
            top_k=TOP_K_CANDIDATES,
            start_date=start_date,
            end_date=end_date,
            participant_id=target_pid,
            expanded_queries=analysis.get("expanded_queries"),
            matched_threads=analysis.get("matched_threads")
        )
        retrieval_ms = round((time.perf_counter() - t_retrieval_start) * 1000.0, 2)

        # 4. Multi-Signal Reranking
        t_rerank_start = time.perf_counter()
        limit = request.limit or DEFAULT_RESULTS_LIMIT
        results = self.reranker.rerank(
            query=raw_query,
            candidates=candidates,
            analysis=analysis,
            manual_filters=manual_dict,
            limit=limit
        )
        rerank_ms = round((time.perf_counter() - t_rerank_start) * 1000.0, 2)

        # 5. Conversation Context Reconstruction
        if request.include_context:
            c_window = request.context_window or DEFAULT_CONTEXT_WINDOW
            for r in results:
                r.context = self.context_reconstructor.reconstruct_context(
                    r.message_id,
                    window_size=c_window
                )

        # 6. Direct Answer & Key Data Synthesis
        synthesized_answer = self.answer_synthesizer.synthesize(
            query=raw_query,
            results=results,
            analysis=analysis
        )

        t_elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

        # Build debug trace for developers/evaluators
        retrieval_sources = {}
        for c in candidates:
            src = c.get("retrieved_by", "unknown")
            retrieval_sources[src] = retrieval_sources.get(src, 0) + 1

        debug_trace = {
            "raw_query": raw_query,
            "normalized_query": analysis.get("normalized_query"),
            "cleaned_query": analysis.get("cleaned_query"),
            "query_type": analysis.get("query_type"),
            "detected_topics": analysis.get("detected_topics", []),
            "entity_need": analysis.get("entity_need"),
            "expanded_queries": analysis.get("expanded_queries", []),
            "matched_threads": analysis.get("matched_threads", []),
            "candidates_count": len(candidates),
            "retrieval_sources": retrieval_sources,
            "latency_breakdown": {
                "retrieval_ms": retrieval_ms,
                "rerank_ms": rerank_ms,
                "total_ms": t_elapsed_ms
            }
        }

        return SearchResponse(
            query=raw_query,
            query_type=analysis["query_type"],
            interpreted_filters=interpreted,
            total_found=len(results),
            search_latency_ms=t_elapsed_ms,
            results=results,
            synthesized_answer=synthesized_answer,
            debug_trace=debug_trace
        )
