package com.tongping.robot.controller;

import com.tongping.robot.dto.request.FaultLogStatusUpdateRequest;
import com.tongping.robot.dto.response.ApiResponse;
import com.tongping.robot.dto.response.FaultLogResponse;
import com.tongping.robot.service.FaultLogService;
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
 * 故障日志 Controller
 */
@RestController
@RequestMapping("/api/v1/faults/logs")
@RequiredArgsConstructor
@Validated
@Tag(name = "故障日志管理", description = "故障日志查询与处理接口")
public class FaultLogController {

    private final FaultLogService faultLogService;

    /**
     * 查询所有故障日志
     */
    @GetMapping
    @Operation(summary = "查询所有日志", description = "查询所有故障日志")
    public ApiResponse<List<FaultLogResponse>> listAll(
            @Parameter(description = "查询数量限制")
            @RequestParam(required = false, defaultValue = "200")
            @Min(1) @Max(500) Integer limit) {
        List<FaultLogResponse> logs = faultLogService.listAll(limit);
        return ApiResponse.success(logs);
    }

    /**
     * 根据机器人ID查询故障日志
     */
    @GetMapping("/robot/{robotId}")
    @Operation(summary = "按机器人查询", description = "查询指定机器人的故障日志")
    public ApiResponse<List<FaultLogResponse>> listByRobotId(
            @Parameter(description = "机器人ID", required = true)
            @PathVariable @Positive Long robotId,

            @Parameter(description = "查询数量限制")
            @RequestParam(required = false, defaultValue = "200")
            @Min(1) @Max(500) Integer limit) {
        List<FaultLogResponse> logs = faultLogService.listByRobotId(robotId, limit);
        return ApiResponse.success(logs);
    }

    /**
     * 根据状态查询故障日志
     */
    @GetMapping("/status/{status}")
    @Operation(summary = "按状态查询", description = "按处理状态查询故障日志")
    public ApiResponse<List<FaultLogResponse>> listByStatus(
            @Parameter(description = "状态", example = "未处理", required = true)
            @PathVariable String status,

            @Parameter(description = "查询数量限制")
            @RequestParam(required = false, defaultValue = "200")
            @Min(1) @Max(500) Integer limit) {
        List<FaultLogResponse> logs = faultLogService.listByStatus(status, limit);
        return ApiResponse.success(logs);
    }

    /**
     * 根据ID查询故障日志
     */
    @GetMapping("/{id}")
    @Operation(summary = "查询日志详情", description = "根据日志ID查询详情")
    public ApiResponse<FaultLogResponse> getById(
            @Parameter(description = "日志ID", required = true)
            @PathVariable @Positive Long id) {
        FaultLogResponse log = faultLogService.getById(id);
        return ApiResponse.success(log);
    }

    /**
     * 更新故障日志状态
     */
    @PutMapping("/{id}/status")
    @Operation(summary = "更新日志状态", description = "更新故障日志的处理状态")
    public ApiResponse<FaultLogResponse> updateStatus(
            @Parameter(description = "日志ID", required = true)
            @PathVariable @Positive Long id,

            @Valid @RequestBody FaultLogStatusUpdateRequest request) {
        FaultLogResponse log = faultLogService.updateStatus(id, request);
        return ApiResponse.success("状态更新成功", log);
    }

    /**
     * 统计未处理的故障数量
     */
    @GetMapping("/statistics/unhandled")
    @Operation(summary = "未处理统计", description = "统计未处理的故障数量")
    public ApiResponse<Long> countUnhandled() {
        Long count = faultLogService.countUnhandled();
        return ApiResponse.success(count);
    }
}
