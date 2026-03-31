package com.tongping.robot.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 故障规则响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "故障规则响应")
public class FaultRuleResponse {

    @Schema(description = "规则ID", example = "1")
    private Long id;

    @Schema(description = "规则名称", example = "温度过高告警")
    private String name;

    @Schema(description = "传感器类型", example = "temperature")
    private String sensorType;

    @Schema(description = "比较操作符", example = ">")
    private String operator;

    @Schema(description = "阈值", example = "80.0")
    private BigDecimal threshold;

    @Schema(description = "告警级别", example = "严重")
    private String level;

    @Schema(description = "是否启用", example = "true")
    private Boolean enabled;

    @Schema(description = "创建时间")
    private LocalDateTime createdAt;
}
