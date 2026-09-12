from typing import Optional, List
from pydantic import BaseModel, Field

class Participant(BaseModel):
    id: str
    name: str
    handle: str
    role: str
    color: str
    avatar: str

class Message(BaseModel):
    id: str
    participant_id: str
    participant_name: str
    timestamp: str
    text: str
    thread_id: str
    reply_to: Optional[str] = None
    message_type: str = "text"
    is_forwarded: bool = False
    is_media: bool = False
    is_decision: bool = False
    normalized_text: Optional[str] = None

class ContextMessage(BaseModel):
    id: str
    participant_id: str
    participant_name: str
    timestamp: str
    text: str
    thread_id: Optional[str] = None
    is_target: bool = False
    is_forwarded: bool = False
    is_media: bool = False
