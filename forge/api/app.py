from fastapi import FastAPI
from forge.config.settings import settings
from forge.core.logger import setup_logging, get_logger
from forge.api.middleware import RequestMiddleware
from forge.api.error_handler import register_error_handlers
from forge.infra.db.mongo import connect as mongo_connect, disconnect as mongo_disconnect
from forge.infra.cache.redis import connect as redis_connect, disconnect as redis_disconnect
from contextlib import asynccontextmanager

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("forge_starting")
    await mongo_connect()
    await redis_connect()
    logger.info("forge_ready")
    yield
    logger.info("forge_stopping")
    await mongo_disconnect()
    await redis_disconnect()

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    app.add_middleware(RequestMiddleware)
    register_error_handlers(app)

    @app.get("/health")
    async def health() -> dict:
        logger.info("health_check_called")
        return {
            "status": "ok",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    return app


app = create_app()
