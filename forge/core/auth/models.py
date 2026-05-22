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