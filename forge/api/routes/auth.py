from fastapi import APIRouter
from forge.api.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from forge.core.auth.service import AuthService
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