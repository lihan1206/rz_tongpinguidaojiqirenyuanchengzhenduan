package com.tongping.robot.service.strategy;

import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 诊断策略工厂
 * 用于管理和获取不同类型的诊断策略
 */
@Component
public class DiagnosisStrategyFactory {

    private final Map<String, DiagnosisStrategy> strategyMap = new HashMap<>();
    private final List<DiagnosisStrategy> strategies;
    private final GenericDiagnosisStrategy genericStrategy;

    public DiagnosisStrategyFactory(List<DiagnosisStrategy> strategies, GenericDiagnosisStrategy genericStrategy) {
        this.strategies = strategies;
        this.genericStrategy = genericStrategy;
    }

    @PostConstruct
    public void init() {
        for (DiagnosisStrategy strategy : strategies) {
            if (!(strategy instanceof GenericDiagnosisStrategy)) {
                strategyMap.put(strategy.getSensorType().toLowerCase(), strategy);
            }
        }
    }

    /**
     * 获取指定传感器类型的诊断策略
     *
     * @param sensorType 传感器类型
     * @return 对应的诊断策略，如果没有则返回通用策略
     */
    public DiagnosisStrategy getStrategy(String sensorType) {
        return strategyMap.getOrDefault(sensorType.toLowerCase(), genericStrategy);
    }

    /**
     * 注册新的诊断策略
     * 支持运行时动态扩展
     *
     * @param sensorType 传感器类型
     * @param strategy   诊断策略
     */
    public void registerStrategy(String sensorType, DiagnosisStrategy strategy) {
        strategyMap.put(sensorType.toLowerCase(), strategy);
    }

    /**
     * 检查是否支持指定传感器类型
     *
     * @param sensorType 传感器类型
     * @return 是否支持
     */
    public boolean supports(String sensorType) {
        return strategyMap.containsKey(sensorType.toLowerCase());
    }

    /**
     * 获取所有支持的传感器类型
     *
     * @return 传感器类型列表
     */
    public java.util.Set<String> getSupportedTypes() {
        return strategyMap.keySet();
    }
}
