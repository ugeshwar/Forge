from datetime import datetime, timezone
from openai import AsyncOpenAI
from forge.config.settings import settings
from forge.core.agents.models import Agent, Conversation, Message, MessageRole
from forge.core.exceptions import NotFoundError
from forge.infra.db.repositories.agent_repository import AgentRepository
from forge.infra.db.repositories.conversation_repository import ConversationRepository

class AgentService:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.agent_repo = AgentRepository(tenant_id)
        self.conversation_repo = ConversationRepository(tenant_id)
        self.client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key
        )
    
    async def get_or_create_conversation(
            self, chat_id: str | None, agent_id: str, user_id: str
    ) -> Conversation:
        if chat_id:
            conv = await self.conversation_repo.find_conversation(chat_id)
            if conv:
                return conv
        conv = Conversation(
            tenant_id=self.tenant_id,
            agent_id=agent_id,
            user_id=user_id
        )
        return await self.conversation_repo.create_conversation(conv)
    
    async def stream_chat(
            self,
            agent_id: str,
            chat_id: str | None,
            user_message: str,
            user_id: str
    ):
        agent = await self.agent_repo.find_by_id(agent_id)
        if not agent:
            raise NotFoundError(f"Agent {agent_id} not found")
        
        conversation = await self.get_or_create_conversation(chat_id, agent_id, user_id)

        yield f"data: {{\"chat_id\": \"{conversation.id}\"}}\n\n"

        sequence = await self.conversation_repo.get_next_sequence(conversation.id)
        user_msg = Message(
            chat_id=conversation.id,
            tenant_id=self.tenant_id,
            role=MessageRole.USER,
            message_content=user_message,
            sequence=sequence
        )

        await self.conversation_repo.add_message(user_msg)

        history = await self.conversation_repo.get_message(conversation.id, limit=agent.context_limit)
        
        messages = [{"role": "system", "content": agent.system_prompt}]

        for msg in history:
            messages.append({
                "role": msg.role.value,
                "content": msg.message_content
            })
        
        full_response = ""

        stream = await self.client.chat.completions.create(
            model=settings.default_model,
            messages=messages,
            stream=True
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                yield f"data: {delta}\n\n"

        next_sequence = await self.conversation_repo.get_next_sequence(conversation.id)
        assistant_msg = Message(
            chat_id=conversation.id,
            tenant_id=self.tenant_id,
            role=MessageRole.ASSISTANT,
            message_content=full_response,
            sequence=next_sequence
        )

        await self.conversation_repo.add_message(assistant_msg)

        yield f"data: [DONE]\n\n"