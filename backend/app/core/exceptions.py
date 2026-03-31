from enum import Enum
from typing import Any, Optional

from fastapi import HTTPException, status


class ErrorCode(Enum):
    """错误码枚举"""

    # 通用错误 10000-19999
    SUCCESS = (0, "成功")
    BAD_REQUEST = (10000, "请求参数错误")
    UNAUTHORIZED = (10001, "未授权")
    FORBIDDEN = (10002, "禁止访问")
    NOT_FOUND = (10003, "资源不存在")
    INTERNAL_ERROR = (10004, "服务器内部错误")
    VALIDATION_ERROR = (10005, "参数校验失败")

    # 业务错误 20000-29999
    # 诊断相关 20000-20999
    DIAGNOSE_RULE_NOT_FOUND = (20000, "诊断规则不存在")
    DIAGNOSE_RULE_ALREADY_EXISTS = (20001, "诊断规则已存在")
    DIAGNOSE_TYPE_NOT_SUPPORTED = (20002, "不支持的诊断类型")
    DIAGNOSE_EXECUTION_FAILED = (20003, "诊断执行失败")

    # 机器人相关 21000-21999
    ROBOT_NOT_FOUND = (21000, "机器人不存在")
    ROBOT_ALREADY_EXISTS = (21001, "机器人已存在")
    ROBOT_OFFLINE = (21002, "机器人已离线")

    # 传感器相关 22000-22999
    SENSOR_NOT_FOUND = (22000, "传感器不存在")
    SENSOR_DATA_INVALID = (22001, "传感器数据无效")

    # 故障相关 23000-23999
    FAULT_LOG_NOT_FOUND = (23000, "故障记录不存在")
    FAULT_STATUS_INVALID = (23001, "故障状态无效")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class BusinessException(HTTPException):
    """业务异常基类"""

    def __init__(
        self,
        error_code: ErrorCode,
        message: Optional[str] = None,
        detail: Any = None,
        headers: Optional[dict[str, str]] = None,
    ):
        self.error_code = error_code
        self.message = message or error_code.message
        self.detail = detail
        self.status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(
            status_code=self.status_code,
            detail={
                "code": error_code.code,
                "message": self.message,
                "detail": detail,
            },
            headers=headers,
        )


class NotFoundException(BusinessException):
    """资源不存在异常"""

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.NOT_FOUND,
        message: Optional[str] = None,
        detail: Any = None,
    ):
        super().__init__(error_code, message, detail)
        self.status_code = status.HTTP_404_NOT_FOUND


class ValidationException(BusinessException):
    """参数校验异常"""

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        message: Optional[str] = None,
        detail: Any = None,
    ):
        super().__init__(error_code, message, detail)
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class UnauthorizedException(BusinessException):
    """未授权异常"""

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.UNAUTHORIZED,
        message: Optional[str] = None,
        detail: Any = None,
    ):
        super().__init__(error_code, message, detail)
        self.status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(BusinessException):
    """禁止访问异常"""

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.FORBIDDEN,
        message: Optional[str] = None,
        detail: Any = None,
    ):
        super().__init__(error_code, message, detail)
        self.status_code = status.HTTP_403_FORBIDDEN