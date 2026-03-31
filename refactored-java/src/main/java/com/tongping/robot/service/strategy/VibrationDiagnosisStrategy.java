package com.tongping.robot.service.strategy;

import com.tongping.robot.entity.FaultRule;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * 振动传感器诊断策略
 */
@Slf4j
@Component
public class VibrationDiagnosisStrategy implements DiagnosisStrategy {

    @Override
    public String getSensorType() {
        return "vibration";
    }

    @Override
    public List<FaultRule> diagnose(Long robotId, BigDecimal value, List<FaultRule> rules) {
        List<FaultRule> triggeredRules = new ArrayList<>();

        for (FaultRule rule : rules) {
            if (isTriggered(rule.getOperator(), value, rule.getThreshold())) {
                triggeredRules.add(rule);
                log.warn("机器人[{}]振动异常: 当前值{}mm/s, 触发规则: {}{}mm/s, 级别: {}",
                        robotId, value, rule.getOperator(), rule.getThreshold(), rule.getLevel());
            }
        }

        return triggeredRules;
    }
}
