import sqlite3
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from ..config import SQLITE_DB
from ..nlp.normalizer import tokenize, normalize_text

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}
HINGLISH_STOP_WORDS = {
    "hai", "h", "ka", "ki", "ke", "ko", "me", "mein", "se", "ne", "tha", "thi", "the",
    "kya", "bhai", "yaar", "yr", "na", "to", "bhi", "ho", "gaya", "gayi", "karna", "krna",
    "mera", "meri", "mere", "hum", "hume", "humara", "apna", "apni", "kuch", "sab", "sabhi"
}

ALL_STOP_WORDS = STOP_WORDS | HINGLISH_STOP_WORDS

class LexicalIndex:

    def __init__(self, db_path: Path = SQLITE_DB):
        self.db_path = str(db_path)
        self._ensure_tables()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    participant_id TEXT,
                    participant_name TEXT,
                    timestamp TEXT,
                    text TEXT,
                    normalized_text TEXT,
                    thread_id TEXT,
                    reply_to TEXT,
                    message_type TEXT,
                    is_forwarded INTEGER,
                    is_media INTEGER,
                    is_decision INTEGER
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id);
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_participant ON messages(participant_id);
            """)

            cur.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                    id UNINDEXED,
                    text,
                    normalized_text,
                    participant_name,
                    thread_id
                );
            """)
            conn.commit()

    def populate(self, messages: List[Dict[str, Any]]):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM messages")
            cur.execute("DELETE FROM messages_fts")

            msg_rows = []
            fts_rows = []
            for m in messages:
                norm_text = normalize_text(m["text"])
                msg_rows.append((
                    m["id"],
                    m["participant_id"],
                    m["participant_name"],
                    m["timestamp"],
                    m["text"],
                    norm_text,
                    m["thread_id"],
                    m.get("reply_to"),
                    m.get("message_type", "text"),
                    1 if m.get("is_forwarded") else 0,
                    1 if m.get("is_media") else 0,
                    1 if m.get("is_decision") else 0,
                ))
                fts_rows.append((
                    m["id"],
                    m["text"],
                    norm_text,
                    m["participant_name"],
                    m["thread_id"],
                ))

            cur.executemany("""
                INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, msg_rows)

            cur.executemany("""
                INSERT INTO messages_fts VALUES (?,?,?,?,?)
            """, fts_rows)

            conn.commit()
            print(f"[LexicalIndex] Indexed {len(messages)} messages successfully.")

    def search_lexical(self, query: str, limit: int = 50) -> List[Tuple[str, float]]:
        """
        Executes BM25 search over FTS5 with stop-words removed to prevent noisy false positives.
        Normalizes Hinglish abbreviations so words like 'bday' match 'birthday'.
        """
        normalized_q = normalize_text(query)
        raw_tokens = tokenize(normalized_q)
        # Filter English & Hinglish stop words
        content_tokens = [t for t in raw_tokens if t not in ALL_STOP_WORDS and len(t) > 2]
        if not content_tokens:
            # Fallback for short queries (e.g. "trip", "venue")
            content_tokens = [t for t in tokenize(query) if len(t) > 2]
            if not content_tokens:
                return []

        clean_tokens = [re.sub(r"[^\w]", "", t) for t in content_tokens]
        clean_tokens = [t for t in clean_tokens if t]
        if not clean_tokens:
            return []

        fts_query = " OR ".join(clean_tokens)

        with self.get_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT id, bm25(messages_fts) as rank_score
                    FROM messages_fts
                    WHERE messages_fts MATCH ?
                    ORDER BY rank_score ASC
                    LIMIT ?
                """, (fts_query, limit))
                rows = cur.fetchall()

                if not rows:
                    return []

                min_score = abs(rows[0]["rank_score"]) if rows else 1.0
                results = []
                for r in rows:
                    raw_score = r["rank_score"]
                    norm_score = max(0.0, min(1.0, abs(raw_score) / (min_score + 10.0)))
                    results.append((r["id"], norm_score))
                return results
            except sqlite3.OperationalError:
                return []

    def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
            row = cur.fetchone()
            if row:
                return dict(row)
            return None

    def get_context_messages(self, message_id: str, window_size: int = 3) -> List[Dict[str, Any]]:
        target = self.get_message_by_id(message_id)
        if not target:
            return []

        thread_id = target["thread_id"]
        target_time = target["timestamp"]

        with self.get_connection() as conn:
            cur = conn.cursor()

            # Preceding messages in thread
            cur.execute("""
                SELECT * FROM messages
                WHERE thread_id = ? AND timestamp < ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (thread_id, target_time, window_size))
            preceding = [dict(r) for r in cur.fetchall()]
            preceding.reverse()

            # Following messages in thread
            cur.execute("""
                SELECT * FROM messages
                WHERE thread_id = ? AND timestamp > ?
                ORDER BY timestamp ASC
                LIMIT ?
            """, (thread_id, target_time, window_size))
            following = [dict(r) for r in cur.fetchall()]

            context = []
            for m in preceding:
                m["is_target"] = False
                context.append(m)

            target["is_target"] = True
            context.append(target)

            for m in following:
                m["is_target"] = False
                context.append(m)

            return context

    def get_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM messages
                WHERE thread_id = ?
                ORDER BY timestamp ASC
            """, (thread_id,))
            return [dict(r) for r in cur.fetchall()]

    def get_all_messages(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM messages ORDER BY timestamp ASC")
            return [dict(r) for r in cur.fetchall()]

    def get_decisions(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM messages
                WHERE is_decision = 1
                ORDER BY timestamp ASC
            """)
            return [dict(r) for r in cur.fetchall()]

    def get_messages_by_time_range(self, start_iso: str, end_iso: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM messages
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC
                LIMIT ?
            """, (start_iso, end_iso, limit))
            return [dict(r) for r in cur.fetchall()]

    def get_messages_by_participant(self, participant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM messages
                WHERE participant_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (participant_id, limit))
            return [dict(r) for r in cur.fetchall()]
