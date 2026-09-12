from typing import Optional, List
from pydantic import BaseModel

class DecisionItem(BaseModel):
    id: str
    title: str
    topic: str
    decision: str
    message_id: str
    participant: str
    timestamp: str
    context_summary: str
    status: str = "Confirmed"
    icon: Optional[str] = "check-circle"
