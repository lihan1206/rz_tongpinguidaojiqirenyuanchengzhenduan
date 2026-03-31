package com.tongping.robot.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 故障日志状态更新请求 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "故障日志状态更新请求")
public class FaultLogStatusUpdateRequest {

    @NotBlank(message = "状态不能为空")
    @Pattern(regexp = "^(未处理|处理中|已处理|已忽略)$", message = "状态必须是 未处理、处理中、已处理、已忽略 之一")
    @Schema(description = "故障状态", example = "处理中", allowableValues = {"未处理", "处理中", "已处理", "已忽略"})
    private String status;

    @Schema(description = "处理备注")
    private String remark;
}
