"""
RecallX Index Builder
Generates dense embeddings for all 5,200 messages and initializes SQLite FTS5 database.
"""

import sys
import os

# Ensure project root is in python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from app.indexing.index_manager import IndexManager

if __name__ == "__main__":
    print("=" * 60)
    print("RECALLX EMBEDDINGS & LEXICAL INDEX BUILDER")
    print("=" * 60)
    manager = IndexManager.get_instance()
    manager.initialize(force_rebuild=True)
    print("[SUCCESS] Index build complete!")
