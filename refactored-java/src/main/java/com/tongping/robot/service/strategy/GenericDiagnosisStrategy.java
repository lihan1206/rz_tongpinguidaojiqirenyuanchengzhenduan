package com.tongping.robot.service.strategy;

import com.tongping.robot.entity.FaultRule;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * 通用诊断策略
 * 用于处理未定义特定策略的传感器类型
 */
@Slf4j
@Component
public class GenericDiagnosisStrategy implements DiagnosisStrategy {

    @Override
    public String getSensorType() {
        return "generic";
    }

    @Override
    public List<FaultRule> diagnose(Long robotId, BigDecimal value, List<FaultRule> rules) {
        List<FaultRule> triggeredRules = new ArrayList<>();

        for (FaultRule rule : rules) {
            if (isTriggered(rule.getOperator(), value, rule.getThreshold())) {
                triggeredRules.add(rule);
                log.warn("机器人[{}]传感器[{}]异常: 当前值{}, 触发规则: {}{}, 级别: {}",
                        robotId, rule.getSensorType(), value,
                        rule.getOperator(), rule.getThreshold(), rule.getLevel());
            }
        }

        return triggeredRules;
    }
}
