import uvicorn
from forge.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "forge.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
