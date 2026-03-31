from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AppException, ErrorCode


class ErrorResponse:
    def __init__(self, code: ErrorCode, message: str, details: any = None):
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self):
        result = {"code": self.code.value, "message": self.message}
        if self.details is not None:
            result["details"] = self.details
        return result


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(exc.code, exc.message, exc.details).to_dict(),
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            ErrorCode.VALIDATION_ERROR,
            "参数校验失败",
            exc.errors(),
        ).to_dict(),
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            ErrorCode.BUSINESS_ERROR,
            "数据操作冲突，请检查数据是否重复或存在关联约束",
        ).to_dict(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            ErrorCode.INTERNAL_ERROR,
            "服务器内部错误",
        ).to_dict(),
    )


def register_exception_handlers(app):
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
