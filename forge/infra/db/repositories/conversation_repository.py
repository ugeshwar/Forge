from datetime import datetime, timezone
from forge.core.agents.models import Conversation, ConversationStatus, Message
from forge.infra.db.mongo import get_database
from forge.config.settings import settings

class ConversationRepository:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.db = get_database()
        self.col_conversations = self.db[settings.mongo_db_name]["conversations"]
        self.col_messages = self.db[settings.mongo_db_name]["messages"]

    async def create_conversation(self, conversation: Conversation) -> Conversation | None:
        await self.col_conversations.insert_one(conversation.model_dump())
        return conversation
    
    async def find_conversation(self, chat_id: str) -> Conversation | None:
        doc = await self.col_conversations.find_one(
            {"id": chat_id, "tenant_id": self.tenant_id},
            {"_id": 0}
        )
        if not doc:
            return None
        return Conversation(**doc)
    
    async def add_message(self, message: Message) -> Message:
        await self.col_messages.insert_one(message.model_dump())
        await self.col_conversations.update_one(
            {"id": message.chat_id, "tenant_id": self.tenant_id},
            {"$set": {"last_message_at": datetime.now(timezone.utc)}}
        )
        return message
    
    async def get_message(self, chat_id: str, limit: int = 50) -> list[Message]:
        cursor = self.col_messages.find(
            {"chat_id": chat_id, "tenant_id": self.tenant_id},
            {"_id": 0}
        ).sort("sequence", 1).limit(limit)
        return [Message(**doc) async for doc in cursor]
    
    async def get_next_sequence(self, chat_id: str) -> int:
        last = await self.col_messages.find_one(
            {"chat_id": chat_id},
            {"_id": 0, "sequence": 1},
            sort = [("sequence", -1)]
        )
        return (last["sequence"] + 1) if last else 1
    
    async def ensure_indexes(self) -> None:
        await self.col_conversations.create_index(
            [("tenant_id", 1), ("id", 1)],
            unique = True
        )
        await self.col_messages.create_index(
            [("tenant_id", 1), ("chat_id", 1), ("sequence", 1)]
        )