import time
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

from ..indexing.index_manager import IndexManager
from ..indexing.embedder import Embedder
from ..config import TOP_K_CANDIDATES

class HybridRetriever:
    def __init__(self, index_manager: Optional[IndexManager] = None):
        self.index_manager = index_manager or IndexManager.get_instance()
        if not self.index_manager.is_ready:
            self.index_manager.initialize()

    def retrieve_candidates(
        self,
        query: str,
        top_k: int = TOP_K_CANDIDATES,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        participant_id: Optional[str] = None,
        expanded_queries: Optional[List[str]] = None,
        matched_threads: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Multi-modal candidate retrieval:
        1. Dense Semantic cosine similarity (Primary query + Expanded representations)
        2. Lexical FTS5 BM25 search (Primary query + Normalized terms)
        3. Structured metadata filtering (Temporal window, Participant, & Thread context)
        """
        # 1. Semantic retrieval with primary query
        query_emb = self.index_manager.embedder.encode(query)
        fetch_k = max(top_k, 150)
        semantic_results = self.index_manager.search_semantic(query_emb, top_k=fetch_k)

        best_sem: Dict[str, float] = {}
        sem_text_counts: Dict[str, int] = {}
        for mid, s in semantic_results:
            msg = self.index_manager.get_message(mid)
            if not msg:
                continue
            norm_t = msg["text"].strip().lower()
            count = sem_text_counts.get(norm_t, 0)
            if count < 3:
                best_sem[mid] = float(s)
                sem_text_counts[norm_t] = count + 1
            if len(best_sem) >= top_k:
                break

        # Multi-representation semantic search with expanded representations
        exp_embs: List[np.ndarray] = []
        if expanded_queries:
            queries_to_encode = [q.strip() for q in expanded_queries[:2] if q.strip()]
            if queries_to_encode:
                encoded = self.index_manager.embedder.encode(queries_to_encode)
                if len(encoded.shape) == 1:
                    exp_embs = [encoded]
                else:
                    exp_embs = [encoded[i] for i in range(len(encoded))]
                for exp_emb in exp_embs:
                    exp_results = self.index_manager.search_semantic(exp_emb, top_k=top_k // 2)
                    for mid, s in exp_results:
                        if mid in best_sem:
                            best_sem[mid] = max(best_sem[mid], float(s))
                        else:
                            msg = self.index_manager.get_message(mid)
                            if msg:
                                norm_t = msg["text"].strip().lower()
                                if sem_text_counts.get(norm_t, 0) < 3:
                                    best_sem[mid] = float(s)
                                    sem_text_counts[norm_t] = sem_text_counts.get(norm_t, 0) + 1

        # 2. Lexical retrieval with primary query and expanded variants
        lexical_results = self.index_manager.lexical_index.search_lexical(query, limit=top_k)
        best_lex: Dict[str, float] = {mid: float(s) for mid, s in lexical_results}

        if expanded_queries:
            for exp_q in expanded_queries[:2]:
                exp_lex_res = self.index_manager.lexical_index.search_lexical(exp_q, limit=20)
                for mid, s in exp_lex_res:
                    if mid in best_lex:
                        best_lex[mid] = max(best_lex[mid], float(s))
                    else:
                        best_lex[mid] = float(s)

        candidate_dict: Dict[str, Dict[str, Any]] = {}
        q_vec = query_emb.squeeze()

        # Merge semantic candidates
        for msg_id, sem_score in best_sem.items():
            msg = self.index_manager.get_message(msg_id)
            if msg:
                candidate_dict[msg_id] = {
                    "message": msg,
                    "semantic_score": max(0.0, sem_score),
                    "lexical_score": best_lex.get(msg_id, 0.0),
                    "retrieved_by": "semantic"
                }

        # Merge lexical candidates
        for msg_id, lex_score in best_lex.items():
            if msg_id in candidate_dict:
                candidate_dict[msg_id]["lexical_score"] = float(lex_score)
                candidate_dict[msg_id]["retrieved_by"] = "both"
            else:
                msg = self.index_manager.get_message(msg_id)
                if msg:
                    idx = self.index_manager.id_to_idx.get(msg_id)
                    sem_val = 0.0
                    if idx is not None and self.index_manager.embeddings is not None:
                        msg_vec = self.index_manager.embeddings[idx]
                        sem_val = float(np.dot(msg_vec, q_vec))
                        for exp_e in exp_embs:
                            sem_val = max(sem_val, float(np.dot(msg_vec, exp_e.squeeze())))

                    candidate_dict[msg_id] = {
                        "message": msg,
                        "semantic_score": max(0.0, sem_val),
                        "lexical_score": float(lex_score),
                        "retrieved_by": "lexical"
                    }

        # Thread context candidate enrichment
        if matched_threads:
            for th_id in matched_threads:
                th_msgs = self.index_manager.lexical_index.get_thread(th_id)
                for m in th_msgs:
                    mid = m["id"]
                    if mid not in candidate_dict:
                        idx = self.index_manager.id_to_idx.get(mid)
                        sem_val = 0.0
                        if idx is not None and self.index_manager.embeddings is not None:
                            msg_vec = self.index_manager.embeddings[idx]
                            sem_val = float(np.dot(msg_vec, q_vec))
                            for exp_e in exp_embs:
                                sem_val = max(sem_val, float(np.dot(msg_vec, exp_e.squeeze())))
                        candidate_dict[mid] = {
                            "message": m,
                            "semantic_score": max(0.0, sem_val),
                            "lexical_score": best_lex.get(mid, 0.0),
                            "retrieved_by": "thread_context"
                        }


        # 3. Add temporal candidates if date range exists
        if start_date and end_date:
            time_msgs = self.index_manager.lexical_index.get_messages_by_time_range(start_date, end_date, limit=40)
            for m in time_msgs:
                mid = m["id"]
                if mid not in candidate_dict:
                    idx = self.index_manager.id_to_idx.get(mid)
                    sem_val = 0.0
                    if idx is not None and self.index_manager.embeddings is not None:
                        sem_val = float(np.dot(self.index_manager.embeddings[idx], query_emb.squeeze()))

                    candidate_dict[mid] = {
                        "message": m,
                        "semantic_score": max(0.0, sem_val),
                        "lexical_score": 0.0,
                        "retrieved_by": "temporal_metadata"
                    }

        # 4. Add participant candidates if participant filter exists
        if participant_id:
            person_msgs = self.index_manager.lexical_index.get_messages_by_participant(participant_id, limit=40)
            for m in person_msgs:
                mid = m["id"]
                if mid not in candidate_dict:
                    idx = self.index_manager.id_to_idx.get(mid)
                    sem_val = 0.0
                    if idx is not None and self.index_manager.embeddings is not None:
                        sem_val = float(np.dot(self.index_manager.embeddings[idx], query_emb.squeeze()))

                    candidate_dict[mid] = {
                        "message": m,
                        "semantic_score": max(0.0, sem_val),
                        "lexical_score": 0.0,
                        "retrieved_by": "person_metadata"
                    }

        return list(candidate_dict.values())
