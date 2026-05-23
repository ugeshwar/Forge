from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from forge.core.auth.jwt import decode_access_token
from forge.core.auth.models import UserRole
from forge.core.context import tenant_id_var, get_current_user_context
from forge.core.exceptions import AuthenticationError, AuthorizationError

bearer_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),) -> dict:
    cached = get_current_user_context()
    if cached:
        return cached
    
    token = credentials.credentials
    payload = decode_access_token(token)
    tenant_id_var.set(payload["tenant_id"])
    return payload

def require_role(required_role: UserRole):
    async def role_checker(currrent_user: dict = Depends(get_current_user),) -> dict:
        if currrent_user["role"] != required_role:
            raise AuthorizationError()
        return currrent_user
    return role_checker