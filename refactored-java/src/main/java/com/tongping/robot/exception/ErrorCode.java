package com.tongping.robot.exception;

import lombok.Getter;

/**
 * 错误码枚举
 */
@Getter
public enum ErrorCode {

    // 系统级错误 (1000-1999)
    SYSTEM_ERROR(1000, "系统内部错误", "SYSTEM_ERROR"),
    SERVICE_UNAVAILABLE(1001, "服务暂不可用", "SYSTEM_ERROR"),
    REQUEST_TIMEOUT(1002, "请求超时", "SYSTEM_ERROR"),

    // 参数错误 (2000-2999)
    PARAM_ERROR(2000, "参数错误", "PARAM_ERROR"),
    PARAM_MISSING(2001, "缺少必要参数", "PARAM_ERROR"),
    PARAM_FORMAT_ERROR(2002, "参数格式错误", "PARAM_ERROR"),
    PARAM_VALIDATION_ERROR(2003, "参数校验失败", "PARAM_ERROR"),

    // 资源错误 (3000-3999)
    RESOURCE_NOT_FOUND(3000, "资源不存在", "RESOURCE_ERROR"),
    RESOURCE_ALREADY_EXISTS(3001, "资源已存在", "RESOURCE_ERROR"),
    RESOURCE_CONFLICT(3002, "资源冲突", "RESOURCE_ERROR"),

    // 业务错误 (4000-4999)
    ROBOT_NOT_FOUND(4000, "机器人不存在", "BUSINESS_ERROR"),
    SENSOR_TYPE_NOT_SUPPORTED(4001, "不支持的传感器类型", "BUSINESS_ERROR"),
    FAULT_RULE_NOT_FOUND(4002, "故障规则不存在", "BUSINESS_ERROR"),
    FAULT_LOG_NOT_FOUND(4003, "故障日志不存在", "BUSINESS_ERROR"),
    DIAGNOSIS_RULE_ERROR(4004, "诊断规则执行错误", "BUSINESS_ERROR"),

    // 权限错误 (5000-5999)
    UNAUTHORIZED(5000, "未授权访问", "AUTH_ERROR"),
    FORBIDDEN(5001, "禁止访问", "AUTH_ERROR"),
    TOKEN_EXPIRED(5002, "Token已过期", "AUTH_ERROR"),
    INSUFFICIENT_PERMISSION(5003, "权限不足", "AUTH_ERROR");

    private final Integer code;
    private final String message;
    private final String type;

    ErrorCode(Integer code, String message, String type) {
        this.code = code;
        this.message = message;
        this.type = type;
    }
}
