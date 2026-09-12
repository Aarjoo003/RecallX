"""
RecallX Automated Evaluation Suite
Evaluates the retrieval pipeline across 40 evaluation queries:
- 10 Zero-Word-Overlap queries (Hard Set)
- Semantic / meaning queries
- Person queries
- Time queries
- Person + topic queries
- Time + topic queries
- Decision-oriented queries
- Hinglish queries
- Typo/informal queries

Executes genuine hybrid retrieval without hardcoded answers.
Calculates Top-1 accuracy, Top-3 accuracy, word overlap, and latency.
"""

import sys
import os
import json
import time

# Support UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "backend")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
EVAL_DIR = os.path.join(DATA_DIR, "evaluation")
QUESTIONS_FILE = os.path.join(EVAL_DIR, "questions.json")
EVAL_RESULTS_FILE = os.path.join(EVAL_DIR, "eval_results.json")

sys.path.insert(0, BACKEND_DIR)

from app.services.search_service import SearchService
from app.models.search import SearchRequest
from app.nlp.normalizer import compute_word_overlap

def run_evaluation(save_results: bool = True):
    print("=" * 75)
    print("RECALLX RETRIEVAL EVALUATION SUITE")
    print("=" * 75)

    if not os.path.exists(QUESTIONS_FILE):
        print(f"[ERROR] Evaluation file not found: {QUESTIONS_FILE}")
        return None

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} evaluation queries from dataset.")
    print("Initializing SearchService & IndexManager...")
    service = SearchService.get_instance()

    results_detail = []
    category_stats = {}
    top1_correct = 0
    top3_correct = 0
    zero_overlap_total = 0
    zero_overlap_top1 = 0
    zero_overlap_top3 = 0

    print("-" * 75)
    print(f"{'ID':<8} {'CATEGORY':<14} {'OVERLAP':<8} {'TOP-1':<7} {'TOP-3':<7} {'QUERY'}")
    print("-" * 75)

    total_latency_ms = 0.0

    for idx, q in enumerate(questions, 1):
        qid = q["id"]
        query_text = q["query"]
        expected_id = q["expected_message_id"]
        category = q.get("category", "general")

        if category not in category_stats:
            category_stats[category] = {"total": 0, "top1": 0, "top3": 0}
        category_stats[category]["total"] += 1

        t0 = time.perf_counter()
        req = SearchRequest(query=query_text, limit=5, include_context=False)
        resp = service.search(req)
        lat = (time.perf_counter() - t0) * 1000.0
        total_latency_ms += lat

        retrieved_ids = [r.message_id for r in resp.results]
        top1_hit = (len(retrieved_ids) > 0 and retrieved_ids[0] == expected_id)
        top3_hit = (expected_id in retrieved_ids[:3])

        if top1_hit:
            top1_correct += 1
            category_stats[category]["top1"] += 1
        if top3_hit:
            top3_correct += 1
            category_stats[category]["top3"] += 1

        top_predicted_id = retrieved_ids[0] if retrieved_ids else "NONE"
        top_predicted_text = resp.results[0].text if resp.results else ""
        predicted_overlap = resp.results[0].word_overlap if resp.results else 0

        # Calculate actual overlap with top prediction
        overlap_cnt, _ = compute_word_overlap(query_text, top_predicted_text)

        if category == "zero_overlap":
            zero_overlap_total += 1
            if top1_hit:
                zero_overlap_top1 += 1
            if top3_hit:
                zero_overlap_top3 += 1

        mark_top1 = "[PASS]" if top1_hit else "[FAIL]"
        mark_top3 = "[PASS]" if top3_hit else "[FAIL]"

        print(f"{qid:<8} {category:<14} {overlap_cnt:<8} {mark_top1:<7} {mark_top3:<7} {query_text[:35]}...")

        results_detail.append({
            "id": qid,
            "category": category,
            "query": query_text,
            "expected_message_id": expected_id,
            "target_text": q.get("target_text", ""),
            "predicted_message_id": top_predicted_id,
            "predicted_text": top_predicted_text,
            "top1_match": top1_hit,
            "top3_match": top3_hit,
            "word_overlap": overlap_cnt,
            "is_zero_overlap": (overlap_cnt == 0),
            "latency_ms": round(lat, 2),
            "top_candidates": [
                {
                    "message_id": r.message_id,
                    "text": r.text,
                    "participant": r.participant_name,
                    "final_score": r.final_score,
                    "semantic_score": r.semantic_score,
                    "lexical_score": r.lexical_score,
                }
                for r in resp.results[:3]
            ]
        })

    num_q = len(questions)
    overall_top1_acc = (top1_correct / num_q) * 100.0 if num_q else 0.0
    overall_top3_acc = (top3_correct / num_q) * 100.0 if num_q else 0.0

    zero_top1_acc = (zero_overlap_top1 / zero_overlap_total) * 100.0 if zero_overlap_total else 0.0
    zero_top3_acc = (zero_overlap_top3 / zero_overlap_total) * 100.0 if zero_overlap_total else 0.0

    avg_lat = total_latency_ms / num_q if num_q else 0.0

    print("=" * 75)
    print("RECALLX EVALUATION SUMMARY METRICS")
    print("=" * 75)
    print(f"Total Queries Evaluated:    {num_q}")
    print(f"Overall Top-1 Accuracy:     {overall_top1_acc:.1f}% ({top1_correct}/{num_q})")
    print(f"Overall Top-3 Accuracy:     {overall_top3_acc:.1f}% ({top3_correct}/{num_q})")
    print(f"Hard Zero-Overlap Top-1:    {zero_top1_acc:.1f}% ({zero_overlap_top1}/{zero_overlap_total})")
    print(f"Hard Zero-Overlap Top-3:    {zero_top3_acc:.1f}% ({zero_overlap_top3}/{zero_overlap_total})")
    print(f"Average Query Latency:      {avg_lat:.2f} ms")
    print("-" * 75)
    print(f"{'CATEGORY':<18} {'TOTAL':<8} {'TOP-1 ACC':<12} {'TOP-3 ACC':<12}")
    print("-" * 75)

    category_breakdown = {}
    for cat, stats in category_stats.items():
        c_tot = stats["total"]
        c_top1 = (stats["top1"] / c_tot) * 100.0 if c_tot else 0.0
        c_top3 = (stats["top3"] / c_tot) * 100.0 if c_tot else 0.0
        category_breakdown[cat] = {
            "total": c_tot,
            "top1_correct": stats["top1"],
            "top3_correct": stats["top3"],
            "top1_accuracy": round(c_top1, 1),
            "top3_accuracy": round(c_top3, 1),
        }
        print(f"{cat:<18} {c_tot:<8} {c_top1:>6.1f}%      {c_top3:>6.1f}%")
    print("=" * 75)

    summary_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_queries": num_q,
        "overall_top1_accuracy": round(overall_top1_acc, 2),
        "overall_top3_accuracy": round(overall_top3_acc, 2),
        "zero_overlap_top1_accuracy": round(zero_top1_acc, 2),
        "zero_overlap_top3_accuracy": round(zero_top3_acc, 2),
        "avg_latency_ms": round(avg_lat, 2),
        "category_breakdown": category_breakdown,
        "results": results_detail,
    }

    if save_results:
        with open(EVAL_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        print(f"Saved complete evaluation report to {EVAL_RESULTS_FILE}")

    return summary_data

if __name__ == "__main__":
    run_evaluation(save_results=True)
