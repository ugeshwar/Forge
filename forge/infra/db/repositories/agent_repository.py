from datetime import datetime, timezone
from forge.core.agents.models import Agent
from forge.infra.db.mongo import get_database
from forge.config.settings import settings

class AgentRepository:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.db = get_database()
        self.collection = self.db[settings.mongo_db_name]["agents"]

    async def create(self, agent: Agent) -> Agent:
        doc = agent.model_dump()
        doc["mcp_connections"] = [m.model_dump() for m in agent.mcp_connections]
        await self.collection.insert_one(doc)
        return agent
    
    async def find_by_id(self,agent_id: str) -> Agent | None:
        doc = await self.collection.find_one(
            {"id": agent_id, "tenant_id": self.tenant_id},
            {"_id": 0}
        )

        if not doc:
            return None
        return Agent(**doc)
    
    async def find_all(self) -> list[Agent]:
        cursor = self.collection.find(
            {"tenant_id": self.tenant_id, "is_active": True},
            {"_id": 0}
        )
        return [Agent(**doc) async for doc in cursor]
    
    async def ensure_indexes(self) -> None:
        await self.collection.create_index(
            [("tenant_id", 1), ("id", 1)],
            unique = True
        )