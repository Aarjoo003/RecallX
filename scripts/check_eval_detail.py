import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("data/evaluation/eval_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for r in data["results"][:10]:
    print("=" * 60)
    print(f"ID: {r['id']} | Query: {r['query']}")
    print(f"Target: [{r['expected_message_id']}] {r['target_text']}")
    print(f"Top Pred: [{r['predicted_message_id']}] {r['predicted_text']}")
    print(f"Top 1 match: {r['top1_match']} | Top 3 match: {r['top3_match']}")
    for i, c in enumerate(r["top_candidates"]):
        print(f"   Rank {i+1}: [{c['message_id']}] (final={c['final_score']}, sem={c['semantic_score']}, lex={c['lexical_score']}) -> {c['text']}")
