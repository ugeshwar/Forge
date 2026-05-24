from forge.core.auth.models import User, UserRole
from forge.core.auth.security import verify_password
from forge.core.auth.jwt import create_access_token
from forge.core.exceptions import AuthenticationError, AuthorizationError, ValidationError
from forge.infra.db.repositories.user_repository import UserRepository
from forge.core.logger import get_logger

logger = get_logger(__name__)

class AuthService:
    def __init__(self, tenant_id: str):
        self.repo = UserRepository(tenant_id=tenant_id)
        self.tenant_id = tenant_id

    async def register(self, email: str, password: str) -> User:
        
        existing = await self.repo.find_by_email(email)
        
        if existing:
            raise ValidationError(details=[{
                "field": "email",
                "message": "Email already Registered"
            }])
        
        if len(password) < 8:
            raise ValidationError(details=[{
                "field": "password",
                "message": "Password must be at least 8 characters"
            }])
        
        user = await self.repo.create(email=email, password=password, role=UserRole.USER)

        return user
    
    async def login(self, email: str, password: str) -> dict:
        from forge.infra.db.repositories.token_repository import TokenRepository

        user = await self.repo.find_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid Email or Password")
        
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        token = create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role,
        )

        token_repo = TokenRepository(tenant_id=self.tenant_id)
        await token_repo.ensure_indexes()
        refresh_token = await token_repo.create_refresh_token(user_id=user.id)

        logger.info("user_logged_in", user_id=user.id, tenant_id=self.tenant_id)

        return {
            "access_token": token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,
        }