package com.tongping.robot.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * 传感器数据上报请求 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "传感器数据上报请求")
public class SensorDataRequest {

    @NotNull(message = "机器人ID不能为空")
    @Positive(message = "机器人ID必须为正整数")
    @Schema(description = "机器人ID", example = "1", requiredMode = Schema.RequiredMode.REQUIRED)
    private Long robotId;

    @NotBlank(message = "传感器类型不能为空")
    @Schema(description = "传感器类型", example = "temperature", requiredMode = Schema.RequiredMode.REQUIRED)
    private String sensorType;

    @NotNull(message = "传感器数值不能为空")
    @Schema(description = "传感器数值", example = "85.5", requiredMode = Schema.RequiredMode.REQUIRED)
    private BigDecimal value;

    @Schema(description = "时间戳，为空则使用服务器时间")
    private Long timestamp;
}
