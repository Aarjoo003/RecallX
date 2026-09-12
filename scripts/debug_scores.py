import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, "backend")
from app.services.search_service import SearchService
from app.models.search import SearchRequest

service = SearchService.get_instance()
resp = service.search(SearchRequest(query="When did we finally settle on the destination?", limit=10))

print("Results for 'When did we finally settle on the destination?':")
for r in resp.results:
    print(f"[{r.message_id}] final={r.final_score:.4f} sem={r.semantic_score:.4f} lex={r.lexical_score:.4f} dec={r.decision_score:.2f}: {r.text[:60]}")

# Also check target directly
mgr = service.retriever.index_manager
target_id = "msg_3769"
t_msg = mgr.get_message(target_id)
q_emb = mgr.embedder.encode("When did we finally settle on the destination?")
t_idx = mgr.id_to_idx[target_id]
import numpy as np
t_sem = float(np.dot(mgr.embeddings[t_idx], q_emb.squeeze()))
print(f"Direct Target [{target_id}]: text='{t_msg['text']}' | sem={t_sem:.4f}")
