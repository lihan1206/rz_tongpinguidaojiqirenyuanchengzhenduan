package com.tongping.robot.service.impl;

import com.tongping.robot.dto.request.FaultRuleCreateRequest;
import com.tongping.robot.dto.response.FaultRuleResponse;
import com.tongping.robot.entity.FaultRule;
import com.tongping.robot.exception.ResourceNotFoundException;
import com.tongping.robot.exception.ValidationException;
import com.tongping.robot.mapper.EntityMapper;
import com.tongping.robot.repository.FaultRuleRepository;
import com.tongping.robot.service.FaultRuleService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 故障规则服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class FaultRuleServiceImpl implements FaultRuleService {

    private final FaultRuleRepository faultRuleRepository;
    private final EntityMapper entityMapper;

    @Override
    @Transactional
    public FaultRuleResponse create(FaultRuleCreateRequest request) {
        // 检查是否已存在相同规则
        if (faultRuleRepository.existsBySensorTypeAndName(request.getSensorType(), request.getName())) {
            throw new ValidationException(String.format("传感器类型[%s]的规则[%s]已存在",
                    request.getSensorType(), request.getName()));
        }

        FaultRule rule = FaultRule.builder()
                .name(request.getName())
                .sensorType(request.getSensorType())
                .operator(request.getOperator())
                .threshold(request.getThreshold())
                .level(request.getLevel())
                .enabled(request.getEnabled())
                .build();

        FaultRule savedRule = faultRuleRepository.save(rule);
        log.info("故障规则已创建: id={}, name={}, sensorType={}",
                savedRule.getId(), savedRule.getName(), savedRule.getSensorType());

        return entityMapper.toFaultRuleResponse(savedRule);
    }

    @Override
    @Transactional(readOnly = true)
    public List<FaultRuleResponse> listAll() {
        return faultRuleRepository.findAll().stream()
                .sorted((a, b) -> b.getId().compareTo(a.getId()))
                .map(entityMapper::toFaultRuleResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<FaultRuleResponse> listEnabled() {
        return faultRuleRepository.findByEnabledTrueOrderByIdDesc().stream()
                .map(entityMapper::toFaultRuleResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<FaultRuleResponse> listBySensorType(String sensorType) {
        return faultRuleRepository.findBySensorTypeAndEnabledTrue(sensorType).stream()
                .map(entityMapper::toFaultRuleResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public FaultRuleResponse getById(Long id) {
        FaultRule rule = faultRuleRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("故障规则", id));
        return entityMapper.toFaultRuleResponse(rule);
    }

    @Override
    @Transactional
    public FaultRuleResponse updateStatus(Long id, Boolean enabled) {
        FaultRule rule = faultRuleRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("故障规则", id));

        rule.setEnabled(enabled);
        FaultRule updatedRule = faultRuleRepository.save(rule);

        log.info("故障规则状态已更新: id={}, enabled={}", id, enabled);
        return entityMapper.toFaultRuleResponse(updatedRule);
    }

    @Override
    @Transactional
    public void delete(Long id) {
        if (!faultRuleRepository.existsById(id)) {
            throw new ResourceNotFoundException("故障规则", id);
        }
        faultRuleRepository.deleteById(id);
        log.info("故障规则已删除: id={}", id);
    }
}
