package com.tongping.robot.exception;

import lombok.Getter;

/**
 * 业务异常基类
 */
@Getter
public class BusinessException extends RuntimeException {

    private final Integer code;
    private final String errorType;

    public BusinessException(String message) {
        super(message);
        this.code = 400;
        this.errorType = "BUSINESS_ERROR";
    }

    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
        this.errorType = "BUSINESS_ERROR";
    }

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.code = errorCode.getCode();
        this.errorType = errorCode.getType();
    }

    public BusinessException(ErrorCode errorCode, String message) {
        super(message);
        this.code = errorCode.getCode();
        this.errorType = errorCode.getType();
    }
}
