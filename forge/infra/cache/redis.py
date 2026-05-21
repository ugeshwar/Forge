import redis.asyncio as aioredis
from forge.config.settings import settings
from forge.core.logger import get_logger

logger = get_logger(__name__)

_client: aioredis.Redis | None = None

async def connect() -> None:
    global _client
    _client = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
    )
    await _client.ping()
    logger.info("redis_connected")

async def disconnect() -> None:
    global _client
    if _client:
        await _client.aclose()
        logger.info("redis_disconnected")

def get_client() -> aioredis.Redis:
    if not _client:
        raise RuntimeError("Redis not connected")
    return _client