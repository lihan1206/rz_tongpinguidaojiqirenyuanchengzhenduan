import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.exceptions import BusinessException, ErrorCode

logger = logging.getLogger(__name__)


def create_error_response(
    code: int,
    message: str,
    detail: Any = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    """创建统一的错误响应格式"""
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "detail": detail,
            "success": False,
        },
    )


def add_exception_handlers(app: FastAPI):
    """添加全局异常处理器"""

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        """处理自定义业务异常"""
        logger.warning(f"业务异常: {exc.error_code.code} - {exc.message}, detail: {exc.detail}")
        return create_error_response(
            code=exc.error_code.code,
            message=exc.message,
            detail=exc.detail,
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求参数校验异常"""
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": "->".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        logger.warning(f"请求参数校验失败: {errors}")
        return create_error_response(
            code=ErrorCode.VALIDATION_ERROR.code,
            message=ErrorCode.VALIDATION_ERROR.message,
            detail=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """处理Pydantic模型校验异常"""
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": "->".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        logger.warning(f"模型校验失败: {errors}")
        return create_error_response(
            code=ErrorCode.VALIDATION_ERROR.code,
            message=ErrorCode.VALIDATION_ERROR.message,
            detail=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """处理值错误异常"""
        logger.warning(f"值错误: {str(exc)}")
        return create_error_response(
            code=ErrorCode.BAD_REQUEST.code,
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """处理全局异常"""
        logger.exception(f"未捕获的异常: {str(exc)}")
        return create_error_response(
            code=ErrorCode.INTERNAL_ERROR.code,
            message=ErrorCode.INTERNAL_ERROR.message,
            detail=str(exc) if app.debug else None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )