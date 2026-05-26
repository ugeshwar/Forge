from pydantic import BaseModel
from typing import Optional
from forge.core.agents.models import MCPConnection


class CreateAgentRequest(BaseModel):
    agent_name: str
    system_prompt: str
    llm_id: str
    mcp_connections: list[MCPConnection] = []
    context_limit: int = 20
    max_iterations: int = 10