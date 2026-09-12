import json
import os
from typing import List, Dict, Any, Optional
from ..config import DECISIONS_FILE
from ..models.decision import DecisionItem
from ..indexing.lexical_index import LexicalIndex
from ..config import SQLITE_DB

class DecisionDetector:
    def __init__(self, lexical_index: Optional[LexicalIndex] = None):
        self.lexical_index = lexical_index or LexicalIndex(SQLITE_DB)
        self.canonical_file = DECISIONS_FILE

    def get_detected_decisions(self) -> List[DecisionItem]:
        """
        Loads the verified decisions detected from the corpus.
        """
        if self.canonical_file.exists():
            with open(self.canonical_file, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
                return [DecisionItem(**item) for item in raw_list]

        # Fallback to query database for decision-flagged messages
        db_decisions = self.lexical_index.get_decisions()
        results = []
        for idx, d in enumerate(db_decisions, 1):
            results.append(DecisionItem(
                id=f"dec_{idx:02d}",
                title=f"Decision #{idx}",
                topic=d.get("thread_id", "General"),
                decision=d.get("text", ""),
                message_id=d.get("id"),
                participant=d.get("participant_name", "Group"),
                timestamp=d.get("timestamp", ""),
                context_summary="Identified consensus point in conversation.",
                status="Confirmed",
                icon="check-circle"
            ))
        return results
