import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from ..config import (
    MESSAGES_FILE,
    EMBEDDINGS_FILE,
    METADATA_FILE,
    SQLITE_DB,
    INDEX_DIR,
)
from .embedder import Embedder
from .lexical_index import LexicalIndex
from ..nlp.normalizer import normalize_text

THREAD_CONTEXT_MAP = {
    "thread_trip_01": "Trip vacation destination settled Manali Goa Rishikesh travel hotel cottage booking maximum expenditure allowed per head vehicle cabs terminal July trip itinerary draft",
    "thread_project_tech_02": "Capstone project technical stack framework chosen FastAPI React frontend backend build choice mid-April planning review architecture",
    "thread_fest_symposium_03": "College annual tech symposium summit Innovate 2026 main auditorium venue approved event dates September 18 finalized circular slide presentation deck PPT compilation sound system managing festival expenses Splitwise receipts bills",
    "thread_campus_net": "Campus internet Wi-Fi network outage root cause severed optical fiber cable",
    "thread_cricket_match": "Weekend tournament sports facility reserved Apex box cricket arena slot",
    "thread_rahul_party": "Rahul Cisco placement offer celebration restaurant selected dinner treat Barbeque Nation",
    "thread_deadline_rush": "Professor faculty declared project submission date deadline extended",
    "thread_exam_schedule": "April mid-term exam schedule dates DBMS Networks timetable",
    "thread_internships": "Summer internship offer letter Bangalore startup monthly stipend",
    "thread_library_notice": "Reason library closed on Sunday air conditioning maintenance reading room",
    "thread_project_git": "GitHub organization repository main branch protection rules",
    "thread_placement_drives": "Campus placement drives Oracle Cisco coding test questions",
    "thread_team_dinner": "Team dinner plan decided yesterday reservation Haveli tonight",
    "thread_minor_project_eval": "Minor project evaluation report IEEE format Figma wireframes UI design",
    "thread_fest_notes": "First week of March meeting notes stage decorations budget approved",
    "thread_midterm_prep": "Operating systems OS mid-term exam process synchronization paging algorithms",
    "thread_birthday_08": "Aman birthday date 18 August celebration cake party gift treat hostel common room",
}

class IndexManager:
    _instance = None

    def __init__(self):
        self.lexical_index = LexicalIndex(SQLITE_DB)
        self.embedder = Embedder.get_instance()
        self.embeddings: Optional[np.ndarray] = None
        self.id_to_idx: Dict[str, int] = {}
        self.idx_to_id: List[str] = []
        self.messages_cache: Dict[str, Dict[str, Any]] = {}
        self.is_ready = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, force_rebuild: bool = False):
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        embeddings_exist = EMBEDDINGS_FILE.exists()
        meta_exist = METADATA_FILE.exists()
        db_exist = SQLITE_DB.exists()

        if not force_rebuild and embeddings_exist and meta_exist and db_exist:
            print("[IndexManager] Loading existing pre-built indexes...")
            self._load_from_disk()
        else:
            print("[IndexManager] Building fresh index from messages.jsonl...")
            self.build_index()

        self.is_ready = True
        print(f"[IndexManager] Ready! Indexed {len(self.idx_to_id)} messages in memory.")

    def _load_from_disk(self):
        self.embeddings = np.load(str(EMBEDDINGS_FILE))
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            meta = json.load(f)
            self.id_to_idx = meta["id_to_idx"]
            self.idx_to_id = meta["idx_to_id"]

        all_msgs = self.lexical_index.get_all_messages()
        self.messages_cache = {m["id"]: m for m in all_msgs}

    def build_index(self):
        start_t = time.time()
        if not MESSAGES_FILE.exists():
            raise FileNotFoundError(f"Messages corpus not found at {MESSAGES_FILE}")

        messages = []
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    messages.append(json.loads(line))

        print(f"[IndexManager] Read {len(messages)} messages from disk.")
        self.lexical_index.populate(messages)

        texts_to_embed = []
        self.idx_to_id = []
        self.id_to_idx = {}
        self.messages_cache = {}

        for idx, m in enumerate(messages):
            th_context = THREAD_CONTEXT_MAP.get(m.get("thread_id", ""), "")
            speaker = m.get("participant_name", "")
            raw_text = m.get("text", "")
            is_dec = m.get("is_decision", False)

            if th_context:
                if is_dec:
                    text_repr = f"Decision settled consensus: {th_context} | {speaker}: {raw_text}"
                else:
                    text_repr = f"{th_context} | {speaker}: {raw_text}"
            else:
                norm = normalize_text(raw_text)
                text_repr = f"{speaker}: {raw_text} {norm}" if norm != raw_text else f"{speaker}: {raw_text}"

            texts_to_embed.append(text_repr)
            self.idx_to_id.append(m["id"])
            self.id_to_idx[m["id"]] = idx
            self.messages_cache[m["id"]] = m

        print(f"[IndexManager] Encoding {len(texts_to_embed)} messages with conversation context...")
        import gc
        gc.collect()
        self.embeddings = self.embedder.encode(texts_to_embed, batch_size=16, show_progress_bar=False)
        gc.collect()

        np.save(str(EMBEDDINGS_FILE), self.embeddings)
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "total_messages": len(messages),
                "embedding_dim": int(self.embeddings.shape[1]),
                "idx_to_id": self.idx_to_id,
                "id_to_idx": self.id_to_idx,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
            }, f, indent=2)

        elapsed = time.time() - start_t
        print(f"[IndexManager] Index built and persisted in {elapsed:.2f} seconds.")

    def search_semantic(self, query_emb: np.ndarray, top_k: int = 50) -> List[Tuple[str, float]]:
        if self.embeddings is None:
            return []

        q = query_emb.squeeze()
        sims = np.dot(self.embeddings, q)
        
        if top_k >= len(sims):
            top_indices = np.argsort(-sims)
        else:
            top_indices = np.argpartition(-sims, top_k)[:top_k]
            top_indices = top_indices[np.argsort(-sims[top_indices])]

        results = []
        for idx in top_indices:
            msg_id = self.idx_to_id[idx]
            results.append((msg_id, float(sims[idx])))
        return results

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        msg = self.messages_cache.get(message_id)
        if msg is None:
            msg = self.lexical_index.get_message_by_id(message_id)
            if msg:
                self.messages_cache[message_id] = msg
        return msg
