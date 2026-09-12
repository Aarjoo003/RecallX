import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("data/evaluation/eval_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for r in data["results"][:10]:
    if not r["top1_match"]:
        print("=" * 60)
        print(f"ID: {r['id']} | Query: {r['query']}")
        print(f"Target: [{r['expected_message_id']}] {r['target_text']}")
        print(f"Top Pred: [{r['predicted_message_id']}] {r['predicted_text']}")
        print("Top 3 retrieved:")
        for c in r["top_candidates"]:
            print(f"  - [{c['message_id']}] (final={c['final_score']}, sem={c['semantic_score']}, lex={c['lexical_score']}): {c['text'][:60]}")
