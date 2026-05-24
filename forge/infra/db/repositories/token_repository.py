import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from forge.infra.db.mongo import get_database
from forge.core.auth.models import RefreshToken
from forge.config.settings import settings
from forge.core.logger import get_logger

logger = get_logger(__name__)

class TokenRepository:
    def __init__(self, tenant_id: str):
        self.db = get_database()
        self.collection = self.db.refresh_tokens
        self.tenant_id = tenant_id

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def create_refresh_token(self, user_id: str) -> str:
        raw_token = secrets.token_urlsafe(64)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
        refresh_token = RefreshToken(id=str(uuid.uuid4()), user_id=user_id, tenant_id=self.tenant_id, token_hash=self._hash_token(raw_token), expires_at=expires_at, is_used=False, created_at=datetime.now(timezone.utc),)
        await self.collection.insert_one(refresh_token.model_dump())
        return raw_token
    
    async def find_and_rotate(self, raw_token: str) -> RefreshToken | None:
        token_hash = self._hash_token(raw_token)
        doc = await self.collection.find_one_and_update(
            {
                "tenant_id": self.tenant_id,
                "token_hash": token_hash,
                "is_used": False,
                "expires_at": {"$gt": datetime.now(timezone.utc)},
            },
            {"$set": {"is_used":True}},
            projection={"_id": 0},
        )
        return RefreshToken(**doc) if doc else None
    
    async def ensure_indexes(self) -> None:
        await self.collection.create_index(
            [("tenant_id", 1), ("token_hash", 1)],
            unique=True
        )