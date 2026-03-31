package com.tongping.robot.service.impl;

import com.tongping.robot.dto.request.FaultLogStatusUpdateRequest;
import com.tongping.robot.dto.response.FaultLogResponse;
import com.tongping.robot.entity.FaultLog;
import com.tongping.robot.exception.ResourceNotFoundException;
import com.tongping.robot.exception.ValidationException;
import com.tongping.robot.mapper.EntityMapper;
import com.tongping.robot.repository.FaultLogRepository;
import com.tongping.robot.service.FaultLogService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;
import java.util.List;

/**
 * 故障日志服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class FaultLogServiceImpl implements FaultLogService {

    private final FaultLogRepository faultLogRepository;
    private final EntityMapper entityMapper;

    private static final List<String> VALID_STATUSES = Arrays.asList("未处理", "处理中", "已处理", "已忽略");

    @Override
    @Transactional(readOnly = true)
    public List<FaultLogResponse> listAll(Integer limit) {
        Pageable pageable = PageRequest.of(0, Math.min(limit, 500));
        return faultLogRepository.findAllByOrderByIdDesc(pageable).stream()
                .map(entityMapper::toFaultLogResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<FaultLogResponse> listByRobotId(Long robotId, Integer limit) {
        Pageable pageable = PageRequest.of(0, Math.min(limit, 500));
        return faultLogRepository.findByRobotIdOrderByIdDesc(robotId, pageable).stream()
                .map(entityMapper::toFaultLogResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<FaultLogResponse> listByStatus(String status, Integer limit) {
        Pageable pageable = PageRequest.of(0, Math.min(limit, 500));
        return faultLogRepository.findByStatusOrderByIdDesc(status, pageable).stream()
                .map(entityMapper::toFaultLogResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public FaultLogResponse getById(Long id) {
        FaultLog faultLog = faultLogRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("故障日志", id));
        return entityMapper.toFaultLogResponse(faultLog);
    }

    @Override
    @Transactional
    public FaultLogResponse updateStatus(Long id, FaultLogStatusUpdateRequest request) {
        // 校验状态值
        if (!VALID_STATUSES.contains(request.getStatus())) {
            throw new ValidationException("status", "状态必须是：未处理、处理中、已处理、已忽略之一");
        }

        FaultLog faultLog = faultLogRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("故障日志", id));

        faultLog.setStatus(request.getStatus());
        FaultLog updatedLog = faultLogRepository.save(faultLog);

        log.info("故障日志状态已更新: id={}, status={}", id, request.getStatus());
        return entityMapper.toFaultLogResponse(updatedLog);
    }

    @Override
    @Transactional(readOnly = true)
    public Long countUnhandled() {
        return faultLogRepository.countByStatus("未处理");
    }
}
