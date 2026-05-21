from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from forge.core.exceptions import ForgeError
from forge.core.context import get_request_id
from forge.core.logger import get_logger
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = get_logger(__name__)


def _error_response(
    code: str,
    message: str,
    status_code: int,
    request_id: str,
    details: list | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": details,
            }
        },
    )


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = get_request_id()
        logger.warning(
            "http_error",
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return _error_response(
            code="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=request_id,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = get_request_id()
        logger.warning(
            "http_error",
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return _error_response(
            code="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=request_id,
        )

    @app.exception_handler(ForgeError)
    async def forge_error_handler(request: Request, exc: ForgeError):
        request_id = get_request_id()
        logger.warning(
            "forge_error",
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
        )
        return _error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            request_id=request_id,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        request_id = get_request_id()
        details = [
            {
                "field": ".".join(str(l) for l in err["loc"]),
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        logger.warning("validation_error", details=details)
        return _error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=422,
            request_id=request_id,
            details=details,
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        request_id = get_request_id()
        logger.error(
            "unhandled_error",
            error_type=type(exc).__name__,
            error=str(exc),
        )
        return _error_response(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            status_code=500,
            request_id=request_id,
        )
