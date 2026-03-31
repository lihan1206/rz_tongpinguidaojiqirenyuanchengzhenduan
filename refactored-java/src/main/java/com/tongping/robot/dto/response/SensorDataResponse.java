package com.tongping.robot.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 传感器数据响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "传感器数据响应")
public class SensorDataResponse {

    @Schema(description = "数据ID", example = "1")
    private Long id;

    @Schema(description = "机器人ID", example = "1")
    private Long robotId;

    @Schema(description = "传感器类型", example = "temperature")
    private String sensorType;

    @Schema(description = "传感器数值", example = "85.5")
    private BigDecimal value;

    @Schema(description = "采集时间")
    private LocalDateTime timestamp;
}
