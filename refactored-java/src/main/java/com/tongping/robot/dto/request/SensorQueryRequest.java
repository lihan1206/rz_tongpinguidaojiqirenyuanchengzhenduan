package com.tongping.robot.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 传感器数据查询请求 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "传感器数据查询请求")
public class SensorQueryRequest {

    @Positive(message = "机器人ID必须为正整数")
    @Schema(description = "机器人ID（可选）", example = "1")
    private Long robotId;

    @Schema(description = "传感器类型（可选）", example = "temperature")
    private String sensorType;

    @Min(value = 1, message = "每页数量最小为1")
    @Max(value = 500, message = "每页数量最大为500")
    @Builder.Default
    @Schema(description = "查询数量限制", example = "200")
    private Integer limit = 200;

    @Min(value = 0, message = "偏移量不能为负数")
    @Builder.Default
    @Schema(description = "偏移量", example = "0")
    private Integer offset = 0;
}
