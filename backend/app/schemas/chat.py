from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
    context: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    sources: Optional[List[str]] = None
