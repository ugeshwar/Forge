from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from forge.config.settings import settings
from forge.core.logger import get_logger

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None

async def connect() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.mongo_url, serverSelectionTimeoutMS=5000, connectTimeoutMS=3000)
    await _client.admin.command("ping")
    logger.info("mongodb_connected")

async def disconnect() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("mongodb_disconnected")

def get_database() -> AsyncIOMotorDatabase:
    if not _client:
        raise RuntimeError("MongoDB not connected")
    return _client[settings.mongo_db_name]