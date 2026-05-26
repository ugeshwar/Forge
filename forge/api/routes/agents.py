from fastapi import APIRouter, Depends
from forge.infra.db.repositories.agent_repository import AgentRepository
from forge.api.deps import get_current_user, require_role
from forge.core.auth.models import UserRole
from forge.core.exceptions import NotFoundError
from forge.api.schemas.agent import CreateAgentRequest
from forge.core.agents.models import Agent
import uuid

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, current_user: dict = Depends(get_current_user)):
    repo = AgentRepository(tenant_id=current_user["tenant_id"])
    agent = await repo.find_by_id(agent_id)
    if not agent:
        raise NotFoundError(f"Agent {agent_id} not found")
    return agent

@router.get("", response_model=list[Agent])
async def list_agents(current_user: dict = Depends(get_current_user)):
    repo = AgentRepository(tenant_id=current_user["tenant_id"])
    return await repo.find_all()

@router.post("", response_model=Agent)
async def create_agent(
    payload: CreateAgentRequest,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    repo = AgentRepository(tenant_id=current_user["tenant_id"])
    agent = Agent(
        tenant_id=current_user["tenant_id"],
        **payload.model_dump()
    )
    return await repo.create(agent)