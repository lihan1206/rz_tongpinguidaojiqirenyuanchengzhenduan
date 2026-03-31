package com.tongping.robot.service;

import com.tongping.robot.dto.request.FaultLogStatusUpdateRequest;
import com.tongping.robot.dto.response.FaultLogResponse;

import java.util.List;

/**
 * 故障日志服务接口
 */
public interface FaultLogService {

    /**
     * 查询所有故障日志
     *
     * @param limit 查询数量限制
     * @return 故障日志列表
     */
    List<FaultLogResponse> listAll(Integer limit);

    /**
     * 根据机器人ID查询故障日志
     *
     * @param robotId 机器人ID
     * @param limit   查询数量限制
     * @return 故障日志列表
     */
    List<FaultLogResponse> listByRobotId(Long robotId, Integer limit);

    /**
     * 根据状态查询故障日志
     *
     * @param status 状态
     * @param limit  查询数量限制
     * @return 故障日志列表
     */
    List<FaultLogResponse> listByStatus(String status, Integer limit);

    /**
     * 根据ID查询故障日志
     *
     * @param id 日志ID
     * @return 故障日志详情
     */
    FaultLogResponse getById(Long id);

    /**
     * 更新故障日志状态
     *
     * @param id      日志ID
     * @param request 状态更新请求
     * @return 更新后的故障日志
     */
    FaultLogResponse updateStatus(Long id, FaultLogStatusUpdateRequest request);

    /**
     * 统计未处理的故障数量
     *
     * @return 未处理数量
     */
    Long countUnhandled();
}
