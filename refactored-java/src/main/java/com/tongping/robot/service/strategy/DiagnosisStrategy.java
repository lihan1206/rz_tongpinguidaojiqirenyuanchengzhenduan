package com.tongping.robot.service.strategy;

import com.tongping.robot.entity.FaultRule;

import java.math.BigDecimal;
import java.util.List;

/**
 * 诊断策略接口
 * 策略模式：定义诊断算法的通用接口
 */
public interface DiagnosisStrategy {

    /**
     * 获取策略支持的传感器类型
     *
     * @return 传感器类型标识
     */
    String getSensorType();

    /**
     * 执行诊断
     *
     * @param robotId     机器人ID
     * @param value       传感器数值
     * @param rules       适用的诊断规则列表
     * @return 触发的规则列表
     */
    List<FaultRule> diagnose(Long robotId, BigDecimal value, List<FaultRule> rules);

    /**
     * 检查数值是否触发规则
     *
     * @param operator  操作符 (> >= < <= ==)
     * @param value     传感器数值
     * @param threshold 阈值
     * @return 是否触发
     */
    default boolean isTriggered(String operator, BigDecimal value, BigDecimal threshold) {
        return switch (operator) {
            case ">" -> value.compareTo(threshold) > 0;
            case ">=" -> value.compareTo(threshold) >= 0;
            case "<" -> value.compareTo(threshold) < 0;
            case "<=" -> value.compareTo(threshold) <= 0;
            case "==" -> value.compareTo(threshold) == 0;
            default -> false;
        };
    }
}
