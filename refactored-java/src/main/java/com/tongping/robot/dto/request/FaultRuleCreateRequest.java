package com.tongping.robot.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * 故障规则创建请求 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "故障规则创建请求")
public class FaultRuleCreateRequest {

    @NotBlank(message = "规则名称不能为空")
    @Schema(description = "规则名称", example = "温度过高告警", requiredMode = Schema.RequiredMode.REQUIRED)
    private String name;

    @NotBlank(message = "传感器类型不能为空")
    @Schema(description = "传感器类型", example = "temperature", requiredMode = Schema.RequiredMode.REQUIRED)
    private String sensorType;

    @NotBlank(message = "操作符不能为空")
    @Pattern(regexp = "^(>|>=|<|<=|==)$", message = "操作符必须是 >, >=, <, <=, == 之一")
    @Schema(description = "比较操作符", example = ">", allowableValues = {">", ">=", "<", "<=", "=="})
    private String operator;

    @NotNull(message = "阈值不能为空")
    @Schema(description = "阈值", example = "80.0", requiredMode = Schema.RequiredMode.REQUIRED)
    private BigDecimal threshold;

    @NotBlank(message = "告警级别不能为空")
    @Pattern(regexp = "^(严重|警告|提示)$", message = "告警级别必须是 严重、警告、提示 之一")
    @Schema(description = "告警级别", example = "严重", allowableValues = {"严重", "警告", "提示"})
    private String level;

    @Builder.Default
    @Schema(description = "是否启用", example = "true")
    private Boolean enabled = true;
}
