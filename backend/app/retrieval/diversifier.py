"""
RecallX Result Deduplication and Diversification Engine.

Provides relevance-preserving result deduplication and diversification:
1. Keeps the highest-ranked correct/relevant result (#1) strictly unchanged.
2. Identifies exact duplicates using normalized canonical representations and ensures
   they never appear multiple times.
3. Identifies near-duplicate messages using character sequence similarity and token Jaccard overlap.
4. Penalizes near-duplicate candidates during final ranking so that repetitive statements
   do not occupy the top-k list.
5. Promotes diverse supporting evidence:
   - Corroborating consensus statements
   - Different participants discussing the topic
   - Contextual continuity across the conversation thread
6. Balances ranking using: final_score = relevance_score + diversity_adjustment.
"""

import difflib
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from ..models.search import SearchResult
from ..nlp.normalizer import tokenize


def normalize_for_dedup(text: str) -> str:
    """
    Normalizes message text for duplicate detection:
    - Strips common forward headers (e.g. 'forwarded:', 'fwd:').
    - Converts to lowercase and removes punctuation and symbols.
    - Collapses consecutive whitespace.
    """
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r"^(forwarded|fwd|fw)\s*:\s*", "", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.split())


def compute_text_similarity(text1: str, text2: str) -> float:
    """
    Computes text similarity using normalized string comparison,
    token-level Jaccard similarity, and sequence pattern matching ratio.
    Returns a float in [0.0, 1.0].
    """
    n1 = normalize_for_dedup(text1)
    n2 = normalize_for_dedup(text2)
    if n1 == n2:
        return 1.0

    toks1 = set(tokenize(text1))
    toks2 = set(tokenize(text2))
    if not toks1 or not toks2:
        return 0.0

    jaccard = len(toks1 & toks2) / len(toks1 | toks2)
    # Only evaluate full sequence alignment if token overlap is substantial
    if jaccard >= 0.35:
        seq = difflib.SequenceMatcher(None, n1, n2).ratio()
        return max(jaccard, seq)
    return jaccard


class ResultDiversifier:
    def __init__(
        self,
        exact_threshold: float = 0.95,
        near_dup_threshold: float = 0.70,
        redundancy_penalty_weight: float = 0.45,
        participant_novelty_bonus: float = 0.03,
        corroboration_bonus: float = 0.04,
        context_continuity_bonus: float = 0.03,
    ):
        self.exact_threshold = exact_threshold
        self.near_dup_threshold = near_dup_threshold
        self.redundancy_penalty_weight = redundancy_penalty_weight
        self.participant_novelty_bonus = participant_novelty_bonus
        self.corroboration_bonus = corroboration_bonus
        self.context_continuity_bonus = context_continuity_bonus

    def diversify(
        self,
        scored_items: List[Dict[str, Any]],
        limit: int = 8,
        query: str = "",
        analysis: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Deduplicates and diversifies ranked candidates:
        - Slot #1: Always the highest-ranked anchor answer (UNMODIFIED).
        - Slots #2..N: Greedily select complementary supporting evidence using:
          Score_div = base_score - redundancy_penalty + diversity_bonuses
        - Discards exact duplicate normalized text.
        """
        if not scored_items:
            return []

        # Pre-compute normalized text and token sets for all candidates
        # to guarantee high-performance sub-millisecond execution
        cand_meta: List[Tuple[str, Set[str]]] = []
        for item in scored_items:
            r = item["result"]
            cand_meta.append((normalize_for_dedup(r.text), set(tokenize(r.text))))

        # Requirement 1 & 11: Keep the highest-ranked correct/relevant result unchanged
        top_item = scored_items[0]
        selected: List[SearchResult] = [top_item["result"]]
        selected_indices = {0}

        selected_norms: List[str] = [cand_meta[0][0]]
        selected_toks: List[Set[str]] = [cand_meta[0][1]]
        selected_pids: Set[str] = {top_item["result"].participant_id}
        anchor_thread = top_item["result"].thread_id

        # Decision & commitment markers for corroboration bonus
        decision_kws = [
            "confirm", "lock", "approved", "final", "receipt", "booked",
            "done", "settled", "agreed", "scheduled", "fix kar di"
        ]

        # Greedy selection for slots 2..limit
        while len(selected) < limit:
            best_candidate_idx = None
            best_candidate_score = -999.0

            for idx, item in enumerate(scored_items):
                if idx in selected_indices:
                    continue

                r: SearchResult = item["result"]
                norm_text, r_toks = cand_meta[idx]

                # Requirement 3: Do not show exact duplicate messages multiple times
                if norm_text in selected_norms:
                    continue

                # Fast similarity calculation against all selected items
                max_sim = 0.0
                for s_idx, s_norm in enumerate(selected_norms):
                    if norm_text == s_norm:
                        max_sim = 1.0
                        break
                    s_tok = selected_toks[s_idx]
                    if not r_toks or not s_tok:
                        continue
                    union_len = len(r_toks | s_tok)
                    jaccard = len(r_toks & s_tok) / union_len if union_len > 0 else 0.0
                    if jaccard >= 0.35:
                        seq = difflib.SequenceMatcher(None, norm_text, s_norm).ratio()
                        sim = max(jaccard, seq)
                    else:
                        sim = jaccard
                    if sim > max_sim:
                        max_sim = sim

                # Prune if practically identical wording (>= exact_threshold)
                if max_sim >= self.exact_threshold:
                    continue

                # Base relevance score from multi-signal reranking remains primary (Requirement 7)
                base_score = item["sort_key"][0]

                # Requirement 4: Redundancy penalty for near-duplicate candidates
                redundancy_penalty = 0.0
                if max_sim >= self.near_dup_threshold:
                    redundancy_penalty = (max_sim - 0.45) * self.redundancy_penalty_weight * 2.0
                elif max_sim >= 0.50:
                    redundancy_penalty = (max_sim - 0.40) * 0.15

                # Requirement 5: Diversity & supporting evidence bonuses
                bonus = 0.0

                # 1. Corroborating consensus / agreement signal
                t_lower = r.text.lower()
                if r.decision_score > 0.6 or any(kw in t_lower for kw in decision_kws):
                    bonus += self.corroboration_bonus

                # 2. Participant diversity: corroborating evidence from different group members
                if r.participant_id not in selected_pids:
                    bonus += self.participant_novelty_bonus

                # 3. Context continuity: different message in the same conversation thread
                if anchor_thread and r.thread_id == anchor_thread and max_sim < 0.45:
                    bonus += self.context_continuity_bonus

                # Requirement 8: Relevance score + diversity adjustment
                adj_score = base_score - redundancy_penalty + bonus

                if adj_score > best_candidate_score:
                    best_candidate_score = adj_score
                    best_candidate_idx = idx

            if best_candidate_idx is None:
                # No more distinct non-duplicate candidates available
                break

            chosen_item = scored_items[best_candidate_idx]
            chosen_res: SearchResult = chosen_item["result"]
            selected.append(chosen_res)
            selected_indices.add(best_candidate_idx)
            selected_norms.append(cand_meta[best_candidate_idx][0])
            selected_toks.append(cand_meta[best_candidate_idx][1])
            selected_pids.add(chosen_res.participant_id)

        return selected
