package com.tongping.robot.exception;

/**
 * 诊断异常
 */
public class DiagnosisException extends BusinessException {

    public DiagnosisException(String message) {
        super(ErrorCode.DIAGNOSIS_RULE_ERROR, message);
    }

    public DiagnosisException(String sensorType, String message) {
        super(ErrorCode.DIAGNOSIS_RULE_ERROR, String.format("传感器类型[%s]诊断失败: %s", sensorType, message));
    }
}
