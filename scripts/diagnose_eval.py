import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("data/evaluation/eval_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for r in data["results"]:
    if not r["top1_match"]:
        print("=" * 60)
        print(f"ID: {r['id']} | Category: {r['category']}")
        print(f"Query:    {r['query']}")
        print(f"Target:   {r['target_text']} (ID: {r['expected_message_id']})")
        print(f"Pred:     {r['predicted_text']} (ID: {r['predicted_message_id']})")
        print("Top 3 retrieved:")
        for c in r["top_candidates"]:
            print(f"  - [{c['message_id']}] (final={c['final_score']}, sem={c['semantic_score']}, lex={c['lexical_score']}): {c['text'][:60]}")
