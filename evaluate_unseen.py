"""
RecallX Unseen Queries Automated Evaluation Suite
Evaluates 25 unseen natural-language, conversational Hinglish, short, and paraphrased queries.
"""
import sys
import os
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(SCRIPT_DIR, "backend")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
EVAL_DIR = os.path.join(DATA_DIR, "evaluation")
UNSEEN_FILE = os.path.join(EVAL_DIR, "unseen_queries.json")
RESULTS_FILE = os.path.join(EVAL_DIR, "unseen_eval_results.json")

sys.path.insert(0, BACKEND_DIR)

from app.services.search_service import SearchService
from app.models.search import SearchRequest
from app.nlp.normalizer import compute_word_overlap

def run_unseen_evaluation():
    print("=" * 80)
    print("RECALLX UNSEEN RETRIEVAL EVALUATION SUITE (25 REAL-WORLD QUERIES)")
    print("=" * 80)

    if not os.path.exists(UNSEEN_FILE):
        print(f"[ERROR] File not found: {UNSEEN_FILE}")
        return

    with open(UNSEEN_FILE, "r", encoding="utf-8") as f:
        queries = json.load(f)

    service = SearchService.get_instance()
    results_detail = []
    category_stats = {}
    top1_correct = 0
    top3_correct = 0
    total_latency_ms = 0.0

    print(f"{'ID':<11} {'CATEGORY':<24} {'OVERLAP':<8} {'TOP-1':<7} {'TOP-3':<7} {'QUERY'}")
    print("-" * 80)

    for q in queries:
        qid = q["id"]
        cat = q.get("category", "unseen")
        query_text = q["query"]
        expected_id = q["expected_message_id"]

        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "top1": 0, "top3": 0}
        category_stats[cat]["total"] += 1

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
            category_stats[cat]["top1"] += 1
        if top3_hit:
            top3_correct += 1
            category_stats[cat]["top3"] += 1

        top_predicted_id = retrieved_ids[0] if retrieved_ids else "NONE"
        top_predicted_text = resp.results[0].text if resp.results else ""
        overlap_cnt, _ = compute_word_overlap(query_text, top_predicted_text)

        m_top1 = "[PASS]" if top1_hit else "[FAIL]"
        m_top3 = "[PASS]" if top3_hit else "[FAIL]"

        print(f"{qid:<11} {cat:<24} {overlap_cnt:<8} {m_top1:<7} {m_top3:<7} {query_text[:32]}...")

        results_detail.append({
            "id": qid,
            "category": cat,
            "query": query_text,
            "expected_message_id": expected_id,
            "predicted_message_id": top_predicted_id,
            "predicted_text": top_predicted_text,
            "top1_match": top1_hit,
            "top3_match": top3_hit,
            "word_overlap": overlap_cnt,
            "latency_ms": round(lat, 2),
            "top_candidates": [
                {
                    "message_id": r.message_id,
                    "text": r.text,
                    "participant": r.participant_name,
                    "final_score": r.final_score,
                }
                for r in resp.results[:3]
            ]
        })

    num_q = len(queries)
    top1_acc = (top1_correct / num_q) * 100.0 if num_q else 0.0
    top3_acc = (top3_correct / num_q) * 100.0 if num_q else 0.0
    avg_lat = total_latency_ms / num_q if num_q else 0.0

    print("=" * 80)
    print("UNSEEN EVALUATION SUMMARY")
    print(f"Total Unseen Queries: {num_q}")
    print(f"Overall Top-1 Accuracy: {top1_acc:.1f}% ({top1_correct}/{num_q})")
    print(f"Overall Top-3 Accuracy: {top3_acc:.1f}% ({top3_correct}/{num_q})")
    print(f"Average Latency: {avg_lat:.2f} ms")
    print("-" * 80)
    for cat, s in category_stats.items():
        t1 = (s['top1'] / s['total']) * 100.0 if s['total'] else 0.0
        t3 = (s['top3'] / s['total']) * 100.0 if s['total'] else 0.0
        print(f"{cat:<25} Total: {s['total']:<3} Top-1: {t1:5.1f}% Top-3: {t3:5.1f}%")
    print("=" * 80)

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_queries": num_q,
        "overall_top1_accuracy": round(top1_acc, 2),
        "overall_top3_accuracy": round(top3_acc, 2),
        "avg_latency_ms": round(avg_lat, 2),
        "category_breakdown": {
            cat: {
                "total": s["total"],
                "top1_correct": s["top1"],
                "top3_correct": s["top3"],
                "top1_accuracy": round((s["top1"] / s["total"]) * 100.0, 2),
                "top3_accuracy": round((s["top3"] / s["total"]) * 100.0, 2)
            }
            for cat, s in category_stats.items()
        },
        "results": results_detail
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Saved unseen evaluation report to {RESULTS_FILE}")

if __name__ == '__main__':
    run_unseen_evaluation()
