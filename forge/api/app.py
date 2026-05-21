from fastapi import FastAPI
from forge.config.settings import settings
from forge.core.logger import setup_logging, get_logger
from forge.api.middleware import RequestMiddleware

logger = get_logger(__name__)


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    app.add_middleware(RequestMiddleware)

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
