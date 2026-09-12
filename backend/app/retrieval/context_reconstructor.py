from typing import List, Dict, Any, Optional
from ..models.message import ContextMessage
from ..indexing.lexical_index import LexicalIndex
from ..config import SQLITE_DB

class ContextReconstructor:
    def __init__(self, lexical_index: Optional[LexicalIndex] = None):
        self.lexical_index = lexical_index or LexicalIndex(SQLITE_DB)

    def reconstruct_context(self, message_id: str, window_size: int = 3) -> List[ContextMessage]:
        """
        Reconstructs the surrounding chronological conversation context around a target message.
        """
        raw_msgs = self.lexical_index.get_context_messages(message_id, window_size=window_size)
        context_items = []
        for m in raw_msgs:
            context_items.append(ContextMessage(
                id=m["id"],
                participant_id=m["participant_id"],
                participant_name=m["participant_name"],
                timestamp=m["timestamp"],
                text=m["text"],
                thread_id=m.get("thread_id"),
                is_target=m.get("is_target", False),
                is_forwarded=bool(m.get("is_forwarded")),
                is_media=bool(m.get("is_media")),
            ))
        return context_items

    def get_full_thread(self, thread_id: str) -> List[ContextMessage]:
        """
        Fetches the complete conversation thread chronologically.
        """
        raw_msgs = self.lexical_index.get_thread(thread_id)
        thread_items = []
        for m in raw_msgs:
            thread_items.append(ContextMessage(
                id=m["id"],
                participant_id=m["participant_id"],
                participant_name=m["participant_name"],
                timestamp=m["timestamp"],
                text=m["text"],
                thread_id=m.get("thread_id") or thread_id,
                is_target=False,
                is_forwarded=bool(m.get("is_forwarded")),
                is_media=bool(m.get("is_media")),
            ))
        return thread_items
