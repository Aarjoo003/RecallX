"""
Unit and Integration Tests for RecallX Result Deduplication and Diversification.

Tests verify:
1. Exact duplicate messages are pruned and never repeated in top results.
2. Near-duplicate messages are penalized so repetitive phrasing does not monopolize top-k.
3. Multiple relevant messages from the same participant are retained when they provide distinct information.
4. Different participants discussing the same topic are promoted as complementary supporting evidence.
5. Zero-word-overlap queries preserve the exact #1 anchor answer with rich diverse supporting evidence.
6. The #1 highest-ranked result is strictly protected and never pushed down by diversity bonuses.
"""

import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.models.search import SearchResult, Explanation, SearchRequest
from app.retrieval.diversifier import ResultDiversifier, normalize_for_dedup, compute_text_similarity
from app.services.search_service import SearchService
from app.indexing.index_manager import IndexManager


def make_dummy_result(
    message_id: str,
    text: str,
    participant_id: str = "user_1",
    participant_name: str = "Aman",
    thread_id: str = "thread_trip",
    final_score: float = 0.80,
    decision_score: float = 0.0,
) -> SearchResult:
    return SearchResult(
        message_id=message_id,
        participant_id=participant_id,
        participant_name=participant_name,
        timestamp="2026-07-14T10:00:00",
        text=text,
        thread_id=thread_id,
        semantic_score=final_score,
        lexical_score=0.5,
        person_score=0.5,
        time_score=0.5,
        decision_score=decision_score,
        final_score=final_score,
        word_overlap=1,
        is_zero_word_match=False,
        explanation=Explanation(
            semantic_relevance="High",
            person_match="None",
            time_match="None",
            decision_signal="None",
            summary="Test candidate."
        ),
        context=[]
    )


def test_normalize_and_similarity():
    """Verify text normalization and similarity calculation."""
    t1 = "Gym session evening 6 PM anyone joining?"
    t2 = "gym session evening 6 pm anyone joining"
    t3 = "Forwarded: gym session evening 6 PM anyone joining?"

    assert normalize_for_dedup(t1) == "gym session evening 6 pm anyone joining"
    assert compute_text_similarity(t1, t2) == 1.0
    assert compute_text_similarity(t1, t3) == 1.0

    # Near duplicate
    near1 = "Done bhai, Manali final. I'll book tomorrow."
    near2 = "Done bhai, Manali final. I will book tomorrow."
    assert compute_text_similarity(near1, near2) > 0.90

    # Distinct content
    diff1 = "Found a riverside cottage in Old Manali with bonfire, booked 3 rooms."
    assert compute_text_similarity(near1, diff1) < 0.50


def test_exact_duplicate_messages():
    """
    Requirement 3: Do not show exact duplicate messages multiple times.
    """
    diversifier = ResultDiversifier()

    r1 = make_dummy_result("msg_1", "Gym session evening 6 PM anyone joining?", participant_id="user_1", final_score=0.95)
    r2 = make_dummy_result("msg_2", "Gym session evening 6 PM anyone joining?", participant_id="user_2", final_score=0.94)
    r3 = make_dummy_result("msg_3", "gym session evening 6 pm anyone joining?", participant_id="user_3", final_score=0.93)
    r4 = make_dummy_result("msg_4", "Late night coding sessions are ruining my sleep cycle", participant_id="user_4", final_score=0.70)

    scored_items = [
        {"result": r1, "sort_key": (0.95, 0.9, 0.9)},
        {"result": r2, "sort_key": (0.94, 0.9, 0.9)},
        {"result": r3, "sort_key": (0.93, 0.9, 0.9)},
        {"result": r4, "sort_key": (0.70, 0.7, 0.7)},
    ]

    diversified = diversifier.diversify(scored_items, limit=3)

    # Must contain r1 and r4, while exact duplicates r2 and r3 are skipped
    assert len(diversified) == 2
    assert diversified[0].message_id == "msg_1"
    assert diversified[1].message_id == "msg_4"


def test_near_duplicate_penalization():
    """
    Requirement 4: Penalize near-duplicate candidates during final ranking so that
    multiple results from the same repetitive statement do not occupy the entire top-k.
    """
    diversifier = ResultDiversifier()

    r1 = make_dummy_result("msg_1", "Done bhai, Manali final. I'll book tomorrow.", participant_id="user_1", final_score=0.95)
    # Near duplicate of r1 with slightly different wording
    r2_near = make_dummy_result("msg_2", "Done bhai, Manali final. I will book tomorrow.", participant_id="user_2", final_score=0.94)
    # Distinct supporting message with slightly lower base relevance
    r3_distinct = make_dummy_result("msg_3", "Found a riverside cottage in Old Manali with bonfire, booked 3 rooms.", participant_id="user_3", final_score=0.82)

    scored_items = [
        {"result": r1, "sort_key": (0.95, 0.9, 0.9)},
        {"result": r2_near, "sort_key": (0.94, 0.9, 0.9)},
        {"result": r3_distinct, "sort_key": (0.82, 0.8, 0.8)},
    ]

    diversified = diversifier.diversify(scored_items, limit=2)

    # R1 is #1 anchor. Due to near-duplicate penalty on R2, R3 distinct is promoted to #2!
    assert diversified[0].message_id == "msg_1"
    assert diversified[1].message_id == "msg_3"


