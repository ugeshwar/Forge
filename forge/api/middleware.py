import uuid
import time
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from forge.infra.cache.redis import get_client
from forge.core.exceptions import ForgeError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from forge.core.context import request_id_var, get_request_id
from forge.core.logger import get_logger

logger = get_logger(__name__)

class RateLimitError(ForgeError):
    def __init__(self):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please slow down.",
            status_code=429,
        )
class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request_id_var.set(request_id)

        start = time.perf_counter()

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, user_limit: int = 60, tenant_limit: int = 1000, window_seconds: int = 60):
        super().__init__(app)
        self.user_limit = user_limit
        self.tenant_limit = tenant_limit
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        public_paths = {"/health", "/auth/login", "/auth/register", "/docs", "/openapi.json"}
        if request.url.path in public_paths:
            return await call_next(request)
        
        tenant_id = None
        user_id = None

        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            try:
                from forge.core.auth.jwt import decode_access_token
                from forge.core.context import current_user_var, tenant_id_var
                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)
                current_user_var.set(payload)
                tenant_id = payload.get("tenant_id")
                tenant_id_var.set(tenant_id)
                user_id = payload.get("sub")
            except Exception:
                pass

        if tenant_id and user_id:
            redis = get_client()

            user_key = f"rate_limit:user:{tenant_id}:{user_id}"
            user_count = await redis.incr(user_key)
            if user_count == 1:
                await redis.expire(user_key, self.window_seconds)
            if user_count > self.user_limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests. Please slow down.",
                            "request_id": get_request_id(),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "details": None,
                        }
                    }
                )
            
            tenant_key = f"rate_limit:tenant:{tenant_id}"
            tenant_count = await redis.incr(tenant_key)
            if tenant_count == 1:
                await redis.expire(tenant_key, self.window_seconds)
            if tenant_count > self.tenant_limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Tenant rate limit exceeded.",
                            "request_id": get_request_id(),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "details": None,
                        }
                    }
                )
        
        return await call_next(request)