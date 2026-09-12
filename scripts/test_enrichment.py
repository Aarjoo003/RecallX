import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.abspath("backend"))
from app.indexing.embedder import Embedder

embedder = Embedder.get_instance()

# Query
query = "When did we finally settle on the destination?"
q_emb = embedder.encode(query)

raw_text = "Done bhai, Manali final. I'll book tomorrow."
raw_emb = embedder.encode(raw_text)

# Context-enriched text
enriched_text = "Trip destination discussion Manali Goa: Rahul: Goa tickets cancel kar doon pakka? Aman: Done bhai, Manali final. I'll book tomorrow."
enriched_emb = embedder.encode(enriched_text)

print(f"Query: '{query}'")
print(f"Similarity with raw text:     {float(np.dot(q_emb, raw_emb.T)):.4f}")
print(f"Similarity with enriched text: {float(np.dot(q_emb, enriched_emb.T)):.4f}")
