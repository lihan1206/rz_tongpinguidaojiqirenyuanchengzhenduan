package com.tongping.robot.service.impl;

import com.tongping.robot.dto.request.FaultRuleCreateRequest;
import com.tongping.robot.dto.response.FaultRuleResponse;
import com.tongping.robot.entity.FaultRule;
import com.tongping.robot.exception.ResourceNotFoundException;
import com.tongping.robot.exception.ValidationException;
import com.tongping.robot.mapper.EntityMapper;
import com.tongping.robot.repository.FaultRuleRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * 故障规则服务单元测试
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("故障规则服务测试")
class FaultRuleServiceImplTest {

    @Mock
    private FaultRuleRepository faultRuleRepository;

    @Mock
    private EntityMapper entityMapper;

    @InjectMocks
    private FaultRuleServiceImpl faultRuleService;

    private FaultRuleCreateRequest createRequest;
    private FaultRule faultRule;
    private FaultRuleResponse faultRuleResponse;

    @BeforeEach
    void setUp() {
        createRequest = FaultRuleCreateRequest.builder()
                .name("温度过高告警")
                .sensorType("temperature")
                .operator(">")
                .threshold(new BigDecimal("80.0"))
                .level("严重")
                .enabled(true)
                .build();

        faultRule = FaultRule.builder()
                .id(1L)
                .name("温度过高告警")
                .sensorType("temperature")
                .operator(">")
                .threshold(new BigDecimal("80.0"))
                .level("严重")
                .enabled(true)
                .createdAt(LocalDateTime.now())
                .build();

        faultRuleResponse = FaultRuleResponse.builder()
                .id(1L)
                .name("温度过高告警")
                .sensorType("temperature")
                .operator(">")
                .threshold(new BigDecimal("80.0"))
                .level("严重")
                .enabled(true)
                .createdAt(LocalDateTime.now())
                .build();
    }

    @Test
    @DisplayName("创建规则成功")
    void create_ValidRequest_ShouldSucceed() {
        // Given
        when(faultRuleRepository.existsBySensorTypeAndName(any(), any())).thenReturn(false);
        when(faultRuleRepository.save(any(FaultRule.class))).thenReturn(faultRule);
        when(entityMapper.toFaultRuleResponse(any())).thenReturn(faultRuleResponse);

        // When
        FaultRuleResponse result = faultRuleService.create(createRequest);

        // Then
        assertNotNull(result);
        assertEquals("温度过高告警", result.getName());
        verify(faultRuleRepository).save(any(FaultRule.class));
    }

    @Test
    @DisplayName("创建重复规则应抛出异常")
    void create_DuplicateRule_ShouldThrowException() {
        // Given
        when(faultRuleRepository.existsBySensorTypeAndName("temperature", "温度过高告警"))
                .thenReturn(true);

        // When & Then
        ValidationException exception = assertThrows(ValidationException.class,
                () -> faultRuleService.create(createRequest));
        assertTrue(exception.getMessage().contains("已存在"));
        verify(faultRuleRepository, never()).save(any());
    }

    @Test
    @DisplayName("查询所有规则")
    void listAll_ShouldReturnAllRules() {
        // Given
        FaultRule rule2 = FaultRule.builder()
                .id(2L)
                .name("振动异常告警")
                .sensorType("vibration")
                .build();

        when(faultRuleRepository.findAll()).thenReturn(Arrays.asList(faultRule, rule2));
        when(entityMapper.toFaultRuleResponse(faultRule)).thenReturn(faultRuleResponse);
        when(entityMapper.toFaultRuleResponse(rule2)).thenReturn(
                FaultRuleResponse.builder().id(2L).name("振动异常告警").build());

        // When
        List<FaultRuleResponse> results = faultRuleService.listAll();

        // Then
        assertEquals(2, results.size());
    }

    @Test
    @DisplayName("根据ID查询存在的规则")
    void getById_ExistingRule_ShouldReturnRule() {
        // Given
        when(faultRuleRepository.findById(1L)).thenReturn(Optional.of(faultRule));
        when(entityMapper.toFaultRuleResponse(faultRule)).thenReturn(faultRuleResponse);

        // When
        FaultRuleResponse result = faultRuleService.getById(1L);

        // Then
        assertNotNull(result);
        assertEquals(1L, result.getId());
    }

    @Test
    @DisplayName("根据ID查询不存在的规则应抛出异常")
    void getById_NonExistingRule_ShouldThrowException() {
        // Given
        when(faultRuleRepository.findById(999L)).thenReturn(Optional.empty());

        // When & Then
        assertThrows(ResourceNotFoundException.class, () -> faultRuleService.getById(999L));
    }

    @Test
    @DisplayName("更新规则状态成功")
    void updateStatus_ValidRequest_ShouldSucceed() {
        // Given
        when(faultRuleRepository.findById(1L)).thenReturn(Optional.of(faultRule));
        when(faultRuleRepository.save(any())).thenReturn(faultRule);
        when(entityMapper.toFaultRuleResponse(any())).thenReturn(faultRuleResponse);

        // When
        FaultRuleResponse result = faultRuleService.updateStatus(1L, false);

        // Then
        assertNotNull(result);
        verify(faultRuleRepository).save(argThat(rule -> !rule.getEnabled()));
    }

    @Test
    @DisplayName("删除存在的规则")
    void delete_ExistingRule_ShouldSucceed() {
        // Given
        when(faultRuleRepository.existsById(1L)).thenReturn(true);

        // When
        faultRuleService.delete(1L);

        // Then
        verify(faultRuleRepository).deleteById(1L);
    }

    @Test
    @DisplayName("删除不存在的规则应抛出异常")
    void delete_NonExistingRule_ShouldThrowException() {
        // Given
        when(faultRuleRepository.existsById(999L)).thenReturn(false);

        // When & Then
        assertThrows(ResourceNotFoundException.class, () -> faultRuleService.delete(999L));
    }
}
