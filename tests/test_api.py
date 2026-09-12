import pytest
import sys
import os
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from app.indexing.index_manager import IndexManager


@pytest.fixture(scope="module")
def client():
    IndexManager.get_instance().initialize()
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "RecallX" in data["name"]


def test_health_check_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["index_ready"] is True
    assert data["indexed_messages"] >= 4000


def test_search_endpoint_valid(client):
    payload = {
        "query": "When did we finally settle on the destination?",
        "limit": 5,
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert len(data["results"]) > 0
    assert data["results"][0]["message_id"] == "msg_3769"
    assert data["results"][0]["is_zero_word_match"] is True


def test_search_endpoint_empty(client):
    response = client.post("/api/search", json={"query": "   ", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0
    assert data["total_found"] == 0


def test_decisions_endpoint(client):
    response = client.get("/api/decisions")
    assert response.status_code == 200
    decisions = response.json()
    assert len(decisions) >= 3
    topics = [d["topic"] for d in decisions]
    assert any("Trip" in t or "Destination" in t for t in topics)


def test_participants_endpoint(client):
    response = client.get("/api/participants")
    assert response.status_code == 200
    participants = response.json()
    assert len(participants) >= 8


def test_message_detail_endpoint(client):
    response = client.get("/api/messages/msg_3769")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "msg_3769"
    assert "Manali" in data["text"]


def test_thread_endpoint(client):
    response = client.get("/api/thread/thread_trip_01")
    assert response.status_code == 200
    msgs = response.json()
    assert len(msgs) > 0
    assert all(m["thread_id"] == "thread_trip_01" for m in msgs)


def test_context_endpoint(client):
    response = client.get("/api/context/msg_3769?window=3")
    assert response.status_code == 200
    msgs = response.json()
    assert len(msgs) > 0
    assert any(m["id"] == "msg_3769" and m["is_target"] for m in msgs)


def test_evaluation_endpoint(client):
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert data["total_queries"] == 40
    assert data["overall_top1_accuracy"] >= 95.0
    assert data["zero_overlap_top1_accuracy"] >= 95.0
