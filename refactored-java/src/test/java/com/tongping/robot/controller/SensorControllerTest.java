package com.tongping.robot.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tongping.robot.dto.request.SensorDataRequest;
import com.tongping.robot.dto.response.DiagnosisResultResponse;
import com.tongping.robot.dto.response.SensorDataResponse;
import com.tongping.robot.service.SensorDataService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 传感器 Controller 单元测试
 */
@WebMvcTest(SensorController.class)
@DisplayName("传感器控制器测试")
class SensorControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private SensorDataService sensorDataService;

    private SensorDataRequest validRequest;
    private DiagnosisResultResponse diagnosisResponse;

    @BeforeEach
    void setUp() {
        validRequest = SensorDataRequest.builder()
                .robotId(1L)
                .sensorType("temperature")
                .value(new BigDecimal("85.5"))
                .build();

        diagnosisResponse = DiagnosisResultResponse.builder()
                .robotId(1L)
                .sensorType("temperature")
                .value(new BigDecimal("85.5"))
                .hasFault(true)
                .message("检测到1个异常，已生成故障日志")
                .build();
    }

    @Test
    @DisplayName("接收有效传感器数据应返回200")
    void ingest_ValidRequest_ShouldReturn200() throws Exception {
        // Given
        when(sensorDataService.ingest(any())).thenReturn(diagnosisResponse);

        // When & Then
        mockMvc.perform(post("/api/v1/sensors/ingest")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(validRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.hasFault").value(true))
                .andExpect(jsonPath("$.data.robotId").value(1));
    }

    @Test
    @DisplayName("接收无效传感器数据应返回400")
    void ingest_InvalidRequest_ShouldReturn400() throws Exception {
        // Given - 缺少 robotId
        SensorDataRequest invalidRequest = SensorDataRequest.builder()
                .sensorType("temperature")
                .value(new BigDecimal("85.5"))
                .build();

        // When & Then
        mockMvc.perform(post("/api/v1/sensors/ingest")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(2003));
    }

    @Test
    @DisplayName("查询传感器数据列表")
    void listData_ShouldReturnDataList() throws Exception {
        // Given
        List<SensorDataResponse> dataList = Arrays.asList(
                SensorDataResponse.builder()
                        .id(1L)
                        .robotId(1L)
                        .sensorType("temperature")
                        .value(new BigDecimal("85.5"))
                        .timestamp(LocalDateTime.now())
                        .build(),
                SensorDataResponse.builder()
                        .id(2L)
                        .robotId(1L)
                        .sensorType("vibration")
                        .value(new BigDecimal("12.3"))
                        .timestamp(LocalDateTime.now())
                        .build()
        );
        when(sensorDataService.listData(any())).thenReturn(dataList);

        // When & Then
        mockMvc.perform(get("/api/v1/sensors")
                        .param("limit", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data.length()").value(2));
    }

    @Test
    @DisplayName("根据ID查询传感器数据")
    void getById_ExistingId_ShouldReturnData() throws Exception {
        // Given
        SensorDataResponse response = SensorDataResponse.builder()
                .id(1L)
                .robotId(1L)
                .sensorType("temperature")
                .value(new BigDecimal("85.5"))
                .timestamp(LocalDateTime.now())
                .build();
        when(sensorDataService.getById(1L)).thenReturn(response);

        // When & Then
        mockMvc.perform(get("/api/v1/sensors/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.id").value(1))
                .andExpect(jsonPath("$.data.sensorType").value("temperature"));
    }

    @Test
    @DisplayName("查询最新数据")
    void getLatestByRobotId_ShouldReturnLatestData() throws Exception {
        // Given
        List<SensorDataResponse> latestData = List.of(
                SensorDataResponse.builder()
                        .id(10L)
                        .robotId(1L)
                        .sensorType("temperature")
                        .value(new BigDecimal("88.0"))
                        .timestamp(LocalDateTime.now())
                        .build()
        );
        when(sensorDataService.getLatestByRobotId(1L, 50)).thenReturn(latestData);

        // When & Then
        mockMvc.perform(get("/api/v1/sensors/robot/1/latest"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data[0].id").value(10));
    }

    @Test
    @DisplayName("无效参数应返回400")
    void listData_InvalidLimit_ShouldReturn400() throws Exception {
        mockMvc.perform(get("/api/v1/sensors")
                        .param("limit", "1000"))  // 超过最大值500
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(2003));
    }
}
