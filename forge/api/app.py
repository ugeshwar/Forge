from fastapi import FastAPI
from forge.config.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    @app.get("/health")
    async def health() -> dict:
        return {
            "status": "ok",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    return app


app = create_app()
