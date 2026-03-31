from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BUSINESS_ERROR = "BUSINESS_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppException(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Any = None,
        status_code: int = 400,
    ):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource}不存在"
        if identifier is not None:
            message = f"{resource}(id={identifier})不存在"
        super().__init__(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            status_code=404,
        )


class AlreadyExistsException(AppException):
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            message=f"{resource}的{field}='{value}'已存在",
            status_code=400,
        )


class ValidationException(AppException):
    def __init__(self, message: str, details: Any = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=422,
        )


class BusinessException(AppException):
    def __init__(self, message: str, details: Any = None):
        super().__init__(
            code=ErrorCode.BUSINESS_ERROR,
            message=message,
            details=details,
            status_code=400,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "未授权访问"):
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=401,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            status_code=403,
        )
