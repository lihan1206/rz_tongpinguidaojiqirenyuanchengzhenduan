package com.tongping.robot.service.strategy;

import com.tongping.robot.entity.FaultRule;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 温度诊断策略单元测试
 */
@DisplayName("温度诊断策略测试")
class TemperatureDiagnosisStrategyTest {

    private TemperatureDiagnosisStrategy strategy;

    @BeforeEach
    void setUp() {
        strategy = new TemperatureDiagnosisStrategy();
    }

    @Test
    @DisplayName("获取传感器类型应为 temperature")
    void getSensorType_ShouldReturnTemperature() {
        assertEquals("temperature", strategy.getSensorType());
    }

    @Test
    @DisplayName("温度超过阈值时应触发告警")
    void diagnose_TemperatureExceedsThreshold_ShouldTriggerAlarm() {
        // Given
        Long robotId = 1L;
        BigDecimal value = new BigDecimal("85.5");

        FaultRule highTempRule = FaultRule.builder()
                .id(1L)
                .name("温度过高告警")
                .sensorType("temperature")
                .operator(">")
                .threshold(new BigDecimal("80.0"))
                .level("严重")
                .build();

        List<FaultRule> rules = List.of(highTempRule);

        // When
        List<FaultRule> triggered = strategy.diagnose(robotId, value, rules);

        // Then
        assertEquals(1, triggered.size());
        assertEquals("温度过高告警", triggered.get(0).getName());
    }

    @Test
    @DisplayName("温度正常时不应触发告警")
    void diagnose_TemperatureNormal_ShouldNotTriggerAlarm() {
        // Given
        Long robotId = 1L;
        BigDecimal value = new BigDecimal("75.0");

        FaultRule highTempRule = FaultRule.builder()
                .id(1L)
                .name("温度过高告警")
                .sensorType("temperature")
                .operator(">")
                .threshold(new BigDecimal("80.0"))
                .level("严重")
                .build();

        List<FaultRule> rules = List.of(highTempRule);

        // When
        List<FaultRule> triggered = strategy.diagnose(robotId, value, rules);

        // Then
        assertTrue(triggered.isEmpty());
    }

    @Test
    @DisplayName("多规则情况下应触发所有符合条件的规则")
    void diagnose_MultipleRules_ShouldTriggerAllMatching() {
        // Given
        Long robotId = 1L;
        BigDecimal value = new BigDecimal("90.0");

        FaultRule warningRule = FaultRule.builder()
                .id(1L)
                .name("温度警告")
                .sensorType("temperature")
                .operator(">=")
                .threshold(new BigDecimal("80.0"))
                .level("警告")
                .build();

        FaultRule criticalRule = FaultRule.builder()
                .id(2L)
                .name("温度过高")
                .sensorType("temperature")
                .operator(">")
                .threshold(new BigDecimal("85.0"))
                .level("严重")
                .build();

        FaultRule lowTempRule = FaultRule.builder()
                .id(3L)
                .name("温度过低")
                .sensorType("temperature")
                .operator("<")
                .threshold(new BigDecimal("10.0"))
                .level("警告")
                .build();

        List<FaultRule> rules = Arrays.asList(warningRule, criticalRule, lowTempRule);

        // When
        List<FaultRule> triggered = strategy.diagnose(robotId, value, rules);

        // Then
        assertEquals(2, triggered.size());
        assertTrue(triggered.stream().anyMatch(r -> r.getName().equals("温度警告")));
        assertTrue(triggered.stream().anyMatch(r -> r.getName().equals("温度过高")));
    }

    @ParameterizedTest
    @DisplayName("边界值测试")
    @CsvSource({
            "80.0, >=, 80.0, true",   // 等于阈值
            "80.1, >, 80.0, true",    // 略大于阈值
            "79.9, >, 80.0, false",   // 略小于阈值
            "80.0, ==, 80.0, true",   // 精确等于
            "80.1, ==, 80.0, false",  // 不精确等于
            "79.9, <, 80.0, true",    // 小于阈值
            "80.0, <=, 80.0, true",   // 小于等于阈值
            "80.1, <=, 80.0, false"   // 大于阈值
    })
    void isTriggered_BoundaryValues_ShouldWorkCorrectly(
            String value, String operator, String threshold, boolean expected) {
        BigDecimal val = new BigDecimal(value);
        BigDecimal thr = new BigDecimal(threshold);

        assertEquals(expected, strategy.isTriggered(operator, val, thr));
    }

    @Test
    @DisplayName("空规则列表应返回空结果")
    void diagnose_EmptyRules_ShouldReturnEmptyList() {
        List<FaultRule> triggered = strategy.diagnose(1L, new BigDecimal("100"), List.of());
        assertTrue(triggered.isEmpty());
    }
}
