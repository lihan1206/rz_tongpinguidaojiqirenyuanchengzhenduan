package com.tongping.robot.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 故障日志响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "故障日志响应")
public class FaultLogResponse {

    @Schema(description = "日志ID", example = "1")
    private Long id;

    @Schema(description = "机器人ID", example = "1")
    private Long robotId;

    @Schema(description = "触发规则ID", example = "1")
    private Long ruleId;

    @Schema(description = "故障类型", example = "温度过高告警")
    private String faultType;

    @Schema(description = "故障描述", example = "传感器[temperature]数值为85.5，触发规则：>80.0")
    private String description;

    @Schema(description = "告警级别", example = "严重")
    private String level;

    @Schema(description = "处理状态", example = "未处理")
    private String status;

    @Schema(description = "创建时间")
    private LocalDateTime createdAt;
}
