import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.getenv("RECALLX_DATA_DIR", str(BASE_DIR / "data")))
INDEX_DIR = Path(os.getenv("RECALLX_INDEX_DIR", str(DATA_DIR / "index")))
EVAL_DIR = Path(os.getenv("RECALLX_EVAL_DIR", str(DATA_DIR / "evaluation")))

MESSAGES_FILE = Path(os.getenv("RECALLX_MESSAGES_FILE", str(DATA_DIR / "messages.jsonl")))
PARTICIPANTS_FILE = Path(os.getenv("RECALLX_PARTICIPANTS_FILE", str(DATA_DIR / "participants.json")))
DECISIONS_FILE = Path(os.getenv("RECALLX_DECISIONS_FILE", str(DATA_DIR / "decisions.json")))
QUESTIONS_FILE = Path(os.getenv("RECALLX_QUESTIONS_FILE", str(EVAL_DIR / "questions.json")))

SQLITE_DB = Path(os.getenv("RECALLX_SQLITE_DB", str(INDEX_DIR / "recallx.db")))
EMBEDDINGS_FILE = Path(os.getenv("RECALLX_EMBEDDINGS_FILE", str(INDEX_DIR / "embeddings.npy")))
METADATA_FILE = Path(os.getenv("RECALLX_METADATA_FILE", str(INDEX_DIR / "index_meta.json")))

MODEL_NAME = os.getenv("RECALLX_MODEL", "all-MiniLM-L6-v2")

# Corpus Reference Date (end of archive for relative temporal queries)
CORPUS_REFERENCE_DATE = "2026-09-10T23:59:59"

# Default Retrieval & Ranking Weights
DEFAULT_WEIGHTS = {
    "semantic": 0.55,
    "lexical": 0.20,
    "person": 0.15,
    "time": 0.10,
    "decision_boost": 0.25,
}

# Default Result Deduplication & Diversification Configuration
DEFAULT_DIVERSIFICATION = {
    "exact_threshold": 0.95,
    "near_dup_threshold": 0.70,
    "redundancy_penalty_weight": 0.45,
    "participant_novelty_bonus": 0.03,
    "corroboration_bonus": 0.04,
    "context_continuity_bonus": 0.03,
}

TOP_K_CANDIDATES = 100
DEFAULT_RESULTS_LIMIT = 8
DEFAULT_CONTEXT_WINDOW = 3

