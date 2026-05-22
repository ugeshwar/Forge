from fastapi import FastAPI, Depends
from forge.config.settings import settings
from forge.core.logger import setup_logging, get_logger
from forge.api.middleware import RequestMiddleware
from forge.api.error_handler import register_error_handlers
from forge.infra.db.mongo import connect as mongo_connect, disconnect as mongo_disconnect
from forge.infra.cache.redis import connect as redis_connect, disconnect as redis_disconnect
from forge.infra.db.mongo import get_database
from forge.infra.cache.redis import get_client
from contextlib import asynccontextmanager
from forge.api.deps import get_current_user
from forge.api.routes.auth import router as auth_router

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
        lifespan=lifespan,
    )

    app.add_middleware(RequestMiddleware)
    register_error_handlers(app)
    app.include_router(auth_router)

    @app.get("/me")
    async def me(current_user: dict = Depends(get_current_user)) -> dict:
        return current_user

    @app.get("/health")
    async def health() -> dict:
        logger.info("health_check_called")

        mongo_status = "ok"

        try:
            await get_database().command("ping")
        except Exception as e:
            mongo_status = f"error: {str(e)}"

        redis_status = "ok"

        try:
            await get_client().ping()
        except Exception as e:
            redis_status = f"error: {str(e)}"
        
        overall = "ok" if mongo_status == "ok" and redis_status == "ok" else "degraded"

        return {
            "status": overall,
            "app": settings.app_name,
            "version": settings.app_version,
            "dependencies": {
                "mongodb": mongo_status,
                "redis": redis_status,
                }
        }

    return app


app = create_app()
