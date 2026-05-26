from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid
from pydantic import BaseModel, Field

class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"

class MCPConnection(BaseModel):
    mcp_id:str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    is_active: bool = True

class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    agent_name: str
    system_prompt: str
    llm_id: str
    mcp_connections: list[MCPConnection] = Field(default_factory=list)
    context_limit: int = 20
    max_iterations: int = 10
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    agent_id: str
    user_id: str
    status: ConversationStatus = ConversationStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_message_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chat_id: str
    tenant_id: str
    role: MessageRole
    message_content: str
    sequence: int
    token_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None