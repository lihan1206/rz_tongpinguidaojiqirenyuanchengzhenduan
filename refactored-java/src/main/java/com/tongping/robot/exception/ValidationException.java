package com.tongping.robot.exception;

/**
 * 参数校验异常
 */
public class ValidationException extends BusinessException {

    public ValidationException(String message) {
        super(ErrorCode.PARAM_VALIDATION_ERROR, message);
    }

    public ValidationException(String field, String message) {
        super(ErrorCode.PARAM_VALIDATION_ERROR, String.format("字段[%s]校验失败: %s", field, message));
    }
}
