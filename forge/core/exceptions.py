from datetime import datetime, timezone


class ForgeError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: list | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(ForgeError):
    def __init__(self, resource: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found",
            status_code=404,
        )


class AuthenticationError(ForgeError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code="AUTHENTICATION_REQUIRED",
            message=message,
            status_code=401,
        )


class AuthorizationError(ForgeError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403,
        )


class ValidationError(ForgeError):
    def __init__(self, details: list):
        super().__init__(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=400,
            details=details,
        )
