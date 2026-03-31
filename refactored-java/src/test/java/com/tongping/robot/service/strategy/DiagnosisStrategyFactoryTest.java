package com.tongping.robot.service.strategy;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

/**
 * 诊断策略工厂单元测试
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("诊断策略工厂测试")
class DiagnosisStrategyFactoryTest {

    @Mock
    private TemperatureDiagnosisStrategy temperatureStrategy;

    @Mock
    private VibrationDiagnosisStrategy vibrationStrategy;

    @Mock
    private GenericDiagnosisStrategy genericStrategy;

    private DiagnosisStrategyFactory factory;

    @BeforeEach
    void setUp() {
        when(temperatureStrategy.getSensorType()).thenReturn("temperature");
        when(vibrationStrategy.getSensorType()).thenReturn("vibration");

        List<DiagnosisStrategy> strategies = Arrays.asList(temperatureStrategy, vibrationStrategy);
        factory = new DiagnosisStrategyFactory(strategies, genericStrategy);
        factory.init();
    }

    @Test
    @DisplayName("获取已注册的策略")
    void getStrategy_RegisteredType_ShouldReturnCorrectStrategy() {
        DiagnosisStrategy strategy = factory.getStrategy("temperature");
        assertSame(temperatureStrategy, strategy);

        strategy = factory.getStrategy("vibration");
        assertSame(vibrationStrategy, strategy);
    }

    @Test
    @DisplayName("获取未注册的策略应返回通用策略")
    void getStrategy_UnregisteredType_ShouldReturnGenericStrategy() {
        DiagnosisStrategy strategy = factory.getStrategy("unknown");
        assertSame(genericStrategy, strategy);
    }

    @Test
    @DisplayName("策略查找应忽略大小写")
    void getStrategy_CaseInsensitive_ShouldWork() {
        DiagnosisStrategy strategy = factory.getStrategy("TEMPERATURE");
        assertSame(temperatureStrategy, strategy);

        strategy = factory.getStrategy("Temperature");
        assertSame(temperatureStrategy, strategy);
    }

    @Test
    @DisplayName("检查支持的类型")
    void supports_ShouldReturnCorrectResult() {
        assertTrue(factory.supports("temperature"));
        assertTrue(factory.supports("vibration"));
        assertFalse(factory.supports("unknown"));
    }

    @Test
    @DisplayName("动态注册新策略")
    void registerStrategy_ShouldAddNewStrategy() {
        // Given
        PositionDiagnosisStrategy positionStrategy = new PositionDiagnosisStrategy();

        // When
        factory.registerStrategy("position", positionStrategy);

        // Then
        assertTrue(factory.supports("position"));
        assertSame(positionStrategy, factory.getStrategy("position"));
    }

    @Test
    @DisplayName("获取所有支持的类型")
    void getSupportedTypes_ShouldReturnAllTypes() {
        var types = factory.getSupportedTypes();
        assertEquals(2, types.size());
        assertTrue(types.contains("temperature"));
        assertTrue(types.contains("vibration"));
    }
}
