"""共享异常定义"""

from __future__ import annotations


class AppError(Exception):
    """应用基础异常"""

    def __init__(self, message: str, code: str, status_code: int) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppError):
    """资源不存在"""

    def __init__(self, resource: str, identifier: str | None = None) -> None:
        msg = f"{resource} not found"
        if identifier:
            msg += f": {identifier}"
        super().__init__(msg, "NOT_FOUND", 404)


class ValidationError(AppError):
    """参数校验失败"""

    def __init__(self, errors: list[dict[str, object]]) -> None:
        super().__init__("Validation failed", "VALIDATION_ERROR", 422)
        self.errors = errors


class AuthenticationError(AppError):
    """认证失败"""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message, "AUTHENTICATION_REQUIRED", 401)


class PermissionError(AppError):
    """权限不足"""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, "PERMISSION_DENIED", 403)


class ConflictError(AppError):
    """资源冲突"""

    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, "CONFLICT", 409)
