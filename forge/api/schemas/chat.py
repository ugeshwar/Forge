from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    agent_id: str
    chat_id: Optional[str] = None
    message: str