import uuid
from datetime import datetime, timedelta, timezone
from forge.infra.db.mongo import get_database
from forge.core.auth.models import User, UserRole
from forge.core.auth.security import hash_password
from forge.core.logger import get_logger

logger = get_logger(__name__)

class UserRepository:
    def __init__(self, tenant_id: str):
        self.db = get_database()
        self.collection = self.db.users
        self.tenant_id = tenant_id

    async def find_by_email(self, email: str) -> User | None:
        doc = await self.collection.find_one({
            "tenant_id": self.tenant_id,
            "email": email, 
        })
        return User(**doc) if doc else None
    
    async def find_by_id(self, user_id: str) -> User | None:
        doc = await self.collection.find_one({
            "tenant_id": self.tenant_id,
            "id": user_id,
        })
    
    async def create(
        self,
        email: str,
        password: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        now = datetime.now(timezone.utc)
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hash_password(password),
            tenant_id=self.tenant_id,
            role=role,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        await self.collection.insert_one(user.model_dump())
        logger.info("user_created", user_id=user.id, tenant_id=self.tenant_id)
        return user
    
    async def ensure_indexes(self) -> None:
        await self.collection.create_index(
            [("tenant_id", 1), ("email", 1)],
            unique = True
        )