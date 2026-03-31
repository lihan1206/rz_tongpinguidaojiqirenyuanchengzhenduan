package com.tongping.robot.controller;

import com.tongping.robot.dto.request.FaultRuleCreateRequest;
import com.tongping.robot.dto.response.ApiResponse;
import com.tongping.robot.dto.response.FaultRuleResponse;
import com.tongping.robot.service.FaultRuleService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Positive;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 故障规则 Controller
 */
@RestController
@RequestMapping("/api/v1/faults/rules")
@RequiredArgsConstructor
@Validated
@Tag(name = "故障规则管理", description = "故障诊断规则的增删改查接口")
public class FaultRuleController {

    private final FaultRuleService faultRuleService;

    /**
     * 查询所有故障规则
     */
    @GetMapping
    @Operation(summary = "查询所有规则", description = "查询所有故障诊断规则")
    public ApiResponse<List<FaultRuleResponse>> listAll() {
        List<FaultRuleResponse> rules = faultRuleService.listAll();
        return ApiResponse.success(rules);
    }

    /**
     * 查询启用的故障规则
     */
    @GetMapping("/enabled")
    @Operation(summary = "查询启用的规则", description = "查询所有启用的故障诊断规则")
    public ApiResponse<List<FaultRuleResponse>> listEnabled() {
        List<FaultRuleResponse> rules = faultRuleService.listEnabled();
        return ApiResponse.success(rules);
    }

    /**
     * 根据传感器类型查询规则
     */
    @GetMapping("/sensor-type/{sensorType}")
    @Operation(summary = "按类型查询规则", description = "根据传感器类型查询故障规则")
    public ApiResponse<List<FaultRuleResponse>> listBySensorType(
            @Parameter(description = "传感器类型", example = "temperature", required = true)
            @PathVariable String sensorType) {
        List<FaultRuleResponse> rules = faultRuleService.listBySensorType(sensorType);
        return ApiResponse.success(rules);
    }

    /**
     * 根据ID查询规则
     */
    @GetMapping("/{id}")
    @Operation(summary = "查询规则详情", description = "根据规则ID查询详情")
    public ApiResponse<FaultRuleResponse> getById(
            @Parameter(description = "规则ID", required = true)
            @PathVariable @Positive Long id) {
        FaultRuleResponse rule = faultRuleService.getById(id);
        return ApiResponse.success(rule);
    }

    /**
     * 创建故障规则
     */
    @PostMapping
    @Operation(summary = "创建规则", description = "创建新的故障诊断规则")
    public ApiResponse<FaultRuleResponse> create(
            @Valid @RequestBody FaultRuleCreateRequest request) {
        FaultRuleResponse rule = faultRuleService.create(request);
        return ApiResponse.success("规则创建成功", rule);
    }

    /**
     * 更新规则状态（启用/禁用）
     */
    @PutMapping("/{id}/status")
    @Operation(summary = "更新规则状态", description = "启用或禁用故障规则")
    public ApiResponse<FaultRuleResponse> updateStatus(
            @Parameter(description = "规则ID", required = true)
            @PathVariable @Positive Long id,

            @Parameter(description = "是否启用", required = true)
            @RequestParam Boolean enabled) {
        FaultRuleResponse rule = faultRuleService.updateStatus(id, enabled);
        return ApiResponse.success("状态更新成功", rule);
    }

    /**
     * 删除故障规则
     */
    @DeleteMapping("/{id}")
    @Operation(summary = "删除规则", description = "删除指定的故障规则")
    public ApiResponse<Void> delete(
            @Parameter(description = "规则ID", required = true)
            @PathVariable @Positive Long id) {
        faultRuleService.delete(id);
        return ApiResponse.success("规则删除成功", null);
    }
}
