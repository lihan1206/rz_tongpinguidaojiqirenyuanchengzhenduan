package com.tongping.robot.service.impl;

import com.tongping.robot.dto.request.SensorDataRequest;
import com.tongping.robot.dto.request.SensorQueryRequest;
import com.tongping.robot.dto.response.DiagnosisResultResponse;
import com.tongping.robot.dto.response.FaultLogResponse;
import com.tongping.robot.dto.response.FaultRuleResponse;
import com.tongping.robot.dto.response.SensorDataResponse;
import com.tongping.robot.entity.AlarmNotification;
import com.tongping.robot.entity.FaultLog;
import com.tongping.robot.entity.FaultRule;
import com.tongping.robot.entity.SensorData;
import com.tongping.robot.exception.ResourceNotFoundException;
import com.tongping.robot.mapper.EntityMapper;
import com.tongping.robot.repository.AlarmNotificationRepository;
import com.tongping.robot.repository.FaultLogRepository;
import com.tongping.robot.repository.FaultRuleRepository;
import com.tongping.robot.repository.SensorDataRepository;
import com.tongping.robot.service.SensorDataService;
import com.tongping.robot.service.strategy.DiagnosisStrategy;
import com.tongping.robot.service.strategy.DiagnosisStrategyFactory;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * 传感器数据服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SensorDataServiceImpl implements SensorDataService {

    private final SensorDataRepository sensorDataRepository;
    private final FaultRuleRepository faultRuleRepository;
    private final FaultLogRepository faultLogRepository;
    private final AlarmNotificationRepository alarmNotificationRepository;
    private final DiagnosisStrategyFactory strategyFactory;
    private final EntityMapper entityMapper;

    @Override
    @Transactional
    public DiagnosisResultResponse ingest(SensorDataRequest request) {
        // 1. 保存传感器数据
        SensorData sensorData = SensorData.builder()
                .robotId(request.getRobotId())
                .sensorType(request.getSensorType())
                .value(request.getValue())
                .timestamp(request.getTimestamp() != null
                        ? LocalDateTime.ofEpochSecond(request.getTimestamp() / 1000, 0, java.time.ZoneOffset.UTC)
                        : LocalDateTime.now())
                .build();

        SensorData savedData = sensorDataRepository.save(sensorData);
        log.info("传感器数据已保存: robotId={}, sensorType={}, value={}",
                request.getRobotId(), request.getSensorType(), request.getValue());

        // 2. 获取适用的诊断规则
        List<FaultRule> rules = faultRuleRepository.findBySensorTypeAndEnabledTrue(request.getSensorType());

        // 3. 使用策略模式执行诊断
        DiagnosisStrategy strategy = strategyFactory.getStrategy(request.getSensorType());
        List<FaultRule> triggeredRules = strategy.diagnose(request.getRobotId(), request.getValue(), rules);

        // 4. 生成故障日志和告警通知
        List<FaultLog> faultLogs = new ArrayList<>();
        List<AlarmNotification> notifications = new ArrayList<>();

        for (FaultRule rule : triggeredRules) {
            // 创建故障日志
            FaultLog faultLog = FaultLog.builder()
                    .robotId(request.getRobotId())
                    .ruleId(rule.getId())
                    .faultType(rule.getName())
                    .description(String.format("传感器[%s]数值为%s，触发规则：%s%s",
                            request.getSensorType(), request.getValue(),
                            rule.getOperator(), rule.getThreshold()))
                    .level(rule.getLevel())
                    .status("未处理")
                    .build();

            FaultLog savedLog = faultLogRepository.save(faultLog);
            faultLogs.add(savedLog);

            // 创建告警通知
            AlarmNotification notification = AlarmNotification.builder()
                    .faultLogId(savedLog.getId())
                    .channel("系统")
                    .content(String.format("机器人#%d触发告警：%s", request.getRobotId(), faultLog.getDescription()))
                    .build();

            notifications.add(alarmNotificationRepository.save(notification));
        }

        // 5. 构建响应
        return DiagnosisResultResponse.builder()
                .robotId(request.getRobotId())
                .sensorType(request.getSensorType())
                .value(request.getValue())
                .hasFault(!triggeredRules.isEmpty())
                .triggeredRules(triggeredRules.stream()
                        .map(entityMapper::toFaultRuleResponse)
                        .toList())
                .faultLogs(faultLogs.stream()
                        .map(entityMapper::toFaultLogResponse)
                        .toList())
                .message(triggeredRules.isEmpty()
                        ? "传感器数据正常"
                        : String.format("检测到%d个异常，已生成故障日志", triggeredRules.size()))
                .build();
    }

    @Override
    @Transactional(readOnly = true)
    public List<SensorDataResponse> listData(SensorQueryRequest queryRequest) {
        Pageable pageable = PageRequest.of(
                queryRequest.getOffset() / queryRequest.getLimit(),
                queryRequest.getLimit()
        );

        List<SensorData> dataList;

        if (queryRequest.getRobotId() != null && queryRequest.getSensorType() != null) {
            dataList = sensorDataRepository.findByRobotIdAndSensorTypeOrderByIdDesc(
                    queryRequest.getRobotId(), queryRequest.getSensorType(), pageable);
        } else if (queryRequest.getRobotId() != null) {
            dataList = sensorDataRepository.findByRobotIdOrderByIdDesc(queryRequest.getRobotId(), pageable);
        } else if (queryRequest.getSensorType() != null) {
            dataList = sensorDataRepository.findBySensorTypeOrderByIdDesc(queryRequest.getSensorType(), pageable);
        } else {
            dataList = sensorDataRepository.findLatest(pageable);
        }

        return dataList.stream()
                .map(entityMapper::toSensorDataResponse)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public SensorDataResponse getById(Long id) {
        SensorData data = sensorDataRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("传感器数据", id));
        return entityMapper.toSensorDataResponse(data);
    }

    @Override
    @Transactional(readOnly = true)
    public List<SensorDataResponse> getLatestByRobotId(Long robotId, Integer limit) {
        Pageable pageable = PageRequest.of(0, limit);
        return sensorDataRepository.findLatestByRobotId(robotId, pageable).stream()
                .map(entityMapper::toSensorDataResponse)
                .toList();
    }
}
