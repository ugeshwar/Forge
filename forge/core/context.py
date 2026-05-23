from contextvars import ContextVar
from typing import Optional

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
tenant_id_var: ContextVar[str] = ContextVar("tenant_id", default="")
current_user_var: ContextVar[Optional[dict]] = ContextVar("current_user", default=None)

def get_request_id() -> str:
    return request_id_var.get()

def get_tenant_id() -> str:
    return tenant_id_var.get()

def get_current_user_context() -> Optional[dict]:
    return current_user_var.get()