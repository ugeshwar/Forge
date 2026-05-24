from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    AGENT = "agent"

class User(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    tenant_id: str
    role: UserRole
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class RefreshToken(BaseModel):
    id: str
    user_id: str
    tenant_id: str
    token_hash: str
    expires_at: datetime
    is_used: bool = False
    created_at: datetime