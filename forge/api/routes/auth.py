from fastapi import APIRouter, Depends
from forge.core.auth.jwt import blacklist_token, create_access_token
from forge.api.deps import get_current_user
from forge.api.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from forge.core.auth.service import AuthService
from forge.infra.db.repositories.token_repository import TokenRepository
from forge.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=201)
async def register(payload: RegisterRequest) -> dict:
    service = AuthService(tenant_id=payload.tenant_id)
    await service.repo.ensure_indexes()
    user = await service.register(
        email=payload.email,
        password=payload.password
    )
    return {
        "message": "User Registered Successfully",
        "user_id": user.id,
        "tenant_id": user.tenant_id
    }

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    service = AuthService(tenant_id=payload.tenant_id)
    result = await service.login(
        email=payload.email,
        password=payload.password
    )
    return TokenResponse(**result)

@router.post("/logout", status_code=200)
async def logout(current_user: dict = Depends(get_current_user)) -> dict:
    await blacklist_token(jti=current_user["jti"], exp=current_user["exp"],)
    return  {"message": "Logged Out Successfully"}

@router.post("/refresh")
async def refresh(payload: dict) -> dict:
    raw_token = payload.get("refresh_token")
    tenant_id = payload.get("tenant_id")

    if not raw_token or not tenant_id:
        from forge.core.exceptions import ValidationError
        raise ValidationError(details=[
            {"field": "refresh_token", "message": "Required"}
        ])
    
    token_repo = TokenRepository(tenant_id=tenant_id)
    refresh_token = await token_repo.find_and_rotate(raw_token=raw_token)

    if not refresh_token:
        from forge.core.exceptions import AuthenticationError
        raise AuthenticationError("Invalid or Expired refresh token")
    
    new_access_token = create_access_token(
        user_id=refresh_token.user_id,
        tenant_id=refresh_token.tenant_id,
        role="user",
    )

    new_refresh_token = await token_repo.create_refresh_token(user_id=refresh_token.user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 900,
    }