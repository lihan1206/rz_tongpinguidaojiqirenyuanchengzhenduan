package com.tongping.robot.controller;

import com.tongping.robot.dto.request.SensorDataRequest;
import com.tongping.robot.dto.request.SensorQueryRequest;
import com.tongping.robot.dto.response.ApiResponse;
import com.tongping.robot.dto.response.DiagnosisResultResponse;
import com.tongping.robot.dto.response.SensorDataResponse;
import com.tongping.robot.service.SensorDataService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Positive;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 传感器数据 Controller
 */
@RestController
@RequestMapping("/api/v1/sensors")
@RequiredArgsConstructor
@Validated
@Tag(name = "传感器管理", description = "传感器数据接收与查询接口")
public class SensorController {

    private final SensorDataService sensorDataService;

    /**
     * 接收传感器数据并进行诊断
     */
    @PostMapping("/ingest")
    @Operation(summary = "接收传感器数据", description = "接收传感器数据并进行故障诊断")
    public ApiResponse<DiagnosisResultResponse> ingest(
            @Valid @RequestBody SensorDataRequest request) {
        DiagnosisResultResponse result = sensorDataService.ingest(request);
        return ApiResponse.success("数据接收成功", result);
    }

    /**
     * 查询传感器数据列表
     */
    @GetMapping
    @Operation(summary = "查询传感器数据", description = "支持按机器人ID和传感器类型筛选")
    public ApiResponse<List<SensorDataResponse>> listData(
            @Parameter(description = "机器人ID")
            @RequestParam(required = false) @Positive Long robotId,

            @Parameter(description = "传感器类型")
            @RequestParam(required = false) String sensorType,

            @Parameter(description = "查询数量限制")
            @RequestParam(required = false, defaultValue = "200")
            @Min(1) @Max(500) Integer limit,

            @Parameter(description = "偏移量")
            @RequestParam(required = false, defaultValue = "0")
            @Min(0) Integer offset) {

        SensorQueryRequest queryRequest = SensorQueryRequest.builder()
                .robotId(robotId)
                .sensorType(sensorType)
                .limit(limit)
                .offset(offset)
                .build();

        List<SensorDataResponse> dataList = sensorDataService.listData(queryRequest);
        return ApiResponse.success(dataList);
    }

    /**
     * 根据ID查询传感器数据
     */
    @GetMapping("/{id}")
    @Operation(summary = "查询传感器数据详情", description = "根据数据ID查询详情")
    public ApiResponse<SensorDataResponse> getById(
            @Parameter(description = "数据ID", required = true)
            @PathVariable @Positive Long id) {
        SensorDataResponse data = sensorDataService.getById(id);
        return ApiResponse.success(data);
    }

    /**
     * 查询指定机器人的最新传感器数据
     */
    @GetMapping("/robot/{robotId}/latest")
    @Operation(summary = "查询最新数据", description = "查询指定机器人的最新传感器数据")
    public ApiResponse<List<SensorDataResponse>> getLatestByRobotId(
            @Parameter(description = "机器人ID", required = true)
            @PathVariable @Positive Long robotId,

            @Parameter(description = "查询数量限制")
            @RequestParam(required = false, defaultValue = "50")
            @Min(1) @Max(200) Integer limit) {

        List<SensorDataResponse> dataList = sensorDataService.getLatestByRobotId(robotId, limit);
        return ApiResponse.success(dataList);
    }
}
