import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.nlp.query_analyzer import analyze_query
from app.nlp.normalizer import compute_word_overlap, tokenize


def test_empty_query():
    analysis = analyze_query("")
    assert analysis["cleaned_query"] == ""
    assert analysis["query_type"] == "semantic"


def test_person_intent_detection():
    # Query mentioning person: Priya
    analysis_priya = analyze_query("Priya ka suggestion kya tha?")
    assert analysis_priya["participant"] is not None
    assert analysis_priya["participant"]["id"] == "p02"

    # Query mentioning person: Aman
    analysis_aman = analyze_query("What did Aman say about the slides?")
    assert analysis_aman["participant"] is not None
    assert analysis_aman["participant"]["id"] == "p01"


def test_decision_intent_detection():
    analysis = analyze_query("When did we finally settle on the destination?")
    assert analysis["is_decision"] is True
    assert analysis["entity_need"] == "trip_destination"

    tech_analysis = analyze_query("What tech stack did we finalize for the capstone?")
    assert tech_analysis["is_decision"] is True
    assert tech_analysis["entity_need"] == "tech_stack"


def test_temporal_intent_detection():
    analysis = analyze_query("What was discussed on July 14?")
    assert analysis["temporal"] is not None
    assert "2026-07-14" in analysis["temporal"]["start"]


def test_word_overlap_computation():
    query = "When did we finally settle on the destination?"
    doc = "Gokarna is locked. Tickets booked for 12 people!"
    overlap_count, shared_words = compute_word_overlap(query, doc)
    assert overlap_count == 0
    assert len(shared_words) == 0

    query2 = "react native expo setup"
    doc2 = "We are using React Native with Expo for the mobile client"
    overlap2, shared2 = compute_word_overlap(query2, doc2)
    assert overlap2 > 0
    assert "react" in shared2
    assert "expo" in shared2
