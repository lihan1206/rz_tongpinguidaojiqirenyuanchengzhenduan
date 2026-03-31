package com.tongping.robot.exception;

/**
 * 资源不存在异常
 */
public class ResourceNotFoundException extends BusinessException {

    public ResourceNotFoundException(String resourceName, Long id) {
        super(ErrorCode.RESOURCE_NOT_FOUND, String.format("%s不存在，ID: %d", resourceName, id));
    }

    public ResourceNotFoundException(String message) {
        super(ErrorCode.RESOURCE_NOT_FOUND, message);
    }
}