def test_multiple_relevant_messages_from_same_person():
    """
    Requirement 6: Do NOT simply remove all messages from the same participant.
    Multiple messages from the same person can be highly relevant.
    """
    diversifier = ResultDiversifier()

    # Aman sends milestone lock
    r1 = make_dummy_result("msg_1", "Done bhai, Manali final. I'll book tomorrow.", participant_id="aman", participant_name="Aman", final_score=0.95)
    # Aman ALSO sends important distinct accommodation update
    r2 = make_dummy_result("msg_2", "Booked 3 rooms at riverside cottage with bonfire.", participant_id="aman", participant_name="Aman", final_score=0.88)
    # Aman repeats exact same lock statement (duplicate)
    r3 = make_dummy_result("msg_3", "Done bhai, Manali final. I'll book tomorrow.", participant_id="aman", participant_name="Aman", final_score=0.85)

    scored_items = [
        {"result": r1, "sort_key": (0.95, 0.9, 0.9)},
        {"result": r2, "sort_key": (0.88, 0.8, 0.8)},
        {"result": r3, "sort_key": (0.85, 0.8, 0.8)},
    ]

    diversified = diversifier.diversify(scored_items, limit=3)

    # Both distinct messages from Aman are retained; the duplicate is skipped!
    retained_ids = [r.message_id for r in diversified]
    assert "msg_1" in retained_ids
    assert "msg_2" in retained_ids
    assert "msg_3" not in retained_ids


def test_different_participants_discussing_same_topic():
    """
    Requirement 5: Prefer diverse supporting evidence from different participants
    corroborating the same topic.
    """
    diversifier = ResultDiversifier()

    r1 = make_dummy_result("msg_1", "Aman ka birthday 18 August ko hai na sab yaad rakhna", participant_id="rohan", participant_name="Rohan", final_score=0.95)
    r2 = make_dummy_result("msg_2", "Haan 18 August confirmed hai, chocolate truffle cake order kar diya maine Old Bakery se", participant_id="sneha", participant_name="Sneha", final_score=0.90, decision_score=0.8)
    r3 = make_dummy_result("msg_3", "Sab log Tuesday 7 PM hostel common room me aana birthday party celebration ke liye", participant_id="priya", participant_name="Priya", final_score=0.89, decision_score=0.8)

    scored_items = [
        {"result": r1, "sort_key": (0.95, 0.9, 0.9)},
        {"result": r2, "sort_key": (0.90, 0.9, 0.9)},
        {"result": r3, "sort_key": (0.89, 0.8, 0.8)},
    ]

    diversified = diversifier.diversify(scored_items, limit=3)

    assert len(diversified) == 3
    participants = [r.participant_name for r in diversified]
    assert participants == ["Rohan", "Sneha", "Priya"]


def test_top_result_never_pushed_down():
    """
    Requirement 1 & 11: Verify that the correct top result does not get pushed down
    merely because another result is more diverse.
    """
    diversifier = ResultDiversifier()

    # R1 has highest relevance (0.98), but is alone
    r1 = make_dummy_result("msg_anchor", "Done bhai, Manali final. I'll book tomorrow.", participant_id="aman", final_score=0.98)
    # R2 has lower relevance (0.85), but would theoretically get every diversity bonus
    r2 = make_dummy_result("msg_other", "Auditorium slot approved for symposium.", participant_id="priya", final_score=0.85, decision_score=1.0)

    scored_items = [
        {"result": r1, "sort_key": (0.98, 0.9, 0.9)},
        {"result": r2, "sort_key": (0.85, 0.8, 0.8)},
    ]

    diversified = diversifier.diversify(scored_items, limit=2)

    # R1 MUST be index 0
    assert diversified[0].message_id == "msg_anchor"
    assert diversified[0].final_score == 0.98


def test_zero_word_overlap_diversity():
    """
    Requirement 5, 9 & 10: Zero-word-overlap queries return #1 anchor answer
    and non-duplicate supporting evidence.
    """
    service = SearchService.get_instance()
    req = SearchRequest(query="When did we finally settle on the destination?", limit=5)
    resp = service.search(req)

    assert len(resp.results) >= 3
    # Top result must remain msg_3769 (Aman's Manali lock)
    assert resp.results[0].message_id == "msg_3769"
    assert resp.results[0].word_overlap == 0

    # Ensure no exact duplicates exist in the results list
    unique_texts = {r.text.strip().lower() for r in resp.results}
    assert len(unique_texts) == len(resp.results)
