import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.indexing.index_manager import IndexManager
from app.retrieval.context_reconstructor import ContextReconstructor


@pytest.fixture(scope="module")
def reconstructor():
    IndexManager.get_instance().initialize()
    return ContextReconstructor()


def test_reconstruct_context_window(reconstructor):
    # Retrieve context window around msg_3769
    context = reconstructor.reconstruct_context("msg_3769", window_size=3)
    assert len(context) > 0

    # Ensure target message is in the window and flagged is_target
    targets = [m for m in context if m.is_target]
    assert len(targets) == 1
    assert targets[0].id == "msg_3769"

    # Ensure messages are ordered chronologically
    timestamps = [m.timestamp for m in context]
    assert timestamps == sorted(timestamps)


def test_get_full_thread(reconstructor):
    thread_msgs = reconstructor.get_full_thread("thread_trip_01")
    assert len(thread_msgs) >= 10

    # All returned messages belong to thread_trip_01
    for msg in thread_msgs:
        assert msg.thread_id == "thread_trip_01"

    # Messages sorted chronologically
    timestamps = [m.timestamp for m in thread_msgs]
    assert timestamps == sorted(timestamps)


def test_nonexistent_message_context(reconstructor):
    context = reconstructor.reconstruct_context("non_existent_msg_999999", window_size=3)
    assert context == []
