package com.tongping.robot.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 诊断结果响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "诊断结果响应")
public class DiagnosisResultResponse {

    @Schema(description = "机器人ID", example = "1")
    private Long robotId;

    @Schema(description = "传感器类型", example = "temperature")
    private String sensorType;

    @Schema(description = "传感器数值")
    private java.math.BigDecimal value;

    @Schema(description = "是否触发告警")
    private Boolean hasFault;

    @Schema(description = "触发的故障规则列表")
    private List<FaultRuleResponse> triggeredRules;

    @Schema(description = "生成的故障日志列表")
    private List<FaultLogResponse> faultLogs;

    @Schema(description = "诊断消息")
    private String message;
}
