from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from forge.api.schemas.chat import ChatRequest
from forge.core.agents.service import AgentService
from forge.api.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    service = AgentService(tenant_id=current_user["tenant_id"])

    return StreamingResponse(
        service.stream_chat(
            agent_id=request.agent_id,
            chat_id=request.chat_id,
            user_message=request.message,
            user_id=current_user["sub"]
        ),
        media_type="text/event_stream"
    )