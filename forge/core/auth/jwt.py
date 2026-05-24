import uuid
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from forge.config.settings import settings
from forge.core.exceptions import AuthenticationError

def create_access_token(user_id: str, tenant_id: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

async def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "access":
            raise AuthenticationError("Invalid Token Type")
        if await is_token_blacklisted(payload["jti"]):
            raise AuthenticationError("Token has been revoked")
        return payload
    except JWTError:
        raise AuthenticationError("Invalid or Expired Token")
    
async def blacklist_token(jti: str, exp: int) -> None:
    from forge.infra.cache.redis import get_client
    from datetime import datetime, timezone
    redis = get_client()
    remaining = exp - int(datetime.now(timezone.utc).timestamp())
    if remaining > 0:
        await redis.setex(f"blacklist:jti:{jti}", remaining, "1")

async def is_token_blacklisted(jti:str) -> bool:
    from forge.infra.cache.redis import get_client
    redis = get_client()
    return await redis.exists(f"blacklist:jti:{jti}") > 0