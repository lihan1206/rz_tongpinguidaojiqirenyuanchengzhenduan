package com.tongping.robot.service;

import com.tongping.robot.dto.request.SensorDataRequest;
import com.tongping.robot.dto.request.SensorQueryRequest;
import com.tongping.robot.dto.response.DiagnosisResultResponse;
import com.tongping.robot.dto.response.SensorDataResponse;

import java.util.List;

/**
 * 传感器数据服务接口
 */
public interface SensorDataService {

    /**
     * 接收传感器数据并进行诊断
     *
     * @param request 传感器数据请求
     * @return 诊断结果
     */
    DiagnosisResultResponse ingest(SensorDataRequest request);

    /**
     * 查询传感器数据列表
     *
     * @param queryRequest 查询条件
     * @return 传感器数据列表
     */
    List<SensorDataResponse> listData(SensorQueryRequest queryRequest);

    /**
     * 根据ID查询传感器数据
     *
     * @param id 数据ID
     * @return 传感器数据
     */
    SensorDataResponse getById(Long id);

    /**
     * 根据机器人ID查询最新的传感器数据
     *
     * @param robotId 机器人ID
     * @param limit   查询数量
     * @return 传感器数据列表
     */
    List<SensorDataResponse> getLatestByRobotId(Long robotId, Integer limit);
}
