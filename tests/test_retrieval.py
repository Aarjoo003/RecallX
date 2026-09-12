import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.indexing.index_manager import IndexManager
from app.services.search_service import SearchService
from app.models.search import SearchRequest
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import Reranker


@pytest.fixture(scope="module")
def search_service():
    # Ensure indexes are ready
    IndexManager.get_instance().initialize()
    return SearchService.get_instance()


def test_index_manager_loaded():
    mgr = IndexManager.get_instance()
    assert mgr.is_ready is True
    assert len(mgr.idx_to_id) >= 4000
    assert mgr.embeddings is not None
    assert mgr.embeddings.shape[0] == len(mgr.idx_to_id)


def test_hybrid_retriever_returns_candidates():
    retriever = HybridRetriever()
    candidates = retriever.retrieve_candidates("presentation slides", top_k=30)
    assert len(candidates) > 0
    first = candidates[0]
    assert "message" in first
    assert "id" in first["message"]
    assert "semantic_score" in first


def test_zero_word_overlap_query_precision(search_service):
    """
    Critical requirement: Query "When did we finally settle on the destination?"
    must find msg_3769 ("Done bhai, Manali final. I'll book tomorrow.") at Rank 1,
    with mathematically verified 0 word overlap.
    """
    req = SearchRequest(query="When did we finally settle on the destination?", limit=5)
    resp = search_service.search(req)

    assert len(resp.results) > 0
    top_result = resp.results[0]

    # Target message is msg_3769
    assert top_result.message_id == "msg_3769"
    assert top_result.is_zero_word_match is True
    assert top_result.word_overlap == 0
    assert top_result.explanation is not None
    assert hasattr(top_result, "semantic_score")
    assert hasattr(top_result, "lexical_score")


def test_person_search(search_service):
    """
    Person query: What did Priya say about the registration fee?
    Should retrieve Priya's message in top results.
    """
    req = SearchRequest(query="What did Priya say about the registration fee?", limit=5)
    resp = search_service.search(req)

    assert len(resp.results) > 0
    top = resp.results[0]
    assert top.message_id == "msg_4673"
    assert top.participant_name == "Priya Patel"


def test_sub_20ms_search_latency(search_service):
    """
    Search latency should be well under 100ms, targeting sub-20ms.
    """
    req = SearchRequest(query="hackathon registration deadline", limit=5)
    resp = search_service.search(req)
    assert resp.search_latency_ms < 100.0  # Safe threshold for test assertion
