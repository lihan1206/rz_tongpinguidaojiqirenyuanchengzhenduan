package com.tongping.robot.service;

import com.tongping.robot.dto.request.FaultRuleCreateRequest;
import com.tongping.robot.dto.response.FaultRuleResponse;

import java.util.List;

/**
 * 故障规则服务接口
 */
public interface FaultRuleService {

    /**
     * 创建故障规则
     *
     * @param request 创建请求
     * @return 创建的规则
     */
    FaultRuleResponse create(FaultRuleCreateRequest request);

    /**
     * 查询所有故障规则
     *
     * @return 规则列表
     */
    List<FaultRuleResponse> listAll();

    /**
     * 查询启用的故障规则
     *
     * @return 启用的规则列表
     */
    List<FaultRuleResponse> listEnabled();

    /**
     * 根据传感器类型查询规则
     *
     * @param sensorType 传感器类型
     * @return 规则列表
     */
    List<FaultRuleResponse> listBySensorType(String sensorType);

    /**
     * 根据ID查询规则
     *
     * @param id 规则ID
     * @return 规则详情
     */
    FaultRuleResponse getById(Long id);

    /**
     * 更新规则状态
     *
     * @param id     规则ID
     * @param enabled 是否启用
     * @return 更新后的规则
     */
    FaultRuleResponse updateStatus(Long id, Boolean enabled);

    /**
     * 删除规则
     *
     * @param id 规则ID
     */
    void delete(Long id);
}
