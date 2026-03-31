package com.tongping.robot.mapper;

import com.tongping.robot.dto.response.FaultLogResponse;
import com.tongping.robot.dto.response.FaultRuleResponse;
import com.tongping.robot.dto.response.SensorDataResponse;
import com.tongping.robot.entity.FaultLog;
import com.tongping.robot.entity.FaultRule;
import com.tongping.robot.entity.SensorData;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

/**
 * 实体映射器
 * 使用 MapStruct 实现 DTO 和实体之间的转换
 */
@Mapper(componentModel = "spring")
public interface EntityMapper {

    @Mapping(source = "timestamp", target = "timestamp")
    SensorDataResponse toSensorDataResponse(SensorData sensorData);

    FaultRuleResponse toFaultRuleResponse(FaultRule faultRule);

    FaultLogResponse toFaultLogResponse(FaultLog faultLog);
}
